#!/usr/bin/env python
"""
Create test users via API (since server uses different database)
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

def create_user_via_api(username, email, password, roles, first_name="", last_name=""):
    """Create user via registration API"""
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "roles": roles,
                "first_name": first_name,
                "last_name": last_name
            }
        )
        if response.status_code in [200, 201]:
            print(f"  [OK] Created user: {username}")
            return True
        else:
            print(f"  [INFO] User {username} may already exist or error: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  [FAIL] Error creating {username}: {e}")
        return False

print("Creating test users via API...\n")
print("Note: This requires the registration endpoint to be available.")
print("If registration is disabled, users must be created via Django admin.\n")

# Try to create users
results = []
results.append(create_user_via_api('admin_test', 'admin@test.com', 'admin123', ['admin'], 'Admin', 'Test'))
results.append(create_user_via_api('designer1', 'designer1@test.com', 'designer123', ['designer'], 'Designer', 'One'))
results.append(create_user_via_api('designer2', 'designer2@test.com', 'designer123', ['designer'], 'Designer', 'Two'))
results.append(create_user_via_api('production1', 'production1@test.com', 'production123', ['production'], 'Production', 'One'))
results.append(create_user_via_api('production2', 'production2@test.com', 'production123', ['production'], 'Production', 'Two'))

print(f"\nCompleted: {sum(results)}/{len(results)} users created/attempted")
print("\nIf registration endpoint is not available, please create users via:")
print("  1. Django admin interface")
print("  2. Django shell (python manage.py shell)")
print("  3. Existing setup_test_users command (if database is accessible)")
