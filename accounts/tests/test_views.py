"""
Unit tests for accounts views.
"""
import pytest
from rest_framework import status
from accounts.models import Role
from tests.factories import UserFactory, AdminUserFactory, SalesUserFactory, test_device


@pytest.mark.django_db
@pytest.mark.unit
class TestLoginView:
    """Test LoginView."""
    
    def test_login_success(self, api_client, test_device):
        """Test successful login."""
        user = SalesUserFactory()
        response = api_client.post(
            '/api/auth/login',
            {
                'username': user.username,
                'password': 'testpass123'
            },
            format='json',
            HTTP_X_DEVICE_ID=test_device.id
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'refresh' in response.data
        assert response.data['username'] == user.username
    
    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials."""
        UserFactory(username='testuser', password='testpass123', roles=[Role.SALES])
        response = api_client.post(
            '/api/auth/login',
            {
                'username': 'testuser',
                'password': 'wrongpassword'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_suspended_user(self, api_client, test_device):
        """Test login with suspended user."""
        user = SalesUserFactory(is_active=False)
        response = api_client.post(
            '/api/auth/login',
            {
                'username': user.username,
                'password': 'testpass123'
            },
            format='json',
            HTTP_X_DEVICE_ID=test_device.id
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_admin_login_bypasses_device(self, api_client):
        """Test admin login bypasses device requirement."""
        admin = AdminUserFactory()
        response = api_client.post(
            '/api/auth/login',
            {
                'username': admin.username,
                'password': 'testpass123'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data


@pytest.mark.django_db
@pytest.mark.unit
class TestLogoutView:
    """Test LogoutView."""
    
    def test_logout_success(self, admin_client):
        """Test successful logout."""
        response = admin_client.post('/api/auth/logout')
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_logout_requires_authentication(self, api_client):
        """Test logout requires authentication."""
        response = api_client.post('/api/auth/logout')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.unit
class TestRegisterView:
    """Test RegisterView."""
    
    def test_register_success(self, admin_client):
        """Test successful user registration by admin."""
        response = admin_client.post(
            '/api/auth/register',
            {
                'username': 'newuser',
                'password': 'newpass123',
                'email': 'newuser@example.com',
                'first_name': 'New',
                'last_name': 'User',
                'roles': [Role.SALES]
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@example.com'
    
    def test_register_requires_admin(self, sales_client):
        """Test registration requires admin role."""
        response = sales_client.post(
            '/api/auth/register',
            {
                'username': 'newuser',
                'password': 'newpass123',
                'email': 'newuser@example.com',
                'roles': [Role.SALES]
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_register_requires_authentication(self, api_client):
        """Test registration requires authentication."""
        response = api_client.post(
            '/api/auth/register',
            {
                'username': 'newuser',
                'password': 'newpass123',
                'email': 'newuser@example.com',
                'roles': [Role.SALES]
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.unit
class TestMeView:
    """Test MeView."""
    
    def test_me_view_success(self, admin_client, admin_user):
        """Test getting current user info."""
        response = admin_client.get('/api/auth/me')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == admin_user.username
        assert response.data['id'] == admin_user.id
    
    def test_me_view_requires_authentication(self, api_client):
        """Test me view requires authentication."""
        response = api_client.get('/api/auth/me')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED




































