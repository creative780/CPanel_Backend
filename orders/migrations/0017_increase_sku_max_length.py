# Generated migration to increase SKU field max_length from 100 to 255
# Independent migration that works regardless of intermediate migration state
# Supports both MySQL and PostgreSQL database backends

from django.db import migrations, models
from app.common.safe_migrations import SafeAlterField


def increase_sku_length(apps, schema_editor):
    """
    Increase SKU field max_length from 100 to 255.
    Works directly on the database without depending on migration history.
    Supports both MySQL and PostgreSQL.
    """
    db_vendor = schema_editor.connection.vendor
    
    def check_table_exists(cursor, table_name, db_vendor):
        """Check if a table exists in the database"""
        if db_vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, [table_name])
            return cursor.fetchone()[0]
        elif db_vendor == 'mysql':
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            """, [table_name])
            return cursor.fetchone()[0] > 0
        return False
    
    def check_column_exists(cursor, table_name, column_name, db_vendor):
        """Check if a column exists in a table"""
        if db_vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s 
                    AND column_name = %s
                )
            """, [table_name, column_name])
            return cursor.fetchone()[0]
        elif db_vendor == 'mysql':
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = %s 
                AND column_name = %s
            """, [table_name, column_name])
            return cursor.fetchone()[0] > 0
        return False
    
    with schema_editor.connection.cursor() as cursor:
        # For orders_orderitem.sku
        if check_table_exists(cursor, 'orders_orderitem', db_vendor):
            if check_column_exists(cursor, 'orders_orderitem', 'sku', db_vendor):
                try:
                    if db_vendor == 'postgresql':
                        # Use savepoint to handle errors gracefully
                        cursor.execute("SAVEPOINT sp_alter_orderitem_sku")
                        try:
                            cursor.execute("""
                                ALTER TABLE orders_orderitem 
                                ALTER COLUMN sku TYPE VARCHAR(255)
                            """)
                            cursor.execute("RELEASE SAVEPOINT sp_alter_orderitem_sku")
                        except Exception as e:
                            cursor.execute("ROLLBACK TO SAVEPOINT sp_alter_orderitem_sku")
                            print(f"Note: Could not alter orders_orderitem.sku: {e}")
                    elif db_vendor == 'mysql':
                        cursor.execute("""
                            ALTER TABLE orders_orderitem 
                            MODIFY COLUMN sku VARCHAR(255) NULL
                        """)
                except Exception as e:
                    print(f"Note: Could not alter orders_orderitem.sku: {e}")
        
        # For orders_productmachineassignment.product_sku
        if check_table_exists(cursor, 'orders_productmachineassignment', db_vendor):
            if check_column_exists(cursor, 'orders_productmachineassignment', 'product_sku', db_vendor):
                try:
                    if db_vendor == 'postgresql':
                        # Use savepoint to handle errors gracefully
                        cursor.execute("SAVEPOINT sp_alter_pma_sku")
                        try:
                            cursor.execute("""
                                ALTER TABLE orders_productmachineassignment 
                                ALTER COLUMN product_sku TYPE VARCHAR(255)
                            """)
                            cursor.execute("RELEASE SAVEPOINT sp_alter_pma_sku")
                        except Exception as e:
                            cursor.execute("ROLLBACK TO SAVEPOINT sp_alter_pma_sku")
                            print(f"Note: Could not alter orders_productmachineassignment.product_sku: {e}")
                    elif db_vendor == 'mysql':
                        cursor.execute("""
                            ALTER TABLE orders_productmachineassignment 
                            MODIFY COLUMN product_sku VARCHAR(255)
                        """)
                except Exception as e:
                    print(f"Note: Could not alter orders_productmachineassignment.product_sku: {e}")


def reverse_increase_sku_length(apps, schema_editor):
    """
    Reverse operation: decrease SKU field back to 100 (for rollback)
    """
    db_vendor = schema_editor.connection.vendor
    
    def check_table_exists(cursor, table_name, db_vendor):
        """Check if a table exists in the database"""
        if db_vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, [table_name])
            return cursor.fetchone()[0]
        elif db_vendor == 'mysql':
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            """, [table_name])
            return cursor.fetchone()[0] > 0
        return False
    
    def check_column_exists(cursor, table_name, column_name, db_vendor):
        """Check if a column exists in a table"""
        if db_vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s 
                    AND column_name = %s
                )
            """, [table_name, column_name])
            return cursor.fetchone()[0]
        elif db_vendor == 'mysql':
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = %s 
                AND column_name = %s
            """, [table_name, column_name])
            return cursor.fetchone()[0] > 0
        return False
    
    with schema_editor.connection.cursor() as cursor:
        # For orders_orderitem.sku
        if check_table_exists(cursor, 'orders_orderitem', db_vendor):
            if check_column_exists(cursor, 'orders_orderitem', 'sku', db_vendor):
                try:
                    if db_vendor == 'postgresql':
                        cursor.execute("SAVEPOINT sp_reverse_orderitem_sku")
                        try:
                            cursor.execute("""
                                ALTER TABLE orders_orderitem 
                                ALTER COLUMN sku TYPE VARCHAR(100)
                            """)
                            cursor.execute("RELEASE SAVEPOINT sp_reverse_orderitem_sku")
                        except Exception:
                            cursor.execute("ROLLBACK TO SAVEPOINT sp_reverse_orderitem_sku")
                    elif db_vendor == 'mysql':
                        cursor.execute("""
                            ALTER TABLE orders_orderitem 
                            MODIFY COLUMN sku VARCHAR(100) NULL
                        """)
                except Exception:
                    pass
        
        # For orders_productmachineassignment.product_sku
        if check_table_exists(cursor, 'orders_productmachineassignment', db_vendor):
            if check_column_exists(cursor, 'orders_productmachineassignment', 'product_sku', db_vendor):
                try:
                    if db_vendor == 'postgresql':
                        cursor.execute("SAVEPOINT sp_reverse_pma_sku")
                        try:
                            cursor.execute("""
                                ALTER TABLE orders_productmachineassignment 
                                ALTER COLUMN product_sku TYPE VARCHAR(100)
                            """)
                            cursor.execute("RELEASE SAVEPOINT sp_reverse_pma_sku")
                        except Exception:
                            cursor.execute("ROLLBACK TO SAVEPOINT sp_reverse_pma_sku")
                    elif db_vendor == 'mysql':
                        cursor.execute("""
                            ALTER TABLE orders_productmachineassignment 
                            MODIFY COLUMN product_sku VARCHAR(100)
                        """)
                except Exception:
                    pass


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial which always exists
        # This migration uses SeparateDatabaseAndState so it works even if models don't exist in state
        ('orders', '0001_initial'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to update database and Django state independently
        migrations.SeparateDatabaseAndState(
            # Database operations - supports both MySQL and PostgreSQL
            database_operations=[
                migrations.RunPython(
                    increase_sku_length,
                    reverse_increase_sku_length,
                ),
            ],
            # State operations - update Django's migration state tracking
            # Only include orderitem since productmachineassignment might not exist in state
            state_operations=[
                SafeAlterField(
                    model_name='orderitem',
                    name='sku',
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
                # Note: productmachineassignment.product_sku state change omitted
                # to avoid state conflicts. Database change via RunPython still applies.
            ],
        ),
    ]

