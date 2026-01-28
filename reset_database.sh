#!/bin/bash

# Database Reset Script for CRM Backend
# This script will flush the database and run migrations

echo "🚀 Starting database reset process..."
echo "=================================================="

# Change to the backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Flush the database (remove all data)
echo "🗑️  Flushing database..."
python manage.py flush --noinput

# Run all migrations
echo "📋 Running migrations..."
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

# Check if superuser already exists
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@crm.click2print.store',
        password='admin123'
    )
    print("✅ Superuser created: admin / admin123")
else:
    print("👤 Superuser already exists")
EOF

# Verify the schema
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

echo "=================================================="
echo "🎉 Database reset completed!"
echo "You can now restart your Django server."
