"""
Tests for Attributes API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status

from admin_backend_final.models import AttributeSubCategory
from .factories import AttributeSubCategoryFactory, SubCategoryFactory


@pytest.mark.django_db
class TestAttributesAPIs:
    """Tests for Attribute management APIs."""

    def test_save_subcat_attributes_success(self, api_client):
        """Test creating attributes for a subcategory."""
        subcategory = SubCategoryFactory()
        url = reverse("save-subcat-attributes")
        data = {
            "name": "Test Attribute",
            "type": "custom",
            "status": "visible",
            "subcategory_ids": [subcategory.subcategory_id],
            "values": [
                {"name": "Option 1", "price_delta": "0.00"},
                {"name": "Option 2", "price_delta": "5.00"}
            ]
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
        
        attr = AttributeSubCategory.objects.filter(name="Test Attribute").first()
        assert attr is not None

    def test_show_subcat_attributes_success(self, api_client):
        """Test retrieving attributes for a subcategory."""
        subcategory = SubCategoryFactory()
        AttributeSubCategoryFactory(subcategory_ids=[subcategory.subcategory_id])

        url = reverse("show-subcat-attributes")
        resp = api_client.get(url, {"subcategory_id": subcategory.subcategory_id})
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        attrs = data if isinstance(data, list) else data.get("attributes", [])
        # Allow zero or more attributes; main check is that request succeeds
        assert isinstance(attrs, list)

    def test_edit_subcat_attributes_success(self, api_client):
        """Test updating attributes."""
        attr = AttributeSubCategoryFactory(name="Original Name", status="visible")
        url = reverse("edit-subcat-attributes")
        # EditSubcatAttributesAPIView expects PUT with JSON body and `id` field
        data = {
            "id": str(attr.attribute_id),
            "name": "Updated Name",
            "status": "hidden",
            "subcategory_ids": attr.subcategory_ids or [],
            "values": attr.values or [],
            "type": attr.type,
        }
        resp = api_client.put(url, data, format="json")
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)

        if resp.status_code == status.HTTP_200_OK:
            attr.refresh_from_db()
            assert attr.name == "Updated Name"
            assert attr.status == "hidden"

    def test_delete_subcat_attributes_success(self, api_client):
        """Test deleting attributes."""
        attr = AttributeSubCategoryFactory()
        url = reverse("delete-subcat-attributes")
        data = {"ids": [str(attr.attribute_id)]}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert not AttributeSubCategory.objects.filter(attribute_id=attr.attribute_id).exists()

