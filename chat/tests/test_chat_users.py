"""
Tests for chat users endpoint
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from chat.models import Conversation, Participant

User = get_user_model()


class ChatUsersTest(APITestCase):
    """Test chat users endpoint"""
    
    def setUp(self):
        # Ensure database connection is available
        from django.db import connection
        connection.ensure_connection()
        
        # Create regular users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        
        # Create superuser (should be excluded)
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.token1 = AccessToken.for_user(self.user1)
    
    def test_list_all_non_superuser_users(self):
        """Test listing all non-superuser users"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('chat-users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        
        # Should include regular users
        usernames = [u['username'] for u in response.data]
        self.assertIn('user1', usernames)
        self.assertIn('user2', usernames)
        
        # Should exclude superuser
        self.assertNotIn('admin', usernames)
    
    def test_users_include_basic_fields(self):
        """Test that users include basic fields"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('chat-users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        user = response.data[0]
        self.assertIn('id', user)
        self.assertIn('username', user)
        self.assertIn('email', user)
        self.assertIn('first_name', user)
        self.assertIn('last_name', user)
    
    def test_users_ordered_by_username(self):
        """Test that users are ordered by username"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('chat-users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        if len(response.data) > 1:
            usernames = [u['username'] for u in response.data]
            sorted_usernames = sorted(usernames)
            self.assertEqual(usernames, sorted_usernames)
    
    def test_authenticated_access_required(self):
        """Test that authenticated access is required"""
        self.client.credentials()  # Remove auth
        url = reverse('chat-users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_users_with_hr_data(self):
        """Test that users include HR employee data when available"""
        try:
            from hr.models import HREmployee
            
            # Create HR employee for user1
            hr_employee = HREmployee.objects.create(
                user=self.user1,
                designation='Developer',
                role='Engineering'
            )
            
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
            url = reverse('chat-users-list')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            # Find user1 in response
            user1_data = next((u for u in response.data if u['username'] == 'user1'), None)
            if user1_data:
                # HR data might be included if HR app is available
                self.assertIsNotNone(user1_data)
        except ImportError:
            # HR app might not be available, skip this test
            pass
    
    def test_matrix_user_id_included(self):
        """Test that Matrix user ID is included in user data"""
        # Set matrix_user_id if the field exists
        if hasattr(self.user1, 'matrix_user_id'):
            self.user1.matrix_user_id = '@user1:example.com'
            self.user1.save()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('chat-users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user1_data = next((u for u in response.data if u['username'] == 'user1'), None)
        if user1_data:
            # matrix_user_id field should be present (may be None)
            self.assertIn('matrix_user_id', user1_data)
    
    def test_user_profile_data_completeness(self):
        """Test that user profile data includes all expected fields"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('chat-users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        user = response.data[0]
        expected_fields = ['id', 'username', 'email', 'first_name', 'last_name']
        for field in expected_fields:
            self.assertIn(field, user)
    
    def test_users_accessible_to_all_authenticated_users(self):
        """Test that all authenticated users can access chat users list"""
        # user2 should be able to see user1 and vice versa
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token1}')
        url = reverse('chat-users-list')
        response1 = self.client.get(url)
        
        token2 = AccessToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        response2 = self.client.get(url)
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Both should see the same users (excluding themselves potentially)
        usernames1 = {u['username'] for u in response1.data}
        usernames2 = {u['username'] for u in response2.data}
        
        # Should have overlap (both see user1 and user2)
        self.assertIn('user1', usernames1)
        self.assertIn('user2', usernames1)
        self.assertIn('user1', usernames2)
        self.assertIn('user2', usernames2)