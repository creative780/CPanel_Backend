import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def send_notification_websocket_event(sender, instance, created, **kwargs):
    """Send WebSocket event when a notification is created or updated"""
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.warning("Channel layer not configured, skipping WebSocket event")
            return
        
        # Serialize notification
        serializer = NotificationSerializer(instance)
        notification_data = serializer.data
        
        # Ensure is_read is set correctly
        notification_data['is_read'] = instance.is_read
        # Set title if model title is empty, use first 50 chars of message
        if not instance.title and instance.message:
            notification_data['title'] = instance.message[:50]
        # Set type if model type is empty, use tag_trigger or default to 'general'
        if not instance.type:
            notification_data['type'] = instance.tag_trigger or 'general'
        
        # Determine event type
        event_type = 'notification.created' if created else 'notification.updated'
        
        # Send to user-specific group
        group_name = f'notifications_user_{instance.user.id}'
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': event_type.replace('.', '_'),  # Convert to method name format
                'data': notification_data
            }
        )
        
        logger.debug(f"Sent {event_type} WebSocket event for notification {instance.id} to user {instance.user.id}")
        
    except Exception as e:
        logger.error(f"Error sending WebSocket event for notification {instance.id}: {e}", exc_info=True)

