# Generated manually for order management enhancements
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0036_order_channel'),
    ]

    operations = [
        # Add sample_approval_required to Order
        migrations.AddField(
            model_name='order',
            name='sample_approval_required',
            field=models.BooleanField(default=False, help_text='Whether sample approval is required for this order'),
        ),
        # Make unit_price nullable in OrderItem
        migrations.AlterField(
            model_name='orderitem',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, help_text='Unit price - can be null if not set', max_digits=12, null=True, blank=True),
        ),
        # Add printing_technique and colors_in_print to PrintingStage
        migrations.AddField(
            model_name='printingstage',
            name='printing_technique',
            field=models.CharField(blank=True, choices=[('digital', 'Digital Printing'), ('offset', 'Offset Printing'), ('screen', 'Screen Printing')], help_text='Printing technique used', max_length=50),
        ),
        migrations.AddField(
            model_name='printingstage',
            name='colors_in_print',
            field=models.CharField(blank=True, help_text='Colors used in print', max_length=255),
        ),
        # Make rider_photo_path nullable before adding new fields (SQLite table recreation fix)
        migrations.AlterField(
            model_name='deliverystage',
            name='rider_photo_path',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        # Add delivery_option and expected_delivery_date to DeliveryStage
        migrations.AddField(
            model_name='deliverystage',
            name='delivery_option',
            field=models.CharField(blank=True, choices=[('pickup', 'Pickup'), ('home_office', 'Home/Office Delivery'), ('courier', 'Courier')], help_text='Delivery method', max_length=50),
        ),
        migrations.AddField(
            model_name='deliverystage',
            name='expected_delivery_date',
            field=models.DateField(blank=True, help_text='Expected date of delivery', null=True),
        ),
    ]

