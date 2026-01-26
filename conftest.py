"""
Global pytest fixtures for CRM Backend tests.

This module provides reusable fixtures for:
- Authenticated API clients with different roles
- Test users with various roles
- Test devices and organizations
- Mock external services (Redis, S3, Celery)
- Database transactions
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from monitoring.models import Device, Org
from accounts.models import Role

User = get_user_model()


# ============================================================================
# Test Database Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest-django to use SQLite for tests."""
    # Override DATABASE_URL environment variable to use SQLite for tests
    # This ensures tests run without requiring PostgreSQL
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'


# ============================================================================
# Database and Transaction Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass


@pytest.fixture(autouse=True)
def ensure_db_connection(db):
    """Ensure database connection is open before each test."""
    from django.db import connection
    # Ensure connection is open
    # SQLite connections don't have a 'closed' attribute, so check differently
    if connection.connection is None:
        connection.ensure_connection()
    elif hasattr(connection.connection, 'closed') and connection.connection.closed:
        connection.ensure_connection()
    yield
    # Connection cleanup is handled by pytest-django


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='testpass123',
        roles=[Role.ADMIN],
        is_staff=True,
        is_superuser=True,
        first_name='Admin',
        last_name='User',
    )


@pytest.fixture
def sales_user(db):
    """Create a sales user for testing."""
    return User.objects.create_user(
        username='sales_test',
        email='sales@test.com',
        password='testpass123',
        roles=[Role.SALES],
        first_name='Sales',
        last_name='User',
    )


@pytest.fixture
def designer_user(db):
    """Create a designer user for testing."""
    return User.objects.create_user(
        username='designer_test',
        email='designer@test.com',
        password='testpass123',
        roles=[Role.DESIGNER],
        first_name='Designer',
        last_name='User',
    )


@pytest.fixture
def production_user(db):
    """Create a production user for testing."""
    return User.objects.create_user(
        username='production_test',
        email='production@test.com',
        password='testpass123',
        roles=[Role.PRODUCTION],
        first_name='Production',
        last_name='User',
    )


@pytest.fixture
def delivery_user(db):
    """Create a delivery user for testing."""
    return User.objects.create_user(
        username='delivery_test',
        email='delivery@test.com',
        password='testpass123',
        roles=[Role.DELIVERY],
        first_name='Delivery',
        last_name='User',
    )


@pytest.fixture
def finance_user(db):
    """Create a finance user for testing."""
    return User.objects.create_user(
        username='finance_test',
        email='finance@test.com',
        password='testpass123',
        roles=[Role.FINANCE],
        first_name='Finance',
        last_name='User',
    )


@pytest.fixture
def regular_user(db):
    """Create a regular user (no special roles) for testing."""
    return User.objects.create_user(
        username='user_test',
        email='user@test.com',
        password='testpass123',
        roles=[Role.USER],
        first_name='Regular',
        last_name='User',
    )


@pytest.fixture
def create_user(db):
    """Factory fixture to create users with custom roles."""
    def _create_user(username=None, roles=None, **kwargs):
        if username is None:
            username = f'user_{timezone.now().timestamp()}'
        if roles is None:
            roles = [Role.USER]
        
        return User.objects.create_user(
            username=username,
            password=kwargs.pop('password', 'testpass123'),
            roles=roles,
            email=kwargs.pop('email', f'{username}@test.com'),
            **kwargs
        )
    return _create_user


# ============================================================================
# Device and Organization Fixtures
# ============================================================================

@pytest.fixture
def test_org(db):
    """Create a test organization."""
    return Org.objects.create(
        id='test_org_123',
        name='Test Organization',
        retention_days=30,
    )


@pytest.fixture
def test_device(db, test_org):
    """Create a test device for login requirements."""
    return Device.objects.create(
        id='test-device-123',
        hostname='test-host',
        os='Windows',
        status='ONLINE',
        org=test_org,
        last_heartbeat=timezone.now(),
    )


@pytest.fixture
def create_device(db):
    """Factory fixture to create devices."""
    def _create_device(org=None, device_id=None, **kwargs):
        if org is None:
            org = Org.objects.create(
                id=f'org_{timezone.now().timestamp()}',
                name='Test Org',
            )
        if device_id is None:
            device_id = f'test-device-{timezone.now().timestamp()}'
        
        return Device.objects.create(
            id=device_id,
            org=org,
            hostname=kwargs.pop('hostname', 'test-host'),
            os=kwargs.pop('os', 'Windows'),
            status=kwargs.pop('status', 'ONLINE'),
            last_heartbeat=kwargs.pop('last_heartbeat', timezone.now()),
            **kwargs
        )
    return _create_device


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """Create an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def admin_client(api_client, admin_user, test_device):
    """Create an authenticated API client with admin role."""
    # Admin doesn't need device_id
    response = api_client.post(
        '/api/auth/login',
        {
            'username': admin_user.username,
            'password': 'testpass123',
            'role': Role.ADMIN,
        },
        format='json',
    )
    assert response.status_code == 200, f"Login failed: {response.data if hasattr(response, 'data') else response.content}"
    token = response.data.get('token') or response.data.get('access')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def sales_client(api_client, sales_user, test_device):
    """Create an authenticated API client with sales role."""
    response = api_client.post(
        '/api/auth/login',
        {
            'username': sales_user.username,
            'password': 'testpass123',
            'role': Role.SALES,
        },
        format='json',
        HTTP_X_DEVICE_ID=test_device.id,
    )
    assert response.status_code == 200, f"Login failed: {response.data if hasattr(response, 'data') else response.content}"
    token = response.data.get('token') or response.data.get('access')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def designer_client(api_client, designer_user, test_device):
    """Create an authenticated API client with designer role."""
    response = api_client.post(
        '/api/auth/login',
        {
            'username': designer_user.username,
            'password': 'testpass123',
            'role': Role.DESIGNER,
        },
        format='json',
        HTTP_X_DEVICE_ID=test_device.id,
    )
    assert response.status_code == 200, f"Login failed: {response.data if hasattr(response, 'data') else response.content}"
    token = response.data.get('token') or response.data.get('access')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def production_client(api_client, production_user, test_device):
    """Create an authenticated API client with production role."""
    response = api_client.post(
        '/api/auth/login',
        {
            'username': production_user.username,
            'password': 'testpass123',
            'role': Role.PRODUCTION,
        },
        format='json',
        HTTP_X_DEVICE_ID=test_device.id,
    )
    assert response.status_code == 200, f"Login failed: {response.data if hasattr(response, 'data') else response.content}"
    token = response.data.get('token') or response.data.get('access')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def delivery_client(api_client, delivery_user, test_device):
    """Create an authenticated API client with delivery role."""
    response = api_client.post(
        '/api/auth/login',
        {
            'username': delivery_user.username,
            'password': 'testpass123',
            'role': Role.DELIVERY,
        },
        format='json',
        HTTP_X_DEVICE_ID=test_device.id,
    )
    assert response.status_code == 200, f"Login failed: {response.data if hasattr(response, 'data') else response.content}"
    token = response.data.get('token') or response.data.get('access')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def authenticated_client(api_client, create_user, test_device):
    """Factory fixture to create authenticated clients for any user."""
    def _authenticated_client(user=None, role=None, **kwargs):
        if user is None:
            roles = [role] if role else [Role.USER]
            user = create_user(roles=roles, **kwargs)
        
        # Determine if device_id is needed
        headers = {}
        if not user.is_admin():
            headers['HTTP_X_DEVICE_ID'] = test_device.id
        
        response = api_client.post(
            '/api/auth/login',
            {
                'username': user.username,
                'password': kwargs.get('password', 'testpass123'),
                'role': user.roles[0] if user.roles else Role.USER,
            },
            format='json',
            **headers
        )
        assert response.status_code == 200, f"Login failed: {response.data if hasattr(response, 'data') else response.content}"
        token = response.data.get('token') or response.data.get('access')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return api_client
    return _authenticated_client


# ============================================================================
# Mock External Services
# ============================================================================

@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis connection."""
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None
    mock_redis_client.set.return_value = True
    mock_redis_client.delete.return_value = True
    mock_redis_client.exists.return_value = False
    
    monkeypatch.setattr('django_redis.get_redis_connection', lambda *args, **kwargs: mock_redis_client)
    return mock_redis_client


@pytest.fixture
def mock_s3(monkeypatch):
    """Mock AWS S3 service."""
    mock_s3_client = MagicMock()
    mock_s3_client.upload_fileobj.return_value = None
    mock_s3_client.generate_presigned_url.return_value = 'https://s3.example.com/file.jpg'
    mock_s3_client.delete_object.return_value = {'ResponseMetadata': {'HTTPStatusCode': 204}}
    
    monkeypatch.setattr('boto3.client', lambda *args, **kwargs: mock_s3_client)
    return mock_s3_client


@pytest.fixture
def mock_celery(monkeypatch):
    """Mock Celery tasks."""
    mock_task = MagicMock()
    mock_task.delay = MagicMock(return_value=MagicMock(id='task-123'))
    mock_task.apply_async = MagicMock(return_value=MagicMock(id='task-123'))
    
    def mock_task_decorator(*args, **kwargs):
        def decorator(func):
            func.delay = mock_task.delay
            func.apply_async = mock_task.apply_async
            return func
        return decorator
    
    monkeypatch.setattr('celery.shared_task', mock_task_decorator)
    monkeypatch.setattr('celery.task', mock_task_decorator)
    return mock_task


@pytest.fixture
def mock_websocket(monkeypatch):
    """Mock WebSocket connections."""
    mock_channel_layer = MagicMock()
    mock_channel_layer.send.return_value = None
    mock_channel_layer.group_send.return_value = None
    
    monkeypatch.setattr('channels.layers.get_channel_layer', lambda: mock_channel_layer)
    return mock_channel_layer


# ============================================================================
# JWT Token Fixtures
# ============================================================================

@pytest.fixture
def admin_token(admin_user):
    """Generate JWT token for admin user."""
    refresh = RefreshToken.for_user(admin_user)
    return str(refresh.access_token)


@pytest.fixture
def sales_token(sales_user):
    """Generate JWT token for sales user."""
    refresh = RefreshToken.for_user(sales_user)
    return str(refresh.access_token)


@pytest.fixture
def create_token():
    """Factory fixture to create JWT tokens for any user."""
    def _create_token(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    return _create_token


# ============================================================================
# Helper Functions
# ============================================================================

def authenticate_client(client, user, password='testpass123', device_id=None):
    """
    Helper function to authenticate an API client.
    
    Args:
        client: APIClient instance
        user: User instance
        password: User password
        device_id: Optional device ID (required for non-admin users)
    
    Returns:
        Token string
    """
    headers = {}
    if device_id and not user.is_admin():
        headers['HTTP_X_DEVICE_ID'] = device_id
    
    response = client.post(
        '/api/auth/login',
        {
            'username': user.username,
            'password': password,
            'role': user.roles[0] if user.roles else Role.USER,
        },
        format='json',
        **headers
    )
    assert response.status_code == 200, f"Login failed: {response.data if hasattr(response, 'data') else response.content}"
    token = response.data.get('token') or response.data.get('access')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return token

