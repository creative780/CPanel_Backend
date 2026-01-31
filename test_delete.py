
import os
import django
import sys
import json
from unittest.mock import MagicMock

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def run():
    django.setup()
    from admin_backend_final.models import Category
    from admin_backend_final.category import DeleteCategoryAPIView
    
    # 1. Create Dummy
    cat_id = "TEST-DEL-1"
    if not Category.objects.filter(category_id=cat_id).exists():
        Category.objects.create(
            category_id=cat_id,
            name="Test Delete Msg",
            status="visible",
            created_by="Sys"
        )
        print("Created dummy category.")
    else:
        print("Dummy category already exists.")

    # 2. Mock Request
    view = DeleteCategoryAPIView()
    request = MagicMock()
    request.body = json.dumps({
        "ids": [cat_id],
        "confirm": True
    }).encode('utf-8')
    
    # 3. Call Post
    print("Calling DeleteCategoryAPIView.post...")
    try:
        response = view.post(request)
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.data}")
    except Exception as e:
        print(f"Exception during view call: {e}")
        import traceback
        traceback.print_exc()

    # 4. Verify
    exists = Category.objects.filter(category_id=cat_id).exists()
    print(f"Category {cat_id} exists after delete? {exists}")

if __name__ == '__main__':
    run()
