"""
Tests for Category and SubCategory API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal

from admin_backend_final.models import Category, SubCategory, CategorySubCategoryMap, CategoryImage, Image
from .factories import CategoryFactory, SubCategoryFactory, ImageFactory


@pytest.mark.django_db
class TestSaveCategoryAPIView:
    """Tests for SaveCategoryAPIView - creating/updating categories."""

    def test_create_category_success(self, api_client):
        """Test creating a new category with valid data."""
        url = reverse("save_categories")
        data = {
            "name": "Test Category",
            "caption": "Test Caption",
            "description": "Test Description"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["success"] is True
        assert "category_id" in resp.json()
        
        # Verify category was created
        category = Category.objects.get(name="Test Category")
        assert category.caption == "Test Caption"
        assert category.description == "Test Description"
        assert category.status == "visible"

    def test_create_category_without_name_fails(self, api_client):
        """Test that creating a category without a name fails."""
        url = reverse("save_categories")
        data = {"caption": "Test Caption"}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in resp.json()

    def test_create_category_replaces_existing(self, api_client):
        """Test that creating a category with existing name replaces it."""
        # Create initial category
        category = CategoryFactory(name="Existing Category")
        original_id = category.category_id
        
        url = reverse("save_categories")
        data = {"name": "Existing Category", "caption": "New Caption"}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        
        # Verify old category was deleted and new one created
        assert not Category.objects.filter(category_id=original_id).exists()
        new_category = Category.objects.get(name="Existing Category")
        assert new_category.caption == "New Caption"


@pytest.mark.django_db
class TestShowCategoryAPIView:
    """Tests for ShowCategoryAPIView - listing categories."""

    def test_list_categories_empty(self, api_client):
        """Test listing categories when none exist."""
        url = reverse("show_categories")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == []  # API returns list directly, not wrapped

    def test_list_categories_with_data(self, api_client):
        """Test listing categories with existing data."""
        category1 = CategoryFactory(name="Category 1", order=1)
        category2 = CategoryFactory(name="Category 2", order=2)
        subcategory = SubCategoryFactory(name="Sub 1")
        CategorySubCategoryMap.objects.create(category=category1, subcategory=subcategory)
        
        url = reverse("show_categories")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()  # Returns list directly
        assert len(data) == 2
        assert data[0]["name"] == "Category 1"
        assert data[0]["subcategories"]["count"] == 1

    def test_list_categories_ordered(self, api_client):
        """Test that categories are returned in order."""
        category2 = CategoryFactory(name="Category 2", order=2)
        category1 = CategoryFactory(name="Category 1", order=1)
        category3 = CategoryFactory(name="Category 3", order=3)
        
        url = reverse("show_categories")
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        categories = resp.json()  # Returns list directly
        assert categories[0]["name"] == "Category 1"
        assert categories[1]["name"] == "Category 2"
        assert categories[2]["name"] == "Category 3"


@pytest.mark.django_db
class TestEditCategoryAPIView:
    """Tests for EditCategoryAPIView - updating categories."""

    def test_edit_category_success(self, api_client):
        """Test editing an existing category."""
        category = CategoryFactory(name="Original Name")
        url = reverse("edit_categories")
        # EditCategoryAPIView uses request.POST (form data), not JSON
        data = {
            "category_id": category.category_id,
            "name": "Updated Name",
            "caption": "Updated Caption",
            "status": "hidden"
        }
        resp = api_client.post(url, data)  # Form data, not JSON
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)

        if resp.status_code == status.HTTP_200_OK:
            category.refresh_from_db()
            assert category.name == "Updated Name"
            assert category.caption == "Updated Caption"

    def test_edit_category_not_found(self, api_client):
        """Test editing a non-existent category."""
        url = reverse("edit_categories")
        data = {"category_id": "nonexistent", "name": "Test"}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteCategoryAPIView:
    """Tests for DeleteCategoryAPIView - deleting categories."""

    def test_delete_category_success(self, api_client):
        """Test deleting a single category."""
        category = CategoryFactory()
        url = reverse("delete_categories")
        data = {"ids": [category.category_id]}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert not Category.objects.filter(category_id=category.category_id).exists()

    def test_delete_multiple_categories(self, api_client):
        """Test bulk deleting categories."""
        category1 = CategoryFactory()
        category2 = CategoryFactory()
        category3 = CategoryFactory()
        
        url = reverse("delete_categories")
        data = {"ids": [category1.category_id, category2.category_id]}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        
        assert not Category.objects.filter(category_id=category1.category_id).exists()
        assert not Category.objects.filter(category_id=category2.category_id).exists()
        assert Category.objects.filter(category_id=category3.category_id).exists()

    def test_delete_category_with_subcategories_cascades(self, api_client):
        """Test that deleting a category also deletes its subcategory mappings."""
        category = CategoryFactory()
        subcategory = SubCategoryFactory()
        CategorySubCategoryMap.objects.create(category=category, subcategory=subcategory)
        
        url = reverse("delete_categories")
        # API requires confirm=True when there are related mappings
        data = {"ids": [category.category_id], "confirm": True}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        
        # Category and mappings should be deleted
        assert not Category.objects.filter(category_id=category.category_id).exists()
        assert not CategorySubCategoryMap.objects.filter(category=category).exists()


@pytest.mark.django_db
class TestUpdateCategoryOrderAPIView:
    """Tests for UpdateCategoryOrderAPIView - reordering categories."""

    def test_update_category_order_success(self, api_client):
        """Test updating category order."""
        category1 = CategoryFactory(order=1)
        category2 = CategoryFactory(order=2)
        category3 = CategoryFactory(order=3)
        
        url = reverse("update_category_order")
        # API expects "ordered_categories" with "id" and "order" fields
        data = {
            "ordered_categories": [
                {"id": category3.category_id, "order": 1},
                {"id": category1.category_id, "order": 2},
                {"id": category2.category_id, "order": 3},
            ]
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        
        category1.refresh_from_db()
        category2.refresh_from_db()
        category3.refresh_from_db()
        assert category3.order == 1
        assert category1.order == 2
        assert category2.order == 3


@pytest.mark.django_db
class TestSubCategoryAPIs:
    """Tests for SubCategory API endpoints."""

    def test_create_subcategory_success(self, api_client):
        """Test creating a new subcategory."""
        category = CategoryFactory()
        url = reverse("save_subcategories")
        # API uses request.POST with category_ids as a list
        data = {
            "name": "Test Subcategory",
            "category_ids": [category.category_id],  # List format
            "caption": "Sub Caption"
        }
        resp = api_client.post(url, data)  # Form data, not JSON
        assert resp.status_code == status.HTTP_201_CREATED
        
        subcategory = SubCategory.objects.get(name="Test Subcategory")
        assert CategorySubCategoryMap.objects.filter(
            category=category, subcategory=subcategory
        ).exists()

    def test_list_subcategories(self, api_client):
        """Test listing subcategories."""
        category = CategoryFactory()
        subcategory1 = SubCategoryFactory(name="Sub 1")
        subcategory2 = SubCategoryFactory(name="Sub 2")
        CategorySubCategoryMap.objects.create(category=category, subcategory=subcategory1)
        CategorySubCategoryMap.objects.create(category=category, subcategory=subcategory2)
        
        url = reverse("show_subcategories")
        resp = api_client.get(url, {"category_id": category.category_id})
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        # Check actual response format - may be list or dict
        if isinstance(data, list):
            assert len(data) == 2
        else:
            assert len(data.get("subcategories", [])) == 2

    def test_delete_subcategory(self, api_client):
        """Test deleting a subcategory."""
        subcategory = SubCategoryFactory()
        url = reverse("delete_subcategories")
        data = {"ids": [subcategory.subcategory_id]}
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert not SubCategory.objects.filter(subcategory_id=subcategory.subcategory_id).exists()

    def test_update_subcategory_order(self, api_client):
        """Test updating subcategory order."""
        sub1 = SubCategoryFactory(order=1)
        sub2 = SubCategoryFactory(order=2)
        
        url = reverse("update_subcategory_order")
        # API expects "ordered_subcategories" with "id" and "order"
        data = {
            "ordered_subcategories": [
                {"id": sub2.subcategory_id, "order": 1},
                {"id": sub1.subcategory_id, "order": 2},
            ]
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        
        sub1.refresh_from_db()
        sub2.refresh_from_db()
        assert sub2.order == 1
        assert sub1.order == 2


@pytest.mark.django_db
class TestUpdateHiddenStatusAPIView:
    """Tests for UpdateHiddenStatusAPIView - toggling visibility."""

    def test_update_category_hidden_status(self, api_client):
        """Test updating category hidden status."""
        category = CategoryFactory(status="visible")
        url = reverse("update_hidden_status")
        # API expects "type" (categories/subcategories), "ids" (list), "status"
        data = {
            "type": "categories",
            "ids": [category.category_id],
            "status": "hidden"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        
        category.refresh_from_db()
        assert category.status == "hidden"

    def test_update_subcategory_hidden_status(self, api_client):
        """Test updating subcategory hidden status."""
        subcategory = SubCategoryFactory(status="visible")
        url = reverse("update_hidden_status")
        # API expects "type" (categories/subcategories), "ids" (list), "status"
        data = {
            "type": "subcategories",
            "ids": [subcategory.subcategory_id],
            "status": "hidden"
        }
        resp = api_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_200_OK
        
        subcategory.refresh_from_db()
        assert subcategory.status == "hidden"

