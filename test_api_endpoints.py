#!/usr/bin/env python
"""
Test API endpoints for order assignment implementation
Tests the running server via HTTP requests
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
    print(f"→ {test_name}...")

def print_success(message=""):
    print(f"  [OK] {message}")

def print_error(message):
    print(f"  [FAIL] {message}")

def get_auth_token(username, password):
    """Get authentication token"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password, "role": "admin"}
        )
        if response.status_code == 200:
            return response.json().get('access')
        return None
    except Exception as e:
        print_error(f"Failed to get token: {e}")
        return None

def test_users_by_role():
    """Test 1: Users by Role Endpoint"""
    print_header("Test 1: Users by Role Endpoint")
    
    # Get auth token
    token = get_auth_token('admin_test', 'admin123')
    if not token:
        print_error("Failed to get auth token - check if test users exist")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test designer role
    print_test("Fetching designer users")
    try:
        response = requests.get(f"{API_URL}/accounts/users/by-role/?role=designer", headers=headers)
        if response.status_code == 200:
            users = response.json()
            if isinstance(users, list):
                usernames = [u.get('username') for u in users]
                print_success(f"Found {len(users)} designer users: {usernames}")
                return True
            else:
                print_error(f"Unexpected response format: {type(users)}")
                return False
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False
    
    # Test production role
    print_test("Fetching production users")
    try:
        response = requests.get(f"{API_URL}/accounts/users/by-role/?role=production", headers=headers)
        if response.status_code == 200:
            users = response.json()
            if isinstance(users, list):
                usernames = [u.get('username') for u in users]
                print_success(f"Found {len(users)} production users: {usernames}")
                return True
            else:
                print_error(f"Unexpected response format: {type(users)}")
                return False
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

def test_order_creation():
    """Test 2: Order Creation with Assignments"""
    print_header("Test 2: Order Creation with Assignments")
    
    token = get_auth_token('admin_test', 'admin123')
    if not token:
        print_error("Failed to get auth token")
        return False
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test order with assigned designer
    print_test("Creating order with assigned designer")
    order_data = {
        "clientName": "Test Client",
        "items": [{
            "name": "Test Product",
            "quantity": 1,
            "unit_price": 10.00
        }],
        "assignedDesigner": "designer1"
    }
    
    try:
        response = requests.post(f"{API_URL}/orders/", headers=headers, json=order_data)
        if response.status_code == 201:
            order = response.json().get('data', {})
            order_id = order.get('id')
            print_success(f"Order {order_id} created with designer assignment")
            return True
        else:
            print_error(f"Failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False

if __name__ == '__main__':
    print_header("API Endpoint Testing")
    
    results = []
    results.append(("Users by Role Endpoint", test_users_by_role()))
    results.append(("Order Creation with Assignments", test_order_creation()))
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  SUCCESS: All tests passed!")
    else:
        print(f"\n  WARNING: {total - passed} test(s) failed")
