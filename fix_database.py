#!/usr/bin/env python
"""
Database Fix Script
This script will:
1. Safely flush all data from the database
2. Run all migrations to create proper schema
3. Create a superuser for admin access
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

def flush_and_migrate():
    """Flush database and run migrations"""
    print("🗑️  Flushing database...")
    execute_from_command_line(['manage.py', 'flush', '--noinput'])
    
    print("📋 Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Database setup complete!")

def create_superuser():
    """Create a superuser for admin access"""
    User = get_user_model()
    
    # Check if superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print("👤 Superuser already exists")
        return
    
    print("👤 Creating superuser...")
    username = 'admin'
    email = 'admin@crm.click2print.store'
    # SECURITY: Use environment variable, not hardcoded password
    password = os.getenv('ADMIN_PASSWORD', 'admin123')  # Change in production .env!
    
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    print(f"✅ Superuser created:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print("   ⚠️  Please change the password after first login!")

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
        else:
            print("❌ sales_person column missing from orders_order table")
            return False
    
    print("✅ Database schema verification complete!")
    return True

def main():
    print("🚀 Starting database fix process...")
    print("=" * 50)
    
    try:
        # Step 1: Flush and migrate
        flush_and_migrate()
        
        # Step 2: Verify schema
        if not verify_schema():
            print("❌ Schema verification failed!")
            return False
        
        # Step 3: Create superuser
        create_superuser()
        
        print("=" * 50)
        print("🎉 Database fix completed successfully!")
        print("You can now start your Django server and the APIs should work.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)