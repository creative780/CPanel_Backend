from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users for order assignment testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating test users...\n')
        
        # Admin user
        admin, created = User.objects.get_or_create(
            username='admin_test',
            defaults={'email': 'admin@test.com', 'roles': ['admin']}
        )
        admin.set_password('admin123')
        admin.is_active = True
        admin.roles = ['admin']
        admin.save()
        status = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f'  ✓ admin_test: {status}'))
        
        # Designer users
        designer1, created = User.objects.get_or_create(
            username='designer1',
            defaults={'email': 'designer1@test.com', 'roles': ['designer']}
        )
        designer1.set_password('designer123')
        designer1.is_active = True
        designer1.roles = ['designer']
        designer1.save()
        status = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f'  ✓ designer1: {status}'))
        
        designer2, created = User.objects.get_or_create(
            username='designer2',
            defaults={'email': 'designer2@test.com', 'roles': ['designer']}
        )
        designer2.set_password('designer123')
        designer2.is_active = True
        designer2.roles = ['designer']
        designer2.save()
        status = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f'  ✓ designer2: {status}'))
        
        # Production users
        production1, created = User.objects.get_or_create(
            username='production1',
            defaults={'email': 'production1@test.com', 'roles': ['production']}
        )
        production1.set_password('production123')
        production1.is_active = True
        production1.roles = ['production']
        production1.save()
        status = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f'  ✓ production1: {status}'))
        
        production2, created = User.objects.get_or_create(
            username='production2',
            defaults={'email': 'production2@test.com', 'roles': ['production']}
        )
        production2.set_password('production123')
        production2.is_active = True
        production2.roles = ['production']
        production2.save()
        status = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f'  ✓ production2: {status}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ All test users ready!'))
        self.stdout.write('\nTest user credentials:')
        self.stdout.write('  Admin: admin_test / admin123')
        self.stdout.write('  Designer 1: designer1 / designer123')
        self.stdout.write('  Designer 2: designer2 / designer123')
        self.stdout.write('  Production 1: production1 / production123')
        self.stdout.write('  Production 2: production2 / production123')
