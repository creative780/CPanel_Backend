# Merge migration to resolve conflict between 0012_add_device_config_fields and 0016_merge_0012_0015
# Branch 1: 0001 -> ... -> 0011 -> 0012
# Branch 2: 0001 -> 0013 -> 0014 -> 0015 -> 0016
# Depend on 0001_initial and 0016 to work even if 0012 doesn't exist on production

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # Depend on 0016 which is the latest in branch 2
        # If 0012 exists, it will be applied before this merge
        # If 0012 doesn't exist, this merge still works
        ('monitoring', '0001_initial'),
        ('monitoring', '0016_merge_0012_0015'),
    ]

    operations = [
        # Empty merge migration - just resolves the conflict
    ]

