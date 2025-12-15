# Generated manually to create ProductCards table

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_backend_final', '0008_add_slug_to_productseo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCards',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card1_title', models.CharField(blank=True, default='', max_length=255)),
                ('card1', models.TextField(blank=True, default='')),
                ('card2_title', models.CharField(blank=True, default='', max_length=255)),
                ('card2', models.TextField(blank=True, default='')),
                ('card3_title', models.CharField(blank=True, default='', max_length=255)),
                ('card3', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='admin_backend_final.product')),
            ],
        ),
    ]

