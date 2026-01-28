from __future__ import annotations

import logging
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional, Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction, connection
from django.db.models import Count, Prefetch, Q, Sum
from django.utils import timezone
from rest_framework import serializers as drf_serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from app.common.net_utils import get_client_ip, resolve_client_hostname

from accounts.permissions import RolePermission
from monitoring.models import Employee as MonitoringEmployee

from .models import Attendance, AttendanceRule, AttendanceBreak, LeaveRequest
from .serializers import (
    AttendanceRuleSerializer,
    AttendanceSerializer,
    CheckInSerializer,
    CheckOutSerializer,
    BreakStartSerializer,
    BreakEndSerializer,
    OvertimeVerifySerializer,
    LeaveRequestSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestApproveSerializer,
    LeaveRequestRejectSerializer,
)
from .utils import build_attendance_metadata
from audit.models import ActivityLog
from notifications.services import notify_admins, create_notification

logger = logging.getLogger(__name__)

# Cache for column existence check (avoids checking on every request)
_breaks_columns_exist = None


def _check_overtime_columns_exist():
    """Check if overtime columns exist in the database."""
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            if connection.vendor == 'mysql':
                cursor.execute("""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'attendance_attendance'
                    AND COLUMN_NAME = 'overtime_minutes'
                """)
                return cursor.fetchone()[0] > 0
            elif connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_name = 'attendance_attendance'
                    AND column_name = 'overtime_minutes'
                """)
                return cursor.fetchone()[0] > 0
            else:  # sqlite
                cursor.execute("PRAGMA table_info(attendance_attendance)")
                columns = [row[1] for row in cursor.fetchall()]
                return 'overtime_minutes' in columns
    except Exception:
        # If check fails, assume columns don't exist
        return False


def _get_breaks_prefetch():
    """
    Returns a Prefetch object for breaks that safely handles missing columns.
    Checks if is_flagged and flag_reason columns exist, and defers them if not.
    Uses module-level cache to avoid checking on every request.
    """
    global _breaks_columns_exist
    
    if _breaks_columns_exist is None:
        try:
            # Check if the columns exist in the database
            with connection.cursor() as cursor:
                if connection.vendor == 'mysql':
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE() 
                        AND TABLE_NAME = 'attendance_attendancebreak'
                        AND COLUMN_NAME IN ('is_flagged', 'flag_reason')
                        """
                    )
                    count = cursor.fetchone()[0]
                    _breaks_columns_exist = count == 2
                elif connection.vendor == 'sqlite':
                    cursor.execute(
                        "PRAGMA table_info(attendance_attendancebreak)"
                    )
                    columns = [row[1] for row in cursor.fetchall()]
                    _breaks_columns_exist = 'is_flagged' in columns and 'flag_reason' in columns
                else:
                    # PostgreSQL
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM information_schema.columns
                        WHERE table_name = 'attendance_attendancebreak'
                        AND column_name IN ('is_flagged', 'flag_reason')
                        """
                    )
                    count = cursor.fetchone()[0]
                    _breaks_columns_exist = count == 2
        except Exception:
            # If we can't check, assume columns don't exist and defer them
            _breaks_columns_exist = False
    
    if _breaks_columns_exist:
        # Columns exist, use normal prefetch
        return Prefetch('breaks', queryset=AttendanceBreak.objects.all())
    else:
        # Columns don't exist yet, defer them to avoid SELECT errors
        return Prefetch(
            'breaks',
            queryset=AttendanceBreak.objects.defer('is_flagged', 'flag_reason')
        )


def _format_location(metadata: dict[str, object]) -> str:
    """Create a user-friendly location string from metadata."""

    location = (metadata.get('location_address') or '').strip()
    if location:
        return location

    lat = metadata.get('location_lat')
    lng = metadata.get('location_lng')
    if lat in (None, '') or lng in (None, ''):
        return ''

    return f"{lat}, {lng}"


def _collect_device_meta(request, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Optional[object]]:
    """Capture device identifiers and resolve the hostname for the client."""

    payload = payload or {}

    ip_candidate = (payload.get('ip_address') or get_client_ip(request) or '').strip()
    ip_address = ip_candidate or None

    device_id_candidate = (
        payload.get('device_id')
        or request.headers.get('X-Device-Id')
        or request.META.get('HTTP_X_DEVICE_ID')
    )
    device_id = str(device_id_candidate).strip() if device_id_candidate else ''
    device_id = device_id or None

    user_agent_candidate = (
        payload.get('device_info')
        or request.headers.get('User-Agent')
        or request.META.get('HTTP_USER_AGENT')
        or ''
    )
    device_info = str(user_agent_candidate)[:255].strip()
    device_info = device_info or None

    # Prefer explicit device name (header/payload) over reverse DNS
    device_name_candidate = (
        (payload.get('device_name') if payload else None)
        or request.headers.get('X-Device-Name')
        or request.META.get('HTTP_X_DEVICE_NAME')
        or None
    )
    if device_name_candidate is not None:
        device_name = str(device_name_candidate).strip()[:255] or None
    else:
        device_name = resolve_client_hostname(ip_address)

    return {
        'ip_address': ip_address,
        'device_id': device_id,
        'device_info': device_info,
        'device_name': device_name,
    }


def _log_attendance_action(
    *,
    user,
    action: str,
    attendance: Attendance,
    description: str,
    request,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            content_object=attendance,
            description=description,
            ip_address=get_client_ip(request),
            user_agent=(request.headers.get('User-Agent') or '')[:500],
            metadata={'attendance_id': attendance.id, **(metadata or {})},
        )
    except Exception as exc:  # pragma: no cover - audit failures should not break flow
        logger.debug("Failed to create attendance audit log: %s", exc)


User = get_user_model()

ALL_ROLES = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']


def _apply_common_filters(queryset, request):
    employee_id = request.query_params.get('employee')
    if employee_id:
        queryset = queryset.filter(employee_id=employee_id)

    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    if end_date:
        queryset = queryset.filter(date__lte=end_date)

    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    search_term = request.query_params.get('search') or request.query_params.get('q')
    if search_term:
        queryset = queryset.filter(
            Q(employee__username__icontains=search_term)
            | Q(employee__first_name__icontains=search_term)
            | Q(employee__last_name__icontains=search_term)
        )

    return queryset


class AttendanceCheckInView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ALL_ROLES

    @extend_schema(
        operation_id='attendance_check_in',
        request=CheckInSerializer,
        responses={201: AttendanceSerializer},
        summary='Check in employee',
        description='Record employee check-in time',
        tags=['Attendance'],
    )
    def post(self, request):
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        now = timezone.now()
        today = timezone.localdate(now)

        existing = Attendance.objects.filter(
            employee=request.user,
            date=today,
            check_out__isnull=True,
        ).first()
        if existing:
            # Treat duplicate check-ins as idempotent: return the current record instead of failing.
            return Response(
                AttendanceSerializer(existing).data,
                status=status.HTTP_200_OK,
            )

        data = serializer.validated_data
        metadata = build_attendance_metadata(request, data)
        device_meta = _collect_device_meta(request, data)
        metadata.update(
            {
                'ip_address': device_meta.get('ip_address'),
                'device_id': device_meta.get('device_id') or '',
                'device_info': device_meta.get('device_info') or '',
                'device_name': device_meta.get('device_name'),
            }
        )

        attendance = Attendance.objects.create(
            employee=request.user,
            check_in=now,
            date=today,
            notes=data.get('notes', ''),
            status=Attendance.determine_status(now),
            **metadata,
        )

        _log_attendance_action(
            user=request.user,
            action='create',
            attendance=attendance,
            description='Attendance check-in recorded',
            request=request,
            metadata={'event': 'check_in'},
        )

        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)


class AttendanceCheckOutView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ALL_ROLES

    @extend_schema(
        operation_id='attendance_check_out',
        request=CheckOutSerializer,
        responses={200: AttendanceSerializer},
        summary='Check out employee',
        description='Record employee check-out time',
        tags=['Attendance'],
    )
    def post(self, request):
        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        now = timezone.now()
        today = timezone.localdate(now)

        attendance = Attendance.objects.filter(
            employee=request.user,
            date=today,
            check_out__isnull=True,
        ).order_by('-check_in').first()

        if not attendance:
            return Response(
                {'detail': 'No active check-in found for today'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data

        with transaction.atomic():
            attendance.check_out = now
            if data.get('notes'):
                if attendance.notes:
                    attendance.notes = f"{attendance.notes}\n{data['notes']}"
                else:
                    attendance.notes = data['notes']

            metadata = build_attendance_metadata(request, data)
            device_meta = _collect_device_meta(request, data)

            for field in ('ip_address', 'device_id', 'device_info', 'device_name'):
                value = device_meta.get(field)
                if field in ('device_id', 'device_info') and value is None:
                    value = ''
                setattr(attendance, field, value)

            for field, value in metadata.items():
                if field in ('ip_address', 'device_id', 'device_info', 'device_name'):
                    continue
                if value not in (None, ''):
                    setattr(attendance, field, value)

            active_break = attendance.active_break
            if active_break:
                active_break.end_break(metadata={'closed_by': 'checkout'})

            attendance.save()
            attendance.refresh_from_db()
            # Calculate overtime after checkout
            attendance.calculate_overtime(save=True)

        _log_attendance_action(
            user=request.user,
            action='update',
            attendance=attendance,
            description='Attendance check-out recorded',
            request=request,
            metadata={'event': 'check_out'},
        )

        return Response(AttendanceSerializer(attendance).data)


class AttendanceBreakStartView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ALL_ROLES

    @extend_schema(
        operation_id='attendance_break_start',
        request=BreakStartSerializer,
        responses={201: AttendanceSerializer},
        summary='Start break',
        description='Start a break session for the current active attendance record.',
        tags=['Attendance'],
    )
    def post(self, request):
        serializer = BreakStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            attendance = (
                Attendance.objects.select_for_update()
                .filter(
                    employee=request.user,
                    check_out__isnull=True,
                )
                .order_by('-check_in')
                .first()
            )
            if not attendance:
                return Response({'detail': 'No active attendance session found.'}, status=status.HTTP_400_BAD_REQUEST)
            if attendance.has_active_break:
                return Response({'detail': 'A break is already in progress.'}, status=status.HTTP_400_BAD_REQUEST)

            payload = serializer.validated_data
            attendance_break = AttendanceBreak.objects.create(
                attendance=attendance,
                started_at=timezone.now(),
                source=payload.get('source') or AttendanceBreak.SOURCE_WEB,
                notes=payload.get('notes', ''),
            )
            attendance.refresh_from_db()

        _log_attendance_action(
            user=request.user,
            action='create',
            attendance=attendance,
            description='Break started',
            request=request,
            metadata={'event': 'break_start', 'break_id': attendance_break.id},
        )

        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)


class AttendanceBreakEndView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ALL_ROLES

    @extend_schema(
        operation_id='attendance_break_end',
        request=BreakEndSerializer,
        responses={200: AttendanceSerializer},
        summary='End break',
        description='End the active break session for the current attendance record.',
        tags=['Attendance'],
    )
    def post(self, request):
        serializer = BreakEndSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            attendance = (
                Attendance.objects.select_for_update()
                .filter(
                    employee=request.user,
                    check_out__isnull=True,
                )
                .order_by('-check_in')
                .first()
            )
            if not attendance:
                return Response({'detail': 'No active attendance session found.'}, status=status.HTTP_400_BAD_REQUEST)

            active_break = attendance.active_break
            if not active_break:
                return Response({'detail': 'No active break found.'}, status=status.HTTP_400_BAD_REQUEST)

            notes = serializer.validated_data.get('notes')
            if notes:
                active_break.notes = notes
            active_break.end_break(metadata={'event': 'break_end'})
            attendance.refresh_from_db()

        _log_attendance_action(
            user=request.user,
            action='update',
            attendance=attendance,
            description='Break ended',
            request=request,
            metadata={'event': 'break_end', 'break_id': active_break.id},
        )

        return Response(AttendanceSerializer(attendance).data)


class AttendanceContextView(APIView):
    """Return contextual metadata for the authenticated user's device."""

    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ALL_ROLES

    @extend_schema(
        operation_id='attendance_context',
        summary='Get device context for attendance',
        description='Returns the requesting user\'s IP, location and device identifiers',
        responses={200: None},
        tags=['Attendance'],
    )
    def get(self, request):
        metadata = build_attendance_metadata(request)
        device_meta = _collect_device_meta(request)

        ip_address = (device_meta.get('ip_address') or metadata.get('ip_address') or '').strip()
        device_id = (device_meta.get('device_id') or metadata.get('device_id') or '').strip()
        device_info = device_meta.get('device_info') or metadata.get('device_info') or ''
        device_name = (device_meta.get('device_name') or '').strip()

        location = _format_location(metadata)

        fallback_device_name = device_name or device_id

        return Response(
            {
                'ip': ip_address,
                'location': location,
                'deviceId': device_id,
                'deviceName': fallback_device_name,
            }
        )


class AttendanceListView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='attendance_list',
        summary='List attendance records',
        description='Get attendance records with optional filtering',
        responses={200: AttendanceSerializer(many=True)},
        tags=['Attendance'],
    )
    def get(self, request):
        queryset = Attendance.objects.select_related('employee').prefetch_related(_get_breaks_prefetch())
        queryset = _apply_common_filters(queryset, request)
        queryset = queryset.order_by('-date', '-check_in')
        # If overtime columns don't exist, use only() to exclude them from SELECT
        if not _check_overtime_columns_exist():
            queryset = queryset.only(
                'id', 'employee_id', 'check_in', 'check_out', 'date', 'total_hours',
                'notes', 'status', 'location_lat', 'location_lng', 'location_address',
                'ip_address', 'device_id', 'device_info', 'device_name',
                'created_at', 'updated_at', 'total_break_minutes', 'effective_minutes'
            )
        return Response(AttendanceSerializer(queryset, many=True).data)


class MyAttendanceView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ALL_ROLES

    @extend_schema(
        operation_id='attendance_me',
        summary='Get my attendance',
        description='Get current user attendance records with optional filtering',
        responses={200: AttendanceSerializer(many=True)},
        tags=['Attendance'],
    )
    def get(self, request):
        queryset = Attendance.objects.filter(employee=request.user).prefetch_related(_get_breaks_prefetch())
        queryset = _apply_common_filters(queryset, request)
        queryset = queryset.order_by('-date', '-check_in')
        # If overtime columns don't exist, use only() to exclude them from SELECT
        if not _check_overtime_columns_exist():
            queryset = queryset.only(
                'id', 'employee_id', 'check_in', 'check_out', 'date', 'total_hours',
                'notes', 'status', 'location_lat', 'location_lng', 'location_address',
                'ip_address', 'device_id', 'device_info', 'device_name',
                'created_at', 'updated_at', 'total_break_minutes', 'effective_minutes'
            )
        return Response(AttendanceSerializer(queryset, many=True).data)


class AttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='attendance_summary',
        summary='Attendance summary metrics',
        description='Aggregated metrics for attendance records',
        tags=['Attendance'],
    )
    def get(self, request):
        queryset = Attendance.objects.select_related('employee').prefetch_related(_get_breaks_prefetch())
        queryset = _apply_common_filters(queryset, request)

        if not request.user.is_superuser and 'admin' not in (request.user.roles or []):
            queryset = queryset.filter(employee=request.user)

        total_records = queryset.count()
        total_hours = queryset.aggregate(total=Sum('total_hours'))['total'] or Decimal('0')
        total_effective_minutes = queryset.aggregate(total=Sum('effective_minutes'))['total'] or 0
        present_count = queryset.filter(status=Attendance.STATUS_PRESENT).count()
        late_count = queryset.filter(status=Attendance.STATUS_LATE).count()
        absent_count = queryset.filter(status=Attendance.STATUS_ABSENT).count()
        active_count = queryset.filter(check_out__isnull=True).count()
        avg_hours = float(total_hours) / total_records if total_records else 0.0

        daily = list(
            queryset.values('date').annotate(
                present=Count('id', filter=Q(status=Attendance.STATUS_PRESENT)),
                late=Count('id', filter=Q(status=Attendance.STATUS_LATE)),
                absent=Count('id', filter=Q(status=Attendance.STATUS_ABSENT)),
                total_hours=Sum('total_hours'),
                total_effective_minutes=Sum('effective_minutes'),
            ).order_by('-date')[:60]
        )

        for item in daily:
            item['total_hours'] = float(item['total_hours'] or 0)
            item['total_effective_hours'] = round((item.pop('total_effective_minutes') or 0) / 60, 2)

        return Response(
            {
                'total_records': total_records,
                'present': present_count,
                'late': late_count,
                'absent': absent_count,
                'active': active_count,
                'total_hours': float(total_hours),
                'total_effective_hours': round(total_effective_minutes / 60, 2),
                'average_hours': round(avg_hours, 2),
                'daily': daily,
            }
        )


class AttendanceRuleView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='attendance_rules_get',
        summary='Get attendance rules',
        responses={200: AttendanceRuleSerializer},
        tags=['Attendance'],
    )
    def get(self, request):
        rules = AttendanceRule.get_solo()
        return Response(AttendanceRuleSerializer(rules).data)

    @extend_schema(
        operation_id='attendance_rules_update',
        summary='Update attendance rules',
        request=AttendanceRuleSerializer,
        responses={200: AttendanceRuleSerializer},
        tags=['Attendance'],
    )
    def put(self, request):
        rules = AttendanceRule.get_solo()
        serializer = AttendanceRuleSerializer(rules, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AttendanceEmployeesView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='attendance_employees',
        summary='List employees for attendance',
        description='Returns employees with salary data for payroll calculations',
        tags=['Attendance'],
    )
    def get(self, request):
        employees = MonitoringEmployee.objects.all().order_by('name')
        data = [
            {
                'id': emp.id,
                'name': emp.name,
                'email': emp.email,
                'base_salary': float(emp.salary),
            }
            for emp in employees
        ]
        return Response({'employees': data})


class AttendancePayrollView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='attendance_payroll',
        summary='Generate payroll summary',
        description='Generates a payroll summary for the provided month',
        tags=['Attendance'],
    )
    def get(self, request):
        month_param = request.query_params.get('month')
        if month_param:
            try:
                year, month = map(int, month_param.split('-'))
            except ValueError:
                return Response({'detail': 'month must be YYYY-MM'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            today = timezone.localdate()
            year, month = today.year, today.month

        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
        rules = AttendanceRule.get_solo()

        queryset = (
            Attendance.objects.filter(date__range=(start, end))
            .select_related('employee')
            .prefetch_related(_get_breaks_prefetch())
        )
        records_map: dict[tuple[int, date], list[Attendance]] = defaultdict(list)
        for record in queryset:
            records_map[(record.employee_id, record.date)].append(record)

        weekend_days = set(int(d) for d in (rules.weekend_days or []))
        days = []
        cur = start
        while cur <= end:
            js_weekday = (cur.weekday() + 1) % 7
            if js_weekday not in weekend_days:
                days.append(cur)
            cur += timedelta(days=1)

        users = User.objects.filter(id__in={r.employee_id for r in queryset})
        users_by_id = {user.id: user for user in users}
        salaries_by_email = {
            emp.email.lower(): Decimal(emp.salary)
            for emp in MonitoringEmployee.objects.filter(email__in=[u.email for u in users if u.email])
        }

        # Get all approved leave requests for the month
        approved_leaves = LeaveRequest.objects.filter(
            status=LeaveRequest.STATUS_APPROVED,
            start_date__lte=end,
        ).filter(
            Q(end_date__gte=start) | Q(end_date__isnull=True, start_date__gte=start)
        ).select_related('employee')
        
        # Group leaves by employee
        leaves_by_employee: dict[int, list[LeaveRequest]] = defaultdict(list)
        for leave in approved_leaves:
            leaves_by_employee[leave.employee_id].append(leave)
        
        response_rows = []
        for user_id, user in users_by_id.items():
            # HARD BLOCK: Check salary hold status and verification percentage
            try:
                from hr.models import HREmployee, EmployeeVerification, EmployeeExemption
                hr_employee = HREmployee.objects.get(user=user)
                
                # Check salary status
                if hr_employee.salary_status == 'ON_HOLD':
                    from django.core.exceptions import ValidationError
                    raise ValidationError(
                        f"Salary processing blocked for {hr_employee.name}: "
                        f"Bank verification pending or salary on hold. "
                        f"Please verify bank details or grant exemption."
                    )
                
                # Check verification percentage
                try:
                    verification = EmployeeVerification.objects.get(employee=hr_employee)
                    verification_percentage = verification.verification_percentage
                    
                    # Check if exempted
                    is_exempted = False
                    try:
                        exemption = EmployeeExemption.objects.get(employee=hr_employee)
                        is_exempted = exemption.bank_exempted  # Can extend for other exemptions
                    except EmployeeExemption.DoesNotExist:
                        pass
                    
                    # HARD BLOCK: Require 100% verification unless exempted
                    if verification_percentage < 100 and not is_exempted:
                        from django.core.exceptions import ValidationError
                        raise ValidationError(
                            f"Salary processing blocked for {hr_employee.name}: "
                            f"Verification incomplete ({verification_percentage}%). "
                            f"Complete employee verification or grant exemption."
                        )
                except EmployeeVerification.DoesNotExist:
                    # No verification record, block processing
                    from django.core.exceptions import ValidationError
                    raise ValidationError(
                        f"Salary processing blocked for {hr_employee.name}: "
                        f"Employee verification not started. Please complete verification."
                    )
            except HREmployee.DoesNotExist:
                # Employee not in HR system yet, allow processing
                pass
            except ValidationError as e:
                # Re-raise validation error
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for active salary exemptions during the payroll period
            active_exemption = None
            exemption_days = []
            try:
                from hr.models import EmployeeSalaryExemption
                active_exemption = EmployeeSalaryExemption.objects.filter(
                    employee__user=user,
                    is_active=True
                ).first()
                
                if active_exemption:
                    # Check if exemption period overlaps with payroll period
                    exemption_start = active_exemption.granted_at.date()
                    exemption_end = active_exemption.expiry_date.date() if active_exemption.expiry_date else None
                    
                    # If permanent, exemption_end is None (no end date)
                    if active_exemption.exemption_type == 'Permanent' or (exemption_end and exemption_end >= start):
                        # Exemption is active during this payroll period
                        # Calculate which days are within exemption period
                        for day in days:
                            if day >= exemption_start:
                                if exemption_end is None or day <= exemption_end:
                                    exemption_days.append(day)
            except Exception as e:
                logger.warning(f"Error checking exemption for user {user_id}: {e}")
            
            base_salary = salaries_by_email.get((user.email or '').lower(), Decimal('0'))
            present_days = 0
            absent_days = 0
            total_late_minutes = 0
            total_overtime_minutes = 0
            total_break_minutes = 0
            total_effective_minutes = 0
            
            # Track daily attendance details
            daily_attendance_list = []
            total_grace_violations = 0
            total_early_checkouts = 0
            check_in_times = []  # For calculating average
            check_out_times = []  # For calculating average
            
            # Calculate leave hours for this employee
            employee_leaves = leaves_by_employee.get(user_id, [])
            total_leave_hours = 0.0
            paid_leave_hours = 0.0
            unpaid_leave_hours = 0.0
            
            for leave in employee_leaves:
                leave_hours = leave.get_total_hours()
                total_leave_hours += leave_hours
                if leave.is_paid:
                    paid_leave_hours += leave_hours
                else:
                    unpaid_leave_hours += leave_hours

            for day in days:
                records = records_map.get((user_id, day), [])
                if not records:
                    absent_days += 1
                    # Add absent day to daily attendance
                    daily_attendance_list.append({
                        'date': str(day),
                        'check_in': None,
                        'check_out': None,
                        'is_grace_violation': False,
                        'is_early_checkout': False,
                        'grace_violation_deduction': 0.0,
                        'early_checkout_deduction': 0.0,
                    })
                    continue

                present_days += 1
                records = sorted(records, key=lambda r: r.check_in)
                completed = [r for r in records if r.check_out]
                record = completed[-1] if completed else records[-1]

                local_in = timezone.localtime(record.check_in)
                start_minutes = rules.work_start.hour * 60 + rules.work_start.minute
                check_in_minutes = local_in.hour * 60 + local_in.minute
                late = max(0, check_in_minutes - (start_minutes + rules.grace_minutes))
                total_late_minutes += late
                
                # Check for grace period violation (check-in after grace period)
                is_grace_violation = check_in_minutes > (start_minutes + rules.grace_minutes)
                grace_violation_deduction = 0.0
                if is_grace_violation:
                    total_grace_violations += 1
                    grace_violation_deduction = float(rules.grace_violation_deduction)
                
                # Format check-in time
                check_in_time_str = local_in.strftime('%H:%M')
                check_in_times.append(check_in_minutes)

                # Check for early check-out
                is_early_checkout = False
                early_checkout_deduction = 0.0
                check_out_time_str = None
                if record.check_out:
                    local_out = timezone.localtime(record.check_out)
                    check_out_time_str = local_out.strftime('%H:%M')
                    check_out_minutes = local_out.hour * 60 + local_out.minute
                    check_out_times.append(check_out_minutes)
                    
                    end_minutes = rules.work_end.hour * 60 + rules.work_end.minute
                    threshold_minutes = rules.early_checkout_threshold_minutes
                    # Early checkout if check-out is more than threshold minutes before work_end
                    if check_out_minutes < (end_minutes - threshold_minutes):
                        is_early_checkout = True
                        total_early_checkouts += 1
                        early_checkout_deduction = float(rules.early_checkout_deduction)
                    
                    effective = record.effective_minutes or 0
                    if effective:
                        worked = effective
                    else:
                        worked = int((local_out - local_in).total_seconds() // 60)
                else:
                    worked = 0
                worked_minutes = int(worked)
                total_effective_minutes += max(worked_minutes, 0)
                break_minutes = int(getattr(record, 'total_break_minutes', 0) or 0)
                total_break_minutes += break_minutes
                
                # Use stored overtime_minutes if available, otherwise calculate
                # New overtime calculation: Effective Hours - Standard Working Hours
                # Only count if monitored (has device_id or device_name)
                stored_overtime = getattr(record, 'overtime_minutes', None)
                if stored_overtime is not None:
                    # Use stored value (already calculated and saved)
                    overtime = stored_overtime
                else:
                    # Calculate on the fly for records that haven't been updated yet
                    is_monitored = bool(record.device_id or record.device_name)
                    if is_monitored and worked_minutes > 0:
                        # Calculate: overtime = max(0, effective_minutes - standard_work_minutes)
                        overtime = max(0, worked_minutes - rules.standard_work_minutes)
                    else:
                        overtime = 0
                total_overtime_minutes += overtime
                
                # Add to daily attendance
                daily_attendance_list.append({
                    'date': str(day),
                    'check_in': check_in_time_str,
                    'check_out': check_out_time_str,
                    'is_grace_violation': is_grace_violation,
                    'is_early_checkout': is_early_checkout,
                    'grace_violation_deduction': grace_violation_deduction,
                    'early_checkout_deduction': early_checkout_deduction,
                })

            # Adjust base salary for permanent exemptions (exclude exempted days from calculation)
            # For permanent exemptions, we calculate salary but exclude exempted days proportionally
            if active_exemption and active_exemption.exemption_type == 'Permanent' and exemption_days:
                # Calculate pro-rated salary excluding exempted days
                total_days_in_month = len(days)
                exempted_days_count = len(exemption_days)
                if total_days_in_month > 0:
                    # Reduce base salary proportionally
                    base_salary = base_salary * Decimal((total_days_in_month - exempted_days_count) / total_days_in_month)
            
            absent_deduction = Decimal(absent_days) * Decimal(rules.per_day_deduction)
            late_deduction = Decimal(total_late_minutes) * Decimal(rules.late_penalty_per_minute)
            grace_violation_deduction_total = Decimal(total_grace_violations) * Decimal(rules.grace_violation_deduction)
            early_checkout_deduction_total = Decimal(total_early_checkouts) * Decimal(rules.early_checkout_deduction)
            overtime_pay = Decimal(total_overtime_minutes) * Decimal(rules.overtime_rate_per_minute)
            net_pay = max(Decimal('0'), base_salary - absent_deduction - late_deduction - grace_violation_deduction_total - early_checkout_deduction_total + overtime_pay)
            
            # For temporary exemptions, mark salary as on hold
            salary_status = 'normal'
            exemption_info = None
            if active_exemption:
                if active_exemption.exemption_type == 'Temporary' and exemption_days:
                    salary_status = 'on_hold'
                    exemption_info = {
                        'type': 'Temporary',
                        'reason': active_exemption.reason,
                        'expiry_date': active_exemption.expiry_date.isoformat() if active_exemption.expiry_date else None,
                        'remarks': active_exemption.remarks,
                        'exempted_days': len(exemption_days),
                        'message': 'Salary calculated but on hold until exemption is cleared'
                    }
                elif active_exemption.exemption_type == 'Permanent' and exemption_days:
                    exemption_info = {
                        'type': 'Permanent',
                        'reason': active_exemption.reason,
                        'remarks': active_exemption.remarks,
                        'exempted_days': len(exemption_days),
                        'message': 'Salary excluded for exempted days'
                    }

            # Calculate unverified overtime (overtime > 4 hours that hasn't been verified)
            unverified_overtime_minutes = 0
            for day in days:
                records = records_map.get((user_id, day), [])
                if not records:
                    continue
                records = sorted(records, key=lambda r: r.check_in)
                completed = [r for r in records if r.check_out]
                record = completed[-1] if completed else records[-1]
                
                if record.check_out and record.overtime_minutes:
                    # Check if overtime > 4 hours (240 minutes) and not verified
                    if record.overtime_minutes > 240 and not getattr(record, 'overtime_verified', False):
                        unverified_overtime_minutes += record.overtime_minutes
            
            # Adjust effective minutes: subtract unpaid leave hours
            # Paid leave hours are not deducted (employee is considered present)
            unpaid_leave_minutes = int(unpaid_leave_hours * 60)
            adjusted_effective_minutes = max(0, total_effective_minutes - unpaid_leave_minutes)
            adjusted_effective_hours = round(adjusted_effective_minutes / 60, 2)
            
            # Calculate average check-in and check-out times
            average_check_in_time = None
            average_check_out_time = None
            if check_in_times:
                avg_check_in_minutes = sum(check_in_times) / len(check_in_times)
                avg_hours = int(avg_check_in_minutes // 60)
                avg_mins = int(avg_check_in_minutes % 60)
                average_check_in_time = f"{avg_hours:02d}:{avg_mins:02d}"
            if check_out_times:
                avg_check_out_minutes = sum(check_out_times) / len(check_out_times)
                avg_hours = int(avg_check_out_minutes // 60)
                avg_mins = int(avg_check_out_minutes % 60)
                average_check_out_time = f"{avg_hours:02d}:{avg_mins:02d}"
            
            # Build deduction breakdown
            deduction_breakdown = []
            if absent_days > 0 and float(rules.per_day_deduction) > 0:
                deduction_breakdown.append({
                    'type': 'Absent',
                    'count': absent_days,
                    'amount_per_occurrence': float(rules.per_day_deduction),
                    'total_amount': float(absent_deduction),
                    'description': f'Absent for {absent_days} day(s)',
                })
            if total_late_minutes > 0 and float(rules.late_penalty_per_minute) > 0:
                deduction_breakdown.append({
                    'type': 'Late',
                    'count': total_late_minutes,
                    'amount_per_occurrence': float(rules.late_penalty_per_minute),
                    'total_amount': float(late_deduction),
                    'description': f'Late by {total_late_minutes} minute(s)',
                })
            if total_grace_violations > 0 and float(rules.grace_violation_deduction) > 0:
                deduction_breakdown.append({
                    'type': 'Grace Period Violation',
                    'count': total_grace_violations,
                    'amount_per_occurrence': float(rules.grace_violation_deduction),
                    'total_amount': float(grace_violation_deduction_total),
                    'description': f'Checked in after grace period {total_grace_violations} time(s)',
                })
            if total_early_checkouts > 0 and float(rules.early_checkout_deduction) > 0:
                deduction_breakdown.append({
                    'type': 'Early Check-out',
                    'count': total_early_checkouts,
                    'amount_per_occurrence': float(rules.early_checkout_deduction),
                    'total_amount': float(early_checkout_deduction_total),
                    'description': f'Checked out early {total_early_checkouts} time(s)',
                })
            
            response_rows.append(
                {
                    'employee': {
                        'id': user.id,
                        'name': user.get_full_name() or user.username,
                        'email': user.email,
                    },
                    'month': f"{year:04d}-{month:02d}",
                    'working_days': len(days),
                    'present_days': present_days,
                    'absent_days': absent_days,
                    'total_late_minutes': total_late_minutes,
                    'total_overtime_minutes': total_overtime_minutes,
                    'total_overtime_hours': round(total_overtime_minutes / 60, 2),
                    'unverified_overtime_minutes': unverified_overtime_minutes,
                    'unverified_overtime_hours': round(unverified_overtime_minutes / 60, 2),
                    'total_break_minutes': total_break_minutes,
                    'total_effective_minutes': total_effective_minutes,
                    'total_effective_hours': round(total_effective_minutes / 60, 2),
                    'total_leave_hours': round(total_leave_hours, 2),
                    'paid_leave_hours': round(paid_leave_hours, 2),
                    'unpaid_leave_hours': round(unpaid_leave_hours, 2),
                    'adjusted_effective_minutes': adjusted_effective_minutes,
                    'adjusted_effective_hours': adjusted_effective_hours,
                    'total_grace_violations': total_grace_violations,
                    'total_early_checkouts': total_early_checkouts,
                    'grace_violation_deduction_total': float(grace_violation_deduction_total),
                    'early_checkout_deduction_total': float(early_checkout_deduction_total),
                    'average_check_in_time': average_check_in_time,
                    'average_check_out_time': average_check_out_time,
                    'daily_attendance': daily_attendance_list,
                    'deduction_breakdown': deduction_breakdown,
                    'base_salary': float(base_salary),
                    'absent_deduction': float(absent_deduction),
                    'late_deduction': float(late_deduction),
                    'overtime_pay': float(overtime_pay),
                    'net_pay': float(net_pay),
                    'salary_status': salary_status,
                    'exemption_info': exemption_info,
                }
            )

        # Calculate ideal monthly hours
        ideal_hours_data = rules.calculate_ideal_monthly_hours(year, month)
        
        return Response(
            {
                'month': f"{year:04d}-{month:02d}",
                'working_days': len(days),
                'ideal_monthly_hours': ideal_hours_data['ideal_monthly_hours'],
                'rows': response_rows,
            }
        )


class AttendanceOvertimeListView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='attendance_overtime_list',
        summary='List overtime records requiring verification',
        description='Returns attendance records with overtime > 4 hours that need admin verification',
        responses={200: AttendanceSerializer(many=True)},
        tags=['Attendance'],
    )
    def get(self, request):
        # Get threshold from query params or use default (4 hours = 240 minutes)
        threshold_minutes = int(request.query_params.get('threshold', 240))
        
        queryset = (
            Attendance.objects.filter(
                overtime_minutes__gt=threshold_minutes,
                overtime_verified=False,
                check_out__isnull=False,
            )
            .select_related('employee', 'overtime_verified_by')
            .prefetch_related(_get_breaks_prefetch())
            .order_by('-date', '-overtime_minutes')
        )
        
        queryset = _apply_common_filters(queryset, request)
        
        return Response(AttendanceSerializer(queryset, many=True).data)


class AttendanceOvertimeVerifyView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='attendance_overtime_verify',
        summary='Verify overtime record',
        description='Mark an attendance record\'s overtime as verified by admin',
        request=OvertimeVerifySerializer,
        responses={200: AttendanceSerializer},
        tags=['Attendance'],
    )
    def post(self, request):
        serializer = OvertimeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attendance_id = serializer.validated_data['attendance_id']
        
        try:
            attendance = Attendance.objects.get(id=attendance_id)
        except Attendance.DoesNotExist:
            return Response(
                {'detail': 'Attendance record not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if not attendance.check_out:
            return Response(
                {'detail': 'Cannot verify overtime for incomplete attendance record'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if attendance.overtime_minutes <= 0:
            return Response(
                {'detail': 'No overtime to verify'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        attendance.overtime_verified = True
        attendance.overtime_verified_by = request.user
        attendance.overtime_verified_at = timezone.now()
        attendance.save(update_fields=['overtime_verified', 'overtime_verified_by', 'overtime_verified_at', 'updated_at'])
        
        _log_attendance_action(
            user=request.user,
            action='update',
            attendance=attendance,
            description=f'Overtime verified: {attendance.overtime_hours} hours',
            request=request,
            metadata={'event': 'overtime_verified', 'overtime_minutes': attendance.overtime_minutes},
        )
        
        return Response(AttendanceSerializer(attendance).data)


class AttendanceMonthlyHoursView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='attendance_monthly_hours',
        summary='Get ideal monthly working hours',
        description='Returns ideal monthly working hours calculation excluding weekends and holidays',
        tags=['Attendance'],
    )
    def get(self, request):
        year_param = request.query_params.get('year')
        month_param = request.query_params.get('month')
        
        if year_param and month_param:
            try:
                year = int(year_param)
                month = int(month_param)
                if not (1 <= month <= 12):
                    return Response(
                        {'detail': 'month must be between 1 and 12'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except ValueError:
                return Response(
                    {'detail': 'year and month must be integers'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            today = timezone.localdate()
            year, month = today.year, today.month
        
        rules = AttendanceRule.get_solo()
        result = rules.calculate_ideal_monthly_hours(year, month)
        
        return Response({
            'year': year,
            'month': month,
            **result,
        })


class LeaveRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='leave_request_list',
        summary='List leave requests',
        description='List leave requests. Employees see only their own, admins see all.',
        tags=['Leave Management'],
        responses={200: LeaveRequestSerializer(many=True)},
    )
    def get(self, request):
        """List leave requests with optional filters."""
        user = request.user
        is_admin = user.is_admin()
        
        queryset = LeaveRequest.objects.all()
        
        # Employees see only their own requests
        if not is_admin:
            queryset = queryset.filter(employee=user)
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by employee_id (admin only)
        employee_id = request.query_params.get('employee_id')
        if employee_id and is_admin:
            try:
                queryset = queryset.filter(employee_id=int(employee_id))
            except ValueError:
                pass
        
        # Filter by month/year
        month_param = request.query_params.get('month')
        year_param = request.query_params.get('year')
        if month_param and year_param:
            try:
                year = int(year_param)
                month = int(month_param)
                start = date(year, month, 1)
                end = date(year, month, monthrange(year, month)[1])
                queryset = queryset.filter(
                    Q(start_date__lte=end, end_date__gte=start) |
                    Q(start_date__lte=end, end_date__isnull=True, start_date__gte=start)
                )
            except ValueError:
                pass
        
        queryset = queryset.select_related('employee', 'approved_by').order_by('-created_at')
        serializer = LeaveRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        operation_id='leave_request_create',
        summary='Create leave request',
        description='Create a new leave request. Employees only.',
        tags=['Leave Management'],
        request=LeaveRequestCreateSerializer,
        responses={201: LeaveRequestSerializer},
    )
    def post(self, request):
        """Create a new leave request."""
        serializer = LeaveRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check for conflicts
        leave_request = LeaveRequest(
            employee=request.user,
            **serializer.validated_data
        )
        
        if leave_request.has_conflict():
            conflicting = leave_request.get_conflicting_leaves()
            return Response(
                {
                    'detail': 'Leave request conflicts with existing approved or pending leave requests.',
                    'conflicts': [lr.id for lr in conflicting[:5]]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            leave_request.save()
        except DjangoValidationError as e:
            return Response(
                {'detail': str(e) if hasattr(e, '__str__') else 'Validation error', 'errors': e.message_dict if hasattr(e, 'message_dict') else None},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Notify admins about the new leave request
        if leave_request.leave_type == LeaveRequest.LEAVE_TYPE_MULTIPLE_DAYS and leave_request.end_date:
            message = f"{request.user.username} requested leave from {leave_request.start_date} to {leave_request.end_date}"
        elif leave_request.leave_type == LeaveRequest.LEAVE_TYPE_PARTIAL_DAY:
            message = f"{request.user.username} requested partial leave on {leave_request.start_date}"
        else:
            message = f"{request.user.username} requested leave on {leave_request.start_date}"
        
        notify_admins(
            title="New Leave Request",
            message=message,
            notification_type="leave_requested",
            actor=request.user,
            related_object_type="leave_request",
            related_object_id=str(leave_request.id)
        )
        
        response_serializer = LeaveRequestSerializer(leave_request)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LeaveRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Get leave request, ensuring user has permission."""
        try:
            leave_request = LeaveRequest.objects.select_related('employee', 'approved_by').get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return None
        
        # Employees can only access their own requests
        if not user.is_admin() and leave_request.employee != user:
            return None
        
        return leave_request

    @extend_schema(
        operation_id='leave_request_detail',
        summary='Get leave request details',
        description='Retrieve a single leave request',
        tags=['Leave Management'],
        responses={200: LeaveRequestSerializer},
    )
    def get(self, request, pk):
        """Retrieve a single leave request."""
        leave_request = self.get_object(pk, request.user)
        if not leave_request:
            return Response(
                {'detail': 'Leave request not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)

    @extend_schema(
        operation_id='leave_request_update',
        summary='Update leave request',
        description='Update a leave request. Only pending requests can be updated.',
        tags=['Leave Management'],
        request=LeaveRequestCreateSerializer,
        responses={200: LeaveRequestSerializer},
    )
    def put(self, request, pk):
        """Update a leave request."""
        leave_request = self.get_object(pk, request.user)
        if not leave_request:
            return Response(
                {'detail': 'Leave request not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Only pending requests can be updated
        if leave_request.status != LeaveRequest.STATUS_PENDING:
            return Response(
                {'detail': 'Only pending leave requests can be updated.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LeaveRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update fields
        for key, value in serializer.validated_data.items():
            setattr(leave_request, key, value)
        
        # Check for conflicts (excluding self)
        if leave_request.has_conflict():
            conflicting = leave_request.get_conflicting_leaves().exclude(pk=leave_request.pk)
            return Response(
                {
                    'detail': 'Leave request conflicts with existing approved or pending leave requests.',
                    'conflicts': [lr.id for lr in conflicting[:5]]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            leave_request.save()
        except DjangoValidationError as e:
            return Response(
                {'detail': str(e) if hasattr(e, '__str__') else 'Validation error', 'errors': e.message_dict if hasattr(e, 'message_dict') else None},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_serializer = LeaveRequestSerializer(leave_request)
        return Response(response_serializer.data)

    @extend_schema(
        operation_id='leave_request_delete',
        summary='Delete leave request',
        description='Cancel a leave request. Only pending requests can be cancelled.',
        tags=['Leave Management'],
        responses={204: None},
    )
    def delete(self, request, pk):
        """Cancel a leave request."""
        leave_request = self.get_object(pk, request.user)
        if not leave_request:
            return Response(
                {'detail': 'Leave request not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Only pending requests can be cancelled
        if leave_request.status != LeaveRequest.STATUS_PENDING:
            return Response(
                {'detail': 'Only pending leave requests can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaveRequestApproveView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='leave_request_approve',
        summary='Approve leave request',
        description='Approve a leave request and mark it as paid or unpaid. Admin only.',
        tags=['Leave Management'],
        request=LeaveRequestApproveSerializer,
        responses={200: LeaveRequestSerializer},
    )
    def post(self, request, pk):
        """Approve a leave request."""
        try:
            leave_request = LeaveRequest.objects.select_related('employee', 'approved_by').get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response(
                {'detail': 'Leave request not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if leave_request.status != LeaveRequest.STATUS_PENDING:
            return Response(
                {'detail': 'Only pending leave requests can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LeaveRequestApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        leave_request.status = LeaveRequest.STATUS_APPROVED
        leave_request.is_paid = serializer.validated_data['is_paid']
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.save()
        
        # Notify the employee about the approval
        message = f"Your request has been accepted by user: {request.user.username}"
        
        create_notification(
            recipient=leave_request.employee,
            title="Leave Request Approved",
            message=message,
            notification_type="leave_approved",
            actor=request.user,
            related_object_type="leave_request",
            related_object_id=str(leave_request.id)
        )
        
        response_serializer = LeaveRequestSerializer(leave_request)
        return Response(response_serializer.data)


class LeaveRequestRejectView(APIView):
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin']

    @extend_schema(
        operation_id='leave_request_reject',
        summary='Reject leave request',
        description='Reject a leave request with a reason. Admin only.',
        tags=['Leave Management'],
        request=LeaveRequestRejectSerializer,
        responses={200: LeaveRequestSerializer},
    )
    def post(self, request, pk):
        """Reject a leave request."""
        try:
            leave_request = LeaveRequest.objects.select_related('employee', 'approved_by').get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response(
                {'detail': 'Leave request not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if leave_request.status != LeaveRequest.STATUS_PENDING:
            return Response(
                {'detail': 'Only pending leave requests can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LeaveRequestRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        leave_request.status = LeaveRequest.STATUS_REJECTED
        leave_request.rejection_reason = serializer.validated_data['rejection_reason']
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.save()
        
        # Notify the employee about the rejection
        message = f"Your request has been rejected by user: {request.user.username}"
        
        create_notification(
            recipient=leave_request.employee,
            title="Leave Request Rejected",
            message=message,
            notification_type="leave_rejected",
            actor=request.user,
            related_object_type="leave_request",
            related_object_id=str(leave_request.id),
            metadata={'rejection_reason': rejection_reason}
        )
        
        response_serializer = LeaveRequestSerializer(leave_request)
        return Response(response_serializer.data)


class LeaveRequestConflictsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='leave_request_conflicts',
        summary='Check for leave conflicts',
        description='Check if a date range has conflicts with existing leave requests.',
        tags=['Leave Management'],
        responses={200: LeaveRequestSerializer(many=True)},
    )
    def get(self, request):
        """Check for conflicts in a date range."""
        employee_id_param = request.query_params.get('employee_id')
        start_date_param = request.query_params.get('start_date')
        end_date_param = request.query_params.get('end_date')
        
        user = request.user
        is_admin = user.is_admin()
        
        # Determine employee
        if employee_id_param and is_admin:
            try:
                employee_id = int(employee_id_param)
            except ValueError:
                return Response(
                    {'detail': 'Invalid employee_id.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            employee_id = user.id
        
        # Validate dates
        if not start_date_param:
            return Response(
                {'detail': 'start_date is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'detail': 'Invalid start_date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        end_date = start_date
        if end_date_param:
            try:
                end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'detail': 'Invalid end_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date < start_date:
            return Response(
                {'detail': 'end_date cannot be before start_date.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for conflicts
        User = get_user_model()
        try:
            employee = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Employee not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create a temporary leave request to use conflict detection
        temp_leave = LeaveRequest(
            employee=employee,
            leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
            start_date=start_date,
            end_date=end_date if end_date != start_date else None
        )
        
        conflicting = temp_leave.get_conflicting_leaves()
        serializer = LeaveRequestSerializer(conflicting, many=True)
        return Response(serializer.data)


class LeaveRequestCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='leave_request_calendar',
        summary='Get leave requests for calendar',
        description='Get leave requests grouped by date for calendar view.',
        tags=['Leave Management'],
        responses={200: drf_serializers.DictField()},
    )
    def get(self, request):
        """Get leave requests for calendar view."""
        year_param = request.query_params.get('year')
        month_param = request.query_params.get('month')
        employee_id_param = request.query_params.get('employee_id')
        
        user = request.user
        is_admin = user.is_admin()
        
        # Get year and month
        if year_param and month_param:
            try:
                year = int(year_param)
                month = int(month_param)
                if not (1 <= month <= 12):
                    return Response(
                        {'detail': 'month must be between 1 and 12'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except ValueError:
                return Response(
                    {'detail': 'year and month must be integers'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            today = timezone.localdate()
            year, month = today.year, today.month
        
        # Determine employee filter
        queryset = LeaveRequest.objects.select_related('employee', 'approved_by')
        
        if employee_id_param and is_admin:
            try:
                queryset = queryset.filter(employee_id=int(employee_id_param))
            except ValueError:
                pass
        elif not is_admin:
            queryset = queryset.filter(employee=user)
        
        # Filter by month
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
        queryset = queryset.filter(
            Q(start_date__lte=end, end_date__gte=start) |
            Q(start_date__lte=end, end_date__isnull=True, start_date__gte=start)
        )
        
        # Group by date
        calendar_data = defaultdict(list)
        for leave in queryset:
            effective_end = leave.end_date if leave.end_date else leave.start_date
            cur = leave.start_date
            while cur <= effective_end:
                if start <= cur <= end:
                    calendar_data[str(cur)].append(LeaveRequestSerializer(leave).data)
                cur += timedelta(days=1)
        
        return Response(dict(calendar_data))


check_in = AttendanceCheckInView.as_view()
check_out = AttendanceCheckOutView.as_view()
attendance_break_start = AttendanceBreakStartView.as_view()
attendance_break_end = AttendanceBreakEndView.as_view()
attendance_context = AttendanceContextView.as_view()
attendance_list = AttendanceListView.as_view()
attendance_me = MyAttendanceView.as_view()
attendance_summary = AttendanceSummaryView.as_view()
attendance_rules = AttendanceRuleView.as_view()
attendance_employees = AttendanceEmployeesView.as_view()
attendance_payroll = AttendancePayrollView.as_view()
attendance_overtime_list = AttendanceOvertimeListView.as_view()
attendance_overtime_verify = AttendanceOvertimeVerifyView.as_view()
attendance_monthly_hours = AttendanceMonthlyHoursView.as_view()
leave_request_list = LeaveRequestListView.as_view()
leave_request_detail = LeaveRequestDetailView.as_view()
leave_request_approve = LeaveRequestApproveView.as_view()
leave_request_reject = LeaveRequestRejectView.as_view()
leave_request_conflicts = LeaveRequestConflictsView.as_view()
leave_request_calendar = LeaveRequestCalendarView.as_view()
