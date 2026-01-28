import uuid
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from notifications.models import Notification
from notifications.services import create_notification, notify_admins
from notifications.permissions import CanViewNotification

User = get_user_model()


# ==================== Test Fixtures ====================

@pytest.fixture
def admin_user(db):
    """Create an admin user for testing"""
    return User.objects.create_user(
        username=f'admin_{uuid.uuid4().hex[:8]}',
        password='testpass123',
        roles=['admin'],
        email='admin@test.com'
    )


@pytest.fixture
def employee_user(db):
    """Create an employee user (non-admin) for testing"""
    return User.objects.create_user(
        username=f'employee_{uuid.uuid4().hex[:8]}',
        password='testpass123',
        roles=['sales'],
        email='employee@test.com'
    )


@pytest.fixture
def designer_user(db):
    """Create a designer user for testing"""
    return User.objects.create_user(
        username=f'designer_{uuid.uuid4().hex[:8]}',
        password='testpass123',
        roles=['designer'],
        email='designer@test.com'
    )


@pytest.fixture
def auth_client(admin_user):
    """Create authenticated API client for admin"""
    client = APIClient()
    login = client.post(
        '/api/auth/login',
        {'username': admin_user.username, 'password': 'testpass123', 'role': 'admin'},
        format='json',
    )
    token = login.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.fixture
def employee_client(employee_user):
    """Create authenticated API client for employee"""
    client = APIClient()
    login = client.post(
        '/api/auth/login',
        {'username': employee_user.username, 'password': 'testpass123', 'role': 'sales'},
        format='json',
    )
    token = login.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


# ==================== 1. Model Creation and Migrations ====================

@pytest.mark.django_db
def test_notification_model_creation_required_fields(employee_user):
    """Test that Notification model can be created with all required fields"""
    notification = Notification.objects.create(
        user=employee_user,
        message='Test notification message',
    )
    assert notification.id is not None
    assert notification.user == employee_user
    assert notification.message == 'Test notification message'
    assert notification.is_read is False
    assert notification.created_at is not None


@pytest.mark.django_db
def test_notification_model_creation_optional_fields(employee_user, admin_user):
    """Test that Notification model can be created with optional fields"""
    notification = Notification.objects.create(
        user=employee_user,
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


@pytest.mark.django_db
def test_notification_model_string_representation(employee_user):
    """Test model string representation"""
    notification = Notification.objects.create(
        user=employee_user,
        message='Test message',
    )
    str_repr = str(notification)
    assert employee_user.username in str_repr
    assert 'unread' in str_repr or 'read' in str_repr


@pytest.mark.django_db
def test_notification_model_ordering(employee_user):
    """Test model ordering (by created_at descending)"""
    # Create notifications with slight time differences
    notif1 = Notification.objects.create(user=employee_user, message='First')
    notif2 = Notification.objects.create(user=employee_user, message='Second')
    notif3 = Notification.objects.create(user=employee_user, message='Third')
    
    notifications = list(Notification.objects.filter(user=employee_user))
    # Should be ordered by created_at descending (newest first)
    assert notifications[0] == notif3
    assert notifications[1] == notif2
    assert notifications[2] == notif1


# ==================== 2. API Endpoints Return Correct Data ====================

@pytest.mark.django_db
def test_get_notifications_list_endpoint(employee_client, employee_user):
    """Test GET /api/notifications/ returns list of notifications"""
    # Create test notifications
    create_notification(
        recipient=employee_user,
        title='Test 1',
        message='Message 1',
        notification_type='order_created',
    )
    create_notification(
        recipient=employee_user,
        title='Test 2',
        message='Message 2',
        notification_type='order_assigned',
    )
    
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['title'] in ['Test 1', 'Test 2']
    assert 'id' in response.data[0]
    assert 'message' in response.data[0]
    assert 'type' in response.data[0]
    assert 'is_read' in response.data[0]
    assert 'created_at' in response.data[0]


@pytest.mark.django_db
def test_get_notification_detail_endpoint(employee_client, employee_user, admin_user):
    """Test GET /api/notifications/{id}/ returns single notification"""
    notification = create_notification(
        recipient=employee_user,
        title='Detail Test',
        message='Detail message',
        notification_type='order_created',
        actor=admin_user,
    )
    
    response = employee_client.get(f'/api/notifications/{notification.id}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == notification.id
    assert response.data['title'] == 'Detail Test'
    assert response.data['message'] == 'Detail message'
    assert response.data['type'] == 'order_created'
    assert 'actor_name' in response.data
    assert 'actor_id' in response.data
    assert 'user_id' in response.data


@pytest.mark.django_db
def test_patch_notification_updates(employee_client, employee_user):
    """Test PATCH /api/notifications/{id}/ updates notification"""
    notification = create_notification(
        recipient=employee_user,
        title='Update Test',
        message='Update message',
        notification_type='order_created',
    )
    assert notification.is_read is False
    
    response = employee_client.patch(
        f'/api/notifications/{notification.id}/',
        {'is_read': True},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    
    notification.refresh_from_db()
    assert notification.is_read is True


@pytest.mark.django_db
def test_filter_notifications_by_is_read(employee_client, employee_user):
    """Test filtering by query parameters (is_read)"""
    # Create read and unread notifications
    read_notif = create_notification(
        recipient=employee_user,
        title='Read',
        message='Read message',
        notification_type='order_created',
    )
    read_notif.is_read = True
    read_notif.save()
    
    unread_notif = create_notification(
        recipient=employee_user,
        title='Unread',
        message='Unread message',
        notification_type='order_assigned',
    )
    
    # Test unread filter
    response = employee_client.get('/api/notifications/?is_read=false')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == unread_notif.id
    
    # Test read filter
    response = employee_client.get('/api/notifications/?is_read=true')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == read_notif.id


@pytest.mark.django_db
def test_unread_count_endpoint(employee_client, employee_user):
    """Test unread count endpoint /api/notifications/unread-count/"""
    # Create 3 unread and 2 read notifications
    for i in range(3):
        create_notification(
            recipient=employee_user,
            title=f'Unread {i}',
            message=f'Message {i}',
            notification_type='order_created',
        )
    
    for i in range(2):
        read_notif = create_notification(
            recipient=employee_user,
            title=f'Read {i}',
            message=f'Message {i}',
            notification_type='order_created',
        )
        read_notif.is_read = True
        read_notif.save()
    
    response = employee_client.get('/api/notifications/unread-count/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3


# ==================== 3. Permissions Work (Users Only See Their Notifications) ====================

@pytest.mark.django_db
def test_employee_sees_only_own_notifications(employee_client, employee_user, admin_user):
    """Test employee user can only see their own notifications"""
    # Create notification for employee
    employee_notif = create_notification(
        recipient=employee_user,
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
    
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == employee_notif.id
    assert admin_notif.id not in [n['id'] for n in response.data]


@pytest.mark.django_db
def test_employee_cannot_access_other_user_notification_detail(employee_client, employee_user, admin_user):
    """Test employee user cannot access notification detail of another user"""
    admin_notif = create_notification(
        recipient=admin_user,
        title='Admin Notification',
        message='For admin',
        notification_type='order_created',
    )
    
    response = employee_client.get(f'/api/notifications/{admin_notif.id}/')
    assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unauthenticated_user_gets_401(employee_user):
    """Test unauthenticated user gets 401/403"""
    create_notification(
        recipient=employee_user,
        title='Test',
        message='Test',
        notification_type='order_created',
    )
    
    client = APIClient()
    response = client.get('/api/notifications/')
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


# ==================== 4. Notifications Are Created When Events Occur ====================

@pytest.mark.django_db
def test_notification_created_via_service(employee_user, admin_user):
    """Test notification creation using create_notification service"""
    notification = create_notification(
        recipient=employee_user,
        title='Service Test',
        message='Created via service',
        notification_type='order_created',
        actor=admin_user,
        related_object_type='order',
        related_object_id='123',
        metadata={'order_code': 'ORD-123'},
    )
    
    assert notification.id is not None
    assert notification.user == employee_user
    assert notification.title == 'Service Test'
    assert notification.type == 'order_created'
    assert notification.actor == admin_user
    assert notification.related_object_type == 'order'
    assert notification.related_object_id == '123'
    assert notification.metadata == {'order_code': 'ORD-123'}


@pytest.mark.django_db
def test_notify_admins_creates_for_all_admins(admin_user, employee_user):
    """Test notify_admins creates notifications for all admin users"""
    # Create another admin
    admin2 = User.objects.create_user(
        username=f'admin2_{uuid.uuid4().hex[:8]}',
        password='testpass123',
        roles=['admin'],
        email='admin2@test.com'
    )
    
    notify_admins(
        title='Admin Alert',
        message='All admins should see this',
        notification_type='monitoring_device_idle',
    )
    
    # Check both admins received notification
    admin1_notifs = Notification.objects.filter(user=admin_user, type='monitoring_device_idle')
    admin2_notifs = Notification.objects.filter(user=admin2, type='monitoring_device_idle')
    
    assert admin1_notifs.count() == 1
    assert admin2_notifs.count() == 1
    assert employee_user.notifications.filter(type='monitoring_device_idle').count() == 0


# ==================== 5. Admins Receive Request Notifications ====================

@pytest.mark.django_db
def test_admin_sees_own_notifications(auth_client, admin_user):
    """Test admin user sees their own notifications"""
    own_notif = create_notification(
        recipient=admin_user,
        title='Own Notification',
        message='For admin',
        notification_type='order_created',
    )
    
    response = auth_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    assert own_notif.id in [n['id'] for n in response.data]


@pytest.mark.django_db
def test_admin_sees_all_leave_requested_notifications(auth_client, admin_user, employee_user, designer_user):
    """Test admin user sees all leave_requested notifications (regardless of recipient)"""
    # Create leave request notifications for different users
    employee_leave = create_notification(
        recipient=employee_user,
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
    response = auth_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    notification_ids = [n['id'] for n in response.data]
    assert employee_leave.id in notification_ids
    assert designer_leave.id in notification_ids


@pytest.mark.django_db
def test_admin_sees_all_design_submitted_notifications(auth_client, admin_user, employee_user, designer_user):
    """Test admin user sees all design_submitted notifications (regardless of recipient)"""
    # Create design submitted notifications for different users
    employee_design = create_notification(
        recipient=employee_user,
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
    response = auth_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    notification_ids = [n['id'] for n in response.data]
    assert employee_design.id in notification_ids
    assert designer_design.id in notification_ids


@pytest.mark.django_db
def test_admin_sees_combined_queryset(auth_client, admin_user, employee_user):
    """Test admin user sees combined queryset (own + request notifications)"""
    # Create admin's own notification
    own_notif = create_notification(
        recipient=admin_user,
        title='Own',
        message='Own notification',
        notification_type='order_created',
    )
    
    # Create request notification for employee
    request_notif = create_notification(
        recipient=employee_user,
        title='Request',
        message='Leave request',
        notification_type='leave_requested',
    )
    
    # Create non-request notification for employee (admin should NOT see this)
    other_notif = create_notification(
        recipient=employee_user,
        title='Other',
        message='Other notification',
        notification_type='order_created',
    )
    
    response = auth_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    notification_ids = [n['id'] for n in response.data]
    assert own_notif.id in notification_ids
    assert request_notif.id in notification_ids
    assert other_notif.id not in notification_ids


@pytest.mark.django_db
def test_non_admin_does_not_see_request_notifications_from_others(employee_client, employee_user, designer_user):
    """Test non-admin user does NOT see request notifications from other users"""
    # Create request notification for designer
    request_notif = create_notification(
        recipient=designer_user,
        title='Request',
        message='Leave request',
        notification_type='leave_requested',
    )
    
    # Employee should NOT see this
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    notification_ids = [n['id'] for n in response.data]
    assert request_notif.id not in notification_ids


# ==================== 6. Employees Receive Approval/Rejection Notifications ====================

@pytest.mark.django_db
def test_employee_receives_leave_approved_notification(employee_client, employee_user, admin_user):
    """Test employee receives notification when their leave request is approved"""
    notification = create_notification(
        recipient=employee_user,
        title='Leave Approved',
        message='Your leave request has been approved',
        notification_type='leave_approved',
        actor=admin_user,
    )
    
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    assert notification.id in [n['id'] for n in response.data]


@pytest.mark.django_db
def test_employee_receives_leave_rejected_notification(employee_client, employee_user, admin_user):
    """Test employee receives notification when their leave request is rejected"""
    notification = create_notification(
        recipient=employee_user,
        title='Leave Rejected',
        message='Your leave request has been rejected',
        notification_type='leave_rejected',
        actor=admin_user,
    )
    
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    assert notification.id in [n['id'] for n in response.data]


@pytest.mark.django_db
def test_employee_receives_design_approved_notification(employee_client, employee_user, admin_user):
    """Test employee receives notification when their design is approved"""
    notification = create_notification(
        recipient=employee_user,
        title='Design Approved',
        message='Your design has been approved',
        notification_type='design_approved',
        actor=admin_user,
    )
    
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    assert notification.id in [n['id'] for n in response.data]


@pytest.mark.django_db
def test_employee_receives_design_rejected_notification(employee_client, employee_user, admin_user):
    """Test employee receives notification when their design is rejected"""
    notification = create_notification(
        recipient=employee_user,
        title='Design Rejected',
        message='Your design has been rejected',
        notification_type='design_rejected',
        actor=admin_user,
    )
    
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    assert notification.id in [n['id'] for n in response.data]


@pytest.mark.django_db
def test_approval_rejection_notifications_only_visible_to_requester(auth_client, admin_user, employee_user, designer_user):
    """Test approval/rejection notifications are ONLY visible to the requester (even admins cannot see others')"""
    # Create approval notification for employee
    employee_approval = create_notification(
        recipient=employee_user,
        title='Leave Approved',
        message='Your leave has been approved',
        notification_type='leave_approved',
        actor=admin_user,
    )
    
    # Create approval notification for designer
    designer_approval = create_notification(
        recipient=designer_user,
        title='Design Approved',
        message='Your design has been approved',
        notification_type='design_approved',
        actor=admin_user,
    )
    
    # Admin should NOT see these approval notifications (they're not the requester)
    response = auth_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    notification_ids = [n['id'] for n in response.data]
    assert employee_approval.id not in notification_ids
    assert designer_approval.id not in notification_ids


# ==================== 7. Channel-Based Rules Trigger Correctly ====================

@pytest.mark.django_db
def test_notification_with_tag_trigger(employee_user):
    """Test notifications are created based on tag_trigger field"""
    notification = Notification.objects.create(
        user=employee_user,
        title='Tagged Notification',
        message='Notification with tag',
        type='order_created',
        tag_trigger='sales',
    )
    
    assert notification.tag_trigger == 'sales'
    assert notification.type == 'order_created'


# ==================== 8. Mark as Read Functionality Works ====================

@pytest.mark.django_db
def test_patch_marks_notification_as_read(employee_client, employee_user):
    """Test PATCH /api/notifications/{id}/ marks notification as read"""
    notification = create_notification(
        recipient=employee_user,
        title='Test',
        message='Test message',
        notification_type='order_created',
    )
    assert notification.is_read is False
    
    response = employee_client.patch(
        f'/api/notifications/{notification.id}/',
        {'is_read': True},
        format='json',
    )
    
    assert response.status_code == status.HTTP_200_OK
    notification.refresh_from_db()
    assert notification.is_read is True


@pytest.mark.django_db
def test_user_can_only_mark_own_notifications_as_read(employee_client, employee_user, admin_user):
    """Test user can only mark their own notifications as read"""
    # Create notification for employee
    employee_notif = create_notification(
        recipient=employee_user,
        title='Employee',
        message='For employee',
        notification_type='order_created',
    )
    
    # Create notification for admin
    admin_notif = create_notification(
        recipient=admin_user,
        title='Admin',
        message='For admin',
        notification_type='order_created',
    )
    
    # Employee can mark their own notification as read
    response = employee_client.patch(
        f'/api/notifications/{employee_notif.id}/',
        {'is_read': True},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Employee cannot mark admin's notification as read
    response = employee_client.patch(
        f'/api/notifications/{admin_notif.id}/',
        {'is_read': True},
        format='json',
    )
    assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
def test_marking_already_read_notification_idempotent(employee_client, employee_user):
    """Test marking already-read notification as read (idempotent)"""
    notification = create_notification(
        recipient=employee_user,
        title='Test',
        message='Test',
        notification_type='order_created',
    )
    notification.is_read = True
    notification.save()
    
    # Marking as read again should still work
    response = employee_client.patch(
        f'/api/notifications/{notification.id}/',
        {'is_read': True},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    notification.refresh_from_db()
    assert notification.is_read is True


@pytest.mark.django_db
def test_mark_notification_as_unread(employee_client, employee_user):
    """Test marking notification as unread (if supported)"""
    notification = create_notification(
        recipient=employee_user,
        title='Test',
        message='Test',
        notification_type='order_created',
    )
    notification.is_read = True
    notification.save()
    
    # Mark as unread
    response = employee_client.patch(
        f'/api/notifications/{notification.id}/',
        {'is_read': False},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    notification.refresh_from_db()
    assert notification.is_read is False


# ==================== 9. Unread Count Is Accurate ====================

@pytest.mark.django_db
def test_unread_count_excludes_read_notifications(employee_client, employee_user):
    """Test unread count excludes read notifications"""
    # Create 3 unread
    for i in range(3):
        create_notification(
            recipient=employee_user,
            title=f'Unread {i}',
            message=f'Message {i}',
            notification_type='order_created',
        )
    
    # Create 2 read
    for i in range(2):
        read_notif = create_notification(
            recipient=employee_user,
            title=f'Read {i}',
            message=f'Message {i}',
            notification_type='order_created',
        )
        read_notif.is_read = True
        read_notif.save()
    
    response = employee_client.get('/api/notifications/unread-count/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3


@pytest.mark.django_db
def test_unread_count_includes_only_own_for_employees(employee_client, employee_user, admin_user):
    """Test unread count includes only user's own notifications (for employees)"""
    # Create notifications for employee
    for i in range(2):
        create_notification(
            recipient=employee_user,
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
    
    response = employee_client.get('/api/notifications/unread-count/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2


@pytest.mark.django_db
def test_unread_count_includes_admin_own_plus_requests(auth_client, admin_user, employee_user):
    """Test unread count includes admin's own + request notifications (for admins)"""
    # Create admin's own notification
    create_notification(
        recipient=admin_user,
        title='Own',
        message='Own notification',
        notification_type='order_created',
    )
    
    # Create request notification for employee (admin should see this)
    create_notification(
        recipient=employee_user,
        title='Request',
        message='Leave request',
        notification_type='leave_requested',
    )
    
    # Create non-request notification for employee (admin should NOT see this)
    create_notification(
        recipient=employee_user,
        title='Other',
        message='Other notification',
        notification_type='order_created',
    )
    
    response = auth_client.get('/api/notifications/unread-count/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2  # Own + request, but not the other


@pytest.mark.django_db
def test_unread_count_updates_when_marked_read(employee_client, employee_user):
    """Test unread count updates when notification is marked as read"""
    # Create 2 unread notifications
    notif1 = create_notification(
        recipient=employee_user,
        title='Test 1',
        message='Message 1',
        notification_type='order_created',
    )
    notif2 = create_notification(
        recipient=employee_user,
        title='Test 2',
        message='Message 2',
        notification_type='order_created',
    )
    
    # Check initial count
    response = employee_client.get('/api/notifications/unread-count/')
    assert response.data['count'] == 2
    
    # Mark one as read
    employee_client.patch(
        f'/api/notifications/{notif1.id}/',
        {'is_read': True},
        format='json',
    )
    
    # Check updated count
    response = employee_client.get('/api/notifications/unread-count/')
    assert response.data['count'] == 1


@pytest.mark.django_db
def test_unread_count_accurate_after_creating_new(employee_client, employee_user):
    """Test unread count is accurate after creating new notifications"""
    # Initial count should be 0
    response = employee_client.get('/api/notifications/unread-count/')
    assert response.data['count'] == 0
    
    # Create notification
    create_notification(
        recipient=employee_user,
        title='New',
        message='New notification',
        notification_type='order_created',
    )
    
    # Count should be 1
    response = employee_client.get('/api/notifications/unread-count/')
    assert response.data['count'] == 1


# ==================== Additional Test Cases ====================

# Role-Based Filtering (ViewSet get_queryset)
@pytest.mark.django_db
def test_viewset_queryset_filters_correctly_for_employees(employee_client, employee_user, admin_user):
    """Test NotificationViewSet.get_queryset() filters correctly for employees"""
    # Create notification for employee
    employee_notif = create_notification(
        recipient=employee_user,
        title='Employee',
        message='For employee',
        notification_type='order_created',
    )
    
    # Create notification for admin
    admin_notif = create_notification(
        recipient=admin_user,
        title='Admin',
        message='For admin',
        notification_type='order_created',
    )
    
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    notification_ids = [n['id'] for n in response.data]
    assert employee_notif.id in notification_ids
    assert admin_notif.id not in notification_ids


@pytest.mark.django_db
def test_viewset_queryset_filters_correctly_for_admins(auth_client, admin_user, employee_user):
    """Test NotificationViewSet.get_queryset() filters correctly for admins"""
    # Create admin's own notification
    own_notif = create_notification(
        recipient=admin_user,
        title='Own',
        message='Own notification',
        notification_type='order_created',
    )
    
    # Create request notification for employee
    request_notif = create_notification(
        recipient=employee_user,
        title='Request',
        message='Leave request',
        notification_type='leave_requested',
    )
    
    # Create non-request notification for employee
    other_notif = create_notification(
        recipient=employee_user,
        title='Other',
        message='Other notification',
        notification_type='order_created',
    )
    
    response = auth_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    notification_ids = [n['id'] for n in response.data]
    assert own_notif.id in notification_ids
    assert request_notif.id in notification_ids
    assert other_notif.id not in notification_ids


@pytest.mark.django_db
def test_viewset_queryset_ordering(auth_client, admin_user):
    """Test queryset ordering (by created_at descending)"""
    # Create notifications with slight delays
    notif1 = create_notification(
        recipient=admin_user,
        title='First',
        message='First message',
        notification_type='order_created',
    )
    notif2 = create_notification(
        recipient=admin_user,
        title='Second',
        message='Second message',
        notification_type='order_created',
    )
    notif3 = create_notification(
        recipient=admin_user,
        title='Third',
        message='Third message',
        notification_type='order_created',
    )
    
    response = auth_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    # Should be ordered newest first
    assert response.data[0]['id'] == notif3.id
    assert response.data[1]['id'] == notif2.id
    assert response.data[2]['id'] == notif1.id


@pytest.mark.django_db
def test_viewset_queryset_distinct_prevents_duplicates(auth_client, admin_user):
    """Test queryset distinct() prevents duplicates"""
    # Create a notification that would appear in both admin's own and request notifications
    # This shouldn't happen in practice, but test distinct() works
    notification = create_notification(
        recipient=admin_user,
        title='Own Request',
        message='Own leave request',
        notification_type='leave_requested',
    )
    
    response = auth_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK
    # Should appear only once
    notification_ids = [n['id'] for n in response.data]
    assert notification_ids.count(notification.id) == 1


# Permission Integration
@pytest.mark.django_db
def test_can_view_notification_has_permission_allows_authenticated(employee_client):
    """Test CanViewNotification.has_permission() allows authenticated users"""
    response = employee_client.get('/api/notifications/')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_can_view_notification_object_permission_own_notifications(employee_user, admin_user):
    """Test CanViewNotification.has_object_permission() for own notifications"""
    notification = create_notification(
        recipient=employee_user,
        title='Test',
        message='Test',
        notification_type='order_created',
    )
    
    permission = CanViewNotification()
    # Mock request object
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    request = MockRequest(employee_user)
    assert permission.has_object_permission(request, None, notification) is True


@pytest.mark.django_db
def test_can_view_notification_object_permission_admin_request_notifications(admin_user, employee_user):
    """Test CanViewNotification.has_object_permission() for admin request notifications"""
    notification = create_notification(
        recipient=employee_user,
        title='Request',
        message='Leave request',
        notification_type='leave_requested',
    )
    
    permission = CanViewNotification()
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    request = MockRequest(admin_user)
    assert permission.has_object_permission(request, None, notification) is True


@pytest.mark.django_db
def test_can_view_notification_blocks_approval_rejection_for_non_owners(admin_user, employee_user):
    """Test CanViewNotification.has_object_permission() blocks approval/rejection notifications for non-owners"""
    notification = create_notification(
        recipient=employee_user,
        title='Approval',
        message='Leave approved',
        notification_type='leave_approved',
    )
    
    permission = CanViewNotification()
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    request = MockRequest(admin_user)
    # Admin should NOT be able to see employee's approval notification
    assert permission.has_object_permission(request, None, notification) is False


# Service Functions
@pytest.mark.django_db
def test_create_notification_handles_optional_fields(employee_user):
    """Test create_notification() handles optional fields correctly"""
    notification = create_notification(
        recipient=employee_user,
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


@pytest.mark.django_db
def test_create_notification_handles_edge_cases(employee_user):
    """Test service functions handle edge cases (None values, empty strings, etc.)"""
    # Test with empty strings
    notification = create_notification(
        recipient=employee_user,
        title='',
        message='',
        notification_type='order_created',
    )
    assert notification.id is not None
    
    # Test with None metadata (should default to empty dict)
    notification2 = create_notification(
        recipient=employee_user,
        title='Test',
        message='Test',
        notification_type='order_created',
        metadata=None,
    )
    assert notification2.metadata == {}
