# Generated migration for overtime calculation

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class SafeAddField(migrations.AddField):
    """AddField that safely handles the case where the field already exists in the database."""
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if field exists before adding."""
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
        model = to_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        
        # Get the actual database column name
        # For ForeignKey fields, Django uses field_name + '_id'
        column_name = self.name
        if hasattr(self.field, 'related_model') and self.field.related_model:
            # This is a ForeignKey, check for the _id column
            column_name = f"{self.name}_id"
        
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
        
        if not exists:
            super().database_forwards(app_label, schema_editor, from_state, to_state)


def calculate_existing_overtime(apps, schema_editor):
    """Calculate overtime for existing attendance records."""
    Attendance = apps.get_model('attendance', 'Attendance')
    AttendanceRule = apps.get_model('attendance', 'AttendanceRule')
    
    # Check if device_id and device_name columns exist in the database
    vendor = schema_editor.connection.vendor
    cursor = schema_editor.connection.cursor()
    table_name = Attendance._meta.db_table
    
    device_id_exists = False
    device_name_exists = False
    
    try:
        if vendor == "mysql":
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table_name, 'device_id'],
            )
            device_id_exists = cursor.fetchone()[0] > 0
            
            cursor.execute(
                """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table_name, 'device_name'],
            )
            device_name_exists = cursor.fetchone()[0] > 0
        elif vendor == "sqlite":
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = {row[1]: row for row in cursor.fetchall()}
            device_id_exists = 'device_id' in columns
            device_name_exists = 'device_name' in columns
        else:  # PostgreSQL
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table_name, 'device_id'],
            )
            device_id_exists = cursor.fetchone()[0] > 0
            
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
                """,
                [table_name, 'device_name'],
            )
            device_name_exists = cursor.fetchone()[0] > 0
    except Exception:
        # If column check fails, assume columns don't exist
        device_id_exists = False
        device_name_exists = False
    
    try:
        rules = AttendanceRule.objects.first()
        if not rules:
            return
        standard_minutes = rules.standard_work_minutes
    except Exception:
        standard_minutes = 510  # Default fallback
    
    # Update all checked-out attendance records
    for attendance in Attendance.objects.filter(check_out__isnull=False):
        # Safely check if monitored (has device_id or device_name)
        # Use getattr() to safely access fields that might not exist in the model state
        device_id = getattr(attendance, 'device_id', '') if device_id_exists else ''
        device_name = getattr(attendance, 'device_name', None) if device_name_exists else None
        is_monitored = bool(device_id or device_name)
        
        # Also check effective_minutes safely
        effective_minutes = getattr(attendance, 'effective_minutes', None)
        
        if is_monitored and effective_minutes:
            overtime = max(0, effective_minutes - standard_minutes)
            # Only update if overtime_minutes field exists (it should, as we just added it)
            if hasattr(attendance, 'overtime_minutes'):
                attendance.overtime_minutes = overtime
                # Set verification flag if overtime > 4 hours (240 minutes)
                if overtime > 240 and hasattr(attendance, 'overtime_verified'):
                    attendance.overtime_verified = False
                # Save only the fields that exist
                update_fields = []
                if hasattr(attendance, 'overtime_minutes'):
                    update_fields.append('overtime_minutes')
                if hasattr(attendance, 'overtime_verified'):
                    update_fields.append('overtime_verified')
                if update_fields:
                    attendance.save(update_fields=update_fields)


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0008_break_flag_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        SafeAddField(
            model_name='attendance',
            name='overtime_minutes',
            field=models.PositiveIntegerField(default=0),
        ),
        SafeAddField(
            model_name='attendance',
            name='overtime_verified',
            field=models.BooleanField(default=False),
        ),
        SafeAddField(
            model_name='attendance',
            name='overtime_verified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='verified_overtime_records',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        SafeAddField(
            model_name='attendance',
            name='overtime_verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(
            calculate_existing_overtime,
            migrations.RunPython.noop,
        ),
    ]

