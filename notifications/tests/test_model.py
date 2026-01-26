"""
Model Tests for Notification System

Test Case Categories:
- Model Creation and Fields
- Model Ordering
- Model String Representation
"""
import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification
from tests.factories import SalesUserFactory, AdminUserFactory, NotificationFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestNotificationModel:
    """Test Notification Model"""
    
    def test_model_creation_required_fields(self, sales_user):
        """Test that Notification model can be created with all required fields"""
        notification = Notification.objects.create(
            user=sales_user,
            message='Test notification message',
        )
        
        assert notification.id is not None
        assert notification.user == sales_user
        assert notification.message == 'Test notification message'
        assert notification.is_read is False
        assert notification.created_at is not None
    
    def test_model_creation_optional_fields(self, sales_user, admin_user):
        """Test that Notification model can be created with optional fields"""
        notification = Notification.objects.create(
            user=sales_user,
            title='Test Title',
            message='Test notification message',
            type='order_created',
            actor=admin_user,
            related_object_type='order',
            related_object_id='123',
            metadata={'key': 'value'},
            tag_trigger='sales',
        )
        
        assert notification.title == 'Test Title'
        assert notification.type == 'order_created'
        assert notification.actor == admin_user
        assert notification.related_object_type == 'order'
        assert notification.related_object_id == '123'
        assert notification.metadata == {'key': 'value'}
        assert notification.tag_trigger == 'sales'
    
    def test_model_string_representation(self, sales_user):
        """Test model string representation"""
        notification = Notification.objects.create(
            user=sales_user,
            message='Test message',
        )
        
        str_repr = str(notification)
        assert sales_user.username in str_repr
        assert 'unread' in str_repr or 'read' in str_repr
    
    def test_model_ordering(self, sales_user):
        """Test model ordering (by created_at descending)"""
        # Create notifications with slight time differences
        notif1 = Notification.objects.create(user=sales_user, message='First')
        notif2 = Notification.objects.create(user=sales_user, message='Second')
        notif3 = Notification.objects.create(user=sales_user, message='Third')
        
        notifications = list(Notification.objects.filter(user=sales_user))
        
        # Should be ordered by created_at descending (newest first)
        assert notifications[0] == notif3
        assert notifications[1] == notif2
        assert notifications[2] == notif1
    
    def test_model_defaults(self, sales_user):
        """Test model default values"""
        notification = Notification.objects.create(
            user=sales_user,
            message='Test message',
        )
        
        assert notification.is_read is False
        assert notification.metadata == {}
        assert notification.created_at is not None
        assert notification.updated_at is not None

