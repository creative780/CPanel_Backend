from django.db import migrations, models


class SafeAddField(migrations.AddField):
    """AddField that safely handles the case where the field already exists in the database or model doesn't exist in state."""
    
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Override to check if field exists before adding."""
        # Try to get the model - if it doesn't exist, skip
        try:
            model = to_state.apps.get_model(app_label, self.model_name)
            table_name = model._meta.db_table
        except LookupError:
            # Model doesn't exist in state, skip database operation
            return
        
        vendor = schema_editor.connection.vendor
        cursor = schema_editor.connection.cursor()
        
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
            super().database_forwards(app_label, schema_editor, from_state, to_state)
    
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


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0007_merge_0005_0006'),
        # Also depend on 0002 to ensure AttendanceRule exists
        ('attendance', '0002_attendancerule_attendance_device_info_and_more'),
    ]

    operations = [
        SafeAddField(
            model_name='attendancebreak',
            name='flag_reason',
            field=models.CharField(blank=True, max_length=255),
        ),
        SafeAddField(
            model_name='attendancebreak',
            name='is_flagged',
            field=models.BooleanField(default=False),
        ),
        SafeAddField(
            model_name='attendancerule',
            name='max_break_minutes',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Flag breaks longer than this duration (minutes). Leave blank to disable.',
                null=True,
            ),
        ),
        SafeAddField(
            model_name='attendancerule',
            name='min_break_minutes',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Flag breaks shorter than this duration (minutes). Leave blank to disable.',
                null=True,
            ),
        ),
    ]


