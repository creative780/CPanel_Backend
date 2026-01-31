
import os
import django
import sys
import json
from unittest.mock import MagicMock

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def run():
    django.setup()
    from admin_backend_final.category import DeleteCategoryAPIView

    # Mock Request with NON-EXISTENT ID
    view = DeleteCategoryAPIView()
    request = MagicMock()
    request.body = json.dumps({
        "ids": ["NON-EXISTENT-ID-123"],
        "confirm": True
    }).encode('utf-8')
    
    # Call Post
    print("Calling DeleteCategoryAPIView.post with invalid ID...")
    try:
        response = view.post(request)
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.data}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == '__main__':
    run()
