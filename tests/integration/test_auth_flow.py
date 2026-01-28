"""
Integration tests for authentication flow.
"""
import pytest
from rest_framework import status
from accounts.models import Role
from tests.factories import UserFactory, AdminUserFactory, SalesUserFactory


@pytest.mark.django_db
@pytest.mark.integration
class TestAuthFlow:
    """Test authentication flow."""
    
    def test_login_logout_flow(self, api_client, test_device):
        """Test complete login and logout flow."""
        user = SalesUserFactory()
        
        # Login
        response = api_client.post(
            '/api/auth/login',
            {
                'username': user.username,
                'password': 'testpass123',
                'role': Role.SALES
            },
            format='json',
            HTTP_X_DEVICE_ID=test_device.id
        )
        
        assert response.status_code == status.HTTP_200_OK
        token = response.data['token']
        
        # Use token to access protected endpoint
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get('/api/auth/me')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        
        # Logout
        response = api_client.post('/api/auth/logout')
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_token_refresh(self, api_client, test_device):
        """Test token refresh flow."""
        user = SalesUserFactory()
        
        # Login
        response = api_client.post(
            '/api/auth/login',
            {
                'username': user.username,
                'password': 'testpass123',
                'role': Role.SALES
            },
            format='json',
            HTTP_X_DEVICE_ID=test_device.id
        )
        
        assert response.status_code == status.HTTP_200_OK
        refresh_token = response.data['refresh']
        
        # Refresh token (if endpoint exists)
        # This would require a refresh endpoint implementation
        # For now, just verify we got a refresh token
        assert refresh_token is not None
    
    def test_role_based_access(self, api_client, test_device):
        """Test role-based access control."""
        sales_user = SalesUserFactory()
        admin_user = AdminUserFactory()
        
        # Sales user login
        response = api_client.post(
            '/api/auth/login',
            {
                'username': sales_user.username,
                'password': 'testpass123',
                'role': Role.SALES
            },
            format='json',
            HTTP_X_DEVICE_ID=test_device.id
        )
        sales_token = response.data['token']
        
        # Sales user cannot register (admin only)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {sales_token}')
        response = api_client.post(
            '/api/auth/register',
            {
                'username': 'newuser',
                'password': 'pass',
                'roles': [Role.SALES]
            },
            format='json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Admin can register
        response = api_client.post(
            '/api/auth/login',
            {
                'username': admin_user.username,
                'password': 'testpass123',
                'role': Role.ADMIN
            },
            format='json'
        )
        admin_token = response.data['token']
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.post(
            '/api/auth/register',
            {
                'username': 'newuser',
                'password': 'newpass123',
                'email': 'new@example.com',
                'roles': [Role.SALES]
            },
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED













































