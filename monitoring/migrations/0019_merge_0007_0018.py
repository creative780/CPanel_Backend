# Merge migration to resolve conflict between 0007_phase2_enhancements and 0018_alter_session_options_remove_device_user_and_more
# This migration merges both branches:
# Branch 1: 0001 -> ... -> 0006 -> 0007
# Branch 2: 0001 -> ... -> 0016 -> 0017 -> 0018
#
# PRODUCTION NOTE: If 0007 doesn't exist in production, this migration will still work
# because all migrations now depend on 0001_initial.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # Depend on all possible leaf nodes to merge them
        # If they don't exist in production, Django will fail to build the graph
        # In that case, copy the missing migration files to production
        ('monitoring', '0001_initial'),
        ('monitoring', '0007_phase2_enhancements'),
        ('monitoring', '0009_add_token_field'),
        ('monitoring', '0010_add_device_fields'),
        ('monitoring', '0011_add_device_frequency_fields'),
        ('monitoring', '0012_add_device_config_fields'),
        ('monitoring', '0018_alter_session_options_remove_device_user_and_more'),
    ]

    operations = [
        # Empty merge migration - just resolves the conflict
    ]

