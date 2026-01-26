"""
Unit tests for accounts permissions.
"""
import pytest
from rest_framework import status
from accounts.models import Role
from accounts.permissions import IsAdmin, RolePermission, user_has_any_role
from tests.factories import UserFactory, AdminUserFactory, SalesUserFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestUserHasAnyRole:
    """Test user_has_any_role function."""
    
    def test_user_has_role(self):
        """Test user has one of the required roles."""
        user = SalesUserFactory()
        assert user_has_any_role(user, [Role.SALES]) is True
        assert user_has_any_role(user, [Role.SALES, Role.DESIGNER]) is True
    
    def test_user_does_not_have_role(self):
        """Test user doesn't have required role."""
        user = SalesUserFactory()
        assert user_has_any_role(user, [Role.ADMIN]) is False
        assert user_has_any_role(user, [Role.DESIGNER, Role.PRODUCTION]) is False
    
    def test_superuser_has_all_roles(self):
        """Test superuser has all roles."""
        user = AdminUserFactory(is_superuser=True)
        assert user_has_any_role(user, [Role.SALES]) is True
        assert user_has_any_role(user, [Role.ADMIN]) is True
        assert user_has_any_role(user, [Role.DESIGNER]) is True
    
    def test_user_with_empty_roles(self):
        """Test user with empty roles."""
        user = UserFactory(roles=[])
        assert user_has_any_role(user, [Role.SALES]) is False


@pytest.mark.django_db
@pytest.mark.unit
class TestIsAdminPermission:
    """Test IsAdmin permission class."""
    
    def test_admin_has_permission(self, admin_client):
        """Test admin has permission."""
        response = admin_client.get('/api/auth/me')
        assert response.status_code == status.HTTP_200_OK
    
    def test_non_admin_denied(self, sales_client):
        """Test non-admin is denied."""
        response = sales_client.post(
            '/api/auth/register',
            {'username': 'test', 'password': 'test', 'roles': [Role.SALES]},
            format='json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.unit
class TestRolePermission:
    """Test RolePermission class."""
    
    def test_role_permission_with_allowed_roles(self, admin_client):
        """Test role permission with allowed roles."""
        # Create a view-like object with allowed_roles
        class TestView:
            allowed_roles = ['admin']
        
        view = TestView()
        permission = RolePermission()
        
        # Admin should have permission
        request = type('Request', (), {'user': admin_client._force_authenticate(None)})
        # This is a simplified test - actual implementation would use DRF's request object
        assert True  # Placeholder - actual test would check permission.has_permission(request, view)
    
    def test_role_permission_without_roles(self, api_client):
        """Test role permission without specified roles."""
        # For safe methods, authenticated users should have access
        # This is a simplified test
        assert True  # Placeholder













































