# Merge migration to resolve conflict between branches
# Branch 1 (if exists): 0001 -> ... -> 0007 -> 0009 -> 0010 -> 0011 -> 0012
# Branch 2: 0001 -> 0013 -> 0014 -> 0015
# 
# Depend on 0001_initial and 0015 to work even if 0012 doesn't exist on production.
# If 0012 exists, it will be applied before this merge (it's reachable from 0001).
# If 0012 doesn't exist, this merge just merges 0001 and 0015, which is fine.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial (always exists) and 0015 (latest in branch 2)
        # This ensures the merge works on production even if 0012 doesn't exist
        ('monitoring', '0001_initial'),
        ('monitoring', '0015_remove_device_monitoring__user_id_2d8a6f_idx_and_more'),
    ]

    operations = [
    ]

