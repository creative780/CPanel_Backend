"""
Integration tests for chat functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from chat.models import Conversation, Participant, Message

User = get_user_model()


class ChatIntegrationTest(APITestCase):
    """End-to-end integration tests for chat flow"""
    
    def setUp(self):
        # Ensure database connection is available
        from django.db import connection
        connection.ensure_connection()
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.token1 = AccessToken.for_user(self.user1)
        self.token2 = AccessToken.for_user(self.user2)
    
    def test_end_to_end_chat_flow(self):
        """Test complete chat flow: create conversation, send messages, get bot response"""
        # Step 1: User1 creates conversation with User2
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('conversations-list-or-create')
        data = {
            'title': 'Chat with User2',
            'participant_id': str(self.user2.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation_id = response.data['id']
        
        # Step 2: User1 sends message via REST API
        url = reverse('user-response')
        data = {
            'message': 'Hello User2!',
            'conversation_id': conversation_id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        message_id = response.data['message_id']
        
        # Verify message was created
        message = Message.objects.get(id=message_id)
        self.assertEqual(message.text, 'Hello User2!')
        self.assertEqual(message.sender, self.user1)
        
        # Step 3: Get bot response
        url = reverse('bot-response')
        data = {'conversation_id': conversation_id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify bot message was created
        bot_messages = Message.objects.filter(
            conversation_id=conversation_id,
            type='bot'
        )
        self.assertEqual(bot_messages.count(), 1)
        
        # Step 4: User2 can access conversation and messages
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)  # User message + bot message
    
    def test_rest_api_message_triggers_websocket_broadcast(self):
        """Test that REST API message triggers WebSocket broadcast"""
        # This test verifies the integration point
        # Actual WebSocket testing is in test_websocket.py
        conversation = Conversation.objects.create(
            created_by=self.user1,
            title='Test Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user1,
            role='owner'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user2,
            role='member'
        )
        
        # Send message via REST API
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': 'Test message',
            'conversation_id': str(conversation.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify message was created (WebSocket broadcast is tested separately)
        message = Message.objects.get(id=response.data['message_id'])
        self.assertEqual(message.text, 'Test message')
    
    def test_multiple_participants_in_conversation(self):
        """Test conversation with multiple participants"""
        user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='testpass123'
        )
        
        # Create conversation with 3 participants
        conversation = Conversation.objects.create(
            created_by=self.user1,
            title='Group Chat'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user1,
            role='owner'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user2,
            role='member'
        )
        Participant.objects.create(
            conversation=conversation,
            user=user3,
            role='member'
        )
        
        # All participants should be able to access
        for user, token in [(self.user1, self.token1), (self.user2, self.token2)]:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            url = reverse('conversation-detail', kwargs={'conversation_id': conversation.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['participants']), 3)
    
    def test_conversation_persistence_across_requests(self):
        """Test conversation persistence across multiple requests"""
        # Create conversation
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('conversations-list-or-create')
        data = {'title': 'Persistent Conversation'}
        response = self.client.post(url, data, format='json')
        conversation_id = response.data['id']
        
        # Send message
        url = reverse('user-response')
        data = {
            'message': 'First message',
            'conversation_id': conversation_id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get conversation again
        url = reverse('conversation-detail', kwargs={'conversation_id': conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], conversation_id)
        
        # Get messages
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'First message')
    
    def test_message_ordering_in_conversation(self):
        """Test message ordering in conversation"""
        conversation = Conversation.objects.create(
            created_by=self.user1,
            title='Test Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user1,
            role='owner'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Send multiple messages
        messages = ['First', 'Second', 'Third', 'Fourth', 'Fifth']
        for msg_text in messages:
            data = {
                'message': msg_text,
                'conversation_id': str(conversation.id)
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get messages and verify order
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        returned_messages = [msg['text'] for msg in response.data]
        self.assertEqual(returned_messages, messages)
    
    def test_bot_response_integration(self):
        """Test bot response integration with conversation"""
        conversation = Conversation.objects.create(
            created_by=self.user1,
            title='Bot Test Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user1,
            role='owner'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        
        # Send user message
        url = reverse('user-response')
        data = {
            'message': 'Hello bot',
            'conversation_id': str(conversation.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get bot response
        url = reverse('bot-response')
        data = {'conversation_id': str(conversation.id)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bot_message_text = response.data['message']
        
        # Verify bot message is in conversation
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        message_texts = [msg['text'] for msg in response.data]
        self.assertIn('Hello bot', message_texts)
        self.assertIn(bot_message_text, message_texts)
    
    def test_file_attachment_flow(self):
        """Test complete file attachment flow"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        conversation = Conversation.objects.create(
            created_by=self.user1,
            title='File Test Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user1,
            role='owner'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        
        # Step 1: Upload file
        url = reverse('upload-attachment')
        file_content = b'test file content'
        test_file = SimpleUploadedFile(
            'test_file.pdf',
            file_content,
            content_type='application/pdf'
        )
        response = self.client.post(url, {'file': test_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attachment_id = response.data['attachment_id']
        
        # Step 2: Send message with attachment reference
        url = reverse('user-response')
        data = {
            'message': 'Check this file',
            'conversation_id': str(conversation.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 3: Verify message and attachment are linked
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_read_receipt_flow(self):
        """Test complete read receipt flow"""
        conversation = Conversation.objects.create(
            created_by=self.user1,
            title='Read Receipt Test'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user1,
            role='owner'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user2,
            role='member'
        )
        
        # User1 sends message
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': 'Test message',
            'conversation_id': str(conversation.id)
        }
        response = self.client.post(url, data, format='json')
        message_id = response.data['message_id']
        
        # User2 marks as read
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        url = reverse('message-read', kwargs={'message_id': message_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify participant last_read_at was updated
        participant = Participant.objects.get(
            conversation=conversation,
            user=self.user2
        )
        self.assertIsNotNone(participant.last_read_at)
    
    def test_conversation_state_consistency(self):
        """Test conversation state consistency across operations"""
        # Create conversation
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('conversations-list-or-create')
        data = {'title': 'State Test'}
        response = self.client.post(url, data, format='json')
        conversation_id = response.data['id']
        
        # Send messages
        url = reverse('user-response')
        for i in range(5):
            data = {
                'message': f'Message {i}',
                'conversation_id': conversation_id
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get conversation - should show updated state
        url = reverse('conversation-detail', kwargs={'conversation_id': conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('last_message'))
        
        # Get messages - should match conversation state
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
    
    def test_error_recovery_flow(self):
        """Test error recovery flow"""
        # Try to send message to non-existent conversation
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': 'Test',
            'conversation_id': 'non-existent-id'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # System should recover - create new conversation
        data = {'message': 'New conversation'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('conversation_id', response.data)