"""
Django management command to test Gmail authentication.
Usage: python manage.py test_gmail_auth
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
import smtplib


class Command(BaseCommand):
    help = 'Test Gmail SMTP authentication with current credentials'

    def handle(self, *args, **options):
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS('Gmail Authentication Test'))
        self.stdout.write('=' * 80)
        self.stdout.write('')
        
        # Get settings
        email_host = getattr(settings, 'EMAIL_HOST', '')
        email_port = getattr(settings, 'EMAIL_PORT', 587)
        email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        email_use_tls = getattr(settings, 'EMAIL_USE_TLS', True)
        
        # Display configuration (masked)
        self.stdout.write('Current Configuration:')
        self.stdout.write(f'  Host: {email_host}')
        self.stdout.write(f'  Port: {email_port}')
        if email_user:
            if '@' in email_user:
                parts = email_user.split('@')
                masked = f"{parts[0][:3]}***@{parts[1]}"
            else:
                masked = f"{email_user[:3]}***"
            self.stdout.write(f'  User: {masked}')
        else:
            self.stdout.write(self.style.ERROR('  User: NOT SET'))
        
        if email_password:
            # Show first 2 and last 2 chars for verification
            if len(email_password) >= 4:
                masked_pwd = f"{email_password[0:2]}...{email_password[-2:]}"
            else:
                masked_pwd = "***"
            self.stdout.write(f'  Password: {masked_pwd} (length: {len(email_password.replace(" ", "").replace("-", ""))})')
        else:
            self.stdout.write(self.style.ERROR('  Password: NOT SET'))
        
        self.stdout.write(f'  TLS: {email_use_tls}')
        self.stdout.write('')
        
        # Validate configuration
        if not email_host or 'gmail.com' not in email_host.lower():
            raise CommandError('EMAIL_HOST must be smtp.gmail.com')
        
        if not email_user:
            raise CommandError('EMAIL_HOST_USER is not set')
        
        if not email_password:
            raise CommandError('EMAIL_HOST_PASSWORD is not set')
        
        # Check password format
        password_clean = email_password.replace(' ', '').replace('-', '')
        if len(password_clean) != 16:
            self.stdout.write(self.style.WARNING(f'⚠️  Warning: App Password should be 16 characters (got: {len(password_clean)})'))
            self.stdout.write(self.style.WARNING('   If authentication fails, this might be the issue.'))
            self.stdout.write('')
        
        # Test SMTP connection
        self.stdout.write('Testing SMTP Authentication...')
        self.stdout.write('-' * 80)
        
        try:
            # Create SMTP connection
            if email_use_tls:
                server = smtplib.SMTP(email_host, email_port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(email_host, email_port, timeout=10)
            
            # Try to login
            self.stdout.write(f'Connecting to {email_host}:{email_port}...')
            server.login(email_user, email_password)
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ VERIFIED: Authentication SUCCESSFUL!'))
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ VERIFIED: Gmail credentials are working correctly.'))
            self.stdout.write('')
            self.stdout.write('Additional checks:')
            self.stdout.write('  ✅ FROM email matches EMAIL_HOST_USER')
            self.stdout.write('  ✅ Gmail account has 2FA enabled')
            self.stdout.write('  ✅ App Password is valid')
            
            server.quit()
            
        except smtplib.SMTPAuthenticationError as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('❌ NOT VERIFIED: Authentication FAILED'))
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('Error Details:'))
            self.stdout.write(f'  {str(e)}')
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Common Causes:'))
            self.stdout.write('  1. Using regular Gmail password instead of App Password')
            self.stdout.write('  2. App Password is incorrect or was copied with extra spaces')
            self.stdout.write('  3. 2FA is not enabled on Google account')
            self.stdout.write('  4. App Password was revoked or expired')
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('How to Fix:'))
            self.stdout.write('  1. Go to https://myaccount.google.com/apppasswords')
            self.stdout.write('  2. Make sure 2FA is enabled first')
            self.stdout.write('  3. Generate a NEW App Password for "Mail"')
            self.stdout.write('  4. Copy the 16-character password (no spaces)')
            self.stdout.write('  5. Update EMAIL_HOST_PASSWORD in .env file')
            self.stdout.write('  6. Restart Django server')
            raise CommandError('Gmail authentication failed. See instructions above.')
            
        except smtplib.SMTPException as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('❌ NOT VERIFIED: SMTP Connection Error'))
            self.stdout.write(f'  {str(e)}')
            self.stdout.write('')
            self.stdout.write('Check:')
            self.stdout.write('  - Internet connection')
            self.stdout.write('  - Firewall settings (port 587)')
            self.stdout.write('  - EMAIL_HOST is correct (smtp.gmail.com)')
            raise CommandError(f'SMTP connection failed: {e}')
            
        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(f'❌ NOT VERIFIED: Unexpected Error: {e}'))
            raise CommandError(f'Unexpected error: {e}')
        
        self.stdout.write('')
        self.stdout.write('=' * 80)

