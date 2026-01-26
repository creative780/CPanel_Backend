# Migration to fix Django's field rename detection
# Migration 0019 already renamed start_time->started_at and actual_completion_time->completed_at in the database
# This migration updates the migration state to reflect these renames and removes expected_completion_time

from django.db import migrations
from app.common.safe_migrations import SafeRenameField, SafeRemoveField


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # Depend on 0023 which is the merge migration
        # If ProductMachineAssignment model doesn't exist, SafeRenameField will skip gracefully
        ('orders', '0001_initial'),
        ('orders', '0023_merge_0015_0022'),
    ]

    operations = [
        # Update state to reflect renames that were already done in migration 0019
        # These operations update the migration state only - database changes were already applied
        SafeRenameField(
            model_name='productmachineassignment',
            old_name='start_time',
            new_name='started_at',
        ),
        SafeRenameField(
            model_name='productmachineassignment',
            old_name='actual_completion_time',
            new_name='completed_at',
        ),
        # Remove expected_completion_time field which is no longer in the model
        SafeRemoveField(
            model_name='productmachineassignment',
            name='expected_completion_time',
        ),
    ]

