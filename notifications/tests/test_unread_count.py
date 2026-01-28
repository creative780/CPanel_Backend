"""
Unread Count Tests for Notification System

Test Case Category: 9. Unread Count Is Accurate
"""
import pytest
from django.contrib.auth import get_user_model
from notifications.services import create_notification
from notifications.models import Notification
from rest_framework import status
from tests.factories import AdminUserFactory, SalesUserFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestUnreadCount:
    """Test Case 9: Unread Count Is Accurate"""
    
    def test_9_1_unread_count_excludes_read_notifications(self, authenticated_employee_client, sales_user):
        """Test Case 9.1: Unread Count Excludes Read Notifications"""
        # Create 3 unread
        for i in range(3):
            create_notification(
                recipient=sales_user,
                title=f'Unread {i}',
                message=f'Message {i}',
                notification_type='order_created',
            )
        
        # Create 2 read
        for i in range(2):
            read_notif = create_notification(
                recipient=sales_user,
                title=f'Read {i}',
                message=f'Message {i}',
                notification_type='order_created',
            )
            read_notif.is_read = True
            read_notif.save()
        
        response = authenticated_employee_client.get('/api/notifications/unread-count/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
    
    def test_9_2_unread_count_includes_only_own_for_employees(self, authenticated_employee_client, sales_user, admin_user):
        """Test Case 9.2: Unread Count Includes Only User's Own Notifications (for employees)"""
        # Create notifications for employee
        for i in range(2):
            create_notification(
                recipient=sales_user,
                title=f'Employee {i}',
                message=f'Message {i}',
                notification_type='order_created',
            )
        
        # Create notifications for admin (employee should not see these)
        for i in range(3):
            create_notification(
                recipient=admin_user,
                title=f'Admin {i}',
                message=f'Message {i}',
                notification_type='order_created',
            )
        
        response = authenticated_employee_client.get('/api/notifications/unread-count/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_9_3_unread_count_includes_admin_own_plus_requests(self, authenticated_admin_client, admin_user, sales_user):
        """Test Case 9.3: Unread Count Includes Admin's Own + Request Notifications (for admins)"""
        # Create admin's own notification
        create_notification(
            recipient=admin_user,
            title='Own',
            message='Own notification',
            notification_type='order_created',
        )
        
        # Create request notification for employee (admin should see this)
        create_notification(
            recipient=sales_user,
            title='Request',
            message='Leave request',
            notification_type='leave_requested',
        )
        
        # Create non-request notification for employee (admin should NOT see this)
        create_notification(
            recipient=sales_user,
            title='Other',
            message='Other notification',
            notification_type='order_created',
        )
        
        response = authenticated_admin_client.get('/api/notifications/unread-count/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # Own + request, but not the other
    
    def test_9_4_unread_count_updates_when_marked_read(self, authenticated_employee_client, sales_user):
        """Test Case 9.4: Unread Count Updates When Notification is Marked as Read"""
        # Create 2 unread notifications
        notif1 = create_notification(
            recipient=sales_user,
            title='Test 1',
            message='Message 1',
            notification_type='order_created',
        )
        notif2 = create_notification(
            recipient=sales_user,
            title='Test 2',
            message='Message 2',
            notification_type='order_created',
        )
        
        # Check initial count
        response = authenticated_employee_client.get('/api/notifications/unread-count/')
        assert response.data['count'] == 2
        
        # Mark one as read
        authenticated_employee_client.patch(
            f'/api/notifications/{notif1.id}/',
            {'is_read': True},
            format='json',
        )
        
        # Check updated count
        response = authenticated_employee_client.get('/api/notifications/unread-count/')
        assert response.data['count'] == 1
    
    def test_9_5_unread_count_accurate_after_creating_new(self, authenticated_employee_client, sales_user):
        """Test Case 9.5: Unread Count Is Accurate After Creating New Notifications"""
        # Initial count should be 0
        response = authenticated_employee_client.get('/api/notifications/unread-count/')
        assert response.data['count'] == 0
        
        # Create notification
        create_notification(
            recipient=sales_user,
            title='New',
            message='New notification',
            notification_type='order_created',
        )
        
        # Count should be 1
        response = authenticated_employee_client.get('/api/notifications/unread-count/')
        assert response.data['count'] == 1

