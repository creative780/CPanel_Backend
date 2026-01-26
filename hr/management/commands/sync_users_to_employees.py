"""
Django management command to sync User records to HREmployee records.
This ensures all users visible in chat also appear in the employee management page.

Usage:
    python manage.py sync_users_to_employees --dry-run  # Preview changes
    python manage.py sync_users_to_employees             # Create records
    python manage.py sync_users_to_employees --username abdullah12  # Sync specific user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from hr.models import HREmployee

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync User records to HREmployee records for users that don\'t have an HREmployee record'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without actually creating records',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Sync only a specific user by username',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-sync even if HREmployee already exists (updates existing records)',
        )
        parser.add_argument(
            '--branch',
            type=str,
            choices=['dubai', 'pakistan'],
            default='dubai',
            help='Set default branch for new employees (default: dubai)',
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=['admin', 'sales', 'designer', 'production', 'delivery', 'finance'],
            default='sales',
            help='Set default role for users without roles (default: sales)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        username_filter = options.get('username')
        force = options.get('force', False)
        default_branch = options.get('branch', 'dubai')
        default_role = options.get('role', 'sales')
        
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS('Sync Users to HREmployee'))
        self.stdout.write('=' * 80)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN MODE - No records will be created\n'))
        
        # Get users to sync
        if username_filter:
            users = User.objects.filter(username=username_filter, is_superuser=False)
            if not users.exists():
                self.stdout.write(
                    self.style.ERROR(f'User "{username_filter}" not found or is a superuser')
                )
                return
        else:
            users = User.objects.filter(is_superuser=False).order_by('username')
        
        self.stdout.write(f'Found {users.count()} user(s) to check...\n')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []
        created_employees = []
        updated_employees = []
        
        for user in users:
            try:
                # Check if HREmployee already exists
                hr_employee = None
                hr_employee_by_user = HREmployee.objects.filter(user=user).first()
                hr_employee_by_email = HREmployee.objects.filter(email=user.email).first() if user.email else None
                
                if hr_employee_by_user:
                    hr_employee = hr_employee_by_user
                elif hr_employee_by_email:
                    hr_employee = hr_employee_by_email
                
                if hr_employee and not force:
                    skipped_count += 1
                    self.stdout.write(
                        f'  ✓ Skipping {user.username} - HREmployee already exists (ID: {hr_employee.id})'
                    )
                    continue
                
                # Prepare employee data
                employee_data = self._prepare_employee_data(user, default_branch, default_role)
                
                if dry_run:
                    if hr_employee:
                        self.stdout.write(
                            self.style.NOTICE(f'  [DRY RUN] Would update HREmployee for {user.username}:')
                        )
                        self.stdout.write(f'    ID: {hr_employee.id}')
                        self.stdout.write(f'    Name: {employee_data["name"]}')
                        self.stdout.write(f'    Email: {employee_data["email"]}')
                        self.stdout.write(f'    Role: {employee_data["role"]}')
                        self.stdout.write(f'    Branch: {employee_data["branch"]}')
                        updated_count += 1
                    else:
                        self.stdout.write(
                            self.style.NOTICE(f'  [DRY RUN] Would create HREmployee for {user.username}:')
                        )
                        self.stdout.write(f'    Name: {employee_data["name"]}')
                        self.stdout.write(f'    Email: {employee_data["email"]}')
                        self.stdout.write(f'    Role: {employee_data["role"]}')
                        self.stdout.write(f'    Branch: {employee_data["branch"]}')
                        created_count += 1
                else:
                    if hr_employee and force:
                        # Update existing employee
                        for key, value in employee_data.items():
                            if key != 'user' or hr_employee.user is None:
                                setattr(hr_employee, key, value)
                        hr_employee.save()
                        updated_count += 1
                        updated_employees.append({
                            'id': hr_employee.id,
                            'username': user.username,
                            'name': hr_employee.name
                        })
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Updated HREmployee for {user.username} (ID: {hr_employee.id})'
                            )
                        )
                    else:
                        # Create new employee
                        hr_employee = HREmployee.objects.create(**employee_data)
                        created_count += 1
                        created_employees.append({
                            'id': hr_employee.id,
                            'username': user.username,
                            'name': hr_employee.name
                        })
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Created HREmployee for {user.username} (ID: {hr_employee.id})'
                            )
                        )
            except IntegrityError as e:
                error_msg = f'  ✗ Integrity error for {user.username}: {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
            except Exception as e:
                error_msg = f'  ✗ Failed to sync {user.username}: {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('SUMMARY')
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total users checked: {users.count()}')
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count}'))
        self.stdout.write(f'Skipped (already exist): {skipped_count}')
        if errors:
            self.stdout.write(self.style.ERROR(f'Errors: {len(errors)}'))
        
        if created_employees:
            self.stdout.write('\nCreated employees:')
            for emp in created_employees:
                self.stdout.write(f'  - {emp["name"]} ({emp["username"]}) - ID: {emp["id"]}')
        
        if updated_employees:
            self.stdout.write('\nUpdated employees:')
            for emp in updated_employees:
                self.stdout.write(f'  - {emp["name"]} ({emp["username"]}) - ID: {emp["id"]}')
        
        if errors:
            self.stdout.write('\nErrors:')
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  {error}'))
        
        if dry_run:
            self.stdout.write('\n' + self.style.WARNING('⚠️  DRY RUN - No records were actually created or updated'))
        else:
            self.stdout.write('\n' + self.style.SUCCESS('✅ Sync completed!'))
        
        self.stdout.write('=' * 80)
    
    def _prepare_employee_data(self, user, default_branch, default_role):
        """Prepare HREmployee data from User record"""
        # Build name from first_name and last_name, fallback to username
        name_parts = [user.first_name, user.last_name]
        name = ' '.join(filter(None, name_parts)).strip()
        if not name:
            name = user.username
        
        # Get email or generate placeholder
        email = user.email
        if not email:
            email = f"{user.username}@example.com"
            self.stdout.write(
                self.style.WARNING(f'    Warning: User {user.username} has no email, using placeholder: {email}')
            )
        
        # Get role from user's roles field, validate and default
        role = default_role
        if user.roles and len(user.roles) > 0:
            user_role = user.roles[0]
            # Validate role is in HREmployee.ROLE_CHOICES
            valid_roles = [choice[0] for choice in HREmployee.ROLE_CHOICES]
            if user_role in valid_roles:
                role = user_role
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'    Warning: User {user.username} has invalid role "{user_role}", using default: {default_role}'
                    )
                )
        
        return {
            'name': name,
            'email': email,
            'user': user,
            'status': 'Active',
            'branch': default_branch,
            'role': role,
            'salary_status': 'ON_HOLD',
            'verification_status': 'not_started',
            'phone': '',
            'image': '',
            'designation': '',
            'department': '',
        }

