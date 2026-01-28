# Generated manually to fix IntegrityError with Quotation.id

from django.db import migrations, models
from app.common.safe_migrations import SafeAlterField


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_add_custom_requirements'),
    ]

    operations = [
        SafeAlterField(
            model_name='quotation',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
