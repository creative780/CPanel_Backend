# Generated manually to add missing fields and fix field name mismatches

from django.db import migrations, models
import django.db.models.deletion


class SafeAddField(migrations.AddField):
    """AddField that safely handles the case where the field already exists in the database or model doesn't exist in state."""
    
    def state_forwards(self, app_label, state):
        """Override to safely handle missing model in state."""
        # Catch all exceptions - if model doesn't exist or anything goes wrong, skip silently
        try:
            super().state_forwards(app_label, state)
        except Exception:
            # Model doesn't exist in state, skip
            pass
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if field exists before adding."""
        # First check if model exists in to_state
        model_key = (app_label, self.model_name.lower())
        if model_key not in to_state.models:
            # Model doesn't exist, skip database operation
            return
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        # Get table name from model
        model = to_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        
        # Check if column exists
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table_name, self.name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            # SQLite PRAGMA doesn't support parameterized queries, but we can quote the table name
            # Use double quotes for SQLite identifiers
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = [row[1] for row in cursor.fetchall()]
            exists = self.name in columns
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table_name, self.name],
            )
            exists = cursor.fetchone()[0] > 0
        
        if not exists:
            # Field doesn't exist, add it normally
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        # If field exists, skip the database operation
        # State will still be updated by state_forwards() which is called separately


class SafeRemoveField(migrations.RemoveField):
    """RemoveField that safely handles the case where the field doesn't exist in state."""
    
    def state_forwards(self, app_label, state):
        """Override to safely handle missing field."""
        try:
            # Try to remove the field - if it doesn't exist, KeyError will be raised
            super().state_forwards(app_label, state)
        except KeyError:
            # Field doesn't exist in state (already removed or never existed), silently skip
            pass


def fix_productmachineassignment_fields(apps, schema_editor):
    """Fix ProductMachineAssignment fields by renaming start_time/actual_completion_time to started_at/completed_at."""
    vendor = schema_editor.connection.vendor
    cursor = schema_editor.connection.cursor()
    
    # Check if the old columns exist
    if vendor == "mysql":
        # Check if start_time and actual_completion_time exist
        cursor.execute(
            """
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'orders_productmachineassignment'
            AND COLUMN_NAME IN ('start_time', 'actual_completion_time')
            """
        )
        old_columns_count = cursor.fetchone()[0]
        
        # Check if started_at and completed_at already exist
        cursor.execute(
            """
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'orders_productmachineassignment'
            AND COLUMN_NAME IN ('started_at', 'completed_at')
            """
        )
        new_columns_count = cursor.fetchone()[0]
        
        if old_columns_count > 0 and new_columns_count == 0:
            # Rename columns using ALTER TABLE
            if old_columns_count == 2:
                # Both columns exist, rename them
                cursor.execute(
                    "ALTER TABLE `orders_productmachineassignment` "
                    "CHANGE COLUMN `start_time` `started_at` DATETIME(6) NULL"
                )
                cursor.execute(
                    "ALTER TABLE `orders_productmachineassignment` "
                    "CHANGE COLUMN `actual_completion_time` `completed_at` DATETIME(6) NULL"
                )
            elif old_columns_count == 1:
                # Only one column exists, check which one
                cursor.execute(
                    """
                    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'orders_productmachineassignment'
                    AND COLUMN_NAME IN ('start_time', 'actual_completion_time')
                    """
                )
                existing_col = cursor.fetchone()
                if existing_col and existing_col[0] == 'start_time':
                    cursor.execute(
                        "ALTER TABLE `orders_productmachineassignment` "
                        "CHANGE COLUMN `start_time` `started_at` DATETIME(6) NULL"
                    )
                elif existing_col and existing_col[0] == 'actual_completion_time':
                    cursor.execute(
                        "ALTER TABLE `orders_productmachineassignment` "
                        "CHANGE COLUMN `actual_completion_time` `completed_at` DATETIME(6) NULL"
                    )
        # If new columns already exist, do nothing
    elif vendor == "sqlite":
        # SQLite doesn't support column renaming directly, need to recreate table
        # Check if we need to do this
        cursor.execute("PRAGMA table_info(orders_productmachineassignment)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        has_old = 'start_time' in columns or 'actual_completion_time' in columns
        has_new = 'started_at' in columns and 'completed_at' in columns
        
        # If table already has the new columns, skip this migration
        if has_new:
            return
        
        if has_old and not has_new:
            # Create new table
            cursor.execute("""
                CREATE TABLE orders_productmachineassignment_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_name VARCHAR(255) NOT NULL,
                    product_sku VARCHAR(255),
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
            
            # Copy data
            # Migration 0006 creates the table with 'product_quantity', so use that
            # If the table doesn't exist or is empty, this will work fine
            try:
                cursor.execute("""
                    INSERT INTO orders_productmachineassignment_new (
                        id, order_id, product_name, product_sku, product_quantity,
                        machine_id, machine_name, estimated_time_minutes,
                        started_at, completed_at, status, assigned_by, notes
                    )
                    SELECT
                        id, order_id, product_name, product_sku, product_quantity,
                        machine_id, machine_name, estimated_time_minutes,
                        start_time, actual_completion_time, status, assigned_by, notes
                    FROM orders_productmachineassignment
                """)
            except Exception:
                # If product_quantity doesn't exist, try with 0 as default
                # This handles the case where the table structure is different
                cursor.execute("""
                    INSERT INTO orders_productmachineassignment_new (
                        id, order_id, product_name, product_sku, product_quantity,
                        machine_id, machine_name, estimated_time_minutes,
                        started_at, completed_at, status, assigned_by, notes
                    )
                    SELECT
                        id, order_id, product_name, product_sku, 0,
                        machine_id, machine_name, estimated_time_minutes,
                        start_time, actual_completion_time, status, assigned_by, notes
                    FROM orders_productmachineassignment
                """)
            
            # Drop old and rename new
            cursor.execute("DROP TABLE orders_productmachineassignment")
            cursor.execute("ALTER TABLE orders_productmachineassignment_new RENAME TO orders_productmachineassignment")
    else:  # PostgreSQL
        # PostgreSQL supports column renaming
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_name = 'orders_productmachineassignment'
            AND column_name IN ('start_time', 'actual_completion_time')
            """
        )
        old_columns_count = cursor.fetchone()[0]
        
        if old_columns_count > 0:
            cursor.execute(
                "ALTER TABLE orders_productmachineassignment "
                "RENAME COLUMN start_time TO started_at"
            )
            cursor.execute(
                "ALTER TABLE orders_productmachineassignment "
                "RENAME COLUMN actual_completion_time TO completed_at"
            )


class Migration(migrations.Migration):

    dependencies = [
        # Depend on 0018 which merges the branches
        # Note: If 0015 exists locally and causes conflicts, it can be applied separately
        ('orders', '0018_merge_20251031_0107'),
    ]

    operations = [
        # Add missing design_completed_at and design_commented_by fields to OrderItem
        SafeAddField(
            model_name='orderitem',
            name='design_completed_at',
            field=models.DateTimeField(blank=True, help_text='When the design was completed', null=True),
        ),
        SafeAddField(
            model_name='orderitem',
            name='design_commented_by',
            field=models.CharField(blank=True, help_text='Who commented on the design', max_length=255, null=True),
        ),
        
        # Remove old fields and add new ones for ProductMachineAssignment
        # Use RunPython to handle different database vendors
        migrations.RunPython(
            fix_productmachineassignment_fields,
            migrations.RunPython.noop,
        ),
        
        # Update Django state for ProductMachineAssignment
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # Database already updated above
            state_operations=[
                SafeRemoveField(
                    model_name='productmachineassignment',
                    name='start_time',
                ),
                SafeRemoveField(
                    model_name='productmachineassignment',
                    name='expected_completion_time',
                ),
                SafeRemoveField(
                    model_name='productmachineassignment',
                    name='actual_completion_time',
                ),
                SafeAddField(
                    model_name='productmachineassignment',
                    name='started_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
                SafeAddField(
                    model_name='productmachineassignment',
                    name='completed_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
            ],
        ),
    ]







