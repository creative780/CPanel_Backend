# Generated manually to fix DeliveryStage id field

from django.db import migrations, models
from app.common.safe_migrations import SafeAlterField


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # If 0010 exists, it will be applied before this migration
        ('orders', '0001_initial'),
    ]

    operations = [
        # Fix DeliveryStage id field to be properly auto-incrementing
        SafeAlterField(
            model_name='deliverystage',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        
        # Fix ApprovalStage id field to be consistent with the original migration
        SafeAlterField(
            model_name='approvalstage', 
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]

