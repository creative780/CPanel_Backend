# Generated manually for profile tagging system

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0030_add_order_channel_field'),
        ('clients', '0002_add_profile_tag_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='client',
            field=models.ForeignKey(blank=True, help_text='Linked client for profile tagging', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='clients.client'),
        ),
    ]

