"""
Django management command to remove device tokens from database.

Usage:
    python manage.py remove_device_tokens --hostname YOUR_HOSTNAME
    python manage.py remove_device_tokens --user-email user@example.com
    python manage.py remove_device_tokens --all (admin only)
    python manage.py remove_device_tokens --dry-run (preview only)
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from monitoring.models import Device, DeviceToken
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Remove device tokens and devices from database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hostname',
            type=str,
            help='Remove devices with this hostname',
        )
        parser.add_argument(
            '--user-email',
            type=str,
            help='Remove devices for this user email',
        )
        parser.add_argument(
            '--device-id',
            type=str,
            help='Remove specific device by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Remove all devices (admin only)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what will be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompts',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("Device Token Removal Tool"))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY-RUN MODE: No changes will be made"))
            self.stdout.write("")
        
        # Determine which devices to remove
        devices_to_remove = None
        
        if options['device_id']:
            # Remove specific device by ID
            try:
                device = Device.objects.get(id=options['device_id'])
                devices_to_remove = Device.objects.filter(id=device.id)
                self.stdout.write(f"Found device: {device.hostname} ({device.id})")
            except Device.DoesNotExist:
                raise CommandError(f"Device with ID '{options['device_id']}' not found")
        
        elif options['hostname']:
            # Remove devices by hostname
            devices_to_remove = Device.objects.filter(hostname=options['hostname'])
            count = devices_to_remove.count()
            if count == 0:
                raise CommandError(f"No devices found with hostname '{options['hostname']}'")
            self.stdout.write(f"Found {count} device(s) with hostname '{options['hostname']}'")
        
        elif options['user_email']:
            # Remove devices by user email
            try:
                user = User.objects.get(email=options['user_email'])
                devices_to_remove = Device.objects.filter(current_user=user)
                count = devices_to_remove.count()
                if count == 0:
                    self.stdout.write(self.style.WARNING(f"No devices found for user '{options['user_email']}'"))
                    return
                self.stdout.write(f"Found {count} device(s) for user '{user.email}'")
            except User.DoesNotExist:
                raise CommandError(f"User with email '{options['user_email']}' not found")
        
        elif options['all']:
            # Remove all devices (admin only)
            if not force:
                self.stdout.write(self.style.ERROR("WARNING: This will delete ALL devices and tokens!"))
                confirm = input("Type 'DELETE ALL' to confirm: ")
                if confirm != 'DELETE ALL':
                    self.stdout.write(self.style.WARNING("Operation cancelled"))
                    return
            
            devices_to_remove = Device.objects.all()
            count = devices_to_remove.count()
            if count == 0:
                self.stdout.write(self.style.WARNING("No devices found in database"))
                return
            self.stdout.write(f"Found {count} device(s) in database")
        
        else:
            raise CommandError("Please specify --hostname, --user-email, --device-id, or --all")
        
        # Show what will be deleted
        self.stdout.write("")
        self.stdout.write("Devices to be removed:")
        self.stdout.write("-" * 80)
        
        for device in devices_to_remove:
            token_info = "No token"
            try:
                token = device.token
                token_info = f"Token expires: {token.expires_at}"
            except DeviceToken.DoesNotExist:
                token_info = "No token record"
            except AttributeError:
                token_info = "No token record"
            
            self.stdout.write(f"  - {device.hostname} ({device.id})")
            self.stdout.write(f"    User: {device.current_user.email if device.current_user else 'None'}")
            self.stdout.write(f"    OS: {device.os}")
            self.stdout.write(f"    Status: {device.status}")
            self.stdout.write(f"    {token_info}")
            self.stdout.write("")
        
        # Confirm deletion
        if not force and not dry_run:
            self.stdout.write("")
            confirm = input("Do you want to proceed? (yes/no): ")
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING("Operation cancelled"))
                return
        
        # Perform deletion
        if dry_run:
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("DRY-RUN: Would delete the above devices"))
            return
        
        self.stdout.write("")
        self.stdout.write("Removing devices and tokens...")
        
        deleted_count = 0
        deleted_tokens = 0
        
        with transaction.atomic():
            for device in devices_to_remove:
                # Delete device token if exists (cascades from device deletion, but explicit for logging)
                try:
                    token = device.token
                    token.delete()
                    deleted_tokens += 1
                    logger.info(f"Deleted token for device {device.id}")
                except DeviceToken.DoesNotExist:
                    pass
                
                # Delete device (this will cascade to token if not already deleted)
                device_id = device.id
                device_hostname = device.hostname
                device.delete()
                deleted_count += 1
                logger.info(f"Deleted device {device_id} ({device_hostname})")
        
        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS(f"Cleanup Complete!"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"  Devices deleted: {deleted_count}")
        self.stdout.write(f"  Tokens deleted: {deleted_tokens}")
        self.stdout.write("")
        self.stdout.write("Next steps:")
        self.stdout.write("  1. Remove local config tokens: .\remove_device_tokens.ps1")
        self.stdout.write("  2. Generate new enrollment token from frontend")
        self.stdout.write("  3. Run installer with new token")
        self.stdout.write("")
