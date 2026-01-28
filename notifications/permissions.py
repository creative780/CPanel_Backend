from rest_framework.permissions import BasePermission
from accounts.permissions import user_has_any_role
from .models import Notification


class CanViewNotification(BasePermission):
    """
    Permission class for notification visibility.
    
    Rules:
    1. Users can always see their own notifications
    2. Admins can see request-related notifications (leave_requested, design_submitted)
    3. Approval/rejection notifications are ONLY visible to the requester (employee), NOT to admins
    4. All other notifications are only visible to the recipient
    """
    
    # Request types that admins can see
    REQUEST_TYPES = ['leave_requested', 'design_submitted']
    
    # Approval/rejection types that are only visible to requester
    APPROVAL_REJECTION_TYPES = [
        'leave_approved', 'leave_rejected',
        'design_approved', 'design_rejected'
    ]
    
    def has_permission(self, request, view):
        """
        Check if user has permission to access the view.
        For list views, filtering is handled at queryset level.
        """
        # Allow authenticated users - actual filtering happens in queryset
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view this notification.
        
        Args:
            request: The request object
            view: The view object
            obj: The notification object
            
        Returns:
            bool: True if user can view, False otherwise
        """
        user = request.user
        
        # Rule 1: User can always see their own notifications
        if obj.user == user:
            return True
        
        # Rule 3: Approval/rejection notifications visibility
        # These are ONLY visible to the recipient (requester), NOT to admins
        if obj.type in self.APPROVAL_REJECTION_TYPES:
            # Only the recipient (requester) can see approval/rejection notifications
            return False
        
        # Rule 2: Admins can see request-related notifications
        if user_has_any_role(user, ['admin']):
            if obj.type in self.REQUEST_TYPES:
                return True
        
        # Rule 4: All other cases - only recipient can see
        return False


def get_notification_queryset(user):
    """
    Helper function to get the appropriate notification queryset for a user.
    
    Args:
        user: The user object
        
    Returns:
        QuerySet: Filtered notification queryset
        
    Rules:
    - All users see their own notifications
    - Admins also see request notifications (leave_requested, design_submitted)
    - Approval/rejection notifications (leave_approved, leave_rejected, etc.) are ONLY
      visible to the employee who requested them, NOT to admins who approved/rejected them
    """
    from .models import Notification
    
    # Start with user's own notifications (includes their own approval/rejection)
    qs = Notification.objects.filter(user=user)
    
    # For admins, also include request notifications (leave_requested, design_submitted)
    # NOTE: Admins should NOT see approval/rejection notifications - these are only for the employee
    if user_has_any_role(user, ['admin']):
        # Admins see request notifications (leave_requested, design_submitted)
        # These are visible to all admins regardless of recipient
        request_notifications = Notification.objects.filter(
            type__in=CanViewNotification.REQUEST_TYPES
        )
        qs = qs | request_notifications
    
    # CRITICAL: Exclude approval/rejection notifications that don't belong to this user
    # Approval/rejection types are ONLY visible to the recipient (requester), NOT to admins
    from django.db.models import Q
    # For all users (including admins): exclude approval/rejection notifications that don't belong to user
    qs = qs.exclude(
        Q(type__in=CanViewNotification.APPROVAL_REJECTION_TYPES) & ~Q(user=user)
    )
    
    return qs.distinct()

