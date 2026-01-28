"""
Integration tests for recording system - end-to-end tests
"""
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import timedelta
from monitoring.models import Device, Recording, Org, DeviceToken
from monitoring.auth_utils import create_device_token
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User


class RecordingIntegrationTest(TestCase):
    """End-to-end integration tests for recording system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        User = get_user_model()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_integration',
            password='testpass123',
            email='admin@test.com',
            roles=['admin']
        )
        
        # Create org and device
        self.org = Org.objects.create(name="Integration Test Org")
        self.device = Device.objects.create(
            hostname="integration-test-device",
            os="Windows",
            status="ONLINE",
            org=self.org
        )
        
        # Create device token
        self.token_obj = create_device_token(self.device)
        self.device_token = self.token_obj.token
        
        # Test video data
        self.video_data = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom' + (b'\x00' * 1000)
        self.start_time = timezone.now() - timedelta(minutes=5)
        self.end_time = timezone.now()
        self.duration_seconds = 300.0
    
    def _login_as_admin(self):
        """Helper to login as admin"""
        response = self.client.post(
            '/api/auth/login',
            {'username': 'admin_integration', 'password': 'testpass123', 'role': 'admin'},
            format='json'
        )
        if response.status_code == 200:
            token = response.data.get('token') or response.data.get('access')
            if token:
                self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return response
    
    def _get_test_video_file(self):
        """Get a test video file"""
        return SimpleUploadedFile('clip.mp4', self.video_data, content_type='video/mp4')
    
    def test_end_to_end_recording_lifecycle(self):
        """Test complete recording lifecycle: upload -> storage -> retrieval -> admin view"""
        # Step 1: Device uploads recording
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds),
        }
        
        video_file = self._get_test_video_file()
        files = {'video': video_file}
        
        upload_response = self.client.post(
            '/api/ingest/recording',
            data=data,
            files=files,
            format='multipart'
        )
        
        self.assertEqual(upload_response.status_code, status.HTTP_200_OK)
        self.assertEqual(upload_response.json()['status'], 'ok')
        
        # Step 2: Verify recording in database
        recording = Recording.objects.filter(device=self.device).first()
        self.assertIsNotNone(recording)
        self.assertEqual(recording.device, self.device)
        self.assertIsNotNone(recording.blob_key)
        self.assertEqual(recording.duration_seconds, self.duration_seconds)
        
        # Step 3: Admin views recording
        self._login_as_admin()
        
        list_response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        
        recordings = list_response.data['recordings']
        self.assertGreater(len(recordings), 0)
        
        # Find our recording
        found_recording = next(
            (r for r in recordings if r['id'] == recording.id),
            None
        )
        self.assertIsNotNone(found_recording)
        self.assertEqual(found_recording['device_id'], self.device.id)
        self.assertIn('video_url', found_recording)
        self.assertIn('thumbnail_url', found_recording)
    
    def test_multiple_recordings_from_same_device(self):
        """Test multiple recordings from the same device"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        # Upload 3 recordings
        for i in range(3):
            data = {
                'start_time': (self.start_time - timedelta(minutes=i*10)).isoformat(),
                'end_time': (self.end_time - timedelta(minutes=i*10)).isoformat(),
                'duration_seconds': str(self.duration_seconds),
            }
            
            video_file = self._get_test_video_file()
            files = {'video': video_file}
            
            response = self.client.post(
                '/api/ingest/recording',
                data=data,
                files=files,
                format='multipart'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all recordings exist
        recordings = Recording.objects.filter(device=self.device)
        self.assertEqual(recordings.count(), 3)
        
        # Admin should see all 3
        self._login_as_admin()
        list_response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_response.data['recordings']), 3)
        self.assertGreaterEqual(list_response.data['total'], 3)
    
    def test_recording_with_user_binding_changes(self):
        """Test recording captures user snapshot even when user binding changes"""
        # Create user and bind to device
        user = User.objects.create_user(
            username='testuser_integration',
            email='user@test.com',
            password='testpass'
        )
        self.device.current_user = user
        self.device.current_user_name = 'Test User'
        self.device.current_user_role = 'employee'
        self.device.save()
        
        # Upload recording
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds),
        }
        
        video_file = self._get_test_video_file()
        files = {'video': video_file}
        
        response = self.client.post(
            '/api/ingest/recording',
            data=data,
            files=files,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify snapshot was captured
        recording = Recording.objects.filter(device=self.device).first()
        self.assertIsNotNone(recording)
        self.assertEqual(recording.user_id_snapshot, user.id)
        self.assertEqual(recording.user_name_snapshot, 'Test User')
        self.assertEqual(recording.user_role_snapshot, 'employee')
        
        # Change user binding
        new_user = User.objects.create_user(
            username='newuser_integration',
            email='newuser@test.com',
            password='testpass'
        )
        self.device.current_user = new_user
        self.device.current_user_name = 'New User'
        self.device.save()
        
        # Upload another recording
        data2 = {
            'start_time': (self.start_time + timedelta(minutes=10)).isoformat(),
            'end_time': (self.end_time + timedelta(minutes=10)).isoformat(),
            'duration_seconds': str(self.duration_seconds),
        }
        
        video_file2 = self._get_test_video_file()
        files2 = {'video': video_file2}
        
        response2 = self.client.post(
            '/api/ingest/recording',
            data=data2,
            files=files2,
            format='multipart'
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify new recording has new user snapshot
        new_recording = Recording.objects.filter(device=self.device).order_by('-created_at').first()
        self.assertIsNotNone(new_recording)
        self.assertEqual(new_recording.user_id_snapshot, new_user.id)
        self.assertEqual(new_recording.user_name_snapshot, 'New User')
        
        # Old recording should still have old snapshot
        self.assertEqual(recording.user_id_snapshot, user.id)
        self.assertEqual(recording.user_name_snapshot, 'Test User')
    
    def test_recording_ordering(self):
        """Test recordings are ordered correctly (newest first)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        # Upload recordings with different timestamps
        timestamps = [
            (self.start_time - timedelta(minutes=30), self.end_time - timedelta(minutes=30)),
            (self.start_time - timedelta(minutes=20), self.end_time - timedelta(minutes=20)),
            (self.start_time - timedelta(minutes=10), self.end_time - timedelta(minutes=10)),
        ]
        
        for start, end in timestamps:
            data = {
                'start_time': start.isoformat(),
                'end_time': end.isoformat(),
                'duration_seconds': str(self.duration_seconds),
            }
            
            video_file = self._get_test_video_file()
            files = {'video': video_file}
            
            self.client.post(
                '/api/ingest/recording',
                data=data,
                files=files,
                format='multipart'
            )
        
        # Admin should see them in descending order (newest first)
        self._login_as_admin()
        list_response = self.client.get(f'/api/admin/recordings?device_id={self.device.id}')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        
        recordings = list_response.data['recordings']
        if len(recordings) >= 3:
            # Check ordering (start_time should be descending)
            for i in range(len(recordings) - 1):
                current_start = recordings[i]['start_time']
                next_start = recordings[i + 1]['start_time']
                self.assertGreaterEqual(current_start, next_start)


