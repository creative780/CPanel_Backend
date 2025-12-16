# Generated manually to create ProductCards table

from django.db import migrations, models
import django.db.models.deletion


def create_productcards_if_not_exist(apps, schema_editor):
    """Safely create ProductCards table if it doesn't exist in the database"""
    # Since ProductCards already exists in 0001_initial, we skip creating it
    # This function is mainly for databases that were created before 0001_initial
    # For SQLite, we skip entirely to avoid issues
    if schema_editor.connection.vendor == 'sqlite':
        return
    
    # For PostgreSQL/MySQL, the table should already exist from 0001_initial
    # So we don't need to do anything here
    pass


def noop_reverse(apps, schema_editor):
    """No-op reverse migration"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('admin_backend_final', '0008_add_slug_to_productseo'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # Skip creating table since it already exists in 0001_initial
                migrations.RunPython(create_productcards_if_not_exist, noop_reverse),
            ],
            state_operations=[
                # Don't try to create model in state since 0001_initial already has it
                # This prevents "table already exists" errors
            ],
        ),
    ]

