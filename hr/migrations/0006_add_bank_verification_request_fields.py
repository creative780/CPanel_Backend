# Generated manually for bank verification request workflow

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0005_alter_otpverification_delivery_method_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='employeebankdetails',
            name='verification_requested_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employeebankdetails',
            name='rejection_reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='employeebankdetails',
            name='rejected_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rejected_banks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='employeebankdetails',
            name='rejected_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employeebankdetails',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('verification_requested', 'Verification Requested'), ('verified', 'Verified'), ('rejected', 'Rejected')], default='pending', max_length=25),
        ),
    ]

