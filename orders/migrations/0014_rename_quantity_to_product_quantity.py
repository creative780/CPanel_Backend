# Generated manually to fix database schema mismatch
# Renames 'quantity' to 'product_quantity' in ProductMachineAssignment table

from django.db import migrations


def rename_quantity_column(apps, schema_editor):
    """Rename quantity to product_quantity using raw SQL"""
    if schema_editor.connection.vendor == 'sqlite':
        # Check if table exists and what columns it has
        cursor = schema_editor.connection.cursor()
        cursor.execute("PRAGMA table_info(orders_productmachineassignment)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        # If product_quantity already exists, skip this migration
        if 'product_quantity' in columns:
            return
        
        # If quantity doesn't exist either, the table might be empty or not exist
        if 'quantity' not in columns:
            return
        
        # SQLite doesn't support column renaming directly, we need to recreate the table
        # Django migrations already run in a transaction, so we don't need to start one
        
        # Create new table with correct column name
        schema_editor.execute("""
            CREATE TABLE orders_productmachineassignment_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                product_sku VARCHAR(100),
                product_quantity INTEGER NOT NULL,
                machine_id VARCHAR(100) NOT NULL,
                machine_name VARCHAR(255) NOT NULL,
                estimated_time_minutes INTEGER NOT NULL,
                started_at DATETIME,
                completed_at DATETIME,
                status VARCHAR(20) NOT NULL,
                assigned_by VARCHAR(255) NOT NULL,
                notes TEXT,
                FOREIGN KEY (order_id) REFERENCES orders_order(id)
            )
        """)
        
        # Copy data from old table, renaming quantity to product_quantity
        schema_editor.execute("""
            INSERT INTO orders_productmachineassignment_new (
                id, order_id, product_name, product_sku, product_quantity,
                machine_id, machine_name, estimated_time_minutes,
                started_at, completed_at, status, assigned_by, notes
            )
            SELECT
                id, order_id, product_name, product_sku, quantity,
                machine_id, machine_name, estimated_time_minutes,
                started_at, completed_at, status, assigned_by, notes
            FROM orders_productmachineassignment
        """)
        
        # Drop old table
        schema_editor.execute("DROP TABLE orders_productmachineassignment;")
        
        # Rename new table
        schema_editor.execute("ALTER TABLE orders_productmachineassignment_new RENAME TO orders_productmachineassignment;")
        
        # Recreate indexes
        schema_editor.execute("""
            CREATE INDEX orders_productmachineassignment_order_status_idx 
                ON orders_productmachineassignment(order_id, status)
        """)
        schema_editor.execute("""
            CREATE INDEX orders_productmachineassignment_machine_status_idx 
                ON orders_productmachineassignment(machine_id, status)
        """)
    else:
        # For PostgreSQL/MySQL
        # Check if quantity column exists before renaming
        cursor = schema_editor.connection.cursor()
        if schema_editor.connection.vendor == 'mysql':
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'orders_productmachineassignment'
                AND COLUMN_NAME = 'quantity'
            """)
            exists = cursor.fetchone()[0] > 0
        else:  # PostgreSQL
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'orders_productmachineassignment'
                AND column_name = 'quantity'
            """)
            exists = cursor.fetchone()[0] > 0
        
        if exists:
            schema_editor.execute(
                "ALTER TABLE orders_productmachineassignment RENAME COLUMN quantity TO product_quantity"
            )


def reverse_rename_quantity_column(apps, schema_editor):
    """Reverse the rename"""
    if schema_editor.connection.vendor == 'sqlite':
        # Not implemented for SQLite - migrations should not be rolled back in production
        pass
    else:
        schema_editor.execute(
            "ALTER TABLE orders_productmachineassignment RENAME COLUMN product_quantity TO quantity"
        )


class Migration(migrations.Migration):

    dependencies = [
        # Depend only on 0001_initial which always exists
        # The rename_quantity_column function already handles missing columns safely
        # If 0012 or 0013 exist, they will be applied before this migration
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rename_quantity_column, reverse_rename_quantity_column),
    ]
