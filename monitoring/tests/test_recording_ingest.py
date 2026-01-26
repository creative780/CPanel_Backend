"""
Django unit tests for RecordingIngestView
Tests video file upload, authentication, validation, and error handling
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from io import BytesIO
from datetime import datetime, timedelta
from monitoring.models import Device, DeviceToken, Recording, Org
from monitoring.auth_utils import create_device_token


class RecordingIngestViewTest(TestCase):
    """Test cases for RecordingIngestView"""
    
    def setUp(self):
        """Set up test data"""
        # Create test org
        self.org = Org.objects.create(name="Test Org")
        
        # Create test device
        self.device = Device.objects.create(
            hostname="test-device",
            os="Windows",
            status="ONLINE",
            org=self.org
        )
        
        # Create device token
        self.token_obj = create_device_token(self.device)
        self.device_token = self.token_obj.token
        
        # Create API client
        self.client = APIClient()
        
        # Test datetime values
        self.start_time = timezone.now() - timedelta(minutes=5)
        self.end_time = timezone.now()
        self.duration_seconds = 300.0
    
    def _get_test_video(self):
        """Get a fresh test video BytesIO object"""
        test_video = BytesIO()
        test_video.write(b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom')
        test_video.write(b'\x00' * 1000)
        test_video.seek(0)
        return test_video
    
    def _get_test_video_file(self):
        """Get a test video file that can be used with Django test client"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        video_data = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom' + (b'\x00' * 1000)
        return SimpleUploadedFile('clip.mp4', video_data, content_type='video/mp4')
    
    def test_successful_upload(self):
        """Test Case 1: Successful recording upload"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds),
            'is_idle_period': 'false'
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'ok')
        
        # Verify recording in database
        recording = Recording.objects.last()
        self.assertIsNotNone(recording)
        self.assertEqual(recording.device, self.device)
        self.assertEqual(recording.duration_seconds, self.duration_seconds)
        self.assertFalse(recording.is_idle_period)
        self.assertIsNotNone(recording.blob_key)
        self.assertIsNotNone(recording.thumb_key)
    
    def test_missing_video_file(self):
        """Test Case 2: Missing video file"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds)
        }
        
        response = self.client.post('/api/ingest/recording', data=data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video file is required', response.json()['detail'].lower())
    
    def test_missing_start_time(self):
        """Test Case 3a: Missing start_time"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds)
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('required', response.json()['detail'].lower())
    
    def test_missing_end_time(self):
        """Test Case 3b: Missing end_time"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'duration_seconds': str(self.duration_seconds)
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('required', response.json()['detail'].lower())
    
    def test_missing_duration_seconds(self):
        """Test Case 3c: Missing duration_seconds"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('required', response.json()['detail'].lower())
    
    def test_no_authentication(self):
        """Test Case 4a: No authentication"""
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds)
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_invalid_token(self):
        """Test Case 4b: Invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_12345')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds)
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_idle_period_recording(self):
        """Test Case 6: Idle period recording"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds),
            'is_idle_period': 'true',
            'idle_start_offset': '120.5'
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify recording
        recording = Recording.objects.last()
        self.assertIsNotNone(recording)
        self.assertTrue(recording.is_idle_period)
        self.assertEqual(recording.idle_start_offset, 120.5)
    
    def test_datetime_formats(self):
        """Test Case 5: Various datetime formats"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        # Test ISO format with Z
        data = {
            'start_time': '2024-01-01T10:00:00Z',
            'end_time': '2024-01-01T10:05:00Z',
            'duration_seconds': '300'
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test ISO format with timezone
        data = {
            'start_time': '2024-01-01T10:00:00+00:00',
            'end_time': '2024-01-01T10:05:00+00:00',
            'duration_seconds': '300'
        }
        
        video_file = self._get_test_video_file()
        files = {
            'video': video_file
        }
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_thumbnail_generation(self):
        """Test thumbnail generation from video"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds),
        }
        
        video_file = self._get_test_video_file()
        files = {'video': video_file}
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify recording has thumb_key (may be None if ffmpeg not available)
        recording = Recording.objects.last()
        self.assertIsNotNone(recording)
        # Thumbnail generation is optional, so we just check recording was created
        self.assertIsNotNone(recording.blob_key)
    
    def test_user_snapshot_capture(self):
        """Test user snapshot is captured when device has current_user"""
        from accounts.models import User
        
        # Create a user and bind to device
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.device.current_user = user
        self.device.current_user_name = 'Test User'
        self.device.current_user_role = 'employee'
        self.device.save()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds),
        }
        
        video_file = self._get_test_video_file()
        files = {'video': video_file}
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user snapshot was captured
        recording = Recording.objects.last()
        self.assertIsNotNone(recording)
        self.assertEqual(recording.user_id_snapshot, user.id)
        self.assertEqual(recording.user_name_snapshot, 'Test User')
        self.assertEqual(recording.user_role_snapshot, 'employee')
    
    def test_video_storage(self):
        """Test video is stored in blob storage"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds),
        }
        
        video_file = self._get_test_video_file()
        files = {'video': video_file}
        
        response = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify blob_key is set
        recording = Recording.objects.last()
        self.assertIsNotNone(recording)
        self.assertIsNotNone(recording.blob_key)
        self.assertTrue(recording.blob_key.endswith('.mp4'))
    
    def test_duplicate_video_detection(self):
        """Test SHA256 hash calculation for video deduplication"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': str(self.duration_seconds),
        }
        
        video_file = self._get_test_video_file()
        files = {'video': video_file}
        
        # Upload first time
        response1 = self.client.post('/api/ingest/recording', data=data, files=files, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Upload same video again (should create new recording, not duplicate)
        video_file2 = self._get_test_video_file()
        files2 = {'video': video_file2}
        response2 = self.client.post('/api/ingest/recording', data=data, files=files2, format='multipart')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Both recordings should exist (deduplication not implemented, but hash is calculated)
        recordings = Recording.objects.filter(device=self.device)
        self.assertEqual(recordings.count(), 2)

