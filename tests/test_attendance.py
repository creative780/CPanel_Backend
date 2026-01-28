import pytest
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from attendance.models import Attendance, AttendanceRule
from monitoring.models import Employee as MonitoringEmployee


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_device(db):
    """Create a test device for login requirements"""
    from monitoring.models import Device, Org
    from django.utils import timezone
    
    org = Org.objects.create(name='Test Org', id='test_org_123')
    device = Device.objects.create(
        id='test-device-123',
        hostname='test-host',
        os='Windows',
        status='ONLINE',
        org=org,
        last_heartbeat=timezone.now(),  # Recent heartbeat
    )
    return device


def authenticate(client: APIClient, username: str, password: str, role: str):
    # For non-admin roles, include device_id header to satisfy device requirement
    headers = {}
    if role != 'admin':
        headers['HTTP_X_DEVICE_ID'] = 'test-device-123'
    
    resp = client.post(
        '/api/auth/login',
        {'username': username, 'password': password, 'role': role},
        format='json',
        **headers
    )
    assert resp.status_code == 200, f"Login failed: {resp.data if hasattr(resp, 'data') else resp.content}"
    token = resp.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


@pytest.mark.django_db
def test_check_in_and_check_out_flow(api_client, monkeypatch, test_device):
    User = get_user_model()
    user = User.objects.create_user(
        username='alice',
        password='pw',
        roles=['sales'],
        first_name='Alice',
        last_name='Smith',
        email='alice@example.com',
    )

    rules = AttendanceRule.get_solo()
    rules.work_start = time(0, 0)
    rules.grace_minutes = 24 * 60
    rules.save()

    def fake_lookup(ip):
        assert ip == '203.0.113.5'
        return {
            'location_lat': Decimal('25.2048'),
            'location_lng': Decimal('55.2708'),
            'location_address': 'Dubai, UAE',
        }

    monkeypatch.setattr('attendance.utils.lookup_location_for_ip', fake_lookup)
    monkeypatch.setattr(
        'app.common.net_utils.resolve_client_hostname',
        lambda ip: 'desktop-alice.example.com' if ip else None,
    )

    authenticate(api_client, 'alice', 'pw', 'sales')

    check_in = api_client.post(
        '/api/attendance/check-in/',
        {'notes': 'Starting'},
        format='json',
        REMOTE_ADDR='203.0.113.5',
        HTTP_USER_AGENT='Mozilla/5.0 (Macintosh)',
        HTTP_X_DEVICE_ID='device-123',
    )
    assert check_in.status_code == 201
    record = Attendance.objects.get(id=check_in.data['id'])
    assert record.status == Attendance.STATUS_PRESENT
    assert record.ip_address == '203.0.113.5'
    assert record.device_id == 'device-123'
    assert record.device_info.startswith('Mozilla/5.0')
    assert record.location_address == 'Dubai, UAE'
    assert record.location_lat == Decimal('25.2048')
    assert record.location_lng == Decimal('55.2708')
    assert record.device_name == 'desktop-alice.example.com'

    earlier = timezone.now() - timedelta(hours=8)
    Attendance.objects.filter(id=record.id).update(check_in=earlier, date=earlier.date())

    check_out = api_client.post(
        '/api/attendance/check-out/',
        {'notes': 'Finished'},
        format='json',
        REMOTE_ADDR='203.0.113.5',
        HTTP_USER_AGENT='Mozilla/5.0 (Macintosh)',
        HTTP_X_DEVICE_ID='device-123',
    )
    assert check_out.status_code == 200
    record.refresh_from_db()
    assert record.check_out is not None
    assert pytest.approx(float(record.total_hours), rel=0.05) == 8.0
    assert 'Finished' in record.notes
    assert record.device_name == 'desktop-alice.example.com'
    # Verify monitored attendance (has device_id)
    assert record.is_monitored is True
    # Verify overtime calculation (8 hours = 480 minutes, standard = 510, so no overtime)
    record.refresh_from_db()
    assert record.overtime_minutes == 0


@pytest.mark.django_db
def test_attendance_listing_and_filters(api_client, test_device):
    User = get_user_model()
    admin = User.objects.create_user(username='admin', password='pw', roles=['admin'], email='admin@example.com')
    employee = User.objects.create_user(username='bob', password='pw', roles=['sales'], first_name='Bob', email='bob@example.com')

    tz = timezone.get_current_timezone()
    first_day = timezone.make_aware(datetime(2024, 1, 2, 9, 0), tz)
    Attendance.objects.create(
        employee=employee,
        check_in=first_day,
        check_out=first_day + timedelta(hours=8),
        date=first_day.date(),
        status=Attendance.STATUS_PRESENT,
    )
    Attendance.objects.create(
        employee=employee,
        check_in=first_day + timedelta(days=1),
        check_out=first_day + timedelta(days=1, hours=8),
        date=(first_day + timedelta(days=1)).date(),
        status=Attendance.STATUS_LATE,
    )

    authenticate(api_client, 'admin', 'pw', 'admin')

    resp = api_client.get('/api/attendance/', {'employee': employee.id})
    assert resp.status_code == 200
    assert len(resp.data) == 2

    resp_search = api_client.get('/api/attendance/', {'search': 'bob'})
    assert resp_search.status_code == 200
    assert len(resp_search.data) >= 2


@pytest.mark.django_db
def test_rules_update_and_summary(api_client, test_device):
    User = get_user_model()
    admin = User.objects.create_user(username='admin2', password='pw', roles=['admin'])
    authenticate(api_client, 'admin2', 'pw', 'admin')

    rules_get = api_client.get('/api/attendance/rules/')
    assert rules_get.status_code == 200

    update_payload = {
        'work_start': '08:30:00',
        'work_end': '17:00:00',
        'grace_minutes': 10,
        'standard_work_minutes': 480,
        'overtime_after_minutes': 480,
        'late_penalty_per_minute': '1.50',
        'per_day_deduction': '0.00',
        'overtime_rate_per_minute': '2.00',
        'weekend_days': [5, 6],
    }
    rules_put = api_client.put('/api/attendance/rules/', update_payload, format='json')
    assert rules_put.status_code == 200
    assert rules_put.data['grace_minutes'] == 10

    summary = api_client.get('/api/attendance/summary/')
    assert summary.status_code == 200
    assert 'total_records' in summary.data


@pytest.mark.django_db
def test_payroll_generation(api_client, test_device):
    User = get_user_model()
    admin = User.objects.create_user(username='pay-admin', password='pw', roles=['admin'])
    employee = User.objects.create_user(
        username='payroll-user',
        password='pw',
        roles=['sales'],
        first_name='Payroll',
        last_name='User',
        email='payroll@example.com',
    )
    MonitoringEmployee.objects.create(name='Payroll User', email='payroll@example.com', salary=6000)

    rules = AttendanceRule.get_solo()
    rules.work_start = time(9, 0)
    rules.work_end = time(17, 30)
    rules.grace_minutes = 5
    rules.standard_work_minutes = 480
    rules.overtime_after_minutes = 480
    rules.late_penalty_per_minute = 0
    rules.per_day_deduction = 0
    rules.overtime_rate_per_minute = 2
    rules.weekend_days = [5, 6]
    rules.save()

    tz = timezone.get_current_timezone()
    day_one_in = timezone.make_aware(datetime(2024, 1, 2, 9, 0), tz)
    att1 = Attendance.objects.create(
        employee=employee,
        check_in=day_one_in,
        check_out=day_one_in + timedelta(hours=8, minutes=30),
        date=day_one_in.date(),
        status=Attendance.STATUS_PRESENT,
        device_id='test-device-123',  # Mark as monitored for overtime calculation
    )
    att1.save()  # Trigger recalculation
    day_two_in = timezone.make_aware(datetime(2024, 1, 3, 9, 20), tz)
    att2 = Attendance.objects.create(
        employee=employee,
        check_in=day_two_in,
        check_out=day_two_in + timedelta(hours=8, minutes=40),
        date=day_two_in.date(),
        status=Attendance.STATUS_LATE,
        device_id='test-device-123',  # Mark as monitored for overtime calculation
    )
    att2.save()  # Trigger recalculation

    authenticate(api_client, 'pay-admin', 'pw', 'admin')

    payroll = api_client.get('/api/attendance/payroll/', {'month': '2024-01'})
    assert payroll.status_code == 200
    assert payroll.data['month'] == '2024-01'
    assert payroll.data['working_days'] > 0
    rows = payroll.data['rows']
    assert len(rows) == 1
    row = rows[0]
    assert row['employee']['email'] == 'payroll@example.com'
    assert row['present_days'] == 2
    assert row['total_late_minutes'] == 15
    assert row['total_overtime_minutes'] == 70
    assert row['base_salary'] == 6000.0
    assert row['net_pay'] == pytest.approx(6000.0 + 70 * 2, rel=0.01)


@pytest.mark.django_db
def test_overtime_calculation_monitored_only(api_client, monkeypatch, test_device):
    """Test that overtime is only calculated for monitored attendance."""
    User = get_user_model()
    user = User.objects.create_user(
        username='overtime-user',
        password='pw',
        roles=['sales'],
        first_name='Overtime',
        last_name='User',
        email='overtime@example.com',
    )

    rules = AttendanceRule.get_solo()
    rules.standard_work_minutes = 480  # 8 hours
    rules.save()

    authenticate(api_client, 'overtime-user', 'pw', 'sales')

    # Test 1: Monitored attendance with overtime
    check_in = api_client.post(
        '/api/attendance/check-in/',
        {'notes': 'Monitored check-in'},
        format='json',
        REMOTE_ADDR='203.0.113.5',
        HTTP_X_DEVICE_ID='device-monitored-123',
    )
    assert check_in.status_code == 201
    record_id = check_in.data['id']
    record = Attendance.objects.get(id=record_id)
    assert record.is_monitored is True

    # Simulate 10 hours of work (600 minutes) - should have 120 minutes overtime
    tz = timezone.get_current_timezone()
    check_in_time = timezone.make_aware(datetime(2024, 1, 2, 9, 0), tz)
    check_out_time = check_in_time + timedelta(hours=10)
    record.refresh_from_db()
    record.check_in = check_in_time
    record.check_out = check_out_time
    record.date = check_in_time.date()
    record.save()  # This will trigger _recalculate_breaks which updates effective_minutes
    
    record.refresh_from_db()
    assert record.effective_minutes == 600  # 10 hours = 600 minutes
    record.calculate_overtime(save=True)
    record.refresh_from_db()
    assert record.overtime_minutes == 120  # 600 - 480 = 120

    # Test 2: Non-monitored attendance (no device_id) - should have 0 overtime
    check_in2 = api_client.post(
        '/api/attendance/check-in/',
        {'notes': 'Manual check-in'},
        format='json',
        REMOTE_ADDR='203.0.113.5',
        # No device_id header
    )
    assert check_in2.status_code == 201
    record_id2 = check_in2.data['id']
    record2 = Attendance.objects.get(id=record_id2)
    # Explicitly clear device fields to ensure it's not monitored
    # device_id is CharField, so use empty string instead of None
    record2.device_id = ''
    record2.device_name = None
    record2.save()
    record2.refresh_from_db()
    assert record2.is_monitored is False

    check_in_time2 = timezone.make_aware(datetime(2024, 1, 3, 9, 0), tz)
    check_out_time2 = check_in_time2 + timedelta(hours=10)
    record2.refresh_from_db()
    record2.check_in = check_in_time2
    record2.check_out = check_out_time2
    record2.date = check_in_time2.date()
    record2.save()  # This will trigger _recalculate_breaks which updates effective_minutes
    
    record2.refresh_from_db()
    record2.calculate_overtime(save=True)
    record2.refresh_from_db()
    assert record2.overtime_minutes == 0  # Non-monitored, so no overtime


@pytest.mark.django_db
def test_overtime_verification_required(api_client, monkeypatch, test_device):
    """Test that overtime >4 hours requires verification."""
    User = get_user_model()
    admin = User.objects.create_user(
        username='overtime-admin',
        password='pw',
        roles=['admin'],
        email='admin-overtime@example.com',
    )
    user = User.objects.create_user(
        username='overtime-employee',
        password='pw',
        roles=['sales'],
        first_name='Employee',
        last_name='Overtime',
        email='employee-overtime@example.com',
    )

    rules = AttendanceRule.get_solo()
    rules.standard_work_minutes = 480  # 8 hours
    rules.save()

    authenticate(api_client, 'overtime-employee', 'pw', 'sales')

    # Create attendance with >4 hours overtime (5 hours = 300 minutes)
    check_in = api_client.post(
        '/api/attendance/check-in/',
        {'notes': 'Long day'},
        format='json',
        REMOTE_ADDR='203.0.113.5',
        HTTP_X_DEVICE_ID='device-123',
    )
    assert check_in.status_code == 201
    record_id = check_in.data['id']

    tz = timezone.get_current_timezone()
    check_in_time = timezone.make_aware(datetime(2024, 1, 2, 9, 0), tz)
    check_out_time = check_in_time + timedelta(hours=13)  # 13 hours = 780 minutes, 300 minutes overtime
    record = Attendance.objects.get(id=record_id)
    record.check_in = check_in_time
    record.check_out = check_out_time
    record.date = check_in_time.date()
    record.save()  # This will trigger _recalculate_breaks which updates effective_minutes
    
    record.refresh_from_db()
    # effective_minutes should be 780 (13 hours) - 0 breaks = 780 minutes
    assert record.effective_minutes == 780
    record.calculate_overtime(save=True)
    record.refresh_from_db()
    assert record.overtime_minutes == 300  # 780 - 480 = 300
    assert record.requires_verification is True  # >240 minutes (4 hours)
    assert record.overtime_verified is False

    # Test admin can verify overtime
    authenticate(api_client, 'overtime-admin', 'pw', 'admin')
    verify_resp = api_client.post(
        '/api/attendance/overtime/verify/',
        {'attendance_id': record_id},
        format='json',
    )
    assert verify_resp.status_code == 200
    record.refresh_from_db()
    assert record.overtime_verified is True
    assert record.overtime_verified_by == admin
