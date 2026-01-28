import base64
import re
import uuid
import json
import hashlib
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import (
    Employee, EmployeeActivity, EmployeeAsset, EmployeeSummary,
    Org, Device, DeviceToken, Heartbeat, Recording, RecordingSegment, Session
)
from .serializers import (
    EmployeeSerializer,
    TrackSerializer,
    ScreenshotUploadSerializer,
    ScreenshotDeleteSerializer,
    DeviceSerializer,
    HeartbeatSerializer,
    RecordingSerializer,
    RecordingIngestSerializer,
    FrameEncodingSerializer,
)
from .authentication import DeviceTokenAuthentication
from .error_handlers import (
    handle_monitoring_errors, log_api_request, log_heartbeat_received,
    log_screenshot_received, log_enrollment_attempt, log_configuration_change,
    validate_device_exists, validate_required_fields, create_error_response,
    create_success_response, log_error_with_context
)
from .auth_utils import (
    create_enrollment_token, verify_enrollment_token, create_device_token,
    authenticate_device_token, check_device_heartbeat_requirement,
    sign_payload, verify_payload_signature
)
from .storage import storage
from accounts.permissions import RolePermission
from drf_spectacular.utils import extend_schema
from notifications.services import notify_admins
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


# Legacy views for backward compatibility
class EmployeesListView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    @extend_schema(responses={200: EmployeeSerializer})
    def get(self, request):
        q = request.query_params.get('q', '')
        dept = request.query_params.get('dept')
        status_filter = request.query_params.get('status')
        queryset = Employee.objects.all()
        if q:
            queryset = queryset.filter(name__icontains=q)
        if dept:
            queryset = queryset.filter(department__iexact=dept)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        data = EmployeeSerializer(queryset, many=True).data
        return Response({'employees': data})


class TrackView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    @extend_schema(request=TrackSerializer, responses={200: None})
    def post(self, request):
        serializer = TrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_ids = serializer.validated_data['employeeIds']
        delta = serializer.validated_data.get('delta', {})
        action = serializer.validated_data.get('action', '')
        application = serializer.validated_data.get('application', '')
        when = serializer.validated_data['when']
        created = 0
        with transaction.atomic():
            for emp in Employee.objects.filter(id__in=employee_ids):
                EmployeeActivity.objects.create(
                    employee=emp,
                    when=when,
                    action=action,
                    application=application,
                    delta_k=delta.get('k', 0),
                    delta_c=delta.get('c', 0),
                )
                created += 1
        return Response({'created': created})


data_url_pattern = re.compile(r'^data:(?P<mime>image/(jpeg|png));base64,(?P<data>.+)$')


def _save_data_url(image_data_url: str) -> str:
    match = data_url_pattern.match(image_data_url)
    if not match:
        raise ValueError('Invalid image data URL')
    mime = match.group('mime')
    data_b64 = match.group('data')
    raw = base64.b64decode(data_b64)
    if len(raw) > 5 * 1024 * 1024:
        raise ValueError('File too large')
    ext = 'jpg' if 'jpeg' in mime else 'png'
    fname = f"screenshot_{uuid.uuid4().hex}.{ext}"
    # ensure media root exists
    upload_dir = settings.MEDIA_ROOT
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    full_path = Path(upload_dir) / fname
    with open(full_path, 'wb') as f:
        f.write(raw)
    return f"{settings.MEDIA_URL}{fname}"


class ScreenshotUploadView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    @extend_schema(request=ScreenshotUploadSerializer, responses={200: None})
    def post(self, request):
        serializer = ScreenshotUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee_ids = serializer.validated_data['employeeIds']
        when = serializer.validated_data['when']
        image_data_url = serializer.validated_data['imageDataUrl']
        try:
            url = _save_data_url(image_data_url)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            for emp in Employee.objects.filter(id__in=employee_ids):
                EmployeeAsset.objects.create(employee=emp, kind='screenshot', path=url)
                emp.last_screenshot_at = when
                emp.save(update_fields=['last_screenshot_at'])
        return Response({'url': url})


class ScreenshotDeleteView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    @extend_schema(request=ScreenshotDeleteSerializer, responses={200: None})
    def post(self, request):
        serializer = ScreenshotDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        emp_id = serializer.validated_data['employeeId']
        file_path = serializer.validated_data['file']
        try:
            asset = EmployeeAsset.objects.filter(employee_id=emp_id, path=file_path, kind='screenshot', deleted_at__isnull=True).latest('created_at')
        except EmployeeAsset.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        asset.deleted_at = timezone.now()
        asset.save(update_fields=['deleted_at'])
        # Try removing the file if under MEDIA_URL
        media_url = settings.MEDIA_URL.rstrip('/') + '/'
        if file_path.startswith(media_url):
            rel = file_path[len(media_url):]
            from pathlib import Path
            fp = Path(settings.MEDIA_ROOT) / rel
            if fp.exists():
                try:
                    fp.unlink()
                except Exception:
                    pass
        return Response({'deleted': True})


# New monitoring system views
class EnrollRequestView(APIView):
    """Request enrollment token for device"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        data = request.data
        os_name = data.get('os')
        hostname = data.get('hostname')
        
        if not os_name or not hostname:
            return Response(
                {'detail': 'OS and hostname are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment token
        org_id = request.user.org_id
        enrollment_token = create_enrollment_token(
            user_id=str(request.user.id),
            org_id=org_id
        )
        
        logger.info(f"Created enrollment token for user {request.user.email}")
        
        return Response({
            'enrollment_token': enrollment_token,
            'expires_in': 900  # 15 minutes
        })


class EnrollCompleteView(APIView):
    """Complete device enrollment with agent"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        logger.info("=" * 80)
        logger.info("Enrollment request received")
        logger.info(f"Request IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request path: {request.path}")
        
        data = request.data
        enrollment_token = data.get('enrollment_token')
        os_name = data.get('os')
        hostname = data.get('hostname')
        agent_version = data.get('agent_version')
        ip = data.get('ip') or request.META.get('REMOTE_ADDR')
        
        logger.info(f"Enrollment data received:")
        logger.info(f"  OS: {os_name}")
        logger.info(f"  Hostname: {hostname}")
        logger.info(f"  Agent Version: {agent_version}")
        logger.info(f"  IP: {ip}")
        logger.info(f"  Enrollment Token: {'***' + enrollment_token[-8:] if enrollment_token and len(enrollment_token) > 8 else '***'}")
        
        if not all([enrollment_token, os_name, hostname, agent_version]):
            missing = [k for k, v in {
                'enrollment_token': enrollment_token,
                'os': os_name,
                'hostname': hostname,
                'agent_version': agent_version
            }.items() if not v]
            logger.error(f"Missing required fields: {', '.join(missing)}")
            return Response(
                {'detail': f'All fields are required. Missing: {", ".join(missing)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            logger.info("Verifying enrollment token...")
            # Verify enrollment token
            payload = verify_enrollment_token(enrollment_token)
            user_id = payload['user_id']
            org_id = payload.get('org_id')
            
            logger.info(f"Token verified successfully. User ID: {user_id}, Org ID: {org_id}")
            
            logger.info(f"Looking up user: {user_id}")
            user = User.objects.get(id=user_id)
            logger.info(f"User found: {user.email}")
            
            # Create or update device
            # First, try to find existing device with same hostname and user
            logger.info(f"Checking for existing device: hostname={hostname}, user={user.email}")
            existing_devices = Device.objects.filter(
                current_user=user,
                hostname=hostname
            )
            
            if existing_devices.exists():
                # Use the most recent device
                device = existing_devices.order_by('-created_at').first()
                created = False
                logger.info(f"Found existing device: {device.id}. Updating...")
                
                # Update existing device
                device.os = os_name
                device.agent_version = agent_version
                device.ip = ip  # Update IP on re-enrollment
                device.save()
                logger.info(f"Device {device.id} updated successfully")
            else:
                # Create new device
                logger.info("Creating new device...")
                device = Device.objects.create(
                    current_user=user,
                    hostname=hostname,
                    os=os_name,
                    agent_version=agent_version,
                    org=org_id,
                    status='OFFLINE',
                    ip=ip
                )
                created = True
                logger.info(f"New device created: {device.id}")
            
            # Create device token
            logger.info("Creating device token...")
            device_token = create_device_token(device)
            logger.info(f"Device token created. Expires at: {device_token.expires_at}")
            
            logger.info("=" * 80)
            logger.info(f"Device enrolled successfully!")
            logger.info(f"  Device ID: {device.id}")
            logger.info(f"  User: {user.email}")
            logger.info(f"  Hostname: {hostname}")
            logger.info(f"  OS: {os_name}")
            logger.info(f"  Agent Version: {agent_version}")
            logger.info(f"  IP: {ip}")
            logger.info(f"  Created: {created}")
            logger.info("=" * 80)
            
            return Response({
                'device_id': device.id,
                'device_token': device_token.secret,
                'expires_at': device_token.expires_at.isoformat()
            })
            
        except AuthenticationFailed as e:
            logger.error("=" * 80)
            logger.error(f"Enrollment failed: Authentication error")
            logger.error(f"Error: {str(e)}")
            logger.error("=" * 80)
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            logger.error("=" * 80)
            logger.error(f"Enrollment failed: User not found")
            logger.error(f"User ID from token: {user_id if 'user_id' in locals() else 'Unknown'}")
            logger.error("=" * 80)
            return Response(
                {'detail': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"Enrollment failed: Unexpected error")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            logger.error("=" * 80)
            return Response(
                {'detail': f'Enrollment failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HeartbeatView(APIView):
    """Device heartbeat endpoint"""
    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [permissions.AllowAny]
    
    @handle_monitoring_errors
    @log_api_request
    def post(self, request):
        # Device is already authenticated by DeviceTokenAuthentication
        device = request.auth  # This is the device object from authentication
        
        # Check if device authentication failed
        if not device:
            logger.error("Heartbeat request failed: Device not authenticated")
            return Response(
                {'detail': 'Device authentication failed'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Handle both DRF and Django request objects
        if hasattr(request, 'data'):
            data = request.data
        else:
            # Fallback for Django WSGIRequest (for testing)
            import json
            try:
                data = json.loads(request.body.decode('utf-8')) if request.body else {}
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = {}
        
        # Log heartbeat reception
        if device:
            log_heartbeat_received(device.id, {
                'cpu_percent': data.get('cpu_percent', data.get('cpu', 0.0)),
                'mem_percent': data.get('mem_percent', data.get('mem', 0.0)),
                'active_window': data.get('active_window', data.get('activeWindow')),
                'is_locked': data.get('is_locked', data.get('isLocked', False)),
            })
        
        # Sanitize helpers
        def to_float(val, default=0.0):
            try:
                v = float(val)
                if v != v or v in (float('inf'), float('-inf')):
                    return default
                return v
            except Exception:
                return default

        def to_int(val, default=0):
            try:
                return int(val)
            except Exception:
                return default

        def to_bool(val, default=False):
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ("1", "true", "yes", "y")
            return default

        def clamp(v, lo, hi):
            try:
                return max(lo, min(hi, v))
            except Exception:
                return lo

        cpu_percent = clamp(to_float(data.get('cpu_percent', data.get('cpu', 0.0)), 0.0), 0.0, 100.0)
        mem_percent = clamp(to_float(data.get('mem_percent', data.get('mem', 0.0)), 0.0), 0.0, 100.0)
        active_window = data.get('active_window', data.get('activeWindow'))
        # DB column is CharField(max_length=255); ensure we don't exceed it
        if isinstance(active_window, str):
            active_window = active_window[:255]
        is_locked = to_bool(data.get('is_locked', data.get('isLocked', False)), False)
        
        # Get IP from request body (sent by agent) or fallback to REMOTE_ADDR
        ip = data.get('ip') or request.META.get('REMOTE_ADDR')
        
        # Phase 2: Enhanced monitoring data (sanitized)
        keystroke_count = clamp(to_int(data.get('keystroke_count', 0), 0), 0, 10_000_000)
        mouse_click_count = clamp(to_int(data.get('mouse_click_count', 0), 0), 0, 10_000_000)
        productivity_score = clamp(to_float(data.get('productivity_score', 0.0), 0.0), 0.0, 100.0)
        keystroke_rate_per_minute = clamp(to_float(data.get('keystroke_rate_per_minute', 0.0), 0.0), 0.0, 1000.0)
        click_rate_per_minute = clamp(to_float(data.get('click_rate_per_minute', 0.0), 0.0), 0.0, 1000.0)
        active_time_minutes = clamp(to_float(data.get('active_time_minutes', 0.0), 0.0), 0.0, 1_000_000.0)
        session_duration_minutes = clamp(to_float(data.get('session_duration_minutes', 0.0), 0.0), 0.0, 1_000_000.0)

        top_applications_in = data.get('top_applications', {}) or {}
        top_applications = {}
        if isinstance(top_applications_in, dict):
            try:
                for i, (k, v) in enumerate(top_applications_in.items()):
                    if i >= 10:
                        break
                    key = str(k)[:100]
                    val = to_float(v, 0.0)
                    top_applications[key] = val
            except Exception:
                top_applications = {}
        else:
            top_applications = {}

        idle_alert = to_bool(data.get('idle_alert', False), False)
        
        # Create heartbeat record with user snapshots and enhanced data
        try:
            user_id_snapshot = None
            if device.current_user and hasattr(device.current_user, 'id'):
                user_id_snapshot = device.current_user.id
            elif hasattr(device, 'current_user_id') and device.current_user_id:
                user_id_snapshot = device.current_user_id
            
            heartbeat = Heartbeat.objects.create(
                device=device,
                cpu_percent=cpu_percent,
                mem_percent=mem_percent,
                active_window=active_window,
                is_locked=is_locked,
                ip=ip,
                user_id_snapshot=user_id_snapshot,
                user_name_snapshot=getattr(device, 'current_user_name', None),
                user_role_snapshot=getattr(device, 'current_user_role', None),
                # Phase 2: Enhanced fields (will be ignored if not in model)
                keystroke_count=keystroke_count,
                mouse_click_count=mouse_click_count,
                productivity_score=productivity_score,
                keystroke_rate_per_minute=keystroke_rate_per_minute,
                click_rate_per_minute=click_rate_per_minute,
                active_time_minutes=active_time_minutes,
                session_duration_minutes=session_duration_minutes,
                top_applications=top_applications,
                idle_alert=idle_alert
            )
        except Exception as e:
            logger.error(f"Failed to create heartbeat: {e}")
            return Response(
                {'detail': 'Failed to create heartbeat record'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Handle idle alert if present
        if idle_alert:
            # Create idle alert record if IdleAlert model exists
            try:
                from .models import IdleAlert
                idle_duration = 30  # Default threshold
                IdleAlert.objects.create(
                    device=device,
                    idle_duration_minutes=idle_duration
                )
                # Send notification to admins
                notify_admins(
                    title="Device Idle Alert",
                    message=f"Device {device.hostname} ({device.id}) has been idle for {idle_duration} minutes",
                    notification_type="monitoring_device_idle",
                    related_object_type="device",
                    related_object_id=device.id,
                    metadata={'device_id': device.id, 'idle_time': idle_duration, 'hostname': device.hostname}
                )
            except ImportError:
                # IdleAlert model doesn't exist yet, skip
                pass
        
        # Update device status
        device.last_heartbeat = timezone.now()
        device.ip = ip
        
        if is_locked:
            device.status = 'IDLE'
        else:
            device.status = 'ONLINE'
        
        device.save()
        
        # Emit WebSocket events for real-time updates (optional - gracefully handle Redis connection issues)
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            if channel_layer:
                # Send to monitoring group
                async_to_sync(channel_layer.group_send)(
                    'monitoring_updates',
                    {
                        'type': 'heartbeat_update',
                        'device_id': device.id,
                        'heartbeat': {
                            'cpu_percent': cpu_percent,
                            'mem_percent': mem_percent,
                            'active_window': active_window,
                            'is_locked': is_locked,
                            'keystroke_count': keystroke_count,
                            'mouse_click_count': mouse_click_count,
                            'productivity_score': productivity_score,
                            'timestamp': timezone.now().isoformat()
                        }
                    }
                )
                
                # Send to device-specific group
                async_to_sync(channel_layer.group_send)(
                    f'device_{device.id}',
                    {
                        'type': 'device_heartbeat',
                        'heartbeat': {
                            'cpu_percent': cpu_percent,
                            'mem_percent': mem_percent,
                            'active_window': active_window,
                            'is_locked': is_locked,
                            'keystroke_count': keystroke_count,
                            'mouse_click_count': mouse_click_count,
                            'productivity_score': productivity_score,
                            'timestamp': timezone.now().isoformat()
                        }
                    }
                )
        except Exception as e:
            # Log the error but don't fail the heartbeat
            logger.warning(f"WebSocket event emission failed (Redis not available?): {e}")
        
        logger.debug(f"Heartbeat received from device {device.id}")
        
        # Check if device token needs renewal (expires within 7 days)
        try:
            # Access device token via the OneToOne relationship
            device_token = None
            try:
                device_token = device.token
            except DeviceToken.DoesNotExist:
                logger.debug(f"Device {device.id} has no token record (this is OK for new devices)")
            except AttributeError:
                # Device model might not have token attribute directly
                device_token = DeviceToken.objects.filter(device=device).first()
            
            if device_token:
                days_until_expiry = (device_token.expires_at - timezone.now()).days
                
                if days_until_expiry <= 7:
                    logger.info(f"Device token for {device.id} expires in {days_until_expiry} days. Renewing...")
                    from monitoring.auth_utils import create_device_token
                    new_token = create_device_token(device, expires_days=14)
                    logger.info(f"New device token created for {device.id}. Expires: {new_token.expires_at}")
                    
                    return Response({
                        'ok': True,
                        'token_renewed': True,
                        'device_token': new_token.secret,
                        'device_id': device.id,
                        'expires_at': new_token.expires_at.isoformat()
                    })
                else:
                    logger.debug(f"Device token for {device.id} expires in {days_until_expiry} days (no renewal needed)")
        except Exception as e:
            # Log error but don't fail heartbeat if token check fails
            logger.warning(f"Failed to check/renew device token: {e}")
            import traceback
            logger.debug(f"Token renewal error traceback: {traceback.format_exc()}")
        
        return Response({'ok': True})


class ScreenshotIngestView(APIView):
    """Screenshot ingestion endpoint - DEPRECATED: Use RecordingIngestView instead"""
    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Deprecated endpoint - screenshots are no longer supported"""
        return Response(
            {
                'detail': 'Screenshot ingestion is deprecated. Please use /api/ingest/recording endpoint for video recordings instead.',
                'deprecated': True,
                'alternative_endpoint': '/api/ingest/recording'
            }, 
            status=status.HTTP_410_GONE
        )


class RecordingIngestView(APIView):
    """Recording ingestion endpoint for video uploads"""
    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [permissions.AllowAny]
    
    @handle_monitoring_errors
    @log_api_request
    def post(self, request):
        # Device is already authenticated by DeviceTokenAuthentication
        device = request.auth  # This is the device object from authentication
        
        # Check if device authentication failed
        if not device:
            logger.error("Recording request failed: Device not authenticated")
            return Response(
                {'detail': 'Device authentication failed'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get video file from request
        video_file = request.FILES.get('video')
        if not video_file:
            return Response(
                {'detail': 'Video file is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse form data
        start_time_str = request.data.get('start_time')
        end_time_str = request.data.get('end_time')
        duration_seconds_str = request.data.get('duration_seconds')
        is_idle_period = request.data.get('is_idle_period', 'false').lower() in ('true', '1', 'yes')
        idle_start_offset_str = request.data.get('idle_start_offset')
        
        # Validate required fields
        if not all([start_time_str, end_time_str, duration_seconds_str]):
            return Response(
                {'detail': 'start_time, end_time, and duration_seconds are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Parse datetime strings - try multiple formats
            try:
                from dateutil import parser as date_parser
                start_time = date_parser.parse(start_time_str)
                end_time = date_parser.parse(end_time_str)
            except ImportError:
                # Fallback to Django's timezone parser if dateutil not available
                from django.utils.dateparse import parse_datetime
                start_time = parse_datetime(start_time_str)
                end_time = parse_datetime(end_time_str)
                if not start_time or not end_time:
                    raise ValueError("Invalid datetime format")
                # Convert to timezone-aware if not already
                if timezone.is_naive(start_time):
                    start_time = timezone.make_aware(start_time)
                if timezone.is_naive(end_time):
                    end_time = timezone.make_aware(end_time)
            duration_seconds = float(duration_seconds_str)
            idle_start_offset = float(idle_start_offset_str) if idle_start_offset_str else None
            
            # Read video file
            video_bytes = video_file.read()
            
            # Calculate SHA256 for deduplication
            sha256_hash = hashlib.sha256(video_bytes).hexdigest()
            
            # Generate storage keys
            date_str = timezone.now().strftime('%Y/%m/%d')
            org_prefix = getattr(device, 'org_id', None) if device else "default"
            if device:
                org_prefix = org_prefix or "default"
                blob_key = f"{org_prefix}/{device.id}/{date_str}/{sha256_hash}.mp4"
                thumb_key = f"{org_prefix}/{device.id}/{date_str}/{sha256_hash}-thumb.jpg"
            else:
                blob_key = f"default/unknown/{date_str}/{sha256_hash}.mp4"
                thumb_key = f"default/unknown/{date_str}/{sha256_hash}-thumb.jpg"
            
            # Store video file
            import asyncio
            asyncio.run(storage.put(blob_key, video_bytes, 'video/mp4'))
            
            # Generate thumbnail from video (first frame)
            thumb_data = None
            try:
                import subprocess
                import tempfile
                import os
                
                # Create temporary files
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
                    temp_video.write(video_bytes)
                    temp_video_path = temp_video.name
                
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_thumb:
                    temp_thumb_path = temp_thumb.name
                
                try:
                    # Use ffmpeg to extract first frame
                    subprocess.run([
                        'ffmpeg', '-i', temp_video_path,
                        '-ss', '00:00:00',
                        '-vframes', '1',
                        '-q:v', '2',
                        temp_thumb_path
                    ], check=True, capture_output=True, timeout=10)
                    
                    # Read thumbnail
                    with open(temp_thumb_path, 'rb') as f:
                        thumb_data = f.read()
                    
                    # Store thumbnail
                    if thumb_data:
                        asyncio.run(storage.put(thumb_key, thumb_data, 'image/jpeg'))
                finally:
                    # Clean up temp files
                    try:
                        os.unlink(temp_video_path)
                        os.unlink(temp_thumb_path)
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Failed to generate thumbnail from video: {e}")
                # Continue without thumbnail - it's optional
            
            # Create recording record with user snapshots
            try:
                user_id_snapshot = None
                if device.current_user and hasattr(device.current_user, 'id'):
                    user_id_snapshot = device.current_user.id
                elif hasattr(device, 'current_user_id') and device.current_user_id:
                    user_id_snapshot = device.current_user_id
                
                # thumb_key is required, so use empty string if no thumbnail
                final_thumb_key = thumb_key if thumb_data else ""
                
                recording = Recording.objects.create(
                    device=device,
                    blob_key=blob_key,
                    thumb_key=final_thumb_key,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration_seconds,
                    is_idle_period=is_idle_period,
                    idle_start_offset=idle_start_offset,
                    user_id_snapshot=user_id_snapshot,
                    user_name_snapshot=getattr(device, 'current_user_name', None),
                    user_role_snapshot=getattr(device, 'current_user_role', None),
                )
            except Exception as e:
                logger.error(f"Failed to create recording: {e}", exc_info=True)
                return Response(
                    {'detail': f'Failed to create recording record: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Emit WebSocket events for real-time updates
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                if channel_layer:
                    # Send to monitoring group
                    async_to_sync(channel_layer.group_send)(
                        'monitoring_updates',
                        {
                            'type': 'recording_update',
                            'device_id': device.id,
                            'recording': {
                                'id': recording.id,
                                'thumb_url': f'/api/monitoring/files/{final_thumb_key}' if final_thumb_key else None,
                                'start_time': start_time.isoformat(),
                                'duration_seconds': duration_seconds
                            }
                        }
                    )
                    
                    # Send to device-specific group
                    async_to_sync(channel_layer.group_send)(
                        f'device_{device.id}',
                        {
                            'type': 'device_recording',
                            'recording': {
                                'id': recording.id,
                                'thumb_url': f'/api/monitoring/files/{final_thumb_key}' if final_thumb_key else None,
                                'start_time': start_time.isoformat(),
                                'duration_seconds': duration_seconds
                            }
                        }
                    )
            except Exception as e:
                # Log the error but don't fail the recording ingestion
                logger.warning(f"WebSocket event emission failed (Redis not available?): {e}")
            
            logger.info(f"Recording ingested for device {device.id}")
            
            return Response({'status': 'ok'})
            
        except ValueError as e:
            logger.error(f"Invalid data format: {e}")
            return Response(
                {'detail': f'Invalid data format: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to ingest recording: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to process recording'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FrameEncodingView(APIView):
    """Frame encoding endpoint for server-side video encoding (Hybrid Approach)"""
    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [permissions.AllowAny]
    
    @handle_monitoring_errors
    @log_api_request
    def post(self, request):
        # Device is already authenticated by DeviceTokenAuthentication
        device = request.auth  # This is the device object from authentication
        
        # Check if device authentication failed
        if not device:
            logger.error("Frame encoding request failed: Device not authenticated")
            return Response(
                {'detail': 'Device authentication failed'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Validate request payload
        serializer = FrameEncodingSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid frame encoding request: {serializer.errors}")
            return Response(
                {'detail': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        frames_b64 = serializer.validated_data['frames']
        metadata = serializer.validated_data['metadata']
        
        # Extract metadata
        segment_start_str = metadata.get('segment_start')
        segment_end_str = metadata.get('segment_end')
        segment_index = metadata.get('segment_index')
        segment_id = metadata.get('segment_id')
        date_str = metadata.get('date')
        duration_seconds = float(metadata.get('duration_seconds', 0))
        
        if not all([segment_start_str, segment_end_str]):
            return Response(
                {'detail': 'segment_start and segment_end are required in metadata'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Parse datetime strings
            try:
                from dateutil import parser as date_parser
                start_time = date_parser.parse(segment_start_str)
                end_time = date_parser.parse(segment_end_str)
            except ImportError:
                # Fallback to Django's timezone parser if dateutil not available
                from django.utils.dateparse import parse_datetime
                start_time = parse_datetime(segment_start_str)
                end_time = parse_datetime(segment_end_str)
                if not start_time or not end_time:
                    raise ValueError("Invalid datetime format")
                # Convert to timezone-aware if not already
                if timezone.is_naive(start_time):
                    start_time = timezone.make_aware(start_time)
                if timezone.is_naive(end_time):
                    end_time = timezone.make_aware(end_time)
            
            # Decode base64 frames to JPEG bytes, then to numpy arrays
            import numpy as np
            from PIL import Image
            import io
            import platform
            
            frames = []
            for i, frame_b64 in enumerate(frames_b64):
                try:
                    # Decode base64 to JPEG bytes
                    jpeg_bytes = base64.b64decode(frame_b64)
                    
                    # Convert JPEG bytes to PIL Image
                    img = Image.open(io.BytesIO(jpeg_bytes))
                    
                    # Convert PIL Image to numpy array (RGB format)
                    frame_array = np.array(img)
                    
                    # Ensure uint8 dtype
                    if frame_array.dtype != np.uint8:
                        frame_array = (frame_array * 255).astype(np.uint8) if frame_array.max() <= 1.0 else frame_array.astype(np.uint8)
                    
                    frames.append(frame_array)
                except Exception as e:
                    logger.warning(f"Failed to decode frame {i}: {e}")
                    continue
            
            if not frames:
                logger.error("No frames successfully decoded")
                return Response(
                    {'detail': 'Failed to decode any frames'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get frame dimensions from first frame
            first_frame = frames[0]
            height, width = first_frame.shape[:2]
            
            logger.info(f"Encoding {len(frames)} frames for device {device.id}, segment {segment_index}")
            
            # Encode frames to MP4 using FFmpeg
            video_bytes = None
            try:
                # Check if FFmpeg is available
                import subprocess
                import shutil
                
                # Find FFmpeg binary
                ffmpeg_binary = shutil.which('ffmpeg')
                if not ffmpeg_binary:
                    # Try to find ffmpeg.exe in current directory (Windows)
                    import os
                    if os.path.exists('ffmpeg.exe'):
                        ffmpeg_binary = os.path.abspath('ffmpeg.exe')
                    elif os.path.exists(os.path.join(settings.BASE_DIR, 'ffmpeg.exe')):
                        ffmpeg_binary = os.path.join(settings.BASE_DIR, 'ffmpeg.exe')
                
                if not ffmpeg_binary:
                    logger.error("FFmpeg binary not found on server")
                    return Response(
                        {
                            'detail': 'FFmpeg is not installed on the server. Please install FFmpeg to enable server-side encoding.',
                            'error_code': 'FFMPEG_NOT_FOUND'
                        }, 
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                
                # Set FFMPEG_BINARY environment variable for ffmpeg-python
                import os
                os.environ['FFMPEG_BINARY'] = ffmpeg_binary
                # Also add to PATH if not already there
                ffmpeg_dir = os.path.dirname(ffmpeg_binary)
                if ffmpeg_dir not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
                
                logger.info(f"Using FFmpeg binary: {ffmpeg_binary}")
                
                # Import ffmpeg-python
                import ffmpeg
                import tempfile
                
                # On Windows, use temp files instead of pipes to avoid errno 22 issues
                use_temp_files = platform.system() == 'Windows'
                
                if use_temp_files:
                    # Use temporary files for input and output (Windows workaround)
                    with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as tmp_input:
                        input_path = tmp_input.name
                    
                    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_output:
                        output_path = tmp_output.name
                    
                    try:
                        # Write frames to temporary input file
                        with open(input_path, 'wb') as f:
                            for frame in frames:
                                if frame.dtype != np.uint8:
                                    frame = (frame * 255).astype(np.uint8)
                                f.write(frame.tobytes())
                        
                        # Use FFmpeg with file input/output
                        # Match agent's encoding parameters exactly
                        (
                            ffmpeg
                            .input(input_path, format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}', r=10)
                            .output(output_path, format='mp4', vcodec='libx264', preset='ultrafast', crf=28, 
                                   movflags='faststart', pix_fmt='yuv420p')
                            .overwrite_output()
                            .run(quiet=True)
                        )
                        
                        # Read encoded video
                        with open(output_path, 'rb') as f:
                            video_bytes = f.read()
                        
                        logger.info(f"Video encoded successfully using ffmpeg-python (H.264) with temp files: {len(video_bytes)} bytes")
                        
                    finally:
                        # Clean up temp files
                        for path in [input_path, output_path]:
                            if os.path.exists(path):
                                try:
                                    os.unlink(path)
                                except:
                                    pass
                else:
                    # Use pipes for non-Windows systems (Linux/Mac)
                    process = (
                        ffmpeg
                        .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}', r=10)
                        .output('pipe:', format='mp4', vcodec='libx264', preset='ultrafast', crf=28, 
                               movflags='faststart', pix_fmt='yuv420p')
                        .overwrite_output()
                        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
                    )
                    
                    # Write frames to stdin
                    for frame in frames:
                        if frame.dtype != np.uint8:
                            frame = (frame * 255).astype(np.uint8)
                        process.stdin.write(frame.tobytes())
                    
                    process.stdin.close()
                    video_bytes = process.stdout.read()
                    process.wait()
                    
                    if process.returncode != 0:
                        stderr = process.stderr.read().decode() if process.stderr else "Unknown error"
                        raise Exception(f"FFmpeg encoding failed (return code {process.returncode}): {stderr}")
                    
                    logger.info(f"Video encoded successfully using ffmpeg-python (H.264): {len(video_bytes)} bytes")
                
            except ImportError:
                logger.error("ffmpeg-python package not installed")
                return Response(
                    {
                        'detail': 'ffmpeg-python package is not installed. Please install it to enable server-side encoding.',
                        'error_code': 'FFMPEG_PYTHON_NOT_INSTALLED'
                    }, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            except Exception as e:
                logger.error(f"FFmpeg encoding failed: {e}", exc_info=True)
                return Response(
                    {
                        'detail': f'Video encoding failed: {str(e)}',
                        'error_code': 'ENCODING_FAILED'
                    }, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            if not video_bytes:
                logger.error("Video encoding produced no output")
                return Response(
                    {'detail': 'Video encoding produced no output'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Calculate SHA256 for deduplication
            sha256_hash = hashlib.sha256(video_bytes).hexdigest()
            
            # Generate storage keys
            if not date_str:
                date_str = timezone.now().strftime('%Y/%m/%d')
            org_prefix = getattr(device, 'org_id', None) if device else "default"
            if device:
                org_prefix = org_prefix or "default"
                blob_key = f"{org_prefix}/{device.id}/{date_str}/{sha256_hash}.mp4"
                thumb_key = f"{org_prefix}/{device.id}/{date_str}/{sha256_hash}-thumb.jpg"
            else:
                blob_key = f"default/unknown/{date_str}/{sha256_hash}.mp4"
                thumb_key = f"default/unknown/{date_str}/{sha256_hash}-thumb.jpg"
            
            # Store video file
            import asyncio
            asyncio.run(storage.put(blob_key, video_bytes, 'video/mp4'))
            
            # Generate thumbnail from first frame using FFmpeg
            thumb_data = None
            try:
                import subprocess
                import tempfile
                import os
                
                # Convert first frame to JPEG bytes
                first_img = Image.fromarray(frames[0])
                jpeg_buffer = io.BytesIO()
                first_img.save(jpeg_buffer, format='JPEG', quality=85)
                first_frame_jpeg = jpeg_buffer.getvalue()
                
                # Create temporary files
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_input:
                    temp_input.write(first_frame_jpeg)
                    temp_input_path = temp_input.name
                
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_thumb:
                    temp_thumb_path = temp_thumb.name
                
                try:
                    # Use ffmpeg to process thumbnail (resize/optimize if needed)
                    # For now, just copy the JPEG, but we could resize it
                    subprocess.run([
                        'ffmpeg', '-i', temp_input_path,
                        '-vf', 'scale=320:-1',  # Resize to width 320, maintain aspect ratio
                        '-q:v', '2',
                        temp_thumb_path
                    ], check=True, capture_output=True, timeout=10)
                    
                    # Read thumbnail
                    with open(temp_thumb_path, 'rb') as f:
                        thumb_data = f.read()
                    
                    # Store thumbnail
                    if thumb_data:
                        asyncio.run(storage.put(thumb_key, thumb_data, 'image/jpeg'))
                finally:
                    # Clean up temp files
                    try:
                        os.unlink(temp_input_path)
                        os.unlink(temp_thumb_path)
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Failed to generate thumbnail from first frame: {e}")
                # Continue without thumbnail - it's optional
            
            # Create recording record with user snapshots
            try:
                user_id_snapshot = None
                if device.current_user and hasattr(device.current_user, 'id'):
                    user_id_snapshot = device.current_user.id
                elif hasattr(device, 'current_user_id') and device.current_user_id:
                    user_id_snapshot = device.current_user_id
                
                # thumb_key is required, so use empty string if no thumbnail
                final_thumb_key = thumb_key if thumb_data else ""
                
                # Parse is_idle_period from metadata if present
                is_idle_period = metadata.get('is_idle_period', False)
                idle_start_offset = metadata.get('idle_start_offset')
                if idle_start_offset is not None:
                    idle_start_offset = float(idle_start_offset)
                
                recording = Recording.objects.create(
                    device=device,
                    blob_key=blob_key,
                    thumb_key=final_thumb_key,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration_seconds,
                    is_idle_period=is_idle_period,
                    idle_start_offset=idle_start_offset,
                    user_id_snapshot=user_id_snapshot,
                    user_name_snapshot=getattr(device, 'current_user_name', None),
                    user_role_snapshot=getattr(device, 'current_user_role', None),
                )
            except Exception as e:
                logger.error(f"Failed to create recording: {e}", exc_info=True)
                return Response(
                    {'detail': f'Failed to create recording record: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Emit WebSocket events for real-time updates
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                if channel_layer:
                    # Send to monitoring group
                    async_to_sync(channel_layer.group_send)(
                        'monitoring_updates',
                        {
                            'type': 'recording_update',
                            'device_id': device.id,
                            'recording': {
                                'id': recording.id,
                                'thumb_url': f'/api/monitoring/files/{final_thumb_key}' if final_thumb_key else None,
                                'start_time': start_time.isoformat(),
                                'duration_seconds': duration_seconds
                            }
                        }
                    )
                    
                    # Send to device-specific group
                    async_to_sync(channel_layer.group_send)(
                        f'device_{device.id}',
                        {
                            'type': 'device_recording',
                            'recording': {
                                'id': recording.id,
                                'thumb_url': f'/api/monitoring/files/{final_thumb_key}' if final_thumb_key else None,
                                'start_time': start_time.isoformat(),
                                'duration_seconds': duration_seconds
                            }
                        }
                    )
            except Exception as e:
                # Log the error but don't fail the recording ingestion
                logger.warning(f"WebSocket event emission failed (Redis not available?): {e}")
            
            logger.info(f"Frame encoding completed for device {device.id}, segment {segment_index}, recording {recording.id}")
            
            return Response({
                'status': 'ok',
                'recording_id': recording.id,
                'blob_key': blob_key,
                'thumb_key': final_thumb_key if final_thumb_key else None
            })
            
        except ValueError as e:
            logger.error(f"Invalid data format: {e}")
            return Response(
                {'detail': f'Invalid data format: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to encode frames: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to process frame encoding'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminDevicesListView(APIView):
    """List devices for admin monitoring"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    
    def _get_authenticated_url(self, file_path, request):
        """Generate URL for file access"""
        return f"/api/files/{file_path}"
    
    def get(self, request):
        # Get query parameters
        status_filter = request.GET.get('status')
        org_filter = request.GET.get('org')
        os_filter = request.GET.get('os')
        search_query = request.GET.get('q')
        
        # Build queryset
        devices = Device.objects.select_related('current_user').prefetch_related(
            'heartbeats', 'recordings'
        ).all()
        
        if status_filter:
            devices = devices.filter(status=status_filter)
        
        if org_filter:
            devices = devices.filter(org_id=org_filter)
        
        if os_filter:
            devices = devices.filter(os__icontains=os_filter)
        
        if search_query:
            from django.db import models
            devices = devices.filter(
                models.Q(hostname__icontains=search_query) |
                models.Q(current_user__email__icontains=search_query) |
                models.Q(current_user__first_name__icontains=search_query) |
                models.Q(current_user__last_name__icontains=search_query)
            )
        
        # Serialize devices with latest heartbeat and recording
        device_data = []
        for device in devices:
            latest_heartbeat = device.heartbeats.order_by('-created_at').first()
            latest_recording = device.recordings.order_by('-start_time').first()
            
            device_info = {
                'id': device.id,
                'hostname': device.hostname,
                'os': device.os,
                'agent_version': getattr(device, 'agent_version', None),
                'status': device.status,
                'ip': device.ip,
                'enrolled_at': device.enrolled_at.isoformat(),
                'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                'screenshot_freq_sec': getattr(device, 'screenshot_freq_sec', 30),
                'user': {
                    'id': device.current_user.id if device.current_user else None,
                    'email': device.current_user.email if device.current_user else None,
                    'name': device.current_user_name or (f"{device.current_user.first_name} {device.current_user.last_name}".strip() if device.current_user else None)
                } if device.current_user else None,
                'current_user': {
                    'id': device.current_user.id if device.current_user else None,
                    'email': device.current_user.email if device.current_user else None,
                    'name': device.current_user_name or (f"{device.current_user.first_name} {device.current_user.last_name}".strip() if device.current_user else None),
                    'role': device.current_user_role
                } if device.current_user else None,
                'org': {
                    'id': device.org.id,
                    'name': device.org.name
                } if device.org else None,
                'latest_heartbeat': {
                    'cpu_percent': latest_heartbeat.cpu_percent,
                    'mem_percent': latest_heartbeat.mem_percent,
                    'active_window': latest_heartbeat.active_window,
                    'is_locked': latest_heartbeat.is_locked,
                    'created_at': latest_heartbeat.created_at.isoformat(),
                    # Phase 2: Enhanced monitoring data
                    'keystroke_count': getattr(latest_heartbeat, 'keystroke_count', 0),
                    'mouse_click_count': getattr(latest_heartbeat, 'mouse_click_count', 0),
                    'productivity_score': getattr(latest_heartbeat, 'productivity_score', 0.0),
                    'keystroke_rate_per_minute': getattr(latest_heartbeat, 'keystroke_rate_per_minute', 0.0),
                    'click_rate_per_minute': getattr(latest_heartbeat, 'click_rate_per_minute', 0.0),
                    'active_time_minutes': getattr(latest_heartbeat, 'active_time_minutes', 0.0),
                    'session_duration_minutes': getattr(latest_heartbeat, 'session_duration_minutes', 0.0),
                    'top_applications': getattr(latest_heartbeat, 'top_applications', {}),
                    'idle_alert': getattr(latest_heartbeat, 'idle_alert', False)
                } if latest_heartbeat else None,
                'latest_recording': {
                    'id': latest_recording.id,
                    'thumb_url': self._get_authenticated_url(latest_recording.thumb_key, request) if latest_recording.thumb_key else None,
                    'start_time': latest_recording.start_time.isoformat(),
                    'duration_seconds': latest_recording.duration_seconds
                } if latest_recording else None,
                'latest_thumb': latest_recording.thumb_key if latest_recording and latest_recording.thumb_key else None
            }
            device_data.append(device_info)
        
        return Response({'devices': device_data})


class AdminDeviceDetailView(APIView):
    """Get detailed device information"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    
    def get(self, request, device_id):
        try:
            device = Device.objects.select_related('current_user').prefetch_related(
                'heartbeats', 'recordings'
            ).get(id=device_id)
        except Device.DoesNotExist:
            return Response(
                {'detail': 'Device not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get paginated recordings
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        offset = (page - 1) * page_size
        
        recordings = device.recordings.order_by('-start_time')[offset:offset + page_size]
        heartbeats = device.heartbeats.order_by('-created_at')[:100]  # Last 100 heartbeats
        
        device_data = {
            'id': device.id,
            'hostname': device.hostname,
            'os': device.os,
            'agent_version': getattr(device, 'agent_version', None),
            'status': device.status,
            'ip': device.ip,
            'enrolled_at': device.enrolled_at.isoformat(),
            'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
            'screenshot_freq_sec': getattr(device, 'screenshot_freq_sec', 30),
            'user': {
                'id': device.current_user.id if device.current_user else None,
                'email': device.current_user.email if device.current_user else None,
                'name': device.current_user_name or (f"{device.current_user.first_name} {device.current_user.last_name}".strip() if device.current_user else None)
            } if device.current_user else None,
            'current_user': {
                'id': device.current_user.id if device.current_user else None,
                'email': device.current_user.email if device.current_user else None,
                'name': device.current_user_name or (f"{device.current_user.first_name} {device.current_user.last_name}".strip() if device.current_user else None),
                'role': device.current_user_role
            } if device.current_user else None,
            'org': {
                'id': device.org.id,
                'name': device.org.name
            } if device.org else None,
            'recordings': [
                {
                    'id': r.id,
                    'start_time': r.start_time.isoformat(),
                    'end_time': r.end_time.isoformat(),
                    'duration_seconds': r.duration_seconds,
                    'is_idle_period': r.is_idle_period,
                    'idle_start_offset': r.idle_start_offset,
                    'thumb_url': f"/api/monitoring/files/{r.thumb_key}" if r.thumb_key else None,
                    'video_url': f"/api/monitoring/files/{r.blob_key}",
                    'created_at': r.created_at.isoformat()
                }
                for r in recordings
            ],
            'heartbeats': [
                {
                    'id': h.id,
                    'cpu_percent': h.cpu_percent,
                    'mem_percent': h.mem_percent,
                    'active_window': h.active_window,
                    'is_locked': h.is_locked,
                    'ip': h.ip,
                    'created_at': h.created_at.isoformat()
                }
                for h in heartbeats
            ]
        }
        
        return Response(device_data)




class AdminScreenshotsView(APIView):
    """Admin endpoint to view employee screenshots - DEPRECATED: Use AdminRecordingsView instead"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    
    def get(self, request):
        """Deprecated endpoint - screenshots are no longer supported"""
        return Response(
            {
                'detail': 'Screenshot viewing is deprecated. Please use /api/admin/recordings endpoint for video recordings instead.',
                'deprecated': True,
                'alternative_endpoint': '/api/admin/recordings'
            }, 
            status=status.HTTP_410_GONE
        )


class AdminRecordingsView(APIView):
    """Admin endpoint to view recordings"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    
    def _get_authenticated_url(self, file_path, request):
        """Generate URL for file access"""
        if not file_path or file_path.strip() == "":
            return None
        # Use /api/files/ to match test expectations and provide cleaner URLs
        return f"/api/files/{file_path}"
    
    def get(self, request):
        """Get recordings for all devices or a specific device"""
        try:
            device_id = request.query_params.get('device_id')
            limit = int(request.query_params.get('limit', 50))
            offset = int(request.query_params.get('offset', 0))
            
            # Build query
            recordings_query = Recording.objects.select_related('device', 'device__current_user')
            
            if device_id:
                recordings_query = recordings_query.filter(device_id=device_id)
            
            # Order by most recent first (start_time descending)
            recordings_query = recordings_query.order_by('-start_time')
            
            # Get total count before pagination
            total = recordings_query.count()
            
            # Apply pagination
            recordings = recordings_query[offset:offset + limit]
            
            # Serialize with device and user info
            result = []
            for recording in recordings:
                # Use current_user if available, otherwise use user_name_snapshot
                user_name = "Unknown User"
                
                if recording.device.current_user:
                    user_name = f"{recording.device.current_user.first_name} {recording.device.current_user.last_name}".strip()
                    if not user_name:
                        user_name = recording.device.current_user.email
                elif recording.user_name_snapshot:
                    user_name = recording.user_name_snapshot
                
                result.append({
                    'id': recording.id,
                    'device_id': recording.device.id,
                    'device_name': recording.device.hostname,
                    'user_name': user_name,
                    'start_time': recording.start_time.isoformat(),
                    'end_time': recording.end_time.isoformat(),
                    'duration_seconds': recording.duration_seconds,
                    'is_idle_period': recording.is_idle_period,
                    'idle_start_offset': recording.idle_start_offset,
                    'video_url': self._get_authenticated_url(recording.blob_key, request),
                    'thumbnail_url': self._get_authenticated_url(recording.thumb_key, request),
                    'created_at': recording.created_at.isoformat(),
                })
            
            logger.info(f"Returning {len(result)} recordings for device {device_id}")
            
            return Response({
                'recordings': result,
                'total': total,
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            logger.error(f"Error in AdminRecordingsView: {e}", exc_info=True)
            return Response(
                {'detail': 'Failed to fetch recordings'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminEmployeeActivityView(APIView):
    """Admin endpoint to view employee activity summary"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    
    def get(self, request):
        """Get activity summary for all employees"""
        # Get recent heartbeats (last 24 hours)
        from django.utils import timezone
        from datetime import timedelta
        
        recent_threshold = timezone.now() - timedelta(hours=24)
        
        # Get all devices with recent activity
        devices = Device.objects.filter(
            last_heartbeat__gte=recent_threshold
        ).select_related('current_user').prefetch_related('heartbeats', 'recordings')
        
        result = []
        for device in devices:
            # Get recent heartbeats
            recent_heartbeats = device.heartbeats.filter(created_at__gte=recent_threshold)
            
            # Get recent recordings
            recent_recordings = device.recordings.filter(start_time__gte=recent_threshold)
            
            # Calculate activity metrics
            total_heartbeats = recent_heartbeats.count()
            total_recordings = recent_recordings.count()
            
            # Get latest activity
            latest_heartbeat = recent_heartbeats.order_by('-created_at').first()
            latest_recording = recent_recordings.order_by('-start_time').first()
            
            result.append({
                'device_id': device.id,
                'device_name': device.hostname,
                'user_name': f"{device.current_user.first_name} {device.current_user.last_name}".strip() if device.current_user else None,
                'user_email': device.current_user.email if device.current_user else None,
                'status': device.status,
                'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                'total_heartbeats_24h': total_heartbeats,
                'total_recordings_24h': total_recordings,
                'latest_cpu': latest_heartbeat.cpu_percent if latest_heartbeat else None,
                'latest_memory': latest_heartbeat.mem_percent if latest_heartbeat else None,
                'latest_window': latest_heartbeat.active_window if latest_heartbeat else None,
                'latest_recording': latest_recording.start_time.isoformat() if latest_recording else None,
            })
        
        return Response({
            'employees': result,
            'total_active': len(result)
        })


class AgentContextView(APIView):
    """Agent context endpoint - returns current user binding for device"""
    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get current user context for this device"""
        device = request.auth  # Device object from authentication
        
        if not device:
            return Response({'error': 'Device not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if device.current_user:
            context = {
                'user': {
                    'id': device.current_user.id,
                    'name': device.current_user_name,
                    'role': device.current_user_role,
                }
            }
        else:
            context = {'user': None}
        
        return Response(context)


class AgentDownloadView(APIView):
    """Agent installer download endpoint"""
    permission_classes = [permissions.AllowAny]  # Allow anyone to download the agent
    
    def get(self, request):
        """Download the agent installer for the detected OS"""
        import os
        from django.http import FileResponse, Http404, HttpResponse
        from django.conf import settings
        
        # Get OS from user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Check if a specific file is requested via query parameter
        requested_file = request.GET.get('file', None)
        if requested_file:
            # User explicitly requested a specific file (e.g., the executable)
            # Try to find and serve that file directly
            possible_paths = [
                os.path.join(settings.BASE_DIR, '..', 'agent', 'dist'),
                os.path.join(settings.BASE_DIR, 'media', 'agents'),
                os.path.join(settings.MEDIA_ROOT, 'agents'),
                os.path.join(settings.MEDIA_ROOT, 'uploads', 'agents'),
                '/home/api.crm.click2print.store/agents',
            ]
            
            for agent_dir in possible_paths:
                test_path = os.path.join(agent_dir, requested_file)
                if os.path.exists(test_path):
                    # Determine content type based on file extension
                    if requested_file.endswith('.exe'):
                        content_type = 'application/octet-stream'
                    elif requested_file.endswith('.ps1'):
                        content_type = 'application/x-powershell'
                    elif requested_file.endswith('.bat'):
                        content_type = 'application/x-msdos-program'
                    else:
                        content_type = 'application/octet-stream'
                    
                    response = FileResponse(open(test_path, 'rb'), content_type=content_type)
                    response['Content-Disposition'] = f'attachment; filename="{requested_file}"'
                    response['Content-Length'] = os.path.getsize(test_path)
                    return response
            
            # File not found, raise 404
            raise Http404(f"Requested file '{requested_file}' not found")
        
        # Determine the correct installer file (prefer newest builds first)
        installers = []
        if 'win' in user_agent:
            installers = [
                ('agent-installer.ps1', 'application/x-powershell'),
                ('agent-installer.bat', 'application/x-msdos-program'),
                ('crm-monitoring-agent-windows-amd64.exe', 'application/octet-stream'),
                ('install-agent-windows.bat', 'application/x-msdos-program'),
                ('crm-monitoring-agent.exe', 'application/octet-stream'),
            ]
        elif 'mac' in user_agent:
            installers = [
                ('agent-installer.pkg', 'application/octet-stream'),
                ('agent-installer.sh', 'application/x-sh'),
            ]
        elif 'linux' in user_agent:
            installers = [
                ('agent-installer-linux.sh', 'application/x-sh'),
                ('agent-installer.sh', 'application/x-sh'),
            ]
        else:
            # Default to Windows candidates for unknown OS (highest success rate)
            installers = [
                ('crm-monitoring-agent-windows-amd64.exe', 'application/octet-stream'),
                ('install-agent-windows.bat', 'application/x-msdos-program'),
                ('crm-monitoring-agent.exe', 'application/octet-stream'),
            ]
        default_installer_name = installers[0][0] if installers else 'crm-monitoring-agent.exe'
        
        # Try multiple locations for agent files
        possible_paths = [
            os.path.join(settings.BASE_DIR, '..', 'agent', 'dist'),  # Development path
            os.path.join(settings.BASE_DIR, 'media', 'agents'),      # Production path
            os.path.join(settings.MEDIA_ROOT, 'agents'),             # Media root path
            os.path.join(settings.MEDIA_ROOT, 'uploads', 'agents'),  # Uploads path
            '/home/api.crm.click2print.store/agents',                # Server path
        ]
        
        selected_filename = None
        selected_content_type = None
        file_path = None
        for candidate_name, candidate_type in installers:
            for agent_dir in possible_paths:
                test_path = os.path.join(agent_dir, candidate_name)
                if os.path.exists(test_path):
                    file_path = test_path
                    selected_filename = candidate_name
                    selected_content_type = candidate_type
                    break
            if file_path:
                break
        
        # If no file found, try Windows executable in all locations
        if not file_path:
            for fallback_name in ('crm-monitoring-agent.exe',):
                for agent_dir in possible_paths:
                    test_path = os.path.join(agent_dir, fallback_name)
                    if os.path.exists(test_path):
                        file_path = test_path
                        selected_filename = fallback_name
                        selected_content_type = 'application/octet-stream'
                        break
                if file_path:
                    break
        
        # If still no file found, create a generic installer script
        if not file_path:
            # If mac/linux requested, fall back to generating a shell installer script
            if default_installer_name.endswith('.sh'):
                return self._create_installer_script(request, default_installer_name)
            else:
                raise Http404("Agent installer not found. Please contact administrator to upload agent files.")
        
        # For .bat files, dynamically inject server URL and enrollment token
        if selected_filename and selected_filename.endswith('.bat') and file_path:
            try:
                # Helper function to escape special characters for batch files
                def escape_batch_token(token):
                    """Escape special characters for batch file syntax"""
                    if not token:
                        return token
                    # In batch files, we need to escape special characters
                    # Double quotes need to be doubled
                    token = token.replace('"', '""')
                    # Escape other special characters that could break batch syntax
                    token = token.replace('&', '^&')
                    token = token.replace('|', '^|')
                    token = token.replace('<', '^<')
                    token = token.replace('>', '^>')
                    # Escape caret itself (must be done last)
                    token = token.replace('^', '^^')
                    return token
                
                # Read the template .bat file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    bat_content = f.read()
                
                # Get server URL and token from request
                server_url = f"{request.scheme}://{request.get_host()}"
                enrollment_token = request.GET.get('token', '')
                
                # Inject server URL (replace both localhost and 127.0.0.1 variants)
                bat_content = bat_content.replace(
                    'set "SERVER_URL=http://127.0.0.1:8000"',
                    f'set "SERVER_URL={server_url}"'
                )
                bat_content = bat_content.replace(
                    'set "SERVER_URL=http://localhost:8000"',
                    f'set "SERVER_URL={server_url}"'
                )
                
                # If token provided, inject it as default TOKEN value
                if enrollment_token:
                    # Escape special characters in token
                    escaped_token = escape_batch_token(enrollment_token)
                    # Replace empty token with the provided token (properly escaped)
                    bat_content = bat_content.replace(
                        'set "TOKEN="',
                        f'set "TOKEN={escaped_token}"'
                    )
                
                # Serve modified content
                download_name = selected_filename or os.path.basename(file_path)
                response = HttpResponse(bat_content, content_type=selected_content_type or 'application/x-msdos-program')
                response['Content-Disposition'] = f'attachment; filename="{download_name}"'
                response['Content-Length'] = len(bat_content.encode('utf-8'))
                return response
            except Exception as e:
                # If dynamic generation fails, fall back to static file
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to dynamically generate .bat file: {e}. Falling back to static file.", exc_info=True)
        
        # For .ps1 files, dynamically inject server URL and enrollment token
        if selected_filename and selected_filename.endswith('.ps1') and file_path:
            try:
                # Helper function to escape special characters for PowerShell
                def escape_powershell_token(token):
                    """Escape special characters for PowerShell string syntax"""
                    if not token:
                        return token
                    # In PowerShell, we need to escape backticks, dollar signs, and quotes
                    token = token.replace('`', '``')
                    token = token.replace('$', '`$')
                    token = token.replace('"', '`"')
                    return token
                
                # Read the template .ps1 file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    ps1_content = f.read()
                
                # Get server URL and token from request
                server_url = f"{request.scheme}://{request.get_host()}"
                enrollment_token = request.GET.get('token', '')
                
                # Inject server URL (replace default localhost value)
                ps1_content = ps1_content.replace(
                    '$SERVER_URL = "http://localhost:8000"',
                    f'$SERVER_URL = "{server_url}"'
                )
                ps1_content = ps1_content.replace(
                    '$SERVER_URL = "http://127.0.0.1:8000"',
                    f'$SERVER_URL = "{server_url}"'
                )
                
                # If token provided, inject it as default TOKEN value
                if enrollment_token:
                    escaped_token = escape_powershell_token(enrollment_token)
                    ps1_content = ps1_content.replace(
                        '$TOKEN = ""',
                        f'$TOKEN = "{escaped_token}"'
                    )
                
                # Serve modified content
                download_name = selected_filename or os.path.basename(file_path)
                response = HttpResponse(ps1_content, content_type='application/x-powershell')
                response['Content-Disposition'] = f'attachment; filename="{download_name}"'
                response['Content-Length'] = len(ps1_content.encode('utf-8'))
                return response
            except Exception as e:
                # If dynamic generation fails, fall back to static file
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to dynamically generate .ps1 file: {e}. Falling back to static file.", exc_info=True)
        
        # Serve the file as-is (for non-.bat/.ps1 files or if dynamic generation failed)
        response = FileResponse(open(file_path, 'rb'), content_type=selected_content_type or 'application/octet-stream')
        download_name = selected_filename or os.path.basename(file_path)
        response['Content-Disposition'] = f'attachment; filename="{download_name}"'
        response['Content-Length'] = os.path.getsize(file_path)
        
        return response
    
    def _create_installer_script(self, request, filename):
        """Create a generic installer script for Unix-like systems"""
        import os
        from django.http import HttpResponse
        
        # Get enrollment token from query params
        enrollment_token = request.GET.get('token', '')
        
        # Get server URL from request
        server_url = f"{request.scheme}://{request.get_host()}"
        
        if 'mac' in request.META.get('HTTP_USER_AGENT', '').lower():
            script_content = f"""#!/bin/bash
# CRM Monitoring Agent Installer for macOS

echo "Installing CRM Monitoring Agent for macOS..."

# Create installation directory
INSTALL_DIR="$HOME/Library/Application Support/CRM_Agent"
mkdir -p "$INSTALL_DIR"

# Download Python dependencies
echo "Installing Python dependencies..."
pip3 install requests mss psutil Pillow websocket-client

# Create agent script
cat > "$INSTALL_DIR/agent.py" << 'EOF'
import requests
import time
import platform
import socket
import json
import base64
import hashlib
from datetime import datetime
from pathlib import Path

class MonitoringAgent:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.device_token = None
        self.device_id = None
        self.config_file = Path.home() / ".creative_connect_agent_config.json"
        
    def enroll_device(self, enrollment_token):
        try:
            response = requests.post(
                f"{server_url}/api/enroll/complete",
                json={{
                    "enrollment_token": enrollment_token,
                    "os": platform.system(),
                    "hostname": socket.gethostname(),
                    "agent_version": "1.0.0"
                }},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.device_token = data.get("device_token")
                self.device_id = data.get("device_id")
                print(f"Device enrolled successfully! Device ID: {{self.device_id}}")
                return True
            else:
                print(f"Enrollment failed: {{response.status_code}}")
                return False
        except Exception as e:
            print(f"Enrollment error: {{e}}")
            return False
    
    def send_heartbeat(self):
        if not self.device_token:
            return False
        try:
            response = requests.post(
                f"{server_url}/api/ingest/heartbeat",
                headers={{"Authorization": f"Bearer {{self.device_token}}", "Content-Type": "application/json"}},
                json={{"cpu": 0.0, "mem": 0.0, "activeWindow": "Unknown", "isLocked": False, "timestamp": time.time()}},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def run(self, enrollment_token=None):
        if not self.device_token and enrollment_token:
            if not self.enroll_device(enrollment_token):
                return False
        
        if not self.device_token:
            print("No device token available. Please enroll first.")
            return False
        
        print(f"Agent running for device {{self.device_id}}")
        try:
            while True:
                self.send_heartbeat()
                time.sleep(30)
        except KeyboardInterrupt:
            print("Agent stopped by user")
        return True

if __name__ == "__main__":
    import sys
    agent = MonitoringAgent()
    agent.run("{enrollment_token}")
EOF

# Make agent executable
chmod +x "$INSTALL_DIR/agent.py"

# Create LaunchAgent plist for auto-start
cat > "$HOME/Library/LaunchAgents/com.company.crmagent.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.company.crmagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>$INSTALL_DIR/agent.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load the LaunchAgent
launchctl load "$HOME/Library/LaunchAgents/com.company.crmagent.plist"

echo "Installation completed!"
echo "Agent installed to: $INSTALL_DIR"
echo "Auto-start enabled via LaunchAgent"
"""
        else:
            script_content = f"""#!/bin/bash
# CRM Monitoring Agent Installer for Linux

echo "Installing CRM Monitoring Agent for Linux..."

# Create installation directory
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user requests mss psutil Pillow websocket-client

# Create agent script
cat > "$INSTALL_DIR/crm-agent" << 'EOF'
import requests
import time
import platform
import socket
import json
import base64
import hashlib
from datetime import datetime
from pathlib import Path

class MonitoringAgent:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.device_token = None
        self.device_id = None
        self.config_file = Path.home() / ".creative_connect_agent_config.json"
        
    def enroll_device(self, enrollment_token):
        try:
            response = requests.post(
                f"{server_url}/api/enroll/complete",
                json={{
                    "enrollment_token": enrollment_token,
                    "os": platform.system(),
                    "hostname": socket.gethostname(),
                    "agent_version": "1.0.0"
                }},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.device_token = data.get("device_token")
                self.device_id = data.get("device_id")
                print(f"Device enrolled successfully! Device ID: {{self.device_id}}")
                return True
            else:
                print(f"Enrollment failed: {{response.status_code}}")
                return False
        except Exception as e:
            print(f"Enrollment error: {{e}}")
            return False
    
    def send_heartbeat(self):
        if not self.device_token:
            return False
        try:
            response = requests.post(
                f"{server_url}/api/ingest/heartbeat",
                headers={{"Authorization": f"Bearer {{self.device_token}}", "Content-Type": "application/json"}},
                json={{"cpu": 0.0, "mem": 0.0, "activeWindow": "Unknown", "isLocked": False, "timestamp": time.time()}},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def run(self, enrollment_token=None):
        if not self.device_token and enrollment_token:
            if not self.enroll_device(enrollment_token):
                return False
        
        if not self.device_token:
            print("No device token available. Please enroll first.")
            return False
        
        print(f"Agent running for device {{self.device_id}}")
        try:
            while True:
                self.send_heartbeat()
                time.sleep(30)
        except KeyboardInterrupt:
            print("Agent stopped by user")
        return True

if __name__ == "__main__":
    import sys
    agent = MonitoringAgent()
    agent.run("{enrollment_token}")
EOF

# Make agent executable
chmod +x "$INSTALL_DIR/crm-agent"

# Create systemd user service for auto-start
mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/crm-agent.service" << EOF
[Unit]
Description=CRM Monitoring Agent
After=network.target

[Service]
ExecStart=$INSTALL_DIR/crm-agent
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# Enable and start the service
systemctl --user enable crm-agent.service
systemctl --user start crm-agent.service

echo "Installation completed!"
echo "Agent installed to: $INSTALL_DIR"
echo "Auto-start enabled via systemd"
"""

        response = HttpResponse(script_content, content_type='application/x-sh')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class AdminDeviceConfigView(APIView):
    """Admin endpoint to manage device configuration"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    
    @handle_monitoring_errors
    @log_api_request
    def get(self, request, device_id):
        """Get device configuration"""
        try:
            device = Device.objects.get(id=device_id)
            
            # Get current configuration (stored in device model or separate config)
            config = {
                'screenshot_freq_sec': getattr(device, 'screenshot_freq_sec', 15),
                'heartbeat_freq_sec': getattr(device, 'heartbeat_freq_sec', 20),
                'auto_start': getattr(device, 'auto_start', True),
                'debug_mode': getattr(device, 'debug_mode', False),
                'pause_monitoring': getattr(device, 'pause_monitoring', False),
                'max_screenshot_storage_days': getattr(device, 'max_screenshot_storage_days', 30),
                'keystroke_monitoring': getattr(device, 'keystroke_monitoring', True),
                'mouse_click_monitoring': getattr(device, 'mouse_click_monitoring', True),
                'productivity_tracking': getattr(device, 'productivity_tracking', True),
                'idle_detection': getattr(device, 'idle_detection', True),
                'idle_threshold_minutes': getattr(device, 'idle_threshold_minutes', 30),
            }
            
            return Response(config)
            
        except Device.DoesNotExist:
            return Response(
                {'detail': 'Device not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting device config: {e}")
            return Response(
                {'detail': 'Failed to get device configuration'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @handle_monitoring_errors
    @log_api_request
    def put(self, request, device_id):
        """Update device configuration"""
        try:
            device = Device.objects.get(id=device_id)
            
            # Log configuration change
            log_configuration_change(device_id, request.data, request.user.id if request.user else None)
            
            # Update device configuration fields
            config_fields = [
                'screenshot_freq_sec', 'heartbeat_freq_sec', 'auto_start', 
                'debug_mode', 'pause_monitoring', 'max_screenshot_storage_days',
                'keystroke_monitoring', 'mouse_click_monitoring', 'productivity_tracking',
                'idle_detection', 'idle_threshold_minutes'
            ]
            
            for field in config_fields:
                if field in request.data:
                    setattr(device, field, request.data[field])
            
            device.save()
            
            # Emit WebSocket event for configuration change
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f'device_{device.id}',
                        {
                            'type': 'config_update',
                            'config': request.data
                        }
                    )
            except Exception as e:
                logger.warning(f"WebSocket event emission failed (Redis not available?): {e}")
            
            logger.info(f"Device configuration updated for device {device_id}")
            
            return Response({'detail': 'Configuration updated successfully'})
            
        except Device.DoesNotExist:
            return Response(
                {'detail': 'Device not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating device config: {e}")
            return Response(
                {'detail': 'Failed to update device configuration'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Create your views here.
