# admin_backend_final/permissions.py
import os
from dotenv import load_dotenv
from rest_framework.permissions import BasePermission, AllowAny

load_dotenv()
FRONTEND_KEY = os.environ.get("FRONTEND_KEY", "").strip()

class FrontendOnlyPermission(BasePermission):
    """
    Permission class that checks for X-Frontend-Key header.
    If FRONTEND_KEY is not set, allows all requests (for development).
    This is used for public-facing endpoints that should be accessible
    from the frontend without JWT authentication.
    """
    def has_permission(self, request, view):
        # If FRONTEND_KEY is not configured, allow access (development mode)
        if not FRONTEND_KEY:
            return True
        
        # Check for the header (Django normalizes headers, so try both formats)
        header_value = (
            request.headers.get("X-Frontend-Key") or 
            request.headers.get("x-frontend-key") or
            request.META.get("HTTP_X_FRONTEND_KEY", "")
        )
        return header_value.strip() == FRONTEND_KEY
