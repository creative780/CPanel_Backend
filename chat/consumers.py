import json
import logging
import bleach
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import Conversation, Participant, Message

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat features"""
    
    async def connect(self):
        """Connect to WebSocket"""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        # Sanitize conversation ID for group name (Channels only allows ASCII alphanumerics, hyphens, underscores, periods)
        # Matrix room IDs contain special characters like ':' which aren't allowed
        sanitized_id = self.sanitize_group_name(self.conversation_id)
        self.conversation_group_name = f'chat_{sanitized_id}'
        
        # Authenticate user
        self.user = await self.authenticate_user()
        if not self.user or isinstance(self.user, AnonymousUser):
            logger.warning(f"WebSocket connection rejected: Unauthenticated user for conversation {self.conversation_id}")
            await self.close(code=4001)  # Unauthorized
            return
        
        # Connection rate limiting: max 5 concurrent WebSocket connections per user
        user_connections_key = f'user_ws_connections_{self.user.id}'
        user_connections = cache.get(user_connections_key, [])
        
        # Clean up stale connections by checking if they still exist
        # Note: This is a simple approach - in production, consider using Redis sets
        if len(user_connections) >= 5:
            logger.warning(f"WebSocket connection rejected: User {self.user.id} has too many connections (max 5)")
            await self.close(code=4001)  # Too many connections
            return
        
        # Add this connection to the list
        if self.channel_name not in user_connections:
            user_connections.append(self.channel_name)
        cache.set(user_connections_key, user_connections, 3600)  # Cache for 1 hour
        
        # Check if this is a Matrix conversation ID (starts with '!')
        # Matrix conversations don't exist in Django database, so skip validation
        is_matrix_conversation = self.conversation_id.startswith('!')
        
        if not is_matrix_conversation:
            # Validate conversation exists (only for Django conversations)
            if not await self.conversation_exists():
                logger.warning(f"WebSocket connection rejected: Conversation {self.conversation_id} does not exist")
                # Remove from connections list
                if self.channel_name in user_connections:
                    user_connections.remove(self.channel_name)
                    cache.set(user_connections_key, user_connections, 3600)
                await self.close(code=4004)  # Not Found
                return
            
            # Check if user is participant in conversation (only for Django conversations)
            if not await self.is_participant():
                logger.warning(f"WebSocket connection rejected: User {self.user.id} is not a participant in conversation {self.conversation_id}")
                # Remove from connections list
                if self.channel_name in user_connections:
                    user_connections.remove(self.channel_name)
                    cache.set(user_connections_key, user_connections, 3600)
                await self.close(code=4003)  # Forbidden
                return
        else:
            # For Matrix conversations, just log that we're allowing the connection
            logger.info(f"Allowing WebSocket connection for Matrix conversation {self.conversation_id} (user {self.user.id})")
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        # Also join user-specific group for receiving calls even when not viewing the conversation
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Track active WebSocket connections
        try:
            current_count = cache.get('active_ws_connections', 0)
            cache.set('active_ws_connections', current_count + 1, 3600)
            logger.info(f"WebSocket connection established: user {self.user.id}, conversation {self.conversation_id}, total active: {current_count + 1}")
        except Exception as e:
            logger.error(f"Error tracking connection metrics: {e}")
        
        # Send user joined event
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'user_joined',
                'user_id': str(self.user.id),
                'username': self.user.username,
            }
        )
    
    async def disconnect(self, close_code):
        """Disconnect from WebSocket"""
        # Decrement active WebSocket connections counter
        try:
            current_count = cache.get('active_ws_connections', 0)
            if current_count > 0:
                cache.set('active_ws_connections', current_count - 1, 3600)
            logger.info(f"WebSocket connection closed: user {self.user.id if hasattr(self, 'user') and self.user else 'unknown'}, conversation {self.conversation_id if hasattr(self, 'conversation_id') else 'unknown'}, total active: {cache.get('active_ws_connections', 0)}")
        except Exception as e:
            logger.error(f"Error updating connection metrics: {e}")
        
        # Remove connection from user's connection list
        if hasattr(self, 'user') and self.user and not isinstance(self.user, AnonymousUser):
            user_connections_key = f'user_ws_connections_{self.user.id}'
            user_connections = cache.get(user_connections_key, [])
            if self.channel_name in user_connections:
                user_connections.remove(self.channel_name)
                cache.set(user_connections_key, user_connections, 3600)
                logger.debug(f"Removed connection {self.channel_name} from user {self.user.id} connections")
        
        if hasattr(self, 'conversation_group_name'):
            # Send user left event
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'user_left',
                    'user_id': str(self.user.id) if hasattr(self, 'user') and self.user else None,
                    'username': self.user.username if hasattr(self, 'user') and self.user else None,
                }
            )
            
            # Leave conversation group
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )
        
        # Leave user-specific group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read':
                await self.handle_read_receipt(data)
            elif message_type == 'ping':
                # Respond to ping with pong
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
    
    async def handle_message(self, data):
        """Handle new message with validation, sanitization, and rate limiting"""
        text = data.get('text', '').strip()
        
        # Validation: Check if message is empty
        if not text:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message cannot be empty'
            }))
            return
        
        # Validation: Check message length (max 5000 characters)
        if len(text) > 5000:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message too long (max 5000 characters)'
            }))
            return
        
        # Sanitization: Strip HTML tags to prevent XSS attacks
        text = bleach.clean(text, tags=[], strip=True)
        
        # Rate limiting: max 10 messages per minute per user per conversation
        cache_key = f'msg_rate_{self.user.id}_{self.conversation_id}'
        msg_count = cache.get(cache_key, 0)
        if msg_count >= 10:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Rate limit exceeded. Please wait a moment before sending another message.'
            }))
            logger.warning(f"Rate limit exceeded for user {self.user.id} in conversation {self.conversation_id}")
            return
        cache.set(cache_key, msg_count + 1, 60)  # Cache for 60 seconds
        
        # Create message in database
        message = await self.create_message(text)
        
        # Create notifications for all participants except sender
        await self.create_notifications_for_message(message)
        
        # Send message to group
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'message_new',
                'message': {
                    'id': str(message.id),
                    'conversation_id': str(message.conversation.id),
                    'type': message.type,
                    'text': message.text,
                    'sender': message.sender.username if message.sender else None,
                    'sender_id': str(message.sender.id) if message.sender else None,  # Add sender_id for frontend
                    'sender_name': f"{message.sender.first_name} {message.sender.last_name}".strip() if message.sender else "System",
                    'created_at': message.created_at.isoformat(),
                    'attachment': message.attachment.url if message.attachment else None,
                }
            }
        )
    
    async def handle_typing(self, data):
        """Handle typing indicator"""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing,
            }
        )
    
    async def handle_read_receipt(self, data):
        """Handle read receipt"""
        message_ids = data.get('message_ids', [])
        if not message_ids:
            return
        
        # Mark messages as read
        await self.mark_messages_read(message_ids)
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'read_receipt',
                'message_ids': message_ids,
                'user_id': str(self.user.id),
                'username': self.user.username,
            }
        )
    
    # WebSocket event handlers
    async def message_new(self, event):
        """Send new message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message:new',
            'message': event['message']
        }))
    
    async def message_ack(self, event):
        """Send message acknowledgment to sender"""
        if str(self.user.id) == event['sender_id']:
            await self.send(text_data=json.dumps({
                'type': 'message:ack',
                'message_id': event['message_id'],
                'status': event['status']
            }))
    
    async def typing(self, event):
        """Send typing indicator"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    async def read_receipt(self, event):
        """Send read receipt"""
        await self.send(text_data=json.dumps({
            'type': 'read',
            'message_ids': event['message_ids'],
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def user_joined(self, event):
        """Send user joined notification"""
        if str(self.user.id) != event['user_id']:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username']
            }))
    
    async def user_left(self, event):
        """Send user left notification"""
        if str(self.user.id) != event['user_id']:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username']
            }))
    
    # Database operations
    @database_sync_to_async
    def authenticate_user(self):
        """Authenticate user from JWT token"""
        try:
            # Get token from query params or headers
            token = None
            
            # Try query params first
            if 'token' in self.scope['query_string'].decode():
                token = self.scope['query_string'].decode().split('token=')[1].split('&')[0]
            
            # Try Authorization header
            if not token:
                headers = dict(self.scope['headers'])
                auth_header = headers.get(b'authorization', b'').decode()
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
            
            if not token:
                return AnonymousUser()
            
            # Validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
            
        except (InvalidToken, TokenError, User.DoesNotExist):
            return AnonymousUser()
    
    @database_sync_to_async
    def conversation_exists(self):
        """Authenticate user from JWT token"""
        try:
            # Get token from query params or headers
            token = None
            
            # Try query params first
            if 'token' in self.scope['query_string'].decode():
                token = self.scope['query_string'].decode().split('token=')[1].split('&')[0]
            
            # Try Authorization header
            if not token:
                headers = dict(self.scope['headers'])
                auth_header = headers.get(b'authorization', b'').decode()
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
            
            if not token:
                return AnonymousUser()
            
            # Validate token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
            
        except (InvalidToken, TokenError, User.DoesNotExist):
            return AnonymousUser()
    
    @database_sync_to_async
    def conversation_exists(self):
        """Check if conversation exists"""
        try:
            return Conversation.objects.filter(id=self.conversation_id).exists()
        except Exception:
            return False
    
    @database_sync_to_async
    def is_participant(self):
        """Check if user is participant in conversation - optimized with select_related"""
        try:
            return Participant.objects.filter(
                conversation_id=self.conversation_id,
                user=self.user
            ).select_related('user', 'conversation').exists()
        except Exception:
            return False
    
    @database_sync_to_async
    def get_recent_messages(self, limit=50):
        """Get recent messages with caching to reduce database queries"""
        cache_key = f'conv_messages_{self.conversation_id}'
        messages = cache.get(cache_key)
        
        if not messages:
            # Get messages with related data
            message_objects = Message.objects.filter(
                conversation_id=self.conversation_id
            ).select_related('sender', 'conversation').order_by('-created_at')[:limit]
            
            # Convert to dict format for caching
            messages = []
            for msg in message_objects:
                messages.append({
                    'id': str(msg.id),
                    'text': msg.text,
                    'type': msg.type,
                    'created_at': msg.created_at.isoformat(),
                    'status': msg.status,
                    'sender_id': str(msg.sender.id) if msg.sender else None,
                    'sender_username': msg.sender.username if msg.sender else None,
                    'sender_first_name': msg.sender.first_name if msg.sender else None,
                    'sender_last_name': msg.sender.last_name if msg.sender else None,
                    'conversation_id': str(msg.conversation.id) if msg.conversation else None,
                })
            
            # Cache for 5 minutes
            cache.set(cache_key, messages, 300)
            logger.debug(f"Cached {len(messages)} messages for conversation {self.conversation_id}")
        
        return messages
    
    @database_sync_to_async
    def create_message(self, text):
        """Create message in database - optimized with select_related"""
        conversation = Conversation.objects.select_related('created_by').get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            type='user',
            text=text,
            status='sent'
        )
        # Update conversation timestamp
        conversation.save(update_fields=['updated_at'])
        
        # Invalidate message cache when new message is created
        cache_key = f'conv_messages_{self.conversation_id}'
        cache.delete(cache_key)
        logger.debug(f"Invalidated message cache for conversation {self.conversation_id}")
        
        return message
    
    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Mark messages as read"""
        try:
            messages = Message.objects.filter(
                id__in=message_ids,
                conversation_id=self.conversation_id
            )
            for message in messages:
                message.mark_as_read(self.user)
        except Exception as e:
            logger.error(f"Error marking messages as read: {e}")
    
    @database_sync_to_async
    def create_notifications_for_message(self, message):
        """Create notifications for all participants except sender - optimized with select_related"""
        try:
            from notifications.services import create_notification
            
            conversation = message.conversation
            sender = message.sender
            
            # Get all participants except sender - optimized with select_related
            participants = conversation.participants.select_related('user').exclude(user=sender)
            
            for participant in participants:
                sender_name = sender.username if sender else "System"
                sender_display = f"{sender.first_name} {sender.last_name}".strip() if sender and (sender.first_name or sender.last_name) else sender_name
                
                create_notification(
                    recipient=participant.user,
                    title=f"New message from {sender_display}",
                    message=message.text[:100] if message.text else "New message",
                    notification_type='chat_message_received',
                    actor=sender,
                    related_object_type='chat_message',
                    related_object_id=str(message.id),
                    metadata={
                        'conversation_id': str(conversation.id),
                        'sender_username': sender_name,
                    }
                )
        except Exception as e:
            logger.error(f"Error creating notifications for message: {e}")
    
    def sanitize_group_name(self, name: str) -> str:
        """Sanitize a string to be a valid Channels group name.
        
        Channels group names must be:
        - Valid unicode string
        - Length < 100
        - Only ASCII alphanumerics, hyphens, underscores, or periods
        """
        import re
        # Replace invalid characters with underscores
        # Keep only alphanumerics, hyphens, underscores, and periods
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
        # Ensure length is less than 100
        if len(sanitized) > 99:
            # Use a hash for very long names
            import hashlib
            hash_suffix = hashlib.md5(name.encode()).hexdigest()[:16]
            sanitized = sanitized[:82] + '_' + hash_suffix
        return sanitized
    
    # Call database operations
    @database_sync_to_async
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    