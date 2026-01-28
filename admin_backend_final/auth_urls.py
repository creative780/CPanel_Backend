from django.urls import path
from .auth_views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    MeView,
    PasswordChangeView,
    RegisterView,
    RequestVerificationEmailView,
    VerifyEmailCodeView,
    csrf,
)

urlpatterns = [
    path("api/csrf/", csrf, name="csrf"),
    path("api/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/me/", MeView.as_view(), name="me"),
    path("api/password-change/", PasswordChangeView.as_view(), name="password_change"),
    path("api/request-verification/", RequestVerificationEmailView.as_view(), name="request_verification"),
    path("api/verify-email/", VerifyEmailCodeView.as_view(), name="verify_email"),
]
