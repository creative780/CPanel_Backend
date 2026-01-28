# Generated manually for HREmployee model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HREmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(unique=True)),
                ('phone', models.CharField(blank=True, max_length=32)),
                ('image', models.CharField(blank=True, max_length=500)),
                ('salary', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('designation', models.CharField(blank=True, max_length=120)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('On Leave', 'On Leave'), ('Inactive', 'Inactive')], default='Active', max_length=20)),
                ('branch', models.CharField(choices=[('dubai', 'Dubai'), ('pakistan', 'Pakistan')], default='dubai', max_length=20)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('sales', 'Sales'), ('designer', 'Designer'), ('production', 'Production'), ('delivery', 'Delivery'), ('finance', 'Finance')], default='sales', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hr_employee', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
