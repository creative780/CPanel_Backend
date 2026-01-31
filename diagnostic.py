
import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Set environment variable for Django settings (assuming standard layout)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def run():
    try:
        django.setup()
        from admin_backend_final.models import Category
        print("--- START DIAGNOSTIC ---")
        cats = Category.objects.all()
        print(f"Total Categories: {cats.count()}")
        for c in cats:
            print(f"ID: {c.category_id}, Name: {c.name}, Status: {c.status}")
        print("--- END DIAGNOSTIC ---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run()
