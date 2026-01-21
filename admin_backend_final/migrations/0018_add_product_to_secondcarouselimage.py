# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_backend_final', '0015_merge_20251216_0441'),
    ]

    operations = [
        migrations.AddField(
            model_name='secondcarouselimage',
            name='product',
            field=models.ForeignKey(blank=True, db_column='product_id', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='second_carousel_images', to='admin_backend_final.product', to_field='product_id'),
        ),
    ]

