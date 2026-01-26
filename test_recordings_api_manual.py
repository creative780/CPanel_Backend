"""
Standalone manual test script for AdminRecordingsView API endpoint.
Run with: python test_recordings_api_manual.py
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
django.setup()

from django.test import Client, override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from monitoring.models import Device, Recording, Org
from monitoring.auth_utils import create_device_token


def print_result(test_name, passed, details=""):
    """Print test result"""
    status = "[OK]" if passed else "[ERROR]"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")


@override_settings(ALLOWED_HOSTS=['*'])
def main():
    """Run manual tests"""
    print("=" * 70)
    print("ADMIN RECORDINGS API MANUAL TEST")
    print("=" * 70)
    print()
    
    client = APIClient()
    User = get_user_model()
    
    # Setup: Create test data
    print("Setting up test data...")
    try:
        org, _ = Org.objects.get_or_create(name='Test Org Manual', defaults={'id': 'test_org_manual'})
        
        device, _ = Device.objects.get_or_create(
            id='test-device-manual',
            defaults={
                'hostname': 'test-device-manual',
                'os': 'Windows',
                'status': 'ONLINE',
                'org': org,
                'last_heartbeat': timezone.now(),
            }
        )
        
        # Create admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin_manual_test',
            defaults={
                'email': 'admin_manual@test.com',
                'roles': ['admin']
            }
        )
        admin_user.set_password('testpass123')
        admin_user.save()
        
        # Create test recordings
        now = timezone.now()
        recording1, _ = Recording.objects.get_or_create(
            id='rec_manual_1',
            defaults={
                'device': device,
                'blob_key': 'org1/device1/2025/01/01/rec_manual_1.mp4',
                'thumb_key': 'org1/device1/2025/01/01/rec_manual_1-thumb.jpg',
                'start_time': now - timedelta(minutes=10),
                'end_time': now - timedelta(minutes=5),
                'duration_seconds': 300.0,
                'is_idle_period': False,
                'user_name_snapshot': 'Test User Manual',
            }
        )
        
        recording2, _ = Recording.objects.get_or_create(
            id='rec_manual_2',
            defaults={
                'device': device,
                'blob_key': 'org1/device1/2025/01/01/rec_manual_2.mp4',
                'thumb_key': 'org1/device1/2025/01/01/rec_manual_2-thumb.jpg',
                'start_time': now - timedelta(minutes=5),
                'end_time': now - timedelta(minutes=2),
                'duration_seconds': 180.0,
                'is_idle_period': True,
                'idle_start_offset': 60.0,
                'user_name_snapshot': 'Test User Manual',
            }
        )
        
        print("Test data created successfully")
        print()
    except Exception as e:
        print(f"[ERROR] Failed to setup test data: {e}")
        return
    
    # Test 1: No authentication
    print("Test 1: GET /api/admin/recordings without auth")
    response = client.get('/api/admin/recordings')
    passed = response.status_code == 403
    print_result("Unauthorized access", passed, f"Status: {response.status_code}")
    print()
    
    # Test 2: Login and get token
    print("Test 2: Login as admin")
    login_response = client.post(
        '/api/auth/login',
        {'username': 'admin_manual_test', 'password': 'testpass123', 'role': 'admin'},
        format='json'
    )
    if login_response.status_code == 200:
        token = login_response.data.get('token') or login_response.data.get('access')
        if token:
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            print_result("Login successful", True, f"Token obtained")
        else:
            print_result("Login successful", False, "No token in response")
            return
    else:
        print_result("Login failed", False, f"Status: {login_response.status_code}")
        return
    print()
    
    # Test 3: Get all recordings
    print("Test 3: GET /api/admin/recordings (all recordings)")
    response = client.get('/api/admin/recordings')
    passed = response.status_code == 200
    if passed:
        recordings = response.data.get('recordings', [])
        total = response.data.get('total', 0)
        print_result("Get all recordings", True, f"Found {len(recordings)} recordings (total: {total})")
        if recordings:
            rec = recordings[0]
            print(f"    Sample recording: id={rec.get('id')}, device={rec.get('device_name')}, duration={rec.get('duration_seconds')}s")
    else:
        print_result("Get all recordings", False, f"Status: {response.status_code}")
    print()
    
    # Test 4: Filter by device_id
    print(f"Test 4: GET /api/admin/recordings?device_id={device.id}")
    response = client.get(f'/api/admin/recordings?device_id={device.id}')
    passed = response.status_code == 200
    if passed:
        recordings = response.data.get('recordings', [])
        all_for_device = all(r['device_id'] == device.id for r in recordings)
        print_result("Filter by device_id", all_for_device, f"Found {len(recordings)} recordings for device")
    else:
        print_result("Filter by device_id", False, f"Status: {response.status_code}")
    print()
    
    # Test 5: Pagination
    print("Test 5: GET /api/admin/recordings?limit=1&offset=0")
    response = client.get('/api/admin/recordings?limit=1&offset=0')
    passed = response.status_code == 200
    if passed:
        recordings = response.data.get('recordings', [])
        limit = response.data.get('limit', 0)
        offset = response.data.get('offset', 0)
        print_result("Pagination", len(recordings) <= 1, f"limit={limit}, offset={offset}, returned={len(recordings)}")
    else:
        print_result("Pagination", False, f"Status: {response.status_code}")
    print()
    
    # Test 6: Verify response format
    print("Test 6: Verify response format")
    response = client.get(f'/api/admin/recordings?device_id={device.id}')
    if response.status_code == 200:
        recordings = response.data.get('recordings', [])
        if recordings:
            rec = recordings[0]
            required_fields = [
                'id', 'device_id', 'device_name', 'user_name',
                'start_time', 'end_time', 'duration_seconds',
                'is_idle_period', 'video_url', 'thumbnail_url', 'created_at'
            ]
            missing = [f for f in required_fields if f not in rec]
            passed = len(missing) == 0
            print_result("Response format", passed, f"Missing fields: {missing}" if missing else "All fields present")
            
            # Check URL format
            if 'video_url' in rec and 'thumbnail_url' in rec:
                url_ok = rec['video_url'].startswith('/api/files/') and rec['thumbnail_url'].startswith('/api/files/')
                print_result("URL format", url_ok, f"video_url={rec['video_url'][:50]}...")
        else:
            print_result("Response format", False, "No recordings to check")
    else:
        print_result("Response format", False, f"Status: {response.status_code}")
    print()
    
    print("=" * 70)
    print("MANUAL TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()

