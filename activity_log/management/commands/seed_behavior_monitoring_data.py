"""
Django management command to seed behavior monitoring test data

Usage:
    python manage.py seed_behavior_monitoring_data

This command creates test activity events for all behavior monitoring categories:
- Failed login attempts
- Suspicious logins (multiple IPs within 1 hour)
- Unauthorized access attempts
- High-risk edits (Payroll/Salary records)
- Inactive user access attempts
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from activity_log.models import ActivityEvent, ActorRole, Verb, Source
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed test data for behavior monitoring system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            # Clear test events (those with specific context markers)
            ActivityEvent.objects.filter(
                context__test_data=True
            ).delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing test data'))

        self.stdout.write('Creating behavior monitoring test data...')
        
        # Create or get admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@test.com',
                'roles': ['admin'],
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if not admin_user.has_usable_password():
            admin_user.set_password('admin123')
            admin_user.save()

        # Create test users
        test_user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'testuser@test.com',
                'roles': ['sales'],
                'is_active': True,
            }
        )
        
        inactive_user, _ = User.objects.get_or_create(
            username='inactive_user',
            defaults={
                'email': 'inactive@test.com',
                'roles': ['sales'],
                'is_active': False,  # Inactive user
            }
        )

        now = timezone.now()
        
        # 1. Create Failed Login Attempts
        self.stdout.write('  Creating failed login attempts...')
        self.create_failed_logins(now)
        
        # 2. Create Suspicious Logins
        self.stdout.write('  Creating suspicious login patterns...')
        self.create_suspicious_logins(admin_user, now)
        
        # 3. Create Unauthorized Access
        self.stdout.write('  Creating unauthorized access attempts...')
        self.create_unauthorized_access(admin_user, now)
        
        # 4. Create High-Risk Edits
        self.stdout.write('  Creating high-risk edits...')
        self.create_high_risk_edits(admin_user, now)
        
        # 5. Create Inactive User Access
        self.stdout.write('  Creating inactive user access attempts...')
        self.create_inactive_user_access(inactive_user, now)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created behavior monitoring test data!')
        )

    def create_failed_logins(self, now):
        """Create failed login attempt events"""
        # Multiple failed attempts from same username+IP
        for i in range(3):
            ActivityEvent.objects.create(
                timestamp=now - timedelta(minutes=10-i),
                actor_id=None,  # No actor for failed logins
                actor_role=ActorRole.SYSTEM,
                verb=Verb.LOGIN,
                target_type="User",
                target_id="failed_user",
                context={
                    "username": "failed_user",
                    "ip_address": "192.168.1.100",
                    "device_name": "Windows Desktop",
                    "status": "failed",
                    "success": False,
                    "error": "Invalid credentials",
                    "test_data": True,
                },
                source=Source.FRONTEND,
                request_id=f"req_failed_{uuid.uuid4().hex[:16]}_{i}",
                tenant_id="default",
                hash=uuid.uuid4().hex[:64]
            )
        
        # Single failed attempt from different IP
        ActivityEvent.objects.create(
            timestamp=now - timedelta(minutes=5),
            actor_id=None,
            actor_role=ActorRole.SYSTEM,
            verb=Verb.LOGIN,
            target_type="User",
            target_id="another_user",
            context={
                "username": "another_user",
                "ip_address": "203.0.113.45",
                "device_name": "Unknown Device",
                "status": "failed",
                "success": False,
                "test_data": True,
            },
            source=Source.FRONTEND,
            request_id=f"req_failed_single_{uuid.uuid4().hex[:16]}",
            tenant_id="default",
            hash=uuid.uuid4().hex[:64]
        )

    def create_suspicious_logins(self, user, now):
        """Create suspicious login pattern (same user, multiple IPs within 1 hour)"""
        ips = ["192.168.1.101", "203.0.113.10", "198.51.100.20", "172.16.0.50"]
        locations = ["Dubai, UAE", "Abu Dhabi, UAE", "Sharjah, UAE", "Ras Al Khaimah, UAE"]
        
        # Create 4 logins within 30 minutes from different IPs
        for i, ip in enumerate(ips):
            ActivityEvent.objects.create(
                timestamp=now - timedelta(minutes=30-i*5),
                actor_id=user.id,
                actor_role=ActorRole.ADMIN,
                verb=Verb.LOGIN,
                target_type="User",
                target_id=str(user.id),
                context={
                    "username": user.username,
                    "ip_address": ip,
                    "device_name": f"Device {i+1}",
                    "location_address": locations[i],
                    "success": True,
                    "test_data": True,
                },
                source=Source.FRONTEND,
                request_id=f"req_suspicious_{uuid.uuid4().hex[:16]}_{i}",
                tenant_id="default",
                hash=uuid.uuid4().hex[:64]
            )

    def create_unauthorized_access(self, user, now):
        """Create unauthorized access attempts"""
        # 403 Forbidden error
        ActivityEvent.objects.create(
            timestamp=now - timedelta(minutes=20),
            actor_id=user.id,
            actor_role=ActorRole.ADMIN,
            verb=Verb.UPDATE,
            target_type="Payroll",
            target_id="payroll_1",
            context={
                "status_code": 403,
                "error": "Access forbidden: insufficient permissions",
                "ip_address": "192.168.1.102",
                "test_data": True,
            },
            source=Source.FRONTEND,
            request_id=f"req_unauth_1_{uuid.uuid4().hex[:16]}",
            tenant_id="default",
            hash=uuid.uuid4().hex[:64]
        )
        
        # Failed export
        ActivityEvent.objects.create(
            timestamp=now - timedelta(minutes=15),
            actor_id=user.id,
            actor_role=ActorRole.ADMIN,
            verb="EXPORT",
            target_type="Report",
            target_id="report_1",
            context={
                "status": "failed",
                "error": "Export failed: access denied",
                "ip_address": "192.168.1.103",
                "test_data": True,
            },
            source=Source.FRONTEND,
            request_id=f"req_export_failed_{uuid.uuid4().hex[:16]}",
            tenant_id="default",
            hash=uuid.uuid4().hex[:64]
        )

    def create_high_risk_edits(self, user, now):
        """Create high-risk edit events (multiple edits on sensitive records within 1 hour)"""
        target_id = "payroll_123"
        
        # Create 5 UPDATE events within 40 minutes on same Payroll record
        for i in range(5):
            ActivityEvent.objects.create(
                timestamp=now - timedelta(minutes=40-i*8),
                actor_id=user.id,
                actor_role=ActorRole.ADMIN,
                verb=Verb.UPDATE,
                target_type="Payroll",
                target_id=target_id,
                context={
                    "username": user.username,
                    "ip_address": "192.168.1.104",
                    "changes": {
                        "salary": {
                            "old": 5000 + i * 100,
                            "new": 5100 + i * 100
                        }
                    },
                    "test_data": True,
                },
                source=Source.FRONTEND,
                request_id=f"req_highrisk_{uuid.uuid4().hex[:16]}_{i}",
                tenant_id="default",
                hash=uuid.uuid4().hex[:64]
            )
        
        # Create another high-risk edit scenario with 7 edits (high severity)
        target_id2 = "salary_456"
        for i in range(7):
            ActivityEvent.objects.create(
                timestamp=now - timedelta(minutes=30-i*4),
                actor_id=user.id,
                actor_role=ActorRole.ADMIN,
                verb=Verb.UPDATE,
                target_type="Salary",
                target_id=target_id2,
                context={
                    "username": user.username,
                    "ip_address": "192.168.1.105",
                    "test_data": True,
                },
                source=Source.FRONTEND,
                request_id=f"req_highrisk2_{uuid.uuid4().hex[:16]}_{i}",
                tenant_id="default",
                hash=uuid.uuid4().hex[:64]
            )

    def create_inactive_user_access(self, inactive_user, now):
        """Create login attempts from inactive user"""
        # Create 3 login attempts from inactive user
        for i in range(3):
            ActivityEvent.objects.create(
                timestamp=now - timedelta(minutes=25-i*2),
                actor_id=inactive_user.id,
                actor_role=ActorRole.SALES,
                verb=Verb.LOGIN,
                target_type="User",
                target_id=str(inactive_user.id),
                context={
                    "username": inactive_user.username,
                    "ip_address": "192.168.1.106",
                    "device_name": "MacBook Pro",
                    "is_active": False,
                    "user_status": "inactive",
                    "success": False,
                    "error": "User account is inactive",
                    "test_data": True,
                },
                source=Source.FRONTEND,
                request_id=f"req_inactive_{uuid.uuid4().hex[:16]}_{i}",
                tenant_id="default",
                hash=uuid.uuid4().hex[:64]
            )

