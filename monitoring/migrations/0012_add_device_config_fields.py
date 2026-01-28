# Generated manually to add device configuration fields
# Modified to safely handle duplicate columns

from django.db import migrations, models
from app.common.safe_migrations import SafeAddField


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # If 0011 exists, it will be applied before this migration
        ('monitoring', '0001_initial'),
    ]

    operations = [
        # Add configuration fields to Device model
        SafeAddField(
            model_name='device',
            name='screenshot_freq_sec',
            field=models.IntegerField(default=15),
        ),
        SafeAddField(
            model_name='device',
            name='heartbeat_freq_sec',
            field=models.IntegerField(default=20),
        ),
        SafeAddField(
            model_name='device',
            name='auto_start',
            field=models.BooleanField(default=True),
        ),
        SafeAddField(
            model_name='device',
            name='debug_mode',
            field=models.BooleanField(default=False),
        ),
        SafeAddField(
            model_name='device',
            name='pause_monitoring',
            field=models.BooleanField(default=False),
        ),
        SafeAddField(
            model_name='device',
            name='max_screenshot_storage_days',
            field=models.IntegerField(default=30),
        ),
        SafeAddField(
            model_name='device',
            name='keystroke_monitoring',
            field=models.BooleanField(default=True),
        ),
        SafeAddField(
            model_name='device',
            name='mouse_click_monitoring',
            field=models.BooleanField(default=True),
        ),
        SafeAddField(
            model_name='device',
            name='productivity_tracking',
            field=models.BooleanField(default=True),
        ),
        SafeAddField(
            model_name='device',
            name='idle_detection',
            field=models.BooleanField(default=True),
        ),
        SafeAddField(
            model_name='device',
            name='idle_threshold_minutes',
            field=models.IntegerField(default=30),
        ),
        SafeAddField(
            model_name='device',
            name='avg_productivity_score',
            field=models.FloatField(default=0.0),
        ),
    ]

