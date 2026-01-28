#!/usr/bin/env python
"""
Fix inconsistent migration history for attendance app.
This script directly inserts the missing migration record into django_migrations table.
"""
import os
import sys
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

from django.db import connection

def fix_migration_history():
    """Insert missing migration record into django_migrations table."""
    migration_name = '0002_attendancerule_attendance_device_info_and_more'
    app_name = 'attendance'
    
    with connection.cursor() as cursor:
        # Check if migration already exists
        if connection.vendor == 'mysql':
            cursor.execute(
                """
                SELECT COUNT(*) FROM django_migrations 
                WHERE app = %s AND name = %s
                """,
                [app_name, migration_name]
            )
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                cursor.execute(
                    """
                    INSERT INTO django_migrations (app, name, applied) 
                    VALUES (%s, %s, %s)
                    """,
                    [app_name, migration_name, timezone.now()]
                )
                print(f"✅ Successfully inserted migration record: {app_name}.{migration_name}")
            else:
                print(f"ℹ️  Migration record already exists: {app_name}.{migration_name}")
        
        elif connection.vendor == 'postgresql':
            cursor.execute(
                """
                INSERT INTO django_migrations (app, name, applied) 
                VALUES (%s, %s, %s)
                ON CONFLICT (app, name) DO NOTHING
                """,
                [app_name, migration_name, timezone.now()]
            )
            print(f"✅ Successfully inserted migration record: {app_name}.{migration_name}")
        
        else:  # SQLite
            cursor.execute(
                """
                INSERT OR IGNORE INTO django_migrations (app, name, applied) 
                VALUES (?, ?, ?)
                """,
                [app_name, migration_name, timezone.now()]
            )
            print(f"✅ Successfully inserted migration record: {app_name}.{migration_name}")

if __name__ == '__main__':
    try:
        fix_migration_history()
        print("\n✅ Migration history fixed! Now run: python manage.py migrate --check")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


