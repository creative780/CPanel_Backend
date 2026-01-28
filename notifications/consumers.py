import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import NotificationSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notification updates"""
    
    async def connect(self):
        """Connect to WebSocket"""
        # Authenticate user
        self.user = await self.authenticate_user()
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)  # Unauthorized
            return
        
        # Join user-specific group
        self.group_name = f'notifications_user_{self.user.id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"Notification WebSocket connected for user {self.user.id}")
    
    async def disconnect(self, close_code):
        """Disconnect from WebSocket"""
        if hasattr(self, 'group_name'):
            # Leave notification group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"Notification WebSocket disconnected for user {self.user.id if hasattr(self, 'user') else 'unknown'}")
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # Currently, we don't expect any messages from client
            # But we can handle ping/pong or other control messages here
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    # WebSocket event handlers (called by channel layer)
    async def notification_created(self, event):
        """Send new notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification.created',
            'data': event['data']
        }))
    
    async def notification_updated(self, event):
        """Send updated notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification.updated',
            'data': event['data']
        }))
    
    # Database operations
    @database_sync_to_async
    def authenticate_user(self):
        """Authenticate user from JWT token"""
        try:
            # Get token from query params or headers
            token = None
            
            # Try query params first
            query_string = self.scope.get('query_string', b'').decode()
            if 'token=' in query_string:
                token = query_string.split('token=')[1].split('&')[0]
            
            # Try Authorization header
            if not token:
                headers = dict(self.scope.get('headers', []))
                auth_header = headers.get(b'authorization', b'').decode()
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
            
            if not token:
                return AnonymousUser()
            
            # Validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
            
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            logger.warning(f"Notification WebSocket authentication failed: {e}")
            return AnonymousUser()

