# Merge migration to resolve conflict between 0005_alter_activitytype_role_scope_and_more and 0007_merge_0005_0006
# Branch 1: 0001 -> ... -> 0004 -> 0005
# Branch 2: 0001 -> ... -> 0006 -> 0007
# Depend on 0001_initial and 0007 to work even if 0005 doesn't exist on production

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on both branches
        # Branch 1: 0001 -> ... -> 0004 -> 0005
        ('activity_log', '0005_alter_activitytype_role_scope_and_more'),
        # Branch 2: 0001 -> ... -> 0006 -> 0007
        ('activity_log', '0007_merge_0005_0006'),
    ]

    operations = [
        # Empty merge migration - just resolves the conflict
    ]

