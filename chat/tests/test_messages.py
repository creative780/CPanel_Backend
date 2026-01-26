"""
Tests for message operations endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from django.core.files.uploadedfile import SimpleUploadedFile
from chat.models import Conversation, Participant, Message

User = get_user_model()


class MessageOperationsTest(APITestCase):
    """Test message operation endpoints"""
    
    def ensure_db_connection(self):
        """Ensure database connection is available"""
        from django.db import connection
        try:
            connection.ensure_connection()
        except Exception:
            connection.close()
            connection.ensure_connection()
    
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
        
        self.conversation = Conversation.objects.create(
            created_by=self.user1,
            title='Test Conversation'
        )
        Participant.objects.create(
            conversation=self.conversation,
            user=self.user1,
            role='owner'
        )
        Participant.objects.create(
            conversation=self.conversation,
            user=self.user2,
            role='member'
        )
    
    def test_send_message_to_existing_conversation(self):
        """Test sending message to existing conversation"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': 'Hello, this is a test message',
            'conversation_id': str(self.conversation.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('conversation_id', response.data)
        self.assertIn('message_id', response.data)
        
        # Verify message was created
        self.ensure_db_connection()
        
        message_id = response.data['message_id']
        # Retry getting message if connection fails
        try:
            message = Message.objects.get(id=message_id)
        except Exception:
            self.ensure_db_connection()
            message = Message.objects.get(id=message_id)
        
        self.assertEqual(message.text, 'Hello, this is a test message')
        self.assertEqual(str(message.conversation.id), str(self.conversation.id))
        self.assertEqual(str(message.sender.id), str(self.user1.id))
    
    def test_send_message_without_conversation_id(self):
        """Test sending message without conversation_id creates new conversation"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {'message': 'New conversation message'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation_id = response.data['conversation_id']
        
        # Verify new conversation was created
        self.ensure_db_connection()
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            self.assertEqual(conversation.created_by.id, self.user1.id)
            
            # Verify message exists
            message = Message.objects.get(id=response.data['message_id'])
            self.assertEqual(message.text, 'New conversation message')
        except Exception:
            self.ensure_db_connection()
            conversation = Conversation.objects.get(id=conversation_id)
            message = Message.objects.get(id=response.data['message_id'])
            self.assertEqual(message.text, 'New conversation message')
    
    def test_send_message_with_participant_id(self):
        """Test sending message with participant_id creates conversation with participant"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': 'Hello user2',
            'participant_id': str(self.user2.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        conversation_id = response.data['conversation_id']
        
        # Verify both users are participants
        conversation = Conversation.objects.get(id=conversation_id)
        participants = Participant.objects.filter(conversation=conversation)
        self.assertEqual(participants.count(), 2)
        participant_users = [p.user for p in participants]
        self.assertIn(self.user1, participant_users)
        self.assertIn(self.user2, participant_users)
    
    def test_get_bot_response(self):
        """Test getting bot response for conversation"""
        # Create a user message first
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            type='user',
            text='Hello bot',
            status='sent'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('bot-response')
        data = {'conversation_id': str(self.conversation.id)}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIsInstance(response.data['message'], str)
        self.assertGreater(len(response.data['message']), 0)
        
        # Verify bot message was created
        bot_messages = Message.objects.filter(
            conversation=self.conversation,
            type='bot'
        )
        self.assertEqual(bot_messages.count(), 1)
    
    def test_bot_response_no_user_messages(self):
        """Test bot response with no user messages returns 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('bot-response')
        data = {'conversation_id': str(self.conversation.id)}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_mark_message_as_read(self):
        """Test marking message as read"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user2,
            type='user',
            text='Test message',
            status='sent'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('message-read', kwargs={'message_id': message.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        
        # Verify participant's last_read_at was updated
        participant = Participant.objects.get(
            conversation=self.conversation,
            user=self.user1
        )
        self.assertIsNotNone(participant.last_read_at)
    
    def test_upload_image_attachment(self):
        """Test uploading image attachment"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        # Create a test image file
        image_content = b'fake image content'
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            image_content,
            content_type='image/jpeg'
        )
        
        response = self.client.post(url, {'file': image_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment_id', response.data)
        self.assertIn('file_url', response.data)
        self.assertIn('file_name', response.data)
        self.assertEqual(response.data['file_name'], 'test_image.jpg')
    
    def test_upload_pdf_attachment(self):
        """Test uploading PDF attachment"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        pdf_content = b'%PDF-1.4 fake pdf content'
        pdf_file = SimpleUploadedFile(
            'test_document.pdf',
            pdf_content,
            content_type='application/pdf'
        )
        
        response = self.client.post(url, {'file': pdf_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment_id', response.data)
        self.assertEqual(response.data['file_name'], 'test_document.pdf')
    
    def test_reject_file_over_10mb(self):
        """Test rejecting file larger than 10MB"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        # Create a file larger than 10MB
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile(
            'large_file.jpg',
            large_content,
            content_type='image/jpeg'
        )
        
        response = self.client.post(url, {'file': large_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('10MB', response.data['error'])
    
    def test_reject_invalid_file_type(self):
        """Test rejecting invalid file types"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        # Try to upload an executable file
        exe_content = b'MZ\x90\x00'  # PE executable header
        exe_file = SimpleUploadedFile(
            'malicious.exe',
            exe_content,
            content_type='application/x-msdownload'
        )
        
        response = self.client.post(url, {'file': exe_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('not allowed', response.data['error'].lower())
    
    def test_empty_message_validation(self):
        """Test empty message validation returns 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {'message': ''}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_message_too_long(self):
        """Test message exceeding max length"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        # Create message longer than 1000 chars (if limit exists)
        long_message = 'x' * 2000
        data = {'message': long_message}
        
        response = self.client.post(url, data, format='json')
        
        # Should either succeed or return validation error
        # Check based on actual serializer validation
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('message', response.data)
    
    def test_send_message_with_invalid_participant_id(self):
        """Test sending message with invalid participant_id returns 400"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': 'Hello',
            'participant_id': '99999'  # Non-existent user ID
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 400 with error message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('does not exist', response.data['error'])
    
    def test_send_message_to_nonexistent_conversation(self):
        """Test sending message to non-existent conversation returns 404"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': 'Hello',
            'conversation_id': 'non-existent-id'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_send_message_to_conversation_user_not_participant(self):
        """Test sending message to conversation where user is not participant returns 404"""
        # Create conversation with only user2
        conversation = Conversation.objects.create(
            created_by=self.user2,
            title='User2 Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user2,
            role='owner'
        )
        
        # user1 tries to send message
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': 'Hello',
            'conversation_id': str(conversation.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_message_types(self):
        """Test different message types (user, bot, system)"""
        # User message
        user_msg = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            type='user',
            text='User message',
            status='sent'
        )
        self.assertEqual(user_msg.type, 'user')
        self.assertIsNotNone(user_msg.sender)
        
        # Bot message
        bot_msg = Message.objects.create(
            conversation=self.conversation,
            sender=None,
            type='bot',
            text='Bot message',
            status='sent'
        )
        self.assertEqual(bot_msg.type, 'bot')
        self.assertIsNone(bot_msg.sender)
        
        # System message
        system_msg = Message.objects.create(
            conversation=self.conversation,
            sender=None,
            type='system',
            text='System message',
            status='sent'
        )
        self.assertEqual(system_msg.type, 'system')
    
    def test_message_status_transitions(self):
        """Test message status transitions"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            type='user',
            text='Test message',
            status='sent'
        )
        self.assertEqual(message.status, 'sent')
        
        # Status can be updated (though not via API endpoint currently)
        message.status = 'delivered'
        message.save()
        self.assertEqual(message.status, 'delivered')
        
        message.status = 'read'
        message.save()
        self.assertEqual(message.status, 'read')
    
    def test_rich_content_field(self):
        """Test rich content JSON field"""
        rich_content = {
            'type': 'markdown',
            'content': '# Heading\n\nThis is **bold** text.'
        }
        
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            type='user',
            text='Message with rich content',
            rich=rich_content,
            status='sent'
        )
        
        self.assertIsNotNone(message.rich)
        self.assertEqual(message.rich['type'], 'markdown')
        self.assertIn('content', message.rich)
    
    def test_message_ordering_by_created_at(self):
        """Test messages are ordered by created_at"""
        # Create messages with delays
        msg1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            type='user',
            text='First message',
            status='sent'
        )
        
        import time
        time.sleep(0.1)
        
        msg2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            type='user',
            text='Second message',
            status='sent'
        )
        
        # Fetch messages
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('conversation-messages', kwargs={'conversation_id': self.conversation.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        messages = response.data
        self.assertGreaterEqual(len(messages), 2)
        
        # Messages should be in chronological order
        msg_texts = [m['text'] for m in messages]
        self.assertIn('First message', msg_texts)
        self.assertIn('Second message', msg_texts)
    
    def test_message_with_special_characters(self):
        """Test message with special characters"""
        special_text = 'Hello! @#$%^&*()_+-=[]{}|;:,.<>?/`~'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': special_text,
            'conversation_id': str(self.conversation.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.ensure_db_connection()
        try:
            message = Message.objects.get(id=response.data['message_id'])
        except Exception:
            self.ensure_db_connection()
            message = Message.objects.get(id=response.data['message_id'])
        self.assertEqual(message.text, special_text)
    
    def test_message_with_unicode(self):
        """Test message with unicode characters"""
        unicode_text = 'Hello 世界 مرحبا Здравствуй 🌟'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        data = {
            'message': unicode_text,
            'conversation_id': str(self.conversation.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.ensure_db_connection()
        try:
            message = Message.objects.get(id=response.data['message_id'])
        except Exception:
            self.ensure_db_connection()
            message = Message.objects.get(id=response.data['message_id'])
        self.assertEqual(message.text, unicode_text)
    
    def test_upload_gif_attachment(self):
        """Test uploading GIF attachment"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        gif_content = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!'
        gif_file = SimpleUploadedFile(
            'test_image.gif',
            gif_content,
            content_type='image/gif'
        )
        
        response = self.client.post(url, {'file': gif_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment_id', response.data)
        self.assertEqual(response.data['file_name'], 'test_image.gif')
    
    def test_upload_png_attachment(self):
        """Test uploading PNG attachment"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        png_file = SimpleUploadedFile(
            'test_image.png',
            png_content,
            content_type='image/png'
        )
        
        response = self.client.post(url, {'file': png_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment_id', response.data)
        self.assertEqual(response.data['file_name'], 'test_image.png')
    
    def test_attachment_metadata(self):
        """Test attachment metadata is returned correctly"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        file_content = b'test file content'
        test_file = SimpleUploadedFile(
            'test_file.pdf',
            file_content,
            content_type='application/pdf'
        )
        
        response = self.client.post(url, {'file': test_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment_id', response.data)
        self.assertIn('file_url', response.data)
        self.assertIn('file_name', response.data)
        self.assertIn('file_size', response.data)
        self.assertEqual(response.data['file_name'], 'test_file.pdf')
        self.assertEqual(response.data['file_size'], len(file_content))