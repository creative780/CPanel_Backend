"""
Django management command to delete ALL employee monitoring data from the server.
WARNING: This will permanently delete all monitoring data including:
- Devices, Heartbeats, Recordings, Sessions, DeviceUserBinds, IdleAlerts
- All recording files and thumbnails from storage
- Legacy Employee monitoring data
"""

import os
import asyncio
import inspect
from django.core.management.base import BaseCommand
from django.db import transaction
from monitoring.models import (
    Device, Heartbeat, Recording, RecordingSegment, Session,
    DeviceUserBind, IdleAlert, DeviceToken, Org,
    Employee, EmployeeActivity, EmployeeAsset, EmployeeSummary
)
from monitoring.storage import get_storage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def delete_storage_file(storage, key):
    """Helper to delete a file from storage (handles both sync and async)"""
    try:
        delete_method = storage.delete
        if inspect.iscoroutinefunction(delete_method):
            # Async method
            asyncio.run(delete_method(key))
        else:
            # Sync method
            delete_method(key)
        return True
    except Exception as e:
        logger.warning(f"Failed to delete file {key}: {e}")
        return False


class Command(BaseCommand):
    help = 'Delete ALL employee monitoring data from the server (WARNING: Irreversible!)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion (required to actually delete)'
        )
        parser.add_argument(
            '--keep-devices',
            action='store_true',
            help='Keep device records but delete all monitoring data (heartbeats, recordings, etc.)'
        )
        parser.add_argument(
            '--keep-files',
            action='store_true',
            help='Keep files in storage but delete database records'
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        keep_devices = options['keep_devices']
        keep_files = options['keep_files']

        if not confirm:
            self.stdout.write(self.style.ERROR(
                '\n' + '='*70 + '\n'
                'WARNING: This will delete ALL employee monitoring data!\n'
                'This includes:\n'
                '  - All devices and their configurations\n'
                '  - All heartbeats, recordings, and segments\n'
                '  - All sessions, device-user bindings, and idle alerts\n'
                '  - All recording files and thumbnails from storage\n'
                '  - All legacy employee monitoring data\n'
                '\n'
                'This action is IRREVERSIBLE!\n'
                '='*70 + '\n'
            ))
            self.stdout.write(self.style.WARNING(
                'To proceed, run with --confirm flag:\n'
                '  python manage.py delete_all_monitoring_data --confirm\n'
            ))
            return

        self.stdout.write(self.style.WARNING('Starting deletion of ALL monitoring data...'))
        
        try:
            with transaction.atomic():
                # Delete in order to respect foreign key constraints
                self.delete_monitoring_data(keep_devices, keep_files)
                
            self.stdout.write(self.style.SUCCESS('\n✓ All monitoring data deleted successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error during deletion: {e}'))
            logger.exception('Error deleting monitoring data')
            raise

    def delete_monitoring_data(self, keep_devices, keep_files):
        """Delete all monitoring data"""
        
        # 1. Delete Recording Segments (no dependencies)
        self.stdout.write('Deleting recording segments...')
        segments = RecordingSegment.objects.all()
        segment_count = segments.count()
        if segment_count > 0:
            # Delete segment files if not keeping files
            if not keep_files:
                self.delete_segment_files(segments)
            segments.delete()
            self.stdout.write(f'  ✓ Deleted {segment_count} recording segments')
        else:
            self.stdout.write('  ✓ No recording segments to delete')

        # 2. Delete Recordings
        self.stdout.write('Deleting recordings...')
        recordings = Recording.objects.all()
        recording_count = recordings.count()
        if recording_count > 0:
            # Delete recording files if not keeping files
            if not keep_files:
                self.delete_recording_files(recordings)
            recordings.delete()
            self.stdout.write(f'  ✓ Deleted {recording_count} recordings')
        else:
            self.stdout.write('  ✓ No recordings to delete')

        # 3. Delete Heartbeats
        self.stdout.write('Deleting heartbeats...')
        heartbeat_count = Heartbeat.objects.count()
        if heartbeat_count > 0:
            Heartbeat.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {heartbeat_count} heartbeats')
        else:
            self.stdout.write('  ✓ No heartbeats to delete')

        # 4. Delete Idle Alerts
        self.stdout.write('Deleting idle alerts...')
        idle_alert_count = IdleAlert.objects.count()
        if idle_alert_count > 0:
            IdleAlert.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {idle_alert_count} idle alerts')
        else:
            self.stdout.write('  ✓ No idle alerts to delete')

        # 5. Delete Device User Binds
        self.stdout.write('Deleting device-user bindings...')
        bind_count = DeviceUserBind.objects.count()
        if bind_count > 0:
            DeviceUserBind.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {bind_count} device-user bindings')
        else:
            self.stdout.write('  ✓ No device-user bindings to delete')

        # 6. Delete Sessions (handle schema mismatch gracefully)
        self.stdout.write('Deleting sessions...')
        try:
            # Try to get count first (without ordering)
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM monitoring_session")
                session_count = cursor.fetchone()[0]
            
            if session_count > 0:
                # Use raw SQL to delete to avoid ordering issues
                try:
                    Session.objects.all().delete()
                    self.stdout.write(f'  ✓ Deleted {session_count} sessions')
                except Exception as e:
                    # If there's a schema mismatch, use raw SQL deletion
                    if 'created_at' in str(e) or 'Unknown column' in str(e):
                        self.stdout.write(self.style.WARNING('  ⚠ Schema mismatch detected, using raw SQL...'))
                        with connection.cursor() as cursor:
                            cursor.execute("DELETE FROM monitoring_session")
                            deleted_count = cursor.rowcount
                            self.stdout.write(f'  ✓ Deleted {deleted_count} sessions (via raw SQL)')
                    else:
                        raise
            else:
                self.stdout.write('  ✓ No sessions to delete')
        except Exception as e:
            # Fallback: try raw SQL if anything fails
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM monitoring_session")
                    deleted_count = cursor.rowcount
                    self.stdout.write(f'  ✓ Deleted {deleted_count} sessions (via raw SQL fallback)')
            except Exception as sql_error:
                self.stdout.write(self.style.WARNING(f'  ⚠ Could not delete sessions: {sql_error}'))
                logger.warning(f"Failed to delete sessions: {sql_error}")

        # 7. Delete Device Tokens
        self.stdout.write('Deleting device tokens...')
        token_count = DeviceToken.objects.count()
        if token_count > 0:
            DeviceToken.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {token_count} device tokens')
        else:
            self.stdout.write('  ✓ No device tokens to delete')

        # 8. Delete Devices (if not keeping)
        if not keep_devices:
            self.stdout.write('Deleting devices...')
            # Use raw SQL to avoid Session model ordering issues when Django checks related objects
            from django.db import connection
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM monitoring_device")
                    device_count = cursor.fetchone()[0]
                
                if device_count > 0:
                    # Delete using raw SQL to avoid ORM issues with related models
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM monitoring_device")
                        deleted_count = cursor.rowcount
                        self.stdout.write(f'  ✓ Deleted {deleted_count} devices (via raw SQL)')
                else:
                    self.stdout.write('  ✓ No devices to delete')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Failed to delete devices: {e}'))
                logger.error(f"Failed to delete devices: {e}")
                raise
        else:
            self.stdout.write('  ⚠ Keeping device records (as requested)')
            # Reset device status using raw SQL to avoid Session model issues
            from django.db import connection
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE monitoring_device 
                        SET status = 'OFFLINE',
                            last_heartbeat = NULL,
                            current_user_id = NULL,
                            current_user_name = NULL,
                            current_user_role = NULL,
                            last_user_bind_at = NULL
                    """)
                    updated_count = cursor.rowcount
                    self.stdout.write(f'  ✓ Reset {updated_count} device statuses (via raw SQL)')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Could not reset device statuses: {e}'))
                logger.warning(f"Failed to reset device statuses: {e}")

        # 9. Delete Orgs (only if no devices reference them)
        if not keep_devices:
            self.stdout.write('Deleting organizations...')
            org_count = Org.objects.count()
            if org_count > 0:
                Org.objects.all().delete()
                self.stdout.write(f'  ✓ Deleted {org_count} organizations')
            else:
                self.stdout.write('  ✓ No organizations to delete')

        # 10. Delete Legacy Employee Data
        self.stdout.write('Deleting legacy employee monitoring data...')
        
        # Employee Assets
        asset_count = EmployeeAsset.objects.count()
        if asset_count > 0:
            EmployeeAsset.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {asset_count} employee assets')
        
        # Employee Activities
        activity_count = EmployeeActivity.objects.count()
        if activity_count > 0:
            EmployeeActivity.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {activity_count} employee activities')
        
        # Employee Summaries
        summary_count = EmployeeSummary.objects.count()
        if summary_count > 0:
            EmployeeSummary.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {summary_count} employee summaries')
        
        # Employees (only monitoring-related fields, not the full employee record)
        employee_count = Employee.objects.count()
        if employee_count > 0:
            Employee.objects.all().update(
                status='offline',
                last_screenshot_at=None,
                productivity=0.0
            )
            self.stdout.write(f'  ✓ Reset monitoring data for {employee_count} employees')
        else:
            self.stdout.write('  ✓ No employee records to update')

        # 11. Clean up storage directories (if local storage)
        if not keep_files:
            self.stdout.write('Cleaning up storage directories...')
            self.cleanup_storage_directories()

    def delete_recording_files(self, recordings):
        """Delete recording files from storage"""
        storage = get_storage()
        deleted_count = 0
        error_count = 0

        for recording in recordings:
            try:
                # Delete video file
                if recording.blob_key:
                    if delete_storage_file(storage, recording.blob_key):
                        deleted_count += 1
                    else:
                        error_count += 1

                # Delete thumbnail
                if recording.thumb_key:
                    if delete_storage_file(storage, recording.thumb_key):
                        deleted_count += 1
                    else:
                        error_count += 1

            except Exception as e:
                logger.error(f"Error processing recording {recording.id}: {e}")
                error_count += 1

        if deleted_count > 0:
            self.stdout.write(f'  ✓ Deleted {deleted_count} recording files')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ {error_count} files could not be deleted'))

    def delete_segment_files(self, segments):
        """Delete recording segment files from storage"""
        storage = get_storage()
        deleted_count = 0
        error_count = 0

        for segment in segments:
            try:
                if segment.segment_path:
                    if delete_storage_file(storage, segment.segment_path):
                        deleted_count += 1
                    else:
                        error_count += 1
            except Exception as e:
                logger.error(f"Error processing segment {segment.id}: {e}")
                error_count += 1

        if deleted_count > 0:
            self.stdout.write(f'  ✓ Deleted {deleted_count} segment files')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠ {error_count} files could not be deleted'))

    def cleanup_storage_directories(self):
        """Clean up storage directories for local storage"""
        storage_driver = getattr(settings, 'STORAGE_DRIVER', 'local')
        
        if storage_driver == 'local':
            storage_path = getattr(settings, 'MONITORING_STORAGE_PATH', '/var/app/data')
            
            if os.path.exists(storage_path):
                # Delete monitoring-related directories
                dirs_to_clean = ['recordings', 'segments', 'thumbs', 'screenshots']
                files_deleted = 0
                
                for dir_name in dirs_to_clean:
                    dir_path = os.path.join(storage_path, dir_name)
                    if os.path.exists(dir_path):
                        try:
                            for root, dirs, files in os.walk(dir_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    try:
                                        os.remove(file_path)
                                        files_deleted += 1
                                    except Exception as e:
                                        logger.warning(f"Failed to delete {file_path}: {e}")
                            
                            # Remove empty directories
                            for root, dirs, files in os.walk(dir_path, topdown=False):
                                for dir_name in dirs:
                                    try:
                                        os.rmdir(os.path.join(root, dir_name))
                                    except:
                                        pass
                            
                            # Remove the main directory if empty
                            try:
                                os.rmdir(dir_path)
                            except:
                                pass
                                
                        except Exception as e:
                            logger.warning(f"Error cleaning directory {dir_path}: {e}")
                
                if files_deleted > 0:
                    self.stdout.write(f'  ✓ Deleted {files_deleted} files from storage')
                else:
                    self.stdout.write('  ✓ Storage directories cleaned (no files found)')
            else:
                self.stdout.write(f'  ⚠ Storage path {storage_path} does not exist')
        else:
            self.stdout.write(f'  ⚠ Storage driver is {storage_driver}, skipping local cleanup')

