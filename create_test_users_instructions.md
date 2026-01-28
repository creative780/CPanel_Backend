# Creating Test Users - Instructions

Since the server is running with PostgreSQL but management commands detect test mode and use SQLite, test users need to be created using one of these methods:

## Method 1: Django Admin (Recommended)

1. Open browser: http://127.0.0.1:8000/admin
2. Login with an existing admin account
3. Navigate to "Users" section
4. Click "Add User"
5. Create the following users:

### Admin Test User
- Username: `admin_test`
- Email: `admin@test.com`
- Password: `admin123`
- Roles: `["admin"]`
- Active: ✓

### Designer Users
- Username: `designer1`, Email: `designer1@test.com`, Password: `designer123`, Roles: `["designer"]`
- Username: `designer2`, Email: `designer2@test.com`, Password: `designer123`, Roles: `["designer"]`

### Production Users
- Username: `production1`, Email: `production1@test.com`, Password: `production123`, Roles: `["production"]`
- Username: `production2`, Email: `production2@test.com`, Password: `production123`, Roles: `["production"]`

## Method 2: Django Shell (If you have admin access)

```powershell
cd "D:\Abdullah\CRM Backup\12"
.\.venv\Scripts\Activate.ps1
cd CRM_BACKEND
python manage.py shell
```

Then in the shell:
```python
from accounts.models import User

# Admin
admin = User.objects.create_user('admin_test', 'admin@test.com', 'admin123', roles=['admin'])
admin.is_active = True
admin.save()

# Designers
designer1 = User.objects.create_user('designer1', 'designer1@test.com', 'designer123', roles=['designer'])
designer1.is_active = True
designer1.save()

designer2 = User.objects.create_user('designer2', 'designer2@test.com', 'designer123', roles=['designer'])
designer2.is_active = True
designer2.save()

# Production
production1 = User.objects.create_user('production1', 'production1@test.com', 'production123', roles=['production'])
production1.is_active = True
production1.save()

production2 = User.objects.create_user('production2', 'production2@test.com', 'production123', roles=['production'])
production2.is_active = True
production2.save()

print("All test users created!")
```

## Method 3: Via API (If you have an admin token)

If you have an admin user and can get an auth token, you can use the register endpoint:

```python
import requests

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

# First, login to get token
response = requests.post(f"{API_URL}/auth/login", json={
    "username": "your_admin_username",
    "password": "your_admin_password",
    "role": "admin"
})
token = response.json()['access']

# Then create users
headers = {"Authorization": f"Bearer {token}"}

users = [
    {"username": "admin_test", "email": "admin@test.com", "password": "admin123", "roles": ["admin"]},
    {"username": "designer1", "email": "designer1@test.com", "password": "designer123", "roles": ["designer"]},
    {"username": "designer2", "email": "designer2@test.com", "password": "designer123", "roles": ["designer"]},
    {"username": "production1", "email": "production1@test.com", "password": "production123", "roles": ["production"]},
    {"username": "production2", "email": "production2@test.com", "password": "production123", "roles": ["production"]},
]

for user_data in users:
    requests.post(f"{API_URL}/auth/register", headers=headers, json=user_data)
```

## After Creating Users

Once users are created, you can test the implementation:

1. Test users_by_role endpoint
2. Test order creation with assignments
3. Test order visibility filtering
4. Test frontend UI
