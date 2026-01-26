"""
WebSocket consumers for real-time monitoring updates
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Device, Heartbeat, Recording
from .auth_utils import verify_jwt_token

User = get_user_model()

logger = logging.getLogger(__name__)


class MonitoringConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time monitoring updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Get token from query parameters
        query_string = self.scope['query_string'].decode()
        token = query_string.split('token=')[1] if 'token=' in query_string else None
        
        if not token:
            logger.warning("WebSocket connection rejected: No token provided")
            await self.close(code=4001)
            return
        
        # Verify JWT token
        try:
            user = await self.verify_token(token)
            if not user:
                # Check if token was expired
                error_msg = getattr(self, '_token_error', '').lower()
                if 'expired' in error_msg:
                    logger.warning("WebSocket connection rejected: Token expired")
                    await self.close(code=4001)  # Unauthorized - token expired
                else:
                    logger.warning(f"WebSocket connection rejected: Invalid token - {getattr(self, '_token_error', 'Unknown error')}")
                    await self.close(code=4001)  # Unauthorized - invalid token
                return
            
            # Check if user is admin (using role-based check instead of is_staff)
            if not (hasattr(user, 'is_admin') and user.is_admin()) and not (hasattr(user, 'has_role') and user.has_role('admin')):
                logger.warning(f"WebSocket connection rejected: User {user.username} is not an admin")
                await self.close(code=4003)
                return
                
            self.user = user
            self.room_group_name = 'monitoring_updates'
            
            # Join monitoring group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"Monitoring WebSocket connected for user: {user.username} (email: {getattr(user, 'email', 'N/A')})")
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}", exc_info=True)
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"Monitoring WebSocket disconnected: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            elif message_type == 'subscribe_device':
                device_id = data.get('device_id')
                if device_id:
                    device_group = f'device_{device_id}'
                    await self.channel_layer.group_add(
                        device_group,
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'subscribed',
                        'device_id': device_id
                    }))
            elif message_type == 'unsubscribe_device':
                device_id = data.get('device_id')
                if device_id:
                    device_group = f'device_{device_id}'
                    await self.channel_layer.group_discard(
                        device_group,
                        self.channel_name
                    )
                    
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal error'
            }))
    
    async def device_update(self, event):
        """Handle device update events"""
        await self.send(text_data=json.dumps({
            'type': 'device_update',
            'device': event['device']
        }))
    
    async def heartbeat_update(self, event):
        """Handle heartbeat update events"""
        await self.send(text_data=json.dumps({
            'type': 'heartbeat_update',
            'device_id': event['device_id'],
            'heartbeat': event['heartbeat']
        }))
    
    async def recording_update(self, event):
        """Handle recording update events"""
        await self.send(text_data=json.dumps({
            'type': 'recording_update',
            'device_id': event['device_id'],
            'recording': event['recording']
        }))
    
    async def device_status_change(self, event):
        """Handle device status change events"""
        await self.send(text_data=json.dumps({
            'type': 'device_status_change',
            'device_id': event['device_id'],
            'status': event['status'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def verify_token(self, token):
        """Verify JWT token and return user"""
        try:
            return verify_jwt_token(token)
        except Exception as e:
            # Store the exception message to check if it's expired
            self._token_error = str(e)
            logger.error(f"Token verification error: {e}")
            return None


class DeviceConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for individual device monitoring"""
    
    async def connect(self):
        """Handle WebSocket connection for device monitoring"""
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.room_group_name = f'device_{self.device_id}'
        
        # Get token from query parameters
        token = self.scope['query_string'].decode().split('token=')[1] if 'token=' in self.scope['query_string'].decode() else None
        
        if not token:
            await self.close(code=4001)
            return
        
        # Verify JWT token and admin access
        try:
            user = await self.verify_token(token)
            if not user:
                # Check if token was expired
                error_msg = getattr(self, '_token_error', '').lower()
                if 'expired' in error_msg:
                    logger.warning("Device WebSocket connection rejected: Token expired")
                    await self.close(code=4001)  # Unauthorized - token expired
                else:
                    logger.warning(f"Device WebSocket connection rejected: Invalid token - {getattr(self, '_token_error', 'Unknown error')}")
                    await self.close(code=4001)  # Unauthorized - invalid token
                return
            # Check if user is admin (using role-based check instead of is_staff)
            if not (hasattr(user, 'is_admin') and user.is_admin()) and not (hasattr(user, 'has_role') and user.has_role('admin')):
                logger.warning(f"Device WebSocket connection rejected: User {user.username} is not an admin")
                await self.close(code=4003)
                return
                
            # Check if device exists
            device = await self.get_device(self.device_id)
            if not device:
                await self.close(code=4004)
                return
            
            self.user = user
            self.device = device
            
            # Join device group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"Device WebSocket connected for device: {self.device_id}")
            
        except Exception as e:
            logger.error(f"Device WebSocket connection error: {e}")
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"Device WebSocket disconnected: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            elif message_type == 'get_latest_data':
                # Send latest device data
                latest_data = await self.get_latest_device_data()
                await self.send(text_data=json.dumps({
                    'type': 'latest_data',
                    'data': latest_data
                }))
                    
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Device WebSocket receive error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal error'
            }))
    
    async def device_heartbeat(self, event):
        """Handle device heartbeat events"""
        await self.send(text_data=json.dumps({
            'type': 'heartbeat',
            'heartbeat': event['heartbeat']
        }))
    
    async def device_recording(self, event):
        """Handle device recording events"""
        await self.send(text_data=json.dumps({
            'type': 'recording',
            'recording': event['recording']
        }))
    
    async def device_activity(self, event):
        """Handle device activity events"""
        await self.send(text_data=json.dumps({
            'type': 'activity',
            'activity': event['activity']
        }))
    
    @database_sync_to_async
    def verify_token(self, token):
        """Verify JWT token and return user"""
        try:
            return verify_jwt_token(token)
        except Exception as e:
            # Store the exception message to check if it's expired
            self._token_error = str(e)
            logger.error(f"Token verification error: {e}")
            return None
    
    @database_sync_to_async
    def get_device(self, device_id):
        """Get device by ID"""
        try:
            return Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_latest_device_data(self):
        """Get latest device data including heartbeat and recording"""
        try:
            device = Device.objects.select_related('current_user').get(id=self.device_id)
            latest_heartbeat = device.heartbeats.order_by('-created_at').first()
            latest_recording = device.recordings.order_by('-start_time').first()
            
            data = {
                'device': {
                    'id': device.id,
                    'hostname': device.hostname,
                    'os': device.os,
                    'status': device.status,
                    'ip': device.ip,
                    'enrolled_at': device.enrolled_at.isoformat(),
                    'last_heartbeat': device.last_heartbeat.isoformat() if device.last_heartbeat else None,
                },
                'current_user': {
                    'id': device.current_user.id if device.current_user else None,
                    'email': device.current_user.email if device.current_user else None,
                    'name': device.current_user_name or '',
                    'role': device.current_user_role or '',
                } if device.current_user else None,
                'latest_heartbeat': {
                    'cpu_percent': latest_heartbeat.cpu_percent,
                    'mem_percent': latest_heartbeat.mem_percent,
                    'active_window': latest_heartbeat.active_window,
                    'is_locked': latest_heartbeat.is_locked,
                    'created_at': latest_heartbeat.created_at.isoformat(),
                    'keystroke_count': latest_heartbeat.keystroke_count,
                    'mouse_click_count': latest_heartbeat.mouse_click_count,
                    'productivity_score': latest_heartbeat.productivity_score,
                } if latest_heartbeat else None,
                'latest_recording': {
                    'id': latest_recording.id if latest_recording else None,
                    'thumb_url': f'/api/monitoring/files/{latest_recording.thumb_key}' if latest_recording and latest_recording.thumb_key else None,
                    'start_time': latest_recording.start_time.isoformat() if latest_recording else None,
                    'duration_seconds': latest_recording.duration_seconds if latest_recording else None,
                } if latest_recording else None,
            }
            return data
        except Exception as e:
            logger.error(f"Error getting latest device data: {e}")
            return None


class AgentStreamConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for agent live video streaming"""
    
    async def connect(self):
        """Handle WebSocket connection from agent"""
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        
        # Get token from query parameters
        token = self.scope['query_string'].decode().split('token=')[1] if 'token=' in self.scope['query_string'].decode() else None
        
        if not token:
            logger.warning("Agent stream connection rejected: No token provided")
            await self.close(code=4001)
            return
        
        # Verify device token
        try:
            device = await self.verify_device_token(token)
            if not device or device.id != self.device_id:
                logger.warning(f"Agent stream connection rejected: Invalid token or device mismatch")
                await self.close(code=4001)
                return
            
            self.device = device
            self.room_group_name = f'agent_stream_{self.device_id}'
            
            # Join agent stream group (for agent to send frames)
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"Agent stream connected for device: {self.device_id}")
            
        except Exception as e:
            logger.error(f"Agent stream connection error: {e}")
            await self.close(code=4000)
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"Agent stream disconnected: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages from agent"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            elif message_type == 'frame':
                # Agent is sending a frame - broadcast to all viewers
                await self.channel_layer.group_send(
                    f'stream_viewers_{self.device_id}',
                    {
                        'type': 'stream_frame',
                        'frame_data': data.get('data'),
                        'timestamp': data.get('timestamp'),
                        'idle': data.get('idle', False),
                        'frame_format': data.get('frame_format', 'jpeg')
                    }
                )
                    
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Agent stream receive error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal error'
            }))
    
    @database_sync_to_async
    def verify_device_token(self, token):
        """Verify device token and return device"""
        try:
            from .models import DeviceToken
            # Try to find device token by secret first, then by token field
            try:
                device_token = DeviceToken.objects.get(secret=token)
            except DeviceToken.DoesNotExist:
                device_token = DeviceToken.objects.get(token=token)
            
            if device_token.is_expired():
                device_token.delete()
                return None
            
            return device_token.device
        except DeviceToken.DoesNotExist:
            logger.error(f"Device token not found: {token[:10]}...")
            return None
        except Exception as e:
            logger.error(f"Device token verification error: {e}")
            return None


class StreamViewerConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for admin users viewing live streams"""
    
    async def connect(self):
        """Handle WebSocket connection from admin viewer"""
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        
        # Get token from query parameters
        token = self.scope['query_string'].decode().split('token=')[1] if 'token=' in self.scope['query_string'].decode() else None
        
        if not token:
            logger.warning("Stream viewer connection rejected: No token provided")
            await self.close(code=4001)
            return
        
        # Verify JWT token and admin access
        try:
            user = await self.verify_token(token)
            if not user:
                await self.close(code=4001)
                return
            
            # Check if user is admin
            if not (hasattr(user, 'is_admin') and user.is_admin()) and not (hasattr(user, 'has_role') and user.has_role('admin')):
                logger.warning(f"Stream viewer connection rejected: User {user.username} is not an admin")
                await self.close(code=4003)
                return
            
            # Check if device exists
            device = await self.get_device(self.device_id)
            if not device:
                await self.close(code=4004)
                return
            
            self.user = user
            self.device = device
            self.room_group_name = f'stream_viewers_{self.device_id}'
            
            # Join viewer group (to receive frames from agent)
            try:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as channel_error:
                logger.error(f"Failed to join channel layer group: {channel_error}", exc_info=True)
                # Continue anyway - connection can still work without channel layer
            
            await self.accept()
            self._accepted = True
            logger.info(f"Stream viewer connected for device: {self.device_id}, user: {user.username}")
            
        except Exception as e:
            logger.error(f"Stream viewer connection error: {e}", exc_info=True)
            # Only close if we haven't accepted yet
            if not hasattr(self, '_accepted') or not self._accepted:
                try:
                    await self.close(code=4000)
                except:
                    pass
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"Stream viewer disconnected: {close_code}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages from viewer"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                    
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Stream viewer receive error: {e}")
    
    async def stream_frame(self, event):
        """Handle stream frame events from agent"""
        await self.send(text_data=json.dumps({
            'type': 'frame',
            'data': event['frame_data'],
            'timestamp': event['timestamp'],
            'idle': event['idle'],
            'frame_format': event['frame_format']
        }))
    
    @database_sync_to_async
    def verify_token(self, token):
        """Verify JWT token and return user"""
        try:
            return verify_jwt_token(token)
        except Exception as e:
            self._token_error = str(e)
            logger.error(f"Token verification error: {e}")
            return None
    
    @database_sync_to_async
    def get_device(self, device_id):
        """Get device by ID"""
        try:
            return Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return None

