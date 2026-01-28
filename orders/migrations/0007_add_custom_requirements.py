# Generated manually for custom requirements field
# Modified to safely handle duplicate columns

from django.db import migrations, models
from app.common.safe_migrations import SafeAddField


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_add_workflow_models'),
    ]

    operations = [
        SafeAddField(
            model_name='orderitem',
            name='custom_requirements',
            field=models.TextField(blank=True, help_text='Custom design requirements for this product', null=True),
        ),
    ]
