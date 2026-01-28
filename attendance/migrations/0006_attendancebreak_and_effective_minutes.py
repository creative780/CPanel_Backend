# Modified to safely handle duplicate columns and existing tables

from django.db import migrations, models
import django.db.models.deletion


class SafeAddField(migrations.AddField):
    """AddField that safely handles the case where the field already exists in the database."""
    
    def state_forwards(self, app_label, state):
        """Override to safely handle missing model in state."""
        try:
            # Check if model exists in state
            model_key = (app_label, self.model_name.lower())
            if model_key not in state.models:
                # Model doesn't exist in state, skip state update
                return
            super().state_forwards(app_label, state)
        except KeyError:
            # Model or field doesn't exist in state, skip
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
        
        # Get the actual database column name
        # For ForeignKey fields, Django uses field_name + '_id'
        column_name = self.name
        if hasattr(self.field, 'related_model') and self.field.related_model:
            # This is a ForeignKey, check for the _id column
            column_name = f"{self.name}_id"
        
        # Check if column already exists
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table_name, column_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = [row[1] for row in cursor.fetchall()]
            exists = column_name in columns
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table_name, column_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        # If column exists, skip the database operation
        if exists:
            return
        
        # Column doesn't exist, proceed with adding it
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            # Catch duplicate column errors
            error_str = str(e)
            if "Duplicate column" in error_str or "duplicate" in error_str.lower() or "1060" in error_str:
                # Column already exists, skip
                return
            # Re-raise other exceptions
            raise


class SafeCreateModel(migrations.CreateModel):
    """CreateModel that safely handles the case where the table already exists."""
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if table exists before creating."""
        model = to_state.apps.get_model(app_label, self.name)
        table_name = model._meta.db_table
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        # Check if table already exists
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                """,
                [table_name],
            )
            exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            # Use raw SQLite connection to avoid Django's debug formatting issue
            # The issue is that Django tries to format SQL with % which fails for parameterized queries
            raw_connection = schema_editor.connection.connection
            raw_cursor = raw_connection.cursor()
            try:
                raw_cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    [table_name],
                )
                exists = raw_cursor.fetchone() is not None
            finally:
                raw_cursor.close()
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = %s
                """,
                [table_name],
            )
            exists = cursor.fetchone()[0] > 0
        
        # If table exists, skip the database operation
        if exists:
            return
        
        # Table doesn't exist, proceed with creating it
        try:
            super().database_forwards(app_label, schema_editor, from_state, to_state)
        except Exception as e:
            # Catch duplicate table errors
            error_str = str(e)
            if "already exists" in error_str.lower() or "1050" in error_str:
                # Table already exists, skip
                return
            # Re-raise other exceptions
            raise


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        SafeAddField(
            model_name='attendance',
            name='effective_minutes',
            field=models.PositiveIntegerField(default=0),
        ),
        SafeAddField(
            model_name='attendance',
            name='total_break_minutes',
            field=models.PositiveIntegerField(default=0),
        ),
        SafeCreateModel(
            name='AttendanceBreak',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField()),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('duration_minutes', models.PositiveIntegerField(default=0)),
                ('source', models.CharField(choices=[('web', 'Web'), ('agent', 'Agent')], default='web', max_length=16)),
                ('notes', models.CharField(blank=True, max_length=255)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='breaks', to='attendance.attendance')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
    ]

