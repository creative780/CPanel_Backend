# category.py

import json
from django.db import transaction
from django.db.models import Count, Prefetch, F
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utilities import generate_category_id, generate_subcategory_id, save_image
from .models import (
    Category,
    SubCategory,
    Image,
    CategoryImage,
    SubCategoryImage,
    CategorySubCategoryMap,
    ProductSubCategoryMap,
)
from .permissions import FrontendOnlyPermission


def _safe_json(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return {}


class SaveCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        if request.content_type and "application/json" in request.content_type:
            data = request.data if isinstance(request.data, dict) else _safe_json(request)
            files = {}
        else:
            data = request.POST
            files = request.FILES

        name = (data.get("name") or "").strip()
        if not name:
            return Response({"error": "Name is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Replace existing with same name (preserves original behavior)
        existing = Category.objects.filter(name=name)
        if existing.exists():
            existing.delete()

        # Order calculated inside transaction to avoid races
        category_id = generate_category_id(name)
        now = timezone.now()
        order = (Category.objects.aggregate(cnt=Count("pk"))["cnt"] or 0) + 1

        caption = (data.get("caption") or "").strip() or None
        description = (data.get("description") or "").strip() or None

        category = Category.objects.create(
            category_id=category_id,
            name=name,
            status="visible",
            caption=caption,
            description=description,
            created_by="SuperAdmin",
            created_at=now,
            updated_at=now,
            order=order,
        )

        alt_text = (data.get("alt_text") or data.get("alText") or f"{name} category image").strip()
        tags = (data.get("tags") or data.get("imageTags") or "")

        image_data = files.get("image") or data.get("image")
        if image_data:
            img = save_image(
                file_or_base64=image_data,
                alt_text=alt_text,
                tags=tags,
                linked_table="category",
                linked_page="CategorySubCategoryPage",
                linked_id=category_id,
            )
            if img:
                CategoryImage.objects.create(category=category, image=img)

        return Response(
            {"success": True, "category_id": category_id, "caption": caption, "description": description},
            status=status.HTTP_201_CREATED,
        )


class ShowCategoryAPIView(APIView):
    """
    Optimized: single pass with prefetch + annotate to avoid N+1
    - product count via chained relation Count
    - first image via prefetch; pick in Python without extra queries
    """
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        imgs = Prefetch("images", queryset=CategoryImage.objects.select_related("image"))
        qs = (
            Category.objects
            .prefetch_related(imgs)
            .annotate(products=Count("categorysubcategorymap__subcategory__productsubcategorymap", distinct=True))
            .order_by("order")
        )

        result = []
        for cat in qs:
            rel = cat.images.first()
            img_obj = rel.image if rel and rel.image_id else None
            img_url = img_obj.url if img_obj else None
            alt_text = img_obj.alt_text if img_obj else ""

            # Pre-get subcategory names with one prefetch lookup
            sub_names = list(
                CategorySubCategoryMap.objects
                .filter(category=cat)
                .select_related("subcategory")
                .values_list("subcategory__name", flat=True)
            )

            result.append({
                "id": cat.category_id,
                "name": cat.name,
                "image": img_url,
                "imageAlt": alt_text,
                "subcategories": {
                    "names": sub_names or None,
                    "count": len(sub_names) or 0,
                },
                "products": cat.products or 0,
                "status": cat.status,
                "order": cat.order,
                "caption": cat.caption,
                "description": cat.description,
            })
        return Response(result, status=status.HTTP_200_OK)


class EditCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = request.POST
        category_id = data.get("category_id")
        try:
            category = Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        new_name = (data.get("name") or "").strip()
        if new_name:
            category.name = new_name

        if "caption" in data:
            category.caption = (data.get("caption") or "").strip() or None
        if "description" in data:
            category.description = (data.get("description") or "").strip() or None

        category.updated_at = timezone.now()
        category.save(update_fields=["name", "caption", "description", "updated_at"])

        alt_text = (data.get("alt_text") or data.get("imageAlt") or data.get("altText") or "").strip()
        image_data = request.FILES.get("image") or request.POST.get("image")

        if image_data:
            old_rels = list(CategoryImage.objects.filter(category=category).select_related("image"))
            old_images = [rel.image for rel in old_rels if rel.image_id]
            CategoryImage.objects.filter(category=category).delete()

            for img in old_images:
                if img and not CategoryImage.objects.filter(image=img).exists():
                    if getattr(img, "image_file", None):
                        img.image_file.delete(save=False)
                    img.delete()

            image = save_image(
                image_data,
                alt_text or "Alt-text",
                data.get("tags", ""),
                "category",
                "CategorySubCategoryPage",
                category_id,
            )
            if image:
                CategoryImage.objects.create(category=category, image=image)
        else:
            if alt_text:
                rel = CategoryImage.objects.filter(category=category).select_related("image").first()
                if rel and rel.image:
                    rel.image.alt_text = alt_text
                    rel.image.save(update_fields=["alt_text"])

        return Response({"success": True, "message": "Category updated"}, status=status.HTTP_200_OK)


class DeleteCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = _safe_json(request)
        category_ids = data.get("ids", [])
        confirm = data.get("confirm", False)

        if not category_ids:
            return Response({"error": "No category IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        for cid in set(category_ids):
            try:
                category = Category.objects.get(category_id=cid)
            except Category.DoesNotExist:
                continue

            related_mappings = CategorySubCategoryMap.objects.filter(category=category)
            if not confirm and related_mappings.exists():
                return Response(
                    {
                        "confirm": True,
                        "message": "Deleting this category will delete its subcategories and related products. Continue?",
                    },
                    status=status.HTTP_200_OK,
                )

            for mapping in list(related_mappings.select_related("subcategory")):
                subcat = mapping.subcategory
                other_links = CategorySubCategoryMap.objects.filter(subcategory=subcat).exclude(category=category)
                mapping.delete()
                if not other_links.exists():
                    # If this subcategory becomes orphaned, delete its products (if not shared)
                    rel_prods = ProductSubCategoryMap.objects.filter(subcategory=subcat)
                    for m in list(rel_prods.select_related("product")):
                        other_prod_links = ProductSubCategoryMap.objects.filter(product=m.product).exclude(subcategory=subcat)
                        m.delete()
                        if not other_prod_links.exists():
                            m.product.delete()

                    # Delete subcategory images + subcategory
                    SubCategoryImage.objects.filter(subcategory=subcat).delete()
                    subcat.delete()

            # Finally delete category images and category
            CategoryImage.objects.filter(category=category).delete()
            category.delete()

        return Response({"success": True, "message": "Selected categories deleted"}, status=status.HTTP_200_OK)

class UpdateCategoryOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = _safe_json(request)
        ordered = data.get("ordered_categories")
        if not isinstance(ordered, list):
            ordered = data.get("ordered_subcategories")  # legacy fallback

        if not isinstance(ordered, list) or not ordered:
            return Response({"success": False, "error": "Invalid payload"}, status=400)

        updated_count = 0
        for item in ordered:
            cid = str(item.get("id") or item.get("category_id") or "").strip()
            try:
                ordv = int(item.get("order"))
            except Exception:
                continue
            if cid and ordv:
                updated_count += Category.objects.filter(category_id=cid).update(order=ordv)

        return Response({"success": True, "updated_count": updated_count}, status=200)


class SaveSubCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = request.POST
        name = (data.get("name") or "").strip()
        category_ids = data.getlist("category_ids")

        if not name or not category_ids:
            return Response({"error": "Name and category_ids are required"}, status=status.HTTP_400_BAD_REQUEST)

        categories = list(Category.objects.filter(category_id__in=category_ids))
        if not categories:
            return Response({"error": "One or more category IDs not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate subcategory name within selected categories
        exists_in_sel = CategorySubCategoryMap.objects.filter(
            category__in=categories, subcategory__name__iexact=name
        ).exists()
        if exists_in_sel:
            return Response(
                {"error": f"Subcategory '{name}' already exists in one or more selected categories."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subcategory_id = generate_subcategory_id(name, category_ids)
        now = timezone.now()
        caption = (data.get("caption") or "").strip() or None
        description = (data.get("description") or "").strip() or None

        subcategory = SubCategory.objects.create(
            subcategory_id=subcategory_id,
            name=name,
            status="visible",
            created_by="SuperAdmin",
            created_at=now,
            updated_at=now,
            caption=caption,
            description=description,
            order=(SubCategory.objects.aggregate(cnt=Count("pk"))["cnt"] or 0) + 1,
        )

        CategorySubCategoryMap.objects.bulk_create(
            [CategorySubCategoryMap(category=c, subcategory=subcategory) for c in categories]
        )

        alt_text = (data.get("alt_text") or data.get("imageAlt") or data.get("altText") or "").strip()
        image_data = request.FILES.get("image") or request.POST.get("image")
        if image_data:
            image = save_image(
                image_data, alt_text or "Alt-text", data.get("tags", ""), "subcategory", "CategorySubCategoryPage", subcategory_id
            )
            if image:
                SubCategoryImage.objects.create(subcategory=subcategory, image=image)

        return Response(
            {"success": True, "subcategory_id": subcategory_id, "caption": caption, "description": description},
            status=status.HTTP_201_CREATED,
        )


class ShowSubCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        imgs = Prefetch("images", queryset=SubCategoryImage.objects.select_related("image"))
        qs = (
            SubCategory.objects
            .prefetch_related(imgs)
            .annotate(products=Count("productsubcategorymap", distinct=True))
            .order_by("order")
        )

        # Prefetch category names for all subs in a single pass
        sub_ids = list(qs.values_list("pk", flat=True))
        cat_names_map = {}
        if sub_ids:
            pairs = (
                CategorySubCategoryMap.objects
                .filter(subcategory_id__in=sub_ids)
                .select_related("category", "subcategory")
                .values("subcategory_id", "category__name")
            )
            for row in pairs:
                cat_names_map.setdefault(row["subcategory_id"], []).append(row["category__name"])

        result = []
        for sub in qs:
            rel = sub.images.first()
            img_obj = rel.image if rel and rel.image_id else None
            img_url = img_obj.url if img_obj else None
            alt_text = img_obj.alt_text if img_obj else ""
            names = cat_names_map.get(sub.pk, [])

            result.append({
                "id": sub.subcategory_id,
                "name": sub.name,
                "image": img_url,
                "imageAlt": alt_text,
                "categories": names or None,
                "products": sub.products or 0,
                "status": sub.status,
                "caption": sub.caption,
                "description": sub.description,
                "order": sub.order,
            })
        return Response(result, status=status.HTTP_200_OK)


class EditSubCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = request.POST
        subcategory_id = data.get("subcategory_id")
        try:
            subcategory = SubCategory.objects.get(subcategory_id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({"error": "SubCategory not found"}, status=status.HTTP_404_NOT_FOUND)

        new_name = (data.get("name") or "").strip()
        if new_name:
            subcategory.name = new_name

        if "caption" in data:
            subcategory.caption = (data.get("caption") or "").strip() or None
        if "description" in data:
            subcategory.description = (data.get("description") or "").strip() or None

        subcategory.updated_at = timezone.now()
        subcategory.save(update_fields=["name", "caption", "description", "updated_at"])

        alt_text = (data.get("alt_text") or data.get("imageAlt") or data.get("altText") or "").strip()
        image_data = request.FILES.get("image") or request.POST.get("image")

        if image_data:
            old_rels = list(SubCategoryImage.objects.filter(subcategory=subcategory).select_related("image"))
            old_images = [rel.image for rel in old_rels if rel.image_id]
            SubCategoryImage.objects.filter(subcategory=subcategory).delete()
            for img in old_images:
                if img and not SubCategoryImage.objects.filter(image=img).exists():
                    if getattr(img, "image_file", None):
                        img.image_file.delete(save=False)
                    img.delete()

            image = save_image(
                image_data, alt_text or "Alt-text", data.get("tags", ""), "subcategory", "CategorySubCategoryPage", subcategory_id
            )
            if image:
                SubCategoryImage.objects.create(subcategory=subcategory, image=image)
        else:
            if alt_text:
                rel = SubCategoryImage.objects.filter(subcategory=subcategory).select_related("image").first()
                if rel and rel.image:
                    rel.image.alt_text = alt_text
                    rel.image.save(update_fields=["alt_text"])

        return Response({"success": True, "message": "SubCategory updated"}, status=status.HTTP_200_OK)


class DeleteSubCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = _safe_json(request)
        subcategory_ids = data.get("ids", [])
        confirm = data.get("confirm", False)

        if not subcategory_ids:
            return Response({"error": "No subcategory IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        for sub_id in set(subcategory_ids):
            try:
                subcat = SubCategory.objects.get(subcategory_id=sub_id)
            except SubCategory.DoesNotExist:
                continue

            related_products = ProductSubCategoryMap.objects.filter(subcategory=subcat)

            if not confirm and related_products.exists():
                return Response(
                    {"confirm": True, "message": f'Deleting subcategory "{sub_id}" will delete all its related products. Continue?'},
                    status=status.HTTP_200_OK,
                )

            for mapping in list(related_products.select_related("product")):
                other_links = ProductSubCategoryMap.objects.filter(product=mapping.product).exclude(subcategory=subcat)
                mapping.delete()
                if not other_links.exists():
                    mapping.product.delete()

            SubCategoryImage.objects.filter(subcategory=subcat).delete()
            CategorySubCategoryMap.objects.filter(subcategory=subcat).delete()
            subcat.delete()

        return Response({"success": True, "message": "Selected subcategories deleted successfully"}, status=status.HTTP_200_OK)


class UpdateSubCategoryOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = _safe_json(request)
        ordered = data.get("ordered_subcategories", [])
        if not isinstance(ordered, list) or not ordered:
            return Response({"success": False, "error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

        order_map = {str(item["id"]): int(item["order"]) for item in ordered if "id" in item and "order" in item}
        objs = list(SubCategory.objects.filter(subcategory_id__in=order_map.keys()))
        for obj in objs:
            obj.order = order_map.get(obj.subcategory_id, obj.order)
        SubCategory.objects.bulk_update(objs, ["order"])
        return Response({"success": True}, status=status.HTTP_200_OK)


class UpdateHiddenStatusAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = _safe_json(request)
        item_type = (data.get("type") or "").strip().lower()
        ids = data.get("ids", [])
        new_status = (data.get("status") or "visible").strip().lower()

        if not ids or not isinstance(ids, list):
            return Response({"error": "No valid IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Accept both singular and plural; normalize to plural
        if item_type in {"category", "categories"}:
            item_type = "categories"
        elif item_type in {"subcategory", "subcategories"}:
            item_type = "subcategories"
        else:
            return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

        if item_type == "categories":
            Category.objects.filter(category_id__in=ids).update(status=new_status)
        else:
            SubCategory.objects.filter(subcategory_id__in=ids).update(status=new_status)

        return Response(
            {"success": True, "message": f"{item_type.title()} status updated to {new_status}"},
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        return Response({"error": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
