"""
Services for HR employee verification, OTP, and behavior index calculation
"""
import random
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.cache import cache
from .models import HREmployee, EmployeeBankDetails, EmployeeExemption, EmployeeVerification, OTPVerification

logger = logging.getLogger(__name__)


def validate_email_configuration() -> dict:
    """
    Validate email backend configuration
    Returns dict with validation status and details
    """
    email_backend = getattr(settings, 'EMAIL_BACKEND', '')
    email_host = getattr(settings, 'EMAIL_HOST', '')
    email_port = getattr(settings, 'EMAIL_PORT', 587)
    email_user = getattr(settings, 'EMAIL_HOST_USER', '')
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    email_use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
    email_use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
    debug = getattr(settings, 'DEBUG', False)
    
    is_console = 'console' in email_backend.lower()
    is_smtp = 'smtp' in email_backend.lower()
    
    validation = {
        'backend': email_backend,
        'is_console': is_console,
        'is_smtp': is_smtp,
        'debug_mode': debug,
        'host_configured': bool(email_host and email_host != 'localhost'),
        'user_configured': bool(email_user),
        'password_configured': bool(email_password),
        'port': email_port,
        'use_tls': email_use_tls,
        'use_ssl': email_use_ssl,
        'valid': False,
        'warnings': [],
        'errors': []
    }
    
    # Check console backend
    if is_console:
        if debug:
            validation['warnings'].append('Using console backend in DEBUG mode - emails will only appear in console')
            validation['valid'] = True
        else:
            validation['errors'].append('Console backend should only be used in DEBUG mode')
            validation['valid'] = False
    
    # Check SMTP configuration
    elif is_smtp:
        if not email_host or email_host == 'localhost':
            validation['errors'].append('EMAIL_HOST is not configured or set to localhost')
        if not email_user:
            validation['errors'].append('EMAIL_HOST_USER is not configured')
        if not email_password:
            validation['errors'].append('EMAIL_HOST_PASSWORD is not configured')
        
        if not validation['errors']:
            validation['valid'] = True
        else:
            validation['valid'] = False
    
    # Unknown backend
    else:
        validation['errors'].append(f'Unknown email backend: {email_backend}')
        validation['valid'] = False
    
    return validation


def generate_otp() -> str:
    """Generate a 6-digit OTP code"""
    return f"{random.randint(0, 999999):06d}"


def send_otp_email(email: str, otp_code: str, purpose: str = 'verification') -> bool:
    """
    Send OTP via email using Django email backend with Gmail SMTP support
    Handles both console backend (for development) and SMTP backend (for production)
    Raises exceptions with detailed error messages for better error handling
    """
    try:
        # Validate email format
        validate_email(email)
    except DjangoValidationError as e:
        error_msg = f"Invalid email format: {email} - {e}"
        logger.error(f"[Email] {error_msg}")
        raise ValueError(error_msg)
    
    try:
        subject = f"Your {purpose.replace('_', ' ').title()} Code"
        message = f"Your verification code is: {otp_code}\n\nThis code will expire in 10 minutes."
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        
        # Check email backend configuration
        email_backend = getattr(settings, 'EMAIL_BACKEND', '')
        email_host = getattr(settings, 'EMAIL_HOST', '')
        email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', from_email)
        
        # Log email configuration status (without sensitive data)
        logger.debug(f"[Email] Backend: {email_backend}, Host: {email_host}, User: {email_user[:3] + '***' if email_user else 'Not set'}")
        
        # Gmail-specific validation
        is_gmail = 'gmail.com' in email_host.lower() or 'gmail.com' in (email_user or '').lower()
        if is_gmail:
            # Verify Gmail host is correct
            if 'smtp.gmail.com' not in email_host.lower():
                error_msg = f"Gmail requires EMAIL_HOST=smtp.gmail.com, but got {email_host}. Please update your configuration."
                logger.error(f"[Email] {error_msg}")
                raise ValueError(error_msg)
            
            # Check if FROM email matches Gmail account (Gmail requirement)
            if email_user and from_email.lower() != email_user.lower():
                error_msg = f"Gmail requires DEFAULT_FROM_EMAIL to match EMAIL_HOST_USER. Current: FROM={from_email}, USER={email_user}. Please set EMAIL_FROM={email_user} or ensure DEFAULT_FROM_EMAIL matches."
                logger.error(f"[Email] {error_msg}")
                raise ValueError(error_msg)
            
            # Validate App Password format (Gmail App Passwords are 16 characters, no spaces)
            if email_password:
                # Remove spaces (App Passwords might have spaces when copied)
                password_clean = email_password.replace(' ', '')
                if len(password_clean) != 16 or not password_clean.isalnum():
                    error_msg = "Gmail App Password should be 16 characters (alphanumeric). If you're using your regular Gmail password, please generate an App Password from https://myaccount.google.com/apppasswords"
                    logger.warning(f"[Email] {error_msg}")
                    # Don't fail here, just warn - some passwords might work
        
        # For console backend in DEBUG mode
        if 'console' in email_backend.lower():
            if settings.DEBUG:
                send_mail(subject, message, from_email, [email], fail_silently=False)
                logger.info(f"[Email] OTP sent to {email} (console backend - DEBUG mode)")
                logger.info(f"[Email] OTP code for {email}: {otp_code} (check console output)")
                return True
            else:
                error_msg = "Console email backend is only available in DEBUG mode. Configure SMTP backend for production."
                logger.error(f"[Email] {error_msg}")
                raise ValueError(error_msg)
        
        # For SMTP backend (production)
        # Validate SMTP configuration
        if not email_host or email_host == 'localhost':
            error_msg = "EMAIL_HOST is not configured. Please set EMAIL_HOST in your settings."
            logger.error(f"[Email] {error_msg}")
            raise ValueError(error_msg)
        
        if not email_user:
            error_msg = "EMAIL_HOST_USER is not configured. Please set EMAIL_HOST_USER in your .env file and restart the Django server."
            logger.error(f"[Email] {error_msg}")
            logger.error(f"[Email] Current EMAIL_HOST_USER value: '{email_user}' (empty)")
            logger.error(f"[Email] Make sure .env file exists in CRM_BACKEND/ directory and contains EMAIL_HOST_USER=your-email@gmail.com")
            logger.error(f"[Email] After updating .env, restart Django server for changes to take effect.")
            raise ValueError(error_msg)
        
        if not email_password:
            error_msg = "EMAIL_HOST_PASSWORD is not configured. Please set EMAIL_HOST_PASSWORD in your .env file and restart the Django server."
            logger.error(f"[Email] {error_msg}")
            logger.error(f"[Email] Current EMAIL_HOST_PASSWORD value: '{'*' * min(len(email_password), 10) if email_password else '(empty)'}'")
            logger.error(f"[Email] Make sure .env file exists in CRM_BACKEND/ directory and contains EMAIL_HOST_PASSWORD=your-app-password")
            logger.error(f"[Email] After updating .env, restart Django server for changes to take effect.")
            raise ValueError(error_msg)
        
        # Gmail-specific validation
        is_gmail = 'gmail.com' in email_host.lower() or 'gmail.com' in (email_user or '').lower()
        if is_gmail:
            # Verify Gmail host is correct
            if 'smtp.gmail.com' not in email_host.lower():
                error_msg = f"Gmail requires EMAIL_HOST=smtp.gmail.com, but got {email_host}. Please update your configuration."
                logger.error(f"[Email] {error_msg}")
                raise ValueError(error_msg)
            
            # Check if FROM email matches Gmail account (Gmail requirement)
            if email_user and from_email.lower() != email_user.lower():
                error_msg = f"Gmail requires DEFAULT_FROM_EMAIL to match EMAIL_HOST_USER. Current: FROM={from_email}, USER={email_user}. Please set EMAIL_FROM={email_user} in your .env file."
                logger.error(f"[Email] {error_msg}")
                raise ValueError(error_msg)
            
            # Validate App Password format (Gmail App Passwords are 16 characters, no spaces)
            if email_password:
                # Remove spaces and dashes (App Passwords might have spaces when copied)
                password_clean = email_password.replace(' ', '').replace('-', '')
                if len(password_clean) != 16:
                    error_msg = f"Gmail App Password must be exactly 16 characters (got: {len(password_clean)}). You're likely using your regular Gmail password instead of an App Password. Generate an App Password at https://myaccount.google.com/apppasswords (requires 2FA to be enabled)."
                    logger.error(f"[Email] {error_msg}")
                    raise ValueError(error_msg)
                # Validate it's alphanumeric (App Passwords are alphanumeric)
                if not password_clean.isalnum():
                    error_msg = f"Gmail App Password should contain only letters and numbers. If you're using your regular password, please generate an App Password at https://myaccount.google.com/apppasswords"
                    logger.error(f"[Email] {error_msg}")
                    raise ValueError(error_msg)
        
        # Use fail_silently=False to catch and log actual errors
        try:
            result = send_mail(subject, message, from_email, [email], fail_silently=False)
            if result:
                logger.info(f"[Email] OTP sent successfully to {email}")
                if settings.DEBUG:
                    logger.debug(f"[Email] OTP code for {email}: {otp_code}")
                return True
            else:
                # Email backend returned False - likely configuration issue
                error_msg = "Email backend returned False. Check EMAIL_* settings and SMTP server configuration."
                logger.error(f"[Email] Failed to send OTP email to {email} - {error_msg}")
                raise ValueError(error_msg)
        except Exception as smtp_error:
            # Catch SMTP errors explicitly and provide detailed error messages
            error_str = str(smtp_error).lower()
            is_gmail = 'gmail.com' in email_host.lower() or 'gmail.com' in (email_user or '').lower()
            
            if 'authentication' in error_str or 'credentials' in error_str or '535' in error_str:
                if is_gmail:
                    error_msg = f"Gmail authentication failed: {smtp_error}. For Gmail, you must use an App Password (not your regular password). Generate one at https://myaccount.google.com/apppasswords. Ensure 2FA is enabled on your Google account first."
                else:
                    error_msg = f"Email authentication failed: {smtp_error}. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD settings."
                logger.error(f"[Email] {error_msg}")
                raise ValueError(error_msg)
            elif 'connection' in error_str or 'timeout' in error_str or 'refused' in error_str:
                error_msg = f"Email connection failed: {smtp_error}. Check EMAIL_HOST and EMAIL_PORT settings."
                logger.error(f"[Email] {error_msg}")
                raise ValueError(error_msg)
            elif 'ssl' in error_str or 'tls' in error_str:
                error_msg = f"Email SSL/TLS error: {smtp_error}. Check EMAIL_USE_TLS and EMAIL_USE_SSL settings."
                logger.error(f"[Email] {error_msg}")
                raise ValueError(error_msg)
            else:
                error_msg = f"SMTP error sending OTP to {email}: {smtp_error}"
                logger.error(f"[Email] {error_msg}", exc_info=True)
                raise ValueError(error_msg)
            
    except ValueError:
        # Re-raise ValueError (our custom errors)
        raise
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Unexpected error sending OTP email to {email}: {e}"
        logger.error(f"[Email] {error_msg}", exc_info=True)
        raise ValueError(error_msg)


def send_otp(employee: HREmployee, email: str = None, purpose: str = 'email_verification') -> dict:
    """
    Send OTP via email only
    Returns dict with otp_verification_id, and success status
    Includes rate limiting: Phone OTP 3/hour, Reference OTP 2/hour
    """
    # Rate limiting based on purpose type
    # Phone OTP: 3 per hour, Reference OTP: 2 per hour
    if purpose == 'email_verification' or purpose == 'phone_verification':
        max_requests = 3
        time_window = 3600  # 1 hour in seconds
        error_message = 'Too many phone OTP requests. Please wait 1 hour before requesting again.'
    elif purpose == 'reference_verification':
        max_requests = 2
        time_window = 3600  # 1 hour in seconds
        error_message = 'Too many reference OTP requests. Please wait 1 hour before requesting again.'
    else:
        # Default for other purposes
        max_requests = 3
        time_window = 3600
        error_message = 'Too many OTP requests. Please wait 1 hour before requesting again.'
    
    cache_key = f'otp_rate_limit_{employee.id}_{purpose}'
    otp_count = cache.get(cache_key, 0)
    if otp_count >= max_requests:
        return {
            'success': False,
            'error': error_message
        }
    
    # Get email address
    if not email:
        email = employee.email
    if not email:
        return {'success': False, 'error': 'Email required for OTP delivery'}
    
    # Validate email format
    try:
        validate_email(email)
    except DjangoValidationError as e:
        return {'success': False, 'error': f'Invalid email format: {str(e)}'}
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    # Send OTP via email
    try:
        sent = send_otp_email(email, otp_code, purpose)
        if not sent:
            return {'success': False, 'error': 'Failed to send OTP. Please check email configuration or try again later.'}
    except ValueError as e:
        # Catch ValueError from send_otp_email with detailed error message
        return {'success': False, 'error': str(e)}
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error in send_otp: {e}", exc_info=True)
        return {'success': False, 'error': f'Failed to send OTP: {str(e)}'}
    
    # Store OTP in database
    otp_verification = OTPVerification.objects.create(
        employee=employee,
        phone_number='',  # Empty for email-only
        email=email,
        otp_code=otp_code,
        delivery_method='email',
        purpose=purpose,
        expires_at=expires_at
    )
    
    # Update rate limit counter
    cache.set(cache_key, otp_count + 1, time_window)  # 1 hour = 3600 seconds
    
    # Build response - only include OTP code in DEBUG mode for security
    response = {
        'success': True,
        'otp_verification_id': otp_verification.id,
        'expires_at': expires_at.isoformat()
    }
    
    # Only include OTP code in DEBUG mode for testing
    if settings.DEBUG:
        response['otp_code'] = otp_code
    
    return response


def verify_otp(employee: HREmployee, otp_code: str, purpose: str = 'email_verification') -> dict:
    """
    Verify OTP code
    Returns dict with success status and message
    """
    # Find the most recent unused OTP for this employee and purpose
    otp_verification = OTPVerification.objects.filter(
        employee=employee,
        purpose=purpose,
        is_used=False
    ).order_by('-sent_at').first()
    
    if not otp_verification:
        return {'success': False, 'error': 'No OTP found. Please request a new OTP.'}
    
    if otp_verification.is_expired():
        return {'success': False, 'error': 'OTP has expired after 10 minutes. Please request a new OTP.'}
    
    if otp_verification.otp_code != otp_code:
        return {'success': False, 'error': 'Invalid OTP code.'}
    
    # Mark as used and verified
    otp_verification.is_used = True
    otp_verification.verified_at = timezone.now()
    otp_verification.save()
    
    # Update verification status based on purpose
    verification, _ = EmployeeVerification.objects.get_or_create(employee=employee)
    
    if purpose == 'email_verification' or purpose == 'phone_verification':
        employee.phone_verified = True
        employee.phone_verified_at = timezone.now()
        employee.save(update_fields=['phone_verified', 'phone_verified_at'])
        verification.phone_verified = True
        verification.save()
        logger.info(f"Phone verified for employee {employee.id} - {employee.name}")
    elif purpose == 'reference_verification':
        # Reference verification is handled in the view (sets otp_verified on reference)
        # This will be handled by the signal
        pass
    
    # Check if salary should be activated (Phone + Reference + Bank verified)
    check_and_activate_salary(employee)
    
    return {'success': True, 'message': 'OTP verified successfully'}


def check_and_activate_salary(employee: HREmployee) -> bool:
    """
    Check if salary should be activated when Phone + Reference are verified
    and bank is verified (or exempted).
    Creates log entry: "Verified on [Date/Time] via OTP | Verified by HR System"
    """
    from .models import SalaryStatusLog
    
    verification, _ = EmployeeVerification.objects.get_or_create(employee=employee)
    
    # Check if phone and reference are verified
    phone_verified = verification.phone_verified or employee.phone_verified
    reference_verified = verification.reference_verified
    
    # Check if bank is verified or exempted
    bank_verified = check_bank_verification_status(employee)
    
    # Activate salary if all conditions met
    if phone_verified and reference_verified and bank_verified:
        if employee.salary_status == 'ON_HOLD':
            employee.salary_status = 'ACTIVE'
            employee.save(update_fields=['salary_status'])
            
            # Create log entry with required format
            log_message = f"Verified on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} via OTP | Verified by HR System"
            SalaryStatusLog.objects.create(
                employee=employee,
                old_status='ON_HOLD',
                new_status='ACTIVE',
                reason=log_message,
                changed_by=None  # System change
            )
            
            logger.info(f"Salary activated for employee {employee.id} - {employee.name} (Phone + Reference + Bank verified)")
            return True
    
    return False


def check_bank_verification_status(employee: HREmployee) -> bool:
    """
    Check if bank is verified or employee is exempted
    Returns True if bank is verified OR employee is exempted, False otherwise
    """
    try:
        bank_details = employee.bank_details
        if bank_details.status == 'verified':
            return True
        
        # Check for exemption
        try:
            exemption = employee.exemption
            if exemption.bank_exempted:
                return True
        except EmployeeExemption.DoesNotExist:
            pass
        
        return False
    except EmployeeBankDetails.DoesNotExist:
        return False


def enforce_salary_hold(employee: HREmployee) -> bool:
    """
    Set salary_status to ON_HOLD if bank not verified
    Returns True if hold was enforced, False if already on hold or verified
    """
    if not check_bank_verification_status(employee):
        if employee.salary_status != 'ON_HOLD':
            employee.salary_status = 'ON_HOLD'
            employee.save(update_fields=['salary_status'])
            logger.info(f"Salary hold enforced for employee {employee.id} - {employee.name}")
            return True
    return False


def request_bank_verification(employee: HREmployee) -> dict:
    """Employee requests bank verification"""
    try:
        bank_details = employee.bank_details
        
        # Validate that bank details are complete
        if not bank_details.bank_name or not bank_details.account_holder_name or not bank_details.iban:
            return {'success': False, 'error': 'Bank details are incomplete. Please fill in all required fields.'}
        
        # Validate that proof document exists
        if not bank_details.proof_document:
            return {'success': False, 'error': 'Proof document is required. Please upload a bank proof document.'}
        
        # Check if already verified
        if bank_details.status == 'verified':
            return {'success': False, 'error': 'Bank details are already verified.'}
        
        # Update status to verification_requested
        bank_details.status = 'verification_requested'
        bank_details.verification_requested_at = timezone.now()
        bank_details.save()
        
        logger.info(f"Bank verification requested by employee {employee.id} - {employee.name}")
        return {'success': True, 'message': 'Verification request submitted successfully. Admin will review your request.'}
    except EmployeeBankDetails.DoesNotExist:
        return {'success': False, 'error': 'Bank details not found. Please add your bank details first.'}


def verify_bank_details(employee: HREmployee, verifier) -> bool:
    """Admin verification of bank details"""
    try:
        bank_details = employee.bank_details
        
        # Allow verification from 'verification_requested' or 'pending' status
        if bank_details.status not in ['verification_requested', 'pending']:
            logger.warning(f"Cannot verify bank details for employee {employee.id} - current status is {bank_details.status}")
            return False
        
        bank_details.status = 'verified'
        bank_details.verified_by = verifier
        bank_details.verified_at = timezone.now()
        bank_details.save()
        
        # Update verification status
        verification, _ = EmployeeVerification.objects.get_or_create(employee=employee)
        verification.bank_verified = True
        verification.save()
        
        # Check if salary should be activated (Phone + Reference + Bank verified)
        check_and_activate_salary(employee)
        
        logger.info(f"Bank details verified for employee {employee.id} - {employee.name} by {verifier.username}")
        return True
    except EmployeeBankDetails.DoesNotExist:
        return False


def reject_bank_verification(employee: HREmployee, reason: str, rejected_by) -> bool:
    """Admin rejects bank verification request"""
    try:
        bank_details = employee.bank_details
        
        # Allow rejection if status is 'verification_requested' or 'pending'
        if bank_details.status not in ['verification_requested', 'pending']:
            logger.warning(f"Cannot reject bank verification for employee {employee.id} - current status is {bank_details.status}")
            return False
        
        bank_details.status = 'rejected'
        bank_details.rejection_reason = reason
        bank_details.rejected_by = rejected_by
        bank_details.rejected_at = timezone.now()
        bank_details.save()
        
        # Update verification status
        verification, _ = EmployeeVerification.objects.get_or_create(employee=employee)
        verification.bank_verified = False
        verification.save()
        
        logger.info(f"Bank verification rejected for employee {employee.id} - {employee.name} by {rejected_by.username}")
        return True
    except EmployeeBankDetails.DoesNotExist:
        return False


def grant_bank_exemption(employee: HREmployee, reason: str, granted_by) -> bool:
    """Grant bank exemption to employee"""
    exemption, created = EmployeeExemption.objects.get_or_create(employee=employee)
    exemption.bank_exempted = True
    exemption.bank_exemption_reason = reason
    exemption.bank_exempted_by = granted_by
    exemption.bank_exempted_at = timezone.now()
    exemption.save()
    
    # Update verification status
    verification, _ = EmployeeVerification.objects.get_or_create(employee=employee)
    verification.bank_verified = True  # Consider exempted as verified
    verification.save()
    
    # Check if salary should be activated (Phone + Reference + Bank verified)
    check_and_activate_salary(employee)
    
    logger.info(f"Bank exemption granted to employee {employee.id} - {employee.name} by {granted_by.username}")
    return True


def calculate_behavior_index(employee: HREmployee, period: str = 'month') -> dict:
    """
    Calculate behavior index based on attendance metrics
    Returns dict with score, rating, and breakdown
    """
    from attendance.models import Attendance
    from django.db.models import Count, Avg, Q
    from datetime import datetime, timedelta
    
    # Determine date range
    now = timezone.now()
    if period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = now - timedelta(days=7)
    else:
        start_date = now - timedelta(days=30)
    
    # Get attendance records for the period
    # Note: Attendance uses User model, so we need to get via employee.user
    if not employee.user:
        return {
            'score': 0,
            'rating': 'Poor',
            'breakdown': {}
        }
    
    attendance_records = Attendance.objects.filter(
        employee=employee.user,
        date__gte=start_date.date()
    )
    
    # Calculate metrics
    total_days = attendance_records.count()
    late_count = attendance_records.filter(status='late').count()
    absent_count = attendance_records.filter(status='absent').count()
    
    # Calculate early exits (check-out before work_end - threshold)
    # This would require checking against AttendanceRule, simplified here
    early_exits = 0  # TODO: Calculate based on actual check-out times
    
    # Calculate average check-in time (bonus for consistency)
    check_in_times = attendance_records.exclude(check_in__isnull=True).values_list('check_in', flat=True)
    avg_check_in_bonus = 0  # TODO: Calculate consistency bonus
    
    # Calculate score (starting from 100)
    score = 100.0
    
    # Deductions
    score -= late_count * 5  # -5 per late entry
    score -= absent_count * 10  # -10 per absence
    score -= early_exits * 3  # -3 per early exit
    
    # Add bonus for consistency
    score += avg_check_in_bonus
    
    # Clamp score between 0 and 100
    score = max(0, min(100, score))
    
    # Determine rating
    if score >= 90:
        rating = 'Excellent'
    elif score >= 75:
        rating = 'Fair'
    else:
        rating = 'Poor'
    
    return {
        'score': round(score, 2),
        'rating': rating,
        'breakdown': {
            'total_days': total_days,
            'late_count': late_count,
            'absent_count': absent_count,
            'early_exits': early_exits,
            'period': period
        }
    }

