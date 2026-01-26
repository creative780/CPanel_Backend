from django.urls import path
from .views import (
    conversations_list_or_create, conversation_detail, conversation_messages,
    user_response, bot_response, bot_prompts, message_read, typing_indicator, upload_attachment,
    chat_users_list
)

urlpatterns = [
    # Conversation management
    path('chat/conversations/', conversations_list_or_create, name='conversations-list-or-create'),
    path('chat/conversations/<str:conversation_id>/', conversation_detail, name='conversation-detail'),
    path('chat/conversations/<str:conversation_id>/messages/', conversation_messages, name='conversation-messages'),
    
    # Bot interaction endpoints (matching frontend expectations)
    path('user-response/', user_response, name='user-response'),
    path('bot-response/', bot_response, name='bot-response'),
    path('bot-prompts/', bot_prompts, name='bot-prompts'),
    
    # Message actions
    path('chat/messages/<str:message_id>/read/', message_read, name='message-read'),
    path('chat/typing/', typing_indicator, name='typing-indicator'),
    path('chat/upload/', upload_attachment, name='upload-attachment'),
    
    # Chat users (accessible to all authenticated users)
    path('chat/users/', chat_users_list, name='chat-users-list'),
]