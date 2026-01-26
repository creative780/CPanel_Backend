"""
Django management command to sync CRM users to Matrix (Synapse)
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.services.matrix_service import matrix_service
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync CRM users to Matrix (Synapse) homeserver'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Sync only a specific user by username',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-sync even if user is already synced',
        )
        parser.add_argument(
            '--create-tokens',
            action='store_true',
            help='Create access tokens for synced users',
        )

    def handle(self, *args, **options):
        username_filter = options.get('username')
        force = options.get('force', False)
        create_tokens = options.get('create_tokens', False)
        
        # Check if Matrix service is configured
        if not matrix_service.admin_token:
            self.stdout.write(
                self.style.ERROR(
                    'MATRIX_ADMIN_ACCESS_TOKEN not configured. '
                    'Set it in your environment or Django settings.'
                )
            )
            return
        
        # Get users to sync
        if username_filter:
            users = User.objects.filter(username=username_filter)
            if not users.exists():
                self.stdout.write(
                    self.style.ERROR(f'User "{username_filter}" not found')
                )
                return
        else:
            # Sync all active users
            users = User.objects.filter(is_active=True)
        
        synced_count = 0
        error_count = 0
        skipped_count = 0
        
        # Import time for rate limiting
        import time
        
        for user in users:
                    # Skip if already synced and not forcing
                    if user.matrix_synced and not force:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Skipping {user.username} (already synced)')
                        )
                        continue
                    
                    # Add delay to respect rate limits (1.5 seconds between requests to avoid rate limiting)
                    time.sleep(1.5)
                    
                    try:
                        # Generate Matrix user ID using configured server name
                        matrix_user_id = user.get_matrix_user_id(matrix_service.server_name)
                
                        # Create display name from user's name
                        display_name = user.get_full_name() or user.username
                        
                        # Determine if user should be admin in Matrix
                        is_admin = user.is_admin()
                        
                        # Create user in Matrix
                        # Generate a password for the user (stored in Matrix, used for token creation)
                        import secrets
                        matrix_password = secrets.token_urlsafe(16)
                        
                        result = matrix_service.create_user(
                            username=user.username,
                            password=matrix_password,  # Generate password for Matrix login
                            display_name=display_name,
                            admin=is_admin
                        )
                        
                        if result:
                            # Update user model
                            user.matrix_user_id = matrix_user_id
                            user.matrix_synced = True
                            
                            # Create access token if requested
                            if create_tokens:
                                # Get password from result if available
                                user_password = result.get('password')
                                if user_password:
                                    token = matrix_service.create_access_token(
                                        matrix_user_id,
                                        device_id=f"crm-{user.id}",
                                        password=user_password
                                    )
                                    if token:
                                        user.matrix_access_token = token
                                        self.stdout.write(
                                            self.style.SUCCESS(
                                                f'Created access token for {user.username}'
                                            )
                                        )
                                    else:
                                        self.stdout.write(
                                            self.style.WARNING(
                                                f'Failed to create access token for {user.username} - login may have failed'
                                            )
                                        )
                                else:
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'Cannot create access token for {user.username} - password not available (user may already exist)'
                                        )
                                    )
                            
                            user.save(update_fields=['matrix_user_id', 'matrix_synced', 'matrix_access_token'])
                            synced_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Synced {user.username} -> {matrix_user_id}'
                                )
                            )
                        else:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(
                                    f'Failed to sync {user.username} to Matrix'
                                )
                            )
                    
                    except Exception as e:
                        error_count += 1
                        logger.exception(f'Error syncing user {user.username} to Matrix')
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error syncing {user.username}: {str(e)}'
                            )
                        )
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS(f'Synced: {synced_count}')
        )
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f'Skipped: {skipped_count}')
            )
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'Errors: {error_count}')
            )
        self.stdout.write('=' * 50)

