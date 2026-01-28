import uuid
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from clients.models import Lead, Organization, Contact
from accounts.models import Role


def _auth_client(role: str = 'admin', test_device=None) -> APIClient:
    """Create and authenticate an APIClient for the given role."""
    User = get_user_model()
    username = f"{role}_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(username=username, password='pw', roles=[role])
    client = APIClient()
    
    # Admin doesn't need device_id, others do
    login_data = {
        'username': user.username,
        'password': 'pw',
        'role': role,
    }
    headers = {}
    if not user.is_admin() and test_device:
        headers['HTTP_X_DEVICE_ID'] = test_device.id
    
    login = client.post(
        '/api/auth/login',
        login_data,
        format='json',
        **headers
    )
    token = login.data.get('token') or login.data.get('access')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.mark.django_db(transaction=True)
def test_win_loss_by_segment_endpoint_with_data(admin_client):
    """Test win/loss by segment endpoint with sample data"""
    client = admin_client
    
    # Create test organization and contact
    org1 = Organization.objects.create(name='Test Org 1')
    org2 = Organization.objects.create(name='Test Org 2')
    contact1 = Contact.objects.create(org=org1, first_name='John', last_name='Doe')
    contact2 = Contact.objects.create(org=org2, first_name='Jane', last_name='Smith')
    
    # Create test leads with different segments and stages
    Lead.objects.create(
        org=org1,
        contact=contact1,
        segment='smb',
        stage='won',
        value=5000
    )
    Lead.objects.create(
        org=org1,
        contact=contact1,
        segment='smb',
        stage='won',
        value=3000
    )
    Lead.objects.create(
        org=org1,
        contact=contact1,
        segment='smb',
        stage='lost',
        value=2000
    )
    Lead.objects.create(
        org=org2,
        contact=contact2,
        segment='enterprise',
        stage='won',
        value=10000
    )
    Lead.objects.create(
        org=org2,
        contact=contact2,
        segment='enterprise',
        stage='lost',
        value=8000
    )
    
    # Call the endpoint
    response = client.get('/api/dashboard/win-loss-by-segment/')
    
    assert response.status_code == 200
    data = response.data
    assert data['smb_win'] == 2
    assert data['smb_loss'] == 1
    assert data['enterprise_win'] == 1
    assert data['enterprise_loss'] == 1


@pytest.mark.django_db(transaction=True)
def test_win_loss_by_segment_endpoint_no_data(admin_client):
    """Test win/loss by segment endpoint with no leads"""
    client = admin_client
    
    response = client.get('/api/dashboard/win-loss-by-segment/')
    
    assert response.status_code == 200
    data = response.data
    assert data['smb_win'] == 0
    assert data['smb_loss'] == 0
    assert data['enterprise_win'] == 0
    assert data['enterprise_loss'] == 0


@pytest.mark.django_db(transaction=True)
def test_win_loss_by_segment_endpoint_excludes_null_segments(admin_client):
    """Test that leads with segment=None are excluded from counts"""
    client = admin_client
    
    org = Organization.objects.create(name='Test Org')
    contact = Contact.objects.create(org=org, first_name='Test', last_name='User')
    
    # Create lead without segment
    Lead.objects.create(
        org=org,
        contact=contact,
        segment=None,
        stage='won',
        value=5000
    )
    
    # Create lead with segment
    Lead.objects.create(
        org=org,
        contact=contact,
        segment='smb',
        stage='won',
        value=3000
    )
    
    response = client.get('/api/dashboard/win-loss-by-segment/')
    
    assert response.status_code == 200
    data = response.data
    # Only the lead with segment='smb' should be counted
    assert data['smb_win'] == 1
    assert data['smb_loss'] == 0
    assert data['enterprise_win'] == 0
    assert data['enterprise_loss'] == 0


@pytest.mark.django_db(transaction=True)
def test_win_loss_by_segment_endpoint_requires_authentication(api_client):
    """Test that endpoint requires authentication"""
    client = api_client
    # Don't set credentials
    
    response = client.get('/api/dashboard/win-loss-by-segment/')
    
    assert response.status_code == 401  # Unauthorized


@pytest.mark.django_db(transaction=True)
def test_segment_field_exists_on_lead_model():
    """Test that segment field exists on Lead model"""
    org = Organization.objects.create(name='Test Org')
    contact = Contact.objects.create(org=org, first_name='Test', last_name='User')
    
    lead = Lead.objects.create(
        org=org,
        contact=contact,
        segment='smb',
        stage='new',
        value=1000
    )
    
    # Reload from database
    lead.refresh_from_db()
    assert lead.segment == 'smb'
    
    # Test updating segment
    lead.segment = 'enterprise'
    lead.save()
    lead.refresh_from_db()
    assert lead.segment == 'enterprise'
    
    # Test null segment
    lead.segment = None
    lead.save()
    lead.refresh_from_db()
    assert lead.segment is None

