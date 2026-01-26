# Generated migration for Export & Reporting Features

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.fields.json


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activity_log', '0009_add_is_reviewed_field'),
    ]

    operations = [
        # Add PDF and XML to ExportFormat choices (model change only, no DB change needed)
        # The choices are handled at Python level, so we just need to create the ScheduledReport model
        
        migrations.CreateModel(
            name='ScheduledReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('schedule_type', models.CharField(choices=[('DAILY', 'Daily'), ('WEEKLY', 'Weekly')], max_length=16)),
                ('schedule_time', models.TimeField()),
                ('schedule_day', models.IntegerField(blank=True, help_text='For weekly: 0=Monday, 6=Sunday', null=True)),
                ('recipients', django.db.models.fields.json.JSONField(default=list, help_text='List of email addresses')),
                ('format', models.CharField(choices=[('CSV', 'CSV'), ('NDJSON', 'NDJSON'), ('PDF', 'PDF'), ('XML', 'XML')], max_length=16)),
                ('filters_json', django.db.models.fields.json.JSONField(default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('last_run', models.DateTimeField(blank=True, null=True)),
                ('next_run', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'scheduled_report',
                'ordering': ['-created_at'],
            },
        ),
    ]














































