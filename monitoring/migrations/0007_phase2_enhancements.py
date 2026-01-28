# Generated manually for Phase 2 enhancements
# Modified to safely handle duplicate columns

from django.db import migrations, models
from app.common.safe_migrations import SafeAddField, SafeCreateModel, SafeAddIndex


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0006_remove_unused_models'),
    ]

    operations = [
        # Add Phase 2 fields to Heartbeat model
        SafeAddField(
            model_name='heartbeat',
            name='keystroke_count',
            field=models.IntegerField(default=0),
        ),
        SafeAddField(
            model_name='heartbeat',
            name='mouse_click_count',
            field=models.IntegerField(default=0),
        ),
        SafeAddField(
            model_name='heartbeat',
            name='productivity_score',
            field=models.FloatField(default=0.0),
        ),
        SafeAddField(
            model_name='heartbeat',
            name='keystroke_rate_per_minute',
            field=models.FloatField(default=0.0),
        ),
        SafeAddField(
            model_name='heartbeat',
            name='click_rate_per_minute',
            field=models.FloatField(default=0.0),
        ),
        SafeAddField(
            model_name='heartbeat',
            name='active_time_minutes',
            field=models.FloatField(default=0.0),
        ),
        SafeAddField(
            model_name='heartbeat',
            name='session_duration_minutes',
            field=models.FloatField(default=0.0),
        ),
        SafeAddField(
            model_name='heartbeat',
            name='top_applications',
            field=models.JSONField(blank=True, default=dict),
        ),
        SafeAddField(
            model_name='heartbeat',
            name='idle_alert',
            field=models.BooleanField(default=False),
        ),
        # Create IdleAlert model
        SafeCreateModel(
            name='IdleAlert',
            fields=[
                ('id', models.CharField(default='sess_', max_length=25, primary_key=True, serialize=False)),
                ('idle_duration_minutes', models.IntegerField()),
                ('alert_sent_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('is_resolved', models.BooleanField(default=False)),
                ('device', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='idle_alerts', to='monitoring.device')),
            ],
            options={
                'ordering': ['-alert_sent_at'],
            },
        ),
        SafeAddIndex(
            model_name='idlealert',
            index=models.Index(fields=['device', 'alert_sent_at'], name='monitoring_i_device__f8a8b4_idx'),
        ),
        SafeAddIndex(
            model_name='idlealert',
            index=models.Index(fields=['is_resolved'], name='monitoring_i_is_reso_8b2a8b_idx'),
        ),
    ]

