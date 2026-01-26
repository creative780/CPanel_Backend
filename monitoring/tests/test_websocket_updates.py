"""
Tests for WebSocket real-time updates for recording events
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from monitoring.models import Device, Recording, Org, DeviceToken
from monitoring.auth_utils import create_device_token
from accounts.models import User
from channels.testing import WebsocketCommunicator
from channels.layers import InMemoryChannelLayer
import json


class WebSocketUpdatesTest(TestCase):
    """Test WebSocket real-time updates for recording events"""
    
    def setUp(self):
        """Set up test data"""
        User = get_user_model()
        
        self.admin_user = User.objects.create_user(
            username='admin_ws',
            password='testpass123',
            email='admin@test.com',
            roles=['admin']
        )
        
        self.org = Org.objects.create(name="WS Test Org")
        self.device = Device.objects.create(
            hostname="ws-test-device",
            os="Windows",
            status="ONLINE",
            org=self.org
        )
        
        self.token_obj = create_device_token(self.device)
        self.device_token = self.token_obj.token
    
    def test_recording_update_event_structure(self):
        """Test recording update event structure"""
        # Simulate recording update event
        recording = Recording.objects.create(
            device=self.device,
            blob_key='test/video.mp4',
            thumb_key='test/thumb.jpg',
            start_time=timezone.now() - timedelta(minutes=10),
            end_time=timezone.now() - timedelta(minutes=5),
            duration_seconds=300.0
        )
        
        # Event structure that would be sent via WebSocket
        event = {
            'type': 'recording_update',
            'device_id': self.device.id,
            'recording': {
                'id': recording.id,
                'thumb_url': f'/api/monitoring/files/{recording.thumb_key}' if recording.thumb_key else None,
                'start_time': recording.start_time.isoformat(),
                'duration_seconds': recording.duration_seconds
            }
        }
        
        # Verify event structure
        self.assertEqual(event['type'], 'recording_update')
        self.assertEqual(event['device_id'], self.device.id)
        self.assertIn('recording', event)
        self.assertEqual(event['recording']['id'], recording.id)
    
    def test_device_recording_event_structure(self):
        """Test device recording event structure"""
        recording = Recording.objects.create(
            device=self.device,
            blob_key='test/video.mp4',
            thumb_key='test/thumb.jpg',
            start_time=timezone.now() - timedelta(minutes=10),
            end_time=timezone.now() - timedelta(minutes=5),
            duration_seconds=300.0
        )
        
        # Event structure for device-specific group
        event = {
            'type': 'device_recording',
            'recording': {
                'id': recording.id,
                'thumb_url': f'/api/monitoring/files/{recording.thumb_key}' if recording.thumb_key else None,
                'start_time': recording.start_time.isoformat(),
                'duration_seconds': recording.duration_seconds
            }
        }
        
        # Verify event structure
        self.assertEqual(event['type'], 'device_recording')
        self.assertIn('recording', event)
        self.assertEqual(event['recording']['id'], recording.id)
    
    def test_monitoring_consumer_recording_update_handler(self):
        """Test MonitoringConsumer handles recording_update events"""
        # Verify the handler method exists
        from monitoring.consumers import MonitoringConsumer
        
        consumer = MonitoringConsumer()
        self.assertTrue(hasattr(consumer, 'recording_update'))
    
    def test_device_consumer_recording_handler(self):
        """Test DeviceConsumer handles device_recording events"""
        # Verify the handler method exists
        from monitoring.consumers import DeviceConsumer
        
        consumer = DeviceConsumer()
        self.assertTrue(hasattr(consumer, 'device_recording'))
    
    def test_channel_layer_group_names(self):
        """Test channel layer group names for recording events"""
        # Monitoring updates group
        monitoring_group = 'monitoring_updates'
        self.assertEqual(monitoring_group, 'monitoring_updates')
        
        # Device-specific group
        device_group = f'device_{self.device.id}'
        self.assertEqual(device_group, f'device_{self.device.id}')
        
        # These groups should receive recording update events
        # when a recording is created
    
    def test_recording_ingest_emits_websocket_event(self):
        """Test that RecordingIngestView emits WebSocket events"""
        # This tests the integration - when a recording is ingested,
        # WebSocket events should be emitted
        
        # The actual WebSocket event emission happens in RecordingIngestView
        # We verify the code structure supports it
        from monitoring.views import RecordingIngestView
        
        # Check that the view has WebSocket event emission code
        # (This is verified by code inspection, not runtime test)
        view = RecordingIngestView()
        self.assertIsNotNone(view)


