#!/usr/bin/env python
"""
Quick script to check if Django server is running and accessible
"""
import sys
import requests
from urllib.parse import urljoin

def check_server(base_url='http://127.0.0.1:8000'):
    """Check if the Django server is running and accessible"""
    try:
        # Test health endpoint
        health_url = urljoin(base_url, '/healthz')
        print(f"Testing health endpoint: {health_url}")
        response = requests.get(health_url, timeout=2)
        
        if response.status_code == 200:
            print("✅ Server is running and accessible!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print(f"   Try: python manage.py runserver 0.0.0.0:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server connection timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000'
    success = check_server(base)
    sys.exit(0 if success else 1)

