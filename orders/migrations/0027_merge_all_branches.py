# Comprehensive merge migration to resolve all conflicting branches
# This migration merges all leaf nodes that depend on 0001_initial.
# Since we don't know which migrations exist in production, we depend only on
# 0001_initial and the latest merge migration (0026) if it exists.
# All other migrations (0010-0015) have been updated to depend on 0001_initial,
# so they can be applied independently if they exist.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        ('orders', '0001_initial'),
        # Depend on all leaf nodes to merge them
        # IMPORTANT: All these migration files must exist in production
        # If a migration file doesn't exist, Django will fail to build the graph
        # In that case, you need to either:
        # 1. Copy the missing migration file to production, or
        # 2. Fake-apply it: python manage.py migrate orders <migration_name> --fake
        ('orders', '0010_add_design_fields_to_orderitem'),
        ('orders', '0011_fix_delivery_stage_id_field'),
        ('orders', '0012_fix_delivery_stage_id_with_sql'),
        ('orders', '0013_fix_field_conflicts'),
        ('orders', '0014_rename_quantity_to_product_quantity'),
        ('orders', '0015_fix_designapproval_reviewed_at_field'),
        ('orders', '0026_merge_0015_0025'),
    ]

    operations = [
        # Empty merge migration - just resolves all conflicts
        # All migrations 0010-0015 now depend on 0001_initial, so they can be applied
        # independently. This migration serves as a final merge point.
    ]

