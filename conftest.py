import os

import pytest
from django.conf import settings
from django.test import Client
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


# Ensure a deterministic FRONTEND_KEY for tests before importing permission module
os.environ.setdefault("FRONTEND_KEY", "test-frontend-key")


@pytest.fixture
def django_client() -> Client:
    """Basic Django test client."""
    return Client()


@pytest.fixture
def api_client() -> APIClient:
    """
    DRF APIClient that automatically sends the X-Frontend-Key header
    expected by FrontendOnlyPermission.
    """
    client = APIClient()
    key = os.environ.get("FRONTEND_KEY", "").strip()
    if key:
        client.defaults["HTTP_X_FRONTEND_KEY"] = key
    return client


@pytest.fixture
def user(db):
    """Regular authenticated user."""
    User = get_user_model()
    u = User.objects.create_user(
        username="user@example.com",
        email="user@example.com",
        password="testpassword123",
    )
    return u


@pytest.fixture
def admin_user(db):
    """Admin/superuser for protected endpoints."""
    User = get_user_model()
    admin = User.objects.create_superuser(
        username="admin@example.com",
        email="admin@example.com",
        password="adminpassword123",
    )
    return admin


@pytest.fixture
def auth_api_client(api_client, user):
    """
    APIClient already authenticated as a regular user via JWT.
    Uses the same login flow as the frontend (CookieTokenObtainPairView).
    """
    from django.urls import reverse

    login_url = reverse("token_obtain_pair")
    res = api_client.post(
        login_url,
        {"username": user.email or user.username, "password": "testpassword123"},
        format="json",
    )
    assert res.status_code == 200, f"Login failed in fixture: {res.status_code} {res.data}"
    access = res.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api_client


@pytest.fixture(autouse=True)
def _configure_settings_for_tests(settings):
    """
    Common test-time settings:
    - Use faster password hasher
    - Ensure DEBUG is True for clearer errors
    """
    settings.DEBUG = True
    settings.PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
    return settings



