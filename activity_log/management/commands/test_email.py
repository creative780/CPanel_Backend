"""
Django management command to test email configuration.
Usage: python manage.py test_email recipient@example.com
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            type=str,
            help='Email address to send test email to',
        )
        parser.add_argument(
            '--subject',
            type=str,
            default=None,
            help='Custom email subject (optional)',
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        subject = options.get('subject') or 'Test Email from CRM System'
        
        self.stdout.write(f'Testing email configuration...')
        self.stdout.write(f'Recipient: {recipient}')
        self.stdout.write(f'Backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'Port: {settings.EMAIL_PORT}')
        self.stdout.write(f'TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'From: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write('')
        
        try:
            message = f"""
This is a test email from the CRM Activity Log Reporting System.

If you received this email, your email configuration is working correctly!

Email Backend: {settings.EMAIL_BACKEND}
SMTP Host: {settings.EMAIL_HOST}
SMTP Port: {settings.EMAIL_PORT}
TLS Enabled: {settings.EMAIL_USE_TLS}

This email was sent at: {self.get_current_timestamp()}

Best regards,
CRM System Test
"""
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent test email to {recipient}!')
            )
            self.stdout.write(
                self.style.WARNING(
                    'Note: If using console backend, check the console output above for the email content.'
                )
            )
            
        except Exception as e:
            raise CommandError(
                f'Failed to send test email: {e}\n\n'
                'Please check:\n'
                '1. Email configuration in settings.py or .env file\n'
                '2. SMTP server credentials (username/password)\n'
                '3. Network connectivity to SMTP server\n'
                '4. Firewall settings (port 587/465)\n'
                'See EMAIL_SETUP_GUIDE.md for detailed instructions.'
            )
    
    def get_current_timestamp(self):
        from django.utils import timezone
        return timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')














































