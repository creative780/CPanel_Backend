"""
Serializer Tests for Notification System

Test Case Category: 12. Serializer Testing
"""
import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.serializers import NotificationListSerializer, NotificationDetailSerializer, NotificationUpdateSerializer
from notifications.services import create_notification
from tests.factories import AdminUserFactory, SalesUserFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestNotificationSerializers:
    """Test Case 12: Serializer Testing"""
    
    def test_12_1_notification_list_serializer_fields(self, sales_user, admin_user):
        """Test Case 12.1: NotificationListSerializer Fields"""
        notification = create_notification(
            recipient=sales_user,
            title='Test Title',
            message='Test message',
            notification_type='order_created',
            actor=admin_user,
        )
        
        serializer = NotificationListSerializer(notification)
        data = serializer.data
        
        # Verify minimal fields included
        assert 'id' in data
        assert 'title' in data
        assert 'message' in data
        assert 'type' in data
        assert 'is_read' in data
        assert 'actor_name' in data
        assert 'created_at' in data
        
        # Verify data values
        assert data['title'] == 'Test Title'
        assert data['message'] == 'Test message'
        assert data['type'] == 'order_created'
        assert data['is_read'] is False
    
    def test_12_2_notification_detail_serializer_fields(self, sales_user, admin_user):
        """Test Case 12.2: NotificationDetailSerializer Fields"""
        notification = create_notification(
            recipient=sales_user,
            title='Detail Test',
            message='Detail message',
            notification_type='order_created',
            actor=admin_user,
            related_object_type='order',
            related_object_id='123',
            metadata={'order_code': 'ORD-123'},
        )
        
        serializer = NotificationDetailSerializer(notification)
        data = serializer.data
        
        # Verify full fields included
        assert 'id' in data
        assert 'title' in data
        assert 'message' in data
        assert 'type' in data
        assert 'is_read' in data
        assert 'actor_name' in data
        assert 'actor_id' in data
        assert 'user_id' in data
        assert 'related_object_type' in data
        assert 'related_object_id' in data
        assert 'metadata' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        
        # Verify data values
        assert data['actor_name'] == admin_user.username
        assert data['related_object_type'] == 'order'
        assert data['related_object_id'] == '123'
    
    def test_12_3_notification_update_serializer_validation(self, sales_user):
        """Test Case 12.3: NotificationUpdateSerializer Validation"""
        notification = create_notification(
            recipient=sales_user,
            title='Test',
            message='Test message',
            notification_type='order_created',
        )
        
        # Test updating is_read
        serializer = NotificationUpdateSerializer(
            notification,
            data={'is_read': True},
            partial=True
        )
        assert serializer.is_valid()
        serializer.save()
        
        notification.refresh_from_db()
        assert notification.is_read is True
    
    def test_12_4_actor_name_serialization(self, sales_user, admin_user):
        """Test Case 12.4: Actor Name Serialization"""
        notification = create_notification(
            recipient=sales_user,
            title='Test',
            message='Test message',
            notification_type='order_created',
            actor=admin_user,
        )
        
        serializer = NotificationListSerializer(notification)
        data = serializer.data
        
        assert 'actor_name' in data
        assert data['actor_name'] == admin_user.username
    
    def test_12_5_actor_name_with_null_actor(self, sales_user):
        """Test Case 12.5: Actor Name with Null Actor"""
        notification = create_notification(
            recipient=sales_user,
            title='Test',
            message='Test message',
            notification_type='order_created',
            actor=None,
        )
        
        serializer = NotificationListSerializer(notification)
        data = serializer.data
        
        assert 'actor_name' in data
        # Actor name should be None or empty when actor is None
        assert data['actor_name'] is None or data['actor_name'] == ''

