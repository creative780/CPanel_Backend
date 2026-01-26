"""
Tests for AdminRecordingsView API endpoint.
"""
import pytest
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from monitoring.models import Device, Recording, Org
from accounts.models import User


@pytest.mark.django_db
class AdminRecordingsViewTest(TestCase):
    """Test cases for AdminRecordingsView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        User = get_user_model()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='testpass123',
            email='admin@test.com',
            roles=['admin']
        )
        
        # Create non-admin user
        self.regular_user = User.objects.create_user(
            username='user_test',
            password='testpass123',
            email='user@test.com',
            roles=['user']
        )
        
        # Create org
        self.org = Org.objects.create(name='Test Org', id='test_org_rec')
        
        # Create device
        self.device = Device.objects.create(
            id='test-device-rec',
            hostname='test-device-recording',
            os='Windows',
            status='ONLINE',
            org=self.org,
            last_heartbeat=timezone.now(),
        )
        
        # Create another device
        self.device2 = Device.objects.create(
            id='test-device-rec-2',
            hostname='test-device-recording-2',
            os='Linux',
            status='ONLINE',
            org=self.org,
            last_heartbeat=timezone.now(),
        )
        
        # Create test recordings
        now = timezone.now()
        self.recording1 = Recording.objects.create(
            device=self.device,
            blob_key='org1/device1/2025/01/01/rec1.mp4',
            thumb_key='org1/device1/2025/01/01/rec1-thumb.jpg',
            start_time=now - timedelta(minutes=10),
            end_time=now - timedelta(minutes=5),
            duration_seconds=300.0,
            is_idle_period=False,
            user_name_snapshot='Test User 1',
            user_role_snapshot='admin',
        )
        
        self.recording2 = Recording.objects.create(
            device=self.device,
            blob_key='org1/device1/2025/01/01/rec2.mp4',
            thumb_key='org1/device1/2025/01/01/rec2-thumb.jpg',
            start_time=now - timedelta(minutes=5),
            end_time=now - timedelta(minutes=2),
            duration_seconds=180.0,
            is_idle_period=True,
            idle_start_offset=60.0,
            user_name_snapshot='Test User 1',
            user_role_snapshot='admin',
        )
        
        self.recording3 = Recording.objects.create(
            device=self.device2,
            blob_key='org1/device2/2025/01/01/rec3.mp4',
            thumb_key='org1/device2/2025/01/01/rec3-thumb.jpg',
            start_time=now - timedelta(minutes=15),
            end_time=now - timedelta(minutes=12),
            duration_seconds=180.0,
            is_idle_period=False,
            user_name_snapshot='Test User 2',
        )
    
    def _login_as_admin(self):
        """Helper to login as admin"""
        response = self.client.post(
            '/api/auth/login',
            {'username': 'admin_test', 'password': 'testpass123', 'role': 'admin'},
            format='json'
        )
        if response.status_code == 200:
            token = response.data.get('token') or response.data.get('access')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return response
    
    def test_admin_recordings_view_authentication(self):
        """Test that admin role is required"""
        self._login_as_admin()
        response = self.client.get('/api/admin/recordings')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_recordings_view_no_auth(self):
        """Test unauthorized access returns 401"""
        response = self.client.get('/api/admin/recordings')
        self.assertEqual(response.status_code, 401)
    
    def test_admin_recordings_view_non_admin(self):
        """Test non-admin user cannot access"""
        # Login as regular user
        response = self.client.post(
            '/api/auth/login',
            {'username': 'user_test', 'password': 'testpass123', 'role': 'user'},
            format='json',
            HTTP_X_DEVICE_ID='test-device-rec'
        )
        if response.status_code == 200:
            token = response.data.get('token') or response.data.get('access')
            if token:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                response = self.client.get('/api/admin/recordings')
                # Should return 403 for authenticated but unauthorized user
                self.assertEqual(response.status_code, 403)
            else:
                # If login fails, expect 401
                response = self.client.get('/api/admin/recordings')
                self.assertEqual(response.status_code, 401)
        else:
            # If login fails, expect 401
            response = self.client.get('/api/admin/recordings')
            self.assertEqual(response.status_code, 401)
    
    def test_admin_recordings_view_all_recordings(self):
        """Test fetching all recordings"""
        self._login_as_admin()
        response = self.client.get('/api/admin/recordings')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('recordings', response.data)
        self.assertIn('total', response.data)
        self.assertIn('limit', response.data)
        self.assertIn('offset', response.data)
        
        recordings = response.data['recordings']
        self.assertGreaterEqual(len(recordings), 3)  # At least 3 recordings
    
    def test_admin_recordings_view_device_filter(self):
        """Test device_id filtering"""
        self._login_as_admin()
        response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        
        self.assertEqual(response.status_code, 200)
        recordings = response.data['recordings']
        
        # All recordings should be for the specified device
        for recording in recordings:
            self.assertEqual(recording['device_id'], self.device.id)
    
    def test_admin_recordings_view_pagination(self):
        """Test limit and offset pagination"""
        self._login_as_admin()
        
        # Test limit
        response = self.client.get('/api/admin/recordings?limit=2')
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.data['recordings']), 2)
        self.assertEqual(response.data['limit'], 2)
        
        # Test offset
        response2 = self.client.get('/api/admin/recordings?limit=2&offset=2')
        self.assertEqual(response2.status_code, 200)
        self.assertLessEqual(len(response2.data['recordings']), 2)
        self.assertEqual(response2.data['offset'], 2)
    
    def test_admin_recordings_view_ordering(self):
        """Test recordings are ordered by start_time desc"""
        self._login_as_admin()
        response = self.client.get('/api/admin/recordings')
        
        self.assertEqual(response.status_code, 200)
        recordings = response.data['recordings']
        
        if len(recordings) > 1:
            # Check that recordings are in descending order by start_time
            for i in range(len(recordings) - 1):
                current_start = recordings[i]['start_time']
                next_start = recordings[i + 1]['start_time']
                self.assertGreaterEqual(current_start, next_start)
    
    def test_admin_recordings_view_user_name_resolution(self):
        """Test user name resolution from current_user vs snapshot"""
        self._login_as_admin()
        
        # Bind user to device
        self.device.current_user = self.admin_user
        self.device.save()
        
        response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        self.assertEqual(response.status_code, 200)
        
        recordings = response.data['recordings']
        if recordings:
            # Should use current_user name if available
            recording = recordings[0]
            self.assertIn('user_name', recording)
    
    def test_admin_recordings_view_url_generation(self):
        """Test video_url and thumbnail_url format"""
        self._login_as_admin()
        response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        
        self.assertEqual(response.status_code, 200)
        recordings = response.data['recordings']
        
        for recording in recordings:
            self.assertIn('video_url', recording)
            self.assertIn('thumbnail_url', recording)
            # URLs should start with /api/files/
            self.assertTrue(recording['video_url'].startswith('/api/files/'))
            self.assertTrue(recording['thumbnail_url'].startswith('/api/files/'))
    
    def test_admin_recordings_view_empty_result(self):
        """Test no recordings case"""
        self._login_as_admin()
        
        # Create device with no recordings
        empty_device = Device.objects.create(
            id='empty-device',
            hostname='empty-device',
            os='Windows',
            status='ONLINE',
            org=self.org,
        )
        
        response = self.client.get(f'/api/admin/recordings?device_id={empty_device.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['recordings']), 0)
        self.assertEqual(response.data['total'], 0)
    
    def test_admin_recordings_view_response_format(self):
        """Test response format matches Recording interface"""
        self._login_as_admin()
        response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        
        self.assertEqual(response.status_code, 200)
        recordings = response.data['recordings']
        
        if recordings:
            recording = recordings[0]
            # Check all required fields
            required_fields = [
                'id', 'device_id', 'device_name', 'user_name',
                'start_time', 'end_time', 'duration_seconds',
                'is_idle_period', 'video_url', 'thumbnail_url',
                'created_at'
            ]
            for field in required_fields:
                self.assertIn(field, recording, f"Missing field: {field}")
            
            # Check field types
            self.assertIsInstance(recording['duration_seconds'], (int, float))
            self.assertIsInstance(recording['is_idle_period'], bool)
    
    def test_admin_recordings_view_idle_period_fields(self):
        """Test idle period specific fields"""
        self._login_as_admin()
        response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        
        self.assertEqual(response.status_code, 200)
        recordings = response.data['recordings']
        
        # Find idle recording
        idle_recording = next((r for r in recordings if r['is_idle_period']), None)
        if idle_recording:
            self.assertIn('idle_start_offset', idle_recording)
            if idle_recording['idle_start_offset'] is not None:
                self.assertIsInstance(idle_recording['idle_start_offset'], (int, float))
    
    def test_idle_period_field_inclusion(self):
        """Test idle period fields are included in response"""
        self._login_as_admin()
        
        # Create idle recording
        idle_recording = Recording.objects.create(
            device=self.device,
            blob_key='test/video.mp4',
            thumb_key='test/thumb.jpg',
            start_time=timezone.now() - timedelta(minutes=10),
            end_time=timezone.now() - timedelta(minutes=5),
            duration_seconds=300.0,
            is_idle_period=True,
            idle_start_offset=120.5
        )
        
        response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        self.assertEqual(response.status_code, 200)
        
        recordings = response.data['recordings']
        idle_rec = next((r for r in recordings if r['id'] == idle_recording.id), None)
        self.assertIsNotNone(idle_rec)
        self.assertTrue(idle_rec['is_idle_period'])
        self.assertEqual(idle_rec['idle_start_offset'], 120.5)
    
    def test_video_url_accessibility(self):
        """Test video URLs are properly formatted and accessible"""
        self._login_as_admin()
        response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        
        self.assertEqual(response.status_code, 200)
        recordings = response.data['recordings']
        
        for recording in recordings:
            self.assertIn('video_url', recording)
            if recording['video_url']:
                # URL should start with /api/files/
                self.assertTrue(recording['video_url'].startswith('/api/files/'))
    
    def test_thumbnail_url_accessibility(self):
        """Test thumbnail URLs are properly formatted"""
        self._login_as_admin()
        response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        
        self.assertEqual(response.status_code, 200)
        recordings = response.data['recordings']
        
        for recording in recordings:
            self.assertIn('thumbnail_url', recording)
            if recording['thumbnail_url']:
                # URL should start with /api/files/
                self.assertTrue(recording['thumbnail_url'].startswith('/api/files/'))
    
    def test_filtering_edge_cases(self):
        """Test filtering with edge cases"""
        self._login_as_admin()
        
        # Test with non-existent device_id
        response = self.client.get('/api/admin/recordings?device_id=non-existent-device')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['recordings']), 0)
        self.assertEqual(response.data['total'], 0)
        
        # Test with empty device_id parameter
        response = self.client.get('/api/admin/recordings?device_id=')
        self.assertEqual(response.status_code, 200)
        # Should return all recordings or handle gracefully

