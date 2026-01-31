
import os
import django
import sys
from django.db.models import PROTECT, CASCADE, SET_NULL, SET_DEFAULT, DO_NOTHING

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def run():
    django.setup()
    from admin_backend_final.models import Category
    
    print("--- CATEGORY RELATIONS ---")
    for rel in Category._meta.related_objects:
        on_delete = rel.on_delete
        on_delete_name = "UNKNOWN"
        if on_delete == PROTECT: on_delete_name = "PROTECT"
        elif on_delete == CASCADE: on_delete_name = "CASCADE"
        elif on_delete == SET_NULL: on_delete_name = "SET_NULL"
        elif on_delete == SET_DEFAULT: on_delete_name = "SET_DEFAULT"
        elif on_delete == DO_NOTHING: on_delete_name = "DO_NOTHING"
        
        print(f"Relation: {rel.name}, Model: {rel.related_model.__name__}, Field: {rel.field.name}, On Delete: {on_delete_name}")
    print("--- END ---")

if __name__ == '__main__':
    run()
