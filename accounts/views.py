from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from uuid import uuid4
import logging
import threading

logger = logging.getLogger(__name__)
User = get_user_model()

def _log_login_event_sync(request, user):
    """Synchronous logging function - runs in background thread"""
    try:
        from activity_log.models import ActivityEvent, Source
        from activity_log.permissions import user_role
        from activity_log.utils.hashing import compute_event_hash
        from app.common.net_utils import get_client_ip, resolve_client_hostname

        role = user_role(user) or "SYSTEM"
        # Prefer explicit fields from JSON body, then headers, then DNS fallback
        body_device_id = None
        body_device_name = None
        body_ip = None
        try:
            data = request.data if hasattr(request, 'data') else {}
            body_device_id = (data.get('device_id') or data.get('deviceId'))
            body_device_name = (data.get('device_name') or data.get('deviceName'))
            body_ip = (data.get('ip') or data.get('ip_address'))
        except Exception:
            pass

        ip_address = (body_ip or get_client_ip(request) or request.META.get("REMOTE_ADDR") or "").strip() or None
        device_id = (
            body_device_id
            or request.headers.get("X-Device-Id")
            or request.META.get("HTTP_X_DEVICE_ID")
        )
        device_name_hdr = (
            body_device_name
            or request.headers.get("X-Device-Name")
            or request.META.get("HTTP_X_DEVICE_NAME")
        )
        device_name = (device_name_hdr or resolve_client_hostname(ip_address))
        device_info = request.META.get("HTTP_USER_AGENT")
        ctx = {
            "ip": ip_address,  # legacy key used by logs page
            "user_agent": device_info,  # legacy key
            "ip_address": ip_address,
            "device_id": device_id,
            "device_name": device_name,
            "device_info": device_info,
            "severity": "info",
            "tags": ["auth"],
        }
        # canonical payload for hashing
        canon = {
            "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tenant_id": "default",
            "actor": {"id": str(user.id), "role": role},
            "verb": "LOGIN",
            "target": {"type": "User", "id": str(user.id)},
            "source": "FRONTEND",
            "request_id": f"req_{uuid4().hex}",
            "context": ctx,
        }
        ev_hash = compute_event_hash(canon)
        ActivityEvent.objects.create(
            timestamp=timezone.now(),
            actor_id=user.id,
            actor_role=role,
            verb="LOGIN",
            target_type="User",
            target_id=str(user.id),
            context=ctx,
            source=Source.FRONTEND,
            request_id=canon["request_id"],
            tenant_id="default",
            hash=ev_hash,
        )
    except Exception:
        # do not break auth on logging errors, but log details for troubleshooting
        logger.exception("Failed to log LOGIN activity event")


def _log_login_event(request, user):
    """Log login event in background thread to avoid blocking response"""
    # Store request data in a thread-safe way
    request_data = {}
    request_headers = {}
    request_meta = {}
    
    try:
        if hasattr(request, 'data'):
            request_data = dict(request.data) if request.data else {}
        request_headers = dict(request.headers) if hasattr(request, 'headers') else {}
        request_meta = dict(request.META) if hasattr(request, 'META') else {}
    except Exception:
        pass
    
    # Create a copy of request attributes for the thread
    class RequestCopy:
        def __init__(self, data, headers, meta):
            self.data = data
            self.headers = headers
            self.META = meta
    
    request_copy = RequestCopy(request_data, request_headers, request_meta)
    
    # Run logging in background thread
    thread = threading.Thread(
        target=_log_login_event_sync,
        args=(request_copy, user),
        daemon=True
    )
    thread.start()


def _log_failed_login_event_sync(request, username, error_message=None):
    """Log failed login attempt with detailed logging"""
    logger.info(f"[FAILED_LOGIN_LOG] Starting to log failed login attempt for username: {username}")
    try:
        from activity_log.models import ActivityEvent, Source, ActorRole
        from activity_log.utils.hashing import compute_event_hash
        from app.common.net_utils import get_client_ip, resolve_client_hostname

        # Validate username
        if not username or not isinstance(username, str):
            logger.warning(f"[FAILED_LOGIN_LOG] Invalid username provided: {username}, type: {type(username)}")
            username = str(username) if username else "unknown"
        
        logger.debug(f"[FAILED_LOGIN_LOG] Username validated: {username}")

        # Extract context similar to successful login
        body_device_id = None
        body_device_name = None
        body_ip = None
        try:
            data = request.data if hasattr(request, 'data') else {}
            body_device_id = (data.get('device_id') or data.get('deviceId'))
            body_device_name = (data.get('device_name') or data.get('deviceName'))
            body_ip = (data.get('ip') or data.get('ip_address'))
            logger.debug(f"[FAILED_LOGIN_LOG] Extracted from request body: device_id={body_device_id}, device_name={body_device_name}, ip={body_ip}")
        except Exception as ex:
            logger.warning(f"[FAILED_LOGIN_LOG] Error extracting body data: {ex}")

        ip_address = (body_ip or get_client_ip(request) or request.META.get("REMOTE_ADDR") or "").strip() or None
        device_id = (
            body_device_id
            or request.headers.get("X-Device-Id")
            or request.META.get("HTTP_X_DEVICE_ID")
        )
        device_name_hdr = (
            body_device_name
            or request.headers.get("X-Device-Name")
            or request.META.get("HTTP_X_DEVICE_NAME")
        )
        device_name = (device_name_hdr or resolve_client_hostname(ip_address))
        device_info = request.META.get("HTTP_USER_AGENT")
        
        logger.debug(f"[FAILED_LOGIN_LOG] Extracted IP: {ip_address}, Device ID: {device_id}, Device Name: {device_name}")
        
        ctx = {
            "ip": ip_address,
            "ip_address": ip_address,
            "device_id": device_id,
            "device_name": device_name,
            "device_info": device_info,
            "user_agent": device_info,
            "username": username,  # Store attempted username
            "severity": "high",
            "tags": ["auth", "security"],
            "success": False,
            "status": "failed",
            "error": error_message or "Invalid credentials",
        }
        logger.debug(f"[FAILED_LOGIN_LOG] Context created: {ctx}")
        
        # canonical payload for hashing
        canon = {
            "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tenant_id": "default",
            "actor": {"id": None, "role": "SYSTEM"},  # No user for failed attempts
            "verb": "LOGIN",
            "target": {"type": "User", "id": username},  # Use username as target
            "source": "FRONTEND",
            "request_id": f"req_{uuid4().hex}",
            "context": ctx,
        }
        logger.debug(f"[FAILED_LOGIN_LOG] Canonical payload created")
        
        ev_hash = compute_event_hash(canon)
        logger.debug(f"[FAILED_LOGIN_LOG] Event hash computed: {ev_hash[:16]}...")
        
        logger.info(f"[FAILED_LOGIN_LOG] Creating ActivityEvent in database...")
        event = ActivityEvent.objects.create(
            timestamp=timezone.now(),
            actor_id=None,  # No user for failed attempts
            actor_role=ActorRole.SYSTEM,
            verb="LOGIN",
            target_type="User",
            target_id=username,
            context=ctx,
            source=Source.FRONTEND,
            request_id=canon["request_id"],
            tenant_id="default",
            hash=ev_hash,
        )
        logger.info(f"[FAILED_LOGIN_LOG] ✅ Successfully logged failed login attempt: event_id={event.id}, username={username}, ip={ip_address}, error={error_message}")
        return event
    except ImportError as e:
        logger.error(f"[FAILED_LOGIN_LOG] ❌ Import error while logging failed login: {e}", exc_info=True)
    except Exception as e:
        # do not break auth on logging errors
        logger.exception(f"[FAILED_LOGIN_LOG] ❌ Failed to log FAILED LOGIN activity event: {e}")
        logger.error(f"[FAILED_LOGIN_LOG] Username was: {username}, Error message was: {error_message}")
    return None


def _log_failed_login_event(request, username, error_message=None):
    """Log failed login event in background thread to avoid blocking response"""
    # Store request data in a thread-safe way
    request_data = {}
    request_headers = {}
    request_meta = {}
    
    try:
        if hasattr(request, 'data'):
            request_data = dict(request.data) if request.data else {}
        request_headers = dict(request.headers) if hasattr(request, 'headers') else {}
        request_meta = dict(request.META) if hasattr(request, 'META') else {}
    except Exception:
        pass
    
    # Create a copy of request attributes for the thread
    class RequestCopy:
        def __init__(self, data, headers, meta):
            self.data = data
            self.headers = headers
            self.META = meta
    
    request_copy = RequestCopy(request_data, request_headers, request_meta)
    
    # Run logging in background thread (don't wait for result)
    thread = threading.Thread(
        target=_log_failed_login_event_sync,
        args=(request_copy, username, error_message),
        daemon=True
    )
    thread.start()
    # Return None immediately - logging happens in background
    return None

def _log_logout_event(request, user):
    try:
        from activity_log.models import ActivityEvent, Source
        from activity_log.permissions import user_role
        from activity_log.utils.hashing import compute_event_hash
        from app.common.net_utils import get_client_ip, resolve_client_hostname

        role = user_role(user) or "SYSTEM"
        body_device_id = None
        body_device_name = None
        body_ip = None
        try:
            data = request.data if hasattr(request, 'data') else {}
            body_device_id = (data.get('device_id') or data.get('deviceId'))
            body_device_name = (data.get('device_name') or data.get('deviceName'))
            body_ip = (data.get('ip') or data.get('ip_address'))
        except Exception:
            pass
        ip_address = (body_ip or get_client_ip(request) or request.META.get("REMOTE_ADDR") or "").strip() or None
        device_id = (
            body_device_id
            or request.headers.get("X-Device-Id")
            or request.META.get("HTTP_X_DEVICE_ID")
        )
        device_name_hdr = (
            body_device_name
            or request.headers.get("X-Device-Name")
            or request.META.get("HTTP_X_DEVICE_NAME")
        )
        device_name = (device_name_hdr or resolve_client_hostname(ip_address))
        device_info = request.META.get("HTTP_USER_AGENT")
        ctx = {
            "ip": ip_address,
            "user_agent": device_info,
            "ip_address": ip_address,
            "device_id": device_id,
            "device_name": device_name,
            "device_info": device_info,
            "severity": "info",
            "tags": ["auth"],
        }
        canon = {
            "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tenant_id": "default",
            "actor": {"id": str(user.id), "role": role},
            "verb": "LOGOUT",
            "target": {"type": "User", "id": str(user.id)},
            "source": "FRONTEND",
            "request_id": f"req_{uuid4().hex}",
            "context": ctx,
        }
        ev_hash = compute_event_hash(canon)
        ActivityEvent.objects.create(
            timestamp=timezone.now(),
            actor_id=user.id,
            actor_role=role,
            verb="LOGOUT",
            target_type="User",
            target_id=str(user.id),
            context=ctx,
            source=Source.FRONTEND,
            request_id=canon["request_id"],
            tenant_id="default",
            hash=ev_hash,
        )
    except Exception:
        logger.exception("Failed to log LOGOUT activity event")
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .models import User
from .permissions import IsAdmin
from accounts.permissions import RolePermission
from drf_spectacular.utils import extend_schema
from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal


def get_user_primary_role(user):
    """Get user's primary role based on precedence: admin > sales > designer > production > delivery > finance"""
    roles = (user.roles or [])
    if user.is_superuser:
        return 'admin'
    # Check in order of precedence
    role_precedence = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    for role in role_precedence:
        if role in roles:
            return role
    # Default to first role if any exist, or 'sales' as fallback
    return roles[0] if roles else 'sales'


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    def post(self, request):
        # Extract and validate username early with detailed logging
        username = ""
        try:
            username = request.data.get('username', '') or ''
            if isinstance(username, str):
                username = username.strip()
            else:
                username = str(username).strip() if username else ''
            logger.info(f"[LOGIN] Login attempt started for username: '{username}'")
        except Exception as ex:
            logger.warning(f"[LOGIN] Error extracting username from request: {ex}")
            username = "unknown"
        
        logger.debug(f"[LOGIN] Username extracted: '{username}', type: {type(username)}")
        
        # Initialize serializer and validate - catch ALL errors
        serializer = None
        try:
            logger.debug(f"[LOGIN] Initializing LoginSerializer with data: {dict(request.data) if hasattr(request, 'data') else 'No data'}")
            serializer = LoginSerializer(data=request.data)
            logger.debug(f"[LOGIN] Serializer initialized, calling is_valid...")
            serializer.is_valid(raise_exception=True)
            logger.debug(f"[LOGIN] Validation passed, getting user...")
            user = serializer.validated_data['user']
            logger.info(f"[LOGIN] ✅ Login successful for username: {username}")
        except ValidationError as e:
            # This is the expected case for failed logins - log it
            error_msg = str(e.detail) if hasattr(e, 'detail') else str(e)
            logger.warning(f"[LOGIN] ❌ Failed login attempt for username: '{username}', error: {error_msg}")
            logger.debug(f"[LOGIN] ValidationError details: {e.detail if hasattr(e, 'detail') else e}")
            
            # Log failed login in background (non-blocking)
            try:
                logger.info(f"[LOGIN] Logging failed login attempt for username: '{username}' (background)")
                _log_failed_login_event(request, username, error_msg)
            except Exception as log_ex:
                logger.error(f"[LOGIN] ❌ Error calling _log_failed_login_event: {log_ex}", exc_info=True)
                # Don't raise - we don't want logging errors to break auth flow
            
            # Re-raise the ValidationError so DRF returns proper 400 response
            raise
        except Exception as e:
            # Log ANY other error (including serializer initialization errors)
            error_type = type(e).__name__
            logger.error(f"[LOGIN] ❌ Unexpected error during login for username: '{username}', error_type: {error_type}, error: {str(e)}", exc_info=True)
            
            # Log failed login in background (non-blocking)
            try:
                logger.info(f"[LOGIN] Logging failed login attempt for username: '{username}' (background)")
                _log_failed_login_event(request, username, f"{error_type}: {str(e)}")
            except Exception as log_ex:
                logger.error(f"[LOGIN] ❌ Error calling _log_failed_login_event: {log_ex}", exc_info=True)
                # Don't raise - we don't want logging errors to break auth flow
            
            # Re-raise the exception - let DRF handle it
            raise
        
        # Check device heartbeat requirement for non-admin users
        # Determine primary role from user's database roles
        primary_role = get_user_primary_role(user)
        logger.info(f"🔐 Login attempt for user {user.username} with role {primary_role}")
        logger.info(f"📋 User's database roles: {user.roles}")
        logger.info(f"👑 User.is_admin(): {user.is_admin()}")
        logger.info(f"🔍 Request data: {request.data}")
        logger.info(f"📡 Request headers: {dict(request.META)}")
        
        if primary_role != 'admin':
            logger.info(f"🚫 Non-admin login detected, checking device verification...")
            # Get device ID from request headers
            device_id = request.META.get('HTTP_X_DEVICE_ID')
            logger.info(f"📱 Device ID from headers: {device_id}")
            
            if not device_id:
                # No device ID provided - block login and provide enrollment token
                try:
                    from monitoring.models import Session
                    from monitoring.auth_utils import create_enrollment_token
                    
                    # Create enrollment token for this user
                    enrollment_token = create_enrollment_token(
                        user_id=str(user.id),
                        org_id=user.org_id
                    )
                    
                    # Try to create session, handle missing fields gracefully
                    try:
                        # Don't create session if device is None since it's required
                        logger.warning(f"Cannot create session without device for user {user.username}")
                    except Exception as e:
                        logger.warning(f"Failed to create session: {e}")
                    
                    return Response(
                        {
                            'error': 'Device ID required. Please install and run the monitoring agent.',
                            'enrollment_token': enrollment_token
                        },
                        status=status.HTTP_412_PRECONDITION_FAILED
                    )
                except Exception as e:
                    logger.error(f"Failed to handle missing device ID: {e}")
                    return Response(
                        {
                            'error': 'Device ID required. Please install and run the monitoring agent.',
                            'enrollment_token': None
                        },
                        status=status.HTTP_412_PRECONDITION_FAILED
                    )
            
            # Check if device has recent heartbeat
            try:
                from monitoring.auth_utils import check_device_heartbeat_by_id
                logger.info(f"Checking heartbeat for device {device_id}")
                has_recent_heartbeat, device = check_device_heartbeat_by_id(device_id, max_age_minutes=2)
                logger.info(f"Heartbeat check result: {has_recent_heartbeat}, device: {device}")
                
                if not has_recent_heartbeat:
                    # No recent heartbeat - block login and provide enrollment token
                    try:
                        from monitoring.models import Session
                        from monitoring.auth_utils import create_enrollment_token
                        
                        # Create enrollment token for this user
                        enrollment_token = create_enrollment_token(
                            user_id=str(user.id),
                            org_id=user.org_id
                        )
                        
                        # Try to create session, handle missing fields gracefully
                        try:
                            Session.objects.create(
                                user=user,
                                device=device,
                                status='PRECONDITION_FAILED'
                            )
                        except Exception as e:
                            logger.warning(f"Failed to create session: {e}")
                        
                        return Response(
                            {
                                'error': 'Agent not running or not responding. Please ensure the monitoring agent is running.',
                                'enrollment_token': enrollment_token
                            },
                            status=status.HTTP_412_PRECONDITION_FAILED
                        )
                    except Exception as e:
                        logger.error(f"Failed to handle missing heartbeat: {e}")
                        return Response(
                            {
                                'error': 'Agent not running or not responding. Please ensure the monitoring agent is running.',
                                'enrollment_token': None
                            },
                            status=status.HTTP_412_PRECONDITION_FAILED
                        )
                
                # Device has recent heartbeat - bind device to user and allow login
                logger.info(f"Device has recent heartbeat, allowing login for user {user.username}")
                try:
                    from monitoring.auth_utils import bind_device_to_user
                    bind_device_to_user(device_id, user)
                    
                    # Log session as allowed
                    try:
                        from monitoring.models import Session
                        Session.objects.create(
                            user=user,
                            device=device,
                            status='ALLOWED'
                        )
                    except Exception as e:
                        logger.warning(f"Failed to create session: {e}")
                except Exception as e:
                    logger.warning(f"Failed to bind device to user: {e}")
            except Exception as e:
                logger.error(f"Failed to check device heartbeat: {e}")
                # If we can't check heartbeat, block login for security
                try:
                    from monitoring.auth_utils import create_enrollment_token
                    
                    # Create enrollment token for this user
                    enrollment_token = create_enrollment_token(
                        user_id=str(user.id),
                        org_id=user.org_id
                    )
                    
                    return Response(
                        {
                            'error': 'Unable to verify device status. Please ensure the monitoring agent is running and try again.',
                            'enrollment_token': enrollment_token
                        },
                        status=status.HTTP_412_PRECONDITION_FAILED
                    )
                except Exception as token_error:
                    logger.error(f"Failed to create enrollment token: {token_error}")
                    return Response(
                        {
                            'error': 'Unable to verify device status. Please contact your administrator.',
                            'enrollment_token': None
                        },
                        status=status.HTTP_412_PRECONDITION_FAILED
                    )
        else:
            logger.info(f"👑 Admin login detected - bypassing device verification")
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"✅ Login successful for user {user.username} with role {primary_role}")
        
        # Generate Matrix access token if user is synced to Matrix
        matrix_token = None
        matrix_user_id = None
        matrix_base_url = None
        try:
            from accounts.services.matrix_service import matrix_service
            from django.conf import settings
            
            if user.matrix_synced and user.matrix_user_id:
                matrix_user_id = user.matrix_user_id
                # Create or refresh Matrix access token
                matrix_token = matrix_service.create_access_token(
                    matrix_user_id,
                    device_id=f"crm-{user.id}"
                )
                if matrix_token:
                    # Store token (optional - can regenerate on each login)
                    user.matrix_access_token = matrix_token
                    user.save(update_fields=['matrix_access_token'])
                    matrix_base_url = getattr(settings, 'MATRIX_PUBLIC_URL', 'http://localhost:8008')
                    logger.info(f"Generated Matrix token for {user.username}")
                else:
                    logger.warning(f"Failed to generate Matrix token for {user.username}")
            else:
                logger.debug(f"User {user.username} not synced to Matrix yet")
        except Exception as e:
            logger.warning(f"Error generating Matrix token: {e}", exc_info=True)
        
        # log login event (best effort)
        _log_login_event(request, user)
        
        response_data = {
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'role': primary_role,
            'username': user.username,
        }
        
        # Add Matrix config if available
        if matrix_token and matrix_user_id:
            response_data['matrix'] = {
                'base_url': matrix_base_url,
                'user_id': matrix_user_id,
                'access_token': matrix_token,
            }
        
        return Response(response_data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # best-effort log; token not blacklisted here
        _log_logout_event(request, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    permission_classes = [IsAdmin]

    @extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        user_data = UserSerializer(request.user).data
        
        # Add Matrix config if user is synced
        if request.user.matrix_synced and request.user.matrix_user_id:
            try:
                from accounts.services.matrix_service import matrix_service
                from django.conf import settings
                
                # Generate fresh token if needed
                matrix_token = request.user.matrix_access_token
                if not matrix_token:
                    matrix_token = matrix_service.create_access_token(
                        request.user.matrix_user_id,
                        device_id=f"crm-{request.user.id}"
                    )
                    if matrix_token:
                        request.user.matrix_access_token = matrix_token
                        request.user.save(update_fields=['matrix_access_token'])
                
                if matrix_token:
                    user_data['matrix'] = {
                        'base_url': getattr(settings, 'MATRIX_PUBLIC_URL', 'http://localhost:8008'),
                        'user_id': request.user.matrix_user_id,
                        'access_token': matrix_token,
                    }
            except Exception as e:
                logger.warning(f"Error adding Matrix config to /me: {e}", exc_info=True)
        
        return Response(user_data)


class MatrixConfigView(APIView):
    """Get Matrix configuration for the current user"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        operation_id='matrix_config',
        summary='Get Matrix chat configuration',
        description='Returns Matrix homeserver URL, user ID, and access token for the authenticated user',
        tags=['Chat'],
    )
    def get(self, request):
        """Get Matrix configuration for current user"""
        try:
            from accounts.services.matrix_service import matrix_service
            from django.conf import settings
            
            user = request.user
            
            # Ensure user is synced to Matrix
            if not user.matrix_synced or not user.matrix_user_id:
                return Response(
                    {'error': 'User not synced to Matrix. Please contact administrator.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Generate or refresh access token
            matrix_token = user.matrix_access_token
            if not matrix_token:
                matrix_token = matrix_service.create_access_token(
                    user.matrix_user_id,
                    device_id=f"crm-{user.id}"
                )
                if matrix_token:
                    user.matrix_access_token = matrix_token
                    user.save(update_fields=['matrix_access_token'])
            
            if not matrix_token:
                return Response(
                    {'error': 'Failed to generate Matrix access token'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                'base_url': getattr(settings, 'MATRIX_PUBLIC_URL', 'http://localhost:8008'),
                'user_id': user.matrix_user_id,
                'access_token': matrix_token,
            })
        except Exception as e:
            logger.error(f"Error getting Matrix config: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to get Matrix configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UsersListView(APIView):
    """List all User accounts with attendance summary data"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    
    @extend_schema(
        operation_id='users_list',
        summary='List all users with attendance summary',
        description='Returns all User accounts with their attendance summary for the specified month',
        tags=['Accounts'],
    )
    def get(self, request):
        # Get month parameter (default to current month)
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
        
        # Get all users (excluding superusers)
        users = User.objects.filter(is_superuser=False).order_by('username')
        
        # Import attendance models
        try:
            from attendance.models import Attendance, AttendanceRule, LeaveRequest
            from attendance.views import _get_breaks_prefetch
            from monitoring.models import Employee as MonitoringEmployee
            
            rules = AttendanceRule.get_solo()
            
            # Get attendance records for the month
            attendance_queryset = (
                Attendance.objects.filter(date__range=(start, end))
                .select_related('employee')
                .prefetch_related(_get_breaks_prefetch())
            )
            
            # Map attendance records by user
            records_map: dict[tuple[int, date], list] = defaultdict(list)
            for record in attendance_queryset:
                records_map[(record.employee_id, record.date)].append(record)
            
            # Get weekend days
            weekend_days = set(int(d) for d in (rules.weekend_days or []))
            days = []
            cur = start
            while cur <= end:
                js_weekday = (cur.weekday() + 1) % 7
                if js_weekday not in weekend_days:
                    days.append(cur)
                cur += timedelta(days=1)
            
            # Get approved leave requests
            approved_leaves = LeaveRequest.objects.filter(
                status=LeaveRequest.STATUS_APPROVED,
                start_date__lte=end,
            ).filter(
                Q(end_date__gte=start) | Q(end_date__isnull=True, start_date__gte=start)
            ).select_related('employee')
            
            leaves_by_employee: dict[int, list] = defaultdict(list)
            for leave in approved_leaves:
                leaves_by_employee[leave.employee_id].append(leave)
            
            # Get salaries from MonitoringEmployee
            salaries_by_email = {
                emp.email.lower(): float(emp.salary)
                for emp in MonitoringEmployee.objects.filter(
                    email__in=[u.email for u in users if u.email]
                )
            }
            
            response_data = []
            
            for user in users:
                # Calculate attendance summary for this user
                present_days = 0
                absent_days = 0
                total_late_minutes = 0
                total_overtime_minutes = 0
                total_break_minutes = 0
                total_effective_minutes = 0
                total_grace_violations = 0
                total_early_checkouts = 0
                check_in_times = []
                check_out_times = []
                last_attendance_date = None
                
                # Calculate leave hours
                employee_leaves = leaves_by_employee.get(user.id, [])
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
                
                # Process daily attendance
                for day in days:
                    records = records_map.get((user.id, day), [])
                    if not records:
                        absent_days += 1
                        continue
                    
                    present_days += 1
                    records = sorted(records, key=lambda r: r.check_in)
                    completed = [r for r in records if r.check_out]
                    record = completed[-1] if completed else records[-1]
                    
                    if record.check_out:
                        last_attendance_date = record.date
                    
                    local_in = timezone.localtime(record.check_in)
                    start_minutes = rules.work_start.hour * 60 + rules.work_start.minute
                    check_in_minutes = local_in.hour * 60 + local_in.minute
                    late = max(0, check_in_minutes - (start_minutes + rules.grace_minutes))
                    total_late_minutes += late
                    
                    # Check grace violation
                    is_grace_violation = check_in_minutes > (start_minutes + rules.grace_minutes)
                    if is_grace_violation:
                        total_grace_violations += 1
                    
                    check_in_times.append(check_in_minutes)
                    
                    # Check early checkout
                    if record.check_out:
                        local_out = timezone.localtime(record.check_out)
                        check_out_minutes = local_out.hour * 60 + local_out.minute
                        check_out_times.append(check_out_minutes)
                        
                        end_minutes = rules.work_end.hour * 60 + rules.work_end.minute
                        threshold_minutes = rules.early_checkout_threshold_minutes
                        if check_out_minutes < (end_minutes - threshold_minutes):
                            total_early_checkouts += 1
                        
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
                    
                    # Calculate overtime
                    stored_overtime = getattr(record, 'overtime_minutes', None)
                    if stored_overtime is not None:
                        overtime = stored_overtime
                    else:
                        is_monitored = bool(record.device_id or record.device_name)
                        if is_monitored and worked_minutes > 0:
                            overtime = max(0, worked_minutes - rules.standard_work_minutes)
                        else:
                            overtime = 0
                    total_overtime_minutes += overtime
                
                # Adjust for unpaid leave
                unpaid_leave_minutes = int(unpaid_leave_hours * 60)
                adjusted_effective_minutes = max(0, total_effective_minutes - unpaid_leave_minutes)
                adjusted_effective_hours = round(adjusted_effective_minutes / 60, 2)
                
                # Calculate average check-in/check-out times
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
                
                # Get user's full name
                full_name = user.get_full_name() or user.username
                
                # Get salary if available
                salary = salaries_by_email.get((user.email or '').lower(), 0.0)
                
                response_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email or '',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'full_name': full_name,
                    'roles': user.roles or [],
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'salary': salary,
                    'attendance_summary': {
                        'month': f"{year:04d}-{month:02d}",
                        'present_days': present_days,
                        'absent_days': absent_days,
                        'total_working_hours': round(total_effective_minutes / 60, 2),
                        'adjusted_working_hours': adjusted_effective_hours,
                        'total_break_minutes': total_break_minutes,
                        'total_break_hours': round(total_break_minutes / 60, 2),
                        'total_overtime_hours': round(total_overtime_minutes / 60, 2),
                        'total_leave_hours': round(total_leave_hours, 2),
                        'paid_leave_hours': round(paid_leave_hours, 2),
                        'unpaid_leave_hours': round(unpaid_leave_hours, 2),
                        'total_grace_violations': total_grace_violations,
                        'total_early_checkouts': total_early_checkouts,
                        'average_check_in_time': average_check_in_time,
                        'average_check_out_time': average_check_out_time,
                        'last_attendance_date': last_attendance_date.isoformat() if last_attendance_date else None,
                    }
                })
            
            return Response({'users': response_data, 'month': f"{year:04d}-{month:02d}"})
            
        except ImportError:
            # If attendance app is not available, return users without attendance data
            response_data = []
            for user in users:
                full_name = user.get_full_name() or user.username
                response_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email or '',
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'full_name': full_name,
                    'roles': user.roles or [],
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'salary': 0.0,
                    'attendance_summary': None,
                })
            return Response({'users': response_data, 'month': f"{year:04d}-{month:02d}"})


class UserSuspendReactivateView(APIView):
    """Suspend or reactivate a user account"""
    permission_classes = [IsAdmin]
    
    @extend_schema(
        operation_id='user_suspend_reactivate',
        summary='Suspend or reactivate user',
        description='Toggle user is_active status and log the action',
        tags=['Accounts'],
    )
    def post(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Prevent admin from suspending themselves
        if user.id == request.user.id:
            return Response({'error': 'Cannot suspend your own account'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Toggle is_active status
        new_status = not user.is_active
        user.is_active = new_status
        user.save(update_fields=['is_active'])
        
        # Update linked HREmployee status if it exists
        try:
            from hr.models import HREmployee
            if hasattr(user, 'hr_employee'):
                hr_employee = user.hr_employee
                if new_status is False:
                    # Suspending: set status to Inactive
                    hr_employee.status = 'Inactive'
                    hr_employee.save(update_fields=['status'])
                elif new_status is True and hr_employee.status == 'Inactive':
                    # Reactivating: only change to Active if it was Inactive (preserve 'On Leave')
                    hr_employee.status = 'Active'
                    hr_employee.save(update_fields=['status'])
        except Exception as e:
            # Log but don't fail the request if HREmployee update fails
            logger.warning(f"Failed to update HREmployee status for user {user.id}: {e}")
        
        # Log the action as an ActivityEvent
        try:
            from activity_log.models import ActivityEvent, Source, Verb, ActorRole
            from activity_log.utils.hashing import compute_event_hash
            from activity_log.permissions import user_role
            from uuid import uuid4
            
            role = user_role(request.user) or "ADMIN"
            context = {
                "previous_status": "active" if not new_status else "inactive",
                "new_status": "active" if new_status else "inactive",
                "action": "reactivate" if new_status else "suspend",
                "admin_user": request.user.username,
            }
            
            canon = {
                "timestamp": timezone.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tenant_id": "default",
                "actor": {"id": str(request.user.id), "role": role},
                "verb": Verb.STATUS_CHANGE,
                "target": {"type": "User", "id": str(user.id)},
                "source": Source.ADMIN_UI,
                "request_id": f"req_{uuid4().hex}",
                "context": context,
            }
            ev_hash = compute_event_hash(canon)
            
            # Get previous hash
            prev = ActivityEvent.objects.filter(tenant_id="default").order_by("-timestamp").first()
            
            ActivityEvent.objects.create(
                timestamp=timezone.now(),
                actor_id=request.user.id,
                actor_role=role,
                verb=Verb.STATUS_CHANGE,
                target_type="User",
                target_id=str(user.id),
                context=context,
                source=Source.ADMIN_UI,
                request_id=canon["request_id"],
                tenant_id="default",
                hash=ev_hash,
                prev_hash=prev.hash if prev else None,
            )
        except Exception as e:
            logger.exception(f"Failed to log user suspend/reactivate activity event: {e}")
        
        return Response({
            'id': user.id,
            'username': user.username,
            'is_active': user.is_active,
            'message': f'User {"reactivated" if new_status else "suspended"} successfully'
        }, status=status.HTTP_200_OK)


@extend_schema(
    operation_id='chat_users_list',
    summary='List users for chat',
    description='Get list of all users that can be contacted via chat (accessible to all authenticated users)',
    tags=['Accounts']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_users_list(request):
    """List all users for chat - accessible to all authenticated users"""
    try:
        # Get all users (excluding superusers)
        users = User.objects.filter(is_superuser=False).order_by('username')
        
        # Try to get HR employee data for profile pictures and designations
        hr_employees_map = {}
        try:
            from hr.models import HREmployee
            hr_employees = HREmployee.objects.select_related('user').all()
            for emp in hr_employees:
                if emp.user_id:
                    hr_employees_map[emp.user_id] = {
                        'image': emp.image.url if emp.image else None,
                        'designation': emp.designation,
                        'role': emp.role,
                    }
                if emp.email:
                    hr_employees_map[emp.email.lower()] = {
                        'image': emp.image.url if emp.image else None,
                        'designation': emp.designation,
                        'role': emp.role,
                    }
        except Exception:
            pass  # HR app might not be available
        
        # Serialize users
        users_data = []
        for user in users:
            hr_data = hr_employees_map.get(user.id) or hr_employees_map.get(user.email.lower() if user.email else '') or {}
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': user.roles or [],
                'image': hr_data.get('image'),
                'designation': hr_data.get('designation'),
                'role': hr_data.get('role'),
                'matrix_user_id': user.matrix_user_id,  # Include Matrix user ID for chat integration
            })
        
        return Response(users_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error listing chat users: {e}")
        return Response(
            {'error': 'Failed to fetch users'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id='users_by_role',
    summary='Get users by role',
    description='Get list of users filtered by role (designer, production, etc.)',
    tags=['Accounts']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_by_role(request):
    """Get users filtered by role"""
    try:
        role = request.query_params.get('role', '').lower()
        
        if not role:
            return Response({'error': 'role parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filter users by role
        users = User.objects.filter(
            is_superuser=False,
            is_active=True,
            roles__contains=[role]
        ).order_by('username')
        
        # Serialize users
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': user.roles or [],
            })
        
        return Response(users_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error listing users by role: {e}")
        return Response(
            {'error': 'Failed to fetch users'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
