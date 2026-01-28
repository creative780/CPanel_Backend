#!/usr/bin/env python
"""
Test script for login endpoint performance and timeout issues.
Tests both admin and non-admin login flows.
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')

# Initialize Django
import django
django.setup()

# Configuration
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
LOGIN_ENDPOINT = f'{BASE_URL}/api/auth/login'

# Test credentials (adjust as needed)
TEST_ADMIN = {
    'username': 'check3',
    'password': 'your_password_here',  # Update with actual password
    'role': 'admin'
}

TEST_USER = {
    'username': 'testuser',
    'password': 'your_password_here',  # Update with actual password
    'role': 'user',
    'device_id': 'test-device-id'  # For non-admin login
}


def test_login(credentials, test_name):
    """Test login endpoint and measure performance"""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")
    print(f"Username: {credentials['username']}")
    print(f"Role: {credentials['role']}")
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Add device ID header for non-admin users
    if credentials.get('device_id'):
        headers['X-Device-ID'] = credentials['device_id']
    
    payload = {
        'username': credentials['username'],
        'password': credentials['password'],
        'role': credentials['role']
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            LOGIN_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Time: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login Successful!")
            print(f"   Token received: {len(data.get('token', ''))} characters")
            print(f"   Username: {data.get('username', 'N/A')}")
            print(f"   Role: {data.get('role', 'N/A')}")
            return True, elapsed_time
        elif response.status_code == 412:
            data = response.json()
            print(f"⚠️  Precondition Failed (Expected for non-admin without device)")
            print(f"   Error: {data.get('error', 'N/A')}")
            return False, elapsed_time
        else:
            try:
                data = response.json()
                print(f"❌ Login Failed")
                print(f"   Error: {data.get('detail', data.get('error', 'Unknown error'))}")
            except:
                print(f"❌ Login Failed")
                print(f"   Response: {response.text[:200]}")
            return False, elapsed_time
            
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"\n❌ Request Timed Out after {elapsed_time:.2f} seconds")
        print(f"   This indicates the server is not responding in time")
        return False, elapsed_time
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error")
        print(f"   Could not connect to {BASE_URL}")
        print(f"   Make sure the server is running")
        return False, None
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ Error: {str(e)}")
        return False, elapsed_time


def test_health_check():
    """Test if server is reachable"""
    print(f"\n{'='*60}")
    print("Health Check")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f'{BASE_URL}/healthz', timeout=5)
        if response.status_code == 200:
            print("✅ Server is reachable")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server is not reachable: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Login Endpoint Performance Test")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test health check first
    if not test_health_check():
        print("\n⚠️  Server health check failed. Please start the server first.")
        print("   Use: python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application")
        return
    
    results = []
    
    # Test admin login
    if TEST_ADMIN.get('password') and TEST_ADMIN['password'] != 'your_password_here':
        success, elapsed = test_login(TEST_ADMIN, "Admin Login")
        results.append(('Admin Login', success, elapsed))
    else:
        print("\n⚠️  Skipping admin login test - password not configured")
    
    # Test non-admin login (will likely fail without device, but tests the endpoint)
    if TEST_USER.get('password') and TEST_USER['password'] != 'your_password_here':
        success, elapsed = test_login(TEST_USER, "Non-Admin Login (with device)")
        results.append(('Non-Admin Login', success, elapsed))
    else:
        print("\n⚠️  Skipping non-admin login test - password not configured")
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    for test_name, success, elapsed in results:
        status = "✅ PASS" if success else "❌ FAIL"
        time_str = f"{elapsed:.2f}s" if elapsed else "N/A"
        print(f"{status} - {test_name}: {time_str}")
    
    # Performance check
    print(f"\n{'='*60}")
    print("Performance Analysis")
    print(f"{'='*60}")
    
    successful_times = [elapsed for _, success, elapsed in results if success and elapsed]
    if successful_times:
        avg_time = sum(successful_times) / len(successful_times)
        max_time = max(successful_times)
        min_time = min(successful_times)
        
        print(f"Average response time: {avg_time:.2f} seconds")
        print(f"Fastest response: {min_time:.2f} seconds")
        print(f"Slowest response: {max_time:.2f} seconds")
        
        if avg_time > 2.0:
            print("\n⚠️  WARNING: Average response time is > 2 seconds")
            print("   This may indicate performance issues")
        else:
            print("\n✅ Response times are acceptable (< 2 seconds)")
    
    print(f"\n{'='*60}")
    print("Test Complete")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()





























