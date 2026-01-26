"""
Tests for health check functionality.
"""

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json


class HealthCheckTestCase(TestCase):
    """Test cases for health check endpoints."""

    def test_health_check_endpoint(self):
        """Test the REST API health check endpoint."""
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('services', data)
        self.assertIn('database', data['services'])
        self.assertIn('redis', data['services'])
        self.assertIn('storage', data['services'])

    @patch('app.health.views.check_database')
    def test_health_check_database_failure(self, mock_db_check):
        """Test health check when database is down."""
        mock_db_check.return_value = False
        
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertFalse(data['services']['database'])

    @patch('app.health.views.check_redis')
    def test_health_check_redis_failure(self, mock_redis_check):
        """Test health check when Redis is down."""
        mock_redis_check.return_value = False
        
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertFalse(data['services']['redis'])

    @patch('app.health.views.check_storage')
    def test_health_check_storage_failure(self, mock_storage_check):
        """Test health check when storage is down."""
        mock_storage_check.return_value = False
        
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertFalse(data['services']['storage'])

    def test_health_check_all_services_healthy(self):
        """Test health check when all services are healthy."""
        with patch('app.health.views.check_database', return_value=True), \
             patch('app.health.views.check_redis', return_value=True), \
             patch('app.health.views.check_storage', return_value=True):
            
            url = reverse('health_check')
            response = self.client.get(url)
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'healthy')
            self.assertTrue(data['services']['database'])
            self.assertTrue(data['services']['redis'])
            self.assertTrue(data['services']['storage'])

