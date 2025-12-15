# Generated manually to fix missing CartItem columns

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('admin_backend_final', '0006_favorite'),
    ]

    # This migration originally added fields that are already present in
    # the CartItem model as defined in 0001_initial, which caused
    # \"duplicate column\" errors when running migrations on a fresh DB
    # (especially in tests). It is now a no-op to keep the migration
    # history consistent without changing the schema.
    operations = []

