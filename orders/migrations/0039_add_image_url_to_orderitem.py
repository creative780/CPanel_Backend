# Generated migration to add image_url field to OrderItem

from django.db import migrations, models
from app.common.safe_migrations import SafeAddField


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0038_add_reprint_tracking'),
    ]

    operations = [
        SafeAddField(
            model_name='orderitem',
            name='image_url',
            field=models.URLField(blank=True, null=True, help_text='Product image URL for display in order details'),
        ),
    ]

