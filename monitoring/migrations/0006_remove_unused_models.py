# Generated manually to fix migration issues

from django.db import migrations
from app.common.safe_migrations import SafeRemoveField, SafeDeleteModel


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0005_heartbeat_activity_score_heartbeat_click_rate_and_more'),
    ]

    operations = [
        # Remove fields that were added in 0005 but don't exist in current models
        SafeRemoveField(
            model_name='heartbeat',
            name='activity_score',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='click_rate',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='idle_duration',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='is_idle',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='keystroke_rate',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='keystrokes',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='mouse_clicks',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='productivity_reason',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='productivity_status',
        ),
        SafeRemoveField(
            model_name='heartbeat',
            name='scroll_events',
        ),
        SafeRemoveField(
            model_name='screenshot',
            name='active_window_snapshot',
        ),
        # Remove models that were created in 0004 but don't exist in current models
        SafeDeleteModel(
            name='AnalyticsReport',
        ),
        SafeDeleteModel(
            name='ApplicationUsage',
        ),
        SafeDeleteModel(
            name='ProductivityAlert',
        ),
        SafeDeleteModel(
            name='ProductivityMetric',
        ),
        SafeDeleteModel(
            name='UserActivitySession',
        ),
    ]
