"""
Shared fixtures for notification system tests
"""
import uuid
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tests.factories import AdminUserFactory, SalesUserFactory, DesignerUserFactory, FinanceUserFactory

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing"""
    return AdminUserFactory()


@pytest.fixture
def sales_user(db):
    """Create a sales user (employee) for testing"""
    return SalesUserFactory()


@pytest.fixture
def employee_user(db):
    """Alias for sales_user for backward compatibility"""
    return SalesUserFactory()


@pytest.fixture
def designer_user(db):
    """Create a designer user for testing"""
    return DesignerUserFactory()


@pytest.fixture
def finance_user(db):
    """Create a finance user for testing"""
    return FinanceUserFactory()


@pytest.fixture
def api_client():
    """Create an unauthenticated API client"""
    return APIClient()


@pytest.fixture
def authenticated_admin_client(admin_user, api_client):
    """Create authenticated API client for admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def authenticated_employee_client(sales_user, api_client):
    """Create authenticated API client for regular employee."""
    api_client.force_authenticate(user=sales_user)
    return api_client


@pytest.fixture
def authenticated_designer_client(designer_user, api_client):
    """Create authenticated API client for designer."""
    api_client.force_authenticate(user=designer_user)
    return api_client

