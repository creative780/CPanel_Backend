import os

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_csrf_endpoint_sets_cookie(api_client):
  """
  /api/csrf/ should return 200 and set a csrftoken cookie.
  """
  url = reverse("csrf")
  resp = api_client.get(url)
  assert resp.status_code == status.HTTP_200_OK
  assert "csrfToken" in resp.json()
  # Cookie is set on the response object
  assert "csrftoken" in resp.cookies


@pytest.mark.django_db
def test_jwt_token_obtain_pair_success(api_client, user):
  """
  /api/token/ should issue access & refresh tokens for valid credentials.
  """
  # Get CSRF token first (required by csrf_protect decorator)
  csrf_url = reverse("csrf")
  csrf_resp = api_client.get(csrf_url)
  assert csrf_resp.status_code == status.HTTP_200_OK
  csrf_token = csrf_resp.json().get("csrfToken")
  
  url = reverse("token_obtain_pair")
  resp = api_client.post(
    url,
    {"username": user.email or user.username, "password": "testpassword123"},
    format="json",
    HTTP_X_CSRFTOKEN=csrf_token,
  )
  assert resp.status_code == status.HTTP_200_OK, f"Expected 200, got {resp.status_code}: {resp.data if hasattr(resp, 'data') else resp.content}"
  body = resp.json()
  assert "access" in body
  # Refresh token is in cookie, not response body (CookieTokenObtainPairView behavior)
  assert "refresh_token" in resp.cookies or "refresh" in body


@pytest.mark.django_db
def test_jwt_token_obtain_pair_invalid_credentials(api_client, user):
  """
  /api/token/ should reject invalid credentials.
  """
  # Get CSRF token first (required by csrf_protect decorator)
  csrf_url = reverse("csrf")
  csrf_resp = api_client.get(csrf_url)
  csrf_token = csrf_resp.json().get("csrfToken")
  
  url = reverse("token_obtain_pair")
  resp = api_client.post(
    url,
    {"username": user.email or user.username, "password": "wrong-password"},
    format="json",
    HTTP_X_CSRFTOKEN=csrf_token,
  )
  assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_frontend_only_permission_blocks_missing_header(client):
  """
  Endpoints protected by FrontendOnlyPermission should reject requests
  when X-Frontend-Key is missing or incorrect (if FRONTEND_KEY is set).
  We use show-product as a representative endpoint.
  """
  os.environ["FRONTEND_KEY"] = "test-frontend-key"
  from admin_backend_final.permissions import FRONTEND_KEY as CONFIGURED_KEY

  # Ensure the permission is actually configured in this environment
  assert CONFIGURED_KEY == "test-frontend-key"

  url = reverse("show-product")
  # No header -> should be forbidden or unauthorized
  resp = client.get(url)
  assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_frontend_only_permission_allows_with_header(api_client):
  """
  Same endpoint should succeed (or at least not 401/403) when header is present.
  """
  url = reverse("show-product")
  resp = api_client.get(url)
  # We don't assert on 200 specifically because filters may require params,
  # but we do ensure it's not blocked by auth/permission.
  assert resp.status_code not in (
    status.HTTP_401_UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN,
  )


