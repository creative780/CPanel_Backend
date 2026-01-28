# Generated manually to fix Django migration conflicts
# Fixes field name conflicts for session.created_at and designapproval.responded_at

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # This migration is a no-op, so it's safe to apply even if intermediate migrations don't exist
        ('orders', '0001_initial'),
    ]

    operations = [
        # We're not making any changes - this migration is to resolve conflicts
        # The fields are already properly named in the models
        migrations.RunPython(
            lambda apps, schema_editor: None,
            lambda apps, schema_editor: None
        ),
    ]

