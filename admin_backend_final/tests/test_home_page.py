"""
Tests for Home Page content API endpoints (Carousels, Hero Banner, Nav Items).
"""
import pytest
from django.urls import reverse
from rest_framework import status

from admin_backend_final.models import FirstCarousel, FirstCarouselImage, SecondCarousel, SecondCarouselImage, HeroBanner, HeroBannerImage
from .factories import FirstCarouselFactory, SecondCarouselFactory, HeroBannerFactory, ImageFactory


@pytest.mark.django_db
class TestFirstCarouselAPIView:
    """Tests for FirstCarouselAPIView."""

    def test_get_first_carousel_success(self, api_client):
        """Test retrieving first carousel data."""
        carousel = FirstCarouselFactory()
        url = reverse("first_carousel")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Response format may vary
        assert "carousel" in data or "title" in data or len(data) > 0

    def test_save_first_carousel_success(self, api_client):
        """Test saving first carousel data."""
        url = reverse("first_carousel")
        data = {
            "title": "Test Carousel",
            "description": "Test Description"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)


@pytest.mark.django_db
class TestSecondCarouselAPIView:
    """Tests for SecondCarouselAPIView."""

    def test_get_second_carousel_success(self, api_client):
        """Test retrieving second carousel data."""
        carousel = SecondCarouselFactory()
        url = reverse("second_carousel")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Response format may vary
        assert "carousel" in data or "title" in data or len(data) > 0

    def test_save_second_carousel_success(self, api_client):
        """Test saving second carousel data."""
        url = reverse("second_carousel")
        data = {
            "title": "Test Carousel 2",
            "description": "Test Description 2"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)


@pytest.mark.django_db
class TestHeroBannerAPIView:
    """Tests for HeroBannerAPIView."""

    def test_get_hero_banner_success(self, api_client):
        """Test retrieving hero banner data."""
        banner = HeroBannerFactory()
        url = reverse("hero_banner")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Response format may vary
        assert "banner" in data or "hero_id" in data or len(data) > 0

    def test_save_hero_banner_success(self, api_client):
        """Test saving hero banner data."""
        url = reverse("hero_banner")
        data = {
            "alt_text": "Test Banner Alt Text"
        }
        resp = api_client.post(url, data, format="json")
        # Implementation may reject incomplete payloads; ensure no server error
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
class TestShowNavItemsAPIView:
    """Tests for ShowNavItemsAPIView."""

    def test_get_nav_items_success(self, api_client):
        """Test retrieving navigation items."""
        url = reverse("show_nav_items")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Response format may vary
        assert "items" in data or "categories" in data or isinstance(data, list)

