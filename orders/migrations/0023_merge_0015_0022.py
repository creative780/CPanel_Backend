# Merge migration to resolve conflict between 0015_fix_designapproval_reviewed_at_field and 0022_merge_0016_0021
# Branch 1: 0001 -> ... -> 0014 -> 0015
# Branch 2: 0001 -> ... -> 0016 -> 0021 -> 0022
# This migration should work even if 0015 doesn't exist in production
# It depends on 0014 (parent of 0015) and 0022 (latest in branch 2)
# If 0015 exists, it will be applied before this merge since it's in the same branch

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # Depend on 0022 which is the latest in branch 2
        # If 0015 exists, it will be applied before this merge
        ('orders', '0001_initial'),
        ('orders', '0022_merge_0016_0021'),
    ]

    operations = [
        # Empty merge migration - just resolves the conflict
        # This migration is safe to apply even if 0015 doesn't exist
    ]

