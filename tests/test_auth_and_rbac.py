import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from monitoring.models import Device, Org
from django.utils import timezone


@pytest.fixture
def test_device(db):
    """Create a test device for login requirements"""
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


@pytest.mark.django_db
def test_login_and_me():
    User = get_user_model()
    u = User.objects.create_user(username='tester', password='pw', roles=['admin'])
    c = APIClient()
    resp = c.post('/api/auth/login', {'username': 'tester', 'password': 'pw'}, format='json')
    assert resp.status_code == 200
    token = resp.data['token']
    c.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    me = c.get('/api/auth/me')
    assert me.status_code == 200
    assert me.data['username'] == 'tester'


@pytest.mark.django_db
def test_orders_stage_rbac_denied_for_sales_on_printing(test_device):
    User = get_user_model()
    sales = User.objects.create_user(username='sales', password='pw', roles=['sales'])
    c = APIClient()
    login = c.post('/api/auth/login', {'username': 'sales', 'password': 'pw'}, format='json', HTTP_X_DEVICE_ID='test-device-123')
    token = login.data['token']
    c.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    order = c.post('/api/orders/', {'clientName': 'A', 'items': [{'name': 'Flyer', 'quantity': 1, 'unit_price': 10.0}], 'specs': '', 'urgency': ''}, format='json')
    assert order.status_code == 201
    oid = order.data['data']['id']
    patch = c.patch(f'/api/orders/{oid}', {'stage': 'printing', 'payload': {'print_operator': 'X'}}, format='json')
    assert patch.status_code == 403

