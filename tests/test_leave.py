import pytest
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from attendance.models import Attendance, AttendanceRule, LeaveRequest, Holiday


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_device(db):
    """Create a test device for login requirements"""
    from monitoring.models import Device, Org
    
    org = Org.objects.create(name='Test Org', id='test_org_123')
    device = Device.objects.create(
        id='test-device-123',
        hostname='test-host',
        os='Windows',
        status='ONLINE',
        org=org,
        last_heartbeat=timezone.now(),
    )
    return device


def authenticate(client: APIClient, username: str, password: str, role: str):
    headers = {}
    if role != 'admin':
        headers['HTTP_X_DEVICE_ID'] = 'test-device-123'
    
    resp = client.post(
        '/api/auth/login',
        {'username': username, 'password': password, 'role': role},
        format='json',
        **headers
    )
    assert resp.status_code == 200
    token = resp.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return resp.data


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='admin123',
        role='admin'
    )


@pytest.fixture
def employee_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username='employee',
        email='employee@test.com',
        password='emp123',
        role='employee'
    )


@pytest.fixture
def attendance_rules(db):
    return AttendanceRule.get_solo()


@pytest.mark.django_db
def test_create_full_day_leave_request(api_client, employee_user, test_device):
    """Test creating a full-day leave request"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    response = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'full_day',
            'start_date': str(tomorrow),
            'reason': 'Personal leave'
        },
        format='json'
    )
    
    assert response.status_code == 201
    assert response.data['leave_type'] == 'full_day'
    assert response.data['status'] == 'pending'
    assert response.data['reason'] == 'Personal leave'
    assert response.data['employee'] == employee_user.id


@pytest.mark.django_db
def test_create_partial_day_leave_request(api_client, employee_user, test_device):
    """Test creating a partial-day leave request"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    response = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'partial_day',
            'start_date': str(tomorrow),
            'start_time': '10:00',
            'end_time': '14:00',
            'reason': 'Doctor appointment'
        },
        format='json'
    )
    
    assert response.status_code == 201
    assert response.data['leave_type'] == 'partial_day'
    assert response.data['start_time'] == '10:00:00'
    assert response.data['end_time'] == '14:00:00'


@pytest.mark.django_db
def test_create_multiple_days_leave_request(api_client, employee_user, test_device):
    """Test creating a multiple-days leave request"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    start_date = today + timedelta(days=1)
    end_date = today + timedelta(days=3)
    
    response = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'multiple_days',
            'start_date': str(start_date),
            'end_date': str(end_date),
            'reason': 'Vacation'
        },
        format='json'
    )
    
    assert response.status_code == 201
    assert response.data['leave_type'] == 'multiple_days'
    assert response.data['end_date'] == str(end_date)


@pytest.mark.django_db
def test_leave_request_conflict_detection(api_client, employee_user, test_device):
    """Test that overlapping leave requests are detected"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    # Create first leave request
    response1 = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'full_day',
            'start_date': str(tomorrow),
            'reason': 'First leave'
        },
        format='json'
    )
    assert response1.status_code == 201
    
    # Try to create overlapping leave request
    response2 = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'full_day',
            'start_date': str(tomorrow),
            'reason': 'Second leave'
        },
        format='json'
    )
    
    assert response2.status_code == 400
    assert 'conflict' in response2.data['detail'].lower()


@pytest.mark.django_db
def test_admin_approve_leave_request(api_client, admin_user, employee_user, test_device):
    """Test admin approving a leave request"""
    authenticate(api_client, 'admin', 'admin123', 'admin')
    
    # Create leave request as employee
    api_client.credentials()  # Clear credentials
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    create_response = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'full_day',
            'start_date': str(tomorrow),
            'reason': 'Personal leave'
        },
        format='json'
    )
    leave_id = create_response.data['id']
    
    # Approve as admin
    api_client.credentials()
    authenticate(api_client, 'admin', 'admin123', 'admin')
    
    approve_response = api_client.post(
        f'/api/attendance/leave-requests/{leave_id}/approve/',
        {'is_paid': True},
        format='json'
    )
    
    assert approve_response.status_code == 200
    assert approve_response.data['status'] == 'approved'
    assert approve_response.data['is_paid'] is True
    assert approve_response.data['approved_by'] == admin_user.id


@pytest.mark.django_db
def test_admin_reject_leave_request(api_client, admin_user, employee_user, test_device):
    """Test admin rejecting a leave request"""
    authenticate(api_client, 'admin', 'admin123', 'admin')
    
    # Create leave request as employee
    api_client.credentials()
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    create_response = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'full_day',
            'start_date': str(tomorrow),
            'reason': 'Personal leave'
        },
        format='json'
    )
    leave_id = create_response.data['id']
    
    # Reject as admin
    api_client.credentials()
    authenticate(api_client, 'admin', 'admin123', 'admin')
    
    reject_response = api_client.post(
        f'/api/attendance/leave-requests/{leave_id}/reject/',
        {'rejection_reason': 'Insufficient leave balance'},
        format='json'
    )
    
    assert reject_response.status_code == 200
    assert reject_response.data['status'] == 'rejected'
    assert reject_response.data['rejection_reason'] == 'Insufficient leave balance'
    assert reject_response.data['approved_by'] == admin_user.id


@pytest.mark.django_db
def test_employee_cannot_approve_leave(api_client, employee_user, test_device):
    """Test that employees cannot approve leave requests"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    create_response = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'full_day',
            'start_date': str(tomorrow),
            'reason': 'Personal leave'
        },
        format='json'
    )
    leave_id = create_response.data['id']
    
    # Try to approve as employee (should fail)
    approve_response = api_client.post(
        f'/api/attendance/leave-requests/{leave_id}/approve/',
        {'is_paid': True},
        format='json'
    )
    
    assert approve_response.status_code == 403


@pytest.mark.django_db
def test_leave_hours_calculation_full_day(attendance_rules, employee_user):
    """Test leave hours calculation for full day"""
    today = timezone.localdate()
    leave = LeaveRequest.objects.create(
        employee=employee_user,
        leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
        start_date=today,
        reason='Test leave'
    )
    
    expected_hours = round(attendance_rules.standard_work_minutes / 60, 2)
    assert leave.get_total_hours() == expected_hours


@pytest.mark.django_db
def test_leave_hours_calculation_partial_day(employee_user):
    """Test leave hours calculation for partial day"""
    today = timezone.localdate()
    leave = LeaveRequest.objects.create(
        employee=employee_user,
        leave_type=LeaveRequest.LEAVE_TYPE_PARTIAL_DAY,
        start_date=today,
        start_time=time(10, 0),
        end_time=time(14, 0),
        reason='Test partial leave'
    )
    
    # 4 hours between 10:00 and 14:00
    assert leave.get_total_hours() == 4.0


@pytest.mark.django_db
def test_leave_hours_calculation_multiple_days(attendance_rules, employee_user):
    """Test leave hours calculation for multiple days"""
    today = timezone.localdate()
    start_date = today + timedelta(days=1)
    end_date = today + timedelta(days=3)  # 3 days
    
    leave = LeaveRequest.objects.create(
        employee=employee_user,
        leave_type=LeaveRequest.LEAVE_TYPE_MULTIPLE_DAYS,
        start_date=start_date,
        end_date=end_date,
        reason='Test multiple days leave'
    )
    
    # Should calculate based on working days (excluding weekends)
    hours = leave.get_total_hours()
    assert hours > 0
    # Should be approximately 3 days * standard hours per day
    expected_min = 2 * (attendance_rules.standard_work_minutes / 60)  # At least 2 days
    expected_max = 3 * (attendance_rules.standard_work_minutes / 60)  # At most 3 days
    assert expected_min <= hours <= expected_max


@pytest.mark.django_db
def test_payroll_integration_with_leave(api_client, admin_user, employee_user, test_device, attendance_rules):
    """Test that payroll calculation includes leave hours"""
    from monitoring.models import Employee as MonitoringEmployee
    
    authenticate(api_client, 'admin', 'admin123', 'admin')
    
    # Create monitoring employee with salary
    MonitoringEmployee.objects.create(
        email=employee_user.email,
        salary=Decimal('5000.00')
    )
    
    # Create approved paid leave
    today = timezone.localdate()
    leave = LeaveRequest.objects.create(
        employee=employee_user,
        leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
        start_date=today,
        reason='Paid leave',
        status=LeaveRequest.STATUS_APPROVED,
        is_paid=True,
        approved_by=admin_user,
        approved_at=timezone.now()
    )
    
    # Create approved unpaid leave
    tomorrow = today + timedelta(days=1)
    unpaid_leave = LeaveRequest.objects.create(
        employee=employee_user,
        leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
        start_date=tomorrow,
        reason='Unpaid leave',
        status=LeaveRequest.STATUS_APPROVED,
        is_paid=False,
        approved_by=admin_user,
        approved_at=timezone.now()
    )
    
    # Get payroll data
    year = today.year
    month = today.month
    payroll_response = api_client.get(f'/api/attendance/payroll/?month={year}-{month:02d}')
    
    assert payroll_response.status_code == 200
    rows = payroll_response.data['rows']
    employee_row = next((r for r in rows if r['employee']['id'] == employee_user.id), None)
    
    assert employee_row is not None
    assert employee_row['total_leave_hours'] > 0
    assert employee_row['paid_leave_hours'] > 0
    assert employee_row['unpaid_leave_hours'] > 0
    # Adjusted effective hours should account for unpaid leave
    assert 'adjusted_effective_hours' in employee_row
    assert employee_row['adjusted_effective_hours'] <= employee_row['total_effective_hours']


@pytest.mark.django_db
def test_employee_can_view_own_leaves(api_client, employee_user, test_device):
    """Test that employees can view their own leave requests"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    # Create leave request
    LeaveRequest.objects.create(
        employee=employee_user,
        leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
        start_date=tomorrow,
        reason='Personal leave'
    )
    
    # List leave requests
    response = api_client.get('/api/attendance/leave-requests/')
    
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['employee'] == employee_user.id


@pytest.mark.django_db
def test_employee_cannot_view_other_leaves(api_client, employee_user, test_device):
    """Test that employees cannot view other employees' leave requests"""
    User = get_user_model()
    other_employee = User.objects.create_user(
        username='other_emp',
        email='other@test.com',
        password='other123',
        role='employee'
    )
    
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    # Create leave request for other employee
    LeaveRequest.objects.create(
        employee=other_employee,
        leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
        start_date=tomorrow,
        reason='Other employee leave'
    )
    
    # List leave requests - should only see own
    response = api_client.get('/api/attendance/leave-requests/')
    
    assert response.status_code == 200
    assert len(response.data) == 0  # Should not see other employee's leave


@pytest.mark.django_db
def test_admin_can_view_all_leaves(api_client, admin_user, employee_user, test_device):
    """Test that admins can view all leave requests"""
    User = get_user_model()
    other_employee = User.objects.create_user(
        username='other_emp',
        email='other@test.com',
        password='other123',
        role='employee'
    )
    
    authenticate(api_client, 'admin', 'admin123', 'admin')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    # Create leave requests for multiple employees
    LeaveRequest.objects.create(
        employee=employee_user,
        leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
        start_date=tomorrow,
        reason='Employee 1 leave'
    )
    LeaveRequest.objects.create(
        employee=other_employee,
        leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
        start_date=tomorrow,
        reason='Employee 2 leave'
    )
    
    # List leave requests - should see all
    response = api_client.get('/api/attendance/leave-requests/')
    
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_leave_request_validation_missing_reason(api_client, employee_user, test_device):
    """Test that leave request requires a reason"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    response = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'full_day',
            'start_date': str(tomorrow),
            'reason': ''  # Empty reason
        },
        format='json'
    )
    
    assert response.status_code == 400


@pytest.mark.django_db
def test_leave_request_validation_past_date(api_client, employee_user, test_device):
    """Test that leave request cannot be for past dates"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    yesterday = timezone.localdate() - timedelta(days=1)
    
    response = api_client.post(
        '/api/attendance/leave-requests/',
        {
            'leave_type': 'full_day',
            'start_date': str(yesterday),
            'reason': 'Past leave'
        },
        format='json'
    )
    
    assert response.status_code == 400
    assert 'past' in response.data.get('start_date', [''])[0].lower() or 'past' in str(response.data).lower()


@pytest.mark.django_db
def test_leave_calendar_view(api_client, employee_user, test_device):
    """Test calendar view endpoint"""
    authenticate(api_client, 'employee', 'emp123', 'employee')
    
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    
    # Create leave request
    LeaveRequest.objects.create(
        employee=employee_user,
        leave_type=LeaveRequest.LEAVE_TYPE_FULL_DAY,
        start_date=tomorrow,
        reason='Calendar test leave'
    )
    
    # Get calendar data
    year = tomorrow.year
    month = tomorrow.month
    response = api_client.get(f'/api/attendance/leave-requests/calendar/?year={year}&month={month}')
    
    assert response.status_code == 200
    assert isinstance(response.data, dict)
    # Check that the leave appears on the correct date
    date_key = str(tomorrow)
    assert date_key in response.data
    assert len(response.data[date_key]) > 0


