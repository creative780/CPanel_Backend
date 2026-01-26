from django.db import models
from django.conf import settings


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_created', 'Order Created'),
        ('order_assigned', 'Order Assigned'),
        ('design_submitted', 'Design Submitted'),
        ('design_approved', 'Design Approved'),
        ('design_rejected', 'Design Rejected'),
        ('leave_requested', 'Leave Requested'),
        ('leave_approved', 'Leave Approved'),
        ('leave_rejected', 'Leave Rejected'),
        ('delivery_photo_uploaded', 'Delivery Photo Uploaded'),
        ('delivery_status_updated', 'Delivery Status Updated'),
        ('delivery_code_sent', 'Delivery Code Sent'),
        ('monitoring_device_idle', 'Device Idle'),
        ('monitoring_pollution_threshold', 'Pollution Threshold Exceeded'),
        ('monitoring_sensor_offline', 'Sensor Offline'),
        ('chat_message_received', 'Chat Message Received'),
        ('chat_call_incoming', 'Incoming Call'),
        ('chat_call_missed', 'Missed Call'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text='Short notification title'
    )
    message = models.TextField()
    type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        blank=True,
        null=True,
        help_text='Type of notification'
    )
    is_read = models.BooleanField(
        default=False,
        help_text='Whether the notification has been read'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_acted',
        help_text='User who triggered this notification'
    )
    tag_trigger = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Profile tag that triggered this notification'
    )
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Type of related object (e.g., order, design_approval, leave_request)'
    )
    related_object_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='ID of the related object'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional context data for the notification'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read'], name='notif_user_read_idx'),
            models.Index(fields=['type'], name='notif_type_idx'),
            models.Index(fields=['related_object_type', 'related_object_id'], name='notif_rel_obj_idx'),
            models.Index(fields=['created_at'], name='notif_created_at_idx'),
            models.Index(fields=['tag_trigger'], name='notif_tag_trig_idx'),
        ]
    
    def __str__(self):
        read_status = "read" if self.is_read else "unread"
        return f"Notification for {self.user.username} - {read_status}"
