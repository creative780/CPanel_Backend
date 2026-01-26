# Generated migration for reprint tracking
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0037_add_order_management_enhancements'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_reprint',
            field=models.BooleanField(default=False, help_text='Whether this is a reprint order'),
        ),
        migrations.AddField(
            model_name='order',
            name='original_order',
            field=models.ForeignKey(blank=True, help_text='Original order if this is a reprint', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reprints', to='orders.order'),
        ),
    ]



























