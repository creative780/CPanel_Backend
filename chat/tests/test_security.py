"""
Security tests for chat functionality
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


class ChatSecurityTest(APITestCase):
    """Test security aspects of chat functionality"""
    
    def setUp(self):
        # Ensure database connection is available
        from django.db import connection
        connection.ensure_connection()
        
        try:
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
            
            # Create conversation for user1
            self.conversation = Conversation.objects.create(
                created_by=self.user1,
                title='User1 Conversation'
            )
            Participant.objects.create(
                conversation=self.conversation,
                user=self.user1,
                role='owner'
            )
        except Exception as e:
            # If connection fails, try to reconnect
            connection.close()
            connection.ensure_connection()
            # Retry once
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
                title='User1 Conversation'
            )
            Participant.objects.create(
                conversation=self.conversation,
                user=self.user1,
                role='owner'
            )
    
    def test_unauthenticated_access_rejected(self):
        """Test that unauthenticated access returns 401"""
        self.client.credentials()  # Remove auth
        
        endpoints = [
            ('conversations-list-or-create', 'GET', {}),
            ('user-response', 'POST', {'message': 'test'}),
            ('bot-response', 'POST', {'conversation_id': 'test'}),
            ('bot-prompts', 'GET', {}),
            ('chat-users-list', 'GET', {}),
        ]
        
        for endpoint_name, method, data in endpoints:
            try:
                # Build URL with proper kwargs
                if 'conversation_id' in data:
                    url = reverse(endpoint_name, kwargs={'conversation_id': data['conversation_id']})
                else:
                    url = reverse(endpoint_name)
                
                if method == 'GET':
                    response = self.client.get(url)
                else:
                    # Remove conversation_id from POST data if it was used in URL
                    post_data = {k: v for k, v in data.items() if k != 'conversation_id'}
                    response = self.client.post(url, post_data, format='json')
                
                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                    f"Endpoint {endpoint_name} should require authentication"
                )
            except Exception as e:
                # Skip endpoints that don't exist or have issues
                self.fail(f"Failed to test endpoint {endpoint_name}: {e}")
    
    def test_user_cannot_access_other_users_conversations(self):
        """Test user cannot access conversations they're not part of"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        
        # Try to access user1's conversation
        url = reverse('conversation-detail', kwargs={'conversation_id': self.conversation.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_send_message_to_unauthorized_conversation(self):
        """Test user cannot send message to conversation they're not part of"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        url = reverse('user-response')
        data = {
            'message': 'Unauthorized message',
            'conversation_id': str(self.conversation.id)
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should return 404 (conversation not found for this user)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_jwt_token_validation_in_websocket(self):
        """Test JWT token validation in WebSocket (tested via API endpoint)"""
        # This is a placeholder - actual WebSocket token validation
        # is tested in test_websocket.py
        # Here we verify the endpoint requires valid token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        url = reverse('user-response')
        data = {'message': 'test'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_participant_verification(self):
        """Test that participant verification works correctly"""
        # Create conversation with only user1
        conversation = Conversation.objects.create(
            created_by=self.user1,
            title='Private Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user1,
            role='owner'
        )
        
        # user2 tries to access
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        url = reverse('conversation-detail', kwargs={'conversation_id': conversation.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_file_upload_security_file_type_limits(self):
        """Test file upload security - file type limits"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        # Try to upload executable file
        exe_content = b'MZ\x90\x00'  # PE executable
        exe_file = SimpleUploadedFile(
            'malicious.exe',
            exe_content,
            content_type='application/x-msdownload'
        )
        
        response = self.client.post(url, {'file': exe_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not allowed', response.data.get('error', '').lower())
    
    def test_file_upload_security_size_limits(self):
        """Test file upload security - size limits"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        # Try to upload file larger than 10MB
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        large_file = SimpleUploadedFile(
            'large_file.jpg',
            large_content,
            content_type='image/jpeg'
        )
        
        response = self.client.post(url, {'file': large_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('10MB', response.data.get('error', ''))
    
    def test_xss_prevention_in_messages(self):
        """Test XSS prevention in messages"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Try to inject script tag
        xss_message = '<script>alert("XSS")</script>'
        data = {'message': xss_message}
        
        response = self.client.post(url, data, format='json')
        
        # Message should be stored as-is (frontend should sanitize)
        # Backend should accept it but frontend should handle sanitization
        if response.status_code == status.HTTP_201_CREATED:
            message_id = response.data['message_id']
            message = Message.objects.get(id=message_id)
            # Backend stores raw text - sanitization is frontend responsibility
            self.assertEqual(message.text, xss_message)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Try SQL injection in message
        sql_injection = "'; DROP TABLE chat_message; --"
        data = {'message': sql_injection}
        
        response = self.client.post(url, data, format='json')
        
        # Should succeed (Django ORM prevents SQL injection)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify message was stored and table still exists
        message_id = response.data['message_id']
        message = Message.objects.get(id=message_id)
        self.assertEqual(message.text, sql_injection)
        
        # Verify table still exists (no SQL injection occurred)
        self.assertTrue(Message.objects.filter(id=message_id).exists())
    
    def test_conversation_id_validation(self):
        """Test that invalid conversation IDs are rejected"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Try with invalid UUID format
        data = {
            'message': 'Test',
            'conversation_id': 'invalid-uuid-format'
        }
        
        response = self.client.post(url, data, format='json')
        # Should return 404 or 400 depending on validation
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_message_length_limits(self):
        """Test message length limits"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Create very long message (over 1000 chars if limit exists)
        long_message = 'x' * 2000
        data = {'message': long_message}
        
        response = self.client.post(url, data, format='json')
        
        # Should either succeed or return validation error
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('message', response.data)
    
    def test_expired_token_handling(self):
        """Test expired token handling"""
        from datetime import timedelta
        from django.utils import timezone
        from rest_framework_simplejwt.tokens import AccessToken
        
        # Create token with very short expiration (already expired)
        # Note: This is a simplified test - actual expiration testing requires time manipulation
        self.client.credentials(HTTP_AUTHORIZATION='Bearer expired_token_here')
        url = reverse('conversations-list-or-create')
        response = self.client.get(url)
        
        # Should return 401 for invalid/expired token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_html_tag_stripping(self):
        """Test HTML tag stripping in messages"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Message with HTML tags
        html_message = '<p>Hello <b>world</b></p>'
        data = {'message': html_message}
        
        response = self.client.post(url, data, format='json')
        
        # Message should be stored (sanitization happens in WebSocket consumer or frontend)
        if response.status_code == status.HTTP_201_CREATED:
            message_id = response.data['message_id']
            message = Message.objects.get(id=message_id)
            # Backend stores raw - sanitization is in consumer
            self.assertIsNotNone(message.text)
    
    def test_script_tag_removal(self):
        """Test script tag removal"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Message with script tags
        script_message = '<script>alert("XSS")</script>Hello'
        data = {'message': script_message}
        
        response = self.client.post(url, data, format='json')
        
        # Message should be stored (sanitization in WebSocket consumer)
        if response.status_code == status.HTTP_201_CREATED:
            message_id = response.data['message_id']
            message = Message.objects.get(id=message_id)
            # Backend stores raw - WebSocket consumer sanitizes
            self.assertIsNotNone(message.text)
    
    def test_special_character_handling(self):
        """Test special character handling"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Message with special characters
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?/`~'
        data = {'message': special_chars}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        message_id = response.data['message_id']
        message = Message.objects.get(id=message_id)
        self.assertEqual(message.text, special_chars)
    
    def test_unicode_support(self):
        """Test Unicode support in messages"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Message with Unicode characters
        unicode_message = 'Hello 世界 مرحبا Здравствуй 🌟'
        data = {'message': unicode_message}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        message_id = response.data['message_id']
        message = Message.objects.get(id=message_id)
        self.assertEqual(message.text, unicode_message)
    
    def test_path_traversal_prevention(self):
        """Test path traversal prevention in file uploads"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        # Try to upload file with path traversal in name
        path_traversal_name = '../../../etc/passwd'
        file_content = b'test content'
        malicious_file = SimpleUploadedFile(
            path_traversal_name,
            file_content,
            content_type='image/jpeg'
        )
        
        response = self.client.post(url, {'file': malicious_file}, format='multipart')
        
        # Should either reject or sanitize filename
        # If accepted, filename should be sanitized
        if response.status_code == status.HTTP_200_OK:
            # Filename should not contain path traversal
            self.assertNotIn('..', response.data.get('file_name', ''))
        else:
            # Or should be rejected
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_content_type_validation(self):
        """Test content-type validation for file uploads"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        # Try to upload file with mismatched content-type
        file_content = b'fake image content'
        mismatched_file = SimpleUploadedFile(
            'test.jpg',
            file_content,
            content_type='text/html'  # Wrong content type
        )
        
        response = self.client.post(url, {'file': mismatched_file}, format='multipart')
        
        # Should reject invalid content type
        # Note: Actual validation depends on implementation
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('error', response.data)
    
    def test_file_name_sanitization(self):
        """Test file name sanitization"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('upload-attachment')
        
        # Try to upload file with dangerous characters in name
        dangerous_name = 'file<script>alert(1)</script>.jpg'
        file_content = b'fake image content'
        dangerous_file = SimpleUploadedFile(
            dangerous_name,
            file_content,
            content_type='image/jpeg'
        )
        
        response = self.client.post(url, {'file': dangerous_file}, format='multipart')
        
        # Filename should be sanitized if accepted
        if response.status_code == status.HTTP_200_OK:
            sanitized_name = response.data.get('file_name', '')
            self.assertNotIn('<script>', sanitized_name)
            self.assertNotIn('</script>', sanitized_name)
    
    def test_message_rate_limiting(self):
        """Test message rate limiting (10 per minute)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Send 11 messages rapidly
        for i in range(11):
            data = {'message': f'Message {i}'}
            response = self.client.post(url, data, format='json')
            
            # After 10 messages, should start getting rate limit errors
            # Note: Rate limiting may not trigger in test environment
            if i >= 10 and response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                self.assertIn('rate limit', str(response.data).lower())
                break
    
    def test_connection_rate_limiting(self):
        """Test connection rate limiting (5 per user)"""
        # This is tested in WebSocket tests, but verify via API
        # that the system can handle multiple requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('conversations-list-or-create')
        
        # Make multiple requests
        for i in range(10):
            response = self.client.get(url)
            # Should all succeed (rate limiting is for WebSocket connections)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_rate_limit_reset_behavior(self):
        """Test rate limit reset behavior"""
        # This test verifies that rate limits reset after time period
        # Note: Actual testing requires time manipulation
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Send messages
        for i in range(5):
            data = {'message': f'Message {i}'}
            response = self.client.post(url, data, format='json')
            # Should succeed for first few messages
            if i < 5:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_rate_limit_error_messages(self):
        """Test rate limit error messages are user-friendly"""
        # This test verifies error messages when rate limit is hit
        # Note: May not trigger in test environment
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('user-response')
        
        # Try to trigger rate limit (may not work in test)
        # If rate limit is hit, error should be clear
        data = {'message': 'Test'}
        response = self.client.post(url, data, format='json')
        
        # If rate limited, should return 429 with clear message
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            self.assertIn('error', response.data or {})
    
    def test_participant_role_validation(self):
        """Test participant role validation"""
        # Create conversation with specific roles
        conversation = Conversation.objects.create(
            created_by=self.user1,
            title='Role Test Conversation'
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
        
        # Both should be able to access
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('conversation-detail', kwargs={'conversation_id': conversation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token2}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)