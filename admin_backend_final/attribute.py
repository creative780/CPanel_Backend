# app/attributes_api.py
# DRF backend for AttributeSubCategory – aligned with your frontend contract.

import json
import uuid
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

from django.db import transaction, connection
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from typing import Optional
from .models import AttributeSubCategory, Attribute, Image, Product  # <- model added earlier
from .permissions import FrontendOnlyPermission
from .utilities import save_image


# ------------------------------
# Helpers
# ------------------------------
def _ensure_unique_slug(base_slug: Optional[str]) -> str:
    """
    Ensure slug uniqueness across AttributeSubCategory by suffixing -2, -3, ...
    """
    slug = base_slug or "attr"
    if not AttributeSubCategory.objects.filter(slug=slug).exists():
        return slug
    i = 2
    while True:
        candidate = f"{slug}-{i}"
        if not AttributeSubCategory.objects.filter(slug=candidate).exists():
            return candidate
        i += 1

def _normalize_values(values):
    if values is None:
        return ([], "")
    if not isinstance(values, list):
        return ([], "values must be a list")

    normalized = []
    default_count = 0

    for v in values:
        if not isinstance(v, dict):
            return ([], "each value must be an object")

        vid = str(v.get("id") or uuid.uuid4())
        name = (v.get("name") or "").strip()
        if not name:
            return ([], "each value requires a non-empty 'name'")

        pd = v.get("price_delta", None)
        if pd is not None:
            try:
                pd = float(pd)
            except Exception:
                return ([], "price_delta must be numeric")

        is_default = bool(v.get("is_default", False))
        if is_default:
            default_count += 1

        image_url = (v.get("image_url") or "").strip()
        image_id  = (v.get("image_id") or "").strip()   # ✅ new
        desc = (v.get("description") or "").strip()

        item = {
            "id": vid,
            "name": name,
            "is_default": is_default,
        }
        if pd is not None:
            item["price_delta"] = pd
        if image_url:
            item["image_url"] = image_url
        if image_id:
            item["image_id"] = image_id                 # ✅ persist
        if desc:
            item["description"] = desc

        normalized.append(item)

    if default_count > 1:
        return ([], "only one option can be marked as default")

    return (normalized, "")

def _normalize_sub_ids(sub_ids) -> Tuple[List[str], str]:
    if sub_ids is None:
        return ([], "")
    if not isinstance(sub_ids, list):
        return ([], "subcategory_ids must be a list")
    out = [str(x).strip() for x in sub_ids if str(x).strip()]
    return (out, "")

def _normalize_payload(obj: dict, *, is_create: bool) -> Tuple[dict, str]:
    """
    Map incoming JSON to model fields, validate, and return normalized payload.
    NEW: pass through 'description' for the attribute itself.
    """
    if not isinstance(obj, dict):
        return ({}, "invalid payload")

    name = (obj.get("name") or "").strip()
    if not name:
        return ({}, "name is required")

    type_ = (obj.get("type") or "custom").strip().lower()
    if type_ not in {"size", "color", "material", "custom"}:
        return ({}, "type must be one of: size, color, material, custom")

    status_val = (obj.get("status") or "visible").strip().lower()
    if status_val not in {"visible", "hidden"}:
        return ({}, "status must be 'visible' or 'hidden'")

    values, v_err = _normalize_values(obj.get("values"))
    if v_err:
        return ({}, v_err)

    sub_ids, s_err = _normalize_sub_ids(obj.get("subcategory_ids"))
    if s_err:
        return ({}, s_err)

    raw_slug = (obj.get("slug") or slugify(name) or "attr").lower()
    slug = raw_slug

    # only ensure uniqueness on create or when user changed slug on edit
    if is_create or (obj.get("slug") and AttributeSubCategory.objects.exclude(slug=raw_slug).filter(slug=raw_slug).exists()):
        slug = _ensure_unique_slug(raw_slug)

    normalized = {
        # Use client id if present, else generate UUID (string)
        "attribute_id": str(obj.get("id") or uuid.uuid4()),
        "name": name,
        "slug": slug,
        "type": type_,
        "status": status_val,
        "description": (obj.get("description") or "").strip(),  # NEW
        "values": values,
        "subcategory_ids": sub_ids,  # empty list => global
    }

    return (normalized, "")

def _serialize_attribute(m: AttributeSubCategory) -> dict:
    clean_values = []
    for val in (m.values or []):
        if isinstance(val, dict):
            # strip only image_data, leave image_id and image_url
            clean = {k: v for k, v in val.items() if k != "image_data"}
            clean_values.append(clean)
        else:
            clean_values.append(val)

    return {
        "id": str(m.attribute_id),
        "name": m.name,
        "slug": m.slug,
        "type": m.type,
        "status": m.status,
        "description": getattr(m, "description", "") or "",
        "values": clean_values,
        "created_at": m.created_at.isoformat(),
        "subcategory_ids": m.subcategory_ids or [],
    }

# ------------------------------
# Views
# ------------------------------
class ShowSubcatAttributesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        """
        Optional filter: ?subcategory_id=<ID>
        Pagination: ?page=1&page_size=50

        No DB ordering except PK; Python-sorts the small page by name.
        """
        try:
            sub_id = (request.GET.get("subcategory_id") or "").strip()

            # Pagination (bounded)
            try:
                page = max(1, int(request.GET.get("page", 1)))
            except Exception:
                page = 1
            try:
                page_size = int(request.GET.get("page_size", 50))
            except Exception:
                page_size = 50
            page_size = min(max(1, page_size), 200)
            offset = (page - 1) * page_size

            base = AttributeSubCategory.objects.all().order_by()

            if sub_id:
                # Check database backend to determine query strategy
                is_sqlite = connection.vendor == 'sqlite'
                
                if is_sqlite:
                    # SQLite doesn't support __contains on JSONField
                    # Filter in Python instead
                    all_attrs = list(AttributeSubCategory.objects.all())
                    filtered_attrs = []
                    for attr in all_attrs:
                        sub_ids = attr.subcategory_ids or []
                        # Check if sub_id is in the list OR if list is empty (global attribute)
                        if sub_id in sub_ids or len(sub_ids) == 0:
                            filtered_attrs.append(attr.attribute_id)
                    
                    # Now filter by the IDs we found
                    if filtered_attrs:
                        base = AttributeSubCategory.objects.filter(attribute_id__in=filtered_attrs).order_by()
                    else:
                        # No matches, return empty queryset
                        base = AttributeSubCategory.objects.none()
                else:
                    # MySQL/PostgreSQL support JSONField contains lookup
                    base = base.filter(
                        Q(subcategory_ids__contains=[sub_id]) | Q(subcategory_ids=[])
                    ).order_by()

            total = base.count()

            id_page = list(
                base.order_by("attribute_id")
                    .values_list("attribute_id", flat=True)[offset : offset + page_size]
            )

            if not id_page:
                return Response(
                    {"count": total, "page": page, "page_size": page_size, "results": []},
                    status=status.HTTP_200_OK,
                )

            objs = AttributeSubCategory.objects.only(
                "attribute_id", "name", "slug", "type", "status",
                "description",
                "values", "created_at", "subcategory_ids"
            ).in_bulk(id_page, field_name="attribute_id")

            items = [objs.get(aid) for aid in id_page if aid in objs and objs.get(aid)]
            items.sort(key=lambda o: (o.name or "").lower())

            data = [_serialize_attribute(a) for a in items]

            return Response(
                {"count": total, "page": page, "page_size": page_size, "results": data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": str(e), "message": "Failed to fetch attributes"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SaveSubcatAttributesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        try:
            payload = request.data if isinstance(request.data, dict) else json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            payload = {}

        normalized, err = _normalize_payload(payload, is_create=True)
        if err:
            return Response({"error": err}, status=status.HTTP_400_BAD_REQUEST)

        # Reject duplicate attribute names (global uniqueness)
        if AttributeSubCategory.objects.filter(name__iexact=normalized["name"]).exists():
            return Response({"error": f"An attribute with the name '{normalized['name']}' already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # If slug collides (race), re-ensure
        if AttributeSubCategory.objects.filter(slug=normalized["slug"]).exists():
            normalized["slug"] = _ensure_unique_slug(normalized["slug"])

        obj = AttributeSubCategory.objects.create(
            attribute_id=normalized["attribute_id"],
            name=normalized["name"],
            slug=normalized["slug"],
            type=normalized["type"],
            status=normalized["status"],
            description=normalized["description"],  # NEW
            values=normalized["values"],
            subcategory_ids=normalized["subcategory_ids"],
        )
        return Response(_serialize_attribute(obj), status=status.HTTP_201_CREATED)

class EditSubcatAttributesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def put(self, request):
        try:
            payload = request.data if isinstance(request.data, dict) else json.loads(request.body.decode("utf-8") or "{}")
        except Exception:
            payload = {}

        obj_id = str(payload.get("id") or "").strip()
        if not obj_id:
            return Response({"error": "id is required for edit"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = AttributeSubCategory.objects.get(attribute_id=obj_id)
        except AttributeSubCategory.DoesNotExist:
            return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)

        normalized, err = _normalize_payload(payload, is_create=False)
        if err:
            return Response({"error": err}, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate name (exclude current attribute)
        if AttributeSubCategory.objects.filter(name__iexact=normalized["name"]).exclude(attribute_id=obj.attribute_id).exists():
            return Response({"error": f"An attribute with the name '{normalized['name']}' already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if normalized["slug"] != obj.slug and AttributeSubCategory.objects.exclude(attribute_id=obj.attribute_id).filter(slug=normalized["slug"]).exists():
            normalized["slug"] = _ensure_unique_slug(normalized["slug"])

        obj.name = normalized["name"]
        obj.slug = normalized["slug"]
        obj.type = normalized["type"]
        obj.status = normalized["status"]
        obj.description = normalized["description"]  # NEW
        obj.values = normalized["values"]
        obj.subcategory_ids = normalized["subcategory_ids"]
        obj.updated_at = timezone.now()
        obj.save()

        # Sync product Attribute images when AttributeSubCategory is edited
        # Find all product attributes with matching name
        product_attrs = Attribute.objects.filter(
            name=obj.name,
            parent__isnull=True  # Only parent attributes
        ).select_related('product').prefetch_related('options')

        # Create a mapping of option label to updated image info from AttributeSubCategory.values
        value_map = {}
        for val in obj.values:
            if isinstance(val, dict):
                option_name = val.get('name') or val.get('label', '')
                if option_name:
                    value_map[option_name] = {
                        'image_id': val.get('image_id'),
                        'image_url': val.get('image_url'),
                    }

        # Update product attribute options
        for parent_attr in product_attrs:
            for option in parent_attr.options.all():
                option_label = option.label
                if option_label in value_map:
                    val_data = value_map[option_label]
                    new_image = None
                    
                    # Try to get image by image_id first
                    if val_data.get('image_id'):
                        new_image = Image.objects.filter(image_id=val_data['image_id']).first()
                    
                    # If no image_id or not found, try to save from image_url
                    if not new_image and val_data.get('image_url'):
                        try:
                            saved = save_image(
                                val_data['image_url'],
                                alt_text=f"{obj.name} - {option_label}",
                                tags="attribute,option",
                                linked_table="product_attribute",
                                linked_page="product-detail",
                                linked_id=parent_attr.attr_id,
                            )
                            if hasattr(saved, "pk"):
                                new_image = saved
                            elif isinstance(saved, dict) and saved.get("image_id"):
                                new_image = Image.objects.filter(image_id=saved["image_id"]).first()
                        except Exception:
                            # Skip if image save fails
                            pass
                    
                    # Update option image if we have a new one
                    if new_image and option.image != new_image:
                        option.image = new_image
                        option.save(update_fields=['image'])

        return Response(_serialize_attribute(obj), status=status.HTTP_200_OK)

class DeleteSubcatAttributesAPIView(APIView):
  permission_classes = [FrontendOnlyPermission]

  @transaction.atomic
  def post(self, request):
      try:
          data = request.data if isinstance(request.data, dict) else json.loads(request.body.decode("utf-8") or "{}")
      except Exception:
          data = {}
      ids = data.get("ids", [])
      if not isinstance(ids, list) or not ids:
          return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

      ids = [str(x).strip() for x in ids if str(x).strip()]
      
      try:
          # Get the attribute names before deleting, so we can find and delete product-specific attributes
          attributes_to_delete = AttributeSubCategory.objects.filter(attribute_id__in=ids)
          attribute_names = list(attributes_to_delete.values_list('name', flat=True))
          
          # Delete from AttributeSubCategory
          deleted_subcat, _ = AttributeSubCategory.objects.filter(attribute_id__in=ids).delete()
          
          # Verify deletion
          remaining = AttributeSubCategory.objects.filter(attribute_id__in=ids).count()
          if remaining > 0:
              return Response({
                  "error": f"Failed to delete all attributes. {remaining} still exist.",
                  "deleted": deleted_subcat
              }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
          # Also delete product-specific Attribute records that match these attribute names
          # This will cascade delete their options (due to CASCADE on_delete)
          deleted_product_attrs = 0
          if attribute_names:
              # Find all product attributes (parent attributes only, not options) with matching names
              product_attributes = Attribute.objects.filter(
                  name__in=attribute_names,
                  parent__isnull=True  # Only parent attributes, not options
              )
              deleted_product_attrs, _ = product_attributes.delete()
          
          return Response({
              "success": True, 
              "deleted": deleted_subcat,
              "deleted_product_attributes": deleted_product_attrs
          }, status=status.HTTP_200_OK)
      except Exception as e:
          logger.error(f"Error deleting attributes: {e}", exc_info=True)
          return Response({
              "error": f"Error deleting attributes: {str(e)}"
          }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)