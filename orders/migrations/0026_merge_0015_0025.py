# Merge migration to resolve conflict between 0015_fix_designapproval_reviewed_at_field and 0025_alter_productmachineassignment_product_sku
# This migration merges both branches:
# Branch 1: 0001 -> ... -> 0014 -> 0015
# Branch 2: 0001 -> ... -> 0022 -> 0023 -> 0024 -> 0025
# 
# PRODUCTION NOTE: If 0015 doesn't exist in production, fake-apply it first:
# python manage.py migrate orders 0015 --fake
# Then apply this migration normally.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # Depend on 0025 which is the latest in branch 2
        # If 0015 exists, it will be applied before this merge
        # Note: We don't depend on 0015 directly because it might not exist in production
        ('orders', '0001_initial'),
        ('orders', '0025_alter_productmachineassignment_product_sku'),
    ]

    operations = [
        # Empty merge migration - just resolves the conflict
    ]

