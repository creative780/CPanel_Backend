#!/usr/bin/env python
"""Simple API test to check if server is responding"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

print("Testing API Endpoints...\n")

# Test 1: Check if server is running
print("1. Testing server connection...")
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   [OK] Server is responding")
except Exception as e:
    print(f"   [FAIL] Cannot connect to server: {e}")
    exit(1)

# Test 2: Check users_by_role endpoint (without auth first)
print("\n2. Testing users_by_role endpoint (unauthenticated)...")
try:
    response = requests.get(f"{API_URL}/accounts/users/by-role/?role=designer", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   [OK] Endpoint exists and requires authentication (expected)")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

# Test 3: Check endpoint with missing role parameter
print("\n3. Testing users_by_role endpoint (missing role parameter)...")
try:
    response = requests.get(f"{API_URL}/accounts/users/by-role/", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code in [400, 401]:
        print(f"   [OK] Endpoint handles missing parameter correctly")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

print("\n=== Basic endpoint tests complete ===")
print("\nNote: Full testing requires authentication with existing users.")
print("Please ensure:")
print("  1. Backend server is running on port 8000")
print("  2. Test users exist in the database")
print("  3. Migrations have been run")
