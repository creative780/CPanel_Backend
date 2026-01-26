from rest_framework import serializers
from .models import Attendance, AttendanceRule, AttendanceBreak, Holiday, LeaveRequest


class NullableDecimalField(serializers.DecimalField):
    """Decimal field that treats blank strings as null."""

    def to_internal_value(self, value):
        if value in ("", None):
            return None
        return super().to_internal_value(value)


class AttendanceBreakSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    is_flagged = serializers.SerializerMethodField()
    flag_reason = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceBreak
        fields = [
            'id',
            'started_at',
            'ended_at',
            'duration_minutes',
            'duration_display',
            'is_active',
            'source',
            'notes',
            'metadata',
            'is_flagged',
            'flag_reason',
        ]
        read_only_fields = [
            'duration_minutes',
            'duration_display',
            'is_active',
            'metadata',
            'is_flagged',
            'flag_reason',
        ]

    def get_duration_display(self, obj):
        minutes = obj.current_duration_minutes
        hours, mins = divmod(minutes, 60)
        if hours:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def get_is_active(self, obj):
        return obj.is_active

    def get_is_flagged(self, obj):
        """Safely get is_flagged, returning False if column doesn't exist yet."""
        try:
            return getattr(obj, 'is_flagged', False)
        except AttributeError:
            return False

    def get_flag_reason(self, obj):
        """Safely get flag_reason, returning empty string if column doesn't exist yet."""
        try:
            return getattr(obj, 'flag_reason', '')
        except AttributeError:
            return ''


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    duration_display = serializers.CharField(read_only=True)
    device_name = serializers.SerializerMethodField()
    breaks = AttendanceBreakSerializer(many=True, read_only=True)
    total_break_minutes = serializers.IntegerField(read_only=True)
    effective_minutes = serializers.IntegerField(read_only=True)
    effective_hours = serializers.SerializerMethodField()
    active_break = serializers.SerializerMethodField()
    overtime_minutes = serializers.SerializerMethodField()
    overtime_hours = serializers.SerializerMethodField()
    is_monitored = serializers.SerializerMethodField()
    overtime_verified = serializers.SerializerMethodField()
    overtime_verified_by = serializers.SerializerMethodField()
    overtime_verified_at = serializers.SerializerMethodField()
    requires_verification = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id',
            'employee',
            'employee_name',
            'check_in',
            'check_out',
            'date',
            'total_hours',
            'notes',
            'status',
            'location_lat',
            'location_lng',
            'location_address',
            'ip_address',
            'device_id',
            'device_info',
            'device_name',
            'duration_display',
            'created_at',
            'updated_at',
            'total_break_minutes',
            'effective_minutes',
            'effective_hours',
            'breaks',
            'active_break',
            'overtime_minutes',
            'overtime_hours',
            'is_monitored',
            'overtime_verified',
            'overtime_verified_by',
            'overtime_verified_at',
            'requires_verification',
        ]
        read_only_fields = [
            'total_hours',
            'duration_display',
            'created_at',
            'updated_at',
            'total_break_minutes',
            'effective_minutes',
            'effective_hours',
            'breaks',
            'active_break',
            'overtime_minutes',
            'overtime_hours',
            'is_monitored',
            'overtime_verified',
            'overtime_verified_by',
            'overtime_verified_at',
            'requires_verification',
        ]

    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username

    def get_device_name(self, obj):
        name = (obj.device_name or '').strip()
        if name:
            return name
        # Do not expose device_id or user-agent as the display name
        return None

    def get_effective_hours(self, obj):
        return obj.effective_hours

    def get_active_break(self, obj):
        active = obj.active_break
        if not active:
            return None
        return {
            'id': active.id,
            'started_at': active.started_at,
            'duration_minutes': active.current_duration_minutes,
            'is_flagged': getattr(active, 'is_flagged', False),
            'flag_reason': getattr(active, 'flag_reason', ''),
        }

    def get_overtime_minutes(self, obj):
        """Safely get overtime_minutes, returning 0 if column doesn't exist yet."""
        try:
            return getattr(obj, 'overtime_minutes', 0)
        except (AttributeError, ValueError):
            return 0

    def get_overtime_hours(self, obj):
        """Safely get overtime_hours, returning 0 if column doesn't exist yet."""
        try:
            return getattr(obj, 'overtime_hours', 0.0)
        except (AttributeError, ValueError):
            return 0.0

    def get_is_monitored(self, obj):
        return obj.is_monitored

    def get_overtime_verified(self, obj):
        """Safely get overtime_verified, returning False if column doesn't exist yet."""
        try:
            return getattr(obj, 'overtime_verified', False)
        except (AttributeError, ValueError):
            return False

    def get_overtime_verified_by(self, obj):
        """Safely get overtime_verified_by, returning None if column doesn't exist yet."""
        try:
            verified_by = getattr(obj, 'overtime_verified_by', None)
            return verified_by.id if verified_by else None
        except (AttributeError, ValueError):
            return None

    def get_overtime_verified_at(self, obj):
        """Safely get overtime_verified_at, returning None if column doesn't exist yet."""
        try:
            return getattr(obj, 'overtime_verified_at', None)
        except (AttributeError, ValueError):
            return None

    def get_requires_verification(self, obj):
        """Safely get requires_verification, returning False if columns don't exist yet."""
        try:
            return getattr(obj, 'requires_verification', False)
        except (AttributeError, ValueError):
            return False


class CheckInSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    location_lat = NullableDecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    location_lng = NullableDecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    location_address = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.CharField(required=False, allow_blank=True)
    device_id = serializers.CharField(required=False, allow_blank=True)
    device_info = serializers.CharField(required=False, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_blank=True)


class CheckOutSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    location_lat = NullableDecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    location_lng = NullableDecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    location_address = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.CharField(required=False, allow_blank=True)
    device_id = serializers.CharField(required=False, allow_blank=True)
    device_info = serializers.CharField(required=False, allow_blank=True)
    device_name = serializers.CharField(required=False, allow_blank=True)


class AttendanceRuleSerializer(serializers.ModelSerializer):
    def validate_weekend_days(self, value):
        if value is None:
            return []
        cleaned = []
        for day in value:
            try:
                day_int = int(day)
            except (TypeError, ValueError):
                raise serializers.ValidationError('Weekend days must be integers between 0 and 6.')
            if day_int < 0 or day_int > 6:
                raise serializers.ValidationError('Weekend days must be integers between 0 and 6.')
            cleaned.append(day_int)
        return cleaned

    class Meta:
        model = AttendanceRule
        fields = [
            'work_start',
            'work_end',
            'grace_minutes',
            'standard_work_minutes',
            'overtime_after_minutes',
            'late_penalty_per_minute',
            'per_day_deduction',
            'overtime_rate_per_minute',
            'weekend_days',
            'min_break_minutes',
            'max_break_minutes',
            'grace_violation_deduction',
            'early_checkout_threshold_minutes',
            'early_checkout_deduction',
            'updated_at',
        ]
        read_only_fields = ['updated_at']


class BreakStartSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, max_length=255)
    source = serializers.ChoiceField(
        required=False,
        choices=AttendanceBreak.SOURCE_CHOICES,
    )


class BreakEndSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, max_length=255)


class OvertimeVerifySerializer(serializers.Serializer):
    attendance_id = serializers.IntegerField(required=True, help_text='ID of the attendance record to verify')


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = [
            'id',
            'date',
            'name',
            'is_recurring',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Serializer for LeaveRequest model with computed fields."""
    employee_name = serializers.SerializerMethodField()
    total_hours = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    leave_type_display = serializers.SerializerMethodField()
    conflicts = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id',
            'employee',
            'employee_name',
            'leave_type',
            'leave_type_display',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'hours',
            'reason',
            'status',
            'status_display',
            'is_paid',
            'approved_by',
            'approved_by_name',
            'approved_at',
            'rejection_reason',
            'created_at',
            'updated_at',
            'total_hours',
            'conflicts',
        ]
        read_only_fields = [
            'employee_name',
            'total_hours',
            'status_display',
            'leave_type_display',
            'conflicts',
            'approved_by_name',
            'created_at',
            'updated_at',
        ]
    
    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username
    
    def get_total_hours(self, obj):
        return obj.get_total_hours()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_leave_type_display(self, obj):
        return obj.get_leave_type_display()
    
    def get_conflicts(self, obj):
        """Return list of conflicting leave request IDs."""
        if obj.has_conflict():
            conflicting = obj.get_conflicting_leaves()
            if obj.pk:
                conflicting = conflicting.exclude(pk=obj.pk)
            return [leave.id for leave in conflicting[:5]]  # Limit to 5 to avoid large responses
        return []
    
    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name() or obj.approved_by.username
        return None


class LeaveRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating leave requests."""
    leave_type = serializers.ChoiceField(choices=LeaveRequest.LEAVE_TYPE_CHOICES)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    hours = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    reason = serializers.CharField()
    
    def validate(self, data):
        """Validate leave request data."""
        leave_type = data.get('leave_type')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        hours = data.get('hours')
        reason = data.get('reason')
        
        # Validate reason is provided
        if not reason or not reason.strip():
            raise serializers.ValidationError({'reason': 'Reason is mandatory for leave requests.'})
        
        # Validate end_date for multiple days
        if leave_type == LeaveRequest.LEAVE_TYPE_MULTIPLE_DAYS and not end_date:
            raise serializers.ValidationError({'end_date': 'End date is required for multiple days leave.'})
        
        # Validate end_date is after start_date
        if end_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': 'End date cannot be before start date.'})
        
        # Validate partial-day fields
        if leave_type == LeaveRequest.LEAVE_TYPE_PARTIAL_DAY:
            if not start_time and not hours:
                raise serializers.ValidationError({
                    'start_time': 'Either start_time/end_time or hours must be provided for partial-day leave.'
                })
            if start_time and end_time and end_time < start_time:
                raise serializers.ValidationError({'end_time': 'End time cannot be before start time.'})
        
        # Validate dates are not in the past (allow today)
        from django.utils import timezone
        today = timezone.localdate()
        if start_date < today:
            raise serializers.ValidationError({'start_date': 'Start date cannot be in the past.'})
        if end_date and end_date < today:
            raise serializers.ValidationError({'end_date': 'End date cannot be in the past.'})
        
        return data


class LeaveRequestApproveSerializer(serializers.Serializer):
    """Serializer for approving leave requests."""
    is_paid = serializers.BooleanField(default=False, help_text='Whether this leave is paid')


class LeaveRequestRejectSerializer(serializers.Serializer):
    """Serializer for rejecting leave requests."""
    rejection_reason = serializers.CharField(required=True, help_text='Reason for rejection')
