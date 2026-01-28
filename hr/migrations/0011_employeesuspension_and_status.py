# Generated manually for EmployeeSuspension model and status update

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0010_add_address_proof_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='hremployee',
            name='status',
            field=models.CharField(choices=[('Active', 'Active'), ('On Leave', 'On Leave'), ('Inactive', 'Inactive'), ('Suspended', 'Suspended')], default='Active', max_length=20),
        ),
        migrations.CreateModel(
            name='EmployeeSuspension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(help_text='Reason for suspension')),
                ('expiry_date', models.DateTimeField(help_text='Date and time when suspension should automatically end')),
                ('remarks', models.TextField(blank=True, help_text='Additional remarks or notes')),
                ('suspended_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, help_text='When suspension was ended (manually or automatically)', null=True)),
                ('is_active', models.BooleanField(default=True, help_text='True if suspension is currently active')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suspensions', to='hr.hremployee')),
                ('ended_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ended_suspensions', to=settings.AUTH_USER_MODEL)),
                ('suspended_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='suspended_employees', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-suspended_at'],
            },
        ),
        migrations.AddIndex(
            model_name='employeesuspension',
            index=models.Index(fields=['employee', 'is_active'], name='hr_employees_employee_idx'),
        ),
        migrations.AddIndex(
            model_name='employeesuspension',
            index=models.Index(fields=['expiry_date', 'is_active'], name='hr_employees_expiry_d_idx'),
        ),
        migrations.AddIndex(
            model_name='employeesuspension',
            index=models.Index(fields=['is_active'], name='hr_employees_is_acti_idx'),
        ),
    ]

