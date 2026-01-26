"""
Helper functions for tests.
"""
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from accounts.models import Role

User = get_user_model()


def create_authenticated_client(user=None, role=None, password='testpass123'):
    """
    Helper function to create an authenticated API client.
    
    Args:
        user: User instance (if None, creates a new user)
        role: Role for the user (if user is None)
        password: Password for authentication
    
    Returns:
        Authenticated APIClient
    """
    if user is None:
        if role is None:
            role = Role.USER
        user = User.objects.create_user(
            username=f'test_{role}_{User.objects.count()}',
            password=password,
            roles=[role]
        )
    
    client = APIClient()
    response = client.post(
        '/api/auth/login',
        {
            'username': user.username,
            'password': password,
            'role': user.roles[0] if user.roles else Role.USER
        },
        format='json'
    )
    
    if response.status_code == 200:
        token = response.data.get('token') or response.data.get('access')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    return client


def assert_response_status(response, expected_status):
    """
    Assert response status with helpful error message.
    
    Args:
        response: DRF Response object
        expected_status: Expected status code
    """
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"Response: {response.data if hasattr(response, 'data') else response.content}"
    )


def assert_response_contains(response, key, value=None):
    """
    Assert response contains a key (and optionally a value).
    
    Args:
        response: DRF Response object
        key: Key to check for
        value: Optional value to check
    """
    assert hasattr(response, 'data'), "Response has no data attribute"
    assert key in response.data, f"Response does not contain key '{key}'. Keys: {list(response.data.keys())}"
    
    if value is not None:
        assert response.data[key] == value, (
            f"Expected {key} to be {value}, got {response.data[key]}"
        )













































