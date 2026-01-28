from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """General-purpose serializer for notifications - used for WebSocket events and general serialization"""
    actor_name = serializers.CharField(source='actor.username', read_only=True, allow_null=True)
    actor_id = serializers.IntegerField(source='actor.id', read_only=True, allow_null=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'type', 'is_read',
            'actor_name', 'actor_id', 'user_id',
            'created_at', 'updated_at', 'related_object_type',
            'related_object_id', 'metadata', 'tag_trigger'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer for listing notifications - minimal fields for list views"""
    actor_name = serializers.CharField(source='actor.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'type', 'is_read', 
            'actor_name', 'created_at', 'related_object_type', 
            'related_object_id', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationDetailSerializer(NotificationListSerializer):
    """Serializer for detailed notification view - extends list with full actor details"""
    actor_id = serializers.IntegerField(source='actor.id', read_only=True, allow_null=True)
    actor_username = serializers.CharField(source='actor.username', read_only=True, allow_null=True)
    actor_email = serializers.EmailField(source='actor.email', read_only=True, allow_null=True)
    actor_first_name = serializers.CharField(source='actor.first_name', read_only=True, allow_null=True)
    actor_last_name = serializers.CharField(source='actor.last_name', read_only=True, allow_null=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta(NotificationListSerializer.Meta):
        fields = NotificationListSerializer.Meta.fields + [
            'actor_id', 'actor_username', 'actor_email', 
            'actor_first_name', 'actor_last_name',
            'updated_at', 'tag_trigger', 'user_id'
        ]
        read_only_fields = NotificationListSerializer.Meta.read_only_fields + [
            'updated_at', 'tag_trigger', 'user_id'
        ]


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification - specifically for marking as read/unread"""
    
    class Meta:
        model = Notification
        fields = ['is_read']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications - internal service use"""
    recipient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        help_text='User who will receive this notification'
    )
    actor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        help_text='User who triggered this notification'
    )
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'type', 'recipient', 'actor', 
            'related_object_type', 'related_object_id', 'metadata'
        ]
    
    def validate_type(self, value):
        """Validate that type is one of the allowed notification types"""
        if value and value not in [choice[0] for choice in Notification.NOTIFICATION_TYPES]:
            raise serializers.ValidationError(
                f"Invalid notification type. Must be one of: {[choice[0] for choice in Notification.NOTIFICATION_TYPES]}"
            )
        return value

