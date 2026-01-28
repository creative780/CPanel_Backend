"""
Django management command to add "Attributes" permission to all admin roles.
Usage: python manage.py add_attributes_permission
"""
from django.core.management.base import BaseCommand
from admin_backend_final.models import AdminRole


class Command(BaseCommand):
    help = 'Adds "Attributes" to access_pages for all admin roles'

    def handle(self, *args, **options):
        updated_count = 0
        already_has_count = 0
        
        # Get all admin roles
        all_roles = AdminRole.objects.all()
        
        if not all_roles.exists():
            self.stdout.write(
                self.style.WARNING('No admin roles found in the database.')
            )
            return
        
        for role in all_roles:
            access_pages = role.access_pages or []
            
            # Check if "Attributes" is already in the list (case-insensitive)
            has_attributes = any(
                str(page).strip().lower() == 'attributes' 
                for page in access_pages
            )
            
            if has_attributes:
                already_has_count += 1
                self.stdout.write(
                    f'Role "{role.role_name}" already has "Attributes" permission.'
                )
            else:
                # Add "Attributes" to the access_pages list
                access_pages.append('Attributes')
                role.access_pages = access_pages
                role.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Added "Attributes" permission to role "{role.role_name}"'
                    )
                )
        
        # Summary
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_count} role(s).'
            )
        )
        if already_has_count > 0:
            self.stdout.write(
                f'{already_has_count} role(s) already had "Attributes" permission.'
            )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING(
                'Note: You may need to log out and log back in for the changes to take effect.'
            )
        )
