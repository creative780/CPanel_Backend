"""
Unit tests for accounts models.
"""
import pytest
from django.contrib.auth import get_user_model
from accounts.models import Role
from tests.factories import UserFactory, AdminUserFactory, SalesUserFactory

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = UserFactory()
        assert user.username is not None
        assert user.email is not None
        assert user.check_password('testpass123')
        assert user.is_active is True
    
    def test_user_role_assignment(self):
        """Test user role assignment."""
        user = SalesUserFactory()
        assert Role.SALES in user.roles
        assert user.has_role(Role.SALES)
        assert not user.has_role(Role.ADMIN)
    
    def test_user_has_role_method(self):
        """Test has_role method."""
        user = UserFactory(roles=[Role.SALES, Role.DESIGNER])
        assert user.has_role(Role.SALES)
        assert user.has_role(Role.DESIGNER)
        assert not user.has_role(Role.ADMIN)
    
    def test_user_is_admin_method(self):
        """Test is_admin method."""
        admin_user = AdminUserFactory()
        regular_user = UserFactory()
        
        assert admin_user.is_admin() is True
        assert regular_user.is_admin() is False
    
    def test_user_password_hashing(self):
        """Test password is hashed correctly."""
        user = UserFactory()
        assert user.password != 'testpass123'
        assert user.check_password('testpass123') is True
        assert user.check_password('wrongpassword') is False
    
    def test_user_multiple_roles(self):
        """Test user with multiple roles."""
        user = UserFactory(roles=[Role.SALES, Role.DESIGNER])
        assert len(user.roles) == 2
        assert Role.SALES in user.roles
        assert Role.DESIGNER in user.roles
    
    def test_user_empty_roles(self):
        """Test user with empty roles."""
        user = UserFactory(roles=[])
        assert user.roles == []
        assert not user.has_role(Role.ADMIN)
        assert not user.is_admin()
    
    def test_user_org_id_field(self):
        """Test org_id field."""
        user = UserFactory(org_id='test_org_123')
        assert user.org_id == 'test_org_123'
    
    def test_user_mfa_fields(self):
        """Test MFA fields."""
        user = UserFactory(
            mfa_phone='+1234567890',
            mfa_email_otp_enabled=True
        )
        assert user.mfa_phone == '+1234567890'
        assert user.mfa_email_otp_enabled is True


@pytest.mark.django_db
@pytest.mark.unit
class TestRoleChoices:
    """Test Role choices."""
    
    def test_role_choices_exist(self):
        """Test all role choices exist."""
        assert Role.ADMIN == 'admin'
        assert Role.USER == 'user'
        assert Role.SALES == 'sales'
        assert Role.DESIGNER == 'designer'
        assert Role.PRODUCTION == 'production'
        assert Role.DELIVERY == 'delivery'
        assert Role.FINANCE == 'finance'
    
    def test_role_choices_list(self):
        """Test role choices list."""
        choices = [choice[0] for choice in Role.choices]
        assert 'admin' in choices
        assert 'user' in choices
        assert 'sales' in choices
        assert 'designer' in choices
        assert 'production' in choices
        assert 'delivery' in choices
        assert 'finance' in choices













































