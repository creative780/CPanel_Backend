#!/usr/bin/env python
"""
Fix inconsistent migration history for all apps.
This script directly inserts missing migration records into django_migrations table.
"""
import os
import sys
import django
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

from django.db import connection

def fix_migration_history(app_name, migration_name):
    """Insert missing migration record into django_migrations table."""
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
                print(f"✅ Inserted: {app_name}.{migration_name}")
                return True
            else:
                print(f"ℹ️  Already exists: {app_name}.{migration_name}")
                return False
        
        elif connection.vendor == 'postgresql':
            cursor.execute(
                """
                INSERT INTO django_migrations (app, name, applied) 
                VALUES (%s, %s, %s)
                ON CONFLICT (app, name) DO NOTHING
                """,
                [app_name, migration_name, timezone.now()]
            )
            print(f"✅ Inserted: {app_name}.{migration_name}")
            return True
        
        else:  # SQLite
            cursor.execute(
                """
                INSERT OR IGNORE INTO django_migrations (app, name, applied) 
                VALUES (?, ?, ?)
                """,
                [app_name, migration_name, timezone.now()]
            )
            print(f"✅ Inserted: {app_name}.{migration_name}")
            return True

def main():
    """Fix all known migration history issues."""
    fixes = [
        ('attendance', '0002_attendancerule_attendance_device_info_and_more'),
        ('monitoring', '0002_org_device_screenshot_session_devicetoken_heartbeat_and_more'),
    ]
    
    print("🔧 Fixing migration history...")
    print("=" * 60)
    
    fixed_count = 0
    for app_name, migration_name in fixes:
        try:
            if fix_migration_history(app_name, migration_name):
                fixed_count += 1
        except Exception as e:
            print(f"❌ Error fixing {app_name}.{migration_name}: {e}")
    
    print("=" * 60)
    print(f"✅ Fixed {fixed_count} migration record(s)")
    print("\n📋 Next steps:")
    print("   1. python manage.py showmigrations")
    print("   2. python manage.py migrate --check")
    print("   3. python manage.py migrate")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


