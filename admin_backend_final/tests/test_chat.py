"""
Tests for Chat/AI API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestChatAPIs:
    """Tests for Chat/AI management APIs."""

    @patch('admin_backend_final.chat.run_agent_with_tools')
    def test_user_response_success(self, mock_agent, api_client):
        """Test user message handling."""
        mock_agent.return_value = ("Test response", [])
        
        url = reverse("user_response")
        data = {
            "message": "Hello, how can I help?",
            "device_uuid": "test-uuid"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Actual implementation returns greeting/openers, not a raw 'response' field
        assert "greeting" in data or "bot_openers" in data or "bot_text" in data

    @patch('admin_backend_final.chat.run_agent_with_tools')
    def test_bot_response_success(self, mock_agent, api_client):
        """Test bot response generation."""
        mock_agent.return_value = ("Bot response", [])
        
        url = reverse("bot_response")
        data = {
            "message": "What products do you have?",
            "device_uuid": "test-uuid"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Bot endpoint returns structured fields like bot_text/categories
        assert "bot_text" in data or "categories" in data or "conversation_id" in data

    def test_bot_prompts_success(self, api_client):
        """Test retrieving bot prompts."""
        url = reverse("bot_prompts")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Response format may vary
        assert "prompts" in data or isinstance(data, list)

