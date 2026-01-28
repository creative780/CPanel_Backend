# Generated manually to add Holiday model
# Modified to safely handle existing tables

from django.db import migrations, models
from app.common.safe_migrations import SafeCreateModel


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0010_merge_0005_0009'),
    ]

    operations = [
        SafeCreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Date of the holiday', unique=True)),
                ('name', models.CharField(help_text='Name/description of the holiday', max_length=255)),
                ('is_recurring', models.BooleanField(default=False, help_text='Whether this holiday recurs annually (for future use)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Holiday',
                'verbose_name_plural': 'Holidays',
                'ordering': ['date'],
            },
        ),
    ]

