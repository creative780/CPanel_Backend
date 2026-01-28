# Generated manually to add missing device fields
# Modified to safely handle duplicate columns

from django.db import migrations, models
from app.common.safe_migrations import SafeAddField
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # If 0009 exists, it will be applied before this migration
        ('monitoring', '0001_initial'),
    ]

    operations = [
        # Add missing fields to Device model
        SafeAddField(
            model_name='device',
            name='last_seen',
            field=models.DateTimeField(auto_now=True),
        ),
        SafeAddField(
            model_name='device',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        SafeAddField(
            model_name='device',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        SafeAddField(
            model_name='device',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]


