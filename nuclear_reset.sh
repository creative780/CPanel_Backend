#!/bin/bash

# Nuclear Database Reset Script
# This script will completely wipe and recreate everything

echo "🚀 Starting NUCLEAR database reset..."
echo "⚠️  This will DELETE ALL DATA and recreate everything!"
echo "============================================================"

# Change to the backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Step 1: Delete all migration files
echo "🗑️  Deleting all migration files..."
for app in accounts activity_log attendance audit chat clients delivery hr inventory monitoring orders; do
    if [ -d "$app/migrations" ]; then
        echo "   Deleting migrations for $app..."
        find "$app/migrations" -name "*.py" -not -name "__init__.py" -delete
    fi
done

# Step 2: Recreate migrations
echo "📋 Recreating migrations from scratch..."
python manage.py makemigrations accounts
python manage.py makemigrations activity_log
python manage.py makemigrations attendance
python manage.py makemigrations audit
python manage.py makemigrations chat
python manage.py makemigrations clients
python manage.py makemigrations delivery
python manage.py makemigrations hr
python manage.py makemigrations inventory
python manage.py makemigrations monitoring
python manage.py makemigrations orders

# Step 3: Flush database
echo "🗑️  Flushing database..."
python manage.py flush --noinput

# Step 4: Run all migrations
echo "📋 Running all migrations..."
python manage.py migrate

# Step 5: Create superuser
echo "👤 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

User.objects.create_superuser(
    username='admin',
    email='admin@crm.click2print.store',
    password='admin123'
)
print("✅ Superuser created: admin / admin123")
EOF

# Step 6: Verify schema
echo "🔍 Verifying database schema..."
python manage.py shell << EOF
from django.db import connection

with connection.cursor() as cursor:
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
EOF

echo "============================================================"
echo "🎉 NUCLEAR reset completed!"
echo "Your database is now completely fresh with proper schema."
