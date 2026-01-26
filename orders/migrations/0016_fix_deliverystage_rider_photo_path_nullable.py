# Generated manually to fix rider_photo_path NOT NULL constraint

from django.db import migrations


def fix_deliverystage_rider_photo_path_nullable(apps, schema_editor):
    """Make rider_photo_path nullable using vendor-appropriate SQL."""
    vendor = schema_editor.connection.vendor
    cursor = schema_editor.connection.cursor()
    
    if vendor == "mysql":
        # MySQL/MariaDB supports ALTER TABLE ... MODIFY COLUMN directly
        # Check if column exists and is currently NOT NULL
        cursor.execute(
            """
            SELECT IS_NULLABLE, COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'orders_deliverystage'
            AND COLUMN_NAME = 'rider_photo_path'
            """
        )
        result = cursor.fetchone()
        
        if result:
            is_nullable, column_type = result
            if is_nullable == 'NO':
                # Column exists and is NOT NULL, make it nullable
                cursor.execute(
                    "ALTER TABLE `orders_deliverystage` "
                    "MODIFY COLUMN `rider_photo_path` VARCHAR(500) NULL"
                )
        # If column doesn't exist or is already nullable, do nothing
    
    elif vendor == "sqlite":
        # SQLite doesn't support ALTER COLUMN directly, need to recreate table
        cursor.execute("""
            CREATE TABLE orders_deliverystage_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                rider_photo_path VARCHAR(500),
                delivered_at DATETIME,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders_order(id)
            )
        """)
        
        # Copy data from old table
        cursor.execute("""
            INSERT INTO orders_deliverystage_new (
                id, order_id, rider_photo_path, delivered_at, created_at, updated_at
            )
            SELECT 
                id, order_id, 
                CASE WHEN rider_photo_path = '' THEN NULL ELSE rider_photo_path END,
                delivered_at, created_at, updated_at
            FROM orders_deliverystage
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE orders_deliverystage")
        
        # Rename new table
        cursor.execute("ALTER TABLE orders_deliverystage_new RENAME TO orders_deliverystage")
    
    else:  # PostgreSQL
        # PostgreSQL supports ALTER COLUMN ... DROP NOT NULL
        cursor.execute(
            """
            SELECT is_nullable
            FROM information_schema.columns
            WHERE table_name = 'orders_deliverystage'
            AND column_name = 'rider_photo_path'
            """
        )
        result = cursor.fetchone()
        
        if result:
            is_nullable = result[0]
            if is_nullable == 'NO':
                # Column exists and is NOT NULL, make it nullable
                cursor.execute(
                    "ALTER TABLE orders_deliverystage "
                    "ALTER COLUMN rider_photo_path DROP NOT NULL"
                )
        # If column doesn't exist or is already nullable, do nothing


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0001_initial where DeliveryStage is created
        # This migration uses RunPython so it doesn't need model state, just needs the table to exist
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            fix_deliverystage_rider_photo_path_nullable,
            migrations.RunPython.noop,
        ),
    ]
