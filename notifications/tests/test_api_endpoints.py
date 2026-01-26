"""
Backend API Endpoint Tests for Notification System

Test Case Categories:
1. Notification CRUD Operations
2. Filtering and Query Parameters
3. Unread Count
4. Mark as Read Functionality
"""
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from accounts.models import Role
from tests.factories import (
    AdminUserFactory, SalesUserFactory, DesignerUserFactory,
    FinanceUserFactory, UserFactory, NotificationFactory
)
from notifications.models import Notification
from notifications.services import create_notification, notify_admins

User = get_user_model()


# ============================================================================
# Test Case 1.1: Notification CRUD Operations
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestNotificationCRUD:
    """Test Case 1.1: Notification CRUD Operations"""
    
    def test_1_1_1_list_notifications(self, authenticated_employee_client, sales_user):
        """Test Case 1.1.1: List Notifications (GET /api/notifications/)"""
        # Create test notifications
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
            notification_type='order_assigned',
        )
        
        response = authenticated_employee_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
        assert isinstance(response.data, list)
        
        # Verify required fields in response
        notification = response.data[0]
        assert 'id' in notification
        assert 'title' in notification
        assert 'message' in notification
        assert 'type' in notification
        assert 'is_read' in notification
        assert 'created_at' in notification
    
    def test_1_1_2_filter_notifications_by_unread(self, authenticated_employee_client, sales_user):
        """Test Case 1.1.2: Filter Notifications by Read Status (Unread)"""
        # Create read and unread notifications
        read_notif = create_notification(
            recipient=sales_user,
            title='Read',
            message='Read message',
            notification_type='order_created',
        )
        read_notif.is_read = True
        read_notif.save()
        
        unread_notif = create_notification(
            recipient=sales_user,
            title='Unread',
            message='Unread message',
            notification_type='order_assigned',
        )
        
        response = authenticated_employee_client.get('/api/notifications/?is_read=false')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        
        # Verify all are unread
        for notif in response.data:
            assert notif['is_read'] is False
        
        # Verify unread notification is in response
        notification_ids = [n['id'] for n in response.data]
        assert unread_notif.id in notification_ids
    
    def test_1_1_3_filter_notifications_by_read(self, authenticated_employee_client, sales_user):
        """Test Case 1.1.3: Filter Notifications by Read Status (Read)"""
        # Create read notification
        read_notif = create_notification(
            recipient=sales_user,
            title='Read',
            message='Read message',
            notification_type='order_created',
        )
        read_notif.is_read = True
        read_notif.save()
        
        # Create unread notification
        unread_notif = create_notification(
            recipient=sales_user,
            title='Unread',
            message='Unread message',
            notification_type='order_assigned',
        )
        
        response = authenticated_employee_client.get('/api/notifications/?is_read=true')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        
        # Verify all are read
        for notif in response.data:
            assert notif['is_read'] is True
        
        # Verify read notification is in response
        notification_ids = [n['id'] for n in response.data]
        assert read_notif.id in notification_ids
    
    def test_1_1_4_get_notification_detail(self, authenticated_employee_client, sales_user, admin_user):
        """Test Case 1.1.4: Get Notification Detail (GET /api/notifications/{id}/)"""
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
        
        response = authenticated_employee_client.get(f'/api/notifications/{notification.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == notification.id
        assert response.data['title'] == 'Detail Test'
        assert response.data['message'] == 'Detail message'
        assert response.data['type'] == 'order_created'
        assert 'actor_name' in response.data
        assert 'actor_id' in response.data
        assert 'user_id' in response.data
        assert response.data.get('related_object_type') == 'order'
        assert response.data.get('related_object_id') == '123'
    
    def test_1_1_5_mark_notification_as_read(self, authenticated_employee_client, sales_user):
        """Test Case 1.1.5: Mark Notification as Read (PATCH /api/notifications/{id}/)"""
        notification = create_notification(
            recipient=sales_user,
            title='Update Test',
            message='Update message',
            notification_type='order_created',
        )
        assert notification.is_read is False
        
        response = authenticated_employee_client.patch(
            f'/api/notifications/{notification.id}/',
            {'is_read': True},
            format='json',
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify notification marked as read
        notification.refresh_from_db()
        assert notification.is_read is True
    
    def test_1_1_6_mark_notification_as_unread(self, authenticated_employee_client, sales_user):
        """Test Case 1.1.6: Mark Notification as Unread"""
        notification = create_notification(
            recipient=sales_user,
            title='Test',
            message='Test message',
            notification_type='order_created',
        )
        notification.is_read = True
        notification.save()
        
        # Mark as unread
        response = authenticated_employee_client.patch(
            f'/api/notifications/{notification.id}/',
            {'is_read': False},
            format='json',
        )
        
        assert response.status_code == status.HTTP_200_OK
        notification.refresh_from_db()
        assert notification.is_read is False
    
    def test_1_1_7_get_unread_count(self, authenticated_employee_client, sales_user):
        """Test Case 1.1.7: Get Unread Count"""
        # Create 3 unread and 2 read notifications
        for i in range(3):
            create_notification(
                recipient=sales_user,
                title=f'Unread {i}',
                message=f'Message {i}',
                notification_type='order_created',
            )
        
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
    
    def test_1_1_8_notification_limit_50_most_recent(self, authenticated_employee_client, sales_user):
        """Test Case 1.1.8: Notification Limit (50 Most Recent)"""
        # Create 60 notifications
        for i in range(60):
            create_notification(
                recipient=sales_user,
                title=f'Notification {i}',
                message=f'Message {i}',
                notification_type='order_created',
            )
        
        response = authenticated_employee_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 50
        
        # Verify ordering (newest first)
        notification_ids = [n['id'] for n in response.data]
        # IDs should be in descending order (newer notifications have higher IDs typically)
        assert notification_ids == sorted(notification_ids, reverse=True)


# ============================================================================
# Test Case 1.2: Permission and Access Control
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestNotificationPermissions:
    """Test Case 1.2: Permission and Access Control"""
    
    def test_1_2_1_employee_sees_only_own_notifications(self, authenticated_employee_client, sales_user, admin_user):
        """Test Case 1.2.1: Employee Sees Only Own Notifications"""
        # Create notification for employee
        employee_notif = create_notification(
            recipient=sales_user,
            title='Employee Notification',
            message='For employee',
            notification_type='order_created',
        )
        
        # Create notification for admin
        admin_notif = create_notification(
            recipient=admin_user,
            title='Admin Notification',
            message='For admin',
            notification_type='order_created',
        )
        
        response = authenticated_employee_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert employee_notif.id in notification_ids
        assert admin_notif.id not in notification_ids
    
    def test_1_2_2_admin_sees_own_notifications(self, authenticated_admin_client, admin_user):
        """Test Case 1.2.2: Admin Sees Own Notifications"""
        own_notif = create_notification(
            recipient=admin_user,
            title='Own Notification',
            message='For admin',
            notification_type='order_created',
        )
        
        response = authenticated_admin_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert own_notif.id in notification_ids
    
    def test_1_2_3_admin_sees_leave_requested_notifications(self, authenticated_admin_client, admin_user, sales_user, designer_user):
        """Test Case 1.2.3: Admin Sees Request Notifications (leave_requested)"""
        # Create leave request notifications for different users
        employee_leave = create_notification(
            recipient=sales_user,
            title='Leave Request',
            message='Employee leave request',
            notification_type='leave_requested',
        )
        
        designer_leave = create_notification(
            recipient=designer_user,
            title='Leave Request',
            message='Designer leave request',
            notification_type='leave_requested',
        )
        
        # Admin should see both
        response = authenticated_admin_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert employee_leave.id in notification_ids
        assert designer_leave.id in notification_ids
    
    def test_1_2_4_admin_sees_design_submitted_notifications(self, authenticated_admin_client, admin_user, sales_user, designer_user):
        """Test Case 1.2.4: Admin Sees Request Notifications (design_submitted)"""
        # Create design submitted notifications
        employee_design = create_notification(
            recipient=sales_user,
            title='Design Submitted',
            message='Employee design',
            notification_type='design_submitted',
        )
        
        designer_design = create_notification(
            recipient=designer_user,
            title='Design Submitted',
            message='Designer design',
            notification_type='design_submitted',
        )
        
        # Admin should see both
        response = authenticated_admin_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert employee_design.id in notification_ids
        assert designer_design.id in notification_ids
    
    def test_1_2_5_admin_does_not_see_approval_rejection_notifications(self, authenticated_admin_client, admin_user, sales_user):
        """Test Case 1.2.5: Admin Does NOT See Approval/Rejection Notifications of Others"""
        # Create approval notification for employee
        approval_notif = create_notification(
            recipient=sales_user,
            title='Leave Approved',
            message='Your leave has been approved',
            notification_type='leave_approved',
            actor=admin_user,
        )
        
        # Create rejection notification for employee
        rejection_notif = create_notification(
            recipient=sales_user,
            title='Design Rejected',
            message='Your design has been rejected',
            notification_type='design_rejected',
            actor=admin_user,
        )
        
        # Admin should NOT see these (they're not the requester)
        response = authenticated_admin_client.get('/api/notifications/')
        
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert approval_notif.id not in notification_ids
        assert rejection_notif.id not in notification_ids
    
    def test_1_2_6_employee_cannot_access_other_user_notification_detail(self, authenticated_employee_client, sales_user, admin_user):
        """Test Case 1.2.6: Employee Cannot Access Other User's Notification Detail"""
        admin_notif = create_notification(
            recipient=admin_user,
            title='Admin Notification',
            message='For admin',
            notification_type='order_created',
        )
        
        response = authenticated_employee_client.get(f'/api/notifications/{admin_notif.id}/')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_1_2_7_employee_cannot_mark_other_user_notification_as_read(self, authenticated_employee_client, sales_user, admin_user):
        """Test Case 1.2.7: Employee Cannot Mark Other User's Notification as Read"""
        admin_notif = create_notification(
            recipient=admin_user,
            title='Admin',
            message='For admin',
            notification_type='order_created',
        )
        
        response = authenticated_employee_client.patch(
            f'/api/notifications/{admin_notif.id}/',
            {'is_read': True},
            format='json',
        )
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
        
        # Verify notification not marked as read
        admin_notif.refresh_from_db()
        assert admin_notif.is_read is False
    
    def test_1_2_8_unauthenticated_user_cannot_access(self, api_client, sales_user):
        """Test Case 1.2.8: Unauthenticated User Cannot Access Notifications"""
        create_notification(
            recipient=sales_user,
            title='Test',
            message='Test',
            notification_type='order_created',
        )
        
        client = api_client
        response = client.get('/api/notifications/')
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_1_2_9_admin_can_mark_request_notifications_as_read(self, authenticated_admin_client, admin_user, sales_user):
        """Test Case 1.2.9: Admin Can Mark Request Notifications as Read"""
        request_notif = create_notification(
            recipient=sales_user,
            title='Request',
            message='Leave request',
            notification_type='leave_requested',
        )
        
        response = authenticated_admin_client.patch(
            f'/api/notifications/{request_notif.id}/',
            {'is_read': True},
            format='json',
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify notification marked as read
        request_notif.refresh_from_db()
        assert request_notif.is_read is True


# ============================================================================
# Test Case 1.3: Notification Types
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestNotificationTypes:
    """Test Case 1.3: Notification Types"""
    
    def test_1_3_1_order_created_notification(self, authenticated_employee_client, sales_user):
        """Test Case 1.3.1: Order Created Notification"""
        notification = create_notification(
            recipient=sales_user,
            title='Order Created',
            message='A new order has been created',
            notification_type='order_created',
            related_object_type='order',
            related_object_id='123',
        )
        
        response = authenticated_employee_client.get(f'/api/notifications/{notification.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['type'] == 'order_created'
        assert response.data.get('related_object_type') == 'order'
    
    def test_1_3_2_leave_requested_notification_visibility(self, authenticated_admin_client, authenticated_employee_client, sales_user, admin_user):
        """Test Case 1.3.2: Leave Requested Notification Visibility"""
        leave_notif = create_notification(
            recipient=sales_user,
            title='Leave Request',
            message='Employee requested leave',
            notification_type='leave_requested',
        )
        
        # Employee should see their own request
        response = authenticated_employee_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert leave_notif.id in notification_ids
        
        # Admin should also see the request
        response = authenticated_admin_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert leave_notif.id in notification_ids
    
    def test_1_3_3_design_submitted_notification_visibility(self, authenticated_admin_client, authenticated_designer_client, designer_user, admin_user):
        """Test Case 1.3.3: Design Submitted Notification Visibility"""
        design_notif = create_notification(
            recipient=designer_user,
            title='Design Submitted',
            message='Design has been submitted',
            notification_type='design_submitted',
        )
        
        # Designer should see their own submission
        response = authenticated_designer_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert design_notif.id in notification_ids
        
        # Admin should also see the submission
        response = authenticated_admin_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert design_notif.id in notification_ids
    
    def test_1_3_4_leave_approved_notification_visibility(self, authenticated_admin_client, authenticated_employee_client, sales_user, admin_user):
        """Test Case 1.3.4: Leave Approved Notification Visibility"""
        approval_notif = create_notification(
            recipient=sales_user,
            title='Leave Approved',
            message='Your leave has been approved',
            notification_type='leave_approved',
            actor=admin_user,
        )
        
        # Employee should see their approval
        response = authenticated_employee_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert approval_notif.id in notification_ids
        
        # Admin should see the approval (they created it as the actor)
        response = authenticated_admin_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert approval_notif.id in notification_ids
    
    def test_1_3_5_design_rejected_notification_visibility(self, authenticated_admin_client, authenticated_designer_client, designer_user, admin_user):
        """Test Case 1.3.5: Design Rejected Notification Visibility"""
        rejection_notif = create_notification(
            recipient=designer_user,
            title='Design Rejected',
            message='Your design has been rejected',
            notification_type='design_rejected',
            actor=admin_user,
        )
        
        # Designer should see their rejection
        response = authenticated_designer_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert rejection_notif.id in notification_ids
        
        # Admin should see the rejection (they created it as the actor)
        response = authenticated_admin_client.get('/api/notifications/')
        assert response.status_code == status.HTTP_200_OK
        notification_ids = [n['id'] for n in response.data]
        assert rejection_notif.id in notification_ids
    
    def test_1_3_6_delivery_photo_uploaded_notification(self, authenticated_employee_client, sales_user):
        """Test Case 1.3.6: Delivery Photo Uploaded Notification"""
        notification = create_notification(
            recipient=sales_user,
            title='Delivery Photo',
            message='Delivery photo has been uploaded',
            notification_type='delivery_photo_uploaded',
            related_object_type='delivery',
            related_object_id='456',
        )
        
        response = authenticated_employee_client.get(f'/api/notifications/{notification.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['type'] == 'delivery_photo_uploaded'
    
    def test_1_3_7_monitoring_device_idle_notification(self, authenticated_admin_client, admin_user):
        """Test Case 1.3.7: Monitoring Device Idle Notification"""
        notification = create_notification(
            recipient=admin_user,
            title='Device Idle',
            message='A device has been idle',
            notification_type='monitoring_device_idle',
        )
        
        response = authenticated_admin_client.get(f'/api/notifications/{notification.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['type'] == 'monitoring_device_idle'

