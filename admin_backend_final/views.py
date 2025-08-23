# Standard Library
import os
import re
import json
import uuid
import base64
import hashlib
import traceback
from io import BytesIO
from collections import defaultdict
from decimal import Decimal
from datetime import datetime

# Third-party
from PIL import Image as PILImage

# Django
from django.http import JsonResponse, Http404, HttpResponseNotAllowed
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError, transaction
from django.db.models import Prefetch, Count

# Django REST Framework
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# Local Imports
from .models import *  # Consider specifying models instead of wildcard import
from .serializers import NotificationSerializer
from .permissions import FrontendOnlyPermission


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def parse_json_body(request):
    """Safe JSON body parser used across endpoints."""
    try:
        return request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
    except Exception:
        return {}

def format_datetime(dt):
    return dt.strftime('%d-%B-%Y-%I:%M%p')

def format_slug(name):
    return slugify(name)

def generate_category_id(name):
    base = ''.join(word[0].upper() for word in name.split())
    similar = Category.objects.filter(category_id__startswith=base).count()
    return f"{base}-{similar + 1}"

def generate_subcategory_id(name, category_ids):
    # Extract base name
    base = name.split()[0].upper()

    # Extract category prefix (e.g., from "CAT-01" -> "CAT")
    category_code = category_ids[0].split('-')[0] if category_ids else "GEN"

    # Build the ID prefix to search
    id_prefix = f"{category_code}-{base}-"

    # Find the highest existing number for this prefix
    existing_ids = SubCategory.objects.filter(subcategory_id__startswith=id_prefix).values_list('subcategory_id', flat=True)

    max_number = 0
    for sid in existing_ids:
        try:
            number_part = int(sid.split('-')[-1])
            if number_part > max_number:
                max_number = number_part
        except (ValueError, IndexError):
            continue

    next_number = max_number + 1

    return f"{category_code}-{base}-{next_number:03d}"

def generate_product_id(name, subcat_id):
    fallback_subcat_prefix = subcat_id[0].upper() if subcat_id else 'X'

    if '-' in subcat_id:
        parts = subcat_id.split('-', 1)
        after_hyphen = parts[1]
        segment = after_hyphen.split('-')[0].upper()
        subcat_prefix = segment[:2] if len(segment) >= 1 else fallback_subcat_prefix
    else:
        subcat_prefix = fallback_subcat_prefix

    first_letters = ''.join(word[0].upper() for word in re.findall(r'\b\w', name))

    base = f"{subcat_prefix}-{first_letters}"

    existing_ids = Product.objects.filter(product_id__startswith=base).values_list('product_id', flat=True)

    numbers = []
    for pid in existing_ids:
        match = re.search(r'(\d{3})$', pid)
        if match:
            numbers.append(int(match.group(1)))

    next_num = 1
    if numbers:
        next_num = max(numbers) + 1

    if next_num > 999:
        raise ValueError("Exceeded maximum 3-digit unique number for this base ID")

    num_str = f"{next_num:03d}"

    return f"{base}-{num_str}"

def generate_inventory_id(product_id):
    return f"INV-{product_id}"

def generate_unique_slug(base_slug, instance=None):
    slug = base_slug
    counter = 1
    while ProductSEO.objects.filter(slug=slug).exclude(product=instance).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

def generate_unique_seo_id(base_id):
    count = 1
    new_id = base_id
    while ProductSEO.objects.filter(seo_id=new_id).exists():
        new_id = f"{base_id}-{count}"
        count += 1
    return new_id

def generate_custom_order_id(user_name, email):
    prefix = 'O'
    uname = user_name[:2].upper() if user_name else "GU"
    email_part = email[:2].upper() if email else "EM"
    base_id = f"{prefix}{uname}-{email_part}-"

    existing_ids = Orders.objects.filter(order_id__startswith=f"{base_id}").values_list('order_id', flat=True)

    existing_suffixes = [
        int(order_id.split("-")[-1]) for order_id in existing_ids
        if order_id.split("-")[-1].isdigit()
    ]
    next_number = max(existing_suffixes, default=0) + 1
    formatted_number = f"{next_number:03}"

    return f"{base_id}{formatted_number}"

def generate_admin_id(name: str, role_name: str, attempt=1) -> str:
    first_name = name.split()[0]
    last_name = name.split()[-1]
    prefix = f"A{first_name[0]}{last_name[-2:]}".upper()
    role_prefix = role_name[:2].upper()
    base_id = f"{prefix}-{role_prefix}"

    existing_ids = Admin.objects.filter(admin_id__startswith=base_id).values_list('admin_id', flat=True)

    used_numbers = set()
    for eid in existing_ids:
        try:
            suffix = eid.replace(base_id, "").strip("-")
            used_numbers.add(int(suffix))
        except:
            continue

    i = 1
    while i in used_numbers:
        i += 1

    return f"{base_id}-{i:03d}"

# Safe image saver (unchanged)
def save_image(file_or_base64, alt_text="Alt-text", tags="", linked_table="", linked_page="", linked_id=""):
    try:
        if isinstance(file_or_base64, str) and file_or_base64.startswith("data:image/"):
            header, encoded = file_or_base64.split(",", 1)
            file_ext = header.split('/')[1].split(';')[0]
            image_data = base64.b64decode(encoded)
            image = PILImage.open(BytesIO(image_data))
            width, height = image.size
            filename = f"{uuid.uuid4()}.{file_ext}"
            content_file = ContentFile(image_data, name=filename)
            image_type = f".{file_ext}"
        else:
            image = PILImage.open(file_or_base64)
            width, height = image.size
            filename = file_or_base64.name
            content_file = file_or_base64
            image_type = os.path.splitext(filename)[-1].lower()

        parsed_tags = [tag.strip() for tag in tags.split(',')] if tags else []

        new_image = Image(
            image_id=f"IMG-{uuid.uuid4().hex[:8]}",
            alt_text=alt_text,
            width=width,
            height=height,
            tags=parsed_tags,
            image_type=image_type,
            linked_table=linked_table,
            linked_page=linked_page,
            linked_id=linked_id,
            created_at=timezone.now()
        )
        new_image.image_file.save(filename, content_file)
        new_image.save()

        return new_image

    except Exception as e:
        print("Image save error:", str(e))
        return None


# ---------------------------------------------------------------------
# API Views (same input/output semantics as your original functions)
# ---------------------------------------------------------------------

class GenerateProductIdAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        data = parse_json_body(request)
        name = data.get('name')
        subcat_id = data.get('subcategory_id')

        if not name or not subcat_id:
            return Response({'error': 'Missing name or subcategory_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_id = generate_product_id(name, subcat_id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'product_id': product_id}, status=status.HTTP_200_OK)

    def get(self, request):
        return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SaveImageAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        """
        Wraps save_image() so frontend can POST either multipart (image file)
        or JSON with base64 data URL in 'image', and optional alt_text, tags, linked_*.
        """
        data = request.data if request.content_type and 'application/json' in request.content_type else request.POST
        files = request.FILES

        image_data = files.get('image') or data.get('image')
        if not image_data:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        alt_text = (data.get('alt_text') or 'Alt-text').strip()
        tags = (data.get('tags') or '')
        linked_table = data.get('linked_table') or ''
        linked_page = data.get('linked_page') or ''
        linked_id = data.get('linked_id') or ''

        img = save_image(
            file_or_base64=image_data,
            alt_text=alt_text,
            tags=tags,
            linked_table=linked_table,
            linked_page=linked_page,
            linked_id=linked_id
        )
        if not img:
            return Response({'error': 'Image save failed'}, status=status.HTTP_400_BAD_REQUEST)

        url = getattr(img, 'url', None) or getattr(img.image_file, 'url', None)

        return Response({
            'success': True,
            'image_id': img.image_id,
            'url': url,
            'alt_text': img.alt_text,
            'width': img.width,
            'height': img.height,
            'image_type': img.image_type
        }, status=status.HTTP_201_CREATED)


class SaveCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        # Keep existing behavior: support both JSON and multipart
        if request.content_type and 'application/json' in request.content_type:
            data = parse_json_body(request)
            files = {}
        else:
            data = request.POST
            files = request.FILES

        name = (data.get('name') or '').strip()
        if not name:
            return Response({'error': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Keep original "replace existing with same name"
        if Category.objects.filter(name=name).exists():
            Category.objects.get(name=name).delete()

        category_id = generate_category_id(name)
        now = timezone.now()
        order = Category.objects.count() + 1

        # optional caption/description
        caption = (data.get('caption') or '').strip() or None
        description = (data.get('description') or '').strip() or None

        category = Category.objects.create(
            category_id=category_id,
            name=name,
            status='visible',
            caption=caption,
            description=description,
            created_by='SuperAdmin',
            created_at=now,
            updated_at=now,
            order=order
        )

        # Normalize alt text & tags
        alt_text = (
            (data.get('alt_text') or data.get('alText') or f"{name} category image")
        ).strip()
        tags = (data.get('tags') or data.get('imageTags') or '')

        # Image can be a file OR a base64 data URL string
        image_data = files.get('image') or data.get('image')

        if image_data:
            img = save_image(
                file_or_base64=image_data,
                alt_text=alt_text,
                tags=tags,
                linked_table="category",
                linked_page="CategorySubCategoryPage",
                linked_id=category_id
            )
            if img:
                CategoryImage.objects.create(category=category, image=img)

        return Response({
            'success': True,
            'category_id': category_id,
            'caption': caption,
            'description': description
        }, status=status.HTTP_201_CREATED)


# ---------- OPTIMIZED ----------
class ShowCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        # 1) Flat categories (values)
        cats = list(
            Category.objects.order_by('order')
            .values('id', 'category_id', 'name', 'status', 'order', 'caption', 'description')
        )
        if not cats:
            return Response([], status=status.HTTP_200_OK)
        cat_ids = [c['id'] for c in cats]

        # 2) First image per category (single scan)
        first_img_by_cat = {}
        for rel in (CategoryImage.objects
                    .filter(category_id__in=cat_ids)
                    .select_related('image')
                    .order_by('category_id', 'id')):
            cid = rel.category_id
            if cid not in first_img_by_cat and rel.image:
                d = format_image_object(rel, request=request)
                if d:
                    first_img_by_cat[cid] = d

        # 3) Category → Subcategories (names + ids)
        cat_to_subids = defaultdict(list)
        cat_to_subnames = defaultdict(list)
        for row in (CategorySubCategoryMap.objects
                    .filter(category_id__in=cat_ids)
                    .select_related('subcategory')
                    .values('category_id', 'subcategory_id', 'subcategory__name')):
            cat_to_subids[row['category_id']].append(row['subcategory_id'])
            cat_to_subnames[row['category_id']].append(row['subcategory__name'])

        # 4) Product counts per subcategory aggregated to category
        sub_ids = {sid for sids in cat_to_subids.values() for sid in sids}
        prod_count_by_sub = {}
        if sub_ids:
            for row in (ProductSubCategoryMap.objects
                        .filter(subcategory_id__in=sub_ids)
                        .values('subcategory_id')
                        .annotate(c=Count('id'))):
                prod_count_by_sub[row['subcategory_id']] = row['c']

        # 5) Assemble output
        out = []
        for c in cats:
            sub_names = cat_to_subnames.get(c['id'], [])
            prod_total = sum(prod_count_by_sub.get(sid, 0) for sid in cat_to_subids.get(c['id'], []))
            img = first_img_by_cat.get(c['id'], {})
            out.append({
                "id": c["category_id"],
                "name": c["name"],
                "image": img.get("url"),
                "imageAlt": img.get("alt_text", ""),
                "subcategories": {"names": sub_names or None, "count": len(sub_names)},
                "products": prod_total,
                "status": c["status"],
                "order": c["order"],
                "caption": c["caption"],
                "description": c["description"],
            })
        return Response(out, status=status.HTTP_200_OK)
# ------------------------------


class EditCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = request.POST
        category_id = data.get('category_id')
        try:
            category = Category.objects.select_related().get(category_id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        # -------- Basic fields --------
        new_name = (data.get('name') or '').strip()
        if new_name:
            category.name = new_name

        if 'caption' in data:
            category.caption = (data.get('caption') or '').strip() or None
        if 'description' in data:
            category.description = (data.get('description') or '').strip() or None

        category.updated_at = timezone.now()
        category.save(update_fields=['name','caption','description','updated_at'])

        # -------- Image handling --------
        alt_text = (
            data.get('alt_text') or
            data.get('imageAlt') or
            data.get('altText') or
            ''
        ).strip()

        image_data = request.FILES.get('image') or request.POST.get('image')

        if image_data:
            # HARD REPLACE: remove old bindings & delete orphaned images/files
            old_rels = CategoryImage.objects.filter(category=category).select_related('image')
            old_images = [rel.image for rel in old_rels if rel.image_id]
            # delete relations first
            CategoryImage.objects.filter(category=category).delete()

            # delete image files/records if no other relation uses them
            for img in old_images:
                if img and not CategoryImage.objects.filter(image=img).exists():
                    if getattr(img, 'image_file', None):
                        img.image_file.delete(save=False)  # delete file from storage
                    img.delete()

            # Save new image and bind
            image = save_image(
                image_data,
                alt_text or "Alt-text",
                data.get("tags", ""),
                "category",
                "CategorySubCategoryPage",
                category_id
            )
            if image:
                CategoryImage.objects.create(category=category, image=image)
        else:
            # No new image => just alt_text update on existing FIRST image
            if alt_text:
                rel = category.images.select_related('image').first()
                if rel and rel.image:
                    rel.image.alt_text = alt_text
                    rel.image.save(update_fields=['alt_text'])

        return Response({'success': True, 'message': 'Category updated'}, status=status.HTTP_200_OK)
    
class DeleteCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
        category_ids = data.get('ids', [])
        confirm = data.get('confirm', False)

        if not category_ids:
            return Response({'error': 'No category IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        for category_id in category_ids:
            try:
                category = Category.objects.get(category_id=category_id)
                related_mappings = CategorySubCategoryMap.objects.filter(category=category)

                if not confirm and related_mappings.exists():
                    return Response({
                        'confirm': True,
                        'message': 'Deleting this category will delete its subcategories and related products. Continue?'
                    }, status=status.HTTP_200_OK)

                for mapping in related_mappings:
                    subcat = mapping.subcategory
                    other_links = CategorySubCategoryMap.objects.filter(subcategory=subcat).exclude(category=category)
                    if not other_links.exists():
                        subcat.delete()
                    mapping.delete()

                category.delete()
            except Category.DoesNotExist:
                continue

        return Response({'success': True, 'message': 'Selected categories deleted'}, status=status.HTTP_200_OK)


# ---------- OPTIMIZED (bulk_update) ----------
class UpdateCategoryOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            ordered = data.get("ordered_categories", [])
            ids = [x["id"] for x in ordered]
            desired = {x["id"]: x["order"] for x in ordered}
            objs = list(Category.objects.filter(category_id__in=ids))
            for o in objs:
                o.order = desired.get(o.category_id, o.order)
            Category.objects.bulk_update(objs, ['order'])
            return Response({'success': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ------------------------------------------------


class SaveSubCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        data = request.POST
        name = (data.get('name') or '').strip()
        category_ids = data.getlist('category_ids')

        if not name or not category_ids:
            return Response({'error': 'Name and category_ids are required'}, status=status.HTTP_400_BAD_REQUEST)

        categories = Category.objects.filter(category_id__in=category_ids)
        if not categories.exists():
            return Response({'error': 'One or more category IDs not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Duplicate subcategory name in same category
        existing_matches = CategorySubCategoryMap.objects.filter(
            category__in=categories,
            subcategory__name__iexact=name
        ).exists()
        if existing_matches:
            return Response({'error': f"Subcategory '{name}' already exists in one or more selected categories."},
                            status=status.HTTP_400_BAD_REQUEST)

        subcategory_id = generate_subcategory_id(name, category_ids)
        now = timezone.now()

        caption = (data.get('caption') or '').strip() or None
        description = (data.get('description') or '').strip() or None

        subcategory = SubCategory.objects.create(
            subcategory_id=subcategory_id,
            name=name,
            status='visible',
            created_by='SuperAdmin',
            created_at=now,
            updated_at=now,
            caption=caption,
            description=description,
            order=SubCategory.objects.count() + 1
        )

        for category in categories:
            CategorySubCategoryMap.objects.create(category=category, subcategory=subcategory)

        # Normalize alt text
        alt_text = (
            data.get('alt_text') or
            data.get('imageAlt') or
            data.get('altText') or
            ''
        ).strip()

        image_data = request.FILES.get('image') or request.POST.get('image')
        if image_data:
            image = save_image(
                image_data,
                alt_text or "Alt-text",
                data.get("tags", ""),
                "subcategory",
                "CategorySubCategoryPage",
                subcategory_id
            )
            if image:
                SubCategoryImage.objects.create(subcategory=subcategory, image=image)

        return Response({
            'success': True,
            'subcategory_id': subcategory_id,
            'caption': caption,
            'description': description
        }, status=status.HTTP_201_CREATED)


# ---------- OPTIMIZED ----------
class ShowSubCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        subs = list(
            SubCategory.objects.order_by('order')
            .values('id', 'subcategory_id', 'name', 'status', 'caption', 'description', 'order')
        )
        if not subs:
            return Response([], status=status.HTTP_200_OK)

        sub_ids = [s['id'] for s in subs]

        # First image per subcategory
        first_img_by_sub = {}
        for rel in (SubCategoryImage.objects
                    .filter(subcategory_id__in=sub_ids)
                    .select_related('image')
                    .order_by('subcategory_id', 'id')):
            sid = rel.subcategory_id
            if sid not in first_img_by_sub and rel.image:
                d = format_image_object(rel, request=request)
                if d:
                    first_img_by_sub[sid] = d

        # Subcategory → Categories
        sub_to_catnames = defaultdict(list)
        for row in (CategorySubCategoryMap.objects
                    .filter(subcategory_id__in=sub_ids)
                    .select_related('category')
                    .values('subcategory_id', 'category__name')):
            sub_to_catnames[row['subcategory_id']].append(row['category__name'])

        # Product count per sub
        prod_count_by_sub = {row['subcategory_id']: row['c'] for row in
                             ProductSubCategoryMap.objects
                             .filter(subcategory_id__in=sub_ids)
                             .values('subcategory_id')
                             .annotate(c=Count('id'))}

        out = []
        for s in subs:
            img = first_img_by_sub.get(s['id'], {})
            out.append({
                "id": s["subcategory_id"],
                "name": s["name"],
                "image": img.get("url"),
                "imageAlt": img.get("alt_text", ""),
                "categories": sub_to_catnames.get(s['id']) or None,
                "products": prod_count_by_sub.get(s['id'], 0),
                "status": s["status"],
                "caption": s["caption"],
                "description": s["description"],
                "order": s["order"],
            })
        return Response(out, status=status.HTTP_200_OK)
# ------------------------------


class EditSubCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        data = request.POST
        subcategory_id = data.get('subcategory_id')
        try:
            subcategory = SubCategory.objects.select_related().get(subcategory_id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({'error': 'SubCategory not found'}, status=status.HTTP_404_NOT_FOUND)

        # -------- Basic fields --------
        new_name = (data.get('name') or '').strip()
        if new_name:
            subcategory.name = new_name

        if 'caption' in data:
            subcategory.caption = (data.get('caption') or '').strip() or None
        if 'description' in data:
            subcategory.description = (data.get('description') or '').strip() or None

        subcategory.updated_at = timezone.now()
        subcategory.save(update_fields=['name','caption','description','updated_at'])

        # -------- Image handling --------
        alt_text = (
            data.get('alt_text') or
            data.get('imageAlt') or
            data.get('altText') or
            ''
        ).strip()

        image_data = request.FILES.get('image') or request.POST.get('image')

        if image_data:
            # HARD REPLACE: remove old bindings & delete orphaned images/files
            old_rels = SubCategoryImage.objects.filter(subcategory=subcategory).select_related('image')
            old_images = [rel.image for rel in old_rels if rel.image_id]
            SubCategoryImage.objects.filter(subcategory=subcategory).delete()

            for img in old_images:
                if img and not SubCategoryImage.objects.filter(image=img).exists():
                    if getattr(img, 'image_file', None):
                        img.image_file.delete(save=False)
                    img.delete()

            # Save new image and bind
            image = save_image(
                image_data,
                alt_text or "Alt-text",
                data.get("tags", ""),
                "subcategory",
                "CategorySubCategoryPage",
                subcategory_id
            )
            if image:
                SubCategoryImage.objects.create(subcategory=subcategory, image=image)
        else:
            # No new image => alt_text update on existing FIRST image
            if alt_text:
                rel = subcategory.images.select_related('image').first()
                if rel and rel.image:
                    rel.image.alt_text = alt_text
                    rel.image.save(update_fields=['alt_text'])

        return Response({'success': True, 'message': 'SubCategory updated'}, status=status.HTTP_200_OK)


class DeleteSubCategoryAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
        subcategory_ids = data.get('ids', [])
        confirm = data.get('confirm', False)

        if not subcategory_ids:
            return Response({'error': 'No subcategory IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            for sub_id in set(subcategory_ids):  # de-duplicate IDs
                print(f"Processing subcategory_id: {sub_id}")

                try:
                    subcat = SubCategory.objects.get(subcategory_id=sub_id)
                except SubCategory.DoesNotExist:
                    print(f"Subcategory {sub_id} not found.")
                    continue

                related_products = ProductSubCategoryMap.objects.filter(subcategory=subcat)

                if not confirm and related_products.exists():
                    return Response({
                        'confirm': True,
                        'message': f'Deleting subcategory "{sub_id}" will delete all its related products. Continue?'
                    }, status=status.HTTP_200_OK)

                for mapping in related_products:
                    try:
                        other_links = ProductSubCategoryMap.objects.filter(product=mapping.product).exclude(subcategory=subcat)
                        if not other_links.exists():
                            mapping.product.delete()
                        mapping.delete()
                    except Exception as e:
                        print(f"Error while deleting mapping or product: {e}")

                # Delete image relationships
                try:
                    SubCategoryImage.objects.filter(subcategory=subcat).delete()
                except Exception as e:
                    print(f"Error deleting SubCategoryImage for {sub_id}: {e}")

                # Remove category-subcategory mapping
                CategorySubCategoryMap.objects.filter(subcategory=subcat).delete()

                # Finally, delete subcategory
                subcat.delete()

            return Response({'success': True, 'message': 'Selected subcategories deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------- OPTIMIZED (bulk_update) ----------
class UpdateSubCategoryOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            ordered = data.get("ordered_subcategories", [])
            ids = [x["id"] for x in ordered]
            desired = {x["id"]: x["order"] for x in ordered}
            objs = list(SubCategory.objects.filter(subcategory_id__in=ids))
            for o in objs:
                o.order = desired.get(o.subcategory_id, o.order)
            SubCategory.objects.bulk_update(objs, ['order'])
            return Response({'success': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ------------------------------------------------


class UpdateHiddenStatusAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = json.loads(request.body)
            item_type = data.get('type')
            ids = data.get('ids', [])
            new_status = data.get('status', 'visible')

            if not ids or not isinstance(ids, list):
                return Response({'error': 'No valid IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

            if item_type == 'categories':
                Category.objects.filter(category_id__in=ids).update(status=new_status)
            elif item_type == 'subcategories':
                SubCategory.objects.filter(subcategory_id__in=ids).update(status=new_status)
            else:
                return Response({'error': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': True, 'message': f"{item_type.title()} status updated to {new_status}"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# ------------------ Product helpers (unchanged) ------------------

def save_product_basic(data, is_edit=False, existing_product=None):
    name = data.get('name')
    brand = data.get('brand_title', '')
    price = float(data.get('price', 0))
    discounted_price = float(data.get('discounted_price', 0))
    tax_rate = float(data.get('tax_rate', 0))
    price_calculator = data.get('price_calculator', '')
    video_url = data.get('video_url', '')
    description = data.get('description', '')
    status_val = data.get('status', 'active')
    quantity = int(data.get('quantity', 0))
    low_stock_alert = int(data.get('low_stock_alert', 0))
    stock_status = data.get('stock_status') or ('In Stock' if quantity > 0 else 'Out of Stock')
    subcategory_ids = data.get('subcategory_ids', ['DW-DEFAULTSUB-001'])

    if is_edit and existing_product:
        product = existing_product
    else:
        # Original "create new" logic
        existing_map = ProductSubCategoryMap.objects.filter(
            subcategory=subcategory_ids[0],
            product__title=name
        ).first()

        if existing_map:
            product = existing_map.product
        else:
            product_id = generate_product_id(name, subcategory_ids[0])
            product = Product(
                product_id=product_id,
                created_by='SuperAdmin',
                created_by_type='admin',
                created_at=timezone.now()
            )

    # Shared assignment logic
    product.title = name
    product.description = description
    product.brand = brand
    product.price = price
    product.discounted_price = discounted_price
    product.tax_rate = tax_rate
    product.price_calculator = price_calculator
    product.video_url = video_url
    product.status = status_val
    product.updated_at = timezone.now()
    product.save()

    # Inventory Handling
    inventory, _ = ProductInventory.objects.get_or_create(product=product, defaults={
        'inventory_id': f"INV-{product.product_id}",
        'stock_quantity': quantity,
        'low_stock_alert': low_stock_alert,
        'stock_status': stock_status,
    })

    inventory.stock_quantity = quantity
    inventory.low_stock_alert = low_stock_alert
    inventory.stock_status = stock_status
    inventory.updated_at = timezone.now()
    inventory.save()

    return product

def save_product_seo(data, product):
    base_seo_id = f"SEO-{product.product_id}"
    unique_seo_id = generate_unique_seo_id(base_seo_id)

    seo, created = ProductSEO.objects.get_or_create(
        product=product,
        defaults={
            "seo_id": unique_seo_id,
            "meta_keywords": [],
            "slug": slugify(product.title),
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
        }
    )

    def clean_comma_array(value):
        return [v.strip() for v in value.split(",") if v.strip()] if isinstance(value, str) else value

    seo.image_alt_text = data.get('image_alt_text', '')
    seo.meta_title = data.get('meta_title', '')
    seo.meta_description = data.get('meta_description', '')
    seo.meta_keywords = data.get('meta_keywords', [])
    seo.open_graph_title = data.get('open_graph_title', '')
    seo.open_graph_desc = data.get('open_graph_desc', '')
    seo.open_graph_image_url = data.get('open_graph_image_url', '')
    seo.canonical_url = data.get('canonical_url', '')
    seo.json_ld = data.get('json_ld', '')

    # ✅ NEW FIELDS
    seo.custom_tags = clean_comma_array(data.get('customTags', ''))
    seo.grouped_filters = clean_comma_array(data.get('groupedFilters', ''))

    try:
        seo.slug = generate_unique_slug(slugify(product.title), instance=product)
    except Exception as e:
        print("Slug generation failed:", e)
        seo.slug = slugify(product.title)

    seo.updated_at = timezone.now()
    seo.save()

def save_shipping_info(data, product):
    shipping = ShippingInfo.objects.filter(product=product).first()
    if not shipping:
        shipping = ShippingInfo(
            shipping_id=f"SHIP-{product.product_id}",
            product=product,
            entered_by_id='SuperAdmin',
            entered_by_type='admin',
            created_at=timezone.now()
        )

    shipping.shipping_class = ",".join(data.get("shippingClass", []))
    shipping.processing_time = data.get("processing_time", "")
    shipping.save()

def save_product_variants(data, product):
    ProductVariant.objects.filter(product=product).delete()

    sizes = data.get("size", [])
    colors = data.get("colorVariants", [])
    materials = data.get("materialType", [])
    printing_methods = data.get("printing_method", "")
    add_ons = data.get("addOnOptions", [])
    fabric_finish = data.get("fabric_finish", "")
    combinations = data.get("variant_combinations", "")

    variant = ProductVariant.objects.create(
        variant_id=f"VAR-{uuid.uuid4().hex[:8].upper()}",
        product=product,
        size=",".join(sizes),
        color=",".join(colors),
        material_type=",".join(materials),
        fabric_finish=fabric_finish,
        printing_methods=[printing_methods] if isinstance(printing_methods, str) else printing_methods,
        add_on_options=add_ons,
    )

    if combinations:
        VariantCombination.objects.create(
            combo_id=f"COMBO-{uuid.uuid4().hex[:8].upper()}",
            variant=variant,
            description=combinations,
            price_override=product.discounted_price
        )

def save_product_subcategories(data, product):
    subcategory_ids = data.get('subcategory_ids', [])

    ProductSubCategoryMap.objects.filter(product=product).delete()
    for sub_id in subcategory_ids:
        try:
            sub = SubCategory.objects.get(subcategory_id=sub_id)
            ProductSubCategoryMap.objects.create(product=product, subcategory=sub)
        except SubCategory.DoesNotExist:
            print("Subcategory not found:", sub_id)

def save_product_images(data, product):
    image_data_list = data.get('images', [])

    # Delete existing images mapped to this product
    ProductImage.objects.filter(product=product).delete()
    Image.objects.filter(linked_table='product', linked_id=product.product_id).delete()

    for img_data in image_data_list:
        try:
            image = save_image(
                img_data,
                alt_text=data.get('image_alt_text', 'Product image'),
                tags='',
                linked_table='product',
                linked_page='product-page',
                linked_id=product.product_id
            )
            if image:
                ProductImage.objects.create(product=product, image=image)
        except Exception as e:
            print("Image save error:", e)

def update_stock_status(inventory):
    quantity = inventory.stock_quantity
    low_stock = inventory.low_stock_alert

    if quantity == 0:
        inventory.stock_status = 'Out Of Stock'
    elif quantity <= low_stock:
        inventory.stock_status = 'Low Stock'
    else:
        inventory.stock_status = 'In Stock'

    inventory.updated_at = timezone.now()
    inventory.save()

def save_product_attributes(data, product):
    # accept any casing; frontend sends `custom_attributes`
    attrs = (
        data.get("attributes")
        or data.get("custom_attributes")
        or data.get("customAttributes")
        or []
    )

    if not isinstance(attrs, list):
        attrs = []

    # wipe & rebuild (keeps UI and DB in sync)
    Attribute.objects.filter(product=product).delete()

    for idx, att in enumerate(attrs):
        name = (att.get("name") or "").strip()
        if not name:
            continue

        parent = Attribute.objects.create(
            attr_id=att.get("id") or f"ATTR-{uuid.uuid4().hex[:8].upper()}",
            product=product,
            parent=None,
            name=name,
            order=idx,
        )

        for o_idx, opt in enumerate(att.get("options") or []):
            label = (opt.get("label") or "").strip()
            if not label:
                continue

            # price
            try:
                price_delta = Decimal(str(opt.get("price_delta") or 0))
            except Exception:
                price_delta = Decimal("0")

            # image
            img_obj = None
            if opt.get("image_id"):
                img_obj = Image.objects.filter(image_id=opt["image_id"]).first()
            if not img_obj and isinstance(opt.get("image"), str) and opt["image"].startswith("data:image/"):
                img_obj = save_image(
                    opt["image"],
                    alt_text=f"{name} - {label}",
                    tags="attribute,option",
                    linked_table="product_attribute",
                    linked_page="product-detail",
                    linked_id=parent.attr_id,
                )

            Attribute.objects.create(
                attr_id=opt.get("id") or f"ATOP-{uuid.uuid4().hex[:8].upper()}",
                product=product,
                parent=parent,
                label=label,
                image=img_obj,
                price_delta=price_delta,
                is_default=bool(opt.get("is_default")),
                order=o_idx,
            )


class SaveProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        if request.method != 'POST':
            return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = parse_json_body(request)
            product = save_product_basic(data)
            save_product_seo(data, product)
            save_shipping_info(data, product)
            save_product_variants(data, product)
            save_product_subcategories(data, product)
            save_product_images(data, product)
            save_product_attributes(data, product)
            return Response({'success': True, 'product_id': product.product_id}, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def delete(self, request):
        if request.method != 'DELETE':
            return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = parse_json_body(request)
            ids = data.get('ids', [])
            confirm = data.get('confirm', False)  # kept for parity

            if not ids:
                return Response({'error': 'No product IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

            for pid in ids:
                product = Product.objects.filter(product_id=pid).first()
                if not product:
                    continue

                ProductInventory.objects.filter(product=product).delete()
                ShippingInfo.objects.filter(product=product).delete()
                ProductSEO.objects.filter(product=product).delete()
                ProductSubCategoryMap.objects.filter(product=product).delete()
                ProductVariant.objects.filter(product=product).delete()
                VariantCombination.objects.filter(variant__product=product).delete()
                Image.objects.filter(linked_table='product', linked_id=product.product_id).delete()
                ProductImage.objects.filter(product=product).delete()
                product.delete()

            return Response({'success': True, 'message': 'Products deleted'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------- OPTIMIZED ----------
class ShowProductsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        prows = list(
            Product.objects.order_by('order')
            .values('id', 'product_id', 'title', 'price')
        )
        if not prows:
            return Response([], status=status.HTTP_200_OK)

        pks = [r['id'] for r in prows]

        # First image per product
        first_img = {}
        for rel in (ProductImage.objects
                    .filter(product_id__in=pks)
                    .select_related('image')
                    .order_by('product_id', 'id')):
            pid = rel.product_id
            if pid not in first_img and rel.image:
                d = format_image_object(rel, request=request)
                if d:
                    first_img[pid] = d["url"]

        # First subcategory per product
        first_sub = {}
        for row in (ProductSubCategoryMap.objects
                    .filter(product_id__in=pks)
                    .select_related('subcategory')
                    .values('product_id', 'subcategory__subcategory_id', 'subcategory__name')):
            if row['product_id'] not in first_sub:
                first_sub[row['product_id']] = {
                    "id": row['subcategory__subcategory_id'],
                    "name": row['subcategory__name']
                }

        # Inventory in one go
        inv = {r['product_id']: r for r in
               ProductInventory.objects.filter(product_id__in=pks)
               .values('product_id', 'stock_status', 'stock_quantity')}

        # Printing methods aggregated
        methods = defaultdict(set)
        for r in (ProductVariant.objects
                  .filter(product_id__in=pks)
                  .values('product_id', 'printing_methods')):
            arr = r['printing_methods']
            if isinstance(arr, str):
                methods[r['product_id']].add(arr)
            elif isinstance(arr, list):
                methods[r['product_id']].update(arr or [])

        out = []
        for r in prows:
            pk = r['id']
            invr = inv.get(pk, {})
            out.append({
                "id": r["product_id"],
                "name": r["title"],
                "image": first_img.get(pk, ""),
                "subcategory": first_sub.get(pk, {"id": None, "name": None}),
                "stock_status": invr.get("stock_status"),
                "stock_quantity": invr.get("stock_quantity"),
                "price": str(r["price"]),
                "printing_methods": sorted(methods.get(pk, set())),
            })
        return Response(out, status=status.HTTP_200_OK)
# ------------------------------


class ShowSpecificProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            product_id = data.get('product_id')
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            inventory = ProductInventory.objects.get(product=product)
            stock_status = inventory.stock_status
            stock_quantity = inventory.stock_quantity
            low_stock_alert = inventory.low_stock_alert
        except ProductInventory.DoesNotExist:
            stock_status = None
            stock_quantity = None
            low_stock_alert = None

        subcategory_map = ProductSubCategoryMap.objects.filter(product=product).first()
        subcategory_data = {
            "id": subcategory_map.subcategory.subcategory_id if subcategory_map else None,
            "name": subcategory_map.subcategory.name if subcategory_map else None
        }

        response = {
            "id": product.product_id,
            "name": product.title,
            "brand_title": product.brand,
            "price": str(product.price),
            "discounted_price": str(product.discounted_price),
            "tax_rate": product.tax_rate,
            "price_calculator": product.price_calculator,
            "video_url": product.video_url,
            "fit_description": product.description,
            "stock_status": stock_status,
            "stock_quantity": stock_quantity,
            "low_stock_alert": low_stock_alert,
            "subcategory": subcategory_data
        }

        return Response(response, status=status.HTTP_200_OK)


class ShowProductVariantAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            product_id = data.get('product_id')
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.get(product_id=product_id)
            variants = ProductVariant.objects.filter(product=product)
            printing_methods = set()
            sizes = set()
            colors = set()
            materials = set()
            fabric_finishes = set()
            add_ons = set()

            for variant in variants:
                printing_methods.update(variant.printing_methods or [])
                sizes.update(variant.size.split(",") if variant.size else [])
                colors.update(variant.color.split(",") if variant.color else [])
                materials.update(variant.material_type.split(",") if variant.material_type else [])
                if variant.fabric_finish:
                    fabric_finishes.add(variant.fabric_finish)
                add_ons.update(variant.add_on_options or [])

            data_out = {
                "printing_methods": list(printing_methods),
                "sizes": list(sizes),
                "color_variants": list(colors),
                "material_types": list(materials),
                "fabric_finish": list(fabric_finishes),
                "add_on_options": list(add_ons)
            }

            return Response(data_out, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------- FIXED LOOKUP ----------
class ShowProductShippingInfoAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            product_id = data.get('product_id')
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            # Fix: resolve by relation to public product_id
            shipping = ShippingInfo.objects.get(product__product_id=product_id)

            data_out = {
                "shipping_class": shipping.shipping_class,
                "processing_time": shipping.processing_time
            }

            return Response(data_out, status=status.HTTP_200_OK)
        except ShippingInfo.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ----------------------------------


class ShowProductOtherDetailsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            product_id = data.get("product_id")
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            # Look up by your SKU-like string field
            product = get_object_or_404(Product, product_id=product_id)

            # Fetch through the relation (not by numeric FK)
            images = ProductImage.objects.filter(product=product).select_related('image')

            image_urls = []
            for rel in images:
                d = format_image_object(rel, request=request)  # consistent with your other view
                if d:
                    image_urls.append(d["url"])  # list[str]

            subcategory_ids = list(
                ProductSubCategoryMap.objects
                .filter(product=product)
                .values_list('subcategory__subcategory_id', flat=True)
            )

            data_out = {
                "images": image_urls,
                "subcategory_ids": subcategory_ids
            }
            return Response(data_out, status=status.HTTP_200_OK)

        except Http404:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShowProductSEOAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            product_id = data.get('product_id')
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            seo = ProductSEO.objects.get(product__product_id=product_id)

            data_out = {
                "meta_title": seo.meta_title,
                "meta_description": seo.meta_description,
                "meta_keywords": seo.meta_keywords,
                "image_alt_text": seo.image_alt_text,
                "open_graph_title": seo.open_graph_title,
                "open_graph_desc": seo.open_graph_desc,
                "open_graph_image_url": seo.open_graph_image_url,
                "canonical_url": seo.canonical_url,
                "json_ld": seo.json_ld,
                "slug": seo.slug,
                "custom_tags": seo.custom_tags,
                "grouped_filters": seo.grouped_filters
            }

            return Response(data_out, status=status.HTTP_200_OK)
        except ProductSEO.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShowVariantCombinationsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            product_id = data.get("product_id")
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.get(product_id=product_id)
            variants = ProductVariant.objects.filter(product=product)

            combos = []
            for variant in variants:
                combinations = VariantCombination.objects.filter(variant=variant)
                for combo in combinations:
                    combos.append({
                        "description": combo.description,
                        "price_override": str(combo.price_override)
                    })

            return Response({"variant_combinations": combos}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShowProductAttributesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        # robust payload parsing
        try:
            data = parse_json_body(request)
        except Exception:
            return Response({"error": "Invalid JSON body"}, status=status.HTTP_400_BAD_REQUEST)

        product_id = data.get("product_id")
        if not product_id:
            return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

        # if your Product uses "product_id" (string SKU), keep this:
        product = get_object_or_404(Product, product_id=product_id)

        parents = (
            Attribute.objects
            .filter(product=product, parent__isnull=True)
            .prefetch_related(
                Prefetch(
                    "options",
                    queryset=Attribute.objects.select_related("image").order_by("order", "label")
                )
            )
            .order_by("order", "name")
        )

        out = []
        for p in parents:
            opts = []
            for opt in p.options.all():
                img_dict = format_image_object(opt.image, request=request) if getattr(opt, "image", None) else None
                opts.append({
                    "id": opt.attr_id,
                    "label": opt.label,
                    "image_id": getattr(opt.image, "image_id", None),
                    "image_url": (img_dict or {}).get("url"),
                    "price_delta": float(opt.price_delta) if opt.price_delta is not None else 0.0,
                    "is_default": bool(opt.is_default),
                })
            out.append({
                "id": p.attr_id,
                "name": p.name,
                "options": opts,
            })

        return Response(out, status=status.HTTP_200_OK)


# ---------- OPTIMIZED (bulk_update) ----------
class UpdateProductOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)
            updates = data.get("products", [])
            ids = [x["id"] for x in updates]
            desired = {x["id"]: idx for idx, x in enumerate(updates)}
            objs = list(Product.objects.filter(product_id__in=ids))
            for o in objs:
                o.order = desired.get(o.product_id, o.order)
            Product.objects.bulk_update(objs, ['order'])
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ------------------------------------------------


class EditProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = parse_json_body(request)

            product_ids = data.get('product_ids') or []
            if isinstance(product_ids, str):
                product_ids = [product_ids]
            if not product_ids:
                return Response({'error': 'No product_ids provided'}, status=status.HTTP_400_BAD_REQUEST)

            force_replace = bool(data.get('force_replace_images'))
            incoming_images_raw = data.get('images') or []
            # Only treat `images` as real replacements if we actually received base64 data URLs
            incoming_images = [
                s for s in incoming_images_raw
                if isinstance(s, str) and s.startswith('data:image/')
            ]
            has_new_images = len(incoming_images) > 0

            updated_products = []

            with transaction.atomic():
                for product_id in product_ids:
                    product = (
                        Product.objects
                        .filter(product_id=product_id)
                        .select_for_update()
                        .first()
                    )
                    if not product:
                        continue

                    # --- basic fields ---
                    product.title = data.get('name', product.title)
                    product.description = data.get('description', product.description)
                    product.brand = data.get('brand_title', product.brand)
                    product.price = float(data.get('price', product.price))
                    product.discounted_price = float(data.get('discounted_price', product.discounted_price))
                    product.tax_rate = float(data.get('tax_rate', product.tax_rate))
                    product.price_calculator = data.get('price_calculator', product.price_calculator)
                    product.video_url = data.get('video_url', product.video_url)
                    product.status = data.get('status', product.status)
                    product.updated_at = timezone.now()
                    product.save()

                    # --- inventory ---
                    inventory, _ = ProductInventory.objects.get_or_create(
                        product=product,
                        defaults={
                            'inventory_id': f"INV-{product.product_id}",
                            'stock_quantity': 0,
                            'low_stock_alert': 0,
                            'stock_status': 'Out Of Stock',
                        }
                    )
                    if 'quantity' in data:
                        inventory.stock_quantity = int(data['quantity'])
                    if 'low_stock_alert' in data:
                        inventory.low_stock_alert = int(data['low_stock_alert'])
                    update_stock_status(inventory)

                    # --- keep parity with CREATE for all “details” ---
                    save_product_seo(data, product)
                    save_shipping_info(data, product)
                    save_product_variants(data, product)
                    save_product_subcategories(data, product)
                    save_product_attributes(data, product)

                    # --- images (replace only when there are new base64s) ---
                    if force_replace and has_new_images:
                        save_product_images(
                            {
                                'images': incoming_images,
                                'image_alt_text': (data.get('image_alt_text') or 'Alt-text').strip(),
                            },
                            product
                        )
                    # else: do nothing → existing gallery stays intact

                    updated_products.append(product.product_id)

            return Response({'success': True, 'updated': updated_products}, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def format_image_object(image_obj, request=None):
    """
    Accepts either:
      - a through-model instance (e.g., CategoryImage/SubCategoryImage/ProductImage) that has .image, or
      - an Image instance directly

    Returns: {"url": <abs_or_rel_url>, "alt_text": <str>} or None
    """
    img = getattr(image_obj, "image", image_obj)  # support through-model or direct Image
    if not img:
        return None

    url = getattr(img, "url", None)  # your Image.url property returns "/media/.."
    if not url:
        return None

    # build absolute URL when request is available (prod-safe; works in dev too)
    if request:
        try:
            url = request.build_absolute_uri(url)
        except Exception:
            # fallback to relative on any edge error
            pass

    return {
        "url": url,
        "alt_text": getattr(img, "alt_text", "") or "Image"
    }


# ---------- OPTIMIZED ----------
class ShowNavItemsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        # Visible categories
        cats = list(
            Category.objects.filter(status="visible")
            .order_by("order")
            .values("id", "category_id", "name")
        )
        if not cats:
            return Response([], status=status.HTTP_200_OK)
        cat_pk = [c["id"] for c in cats]

        # Category images grouped
        cat_imgs = defaultdict(list)
        for rel in (CategoryImage.objects
                    .filter(category_id__in=cat_pk)
                    .select_related('image')
                    .order_by('category_id', 'id')):
            d = format_image_object(rel, request=request)
            if d:
                cat_imgs[rel.category_id].append(d)

        # Category → Subcategories (visible)
        sub_rows = list(
            CategorySubCategoryMap.objects
            .filter(category_id__in=cat_pk, subcategory__status="visible")
            .select_related('subcategory')
            .order_by('subcategory__order')
            .values('category_id', 'subcategory_id', 'subcategory__subcategory_id',
                    'subcategory__name', 'subcategory__id')
        )
        if not sub_rows:
            out = []
            for c in cats:
                out.append({
                    "id": c["category_id"],
                    "name": c["name"],
                    "images": cat_imgs.get(c["id"], []),
                    "url": slugify(c["name"]),
                    "subcategories": []
                })
            return Response(out, status=status.HTTP_200_OK)

        sub_pk = [r['subcategory__id'] for r in sub_rows]

        # Subcategory images grouped
        sub_imgs = defaultdict(list)
        for rel in (SubCategoryImage.objects
                    .filter(subcategory_id__in=sub_pk)
                    .select_related('image')
                    .order_by('subcategory_id', 'id')):
            d = format_image_object(rel, request=request)
            if d:
                sub_imgs[rel.subcategory_id].append(d)

        # Subcategory → Products
        prod_rows = list(
            ProductSubCategoryMap.objects
            .filter(subcategory_id__in=sub_pk)
            .select_related('product')
            .values('subcategory_id', 'product__id', 'product__product_id', 'product__title')
        )
        prod_pk = [r['product__id'] for r in prod_rows]

        # Product images grouped
        prod_imgs = defaultdict(list)
        if prod_pk:
            for rel in (ProductImage.objects
                        .filter(product_id__in=prod_pk)
                        .select_related('image')
                        .order_by('product_id', 'id')):
                d = format_image_object(rel, request=request)
                if d:
                    prod_imgs[rel.product_id].append(d)

        # Build maps
        pk_to_public = {r['subcategory__id']: r['subcategory__subcategory_id'] for r in sub_rows}
        cat_to_subs = defaultdict(list)
        for r in sub_rows:
            sub_internal_pk = r['subcategory__id']
            cat_to_subs[r['category_id']].append({
                "id": r['subcategory__subcategory_id'],
                "name": r['subcategory__name'],
                "images": sub_imgs.get(sub_internal_pk, []),
                "url": slugify(r['subcategory__name']),
                "products": []  # fill below
            })

        # Fast subcategory index by public id
        sub_index = {}
        for subs in cat_to_subs.values():
            for s in subs:
                sub_index[s["id"]] = s

        # Append products
        for r in prod_rows:
            public_sub_id = pk_to_public.get(r['subcategory_id'])
            if not public_sub_id:
                continue
            s = sub_index.get(public_sub_id)
            if not s:
                continue
            s["products"].append({
                "id": r['product__product_id'],
                "name": r['product__title'],
                "images": prod_imgs.get(r['product__id'], []),
                "url": slugify(r['product__title'])
            })

        # Final assemble
        out = []
        for c in cats:
            out.append({
                "id": c["category_id"],
                "name": c["name"],
                "images": cat_imgs.get(c["id"], []),
                "url": slugify(c["name"]),
                "subcategories": cat_to_subs.get(c["id"], [])
            })
        return Response(out, status=status.HTTP_200_OK)
# ------------------------------


class SaveUserAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = json.loads(request.body)

            user_id = data.get('user_id')
            email = data.get('email')
            password = data.get('password', '')
            name = data.get('name', '')
            created_at = timezone.now()

            if not user_id or not email:
                return Response({'error': 'Missing user_id or email'}, status=status.HTTP_400_BAD_REQUEST)

            user, created = User.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'username': email,
                    'email': email,
                    'password_hash': make_password(password) if password else '',
                    'first_name': name or '',
                    'created_at': created_at,
                }
            )

            if not created:
                user.updated_at = timezone.now()
                user.save()

            return Response({'message': 'User saved successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShowUserAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        users = User.objects.all().values('user_id', 'email', 'first_name', 'created_at', 'updated_at')
        return Response({'users': list(users)}, status=status.HTTP_200_OK)


def _build_variant_signature(product_id: str, selected_size, selected_attributes: dict) -> str:
    # stable, hashed signature of the selection
    payload = {
        "product": str(product_id),
        "size": selected_size or "",
        "attrs": {k: selected_attributes[k] for k in sorted((selected_attributes or {}).keys())},
    }
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(s.encode()).hexdigest()


class SaveCartAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def _get_primary_cart(self, device_uuid: str) -> Cart:
        cart = Cart.objects.filter(device_uuid=device_uuid).order_by("-updated_at", "-created_at").first()
        if cart:
            # Optional: merge any accidental duplicates for same device_uuid
            dups = Cart.objects.filter(device_uuid=device_uuid).exclude(pk=cart.pk)
            if dups.exists():
                for dup in dups:
                    CartItem.objects.filter(cart=dup).update(cart=cart)
                    dup.delete()
            return cart
        return Cart.objects.create(cart_id=str(uuid.uuid4()), device_uuid=device_uuid)

    def _compute_attributes_delta_and_details(self, selected_attrs: dict) -> tuple[Decimal, list]:
        """
        selected_attrs looks like { "<parent_attr_id>": "<option_attr_id>", ... }
        Sum price_delta from each option attr and return human details.
        """
        total_delta = Decimal("0.00")
        details = []

        if not isinstance(selected_attrs, dict):
            return total_delta, details

        for parent_id, opt_id in selected_attrs.items():
            opt = Attribute.objects.filter(attr_id=opt_id).select_related("parent").first()
            parent = Attribute.objects.filter(attr_id=parent_id).first() if not (opt and opt.parent and opt.parent.attr_id == parent_id) else opt.parent

            price_delta = Decimal(str(opt.price_delta)) if (opt and opt.price_delta is not None) else Decimal("0.00")
            total_delta += price_delta

            details.append({
                "attribute_id": parent_id,
                "option_id": opt_id,
                "attribute_name": (parent.name if parent else parent_id),
                "option_label": (opt.label if opt else opt_id),
                "price_delta": str(price_delta)
            })

        return total_delta, details

    def post(self, request):
        try:
            data = parse_json_body(request)

            device_uuid = data.get("device_uuid") or request.headers.get("X-Device-UUID")
            if not device_uuid:
                return Response({"error": "Missing device UUID."}, status=status.HTTP_400_BAD_REQUEST)

            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            selected_size = data.get("selected_size") or ""
            selected_attributes = data.get("selected_attributes") or {}

            product = get_object_or_404(Product, product_id=product_id)
            _ = get_object_or_404(ProductInventory, product=product)

            cart = self._get_primary_cart(device_uuid)

            # Compute attribute price delta and human details
            attributes_delta, _human_details = self._compute_attributes_delta_and_details(selected_attributes)

            # Base price (use discounted if given, else normal)
            base_price = Decimal(str(product.discounted_price or product.price or 0))
            unit_price = base_price + attributes_delta

            # Signature ensures "same selection" merges
            sig_parts = [f"size:{selected_size}"] + [
                f"{k}:{v}" for k, v in sorted(selected_attributes.items(), key=lambda x: x[0])
            ]
            variant_signature = "|".join(sig_parts)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant_signature=variant_signature,
                defaults={
                    "item_id": str(uuid.uuid4()),
                    "quantity": quantity,
                    "price_per_unit": unit_price,
                    "subtotal": unit_price * quantity,
                    "selected_size": selected_size,
                    "selected_attributes": selected_attributes,
                    "attributes_price_delta": attributes_delta,
                }
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.price_per_unit = unit_price  # keep latest pricing
                cart_item.attributes_price_delta = attributes_delta
                cart_item.selected_size = selected_size
                cart_item.selected_attributes = selected_attributes
                cart_item.subtotal = unit_price * cart_item.quantity
                cart_item.save()

            return Response({"message": "Cart updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ [SAVE_CART] Error:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ---------- OPTIMIZED ----------
class ShowCartAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def _attr_humanize_batch(self, selected_map, attr_cache):
        """
        selected_map: dict[parent_id -> option_id]
        attr_cache: dict[attr_id -> Attribute (with .parent)]
        """
        details = []
        total_delta = Decimal("0.00")
        if not isinstance(selected_map, dict):
            return details, total_delta
        for parent_id, opt_id in selected_map.items():
            opt = attr_cache.get(opt_id)
            parent = attr_cache.get(parent_id) or (opt.parent if opt and opt.parent and opt.parent.attr_id == parent_id else None)
            price_delta = Decimal(str(getattr(opt, "price_delta", 0) or 0))
            total_delta += price_delta
            details.append({
                "attribute_id": parent_id,
                "option_id": opt_id,
                "attribute_name": (parent.name if parent else parent_id),
                "option_label": (opt.label if opt else opt_id),
                "price_delta": str(price_delta)
            })
        return details, total_delta

    def _respond(self, request, device_uuid):
        if not device_uuid:
            return Response({"error": "Missing device UUID."}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(device_uuid=device_uuid).order_by("-updated_at", "-created_at").first()
        if not cart:
            return Response({"cart_items": []}, status=status.HTTP_200_OK)

        items = list(CartItem.objects.filter(cart=cart).select_related("product"))
        if not items:
            return Response({"cart_items": []}, status=status.HTTP_200_OK)

        # 1) First image per product (linked_table='product') in one query
        prod_ids = {it.product.product_id for it in items}
        first_image_by_pid = {}
        for img in (Image.objects
                    .filter(linked_table='product', linked_id__in=prod_ids)
                    .order_by('linked_id', 'created_at')):
            pid = img.linked_id
            if pid not in first_image_by_pid and getattr(img, "url", None):
                try:
                    first_image_by_pid[pid] = request.build_absolute_uri(img.url)
                except Exception:
                    first_image_by_pid[pid] = img.url

        # 2) Attribute cache for all selected attributes in the cart
        wanted_attr_ids = set()
        for it in items:
            sel = it.selected_attributes or {}
            if isinstance(sel, dict):
                wanted_attr_ids.update(sel.keys())
                wanted_attr_ids.update(sel.values())
        attr_cache = {}
        if wanted_attr_ids:
            for a in Attribute.objects.filter(attr_id__in=wanted_attr_ids).select_related("parent"):
                attr_cache[a.attr_id] = a

        # 3) Build response
        rows = []
        for it in items:
            base_price = Decimal(str(it.product.discounted_price or it.product.price or 0))
            selections, attrs_delta = self._attr_humanize_batch(it.selected_attributes or {}, attr_cache)
            unit_price = base_price + attrs_delta
            line_total = unit_price * it.quantity

            selection_bits = []
            if it.selected_size:
                selection_bits.append(f"Size: {it.selected_size}")
            for d in selections:
                selection_bits.append(f"{d['attribute_name']}: {d['option_label']}")
            parenthetical = f" ({', '.join(selection_bits)})" if selection_bits else ""

            price_parts = [str(base_price)] + [d["price_delta"] for d in selections if d["price_delta"] not in ("0", "0.0", "0.00")]
            if not price_parts:
                price_parts = [str(base_price)]
            breakdown_str = f"{it.quantity} x $(" + " + ".join(price_parts) + f") = ${line_total}"

            rows.append({
                "product_id": it.product.product_id,
                "product_name": it.product.title,
                "product_image": first_image_by_pid.get(it.product.product_id),
                "alt_text": "",  # Image model carries alt if needed
                "quantity": it.quantity,
                "selected_size": it.selected_size or "",
                "selected_attributes": it.selected_attributes or {},
                "selected_attributes_human": selections,
                "price_breakdown": {
                    "base_price": str(base_price),
                    "attributes_delta": str(attrs_delta),
                    "unit_price": str(unit_price),
                    "quantity": it.quantity,
                    "line_total": str(line_total),
                },
                "summary_line": f"{it.product.title}{parenthetical}: {breakdown_str}",
            })
        return Response({"cart_items": rows}, status=status.HTTP_200_OK)

    def get(self, request):
        device_uuid = request.headers.get('X-Device-UUID')
        return self._respond(request, device_uuid)

    def post(self, request):
        device_uuid = request.headers.get('X-Device-UUID')
        if not device_uuid:
            try:
                data = parse_json_body(request)
                device_uuid = data.get("device_uuid")
            except Exception:
                device_uuid = None
        return self._respond(request, device_uuid)
# ------------------------------


class DeleteCartItemAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')   # could be user id or device UUID
            product_id = data.get('product_id')

            if not user_id or not product_id:
                return Response({"error": "user_id and product_id are required."}, status=status.HTTP_400_BAD_REQUEST)

            DjangoUser = get_user_model()
            try:
                user = DjangoUser.objects.get(user_id=user_id)
                cart = Cart.objects.filter(user=user).first()
            except DjangoUser.DoesNotExist:
                cart = Cart.objects.filter(device_uuid=user_id).first()

            if not cart:
                return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

            cart_item = CartItem.objects.filter(cart=cart, product__product_id=product_id).first()
            if not cart_item:
                return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

            cart_item.delete()
            return Response({"message": "Cart item deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class SaveOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]
    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body or "{}")

            user_name = data.get("user_name", "Guest")
            delivery_data = data.get("delivery") or {}
            email = delivery_data.get("email") or None

            order_id = generate_custom_order_id(user_name, email or "")
            order = Orders.objects.create(
                order_id=order_id,
                user_name=user_name,
                order_date=timezone.now(),
                status=data.get("status", "pending"),
                total_price=Decimal(str(data.get("total_price", "0"))),
                notes=data.get("notes", "")
            )

            items = data.get("items") or []
            if not isinstance(items, list) or len(items) == 0:
                return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

            for item in items:
                for field in ["product_id", "quantity", "unit_price", "total_price"]:
                    if field not in item:
                        return Response({"error": f"Missing {field} in item"}, status=status.HTTP_400_BAD_REQUEST)

                product = get_object_or_404(Product, product_id=item["product_id"])

                qty = int(item.get("quantity", 1))
                unit_price = Decimal(str(item.get("unit_price", "0")))
                total_price = Decimal(str(item.get("total_price", "0")))
                attrs_delta = Decimal(str(item.get("attributes_price_delta", 0)))

                # base = unit - delta (unless explicitly provided)
                if item.get("base_price") is not None:
                    base_price = Decimal(str(item["base_price"]))
                else:
                    base_price = unit_price - attrs_delta
                    if base_price < 0:
                        base_price = Decimal("0")

                selected_size = (item.get("selected_size") or "").strip()
                selected_attributes = item.get("selected_attributes") or {}
                selected_attributes_human = item.get("selected_attributes_human") or []
                variant_signature = item.get("variant_signature") or ""

                # store as strings to keep JSON clean/consistent
                price_breakdown = {
                    "base_price": str(base_price),
                    "attributes_delta": str(attrs_delta),
                    "unit_price": str(unit_price),
                    "line_total": str(total_price),
                    "selected_size": selected_size,
                    "selected_attributes_human": selected_attributes_human,
                }

                OrderItem.objects.create(
                    item_id=str(uuid.uuid4()),
                    order=order,
                    product=product,
                    quantity=qty,
                    unit_price=unit_price,
                    total_price=total_price,
                    selected_size=selected_size,
                    selected_attributes=selected_attributes,
                    selected_attributes_human=selected_attributes_human,
                    variant_signature=variant_signature,
                    attributes_price_delta=attrs_delta,
                    price_breakdown=price_breakdown,
                )

            # Normalize instructions to a list
            raw_instructions = delivery_data.get("instructions", [])
            if isinstance(raw_instructions, str):
                instructions = [raw_instructions] if raw_instructions.strip() else []
            elif isinstance(raw_instructions, list):
                instructions = raw_instructions
            else:
                instructions = []

            OrderDelivery.objects.create(
                delivery_id=str(uuid.uuid4()),
                order=order,
                name=delivery_data.get("name", user_name),
                email=email,  # may be None
                phone=delivery_data.get("phone", ""),
                street_address=delivery_data.get("street_address", ""),
                city=delivery_data.get("city", ""),
                zip_code=delivery_data.get("zip_code", ""),
                instructions=instructions,
            )

            return Response({"message": "Order saved successfully", "order_id": order_id}, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({"error": "One or more products not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ---------- OPTIMIZED ----------
class ShowOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        try:
            orders = list(Orders.objects.all().order_by('-created_at'))
            if not orders:
                return Response({"orders": []}, status=status.HTTP_200_OK)

            order_pk = [o.pk for o in orders]

            # Items (with product) in one query
            items = list(
                OrderItem.objects.filter(order_id__in=order_pk)
                .select_related('product', 'order')
            )

            # Deliveries in one query
            deliveries = {
                d.order_id: d for d in OrderDelivery.objects.filter(order_id__in=order_pk)
            }

            # Group items per order
            per_order = defaultdict(list)
            for it in items:
                human = it.selected_attributes_human or []
                tokens = []
                if it.selected_size:
                    tokens.append(f"Size: {it.selected_size}")
                for d in human:
                    tokens.append(f"{d.get('attribute_name','')}: {d.get('option_label','')}")
                selection_str = ", ".join(filter(None, tokens))

                # base/deltas (strings safe)
                try:
                    base = Decimal(it.price_breakdown.get("base_price", it.unit_price))
                except Exception:
                    base = it.unit_price
                deltas = []
                for d in human:
                    try:
                        deltas.append(Decimal(d.get("price_delta", "0") or "0"))
                    except Exception:
                        deltas.append(Decimal("0"))

                per_order[it.order_id].append({
                    "product_id": it.product.product_id,
                    "product_name": it.product.title,
                    "quantity": it.quantity,
                    "unit_price": str(it.unit_price),
                    "total_price": str(it.total_price),
                    "selection": selection_str,
                    "math": {"base": str(base), "deltas": [str(x) for x in deltas]},
                    "variant_signature": it.variant_signature or "",
                })

            # Assemble response
            orders_data = []
            for o in orders:
                d = deliveries.get(o.pk)
                address = {"street": d.street_address, "city": d.city, "zip": d.zip_code} if d else {}
                email = d.email or "" if d else ""
                items_detail = per_order.get(o.pk, [])
                orders_data.append({
                    "orderID": o.order_id,
                    "Date": o.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "UserName": o.user_name,
                    "item": {
                        "count": len(items_detail),
                        "names": [x["product_name"] for x in items_detail],
                        "detail": items_detail,
                    },
                    "total": float(o.total_price),
                    "status": o.status,
                    "Address": address,
                    "email": email,
                    "order_placed_on": o.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            return Response({"orders": orders_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ------------------------------


class EditOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def put(self, request):
        try:
            data = json.loads(request.body or "{}")

            order_id = data.get("order_id")
            if not order_id:
                return Response({"error": "Missing order_id in request body"}, status=status.HTTP_400_BAD_REQUEST)

            order = get_object_or_404(Orders, order_id=order_id)

            # Header
            order.user_name = data.get("user_name", order.user_name)
            order.status = data.get("status", order.status)
            if data.get("total_price") is not None:
                order.total_price = Decimal(str(data["total_price"]))
            order.notes = data.get("notes", order.notes)
            order.save()

            # Rebuild items
            OrderItem.objects.filter(order=order).delete()

            for item in data.get("items", []):
                product = get_object_or_404(Product, product_id=item["product_id"])

                qty = int(item.get("quantity", 1))
                unit_price = Decimal(str(item.get("unit_price", "0")))
                total_price = Decimal(str(item.get("total_price", "0")))
                attrs_delta = Decimal(str(item.get("attributes_price_delta", 0)))

                if item.get("base_price") is not None:
                    base_price = Decimal(str(item["base_price"]))
                else:
                    base_price = unit_price - attrs_delta
                    if base_price < 0:
                        base_price = Decimal("0")

                selected_size = (item.get("selected_size") or "").strip()
                selected_attributes = item.get("selected_attributes") or {}
                selected_attributes_human = item.get("selected_attributes_human") or []
                variant_signature = item.get("variant_signature") or ""

                price_breakdown = {
                    "base_price": str(base_price),
                    "attributes_delta": str(attrs_delta),
                    "unit_price": str(unit_price),
                    "line_total": str(total_price),
                    "selected_size": selected_size,
                    "selected_attributes_human": selected_attributes_human,
                }

                OrderItem.objects.create(
                    item_id=str(uuid.uuid4()),
                    order=order,
                    product=product,
                    quantity=qty,
                    unit_price=unit_price,
                    total_price=total_price,
                    selected_size=selected_size,
                    selected_attributes=selected_attributes,
                    selected_attributes_human=selected_attributes_human,
                    variant_signature=variant_signature,
                    attributes_price_delta=attrs_delta,
                    price_breakdown=price_breakdown,
                )

            # Delivery upsert
            delivery_data = data.get("delivery")
            if delivery_data:
                delivery_obj, _ = OrderDelivery.objects.get_or_create(order=order)

                raw_instructions = delivery_data.get("instructions", [])
                if isinstance(raw_instructions, str):
                    instructions = [raw_instructions] if raw_instructions.strip() else []
                elif isinstance(raw_instructions, list):
                    instructions = raw_instructions
                else:
                    instructions = []

                delivery_obj.name = delivery_data.get("name", delivery_obj.name)
                delivery_obj.email = delivery_data.get("email", delivery_obj.email)
                delivery_obj.phone = delivery_data.get("phone", delivery_obj.phone)
                delivery_obj.street_address = delivery_data.get("street_address", delivery_obj.street_address)
                delivery_obj.city = delivery_data.get("city", delivery_obj.city)
                delivery_obj.zip_code = delivery_data.get("zip_code", delivery_obj.zip_code)
                delivery_obj.instructions = instructions
                delivery_obj.save()

            return Response({"message": "Order updated successfully", "order_id": order_id}, status=status.HTTP_200_OK)

        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
       

# ---------- OPTIMIZED ----------
class ShowAdminAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        try:
            rows = (AdminRoleMap.objects
                    .select_related('admin', 'role')
                    .all())
            result = []
            for m in rows:
                a, r = m.admin, m.role
                result.append({
                    "admin_id": a.admin_id,
                    "admin_name": a.admin_name,
                    "password_hash": a.password_hash,
                    "role_id": r.role_id,
                    "role_name": r.role_name,
                    "access_pages": r.access_pages,
                    "created_at": a.created_at,
                })
            return Response({"success": True, "admins": result}, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ------------------------------


class SaveAdminAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = request.data
            admin_name = data.get("admin_name")
            password = data.get("password")
            role_name = data.get("role_name")
            access_pages = data.get("access_pages", [])

            if not admin_name or not password or not role_name:
                return Response({"success": False, "error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            # store plaintext compat as before
            password_hash = password

            # create or get role
            role, created = AdminRole.objects.get_or_create(
                role_name=role_name,
                defaults={
                    "role_id": f"R-{role_name}",
                    "description": f"{role_name} role",
                    "access_pages": access_pages
                }
            )
            if not created and not role.access_pages:
                role.access_pages = access_pages
                role.save()

            # retry ID collision up to 5 times
            for attempt in range(1, 6):
                try:
                    admin_id = generate_admin_id(admin_name, role_name, attempt)
                    admin = Admin.objects.create(
                        admin_id=admin_id,
                        admin_name=admin_name,
                        password_hash=password_hash
                    )
                    break
                except IntegrityError:
                    if attempt == 5:
                        raise
                    continue

            AdminRoleMap.objects.create(admin=admin, role=role)

            return Response({"success": True, "admin_id": admin_id}, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            return Response({
                "success": False,
                "error": str(e),
                "hint": "Check for admin_id collisions or access_pages misconfig"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteAdminAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            admin_id = request.data.get("admin_id")

            if not admin_id:
                return Response({"success": False, "error": "admin_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            admin = Admin.objects.get(admin_id=admin_id)

            # Delete role mapping first
            AdminRoleMap.objects.filter(admin=admin).delete()
            # Then delete admin
            admin.delete()

            return Response({"success": True, "message": f"Admin '{admin_id}' deleted successfully"}, status=status.HTTP_200_OK)

        except Admin.DoesNotExist:
            return Response({"success": False, "error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            traceback.print_exc()
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminLoginAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            admin_name = request.data.get('username')
            password = request.data.get('password')

            if not admin_name or not password:
                return Response({"success": False, "error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

            admin = Admin.objects.get(admin_name=admin_name)

            # plaintext comparison to keep old behavior
            if admin.password_hash == password:
                role_map = AdminRoleMap.objects.get(admin=admin)
                role = role_map.role
                return Response({
                    "success": True,
                    "admin_id": admin.admin_id,
                    "access_pages": role.access_pages
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        except Admin.DoesNotExist:
            return Response({"success": False, "error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            traceback.print_exc()
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ShowAllImagesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        images = Image.objects.all().order_by('-created_at')
        data = []
        for image in images:
            data.append({
                'image_id': image.image_id,
                'url': image.url,
                'alt_text': image.alt_text,
                'width': image.width,
                'height': image.height,
                'linked_page': image.linked_page,
                'linked_id': image.linked_id,
                'linked_table': image.linked_table,
                'image_type': image.image_type,
                'tags': image.tags,
                'created_at': image.created_at,
            })
        # keep same shape (list)
        return Response(data, status=status.HTTP_200_OK)


class EditImageAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def put(self, request):
        try:
            data = json.loads(request.body)
            image_id = data.get('image_id')
            if not image_id:
                return Response({'error': 'Image ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            image = Image.objects.get(image_id=image_id)

            image.alt_text = data.get('alt_text', image.alt_text)
            image.width = data.get('width', image.width)
            image.height = data.get('height', image.height)
            image.linked_page = data.get('linked_page', image.linked_page)
            image.linked_id = data.get('linked_id', image.linked_id)
            image.linked_table = data.get('linked_table', image.linked_table)
            image.image_type = data.get('image_type', image.image_type)
            image.tags = data.get('tags', image.tags)

            image.save()

            return Response({'message': 'Image updated successfully.'}, status=status.HTTP_200_OK)
        except Image.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteImageAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = json.loads(request.body)
            image_id = data.get('image_id')
            if not image_id:
                return Response({'error': 'Image ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            image = Image.objects.get(image_id=image_id)
            image.delete()

            return Response({'message': 'Image deleted successfully'}, status=status.HTTP_200_OK)
        except Image.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FirstCarouselAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        try:
            carousel = FirstCarousel.objects.last()
            if not carousel:
                return Response({
                    'title': 'Default Title',
                    'description': 'Default Description',
                    'images': [
                        '/uploads/img1.jpg',
                        '/uploads/img2.jpg',
                        '/uploads/img3.jpg',
                    ]
                }, status=status.HTTP_200_OK)

            images = carousel.images.order_by("order").all()
            image_data = [
                {
                    'src': img.image.image_file.url,
                    'title': img.title,
                    'caption': img.caption
                }
                for img in images
            ]

            return Response({
                'title': carousel.title,
                'description': carousel.description,
                'images': image_data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ GET Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            description = data.get('description', '')
            raw_images = data.get('images', [])

            FirstCarousel.objects.all().delete()

            carousel = FirstCarousel.objects.create(
                title=title,
                description=description
            )

            for i, img_data in enumerate(raw_images):
                img_src = img_data.get('src') if isinstance(img_data, dict) else None
                img_title = (img_data.get('title') if isinstance(img_data, dict) else None) or f'Product {i + 1}'
                img_caption = (img_data.get('caption') if isinstance(img_data, dict) else None) or 'Catchy tagline'

                if isinstance(img_src, str) and img_src.startswith('/uploads/'):
                    existing_image = Image.objects.filter(
                        image_file=img_src.replace('/uploads/', 'uploads/')
                    ).first()
                    if existing_image:
                        FirstCarouselImage.objects.create(
                            carousel=carousel,
                            image=existing_image,
                            title=img_title,
                            caption=img_caption,
                            order=i
                        )
                    continue

                saved_image = save_image(
                    file_or_base64=img_src,
                    alt_text="Carousel Image",
                    tags="carousel",
                    linked_table="FirstCarousel",
                    linked_id=str(carousel.id),
                    linked_page="first-carousel"
                )
                if saved_image:
                    FirstCarouselImage.objects.create(
                        carousel=carousel,
                        image=saved_image,
                        title=img_title,
                        caption=img_caption,
                        order=i
                    )

            return Response({'message': '✅ First Carousel data saved successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ POST Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SecondCarouselAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        try:
            carousel = SecondCarousel.objects.last()
            if not carousel:
                return Response({
                    'title': 'Default Title',
                    'description': 'Default Description',
                    'images': [
                        '/uploads/img1.jpg',
                        '/uploads/img2.jpg',
                        '/uploads/img3.jpg',
                    ]
                }, status=status.HTTP_200_OK)

            images = carousel.images.order_by("order").all()
            image_data = [
                {
                    'src': img.image.image_file.url,
                    'title': img.title,
                    'caption': img.caption
                }
                for img in images
            ]

            return Response({
                'title': carousel.title,
                'description': carousel.description,
                'images': image_data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ GET Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            description = data.get('description', '')
            raw_images = data.get('images', [])

            SecondCarousel.objects.all().delete()

            carousel = SecondCarousel.objects.create(
                title=title,
                description=description
            )

            for i, img_data in enumerate(raw_images):
                img_src = img_data.get('src') if isinstance(img_data, dict) else None
                img_title = (img_data.get('title') if isinstance(img_data, dict) else None) or f'Product {i + 1}'
                img_caption = (img_data.get('caption') if isinstance(img_data, dict) else None) or 'Catchy tagline'

                if isinstance(img_src, str) and img_src.startswith('/uploads/'):
                    existing_image = Image.objects.filter(
                        image_file=img_src.replace('/uploads/', 'uploads/')
                    ).first()
                    if existing_image:
                        SecondCarouselImage.objects.create(
                            carousel=carousel,
                            image=existing_image,
                            title=img_title,
                            caption=img_caption,
                            order=i
                        )
                    continue

                saved_image = save_image(
                    file_or_base64=img_src,
                    alt_text="Carousel Image",
                    tags="carousel",
                    linked_table="Second Carousel",
                    linked_id=str(carousel.id),
                    linked_page="second-carousel"
                )
                if saved_image:
                    SecondCarouselImage.objects.create(
                        carousel=carousel,
                        image=saved_image,
                        title=img_title,
                        caption=img_caption,
                        order=i
                    )

            return Response({'message': '✅ Second Carousel data saved successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ POST Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HeroBannerAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        try:
            hero = HeroBanner.objects.last()
            if not hero:
                return Response({
                    'images': [
                        {
                            "url": f'{request.scheme}://{request.get_host()}/uploads/desktop_default.jpg',
                            "device_type": "desktop"
                        },
                        {
                            "url": f'{request.scheme}://{request.get_host()}/uploads/mobile_default.jpg',
                            "device_type": "mobile"
                        },
                    ]
                }, status=status.HTTP_200_OK)

            images = hero.images.order_by('order').all()
            image_urls = [
                {
                    "url": request.build_absolute_uri(img.image.image_file.url),
                    "device_type": img.device_type
                }
                for img in images
            ]

            return Response({'images': image_urls}, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ HeroBanner GET Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = json.loads(request.body)
            raw_images = data.get('images', [])

            if not raw_images or len(raw_images) < 2:
                return Response({'error': 'At least two images required (1 desktop & 1 mobile)'}, status=status.HTTP_400_BAD_REQUEST)

            desktop_imgs = []
            mobile_imgs = []

            # detect if device_type provided
            has_device_labels = any(isinstance(img, dict) and 'device_type' in img for img in raw_images)

            if has_device_labels:
                for img in raw_images:
                    if isinstance(img, dict):
                        device_type = img.get('device_type', '').lower()
                        url = img.get('url', '')
                        if device_type == 'desktop':
                            desktop_imgs.append(url)
                        elif device_type == 'mobile':
                            mobile_imgs.append(url)
            else:
                midpoint = len(raw_images) // 2
                desktop_imgs = [img['url'] if isinstance(img, dict) else img for img in raw_images[:midpoint]]
                mobile_imgs = [img['url'] if isinstance(img, dict) else img for img in raw_images[midpoint:]]

            if not desktop_imgs or not mobile_imgs:
                return Response({'error': 'Must include at least one desktop and one mobile image'}, status=status.HTTP_400_BAD_REQUEST)

            # clear previous
            HeroBanner.objects.all().delete()

            banner = HeroBanner.objects.create(
                hero_id=f"HERO-{uuid.uuid4().hex[:8]}",
                alt_text="Homepage Hero Banner"
            )

            def process_images(image_list, device_type, order_start):
                order = order_start
                for img_url in image_list:
                    if isinstance(img_url, str) and img_url.startswith('/uploads/'):
                        existing = Image.objects.filter(image_file=img_url.replace('/uploads/', 'uploads/')).first()
                        if existing:
                            HeroBannerImage.objects.create(
                                banner=banner,
                                image=existing,
                                device_type=device_type,
                                order=order
                            )
                            order += 1
                            continue

                    saved_image = save_image(
                        file_or_base64=img_url,
                        alt_text=f"Hero {device_type.title()} Image",
                        tags=f"hero,{device_type}",
                        linked_table="HeroBanner",
                        linked_id=str(banner.hero_id),
                        linked_page="hero-banner"
                    )
                    if saved_image:
                        HeroBannerImage.objects.create(
                            banner=banner,
                            image=saved_image,
                            device_type=device_type,
                            order=order
                        )
                        order += 1
                return order

            order = 0
            order = process_images(desktop_imgs, 'desktop', order)
            order = process_images(mobile_imgs, 'mobile', order)

            return Response({'message': '✅ Hero Banner images saved successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ HeroBanner POST Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@api_view(['GET'])
@permission_classes([FrontendOnlyPermission])
def get_notifications(request):
    notifications = Notification.objects.order_by('-created_at')[:1000]
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([FrontendOnlyPermission])
def update_notification_status(request):
    notification_id = request.data.get("notification_id")
    new_status = request.data.get("status")
    if not notification_id or new_status not in ["read", "unread"]:
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        notification = Notification.objects.get(notification_id=notification_id)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
    notification.status = new_status
    notification.save()
    return Response({"message": "Status updated"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([FrontendOnlyPermission])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_image(request, image_id):
    try:
        image = Image.objects.get(image_id=image_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

    uploaded = request.FILES.get('image_file')
    if uploaded:
        image.image_file = uploaded

    alt_text = request.data.get('alt_text', None)
    if alt_text is not None:
        image.alt_text = alt_text

    tags_raw = request.data.get('tags', None)
    if tags_raw is not None:
        if isinstance(tags_raw, list):
            image.tags = tags_raw
        elif isinstance(tags_raw, str):
            try:
                image.tags = json.loads(tags_raw)
            except json.JSONDecodeError:
                cleaned = [t.strip() for t in tags_raw.split(',') if t.strip()]
                image.tags = cleaned

    image.save()

    return Response({
        'message': 'Image updated successfully',
        'url': image.url,
        'image_id': image.image_id,
        'alt_text': image.alt_text,
        'tags': image.tags,
    }, status=status.HTTP_200_OK)


@csrf_exempt
def save_blog(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            blog_id = str(uuid.uuid4())
            blog = Blog.objects.create(
                blog_id=blog_id,
                title=data.get("title", ""),
                content=data.get("content", ""),
                blog_image=data.get("blog_image", ""),
                schedule_date=data.get("schedule_date", timezone.now()),
                status=data.get("status", "draft"),
                author_id=data.get("author_id", ""),
                author_type=data.get("author_type", "admin"),
            )

            category_ids = data.get("category_ids", [])
            for cat_id in category_ids:
                BlogCategoryMap.objects.create(blog=blog, category_id=cat_id)

            # Save SEO
            BlogSEO.objects.create(
                blog=blog,
                meta_title=data.get("meta_title", ""),
                meta_description=data.get("meta_description", ""),
                og_title=data.get("og_title", ""),
                og_image=data.get("og_image", ""),
                tags=data.get("tags", ""),
                schema_enabled=data.get("schema_enabled", False),
            )

            return JsonResponse({"message": "Blog saved successfully", "blog_id": blog_id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def edit_blog(request, blog_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            blog = Blog.objects.get(blog_id=blog_id)

            blog.title = data.get("title", blog.title)
            blog.content = data.get("content", blog.content)
            blog.blog_image = data.get("blog_image", blog.blog_image)
            blog.schedule_date = data.get("schedule_date", blog.schedule_date)
            blog.status = data.get("status", blog.status)
            blog.updated_at = timezone.now()
            blog.save()

            BlogCategoryMap.objects.filter(blog=blog).delete()
            for cat_id in data.get("category_ids", []):
                BlogCategoryMap.objects.create(blog=blog, category_id=cat_id)

            # Update or create SEO
            seo_data = {
                "meta_title": data.get("meta_title", ""),
                "meta_description": data.get("meta_description", ""),
                "og_title": data.get("og_title", ""),
                "og_image": data.get("og_image", ""),
                "tags": data.get("tags", ""),
                "schema_enabled": data.get("schema_enabled", False),
            }
            BlogSEO.objects.update_or_create(blog=blog, defaults=seo_data)

            return JsonResponse({"message": "Blog updated successfully"}, status=200)
        except Blog.DoesNotExist:
            return JsonResponse({"error": "Blog not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# ---------- OPTIMIZED ----------
def show_blogs(request):
    if request.method == "GET":
        blogs = list(Blog.objects.all().order_by("-created_at"))
        if not blogs:
            return JsonResponse({"blogs": []}, status=200)

        blog_ids = [b.pk for b in blogs]
        catnames_by_blog = defaultdict(list)
        for m in (BlogCategoryMap.objects
                  .filter(blog_id__in=blog_ids)
                  .select_related("category")):
            if m.category:
                catnames_by_blog[m.blog_id].append(m.category.name)

        blog_list = []
        for b in blogs:
            blog_list.append({
                "blog_id": b.blog_id,
                "title": b.title,
                "content": b.content,
                "blog_image": b.blog_image,
                "schedule_date": b.schedule_date,
                "status": b.status,
                "author_id": b.author_id,
                "author_type": b.author_type,
                "created_at": b.created_at,
                "updated_at": b.updated_at,
                "categories": catnames_by_blog.get(b.pk, [])
            })

        return JsonResponse({"blogs": blog_list}, status=200)
# ------------------------------
