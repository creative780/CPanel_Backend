from django.db import migrations


class Migration(migrations.Migration):
    # Merge migration to resolve conflict between branches
    # Branch 1 (if exists): 0001 -> 0002 -> 0003 -> 0005
    # Branch 2: 0001 -> 0006
    # 
    # Depend on 0001_initial (always exists) and 0006 to work even if 0005 doesn't exist on production.
    # If 0005 exists, it will be applied before this merge since it's in the chain from 0001.
    # If 0005 doesn't exist, this merge just merges 0001 and 0006, which is fine.

    dependencies = [
        ('activity_log', '0001_initial'),
        ('activity_log', '0006_alter_activityevent_actor_role_and_more'),
    ]

    operations = [
    ]

