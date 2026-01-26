from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


def create_notification(
    recipient: User,
    title: str,
    message: str,
    notification_type: str,
    actor: Optional[User] = None,
    related_object_type: Optional[str] = None,
    related_object_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Notification:
    """
    Central function to create notifications from anywhere in the codebase.
    
    Args:
        recipient: User who will receive the notification
        title: Short notification title
        message: Full notification message
        notification_type: One of the NOTIFICATION_TYPES
        actor: User who triggered the notification (optional)
        related_object_type: Type of related object (e.g., 'order', 'leave_request')
        related_object_id: ID of related object (as string)
        metadata: Additional JSON data
        
    Returns:
        Created Notification instance
    """
    return Notification.objects.create(
        user=recipient,
        title=title,
        message=message,
        type=notification_type,
        actor=actor,
        related_object_type=related_object_type,
        related_object_id=str(related_object_id) if related_object_id else None,
        metadata=metadata or {}
    )


def notify_admins(title: str, message: str, notification_type: str, **kwargs):
    """
    Helper to notify all admins.
    
    Args:
        title: Short notification title
        message: Full notification message
        notification_type: One of the NOTIFICATION_TYPES
        **kwargs: Additional arguments to pass to create_notification
                  (e.g., actor, related_object_type, related_object_id, metadata)
    """
    # Filter admin users by checking if 'admin' is in their roles list
    # JSONField doesn't support contains lookup, so we need to filter manually
    all_users = User.objects.all()
    admins = [user for user in all_users if user.has_role('admin')]
    
    for admin in admins:
        create_notification(
            recipient=admin,
            title=title,
            message=message,
            notification_type=notification_type,
            **kwargs
        )







































