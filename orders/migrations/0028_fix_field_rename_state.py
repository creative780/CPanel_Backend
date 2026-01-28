# Migration to fix Django's field rename detection
# Migrations 0015 and 0019/0024 already handled these renames in the database
# This migration updates the migration state to reflect these renames

from django.db import migrations
from app.common.safe_migrations import SafeRenameField


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # Also depend on the latest merge migration
        ('orders', '0001_initial'),
        ('orders', '0027_merge_all_branches'),
    ]

    operations = [
        # Update state to reflect renames that were already done in migrations 0015 and 0019/0024
        # These operations update the migration state only - database changes were already applied
        SafeRenameField(
            model_name='designapproval',
            old_name='responded_at',
            new_name='reviewed_at',
        ),
        SafeRenameField(
            model_name='productmachineassignment',
            old_name='actual_completion_time',
            new_name='completed_at',
        ),
    ]

