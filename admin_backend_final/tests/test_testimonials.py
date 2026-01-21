"""
Tests for Testimonials API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status

from admin_backend_final.models import Testimonial
from .factories import TestimonialFactory


@pytest.mark.django_db
class TestTestimonialsAPIs:
    """Tests for Testimonials management APIs."""

    def test_save_testimonials_success(self, api_client):
        """Test creating a testimonial."""
        url = reverse("save_testimonials")
        data = {
            "name": "Test User",
            "role": "Customer",
            "content": "Great product!",
            "rating": 5,
            "status": "published"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        
        testimonial = Testimonial.objects.filter(name="Test User").first()
        assert testimonial is not None
        assert testimonial.rating == 5

    def test_show_testimonials_success(self, api_client):
        """Test retrieving testimonials."""
        testimonial1 = TestimonialFactory(status="published")
        testimonial2 = TestimonialFactory(status="published")
        
        url = reverse("show_testimonials")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        testimonials = data if isinstance(data, list) else data.get("testimonials", [])
        assert len(testimonials) >= 2

    def test_edit_testimonials_success(self, api_client):
        """Test updating a testimonial."""
        testimonial = TestimonialFactory(name="Original Name")
        url = reverse("edit_testimonials")
        data = {
            "testimonial_id": testimonial.testimonial_id,
            "name": "Updated Name",
            "rating": 4
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        
        testimonial.refresh_from_db()
        assert testimonial.name == "Updated Name"
        assert testimonial.rating == 4












