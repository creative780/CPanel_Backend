"""
Unit tests for accounts serializers.
"""
import pytest
from rest_framework.exceptions import ValidationError
from accounts.serializers import UserSerializer, LoginSerializer, RegisterSerializer
from accounts.models import Role
from tests.factories import UserFactory, AdminUserFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestUserSerializer:
    """Test UserSerializer."""
    
    def test_user_serializer_fields(self):
        """Test UserSerializer includes correct fields."""
        user = UserFactory()
        serializer = UserSerializer(user)
        data = serializer.data
        
        assert 'id' in data
        assert 'username' in data
        assert 'email' in data
        assert 'first_name' in data
        assert 'last_name' in data
        assert 'roles' in data
        assert 'last_login' in data
        assert 'password' not in data  # Password should not be serialized
    
    def test_user_serializer_data(self):
        """Test UserSerializer returns correct data."""
        user = UserFactory(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            roles=[Role.SALES]
        )
        serializer = UserSerializer(user)
        data = serializer.data
        
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert data['first_name'] == 'Test'
        assert data['last_name'] == 'User'
        assert data['roles'] == [Role.SALES]


@pytest.mark.django_db
@pytest.mark.unit
class TestLoginSerializer:
    """Test LoginSerializer."""
    
    def test_login_serializer_valid(self):
        """Test valid login."""
        user = UserFactory(username='testuser', password='testpass123', roles=[Role.SALES])
        serializer = LoginSerializer(data={
            'username': 'testuser',
            'password': 'testpass123',
            'role': Role.SALES
        })
        assert serializer.is_valid() is True
        assert serializer.validated_data['user'] == user
    
    def test_login_serializer_invalid_credentials(self):
        """Test login with invalid credentials."""
        UserFactory(username='testuser', password='testpass123', roles=[Role.SALES])
        serializer = LoginSerializer(data={
            'username': 'testuser',
            'password': 'wrongpassword',
            'role': Role.SALES
        })
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors
    
    def test_login_serializer_invalid_role(self):
        """Test login with invalid role."""
        user = UserFactory(username='testuser', password='testpass123', roles=[Role.SALES])
        serializer = LoginSerializer(data={
            'username': 'testuser',
            'password': 'testpass123',
            'role': Role.ADMIN  # User doesn't have admin role
        })
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors
    
    def test_login_serializer_suspended_user(self):
        """Test login with suspended user."""
        user = UserFactory(username='testuser', password='testpass123', roles=[Role.SALES], is_active=False)
        serializer = LoginSerializer(data={
            'username': 'testuser',
            'password': 'testpass123',
            'role': Role.SALES
        })
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors
    
    def test_login_serializer_nonexistent_user(self):
        """Test login with nonexistent user."""
        serializer = LoginSerializer(data={
            'username': 'nonexistent',
            'password': 'password',
            'role': Role.SALES
        })
        assert serializer.is_valid() is False
        assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
@pytest.mark.unit
class TestRegisterSerializer:
    """Test RegisterSerializer."""
    
    def test_register_serializer_create(self):
        """Test user registration."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'roles': [Role.SALES]
        })
        assert serializer.is_valid() is True
        user = serializer.save()
        
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.check_password('newpass123')
        assert Role.SALES in user.roles
    
    def test_register_serializer_password_not_in_data(self):
        """Test password is not returned in serialized data."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com',
            'roles': [Role.SALES]
        })
        assert serializer.is_valid() is True
        user = serializer.save()
        
        # Password should not be in serialized data
        user_serializer = UserSerializer(user)
        assert 'password' not in user_serializer.data
    
    def test_register_serializer_multiple_roles(self):
        """Test registration with multiple roles."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com',
            'roles': [Role.SALES, Role.DESIGNER]
        })
        assert serializer.is_valid() is True
        user = serializer.save()
        
        assert len(user.roles) == 2
        assert Role.SALES in user.roles
        assert Role.DESIGNER in user.roles
    
    def test_register_serializer_invalid_role(self):
        """Test registration with invalid role."""
        serializer = RegisterSerializer(data={
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com',
            'roles': ['invalid_role']
        })
        assert serializer.is_valid() is False
        assert 'roles' in serializer.errors













































