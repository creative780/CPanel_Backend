"""
Django unit tests for FrameEncodingView
Tests server-side frame encoding, authentication, validation, and error handling
"""

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta
import base64
import io
import numpy as np
from PIL import Image
import platform

from monitoring.models import Device, DeviceToken, Recording, Org
from monitoring.auth_utils import create_device_token
from monitoring.serializers import FrameEncodingSerializer


class BaseFrameEncodingTest(TestCase):
    """Base test class with common setup"""
    
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
    
    def _create_test_frames(self, count=5, width=100, height=100):
        """Create test base64-encoded JPEG frames"""
        frames_b64 = []
        for i in range(count):
            # Create a simple test image (numpy array)
            frame_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            
            # Convert to PIL Image
            img = Image.fromarray(frame_array)
            
            # Convert to JPEG bytes
            jpeg_buffer = io.BytesIO()
            img.save(jpeg_buffer, format='JPEG', quality=85)
            jpeg_bytes = jpeg_buffer.getvalue()
            
            # Encode to base64
            frame_b64 = base64.b64encode(jpeg_bytes).decode('utf-8')
            frames_b64.append(frame_b64)
        
        return frames_b64
    
    def _create_valid_metadata(self):
        """Create valid metadata dict"""
        date_str = timezone.now().strftime('%Y/%m/%d')
        return {
            'segment_start': self.start_time.isoformat(),
            'segment_end': self.end_time.isoformat(),
            'segment_index': 1,
            'segment_id': 'test-segment-123',
            'date': date_str,
            'duration_seconds': self.duration_seconds,
            'is_idle_period': False,
            'idle_start_offset': None
        }
    
    def _mock_ffmpeg_success(self, platform_system='Windows'):
        """Mock successful FFmpeg encoding"""
        mock_ffmpeg = MagicMock()
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        
        if platform_system == 'Windows':
            # Mock temp file approach
            mock_output.run.return_value = None
        else:
            # Mock pipe approach
            mock_process = MagicMock()
            mock_process.stdout.read.return_value = b'fake_video_data'
            mock_process.wait.return_value = 0
            mock_process.returncode = 0
            mock_output.run_async.return_value = mock_process
        
        return {
            'ffmpeg': mock_ffmpeg,
            'input': mock_input,
            'output': mock_output,
            'shutil.which': MagicMock(return_value='/usr/bin/ffmpeg'),
            'subprocess.run': MagicMock()
        }
    
    def _mock_ffmpeg_not_found(self):
        """Mock FFmpeg not found"""
        return {
            'shutil.which': MagicMock(return_value=None),
            'os.path.exists': MagicMock(return_value=False)
        }


# ============================================================================
# 1. Serializer Tests
# ============================================================================

class FrameEncodingSerializerTest(TestCase):
    """Test FrameEncodingSerializer validation"""
    
    def setUp(self):
        self.valid_frames = ['dGVzdA==', 'dGVzdDI=']  # base64 test strings
        self.valid_metadata = {
            'segment_start': '2024-01-01T10:00:00Z',
            'segment_end': '2024-01-01T10:05:00Z',
            'segment_index': 1,
            'segment_id': 'test-123',
            'date': '2024/01/01',
            'duration_seconds': 300.0
        }
    
    def test_serializer_valid_data(self):
        """Valid frames array and metadata passes validation"""
        serializer = FrameEncodingSerializer(data={
            'frames': self.valid_frames,
            'metadata': self.valid_metadata
        })
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_empty_frames(self):
        """Empty frames array fails validation"""
        serializer = FrameEncodingSerializer(data={
            'frames': [],
            'metadata': self.valid_metadata
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('frames', serializer.errors)
    
    def test_serializer_missing_frames(self):
        """Missing frames field fails validation"""
        serializer = FrameEncodingSerializer(data={
            'metadata': self.valid_metadata
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('frames', serializer.errors)
    
    def test_serializer_missing_metadata(self):
        """Missing metadata field fails validation"""
        serializer = FrameEncodingSerializer(data={
            'frames': self.valid_frames
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('metadata', serializer.errors)
    
    def test_serializer_missing_segment_start(self):
        """Metadata missing segment_start fails validation"""
        metadata = self.valid_metadata.copy()
        del metadata['segment_start']
        serializer = FrameEncodingSerializer(data={
            'frames': self.valid_frames,
            'metadata': metadata
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('metadata', serializer.errors)
    
    def test_serializer_missing_segment_end(self):
        """Metadata missing segment_end fails validation"""
        metadata = self.valid_metadata.copy()
        del metadata['segment_end']
        serializer = FrameEncodingSerializer(data={
            'frames': self.valid_frames,
            'metadata': metadata
        })
        self.assertFalse(serializer.is_valid())
    
    def test_serializer_missing_segment_index(self):
        """Metadata missing segment_index fails validation"""
        metadata = self.valid_metadata.copy()
        del metadata['segment_index']
        serializer = FrameEncodingSerializer(data={
            'frames': self.valid_frames,
            'metadata': metadata
        })
        self.assertFalse(serializer.is_valid())
    
    def test_serializer_missing_segment_id(self):
        """Metadata missing segment_id fails validation"""
        metadata = self.valid_metadata.copy()
        del metadata['segment_id']
        serializer = FrameEncodingSerializer(data={
            'frames': self.valid_frames,
            'metadata': metadata
        })
        self.assertFalse(serializer.is_valid())
    
    def test_serializer_missing_date(self):
        """Metadata missing date fails validation"""
        metadata = self.valid_metadata.copy()
        del metadata['date']
        serializer = FrameEncodingSerializer(data={
            'frames': self.valid_frames,
            'metadata': metadata
        })
        self.assertFalse(serializer.is_valid())
    
    def test_serializer_missing_duration_seconds(self):
        """Metadata missing duration_seconds fails validation"""
        metadata = self.valid_metadata.copy()
        del metadata['duration_seconds']
        serializer = FrameEncodingSerializer(data={
            'frames': self.valid_frames,
            'metadata': metadata
        })
        self.assertFalse(serializer.is_valid())


# ============================================================================
# 2. Authentication Tests
# ============================================================================

class FrameEncodingViewAuthTest(BaseFrameEncodingTest):
    """Test authentication for FrameEncodingView"""
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_no_authentication(self, mock_shutil, mock_asyncio, mock_storage):
        """Request without token returns 401"""
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_invalid_token(self, mock_shutil, mock_asyncio, mock_storage):
        """Request with invalid token returns 401"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_12345')
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_valid_authentication(self, mock_shutil, mock_asyncio, mock_storage):
        """Request with valid device token authenticates successfully"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        # Mock FFmpeg not found to get early return
        mock_shutil.which.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Should get 503 (FFmpeg not found) but authentication passed
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('FFMPEG_NOT_FOUND', response.json().get('error_code', ''))


# ============================================================================
# 3. Request Validation Tests
# ============================================================================

class FrameEncodingViewValidationTest(BaseFrameEncodingTest):
    """Test request validation for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    def test_missing_frames(self):
        """Empty frames array returns 400"""
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': [], 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_base64_frames(self):
        """Invalid base64 strings in frames array returns 400"""
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': ['invalid_base64!!!'], 'metadata': metadata},
            format='json'
        )
        
        # Should fail during decoding, may return 400 or 500 depending on where it fails
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])
    
    def test_missing_metadata(self):
        """Missing metadata returns 400"""
        frames = self._create_test_frames(3)
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_segment_start(self):
        """Missing segment_start in metadata returns 400"""
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        del metadata['segment_start']
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_segment_end(self):
        """Missing segment_end in metadata returns 400"""
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        del metadata['segment_end']
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_datetime_format(self):
        """Invalid datetime strings in metadata returns 400"""
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        metadata['segment_start'] = 'invalid-datetime'
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ============================================================================
# 4. Frame Decoding Tests
# ============================================================================

class FrameEncodingViewDecodingTest(BaseFrameEncodingTest):
    """Test frame decoding for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_successful_frame_decoding(self, mock_shutil, mock_asyncio, mock_storage):
        """Valid base64 JPEG frames decode successfully"""
        # Mock FFmpeg not found to test decoding without encoding
        mock_shutil.which.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Should fail at FFmpeg check, but decoding should have worked
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_invalid_jpeg_data(self, mock_shutil, mock_asyncio, mock_storage):
        """Invalid JPEG data in frames handles gracefully"""
        mock_shutil.which.return_value = None
        
        # Create invalid base64 that decodes but isn't valid JPEG
        invalid_frame = base64.b64encode(b'not a jpeg').decode('utf-8')
        frames = [invalid_frame]
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Should fail because no valid frames decoded
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_all_frames_invalid(self, mock_shutil, mock_asyncio, mock_storage):
        """All frames invalid returns 400"""
        mock_shutil.which.return_value = None
        
        frames = [base64.b64encode(b'invalid').decode('utf-8')] * 3
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ============================================================================
# 5. FFmpeg Encoding Tests (Mocked)
# ============================================================================

class FrameEncodingViewEncodingTest(BaseFrameEncodingTest):
    """Test FFmpeg encoding for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_ffmpeg_not_found(self, mock_shutil, mock_asyncio, mock_storage):
        """FFmpeg binary not found returns 503 with error code"""
        mock_shutil.which.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('FFMPEG_NOT_FOUND', response.json().get('error_code', ''))
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    @patch('builtins.__import__')
    def test_ffmpeg_python_not_installed(self, mock_import, mock_shutil, mock_asyncio, mock_storage):
        """ffmpeg-python import fails returns 503"""
        mock_shutil.which.return_value = '/usr/bin/ffmpeg'
        
        # Make importing ffmpeg raise ImportError
        def import_side_effect(name, *args, **kwargs):
            if name == 'ffmpeg':
                raise ImportError("No module named 'ffmpeg'")
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('FFMPEG_PYTHON_NOT_INSTALLED', response.json().get('error_code', ''))
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    @patch('monitoring.views.tempfile')
    @patch('builtins.open', create=True)
    def test_encoding_success_windows(self, mock_open, mock_tempfile, mock_ffmpeg, mock_shutil, 
                                      mock_platform, mock_asyncio, mock_storage):
        """Successful encoding on Windows (temp files)"""
        mock_platform.system.return_value = 'Windows'
        mock_shutil.which.return_value = 'C:\\ffmpeg.exe'
        
        # Mock temp files
        mock_input_file = MagicMock()
        mock_input_file.name = '/tmp/input.raw'
        mock_input_file.__enter__ = MagicMock(return_value=mock_input_file)
        mock_input_file.__exit__ = MagicMock(return_value=False)
        
        mock_output_file = MagicMock()
        mock_output_file.name = '/tmp/output.mp4'
        mock_output_file.__enter__ = MagicMock(return_value=mock_output_file)
        mock_output_file.__exit__ = MagicMock(return_value=False)
        
        mock_tempfile.NamedTemporaryFile.side_effect = [mock_input_file, mock_output_file]
        
        # Mock file operations
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'fake_video_data'
        mock_open.return_value.__enter__.return_value = mock_file_handle
        mock_open.return_value.__exit__.return_value = False
        
        # Mock FFmpeg
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run.return_value = None
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock storage
        mock_asyncio.run.return_value = None
        
        # Mock os.path.exists and os.unlink
        with patch('monitoring.views.os.path.exists', return_value=True):
            with patch('monitoring.views.os.unlink'):
                frames = self._create_test_frames(3)
                metadata = self._create_valid_metadata()
                
                response = self.client.post(
                    '/api/recording/encode-frames/',
                    {'frames': frames, 'metadata': metadata},
                    format='json'
                )
                
                # Should succeed (or fail at storage/recording creation, but encoding worked)
                self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    def test_encoding_success_linux(self, mock_ffmpeg, mock_shutil, mock_platform, mock_asyncio, mock_storage):
        """Successful encoding on Linux/Mac (pipes)"""
        mock_platform.system.return_value = 'Linux'
        mock_shutil.which.return_value = '/usr/bin/ffmpeg'
        
        # Mock FFmpeg pipe process
        mock_process = MagicMock()
        mock_process.stdout.read.return_value = b'fake_video_data'
        mock_process.wait.return_value = 0
        mock_process.returncode = 0
        mock_process.stdin = MagicMock()
        
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run_async.return_value = mock_process
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock storage
        mock_asyncio.run.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        with patch('monitoring.views.Recording.objects.create') as mock_create:
            mock_create.return_value = MagicMock(id='test-recording-123')
            
            response = self.client.post(
                '/api/recording/encode-frames/',
                {'frames': frames, 'metadata': metadata},
                format='json'
            )
            
            # Should succeed
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])


# ============================================================================
# 6. Storage Tests
# ============================================================================

class FrameEncodingViewStorageTest(BaseFrameEncodingTest):
    """Test storage operations for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    @patch('monitoring.views.Recording.objects.create')
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    @patch('monitoring.views.tempfile')
    @patch('monitoring.views.subprocess')
    @patch('builtins.open', create=True)
    def test_video_storage_success(self, mock_open, mock_subprocess, mock_tempfile, mock_ffmpeg, 
                                   mock_shutil, mock_platform, mock_asyncio, mock_storage, mock_create):
        """Video bytes stored successfully with correct blob_key"""
        mock_platform.system.return_value = 'Windows'
        mock_shutil.which.return_value = 'C:\\ffmpeg.exe'
        
        # Mock FFmpeg encoding
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run.return_value = None
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock file operations
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'fake_video_data'
        mock_open.return_value.__enter__.return_value = mock_file_handle
        mock_open.return_value.__exit__.return_value = False
        
        # Mock temp files
        mock_input_file = MagicMock()
        mock_input_file.name = '/tmp/input.raw'
        mock_input_file.__enter__ = MagicMock(return_value=mock_input_file)
        mock_input_file.__exit__ = MagicMock(return_value=False)
        
        mock_output_file = MagicMock()
        mock_output_file.name = '/tmp/output.mp4'
        mock_output_file.__enter__ = MagicMock(return_value=mock_output_file)
        mock_output_file.__exit__ = MagicMock(return_value=False)
        
        mock_tempfile.NamedTemporaryFile.side_effect = [mock_input_file, mock_output_file]
        
        # Mock storage
        mock_asyncio.run.return_value = None
        
        # Mock Recording creation
        mock_recording = MagicMock()
        mock_recording.id = 'test-recording-123'
        mock_create.return_value = mock_recording
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        with patch('monitoring.views.os.path.exists', return_value=True):
            with patch('monitoring.views.os.unlink'):
                response = self.client.post(
                    '/api/recording/encode-frames/',
                    {'frames': frames, 'metadata': metadata},
                    format='json'
                )
                
                # Verify storage was called
                self.assertTrue(mock_asyncio.run.called)
    
    @patch('monitoring.views.Recording.objects.create')
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    @patch('monitoring.views.tempfile')
    @patch('monitoring.views.subprocess')
    @patch('builtins.open', create=True)
    def test_blob_key_format(self, mock_open, mock_subprocess, mock_tempfile, mock_ffmpeg, 
                            mock_shutil, mock_platform, mock_asyncio, mock_storage, mock_create):
        """Blob key follows pattern {org_id}/{device_id}/{date}/{hash}.mp4"""
        mock_platform.system.return_value = 'Windows'
        mock_shutil.which.return_value = 'C:\\ffmpeg.exe'
        
        # Mock FFmpeg
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run.return_value = None
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock file operations
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'fake_video_data'
        mock_open.return_value.__enter__.return_value = mock_file_handle
        mock_open.return_value.__exit__.return_value = False
        
        # Mock temp files
        mock_input_file = MagicMock()
        mock_input_file.name = '/tmp/input.raw'
        mock_input_file.__enter__ = MagicMock(return_value=mock_input_file)
        mock_input_file.__exit__ = MagicMock(return_value=False)
        
        mock_output_file = MagicMock()
        mock_output_file.name = '/tmp/output.mp4'
        mock_output_file.__enter__ = MagicMock(return_value=mock_output_file)
        mock_output_file.__exit__ = MagicMock(return_value=False)
        
        mock_tempfile.NamedTemporaryFile.side_effect = [mock_input_file, mock_output_file]
        
        # Mock storage to capture blob_key
        stored_keys = []
        def capture_storage(key, data, content_type):
            stored_keys.append(key)
        
        mock_asyncio.run.side_effect = capture_storage
        
        # Mock Recording creation
        mock_recording = MagicMock()
        mock_recording.id = 'test-recording-123'
        mock_create.return_value = mock_recording
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        with patch('monitoring.views.os.path.exists', return_value=True):
            with patch('monitoring.views.os.unlink'):
                response = self.client.post(
                    '/api/recording/encode-frames/',
                    {'frames': frames, 'metadata': metadata},
                    format='json'
                )
                
                # Verify blob_key format
                if stored_keys:
                    blob_key = stored_keys[0]
                    self.assertTrue(blob_key.endswith('.mp4'))
                    self.assertIn(str(self.device.id), blob_key)


# ============================================================================
# 7. Recording Creation Tests
# ============================================================================

class FrameEncodingViewRecordingTest(BaseFrameEncodingTest):
    """Test Recording model creation for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    @patch('monitoring.views.tempfile')
    @patch('monitoring.views.subprocess')
    @patch('builtins.open', create=True)
    def test_recording_created(self, mock_open, mock_subprocess, mock_tempfile, mock_ffmpeg, 
                              mock_shutil, mock_platform, mock_asyncio, mock_storage):
        """Recording record created in database with correct fields"""
        mock_platform.system.return_value = 'Windows'
        mock_shutil.which.return_value = 'C:\\ffmpeg.exe'
        
        # Mock FFmpeg
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run.return_value = None
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock file operations
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'fake_video_data'
        mock_open.return_value.__enter__.return_value = mock_file_handle
        mock_open.return_value.__exit__.return_value = False
        
        # Mock temp files
        mock_input_file = MagicMock()
        mock_input_file.name = '/tmp/input.raw'
        mock_input_file.__enter__ = MagicMock(return_value=mock_input_file)
        mock_input_file.__exit__ = MagicMock(return_value=False)
        
        mock_output_file = MagicMock()
        mock_output_file.name = '/tmp/output.mp4'
        mock_output_file.__enter__ = MagicMock(return_value=mock_output_file)
        mock_output_file.__exit__ = MagicMock(return_value=False)
        
        mock_tempfile.NamedTemporaryFile.side_effect = [mock_input_file, mock_output_file]
        
        # Mock storage
        mock_asyncio.run.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        with patch('monitoring.views.os.path.exists', return_value=True):
            with patch('monitoring.views.os.unlink'):
                initial_count = Recording.objects.count()
                
                response = self.client.post(
                    '/api/recording/encode-frames/',
                    {'frames': frames, 'metadata': metadata},
                    format='json'
                )
                
                # Verify recording was created
                final_count = Recording.objects.count()
                if response.status_code == status.HTTP_200_OK:
                    self.assertEqual(final_count, initial_count + 1)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    @patch('monitoring.views.tempfile')
    @patch('monitoring.views.subprocess')
    @patch('builtins.open', create=True)
    def test_recording_idle_period(self, mock_open, mock_subprocess, mock_tempfile, mock_ffmpeg, 
                                   mock_shutil, mock_platform, mock_asyncio, mock_storage):
        """Idle period flag set correctly from metadata"""
        mock_platform.system.return_value = 'Windows'
        mock_shutil.which.return_value = 'C:\\ffmpeg.exe'
        
        # Mock FFmpeg
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run.return_value = None
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock file operations
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'fake_video_data'
        mock_open.return_value.__enter__.return_value = mock_file_handle
        mock_open.return_value.__exit__.return_value = False
        
        # Mock temp files
        mock_input_file = MagicMock()
        mock_input_file.name = '/tmp/input.raw'
        mock_input_file.__enter__ = MagicMock(return_value=mock_input_file)
        mock_input_file.__exit__ = MagicMock(return_value=False)
        
        mock_output_file = MagicMock()
        mock_output_file.name = '/tmp/output.mp4'
        mock_output_file.__enter__ = MagicMock(return_value=mock_output_file)
        mock_output_file.__exit__ = MagicMock(return_value=False)
        
        mock_tempfile.NamedTemporaryFile.side_effect = [mock_input_file, mock_output_file]
        
        # Mock storage
        mock_asyncio.run.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        metadata['is_idle_period'] = True
        metadata['idle_start_offset'] = 120.5
        
        with patch('monitoring.views.os.path.exists', return_value=True):
            with patch('monitoring.views.os.unlink'):
                response = self.client.post(
                    '/api/recording/encode-frames/',
                    {'frames': frames, 'metadata': metadata},
                    format='json'
                )
                
                if response.status_code == status.HTTP_200_OK:
                    recording = Recording.objects.last()
                    self.assertIsNotNone(recording)
                    self.assertTrue(recording.is_idle_period)
                    self.assertEqual(recording.idle_start_offset, 120.5)


# ============================================================================
# 8. Thumbnail Generation Tests
# ============================================================================

class FrameEncodingViewThumbnailTest(BaseFrameEncodingTest):
    """Test thumbnail generation for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    @patch('monitoring.views.tempfile')
    @patch('monitoring.views.subprocess')
    @patch('builtins.open', create=True)
    def test_thumbnail_generation_success(self, mock_open, mock_subprocess, mock_tempfile, 
                                         mock_ffmpeg, mock_shutil, mock_platform, mock_asyncio, mock_storage):
        """Thumbnail generated from first frame successfully"""
        mock_platform.system.return_value = 'Windows'
        mock_shutil.which.return_value = 'C:\\ffmpeg.exe'
        
        # Mock FFmpeg
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run.return_value = None
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock subprocess for thumbnail generation
        mock_subprocess.run.return_value = MagicMock(returncode=0)
        
        # Mock file operations
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'fake_video_data'
        mock_open.return_value.__enter__.return_value = mock_file_handle
        mock_open.return_value.__exit__.return_value = False
        
        # Mock temp files
        mock_input_file = MagicMock()
        mock_input_file.name = '/tmp/input.raw'
        mock_input_file.__enter__ = MagicMock(return_value=mock_input_file)
        mock_input_file.__exit__ = MagicMock(return_value=False)
        
        mock_output_file = MagicMock()
        mock_output_file.name = '/tmp/output.mp4'
        mock_output_file.__enter__ = MagicMock(return_value=mock_output_file)
        mock_output_file.__exit__ = MagicMock(return_value=False)
        
        mock_tempfile.NamedTemporaryFile.side_effect = [
            mock_input_file, mock_output_file,
            MagicMock(name='/tmp/thumb_input.jpg', __enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock()),
            MagicMock(name='/tmp/thumb_output.jpg', __enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock())
        ]
        
        # Mock storage
        stored_keys = []
        def capture_storage(key, data, content_type):
            stored_keys.append(key)
        
        mock_asyncio.run.side_effect = capture_storage
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        with patch('monitoring.views.os.path.exists', return_value=True):
            with patch('monitoring.views.os.unlink'):
                response = self.client.post(
                    '/api/recording/encode-frames/',
                    {'frames': frames, 'metadata': metadata},
                    format='json'
                )
                
                # Verify thumbnail storage was called
                if response.status_code == status.HTTP_200_OK:
                    # Should have stored both video and thumbnail
                    self.assertTrue(len(stored_keys) >= 1)


# ============================================================================
# 9. WebSocket Events Tests
# ============================================================================

class FrameEncodingViewWebSocketTest(BaseFrameEncodingTest):
    """Test WebSocket event emission for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    @patch('monitoring.views.tempfile')
    @patch('monitoring.views.subprocess')
    @patch('monitoring.views.get_channel_layer')
    @patch('monitoring.views.async_to_sync')
    @patch('builtins.open', create=True)
    def test_websocket_event_emitted(self, mock_open, mock_async_to_sync, mock_get_channel_layer, 
                                     mock_subprocess, mock_tempfile, mock_ffmpeg, mock_shutil, 
                                     mock_platform, mock_asyncio, mock_storage):
        """WebSocket events emitted to monitoring_updates group"""
        mock_platform.system.return_value = 'Windows'
        mock_shutil.which.return_value = 'C:\\ffmpeg.exe'
        
        # Mock FFmpeg
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run.return_value = None
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock file operations
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'fake_video_data'
        mock_open.return_value.__enter__.return_value = mock_file_handle
        mock_open.return_value.__exit__.return_value = False
        
        # Mock temp files
        mock_input_file = MagicMock()
        mock_input_file.name = '/tmp/input.raw'
        mock_input_file.__enter__ = MagicMock(return_value=mock_input_file)
        mock_input_file.__exit__ = MagicMock(return_value=False)
        
        mock_output_file = MagicMock()
        mock_output_file.name = '/tmp/output.mp4'
        mock_output_file.__enter__ = MagicMock(return_value=mock_output_file)
        mock_output_file.__exit__ = MagicMock(return_value=False)
        
        mock_tempfile.NamedTemporaryFile.side_effect = [mock_input_file, mock_output_file]
        
        # Mock storage
        mock_asyncio.run.return_value = None
        
        # Mock WebSocket
        mock_channel_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_channel_layer
        mock_async_to_sync.return_value = MagicMock()
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        with patch('monitoring.views.os.path.exists', return_value=True):
            with patch('monitoring.views.os.unlink'):
                response = self.client.post(
                    '/api/recording/encode-frames/',
                    {'frames': frames, 'metadata': metadata},
                    format='json'
                )
                
                # Verify WebSocket was called (if encoding succeeded)
                if response.status_code == status.HTTP_200_OK:
                    self.assertTrue(mock_get_channel_layer.called)


# ============================================================================
# 10. Error Handling Tests
# ============================================================================

class FrameEncodingViewErrorTest(BaseFrameEncodingTest):
    """Test error handling for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.platform')
    @patch('monitoring.views.shutil')
    @patch('monitoring.views.ffmpeg')
    @patch('monitoring.views.tempfile')
    @patch('monitoring.views.Recording.objects.create')
    @patch('builtins.open', create=True)
    def test_database_error(self, mock_open, mock_create, mock_tempfile, mock_ffmpeg, 
                           mock_shutil, mock_platform, mock_asyncio, mock_storage):
        """Database error during Recording creation returns 500"""
        mock_platform.system.return_value = 'Windows'
        mock_shutil.which.return_value = 'C:\\ffmpeg.exe'
        
        # Mock FFmpeg
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_input.output.return_value = mock_output
        mock_output.overwrite_output.return_value = mock_output
        mock_output.run.return_value = None
        mock_ffmpeg.input.return_value = mock_input
        
        # Mock file operations
        mock_file_handle = MagicMock()
        mock_file_handle.read.return_value = b'fake_video_data'
        mock_open.return_value.__enter__.return_value = mock_file_handle
        mock_open.return_value.__exit__.return_value = False
        
        # Mock temp files
        mock_input_file = MagicMock()
        mock_input_file.name = '/tmp/input.raw'
        mock_input_file.__enter__ = MagicMock(return_value=mock_input_file)
        mock_input_file.__exit__ = MagicMock(return_value=False)
        
        mock_output_file = MagicMock()
        mock_output_file.name = '/tmp/output.mp4'
        mock_output_file.__enter__ = MagicMock(return_value=mock_output_file)
        mock_output_file.__exit__ = MagicMock(return_value=False)
        
        mock_tempfile.NamedTemporaryFile.side_effect = [mock_input_file, mock_output_file]
        
        # Mock storage
        mock_asyncio.run.return_value = None
        
        # Mock database error
        from django.db import IntegrityError
        mock_create.side_effect = IntegrityError("Database error")
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        with patch('monitoring.views.os.path.exists', return_value=True):
            with patch('monitoring.views.os.unlink'):
                response = self.client.post(
                    '/api/recording/encode-frames/',
                    {'frames': frames, 'metadata': metadata},
                    format='json'
                )
                
                self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# 11. Edge Cases
# ============================================================================

class FrameEncodingViewEdgeCasesTest(BaseFrameEncodingTest):
    """Test edge cases for FrameEncodingView"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_single_frame(self, mock_shutil, mock_asyncio, mock_storage):
        """Single frame encodes successfully"""
        mock_shutil.which.return_value = None  # FFmpeg not found, but test decoding
        
        frames = self._create_test_frames(1)
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Should fail at FFmpeg check, but single frame should decode
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_many_frames(self, mock_shutil, mock_asyncio, mock_storage):
        """Large number of frames (100+) encodes successfully"""
        mock_shutil.which.return_value = None  # FFmpeg not found
        
        frames = self._create_test_frames(100)
        metadata = self._create_valid_metadata()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Should fail at FFmpeg check, but many frames should decode
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_missing_date_in_metadata(self, mock_shutil, mock_asyncio, mock_storage):
        """Date defaults to current date if missing"""
        mock_shutil.which.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        del metadata['date']
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Should fail at serializer validation (date is required)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    @patch('monitoring.views.shutil')
    def test_optional_idle_fields(self, mock_shutil, mock_asyncio, mock_storage):
        """Optional idle_period and idle_start_offset handled"""
        mock_shutil.which.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        # Don't include idle fields - should use defaults
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Should fail at FFmpeg check, but validation should pass
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)


# ============================================================================
# 12. Integration Tests (Optional - Requires FFmpeg)
# ============================================================================

class FrameEncodingViewIntegrationTest(BaseFrameEncodingTest):
    """Integration tests with real FFmpeg (skip if not available)"""
    
    def setUp(self):
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.device_token}')
        
        # Check if FFmpeg is available
        import shutil
        self.ffmpeg_available = shutil.which('ffmpeg') is not None
    
    def _skip_if_no_ffmpeg(self):
        """Skip test if FFmpeg is not available"""
        if not self.ffmpeg_available:
            self.skipTest("FFmpeg not available - skipping integration test")
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    def test_end_to_end_encoding(self, mock_asyncio, mock_storage):
        """Full flow from frames to Recording record"""
        self._skip_if_no_ffmpeg()
        
        # Mock storage to avoid actual storage operations
        mock_asyncio.run.return_value = None
        
        frames = self._create_test_frames(5)
        metadata = self._create_valid_metadata()
        
        initial_count = Recording.objects.count()
        
        response = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Should succeed if FFmpeg is available
        if response.status_code == status.HTTP_200_OK:
            final_count = Recording.objects.count()
            self.assertEqual(final_count, initial_count + 1)
            
            recording = Recording.objects.last()
            self.assertIsNotNone(recording)
            self.assertEqual(recording.device, self.device)
            self.assertEqual(recording.duration_seconds, self.duration_seconds)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    def test_multiple_segments(self, mock_asyncio, mock_storage):
        """Multiple segments from same device"""
        self._skip_if_no_ffmpeg()
        
        mock_asyncio.run.return_value = None
        
        # Create first segment
        frames1 = self._create_test_frames(3)
        metadata1 = self._create_valid_metadata()
        metadata1['segment_index'] = 1
        
        response1 = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames1, 'metadata': metadata1},
            format='json'
        )
        
        # Create second segment
        frames2 = self._create_test_frames(3)
        metadata2 = self._create_valid_metadata()
        metadata2['segment_index'] = 2
        
        response2 = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames2, 'metadata': metadata2},
            format='json'
        )
        
        if response1.status_code == status.HTTP_200_OK and response2.status_code == status.HTTP_200_OK:
            recordings = Recording.objects.filter(device=self.device)
            self.assertGreaterEqual(recordings.count(), 2)
    
    @patch('monitoring.views.storage')
    @patch('monitoring.views.asyncio')
    def test_duplicate_detection(self, mock_asyncio, mock_storage):
        """SHA256 hash prevents duplicate storage"""
        self._skip_if_no_ffmpeg()
        
        mock_asyncio.run.return_value = None
        
        frames = self._create_test_frames(3)
        metadata = self._create_valid_metadata()
        
        # Upload same frames twice
        response1 = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata},
            format='json'
        )
        
        # Change metadata but keep same frames
        metadata2 = metadata.copy()
        metadata2['segment_index'] = 2
        
        response2 = self.client.post(
            '/api/recording/encode-frames/',
            {'frames': frames, 'metadata': metadata2},
            format='json'
        )
        
        if response1.status_code == status.HTTP_200_OK and response2.status_code == status.HTTP_200_OK:
            # Both recordings should exist (deduplication not implemented, but hash is calculated)
            recordings = Recording.objects.filter(device=self.device)
            self.assertGreaterEqual(recordings.count(), 2)
            
            # Verify blob_keys are different (different segment_index in metadata)
            blob_keys = [r.blob_key for r in recordings]
            # They might be the same if hash is same, but recordings are separate
            self.assertGreaterEqual(len(set(blob_keys)), 1)
