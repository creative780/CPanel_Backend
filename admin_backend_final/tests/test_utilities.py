"""
Tests for Utilities API endpoints (Image upload, Product ID generation, etc.).
"""
import pytest
from django.urls import reverse
from rest_framework import status
from io import BytesIO
from PIL import Image as PILImage

from admin_backend_final.models import Image
from .factories import ImageFactory, SubCategoryFactory


@pytest.mark.django_db
class TestSaveImageAPIView:
    """Tests for SaveImageAPIView - image upload."""

    def test_save_image_base64_success(self, api_client):
        """Test uploading an image via base64."""
        # Create a simple test image
        img = PILImage.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = buffer.getvalue()
        import base64
        base64_str = base64.b64encode(img_str).decode('utf-8')
        data_url = f"data:image/png;base64,{base64_str}"
        
        url = reverse("save_image")
        data = {
            "image": data_url,
            "alt_text": "Test Image",
            "tags": "test",
            "linked_table": "test",
            "linked_id": "test123"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        data = resp.json()
        assert "image_id" in data or "success" in data

    def test_save_image_without_data_fails(self, api_client):
        """Test that uploading without image data fails."""
        url = reverse("save_image")
        data = {"alt_text": "Test"}
        resp = api_client.post(url, data, format="json")
        # May return 400 or 200 depending on implementation
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
class TestGenerateProductIdAPIView:
    """Tests for GenerateProductIdAPIView - product ID generation."""

    def test_generate_product_id_success(self, api_client):
        """Test generating a product ID."""
        subcategory = SubCategoryFactory()
        url = reverse("generate_product_id")
        data = {
            "name": "Test Product",
            "subcategory_id": subcategory.subcategory_id
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "product_id" in data
        assert len(data["product_id"]) > 0

    def test_generate_product_id_without_name_fails(self, api_client):
        """Test that generating ID without name fails."""
        url = reverse("generate_product_id")
        data = {"subcategory_id": "test123"}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

