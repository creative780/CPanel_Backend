import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_backend_final.models import RecentlyDeletedItem

items = RecentlyDeletedItem.objects.all()
print(f"Total Items in Trash: {items.count()}")
for i in items:
    print(f"Table: {i.table_name}, ID: {i.record_id}, Name: {i.record_data.get('title') or i.record_data.get('name')}, Deleted At: {i.deleted_at}")
