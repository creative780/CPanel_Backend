# Generated migration for adding deduction fields to AttendanceRule

from django.db import migrations, models
from app.common.safe_migrations import SafeAddField


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0013_rename_leave_indexes'),
    ]

    operations = [
        SafeAddField(
            model_name='attendancerule',
            name='grace_violation_deduction',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Fixed deduction amount when employee checks in after grace period',
                max_digits=8
            ),
        ),
        SafeAddField(
            model_name='attendancerule',
            name='early_checkout_threshold_minutes',
            field=models.PositiveIntegerField(
                default=20,
                help_text='Threshold in minutes before work_end to consider check-out as early'
            ),
        ),
        SafeAddField(
            model_name='attendancerule',
            name='early_checkout_deduction',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Fixed deduction amount for early check-out',
                max_digits=8
            ),
        ),
    ]

