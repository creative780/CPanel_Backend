"""
Performance tests for chat functionality
"""
import time
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from chat.models import Conversation, Participant, Message

User = get_user_model()


class ChatPerformanceTest(APITestCase):
    """Test performance aspects of chat functionality"""
    
    def setUp(self):
        # Ensure database connection is available
        from django.db import connection
        connection.ensure_connection()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_load_conversations_with_many_messages(self):
        """Test loading conversations with 100+ messages"""
        # Create conversation with 150 messages
        conversation = Conversation.objects.create(
            created_by=self.user,
            title='Large Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user,
            role='owner'
        )
        
        # Create 150 messages
        for i in range(150):
            Message.objects.create(
                conversation=conversation,
                sender=self.user,
                type='user',
                text=f'Message {i}',
                status='sent'
            )
        
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation.id})
        
        start_time = time.time()
        response = self.client.get(url, {'limit': 50, 'offset': 0})
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 50)
        
        # Should complete in reasonable time (< 1 second)
        self.assertLess(elapsed_time, 1.0, f"Query took {elapsed_time}s, should be < 1s")
    
    def test_pagination_performance_large_offset(self):
        """Test pagination performance with large offset"""
        conversation = Conversation.objects.create(
            created_by=self.user,
            title='Large Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user,
            role='owner'
        )
        
        # Create 200 messages
        for i in range(200):
            Message.objects.create(
                conversation=conversation,
                sender=self.user,
                type='user',
                text=f'Message {i}',
                status='sent'
            )
        
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation.id})
        
        # Test accessing messages at offset 190
        start_time = time.time()
        response = self.client.get(url, {'limit': 10, 'offset': 190})
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        
        # Should complete in reasonable time (< 1 second)
        self.assertLess(elapsed_time, 1.0, f"Query took {elapsed_time}s, should be < 1s")
    
    def test_conversation_list_performance(self):
        """Test conversation list performance with many conversations"""
        # Create 50 conversations
        for i in range(50):
            conversation = Conversation.objects.create(
                created_by=self.user,
                title=f'Conversation {i}'
            )
            Participant.objects.create(
                conversation=conversation,
                user=self.user,
                role='owner'
            )
            
            # Add a few messages to each
            for j in range(5):
                Message.objects.create(
                    conversation=conversation,
                    sender=self.user,
                    type='user',
                    text=f'Message {j}',
                    status='sent'
                )
        
        url = reverse('conversations-list-or-create')
        
        start_time = time.time()
        response = self.client.get(url)
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should complete in reasonable time (< 1 second)
        self.assertLess(elapsed_time, 1.0, f"Query took {elapsed_time}s, should be < 1s")
    
    def test_message_creation_performance(self):
        """Test message creation performance"""
        conversation = Conversation.objects.create(
            created_by=self.user,
            title='Test Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user,
            role='owner'
        )
        
        url = reverse('user-response')
        data = {
            'message': 'Test message',
            'conversation_id': str(conversation.id)
        }
        
        # Test multiple message creations
        start_time = time.time()
        for i in range(10):
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elapsed_time = time.time() - start_time
        
        # 10 messages should be created quickly (< 2 seconds)
        self.assertLess(elapsed_time, 2.0, f"10 messages took {elapsed_time}s, should be < 2s")
        avg_time = elapsed_time / 10
        self.assertLess(avg_time, 0.2, f"Average message creation took {avg_time}s, should be < 0.2s")
    
    def test_conversation_detail_with_last_message_performance(self):
        """Test conversation detail query performance with last message"""
        conversation = Conversation.objects.create(
            created_by=self.user,
            title='Test Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user,
            role='owner'
        )
        
        # Create 100 messages
        for i in range(100):
            Message.objects.create(
                conversation=conversation,
                sender=self.user,
                type='user',
                text=f'Message {i}',
                status='sent'
            )
        
        url = reverse('conversation-detail', kwargs={'conversation_id': conversation.id})
        
        start_time = time.time()
        response = self.client.get(url)
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should complete quickly (< 0.5 seconds)
        self.assertLess(elapsed_time, 0.5, f"Query took {elapsed_time}s, should be < 0.5s")
    
    def test_bot_response_performance(self):
        """Test bot response generation performance"""
        conversation = Conversation.objects.create(
            created_by=self.user,
            title='Test Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user,
            role='owner'
        )
        
        Message.objects.create(
            conversation=conversation,
            sender=self.user,
            type='user',
            text='Hello',
            status='sent'
        )
        
        url = reverse('bot-response')
        data = {'conversation_id': str(conversation.id)}
        
        start_time = time.time()
        response = self.client.post(url, data, format='json')
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Bot response should be fast (< 1 second for echo bot)
        self.assertLess(elapsed_time, 1.0, f"Bot response took {elapsed_time}s, should be < 1s")
    
    def test_large_message_history_performance(self):
        """Test performance with large message history (1000+ messages)"""
        conversation = Conversation.objects.create(
            created_by=self.user,
            title='Large History Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user,
            role='owner'
        )
        
        # Create 1000 messages
        messages = []
        for i in range(1000):
            messages.append(Message(
                conversation=conversation,
                sender=self.user,
                type='user',
                text=f'Message {i}',
                status='sent'
            ))
        
        # Bulk create for performance
        Message.objects.bulk_create(messages)
        
        url = reverse('conversation-messages', kwargs={'conversation_id': conversation.id})
        
        # Test fetching first page
        start_time = time.time()
        response = self.client.get(url, {'limit': 50, 'offset': 0})
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 50)
        
        # Should complete quickly even with 1000 messages (< 1 second)
        self.assertLess(elapsed_time, 1.0, f"Query with 1000 messages took {elapsed_time}s")
    
    def test_many_participants_performance(self):
        """Test performance with many participants per conversation"""
        conversation = Conversation.objects.create(
            created_by=self.user,
            title='Multi-participant Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user,
            role='owner'
        )
        
        # Create 20 additional participants
        for i in range(20):
            participant_user = User.objects.create_user(
                username=f'participant{i}',
                email=f'participant{i}@example.com',
                password='testpass123'
            )
            Participant.objects.create(
                conversation=conversation,
                user=participant_user,
                role='member'
            )
        
        url = reverse('conversation-detail', kwargs={'conversation_id': conversation.id})
        
        start_time = time.time()
        response = self.client.get(url)
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should handle many participants efficiently (< 0.5 seconds)
        self.assertLess(elapsed_time, 0.5, f"Query with 21 participants took {elapsed_time}s")
    
    def test_concurrent_operations_performance(self):
        """Test performance under concurrent operations"""
        conversation = Conversation.objects.create(
            created_by=self.user,
            title='Concurrent Test Conversation'
        )
        Participant.objects.create(
            conversation=conversation,
            user=self.user,
            role='owner'
        )
        
        url = reverse('user-response')
        
        # Simulate concurrent message creation
        import threading
        
        results = []
        errors = []
        
        def send_message(i):
            try:
                data = {
                    'message': f'Concurrent message {i}',
                    'conversation_id': str(conversation.id)
                }
                response = self.client.post(url, data, format='json')
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create 10 threads sending messages concurrently
        threads = []
        start_time = time.time()
        for i in range(10):
            thread = threading.Thread(target=send_message, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        elapsed_time = time.time() - start_time
        
        # Should handle concurrent operations (< 2 seconds)
        self.assertLess(elapsed_time, 2.0, f"10 concurrent messages took {elapsed_time}s")
        # Most should succeed
        success_count = sum(1 for code in results if code == status.HTTP_201_CREATED)
        self.assertGreater(success_count, 8, "Most concurrent operations should succeed")
    
    def test_file_upload_performance(self):
        """Test file upload performance"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        url = reverse('upload-attachment')
        
        # Create a reasonably sized file (1MB)
        file_content = b'x' * (1 * 1024 * 1024)
        test_file = SimpleUploadedFile(
            'test_image.jpg',
            file_content,
            content_type='image/jpeg'
        )
        
        start_time = time.time()
        response = self.client.post(url, {'file': test_file}, format='multipart')
        elapsed_time = time.time() - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # File upload should complete in reasonable time (< 2 seconds for 1MB)
        self.assertLess(elapsed_time, 2.0, f"1MB file upload took {elapsed_time}s")