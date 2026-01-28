# Generated manually for profile tagging system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='profile_tag',
            field=models.CharField(blank=True, choices=[('b2b', 'B2B'), ('b2c', 'B2C'), ('walk_in', 'Walk-In'), ('online', 'Online')], help_text='Customer profile tag (B2B, B2C, Walk-In, Online)', max_length=20, null=True),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['profile_tag'], name='clients_cli_profile_idx'),
        ),
    ]

