#!/usr/bin/env python
"""
Nuclear Database Reset Script
This script will:
1. Delete all migration files
2. Recreate migrations from scratch
3. Flush the database
4. Apply all migrations
5. Create a superuser
"""

import os
import sys
import django
import shutil
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

def delete_migration_files():
    """Delete all migration files except __init__.py"""
    print("🗑️  Deleting all migration files...")
    
    apps_to_reset = [
        'accounts',
        'activity_log', 
        'attendance',
        'audit',
        'chat',
        'clients',
        'delivery',
        'hr',
        'inventory',
        'monitoring',
        'orders',
    ]
    
    for app in apps_to_reset:
        migrations_dir = os.path.join(app, 'migrations')
        if os.path.exists(migrations_dir):
            print(f"   Deleting migrations for {app}...")
            for file in os.listdir(migrations_dir):
                if file != '__init__.py' and file.endswith('.py'):
                    file_path = os.path.join(migrations_dir, file)
                    os.remove(file_path)
                    print(f"     Deleted: {file}")
        else:
            print(f"   No migrations directory found for {app}")

def recreate_migrations():
    """Recreate all migrations from scratch"""
    print("📋 Recreating migrations from scratch...")
    
    apps_to_migrate = [
        'accounts',
        'activity_log',
        'attendance', 
        'audit',
        'chat',
        'clients',
        'delivery',
        'hr',
        'inventory',
        'monitoring',
        'orders',
    ]
    
    for app in apps_to_migrate:
        print(f"   Creating initial migration for {app}...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations', app])
        except Exception as e:
            print(f"     Warning: Could not create migration for {app}: {e}")

def flush_and_migrate():
    """Flush database and run all migrations"""
    print("🗑️  Flushing database...")
    execute_from_command_line(['manage.py', 'flush', '--noinput'])
    
    print("📋 Running all migrations...")
    execute_from_command_line(['manage.py', 'migrate'])

def create_superuser():
    """Create a superuser for admin access"""
    User = get_user_model()
    
    print("👤 Creating superuser...")
    username = 'admin'
    email = 'admin@crm.click2print.store'
    # SECURITY: Use environment variable, not hardcoded password
    import os
    password = os.getenv('ADMIN_PASSWORD', 'admin123')  # Change in production .env!
    
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    print(f"✅ Superuser created:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")

def verify_schema():
    """Verify that the database schema is correct"""
    print("🔍 Verifying database schema...")
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if orders_order table has sales_person column
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'orders_order' 
            AND COLUMN_NAME = 'sales_person'
        """)
        
        result = cursor.fetchone()
        if result:
            print("✅ sales_person column exists in orders_order table")
            return True
        else:
            print("❌ sales_person column missing from orders_order table")
            return False

def main():
    print("🚀 Starting NUCLEAR database reset...")
    print("⚠️  This will DELETE ALL DATA and recreate everything!")
    print("=" * 60)
    
    try:
        # Step 1: Delete all migration files
        delete_migration_files()
        
        # Step 2: Recreate migrations
        recreate_migrations()
        
        # Step 3: Flush and migrate
        flush_and_migrate()
        
        # Step 4: Verify schema
        if not verify_schema():
            print("❌ Schema verification failed!")
            return False
        
        # Step 5: Create superuser
        create_superuser()
        
        print("=" * 60)
        print("🎉 NUCLEAR reset completed successfully!")
        print("Your database is now completely fresh with proper schema.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during nuclear reset: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
