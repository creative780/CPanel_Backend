# Generated migration for adding scheduled_report to ExportJob

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity_log', '0011_alter_exportjob_format_alter_scheduledreport_format'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportjob',
            name='scheduled_report',
            field=models.ForeignKey(
                blank=True,
                help_text='The scheduled report that triggered this export (if any)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='export_jobs',
                to='activity_log.ScheduledReport'
            ),
        ),
    ]

