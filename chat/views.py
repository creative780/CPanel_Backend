from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import CursorPagination
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Conversation, Participant, Message, Prompt
from .serializers import (
    ConversationSerializer, CreateConversationSerializer, MessageSerializer,
    CreateMessageSerializer, UserResponseSerializer, BotResponseSerializer,
    PromptSerializer, TypingSerializer, ReadReceiptSerializer
)
from .services.bot import generate_reply
import uuid

User = get_user_model()


class ConversationPagination(CursorPagination):
    page_size = 20
    ordering = '-updated_at'


@extend_schema(
    operation_id='conversations_list',
    summary='List conversations',
    description='Get conversations for the current user with cursor pagination',
    tags=['Chat']
)
@extend_schema(
    operation_id='conversations_create',
    summary='Create conversation',
    description='Create a new conversation',
    tags=['Chat'],
    methods=['POST']
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversations_list_or_create(request):
    """List conversations for current user (GET) or create a new conversation (POST)"""
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'GET':
        # List conversations
        paginator = ConversationPagination()
        
        # Get conversations where user is a participant
        conversations = Conversation.objects.filter(
            participants__user=request.user,
            is_archived=False
        ).prefetch_related(
            Prefetch('participants', queryset=Participant.objects.select_related('user'))
        ).distinct()
        
        result_page = paginator.paginate_queryset(conversations, request)
        serializer = ConversationSerializer(result_page, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        # Create new conversation
        logger.info(f"Creating conversation for user {request.user.id} ({request.user.username})")
        serializer = CreateConversationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                conversation = serializer.save()
                logger.info(f"Successfully created conversation {conversation.id}")
                return Response(
                    ConversationSerializer(conversation, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"Error creating conversation: {e}", exc_info=True)
                return Response(
                    {'error': 'Failed to create conversation', 'detail': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        logger.warning(f"Invalid conversation data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='conversation_detail',
    summary='Get conversation details',
    description='Get conversation details with last message',
    tags=['Chat']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, conversation_id):
    """Get conversation details"""
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related(
            Prefetch('participants', queryset=Participant.objects.select_related('user')),
            Prefetch('messages', queryset=Message.objects.select_related('sender').order_by('-created_at')[:1])
        ),
        id=conversation_id,
        participants__user=request.user
    )
    
    serializer = ConversationSerializer(conversation, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    operation_id='conversation_messages',
    summary='Get conversation messages',
    description='Get messages for a conversation with pagination',
    tags=['Chat']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conversation_id):
    """Get messages for a conversation"""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants__user=request.user
    )
    
    # Get messages with pagination
    limit = min(int(request.query_params.get('limit', 50)), 100)
    offset = int(request.query_params.get('offset', 0))
    
    messages = Message.objects.filter(
        conversation=conversation
    ).select_related('sender').order_by('created_at')[offset:offset+limit]
    
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    operation_id='user_response',
    summary='Submit user message',
    description='Submit a user message and receive conversation_id',
    tags=['Chat']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_response(request):
    """Submit user message and get conversation_id"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        serializer = UserResponseSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            logger.warning(f"Invalid user response data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        message_text = data['message']
        conversation_id = data.get('conversation_id')
        participant_id = data.get('participant_id')
        
        logger.info(f"Processing user message from {request.user.id} ({request.user.username}), conversation_id={conversation_id}, participant_id={participant_id}")
        
        # Get or create conversation
        conversation = None
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    participants__user=request.user
                )
                logger.info(f"Using existing conversation {conversation_id}")
            except Conversation.DoesNotExist:
                logger.warning(f"Conversation {conversation_id} not found or user not a participant")
                return Response(
                    {'error': 'Conversation not found or you are not a participant'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Create new conversation
            try:
                logger.info(f"Creating new conversation for user {request.user.id}")
                conversation = Conversation.objects.create(
                    created_by=request.user,
                    title=f"Chat with {request.user.username}"
                )
                Participant.objects.create(
                    conversation=conversation,
                    user=request.user,
                    role='owner'
                )
                logger.info(f"Created conversation {conversation.id} with owner {request.user.id}")
                
                # Add other participant if provided
                if participant_id:
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        other_user = User.objects.get(id=participant_id)
                        Participant.objects.get_or_create(
                            conversation=conversation,
                            user=other_user,
                            defaults={'role': 'member'}
                        )
                        logger.info(f"Added participant {participant_id} to conversation {conversation.id}")
                    except User.DoesNotExist:
                        logger.warning(f"Participant {participant_id} does not exist")
                        return Response(
                            {'error': f'Participant with ID {participant_id} does not exist'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    except Exception as e:
                        logger.error(f"Error adding participant {participant_id}: {e}", exc_info=True)
                        return Response(
                            {'error': 'Failed to add participant to conversation', 'detail': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
            except Exception as e:
                logger.error(f"Error creating conversation: {e}", exc_info=True)
                return Response(
                    {'error': 'Failed to create conversation', 'detail': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Create user message
        try:
            user_message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                type='user',
                text=message_text,
                status='sent'
            )
            logger.info(f"Created message {user_message.id} in conversation {conversation.id}")
        except Exception as e:
            logger.error(f"Error creating message: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to create message', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Update conversation timestamp
        try:
            conversation.save(update_fields=['updated_at'])
        except Exception as e:
            logger.warning(f"Failed to update conversation timestamp: {e}")
        
        # Broadcast message via WebSocket to all participants
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            from django.core.cache import cache
            
            channel_layer = get_channel_layer()
            if channel_layer:
                conversation_group_name = f'chat_{conversation.id}'
                
                # Get active connection count for logging
                active_connections = cache.get('active_ws_connections', 0)
                
                # Broadcast message to all participants in the conversation
                async_to_sync(channel_layer.group_send)(
                    conversation_group_name,
                    {
                        'type': 'message_new',
                        'message': {
                            'id': str(user_message.id),
                            'conversation_id': str(conversation.id),
                            'type': user_message.type,
                            'text': user_message.text,
                            'sender': user_message.sender.username if user_message.sender else None,
                            'sender_id': str(user_message.sender.id) if user_message.sender else None,
                            'sender_username': user_message.sender.username if user_message.sender else None,
                            'sender_name': f"{user_message.sender.first_name} {user_message.sender.last_name}".strip() if user_message.sender and (user_message.sender.first_name or user_message.sender.last_name) else (user_message.sender.username if user_message.sender else "System"),
                            'created_at': user_message.created_at.isoformat(),
                            'attachment': user_message.attachment.url if user_message.attachment else None,
                        }
                    }
                )
                logger.debug(f"Broadcast message {user_message.id} via WebSocket (active connections: {active_connections})")
        except ImportError:
            logger.debug("Channels not available, skipping WebSocket broadcast")
        except Exception as e:
            # Log error but don't fail the request if WebSocket broadcasting fails
            logger.warning(f"Failed to broadcast message via WebSocket: {e}", exc_info=True)
        
        # Create notifications for all participants except sender
        try:
            from notifications.services import create_notification
            
            participants = conversation.participants.exclude(user=request.user)
            sender_name = request.user.username
            sender_display = f"{request.user.first_name} {request.user.last_name}".strip() if (request.user.first_name or request.user.last_name) else sender_name
            
            for participant in participants:
                try:
                    create_notification(
                        recipient=participant.user,
                        title=f"New message from {sender_display}",
                        message=message_text[:100] if message_text else "New message",
                        notification_type='chat_message_received',
                        actor=request.user,
                        related_object_type='chat_message',
                        related_object_id=str(user_message.id),
                        metadata={
                            'conversation_id': str(conversation.id),
                            'sender_username': sender_name,
                        }
                    )
                    logger.debug(f"Created notification for participant {participant.user.id}")
                except Exception as e:
                    logger.warning(f"Failed to create notification for participant {participant.user.id}: {e}")
        except ImportError:
            logger.debug("Notifications service not available, skipping notification creation")
        except Exception as e:
            logger.warning(f"Failed to create notifications for message: {e}", exc_info=True)
        
        return Response({
            'conversation_id': str(conversation.id),
            'message_id': str(user_message.id)
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Unexpected error in user_response: {e}", exc_info=True)
        return Response(
            {'error': 'An unexpected error occurred', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id='bot_response',
    summary='Get bot response',
    description='Get bot response for a conversation',
    tags=['Chat']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bot_response(request):
    """Get bot response for conversation"""
    serializer = BotResponseSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    conversation_id = serializer.validated_data['conversation_id']
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants__user=request.user
    )
    
    # Get the last user message
    last_user_message = Message.objects.filter(
        conversation=conversation,
        type='user'
    ).order_by('-created_at').first()
    
    if not last_user_message:
        return Response(
            {'error': 'No user message found in conversation'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate bot reply
    try:
        bot_reply_text = generate_reply(conversation, last_user_message)
        
        # Create bot message
        bot_message = Message.objects.create(
            conversation=conversation,
            sender=None,  # Bot messages have no sender
            type='bot',
            text=bot_reply_text,
            status='sent'
        )
        
        # Update conversation timestamp
        conversation.save(update_fields=['updated_at'])
        
        return Response({
            'message': bot_reply_text
        })
        
    except Exception as e:
        return Response(
            {'error': 'Failed to generate bot response'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id='bot_prompts',
    summary='Get bot prompts',
    description='Get quick-start prompts for the bot',
    tags=['Chat']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bot_prompts(request):
    """Get bot prompts"""
    prompts = Prompt.objects.filter(is_active=True).order_by('order', 'title')
    serializer = PromptSerializer(prompts, many=True)
    return Response(serializer.data)


@extend_schema(
    operation_id='chat_users_list',
    summary='List users for chat',
    description='Get list of all users that can be contacted via chat (accessible to all authenticated users)',
    tags=['Chat']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_users_list(request):
    """List all users for chat - accessible to all authenticated users"""
    try:
        # Get all users (excluding superusers)
        users = User.objects.filter(is_superuser=False).order_by('username')
        
        # Try to get HR employee data for profile pictures and designations
        hr_employees_map = {}
        try:
            from hr.models import HREmployee
            hr_employees = HREmployee.objects.select_related('user').all()
            for emp in hr_employees:
                if emp.user_id:
                    hr_employees_map[emp.user_id] = {
                        'image': emp.image.url if emp.image else None,
                        'designation': emp.designation,
                        'role': emp.role,
                    }
                if emp.email:
                    hr_employees_map[emp.email.lower()] = {
                        'image': emp.image.url if emp.image else None,
                        'designation': emp.designation,
                        'role': emp.role,
                    }
        except Exception:
            pass  # HR app might not be available
        
        # Serialize users
        users_data = []
        for user in users:
            hr_data = hr_employees_map.get(user.id) or hr_employees_map.get(user.email.lower() if user.email else '') or {}
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': user.roles or [],
                'image': hr_data.get('image'),
                'designation': hr_data.get('designation'),
                'role': hr_data.get('role'),
                'matrix_user_id': user.matrix_user_id,  # Include Matrix user ID for chat integration
            })
        
        return Response(users_data, status=status.HTTP_200_OK)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error listing chat users: {e}")
        return Response(
            {'error': 'Failed to fetch users'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id='message_read',
    summary='Mark message as read',
    description='Mark messages as read and update participant last_read_at',
    tags=['Chat']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def message_read(request, message_id):
    """Mark message as read"""
    message = get_object_or_404(
        Message,
        id=message_id,
        conversation__participants__user=request.user
    )
    
    # Mark message as read for this user (updates Participant.last_read_at)
    message.mark_as_read(request.user)
    
    # Get updated participant to return last_read_at
    try:
        participant = Participant.objects.get(
            conversation=message.conversation,
            user=request.user
        )
        return Response({
            'status': 'success',
            'last_read_at': participant.last_read_at.isoformat() if participant.last_read_at else None
        })
    except Participant.DoesNotExist:
        return Response({'status': 'success'})


@extend_schema(
    operation_id='typing_indicator',
    summary='Send typing indicator',
    description='Send typing indicator (ephemeral, no DB storage)',
    tags=['Chat']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def typing_indicator(request):
    """Send typing indicator"""
    serializer = TypingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # This is handled by WebSocket consumers
    # HTTP endpoint is just for validation
    return Response({'status': 'success'})


@extend_schema(
    operation_id='upload_attachment',
    summary='Upload attachment',
    description='Upload file attachment for chat messages',
    tags=['Chat']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attachment(request):
    """Upload attachment for chat messages"""
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Check file size
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        return Response(
            {'error': 'File size cannot exceed 10MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
    if file.content_type not in allowed_types:
        return Response(
            {'error': 'File type not allowed. Only images and PDFs are supported.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create a temporary message with attachment
    temp_message = Message.objects.create(
        conversation=None,  # Will be set when message is actually sent
        sender=request.user,
        type='user',
        text='',  # Will be set when message is sent
        attachment=file,
        status='sent'
    )
    
    return Response({
        'attachment_id': str(temp_message.id),
        'file_url': request.build_absolute_uri(temp_message.attachment.url),
        'file_name': file.name,
        'file_size': file.size
    })