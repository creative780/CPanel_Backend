"""
Tests for bot prompts endpoint
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from chat.models import Prompt

User = get_user_model()


class BotPromptsTest(APITestCase):
    """Test bot prompts endpoint"""
    
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
        
        # Create active prompts
        self.prompt1 = Prompt.objects.create(
            title='Prompt 1',
            text='This is prompt 1',
            order=1,
            is_active=True
        )
        self.prompt2 = Prompt.objects.create(
            title='Prompt 2',
            text='This is prompt 2',
            order=2,
            is_active=True
        )
        self.prompt3 = Prompt.objects.create(
            title='Prompt 3',
            text='This is prompt 3',
            order=3,
            is_active=True
        )
        
        # Create inactive prompt (should not appear)
        self.inactive_prompt = Prompt.objects.create(
            title='Inactive Prompt',
            text='This should not appear',
            order=0,
            is_active=False
        )
    
    def test_get_active_prompts_only(self):
        """Test that only active prompts are returned"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('bot-prompts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Verify inactive prompt is not included
        prompt_titles = [p['title'] for p in response.data]
        self.assertIn('Prompt 1', prompt_titles)
        self.assertIn('Prompt 2', prompt_titles)
        self.assertIn('Prompt 3', prompt_titles)
        self.assertNotIn('Inactive Prompt', prompt_titles)
    
    def test_prompts_ordered_by_order_field(self):
        """Test that prompts are ordered by order field"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('bot-prompts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify order
        self.assertEqual(response.data[0]['title'], 'Prompt 1')
        self.assertEqual(response.data[1]['title'], 'Prompt 2')
        self.assertEqual(response.data[2]['title'], 'Prompt 3')
        
        # Verify order values
        self.assertEqual(response.data[0]['order'], 1)
        self.assertEqual(response.data[1]['order'], 2)
        self.assertEqual(response.data[2]['order'], 3)
    
    def test_empty_prompts_list(self):
        """Test empty prompts list when no active prompts exist"""
        # Deactivate all prompts
        Prompt.objects.all().update(is_active=False)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('bot-prompts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])
    
    def test_prompts_include_all_fields(self):
        """Test that prompts include all required fields"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('bot-prompts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        prompt = response.data[0]
        self.assertIn('id', prompt)
        self.assertIn('title', prompt)
        self.assertIn('text', prompt)
        self.assertIn('order', prompt)
    
    def test_unauthorized_access(self):
        """Test that unauthorized access returns 401"""
        self.client.credentials()  # Remove auth
        url = reverse('bot-prompts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
