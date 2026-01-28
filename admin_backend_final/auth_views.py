import re
import uuid
import logging

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.db import connection, OperationalError, DatabaseError

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User, Image, EmailVerificationCode
from .permissions import FrontendOnlyPermission
from .utilities import send_verification_email

logger = logging.getLogger(__name__)

EMIRATES_ID_RE = re.compile(r"^784-\d{4}-\d{7}-\d$")

def safe_delete_image(image):
    """
    Safely delete an Image, handling cases where related tables might not exist.
    """
    try:
        # Try to delete the image file first
        if image.image_file:
            try:
                image.image_file.delete(save=False)
            except Exception:
                pass
        
        # Delete the image record using raw SQL to bypass ORM reverse relationship checks
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM admin_backend_final_image WHERE image_id = %s", [image.image_id])
        return True
    except (OperationalError, DatabaseError) as e:
        # If table doesn't exist or other DB error, log and return False
        logger.warning(f"Could not delete image {image.image_id}: {str(e)}")
        return False
    except Exception as e:
        logger.warning(f"Error deleting image {image.image_id}: {str(e)}")
        return False

def _clean_str(v, default=""):
    return (v or default).strip()

def _user_payload(user):
    profile_picture_url = None
    if user.profile_picture:
        try:
            profile_picture_url = user.profile_picture.url
        except Exception:
            profile_picture_url = None
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name or "",
        "is_verified": getattr(user, "is_verified", False),
        "emirates_id": user.emirates_id or "",
        "phone_number": user.phone_number or "",
        "address": user.address or "",
        "profile_picture": profile_picture_url,
        "created_at": user.created_at.isoformat() if user.created_at else "",
        "updated_at": user.updated_at.isoformat() if user.updated_at else "",
    }

COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/api/token/"
COOKIE_SECURE = False     # set True in HTTPS/prod
COOKIE_SAMESITE = "Lax"   # use "None" + SECURE=True if cross-site in prod
COOKIE_MAX_AGE = 7 * 24 * 60 * 60

@ensure_csrf_cookie
def csrf(request):
    """
    GET /api/csrf/ -> sets csrftoken cookie and returns it as JSON
    Use this once on app load before making POSTs that need CSRF.
    """
    return JsonResponse({"csrfToken": get_token(request)})

@method_decorator(csrf_exempt, name="post")
class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        res = super().post(request, *args, **kwargs)
        if res.status_code == status.HTTP_200_OK and "refresh" in res.data:
            refresh = res.data.pop("refresh")
            res.set_cookie(
                COOKIE_NAME, refresh,
                max_age=COOKIE_MAX_AGE,
                httponly=True,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                path=COOKIE_PATH,
            )
        return res


@method_decorator(csrf_protect, name="post")
class CookieTokenRefreshView(TokenRefreshView):
    """
    POST /api/token/refresh/ -> returns {"access": "..."} using HttpOnly cookie.
    Requires X-CSRFToken header (double submit).
    """
    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.COOKIES.get(COOKIE_NAME)
        return super().post(request, *args, **kwargs)

@method_decorator(csrf_protect, name="post")
class LogoutView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        r = Response({"detail": "Logged out"})
        r.delete_cookie(COOKIE_NAME, path=COOKIE_PATH)
        return r


@method_decorator(csrf_exempt, name="post")
class RegisterView(APIView):
    """
    POST /api/register/. CSRF-exempt for cross-origin SPA; protected by FrontendOnlyPermission.
    """
    authentication_classes = ()
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = request.data if isinstance(getattr(request, "data", None), dict) else {}
            email = _clean_str(data.get("email")).lower()
            password = _clean_str(data.get("password"))
            name = _clean_str(data.get("name"))
            phone_number = _clean_str(data.get("phone_number"))
            address = _clean_str(data.get("address"))
            emirates_id_raw = data.get("emirates_id")
            emirates_id = _clean_str(emirates_id_raw) if emirates_id_raw is not None else None

            if not email:
                return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
            if len(password) < 6:
                return Response({"error": "Password must be at least 6 characters"}, status=status.HTTP_400_BAD_REQUEST)
            if emirates_id and not EMIRATES_ID_RE.match(emirates_id):
                return Response({"error": "Invalid Emirates ID format. Use 784-YYYY-NNNNNNN-C"}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({"error": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username=email).exists():
                return Response({"error": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            user_id = uuid.uuid4().hex
            user = User(
                user_id=user_id,
                email=email,
                username=email,
                first_name=name or "",
                is_verified=False,
                is_active=True,  # Explicitly set to ensure user can login immediately
                emirates_id=emirates_id or None,
                phone_number=phone_number or "",
                address=address or "",
            )
            user.set_password(password)
            # DB may enforce NOT NULL on password_hash; keep it in sync with Django's hashed password.
            user.password_hash = user.password
            user.save()

            logger.info(f"User registered successfully: {email} (user_id: {user_id})")

            return Response(
                {"message": "User registered successfully", "user_id": user_id, "email": email, "username": user.username},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Registration error for email {data.get('email', 'unknown')}: {type(e).__name__}: {str(e)}", exc_info=True)
            return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_user_payload(request.user), status=status.HTTP_200_OK)

    @method_decorator(csrf_exempt)
    def patch(self, request):
        try:
            data = request.data if isinstance(getattr(request, "data", None), dict) else {}
            user = request.user

            if "name" in data:
                user.first_name = _clean_str(data.get("name"))
            if "email" in data:
                val = _clean_str(data.get("email")).lower()
                if val and val != user.email:
                    if User.objects.filter(email=val).exclude(user_id=user.user_id).exists():
                        return Response({"error": "A user with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
                    user.email = val
                    user.username = val
            if "phone_number" in data:
                user.phone_number = _clean_str(data.get("phone_number"))
            if "address" in data:
                user.address = _clean_str(data.get("address"))
            if "emirates_id" in data:
                eid = data.get("emirates_id")
                if eid is not None:
                    eid = _clean_str(eid)
                    if eid and not EMIRATES_ID_RE.match(eid):
                        return Response({"error": "Invalid Emirates ID format. Use 784-YYYY-NNNNNNN-C"}, status=status.HTTP_400_BAD_REQUEST)
                    user.emirates_id = eid or None

            if "profile_picture_id" in data:
                profile_picture_id = data.get("profile_picture_id")
                if profile_picture_id:
                    try:
                        image = Image.objects.get(image_id=profile_picture_id)
                        # Optional: Verify image is linked to this user for security
                        if image.linked_table == "user" and image.linked_id == user.user_id:
                            # Store old profile picture for potential cleanup
                            old_profile_picture = user.profile_picture
                            user.profile_picture = image
                            # Clean up old profile picture if it exists and is only used by this user
                            if old_profile_picture and old_profile_picture.linked_table == "user" and old_profile_picture.linked_id == user.user_id:
                                # Check if image is used by other users as profile picture
                                other_users_with_image = User.objects.filter(profile_picture=old_profile_picture).exclude(user_id=user.user_id)
                                if not other_users_with_image.exists():
                                    # Only delete if not used by other users
                                    safe_delete_image(old_profile_picture)
                        else:
                            return Response({"error": "Image not found or not associated with this user"}, status=status.HTTP_400_BAD_REQUEST)
                    except Image.DoesNotExist:
                        return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    # Setting to None/null to remove profile picture
                    old_profile_picture = user.profile_picture
                    user.profile_picture = None
                    # Clean up old profile picture if it exists and is only used by this user
                    if old_profile_picture and old_profile_picture.linked_table == "user" and old_profile_picture.linked_id == user.user_id:
                        # Check if image is used by other users as profile picture
                        other_users_with_image = User.objects.filter(profile_picture=old_profile_picture).exclude(user_id=user.user_id)
                        if not other_users_with_image.exists():
                            # Only delete if not used by other users
                            safe_delete_image(old_profile_picture)

            update_fields = ["first_name", "email", "username", "phone_number", "address", "emirates_id", "profile_picture"]
            user.save(update_fields=update_fields)

            return Response(_user_payload(user), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name="post")
class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data if isinstance(getattr(request, "data", None), dict) else {}
            current_password = _clean_str(data.get("current_password"))
            new_password = _clean_str(data.get("new_password"))

            if not current_password:
                return Response({"error": "Current password is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not new_password:
                return Response({"error": "New password is required"}, status=status.HTTP_400_BAD_REQUEST)
            if len(new_password) < 6:
                return Response({"error": "New password must be at least 6 characters"}, status=status.HTTP_400_BAD_REQUEST)
            if not request.user.check_password(current_password):
                return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            request.user.set_password(new_password)
            request.user.save(update_fields=["password"])
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Generate and send verification code to user's email"""
        user = request.user
        
        # Check if already verified
        if user.is_verified:
            return Response({"error": "Email already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for recent code (rate limiting - max 1 per minute)
        from datetime import timedelta
        recent_code = EmailVerificationCode.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(minutes=1)
        ).first()
        if recent_code:
            return Response(
                {"error": "Please wait before requesting another code"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Generate 6-digit code
        import random
        code = str(random.randint(100000, 999999))
        
        # Create verification code record (expires in 10 minutes)
        verification_code = EmailVerificationCode.objects.create(
            code_id=f"VC-{uuid.uuid4().hex[:8]}",
            user=user,
            email=user.email,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # Send email
        if send_verification_email(user.email, code):
            return Response({
                "message": "Verification code sent to your email",
                "expires_in_minutes": 10
            }, status=status.HTTP_200_OK)
        else:
            verification_code.delete()  # Clean up if email failed
            return Response(
                {"error": "Failed to send verification email. Please check SMTP configuration."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEmailCodeView(APIView):
    permission_classes = [IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Verify the code and update user verification status"""
        user = request.user
        data = request.data if isinstance(getattr(request, "data", None), dict) else {}
        code = _clean_str(data.get('code', ''))
        
        if not code or len(code) != 6:
            return Response({"error": "Invalid code format"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find valid verification code
        verification_code = EmailVerificationCode.objects.filter(
            user=user,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()
        
        if not verification_code:
            return Response(
                {"error": "Invalid or expired verification code"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark code as used and verify user
        verification_code.is_used = True
        verification_code.save()
        
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        
        return Response({
            "message": "Email verified successfully",
            "is_verified": True
        }, status=status.HTTP_200_OK)
