# Generated manually to fix column name mismatch
# Updated to use SafeRenameField to handle missing model gracefully

from django.db import migrations
from app.common.safe_migrations import SafeRenameField


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # If 0014 exists, it will be applied before this migration
        ('orders', '0001_initial'),
    ]

    operations = [
        SafeRenameField(
            model_name='designapproval',
            old_name='responded_at',
            new_name='reviewed_at',
        ),
    ]
