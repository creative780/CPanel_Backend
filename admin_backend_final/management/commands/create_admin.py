"""
Django management command to create an admin user.
Usage: python manage.py create_admin --username affan --password affan
"""
from django.core.management.base import BaseCommand
from admin_backend_final.models import Admin, AdminRole, AdminRoleMap
from admin_backend_final.utilities import generate_admin_id


class Command(BaseCommand):
    help = 'Creates an admin user with the specified username and password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Admin username'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Admin password'
        )
        parser.add_argument(
            '--role',
            type=str,
            default='Super Admin',
            help='Admin role name (default: Super Admin)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        role_name = options['role']

        # Get or create Super Admin role with all access pages
        all_access_pages = [
            'Dashboard',
            'Products Section',
            'Blog',
            'Settings',
            'First Carousel',
            'Media Library',
            'Notifications',
            'Testimonials',
            'Second Carousel',
            'Hero Banner',
            'Manage Categories',
            'Orders',
            'Inventory',
            'Google Analytics',
            'New Account',
            'Google Settings',
            'Navbar',
            'Attributes',
            'User View',
            'Event Call Back',
            'Recently Deleted',
            'Blog View',
        ]

        # Get or create role (handle potential duplicates)
        role = AdminRole.objects.filter(role_name=role_name).first()
        
        if not role:
            # Create new role
            role = AdminRole.objects.create(
                role_id=f'R-{role_name}',
                role_name=role_name,
                description=f'{role_name} role',
                access_pages=all_access_pages
            )
        else:
            # Update existing role if it has no access pages
            if not role.access_pages:
                role.access_pages = all_access_pages
                role.save()

        # Check if admin already exists
        admin = Admin.objects.filter(admin_name=username).first()
        
        if admin:
            # Update existing admin
            admin.password_hash = password
            admin.save()
            
            # Check if role mapping exists, create if not
            role_map, map_created = AdminRoleMap.objects.get_or_create(
                admin=admin,
                defaults={'role': role}
            )
            
            # Update role if it's different
            if role_map.role != role:
                role_map.role = role
                role_map.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated admin user:\n'
                    f'  Username: {username}\n'
                    f'  Password: {password}\n'
                    f'  Admin ID: {admin.admin_id}\n'
                    f'  Role: {role_name}'
                )
            )
            return

        # Generate admin ID for new admin
        admin_id = generate_admin_id(username, role_name, 1)

        # Check for ID collision and retry if needed
        attempt = 1
        while Admin.objects.filter(admin_id=admin_id).exists():
            attempt += 1
            if attempt > 5:
                self.stdout.write(
                    self.style.ERROR('Failed to generate unique admin ID after 5 attempts.')
                )
                return
            admin_id = generate_admin_id(username, role_name, attempt)

        # Create admin
        admin = Admin.objects.create(
            admin_id=admin_id,
            admin_name=username,
            password_hash=password
        )

        # Create role mapping
        AdminRoleMap.objects.create(admin=admin, role=role)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user:\n'
                f'  Username: {username}\n'
                f'  Password: {password}\n'
                f'  Admin ID: {admin_id}\n'
                f'  Role: {role_name}'
            )
        )
