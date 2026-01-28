"""
OTP System Tests

Test Case Categories:
1. OTP Email Sending
2. OTP Verification
3. OTP Frontend Display
4. Reference OTP Testing
5. Rate Limiting
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings

from tests.factories import (
    AdminUserFactory, SalesUserFactory, HREmployeeFactory, UserFactory
)
from django.contrib.auth import get_user_model
from hr.models import HREmployee, OTPVerification
from hr.services import send_otp, verify_otp, send_otp_email
from accounts.models import Role

User = get_user_model()


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def authenticated_admin_client(admin_user, api_client):
    """Create authenticated API client for admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def employee_with_email(db):
    """Create an employee with email for OTP testing."""
    user = UserFactory(
        username='otp_test_user',
        email='otptest@example.com',
        roles=[Role.SALES]
    )
    return HREmployeeFactory(
        user=user,
        email='otptest@example.com',
        name='OTP Test Employee'
    )


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


# ============================================================================
# Test Case 2.1: OTP Email Sending
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestOTPEmailSending:
    """Test Case 2.1: OTP Email Sending"""
    
    @patch('hr.services.send_otp_email')
    def test_2_1_1_send_otp_with_smtp_backend(self, mock_send_email, authenticated_admin_client, employee_with_email):
        """Test Case 2.1.1: Send OTP with SMTP Backend"""
        mock_send_email.return_value = True
        
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/send-phone-otp',
            {'email': employee_with_email.email},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True
        
        # Verify OTP stored in database
        otp_record = OTPVerification.objects.filter(
            employee=employee_with_email,
            email=employee_with_email.email
        ).first()
        assert otp_record is not None
        assert otp_record.otp_code is not None
        assert len(otp_record.otp_code) == 6
    
    @patch('hr.services.send_otp_email')
    def test_2_1_2_send_otp_with_console_backend(self, mock_send_email, authenticated_admin_client, employee_with_email, settings):
        """Test Case 2.1.2: Send OTP with Console Backend (Development)"""
        # Simulate console backend
        settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        settings.DEBUG = True
        mock_send_email.return_value = False
        
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/send-phone-otp',
            {'email': employee_with_email.email},
            format='json'
        )
        
        # Should return error about console backend
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'success' in response.data and response.data['success'] is False
        assert 'console' in response.data.get('error', '').lower() or 'backend' in response.data.get('error', '').lower()
    
    @patch('hr.services.send_otp_email')
    def test_2_1_3_console_backend_returns_false(self, mock_send_email, settings):
        """Test Case 2.1.3: Console Backend Returns False"""
        settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
        
        # Mock the email backend check
        with patch('hr.services.settings.EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'):
            result = send_otp_email('test@example.com', '123456')
            assert result is False
    
    @patch('hr.services.send_mail')
    def test_2_1_4_smtp_error_handling(self, mock_send_mail, authenticated_admin_client, employee_with_email):
        """Test Case 2.1.4: SMTP Error Handling"""
        # Simulate SMTP authentication error
        from smtplib import SMTPAuthenticationError
        mock_send_mail.side_effect = SMTPAuthenticationError(535, "Authentication failed")
        
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/send-phone-otp',
            {'email': employee_with_email.email},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data.get('success') is False
        # Rate limit should NOT be incremented on error
        cache_key = f"otp_rate_limit:{employee_with_email.id}"
        assert cache.get(cache_key) is None
    
    @patch('hr.services.send_otp_email')
    def test_2_1_5_otp_rate_limiting(self, mock_send_email, authenticated_admin_client, employee_with_email):
        """Test Case 2.1.5: OTP Rate Limiting"""
        mock_send_email.return_value = True
        
        # Send first 3 OTPs (should succeed)
        for i in range(3):
            response = authenticated_admin_client.post(
                f'/api/hr/employees/{employee_with_email.id}/send-phone-otp',
                {'email': employee_with_email.email},
                format='json'
            )
            assert response.status_code == status.HTTP_200_OK
        
        # 4th request should be rate limited
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/send-phone-otp',
            {'email': employee_with_email.email},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'rate limit' in response.data.get('error', '').lower() or 'too many' in response.data.get('error', '').lower()
    
    @patch('hr.services.send_otp_email')
    def test_2_1_6_rate_limit_ttl_calculation(self, mock_send_email, authenticated_admin_client, employee_with_email):
        """Test Case 2.1.6: Rate Limit TTL Calculation"""
        mock_send_email.return_value = True
        
        # Send 3 OTPs to hit rate limit
        for i in range(3):
            authenticated_admin_client.post(
                f'/api/hr/employees/{employee_with_email.id}/send-phone-otp',
                {'email': employee_with_email.email},
                format='json'
            )
        
        # 4th request should include time remaining
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/send-phone-otp',
            {'email': employee_with_email.email},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_msg = response.data.get('error', '')
        # Should mention time remaining (minutes or wait)
        assert 'minute' in error_msg.lower() or 'wait' in error_msg.lower() or 'time' in error_msg.lower()


# ============================================================================
# Test Case 2.2: OTP Verification
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestOTPVerification:
    """Test Case 2.2: OTP Verification"""
    
    def test_2_2_1_verify_valid_otp(self, authenticated_admin_client, employee_with_email):
        """Test Case 2.2.1: Verify Valid OTP"""
        # Create an OTP record
        otp_code = '123456'
        otp_record = OTPVerification.objects.create(
            employee=employee_with_email,
            email=employee_with_email.email,
            otp_code=otp_code,
            delivery_method='email',
            purpose='email_verification',
            expires_at=timezone.now() + timedelta(minutes=15),
            is_used=False
        )
        
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/verify-phone-otp',
            {'otp_code': otp_code},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True
        
        # Verify OTP marked as used
        otp_record.refresh_from_db()
        assert otp_record.is_used is True
        
        # Verify employee phone_verified updated
        employee_with_email.refresh_from_db()
        assert employee_with_email.phone_verified is True
    
    def test_2_2_2_verify_expired_otp(self, authenticated_admin_client, employee_with_email):
        """Test Case 2.2.2: Verify Expired OTP"""
        # Create an expired OTP record
        otp_code = '123456'
        OTPVerification.objects.create(
            employee=employee_with_email,
            email=employee_with_email.email,
            otp_code=otp_code,
            delivery_method='email',
            purpose='email_verification',
            expires_at=timezone.now() - timedelta(minutes=1),  # Expired
            is_used=False
        )
        
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/verify-phone-otp',
            {'otp_code': otp_code},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'expired' in response.data.get('error', '').lower()
    
    def test_2_2_3_verify_invalid_otp(self, authenticated_admin_client, employee_with_email):
        """Test Case 2.2.3: Verify Invalid OTP"""
        # Create a valid OTP
        OTPVerification.objects.create(
            employee=employee_with_email,
            email=employee_with_email.email,
            otp_code='123456',
            delivery_method='email',
            purpose='email_verification',
            expires_at=timezone.now() + timedelta(minutes=15),
            is_used=False
        )
        
        # Try to verify with wrong code
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/verify-phone-otp',
            {'otp_code': '999999'},  # Wrong code
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'invalid' in response.data.get('error', '').lower()
    
    def test_2_2_4_verify_used_otp(self, authenticated_admin_client, employee_with_email):
        """Test Case 2.2.4: Verify Used OTP"""
        otp_code = '123456'
        OTPVerification.objects.create(
            employee=employee_with_email,
            email=employee_with_email.email,
            otp_code=otp_code,
            delivery_method='email',
            purpose='email_verification',
            expires_at=timezone.now() + timedelta(minutes=15),
            is_used=True  # Already used
        )
        
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/verify-phone-otp',
            {'otp_code': otp_code},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'used' in response.data.get('error', '').lower()
    
    def test_2_2_5_verify_otp_with_email_parameter(self, authenticated_admin_client, employee_with_email):
        """Test Case 2.2.5: Verify OTP with Email Parameter"""
        otp_code = '123456'
        email = employee_with_email.email
        
        # Create OTP for specific email
        OTPVerification.objects.create(
            employee=employee_with_email,
            email=email,
            otp_code=otp_code,
            delivery_method='email',
            purpose='email_verification',
            expires_at=timezone.now() + timedelta(minutes=15),
            is_used=False
        )
        
        # Verify with email parameter
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/verify-phone-otp',
            {'otp_code': otp_code, 'email': email},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True


# ============================================================================
# Test Case 2.4: Reference OTP Testing
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestReferenceOTP:
    """Test Case 2.4: Reference OTP Testing"""
    
    def test_2_4_1_send_reference_otp(self, authenticated_admin_client, employee_with_email):
        """Test Case 2.4.1: Send Reference OTP"""
        from hr.models import EmployeeReference
        
        # Create a reference
        reference = EmployeeReference.objects.create(
            employee=employee_with_email,
            name='Reference Person',
            email='reference@example.com',
            phone='+1234567890',
            relationship='Former Manager',
            otp_verified=False
        )
        
        with patch('hr.services.send_otp_email', return_value=True):
            response = authenticated_admin_client.post(
                f'/api/hr/employees/{employee_with_email.id}/references/{reference.id}/send-otp',
                format='json'
            )
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data.get('success') is True
    
    def test_2_4_2_verify_reference_otp(self, authenticated_admin_client, employee_with_email):
        """Test Case 2.4.2: Verify Reference OTP"""
        from hr.models import EmployeeReference
        
        # Create a reference
        reference = EmployeeReference.objects.create(
            employee=employee_with_email,
            name='Reference Person',
            email='reference@example.com',
            phone='+1234567890',
            relationship='Former Manager',
            otp_verified=False
        )
        
        # Create OTP for reference
        otp_code = '123456'
        OTPVerification.objects.create(
            employee=employee_with_email,
            email=reference.email,
            otp_code=otp_code,
            delivery_method='email',
            purpose='reference_verification',
            expires_at=timezone.now() + timedelta(minutes=15),
            is_used=False
        )
        
        response = authenticated_admin_client.post(
            f'/api/hr/employees/{employee_with_email.id}/references/{reference.id}/verify-otp',
            {'otp_code': otp_code},
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('success') is True
        
        # Verify reference marked as verified
        reference.refresh_from_db()
        assert reference.otp_verified is True

