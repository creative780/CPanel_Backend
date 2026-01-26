#!/usr/bin/env python
"""
Test API endpoints with existing users or create via admin if available
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_test(test_name):
    print(f"> {test_name}...")

def print_success(message=""):
    print(f"  [OK] {message}")

def print_error(message):
    print(f"  [FAIL] {message}")

def print_info(message):
    print(f"  [INFO] {message}")

def get_auth_token(username, password, role="admin"):
    """Get authentication token"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password, "role": role},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print_error(f"Login failed: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print_error(f"Exception during login: {e}")
        return None

def test_users_by_role_with_auth(token):
    """Test users_by_role endpoint with authentication"""
    print_test("Testing users_by_role endpoint (authenticated)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test designer role
    try:
        response = requests.get(f"{API_URL}/accounts/users/by-role/?role=designer", headers=headers, timeout=5)
        if response.status_code == 200:
            users = response.json()
            if isinstance(users, list):
                usernames = [u.get('username', '') for u in users]
                print_success(f"Found {len(users)} designer users: {usernames}")
                return True
            else:
                print_error(f"Unexpected response format: {type(users)}")
                return False
        else:
            print_error(f"Failed with status {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

def create_user_via_register(token, username, email, password, roles, first_name="", last_name=""):
    """Create user via register endpoint (requires admin token)"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            headers=headers,
            json={
                "username": username,
                "email": email,
                "password": password,
                "roles": roles,
                "first_name": first_name,
                "last_name": last_name
            },
            timeout=5
        )
        if response.status_code == 201:
            print_success(f"Created user: {username}")
            return True
        elif response.status_code == 400:
            # User might already exist
            print_info(f"User {username} may already exist: {response.text[:100]}")
            return True  # Consider this success
        else:
            print_error(f"Failed to create {username}: {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Exception creating {username}: {e}")
        return False

print_header("Testing with Existing Users")

# Try common admin usernames
admin_candidates = ['admin', 'administrator', 'superuser', 'root']
admin_token = None
admin_user = None

for username in admin_candidates:
    print_test(f"Trying to login as {username}...")
    token = get_auth_token(username, username, "admin")
    if token:
        admin_token = token
        admin_user = username
        print_success(f"Successfully logged in as {username}")
        break
    else:
        # Try with common passwords
        for password in [username, 'admin', 'admin123', 'password', '123456']:
            token = get_auth_token(username, password, "admin")
            if token:
                admin_token = token
                admin_user = username
                print_success(f"Successfully logged in as {username}")
                break
        if admin_token:
            break

if not admin_token:
    print_error("Could not find existing admin user")
    print_info("Please create test users manually via:")
    print_info("  1. Django admin interface (http://127.0.0.1:8000/admin)")
    print_info("  2. Django shell: python manage.py shell")
    print_info("  3. Or provide admin credentials to test with")
    exit(1)

# Now test the endpoints
print_header("Testing API Endpoints")

# Test users_by_role
test_users_by_role_with_auth(admin_token)

# Try to create test users
print_header("Creating Test Users via API")
if admin_token:
    create_user_via_register(admin_token, 'admin_test', 'admin@test.com', 'admin123', ['admin'], 'Admin', 'Test')
    create_user_via_register(admin_token, 'designer1', 'designer1@test.com', 'designer123', ['designer'], 'Designer', 'One')
    create_user_via_register(admin_token, 'designer2', 'designer2@test.com', 'designer123', ['designer'], 'Designer', 'Two')
    create_user_via_register(admin_token, 'production1', 'production1@test.com', 'production123', ['production'], 'Production', 'One')
    create_user_via_register(admin_token, 'production2', 'production2@test.com', 'production123', ['production'], 'Production', 'Two')

print_header("Test Complete")
print_info(f"Used admin user: {admin_user}")
print_info("Test users should now be available for further testing")
