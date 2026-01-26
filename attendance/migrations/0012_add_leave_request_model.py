# Generated manually to add LeaveRequest model
# Modified to safely handle existing tables

from django.conf import settings
from django.db import migrations, models
from app.common.safe_migrations import SafeCreateModel, SafeAddIndex
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0011_add_holiday_model'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        SafeCreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[('full_day', 'Full Day'), ('partial_day', 'Partial Day'), ('multiple_days', 'Multiple Days')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, help_text='Required for multiple days, optional for single day', null=True)),
                ('start_time', models.TimeField(blank=True, help_text='Required for partial-day leave', null=True)),
                ('end_time', models.TimeField(blank=True, help_text='Optional for partial-day leave', null=True)),
                ('hours', models.DecimalField(blank=True, decimal_places=2, help_text='Leave hours for partial-day leave', max_digits=5, null=True)),
                ('reason', models.TextField(help_text='Mandatory reason for leave')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('is_paid', models.BooleanField(default=False, help_text='Whether this leave is paid (set by admin)')),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to=settings.AUTH_USER_MODEL)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leave_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        SafeAddIndex(
            model_name='leaverequest',
            index=models.Index(fields=['employee', 'status'], name='attendance_leaverequest_employee_status_idx'),
        ),
        SafeAddIndex(
            model_name='leaverequest',
            index=models.Index(fields=['start_date', 'end_date'], name='attendance_leaverequest_start_date_end_date_idx'),
        ),
        SafeAddIndex(
            model_name='leaverequest',
            index=models.Index(fields=['status'], name='attendance_leaverequest_status_idx'),
        ),
    ]

