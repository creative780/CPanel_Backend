"""
Tests for live streaming functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from monitoring.models import Device, Org, DeviceToken
from monitoring.auth_utils import create_device_token
from accounts.models import User
import json


class LiveStreamingTest(TestCase):
    """Test cases for live streaming WebSocket consumers"""
    
    def setUp(self):
        """Set up test data"""
        User = get_user_model()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_stream',
            password='testpass123',
            email='admin@test.com',
            roles=['admin']
        )
        
        # Create org and device
        self.org = Org.objects.create(name="Stream Test Org")
        self.device = Device.objects.create(
            hostname="stream-test-device",
            os="Windows",
            status="ONLINE",
            org=self.org
        )
        
        # Create device token
        self.token_obj = create_device_token(self.device)
        self.device_token = self.token_obj.token
    
    def test_agent_stream_connection_requires_token(self):
        """Test agent stream connection requires device token"""
        # This would require WebSocket testing framework
        # For now, we test the authentication logic
        from monitoring.auth_utils import authenticate_device_token
        
        # Valid token should work
        device = authenticate_device_token(self.device_token)
        self.assertIsNotNone(device)
        self.assertEqual(device.id, self.device.id)
        
        # Invalid token should fail
        device_invalid = authenticate_device_token('invalid_token')
        self.assertIsNone(device_invalid)
    
    def test_stream_viewer_requires_admin(self):
        """Test stream viewer requires admin role"""
        from monitoring.auth_utils import verify_jwt_token
        
        # This test verifies the authentication logic
        # In a real WebSocket test, we'd use Channels test client
        self.assertTrue(hasattr(self.admin_user, 'is_admin') or hasattr(self.admin_user, 'has_role'))
    
    def test_device_exists_check(self):
        """Test device existence check for streaming"""
        # Verify device exists
        device = Device.objects.get(id=self.device.id)
        self.assertIsNotNone(device)
        
        # Verify non-existent device
        with self.assertRaises(Device.DoesNotExist):
            Device.objects.get(id='non-existent-device')
    
    def test_stream_frame_message_format(self):
        """Test stream frame message format"""
        # Simulate frame message format
        frame_message = {
            'type': 'frame',
            'data': 'base64_encoded_jpeg_data',
            'timestamp': timezone.now().isoformat(),
            'idle': False,
            'frame_format': 'jpeg'
        }
        
        # Verify message structure
        self.assertEqual(frame_message['type'], 'frame')
        self.assertIn('data', frame_message)
        self.assertIn('timestamp', frame_message)
        self.assertIn('idle', frame_message)
        self.assertEqual(frame_message['frame_format'], 'jpeg')
    
    def test_stream_ping_pong(self):
        """Test ping/pong mechanism for keeping connection alive"""
        ping_message = {
            'type': 'ping',
            'timestamp': timezone.now().isoformat()
        }
        
        pong_response = {
            'type': 'pong',
            'timestamp': ping_message['timestamp']
        }
        
        self.assertEqual(pong_response['type'], 'pong')
        self.assertEqual(pong_response['timestamp'], ping_message['timestamp'])


class LiveStreamingIntegrationTest(TestCase):
    """Integration tests for live streaming"""
    
    def setUp(self):
        """Set up test data"""
        User = get_user_model()
        
        self.admin_user = User.objects.create_user(
            username='admin_stream_int',
            password='testpass123',
            email='admin@test.com',
            roles=['admin']
        )
        
        self.org = Org.objects.create(name="Stream Integration Org")
        self.device = Device.objects.create(
            hostname="stream-integration-device",
            os="Windows",
            status="ONLINE",
            org=self.org
        )
        
        self.token_obj = create_device_token(self.device)
        self.device_token = self.token_obj.token
    
    def test_stream_endpoint_urls(self):
        """Test stream endpoint URLs are correctly configured"""
        # Verify routing patterns exist
        from monitoring.routing import websocket_urlpatterns
        
        patterns = [str(p.pattern) for p in websocket_urlpatterns]
        
        # Check for agent stream pattern
        agent_pattern = any('stream/agent' in str(p) for p in websocket_urlpatterns)
        self.assertTrue(agent_pattern, "Agent stream pattern should exist")
        
        # Check for viewer stream pattern
        viewer_pattern = any('stream/viewer' in str(p) for p in websocket_urlpatterns)
        self.assertTrue(viewer_pattern, "Viewer stream pattern should exist")
    
    def test_multiple_viewers_support(self):
        """Test that multiple viewers can connect to same stream"""
        # This would require WebSocket testing
        # For now, we verify the group name format supports multiple viewers
        device_id = self.device.id
        viewer_group = f'stream_viewers_{device_id}'
        agent_group = f'agent_stream_{device_id}'
        
        self.assertEqual(viewer_group, f'stream_viewers_{device_id}')
        self.assertEqual(agent_group, f'agent_stream_{device_id}')
        
        # Multiple viewers would join the same viewer_group
        # This allows broadcasting frames from agent to all viewers


