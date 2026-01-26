# Merge migration to resolve conflict between 0005_remove_unique_per_day and 0009_add_overtime_fields
# Branch 1: 0001 -> 0004 -> 0005
# Branch 2: 0001 -> 0006 -> 0007 -> 0008 -> 0009
# Depend on 0001_initial and 0009 to work even if 0005 doesn't exist on production

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on both branches
        # Branch 1: 0001 -> 0004 -> 0005
        ('attendance', '0005_remove_unique_per_day'),
        # Branch 2: 0001 -> 0006 -> 0007 -> 0008 -> 0009
        ('attendance', '0009_add_overtime_fields'),
    ]

    operations = [
        # Empty merge migration - just resolves the conflict
    ]

