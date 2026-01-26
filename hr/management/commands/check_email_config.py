"""
Django management command to check email configuration status.
Usage: python manage.py check_email_config
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from hr.services import validate_email_configuration


class Command(BaseCommand):
    help = 'Check email configuration status and validate Gmail setup'

    def handle(self, *args, **options):
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS('Email Configuration Check'))
        self.stdout.write('=' * 80)
        self.stdout.write('')
        
        # Show current settings (masked for security)
        self.stdout.write('Current Email Settings:')
        self.stdout.write(f'  Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'  Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'  TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'  SSL: {settings.EMAIL_USE_SSL}')
        
        email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        if email_user:
            # Mask email for security
            if '@' in email_user:
                parts = email_user.split('@')
                masked = f"{parts[0][:3]}***@{parts[1]}"
            else:
                masked = f"{email_user[:3]}***"
            self.stdout.write(f'  User: {masked}')
        else:
            self.stdout.write(self.style.WARNING('  User: NOT SET'))
        
        email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        if email_password:
            self.stdout.write(f'  Password: {"*" * min(len(email_password), 16)} (configured)')
        else:
            self.stdout.write(self.style.WARNING('  Password: NOT SET'))
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        self.stdout.write(f'  From Email: {from_email}')
        self.stdout.write('')
        
        # Run validation
        validation = validate_email_configuration()
        
        self.stdout.write('Validation Results:')
        self.stdout.write('-' * 80)
        
        if validation['valid']:
            self.stdout.write(self.style.SUCCESS('✅ VERIFIED: Configuration is VALID'))
        else:
            self.stdout.write(self.style.ERROR('❌ NOT VERIFIED: Configuration has ERRORS'))
        
        if validation['errors']:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('Errors:'))
            for error in validation['errors']:
                self.stdout.write(self.style.ERROR(f'  ❌ {error}'))
        
        if validation['warnings']:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Warnings:'))
            for warning in validation['warnings']:
                self.stdout.write(self.style.WARNING(f'  ⚠️  {warning}'))
        
        # Gmail-specific checks
        is_gmail = 'gmail.com' in (settings.EMAIL_HOST or '').lower() or 'gmail.com' in (email_user or '').lower()
        if is_gmail:
            self.stdout.write('')
            self.stdout.write('Gmail-Specific Checks:')
            self.stdout.write('-' * 80)
            
            # Check host
            if 'smtp.gmail.com' in (settings.EMAIL_HOST or '').lower():
                self.stdout.write(self.style.SUCCESS('  ✅ VERIFIED: EMAIL_HOST is smtp.gmail.com'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ NOT VERIFIED: EMAIL_HOST should be smtp.gmail.com (got: {settings.EMAIL_HOST})'))
            
            # Check FROM matches USER
            if email_user and from_email.lower() == email_user.lower():
                self.stdout.write(self.style.SUCCESS('  ✅ VERIFIED: FROM email matches EMAIL_HOST_USER'))
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ NOT VERIFIED: FROM email must match EMAIL_HOST_USER'))
                self.stdout.write(f'     Current: FROM={from_email}, USER={email_user}')
            
            # Check App Password format
            if email_password:
                password_clean = email_password.replace(' ', '').replace('-', '')
                if len(password_clean) == 16:
                    self.stdout.write(self.style.SUCCESS('  ✅ VERIFIED: App Password format is correct (16 characters)'))
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  NOT VERIFIED: App Password should be 16 characters (got: {len(password_clean)})'))
                    self.stdout.write(self.style.WARNING('     If authentication fails, ensure you\'re using App Password, not regular password'))
            else:
                self.stdout.write(self.style.ERROR('  ❌ NOT VERIFIED: EMAIL_HOST_PASSWORD is not set'))
        
        self.stdout.write('')
        self.stdout.write('=' * 80)
        
        if validation['valid']:
            self.stdout.write(self.style.SUCCESS('✅ VERIFIED: Email configuration is ready!'))
            self.stdout.write('')
            self.stdout.write('To test sending an email, run:')
            self.stdout.write(self.style.SUCCESS('  python manage.py test_email your-email@gmail.com'))
        else:
            self.stdout.write(self.style.ERROR('❌ NOT VERIFIED: Please fix the errors above before sending emails'))
            self.stdout.write('')
            self.stdout.write('See EMAIL_SETUP_GUIDE.md for configuration instructions')
        
        self.stdout.write('=' * 80)

