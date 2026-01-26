# Generated manually for EmployeeSalaryExemption model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0011_employeesuspension_and_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeSalaryExemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exemption_type', models.CharField(choices=[('Temporary', 'Temporary'), ('Permanent', 'Permanent')], max_length=20)),
                ('reason', models.TextField(help_text='Reason for exemption')),
                ('expiry_date', models.DateTimeField(blank=True, help_text='Expiry date (required for temporary exemptions, not applicable for permanent)', null=True)),
                ('remarks', models.TextField(blank=True, help_text='Additional remarks or notes')),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, help_text='When exemption was ended (manually or automatically)', null=True)),
                ('is_active', models.BooleanField(default=True, help_text='True if exemption is currently active')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary_exemptions', to='hr.hremployee')),
                ('ended_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ended_salary_exemptions', to=settings.AUTH_USER_MODEL)),
                ('granted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_salary_exemptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-granted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='employeesalaryexemption',
            index=models.Index(fields=['employee', 'is_active'], name='hr_empsalaryex_employee_idx'),
        ),
        migrations.AddIndex(
            model_name='employeesalaryexemption',
            index=models.Index(fields=['exemption_type', 'is_active'], name='hr_empsalaryex_exempti_idx'),
        ),
        migrations.AddIndex(
            model_name='employeesalaryexemption',
            index=models.Index(fields=['expiry_date', 'is_active'], name='hr_empsalaryex_expiry_d_idx'),
        ),
        migrations.AddIndex(
            model_name='employeesalaryexemption',
            index=models.Index(fields=['is_active'], name='hr_empsalaryex_is_acti_idx'),
        ),
    ]

