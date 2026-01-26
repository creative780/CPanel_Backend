"""
Service Function Tests for Notification System

Test Case Category: 1.4 Service Functions
"""
import pytest
from django.contrib.auth import get_user_model
from notifications.models import Notification
from notifications.services import create_notification, notify_admins
from tests.factories import AdminUserFactory, SalesUserFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestNotificationServices:
    """Test Case 1.4: Service Functions"""
    
    def test_1_4_1_create_notification_service_function(self, sales_user, admin_user):
        """Test Case 1.4.1: create_notification Service Function"""
        notification = create_notification(
            recipient=sales_user,
            title='Service Test',
            message='Created via service',
            notification_type='order_created',
            actor=admin_user,
            related_object_type='order',
            related_object_id='123',
            metadata={'order_code': 'ORD-123'},
        )
        
        assert notification.id is not None
        assert notification.user == sales_user
        assert notification.title == 'Service Test'
        assert notification.message == 'Created via service'
        assert notification.type == 'order_created'
        assert notification.actor == admin_user
        assert notification.related_object_type == 'order'
        assert notification.related_object_id == '123'
        assert notification.metadata == {'order_code': 'ORD-123'}
    
    def test_1_4_2_create_notification_with_optional_fields(self, sales_user):
        """Test Case 1.4.2: create_notification with Optional Fields"""
        notification = create_notification(
            recipient=sales_user,
            title='Test',
            message='Test message',
            notification_type='order_created',
            actor=None,
            related_object_type=None,
            related_object_id=None,
            metadata=None,
        )
        
        assert notification.id is not None
        assert notification.actor is None
        assert notification.related_object_type is None
        assert notification.related_object_id is None
        assert notification.metadata == {}
    
    def test_1_4_3_notify_admins_service_function(self, sales_user):
        """Test Case 1.4.3: notify_admins Service Function"""
        # Create admin users
        admin1 = AdminUserFactory()
        admin2 = AdminUserFactory()
        
        notify_admins(
            title='Admin Alert',
            message='All admins should see this',
            notification_type='monitoring_device_idle',
        )
        
        # Check both admins received notification
        admin1_notifs = Notification.objects.filter(user=admin1, type='monitoring_device_idle')
        admin2_notifs = Notification.objects.filter(user=admin2, type='monitoring_device_idle')
        
        assert admin1_notifs.count() == 1
        assert admin2_notifs.count() == 1
        
        # Verify notification content
        notif1 = admin1_notifs.first()
        assert notif1.title == 'Admin Alert'
        assert notif1.message == 'All admins should see this'
        
        # Verify non-admins did not receive notification
        assert Notification.objects.filter(user=sales_user, type='monitoring_device_idle').count() == 0
    
    def test_1_4_4_notify_admins_with_additional_parameters(self, sales_user, admin_user):
        """Test Case 1.4.4: notify_admins with Additional Parameters"""
        admin1 = AdminUserFactory()
        
        notify_admins(
            title='Admin Alert',
            message='All admins should see this',
            notification_type='monitoring_device_idle',
            actor=sales_user,
            related_object_type='device',
            related_object_id='456',
            metadata={'device_id': '456', 'status': 'idle'},
        )
        
        notif = Notification.objects.filter(user=admin1, type='monitoring_device_idle').first()
        
        assert notif is not None
        assert notif.actor == sales_user
        assert notif.related_object_type == 'device'
        assert notif.related_object_id == '456'
        assert notif.metadata == {'device_id': '456', 'status': 'idle'}
    
    def test_1_4_5_create_notification_converts_related_object_id_to_string(self, sales_user):
        """Test that related_object_id is converted to string"""
        notification = create_notification(
            recipient=sales_user,
            title='Test',
            message='Test message',
            notification_type='order_created',
            related_object_id=123,  # Integer ID
        )
        
        assert isinstance(notification.related_object_id, str)
        assert notification.related_object_id == '123'
    
    def test_1_4_6_create_notification_handles_edge_cases(self, sales_user):
        """Test Case 1.4.6: Service Functions Handle Edge Cases"""
        # Test with empty strings
        notification = create_notification(
            recipient=sales_user,
            title='',
            message='',
            notification_type='order_created',
        )
        assert notification.id is not None
        
        # Test with None metadata (should default to empty dict)
        notification2 = create_notification(
            recipient=sales_user,
            title='Test',
            message='Test',
            notification_type='order_created',
            metadata=None,
        )
        assert notification2.metadata == {}

