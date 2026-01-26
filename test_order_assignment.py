#!/usr/bin/env python
"""
Test script for Order Assignment and Visibility Implementation

This script tests:
1. Users by role endpoint
2. Order creation with assignments
3. Order visibility filtering

Usage:
    python test_order_assignment.py
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from django.utils import timezone
from rest_framework.test import APIClient
from accounts.models import Role

User = get_user_model()

# Test configuration
BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
API_URL = f'{BASE_URL}/api'

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_test(test_name):
    print(f"→ {test_name}...")

def print_success(message=""):
    print(f"  ✓ {message}")

def print_error(message):
    print(f"  ✗ {message}")

def create_test_user(username, password, roles, email=None):
    """Create or get test user"""
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.roles = roles
        user.is_active = True
        user.save()
        return user
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email or f"{username}@test.com",
            password=password,
            roles=roles,
            is_active=True
        )
        return user

def get_auth_token(username, password):
    """Get authentication token"""
    client = APIClient()
    response = client.post('/api/auth/login', {
        'username': username,
        'password': password
    }, format='json')
    if response.status_code == 200:
        return response.data.get('access')
    return None

def test_users_by_role():
    """Test 1: Users by Role Endpoint"""
    print_header("Test 1: Users by Role Endpoint")
    
    # Create test users
    admin = create_test_user('admin_test', 'admin123', ['admin'], 'admin@test.com')
    designer1 = create_test_user('designer1', 'designer123', ['designer'], 'designer1@test.com')
    designer2 = create_test_user('designer2', 'designer123', ['designer'], 'designer2@test.com')
    production1 = create_test_user('production1', 'production123', ['production'], 'production1@test.com')
    production2 = create_test_user('production2', 'production123', ['production'], 'production2@test.com')
    
    client = APIClient()
    token = get_auth_token('admin_test', 'admin123')
    
    if not token:
        print_error("Failed to get auth token")
        return False
    
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Test designer role
    print_test("Fetching designer users")
    response = client.get('/api/accounts/users/by-role/?role=designer')
    if response.status_code == 200:
        users = response.data
        designer_usernames = [u['username'] for u in users]
        if 'designer1' in designer_usernames and 'designer2' in designer_usernames:
            print_success(f"Found {len(users)} designer users: {designer_usernames}")
        else:
            print_error(f"Missing designer users. Found: {designer_usernames}")
            return False
    else:
        print_error(f"Failed with status {response.status_code}: {response.data}")
        return False
    
    # Test production role
    print_test("Fetching production users")
    response = client.get('/api/accounts/users/by-role/?role=production')
    if response.status_code == 200:
        users = response.data
        production_usernames = [u['username'] for u in users]
        if 'production1' in production_usernames and 'production2' in production_usernames:
            print_success(f"Found {len(users)} production users: {production_usernames}")
        else:
            print_error(f"Missing production users. Found: {production_usernames}")
            return False
    else:
        print_error(f"Failed with status {response.status_code}: {response.data}")
        return False
    
    # Test missing role parameter
    print_test("Testing missing role parameter")
    response = client.get('/api/accounts/users/by-role/')
    if response.status_code == 400:
        print_success("Correctly returns 400 for missing role parameter")
    else:
        print_error(f"Expected 400, got {response.status_code}")
        return False
    
    return True

def test_order_creation_with_assignments():
    """Test 2: Order Creation with Assignments"""
    print_header("Test 2: Order Creation with Assignments")
    
    client = APIClient()
    token = get_auth_token('admin_test', 'admin123')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    designer1 = User.objects.get(username='designer1')
    production1 = User.objects.get(username='production1')
    
    # Test order with assigned designer
    print_test("Creating order with assigned designer")
    order_data = {
        'clientName': 'Test Client',
        'items': [{
            'name': 'Test Product',
            'quantity': 1,
            'unit_price': 10.00
        }],
        'assignedDesigner': designer1.username
    }
    response = client.post('/api/orders/', order_data, format='json')
    if response.status_code == 201:
        order_id = response.data['data']['id']
        order = Order.objects.get(id=order_id)
        if order.assigned_designer == designer1.username:
            print_success(f"Order {order_id} created with designer assignment: {order.assigned_designer}")
        else:
            print_error(f"Designer assignment mismatch. Expected: {designer1.username}, Got: {order.assigned_designer}")
            return False
    else:
        print_error(f"Failed to create order with status {response.status_code}: {response.data}")
        return False
    
    # Test order with assigned production person
    print_test("Creating order with assigned production person")
    order_data = {
        'clientName': 'Test Client 2',
        'items': [{
            'name': 'Test Product 2',
            'quantity': 1,
            'unit_price': 20.00
        }],
        'assignedProductionPerson': production1.username
    }
    response = client.post('/api/orders/', order_data, format='json')
    if response.status_code == 201:
        order_id = response.data['data']['id']
        order = Order.objects.get(id=order_id)
        if order.assigned_production_person == production1.username:
            print_success(f"Order {order_id} created with production assignment: {order.assigned_production_person}")
        else:
            print_error(f"Production assignment mismatch. Expected: {production1.username}, Got: {order.assigned_production_person}")
            return False
    else:
        print_error(f"Failed to create order with status {response.status_code}: {response.data}")
        return False
    
    # Test order with both assignments
    print_test("Creating order with both assignments")
    order_data = {
        'clientName': 'Test Client 3',
        'items': [{
            'name': 'Test Product 3',
            'quantity': 1,
            'unit_price': 30.00
        }],
        'assignedDesigner': designer1.username,
        'assignedProductionPerson': production1.username
    }
    response = client.post('/api/orders/', order_data, format='json')
    if response.status_code == 201:
        order_id = response.data['data']['id']
        order = Order.objects.get(id=order_id)
        if order.assigned_designer == designer1.username and order.assigned_production_person == production1.username:
            print_success(f"Order {order_id} created with both assignments")
        else:
            print_error(f"Both assignments not set correctly")
            return False
    else:
        print_error(f"Failed to create order with status {response.status_code}: {response.data}")
        return False
    
    # Test order without assignments (backward compatibility)
    print_test("Creating order without assignments")
    order_data = {
        'clientName': 'Test Client 4',
        'items': [{
            'name': 'Test Product 4',
            'quantity': 1,
            'unit_price': 40.00
        }]
    }
    response = client.post('/api/orders/', order_data, format='json')
    if response.status_code == 201:
        order_id = response.data['data']['id']
        order = Order.objects.get(id=order_id)
        if not order.assigned_designer and not order.assigned_production_person:
            print_success(f"Order {order_id} created without assignments (backward compatibility)")
        else:
            print_error("Order should not have assignments")
            return False
    else:
        print_error(f"Failed to create order with status {response.status_code}: {response.data}")
        return False
    
    return True

def test_order_visibility_filtering():
    """Test 3: Order Visibility Filtering"""
    print_header("Test 3: Order Visibility Filtering")
    
    designer1 = User.objects.get(username='designer1')
    designer2 = User.objects.get(username='designer2')
    production1 = User.objects.get(username='production1')
    production2 = User.objects.get(username='production2')
    admin = User.objects.get(username='admin_test')
    
    # Create test orders
    order1 = Order.objects.create(
        order_code='TEST-001',
        client_name='Client 1',
        assigned_designer=designer1.username
    )
    order2 = Order.objects.create(
        order_code='TEST-002',
        client_name='Client 2',
        assigned_production_person=production1.username
    )
    order3 = Order.objects.create(
        order_code='TEST-003',
        client_name='Client 3',
        assigned_designer=designer2.username
    )
    order4 = Order.objects.create(
        order_code='TEST-004',
        client_name='Client 4'
        # No assignments
    )
    
    # Test as admin - should see all orders
    print_test("Testing admin visibility (should see all orders)")
    client = APIClient()
    token = get_auth_token('admin_test', 'admin123')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.get('/api/orders/')
    if response.status_code == 200:
        order_codes = [o['order_code'] for o in response.data]
        if all(code in order_codes for code in ['TEST-001', 'TEST-002', 'TEST-003', 'TEST-004']):
            print_success(f"Admin sees all {len(order_codes)} orders")
        else:
            print_error(f"Admin missing orders. Found: {order_codes}")
            return False
    else:
        print_error(f"Failed with status {response.status_code}")
        return False
    
    # Test as designer1 - should see order1 (assigned) and order4 (unassigned)
    print_test(f"Testing designer1 visibility (should see TEST-001 and TEST-004)")
    token = get_auth_token('designer1', 'designer123')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.get('/api/orders/')
    if response.status_code == 200:
        order_codes = [o['order_code'] for o in response.data]
        if 'TEST-001' in order_codes and 'TEST-004' in order_codes:
            if 'TEST-003' not in order_codes:  # Should NOT see order assigned to designer2
                print_success(f"Designer1 sees assigned and unassigned orders: {order_codes}")
            else:
                print_error("Designer1 should not see TEST-003 (assigned to designer2)")
                return False
        else:
            print_error(f"Designer1 missing required orders. Found: {order_codes}")
            return False
    else:
        print_error(f"Failed with status {response.status_code}")
        return False
    
    # Test as production1 - should see order2 (assigned) and order4 (unassigned)
    print_test(f"Testing production1 visibility (should see TEST-002 and TEST-004)")
    token = get_auth_token('production1', 'production123')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.get('/api/orders/')
    if response.status_code == 200:
        order_codes = [o['order_code'] for o in response.data]
        if 'TEST-002' in order_codes and 'TEST-004' in order_codes:
            if 'TEST-001' not in order_codes:  # Should NOT see order assigned to designer
                print_success(f"Production1 sees assigned and unassigned orders: {order_codes}")
            else:
                print_error("Production1 should not see TEST-001 (assigned to designer)")
                return False
        else:
            print_error(f"Production1 missing required orders. Found: {order_codes}")
            return False
    else:
        print_error(f"Failed with status {response.status_code}")
        return False
    
    # Cleanup test orders
    Order.objects.filter(order_code__startswith='TEST-').delete()
    
    return True

def main():
    """Run all tests"""
    print_header("Order Assignment Implementation Test Suite")
    
    results = []
    
    # Run tests
    results.append(("Users by Role Endpoint", test_users_by_role()))
    results.append(("Order Creation with Assignments", test_order_creation_with_assignments()))
    results.append(("Order Visibility Filtering", test_order_visibility_filtering()))
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed!")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
