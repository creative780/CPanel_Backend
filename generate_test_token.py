
import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from monitoring.auth_utils import create_enrollment_token
from django.contrib.auth import get_user_model

User = get_user_model()
try:
    # Get first admin user or create one
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("No admin user found needed for token generation")
        sys.exit(1)
        
    token = create_enrollment_token(str(user.id), getattr(user, 'org_id', 'default'))
    print(f"TOKEN:{token}")
except Exception as e:
    print(f"Error: {e}")
