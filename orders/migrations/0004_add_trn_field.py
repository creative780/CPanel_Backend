# Generated manually to add trn field
# Modified to safely handle duplicate columns

from django.db import migrations, models
from app.common.safe_migrations import SafeAddField


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_pricing_status_quotation_custom_field_and_more'),
    ]

    operations = [
        SafeAddField(
            model_name='order',
            name='trn',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
