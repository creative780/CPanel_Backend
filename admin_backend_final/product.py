# Standard Library
import uuid
import logging
from decimal import Decimal
from collections import defaultdict
from django.db import DatabaseError
from django.db.utils import OperationalError
from typing import Optional
# Django
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError, connection
from django.db.models import Prefetch, Q

# Django REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

# Utilities / Local
from .utilities import (
    _as_list,
    _now,
    _parse_payload,
    _to_decimal,
    format_image_object,
    generate_product_id,
    generate_unique_seo_id,
    generate_unique_slug,
    save_image,
)
from django.utils.text import slugify
from .models import *
from .permissions import FrontendOnlyPermission

logger = logging.getLogger(__name__)

# -----------------------
# Helpers
# -----------------------


# -----------------------
# Save/Update Functions
def save_product_basic(data, is_edit=False, existing_product=None):
    now = _now()
    name = (data.get('name') or '').strip()
    if not name:
        raise IntegrityError("Missing required field: name")

    brand = data.get('brand_title', '')
    price = _to_decimal(data.get('price', 0))
    discounted_price = _to_decimal(data.get('discounted_price', 0))
    tax_rate = _to_decimal(data.get('tax_rate', 0))
    price_calculator = data.get('price_calculator', '')
    video_url = data.get('video_url', '')

    # CHANGED: accept rich HTML exactly as provided (no strip / sanitize)
    description = data.get('description', '')
    if description is None:
        description = ''  # keep non-null
    long_description = data.get('long_description', '')
    if long_description is None:
        long_description = '' 
    status_val = data.get('status', 'active')
    quantity = int(data.get('quantity', 0) or 0)
    low_stock_alert = int(data.get('low_stock_alert', 0) or 0)
    stock_status = data.get('stock_status') or ('In Stock' if quantity > 0 else 'Out Of Stock')
    subcategory_ids = data.get('subcategory_ids', ['DW-DEFAULTSUB-001'])

    def _coerce_rating(val, fallback):
        try:
            v = float(val)
        except (TypeError, ValueError):
            return fallback
        v = max(0.0, min(5.0, round(v * 2) / 2.0))
        return v

    incoming_rating = data.get('rating', None)
    incoming_rating_count = data.get('rating_count', None)

    if is_edit and existing_product:
        product = existing_product
    else:
        existing_map = (
            ProductSubCategoryMap.objects
            .select_related("product", "subcategory")
            .filter(subcategory__subcategory_id=subcategory_ids[0], product__title=name)
            .first()
        )
        if existing_map:
            product = existing_map.product
        else:
            product_id = generate_product_id(name, subcategory_ids[0])
            product = Product(
                product_id=product_id,
                created_by='SuperAdmin',
                created_by_type='admin',
                created_at=now
            )

    # Shared assignment logic
    product.title = name                     
    product.description = description            
    product.long_description = long_description 
    product.brand = brand
    product.price = price
    product.discounted_price = discounted_price
    product.tax_rate = float(tax_rate)
    product.price_calculator = price_calculator
    product.video_url = video_url
    product.status = status_val
    product.updated_at = now

    # Optional ratings
    if incoming_rating is not None:
        product.rating = _coerce_rating(incoming_rating, getattr(product, "rating", 0.0))
    if incoming_rating_count is not None:
        try:
            rc = int(incoming_rating_count)
            product.rating_count = max(0, rc)
        except (TypeError, ValueError):
            pass

    product.save()

    # Inventory Handling (atomic upsert)
    ProductInventory.objects.update_or_create(
        product=product,
        defaults={
            'inventory_id': f"INV-{product.product_id}",
            'stock_quantity': quantity,
            'low_stock_alert': low_stock_alert,
            'stock_status': stock_status,
            'updated_at': now,
        }
    )
    return product

def save_product_seo(data, product):
    now = _now()
    base_seo_id = f"SEO-{product.product_id}"
    unique_seo_id = generate_unique_seo_id(base_seo_id)

    # Generate slug from product title
    product_title = product.title or data.get('name', '')
    base_slug = slugify(product_title) or f"product-{product.product_id}"
    
    seo, _created = ProductSEO.objects.get_or_create(
        product=product,
        defaults={
            "seo_id": unique_seo_id,
            "slug": generate_unique_slug(base_slug, instance=None),
            "meta_keywords": [],
            "created_at": now,
            "updated_at": now,
        }
    )

    # Ensure slug is always set (for existing records that might not have slug)
    if not seo.slug or not seo.slug.strip():
        seo.slug = generate_unique_slug(base_slug, instance=seo)

    def clean_comma_array(value):
        return [v.strip() for v in value.split(",") if v.strip()] if isinstance(value, str) else (value or [])

    seo.image_alt_text = data.get('image_alt_text', '')
    seo.meta_title = data.get('meta_title', '')
    seo.meta_description = data.get('meta_description', '')
    mk = data.get('meta_keywords', [])
    seo.meta_keywords = _as_list(mk)
    seo.open_graph_title = data.get('open_graph_title', '')
    seo.open_graph_desc = data.get('open_graph_desc', '')
    seo.open_graph_image_url = data.get('open_graph_image_url', '')
    seo.canonical_url = data.get('canonical_url', '')
    seo.json_ld = data.get('json_ld', '')

    # Preserved custom fields
    seo.custom_tags = clean_comma_array(data.get('customTags', ''))
    seo.grouped_filters = clean_comma_array(data.get('groupedFilters', ''))

    seo.updated_at = now
    seo.save()

def save_shipping_info(data, product):
    cls = data.get("shippingClass", [])
    shipping_class = ",".join(_as_list(cls)) if isinstance(cls, (list, tuple, set)) else (cls or "")
    ShippingInfo.objects.update_or_create(
        product=product,
        defaults={
            'shipping_id': f"SHIP-{product.product_id}",
            'entered_by_id': 'SuperAdmin',
            'entered_by_type': 'admin',
            'shipping_class': shipping_class,
            'processing_time': data.get("processing_time", ""),
            'created_at': _now(),
        }
    )

def save_product_variants(data, product):
    ProductVariant.objects.filter(product=product).delete()

    sizes = _as_list(data.get("size", []))
    colors = _as_list(data.get("colorVariants", []))
    materials = _as_list(data.get("materialType", []))
    printing_methods = _as_list(data.get("printing_method", []))
    add_ons = _as_list(data.get("addOnOptions", []))
    fabric_finish = (data.get("fabric_finish", "") or "").strip()
    combinations = data.get("variant_combinations", "")

    variant = ProductVariant.objects.create(
        variant_id=f"VAR-{uuid.uuid4().hex[:8].upper()}",
        product=product,
        size=",".join(sizes),
        color=",".join(colors),
        material_type=",".join(materials),
        fabric_finish=fabric_finish,
        printing_methods=printing_methods,
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
    subcategory_ids = data.get('subcategory_ids', []) or []

    ProductSubCategoryMap.objects.filter(product=product).delete()

    if subcategory_ids:
        subs = {
            s.subcategory_id: s
            for s in SubCategory.objects.filter(subcategory_id__in=subcategory_ids)
        }
        seen = set()
        for sub_id in subcategory_ids:
            if sub_id in seen:
                continue
            seen.add(sub_id)
            sub = subs.get(sub_id)
            if sub:
                ProductSubCategoryMap.objects.create(product=product, subcategory=sub)
            else:
                logger.warning("Subcategory not found: %s", sub_id)
                
def save_product_images(data, product):
    """
    Save/Update product images.

    Accepts either:
      - images_with_meta: [
          {
            "dataUrl": "data:image/..",   # OR existing "image_id"
            "image_id": "IMG-..",         # optional if dataUrl is provided (new)
            "url": "https://...",         # ignored for creation; used only to echo back elsewhere
            "alt": "string",
            "caption": "string",          # <-- caption now stored on ProductImage
            "tags": ["a","b"] or "a,b",
            "is_primary": true/false
          }, ...
        ]
      - legacy: images: ["data:image/..", ...]  (+ image_alt_text)
        (this path still works)

    Behavior:
      - If force_replace_images/force_replace is truthy, we wipe existing relations & product-linked images first.
      - If not replacing, we *upsert* relations and update metadata on existing images by id.
      - Only one ProductImage is_primary=True is enforced when any row sets it.
    """
    images_with_meta = data.get("images_with_meta") or []
    legacy_images = data.get("images", []) or []
    force_replace = bool(data.get("force_replace_images") or data.get("force_replace"))

    def _normalize_tags(val):
        if val is None:
            return []
        if isinstance(val, str):
            # support comma/pipe separated strings
            parts = [p.strip() for p in val.replace("|", ",").split(",")]
            return [p for p in parts if p]
        if isinstance(val, (list, tuple, set)):
            return [str(x).strip() for x in val if str(x).strip()]
        return []

    # -- If replacing, clear existing product images (relations + linked Image rows for this product)
    if force_replace:
        try:
            ProductImage.objects.filter(product=product).delete()
            Image.objects.filter(linked_table='product', linked_id=product.product_id).delete()
        except (DatabaseError, IntegrityError):
            logger.exception("Image cleanup DB error")
            raise
        except Exception:
            logger.exception("Non-DB error during image cleanup; continuing")

    # For non-replace updates, pull current relations into memory
    existing_rels_by_imgid = {}
    if not force_replace:
        for rel in ProductImage.objects.filter(product=product).select_related("image"):
            iid = getattr(rel.image, "image_id", None)
            if iid:
                existing_rels_by_imgid[iid] = rel

    made_rels = []                # keep created/ensured ProductImage rels to decide primary later
    requested_primary_imgid = None
    processed_image_ids = set()   # Track which image_ids we've processed

    if images_with_meta:
        for row in images_with_meta:
            # Resolve or create Image
            img_obj = None
            img_id = row.get("image_id")
            data_url = row.get("dataUrl")

            try:
                # Priority 1: If dataUrl provided, create/replace image
                if isinstance(data_url, str) and data_url.startswith("data:image/"):
                    # If image_id is also provided, this is a REPLACEMENT - delete old relation first
                    if img_id:
                        # Delete the old ProductImage relation to prevent duplicates
                        ProductImage.objects.filter(
                            product=product,
                            image__image_id=img_id
                        ).delete()
                    
                    # Create new image from dataUrl
                    tags_list = _normalize_tags(row.get("tags"))
                    img_obj = save_image(
                        data_url,
                        alt_text=row.get("alt") or 'Product image',
                        tags=",".join(tags_list),
                        linked_table='product',
                        linked_page='product-page',
                        linked_id=product.product_id
                    )
                    # NOTE: caption is NOT on Image; it's on ProductImage (relation), updated below.

                # Priority 2: If image_id provided (and no dataUrl), update existing image metadata
                elif img_id:
                    img_obj = Image.objects.filter(pk=img_id).first()
                    if img_obj:
                        # Update metadata on existing Image (only if not force replacing)
                        if not force_replace:
                            dirty = False
                            if "alt" in row and hasattr(img_obj, "alt_text"):
                                new_alt = row.get("alt") or ""
                                if img_obj.alt_text != new_alt:
                                    img_obj.alt_text = new_alt
                                    dirty = True
                            if "tags" in row and hasattr(img_obj, "tags"):
                                new_tags_list = _normalize_tags(row.get("tags"))
                                # Compare tags lists (handles JSONField properly)
                                current_tags_list = _normalize_tags(img_obj.tags) if img_obj.tags else []
                                if set(new_tags_list) != set(current_tags_list):
                                    img_obj.tags = new_tags_list  # Store as list for JSONField
                                    dirty = True
                            if dirty:
                                try:
                                    img_obj.save()
                                except Exception:
                                    fields = []
                                    for f in ("alt_text", "tags"):
                                        if hasattr(img_obj, f):
                                            fields.append(f)
                                    if fields:
                                        img_obj.save(update_fields=fields)
                else:
                    # Neither dataUrl nor image_id => skip this row
                    continue

                if not img_obj:
                    continue

                # Ensure ProductImage relation exists (get or create)
                rel, rel_created = ProductImage.objects.get_or_create(
                    product=product,
                    image=img_obj,
                    defaults={"caption": row.get("caption") or ""}
                )
                
                # Update caption on the relation (always update, not just on create)
                if "caption" in row:
                    new_caption = row.get("caption") or ""
                    if rel.caption != new_caption:
                        rel.caption = new_caption
                        try:
                            rel.save(update_fields=["caption"])
                        except Exception:
                            rel.save()

                made_rels.append(rel)
                
                # Track which image_ids we've processed (for deletion of removed images)
                final_img_id = getattr(img_obj, "image_id", None)
                if final_img_id:
                    processed_image_ids.add(final_img_id)

                # Track requested primary (we enforce after loop)
                if row.get("is_primary") is True:
                    requested_primary_imgid = getattr(img_obj, "image_id", None)

            except (DatabaseError, IntegrityError):
                logger.exception("DB error while saving/linking image; aborting whole save")
                raise
            except Exception:
                logger.exception("Image processing error; skipping this image row")
                continue
    else:
        # Legacy behavior: simple list of data URLs
        for img_data in legacy_images:
            if not isinstance(img_data, str) or not img_data.strip():
                continue
            if not img_data.startswith("data:image/"):
                continue
            try:
                with transaction.atomic():
                    image = save_image(
                        img_data,
                        alt_text=data.get('image_alt_text', 'Product image'),
                        tags='',
                        linked_table='product',
                        linked_page='product-page',
                        linked_id=product.product_id
                    )
                    if image:
                        rel = ProductImage.objects.create(product=product, image=image)
                        made_rels.append(rel)
            except (DatabaseError, IntegrityError):
                logger.exception("DB error while saving an image; aborting whole save")
                raise
            except Exception:
                logger.exception("Image save error (non-DB); skipping this image")
                continue

    # Delete ProductImage relations that are NOT in the payload (images that were removed)
    # Only do this if we're not force replacing (force_replace already deletes everything)
    if not force_replace and images_with_meta:
        try:
            # Get all current ProductImage relations for this product
            all_current_rels = ProductImage.objects.filter(product=product).select_related("image")
            
            # Delete relations whose image_id is not in processed_image_ids
            for rel in all_current_rels:
                img_id = getattr(rel.image, "image_id", None)
                if img_id and img_id not in processed_image_ids:
                    # This image was removed from the frontend, delete the relation
                    rel.delete()
                    logger.info(f"Deleted ProductImage relation for removed image {img_id} on product {product.product_id}")
        except Exception:
            logger.exception("Error deleting removed ProductImage relations; continuing")

    # Enforce a single primary if caller requested one
    if requested_primary_imgid:
        try:
            with transaction.atomic():
                qs = ProductImage.objects.select_for_update().filter(product=product)
                qs.update(is_primary=False)
                target = qs.filter(image__image_id=requested_primary_imgid).first()
                if target:
                    target.is_primary = True
                    target.save(update_fields=["is_primary"])
        except Exception:
            logger.exception("Failed to set requested primary image")

    # If replacing and nothing was explicitly set primary, mark the first created as primary
    if force_replace and not requested_primary_imgid and made_rels:
        try:
            with transaction.atomic():
                qs = ProductImage.objects.select_for_update().filter(product=product)
                qs.update(is_primary=False)
                first_rel = made_rels[0]
                first_rel.is_primary = True
                first_rel.save(update_fields=["is_primary"])
        except Exception:
            logger.exception("Failed to set default primary on replace")

def update_stock_status(inventory):
    quantity = inventory.stock_quantity
    low_stock = inventory.low_stock_alert

    if quantity == 0:
        inventory.stock_status = 'Out Of Stock'
    elif quantity <= low_stock:
        inventory.stock_status = 'Low Stock'
    else:
        inventory.stock_status = 'In Stock'

    inventory.updated_at = _now()
    inventory.save()

def save_product_attributes(data, product):
    """
    Save (replace) product attributes/options safely.

    - If no attributes key is present, do nothing.
    - If present (even empty list), delete existing rows for this product
      and re-create from payload.
    - Do NOT blindly reuse client-supplied IDs. Generate new IDs unless unused.
    - Supports 'description' at attribute (parent) and option levels.
    - Option images: prefer existing image_id; else accept base64 **or HTTP(S) URL**.
    """
    from decimal import Decimal, InvalidOperation

    def _is_http_url(s: str) -> bool:
        s = (s or "").lower()
        return s.startswith("http://") or s.startswith("https://")

    def _is_data_url(s: str) -> bool:
        return isinstance(s, str) and s.startswith("data:image/")

    # Presence check (do nothing if entirely absent)
    has_any_attr_key = any(
        k in data for k in ("attributes", "custom_attributes", "customAttributes")
    )
    if not has_any_attr_key:
        return

    # Normalize incoming list
    attrs = (
        data.get("attributes")
        or data.get("custom_attributes")
        or data.get("customAttributes")
        or []
    )
    if not isinstance(attrs, list):
        attrs = []

    # Enforce single default: only ONE option across ALL attributes can be is_default=True
    found_default = False
    for attr in attrs:
        for opt in attr.get("options") or []:
            if opt.get("is_default"):
                if found_default:
                    # Already have a default, clear this one
                    opt["is_default"] = False
                else:
                    found_default = True

    # Helper: choose a safe, globally-unique attr_id
    def _safe_attr_id(requested, prefix):
        if requested:
            requested = str(requested).strip()
            if requested and not Attribute.objects.filter(attr_id=requested).exists():
                return requested
        import uuid as _uuid
        while True:
            candidate = f"{prefix}-{_uuid.uuid4().hex[:8].upper()}"
            if not Attribute.objects.filter(attr_id=candidate).exists():
                return candidate

    # Replace strategy: wipe current product attributes then reinsert
    Attribute.objects.filter(product=product).delete()

    for idx, att in enumerate(attrs):
        name = (att.get("name") or "").strip()
        if not name:
            continue

        parent_attr_id = _safe_attr_id(att.get("id"), "ATTR")
        parent_description = (att.get("description") or "").strip()

        parent = Attribute.objects.create(
            attr_id=parent_attr_id,
            product=product,
            parent=None,
            name=name,
            description=parent_description,
            order=idx,
        )

        # Options
        for o_idx, opt in enumerate(att.get("options") or []):
            label = (opt.get("label") or "").strip()
            if not label:
                continue

            # Safe option id
            option_attr_id = _safe_attr_id(opt.get("id"), "OPT")

            # Description
            option_description = (opt.get("description") or "").strip()

            # price_delta normalization (Decimal-friendly)
            price_delta = Decimal("0")
            raw_pd = opt.get("price_delta", 0)
            try:
                if raw_pd not in (None, ""):
                    price_delta = (
                        raw_pd if isinstance(raw_pd, Decimal) else Decimal(str(raw_pd))
                    )
            except (InvalidOperation, TypeError, ValueError):
                price_delta = Decimal("0")

            # Resolve image in this order:
            # 1) image_id -> Image row
            # 2) image (base64 OR http url) -> save_image(...)
            # 3) image_url/_image_preview (http url) -> save_image(...)
            img_obj = None
            try:
                image_id = opt.get("image_id")
                if image_id:
                    img_obj = Image.objects.filter(image_id=image_id).first()

                # accept base64 OR http(s) URL in "image"
                img_data = opt.get("image")
                if not img_obj and isinstance(img_data, str) and ( _is_data_url(img_data) or _is_http_url(img_data) ):
                    with transaction.atomic():
                        saved = save_image(
                            img_data,
                            alt_text=f"{name} - {label}",
                            tags="attribute,option",
                            linked_table="product_attribute",
                            linked_page="product-detail",
                            linked_id=parent.attr_id,
                        )
                        if hasattr(saved, "pk"):
                            img_obj = saved
                        elif isinstance(saved, dict) and saved.get("image_id"):
                            img_obj = Image.objects.filter(image_id=saved["image_id"]).first()

                # fallback to explicit image_url or FE preview field
                if not img_obj:
                    img_url = opt.get("image_url") or opt.get("_image_preview")
                    if isinstance(img_url, str) and _is_http_url(img_url):
                        with transaction.atomic():
                            saved = save_image(
                                img_url,
                                alt_text=f"{name} - {label}",
                                tags="attribute,option",
                                linked_table="product_attribute",
                                linked_page="product-detail",
                                linked_id=parent.attr_id,
                            )
                            if hasattr(saved, "pk"):
                                img_obj = saved
                            elif isinstance(saved, dict) and saved.get("image_id"):
                                img_obj = Image.objects.filter(image_id=saved["image_id"]).first()

            except (DatabaseError, IntegrityError):
                logger.exception("DB error while saving attribute image; aborting")
                raise
            except Exception:
                logger.exception("Non-DB error while saving attribute image; skipping image")
                img_obj = None

            # Create option row
            Attribute.objects.create(
                attr_id=option_attr_id,
                product=product,
                parent=parent,
                label=label,
                description=option_description,
                image=img_obj,
                price_delta=price_delta,
                is_default=bool(opt.get("is_default")),
                order=o_idx,
            )

def save_product_cards(data, product):
    """
    Create or update ProductCards for a product.

    Expected payload keys (any optional):
      - card1_title, card1
      - card2_title, card2
      - card3_title, card3

    Optional behavior:
      - If data['sync_long_description'] is truthy, mirror card2 -> product.long_description.
        (Keeps legacy clients happy while long_description remains optional.)
    """
    now = _now()

    cards, _ = ProductCards.objects.get_or_create(product=product, defaults={"created_at": now})

    # Only update fields that are present; blank is allowed (persisted as "")
    def _apply(field):
        if field in data:
            setattr(cards, field, data.get(field) or "")

    _apply("card1_title")
    _apply("card1")
    _apply("card2_title")
    _apply("card2")
    _apply("card3_title")
    _apply("card3")

    cards.updated_at = now
    cards.save()

    # Optional legacy sync: mirror card2 -> Product.long_description
    if data.get("sync_long_description"):
        product.long_description = cards.card2 or ""
        product.updated_at = now
        product.save(update_fields=["long_description", "updated_at"])

    return cards

# -----------------------
# API Views
# -----------------------

class SaveProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        data = _parse_payload(request)

        if not (data.get('name') or '').strip():
            return Response({"error": "Field 'name' is required."}, status=status.HTTP_400_BAD_REQUEST)

        # NOTE: `description` is allowed to be rich HTML; do not strip/sanitize here.
        try:
            with transaction.atomic():
                product = save_product_basic(data)
                save_product_seo(data, product)
                save_shipping_info(data, product)
                save_product_variants(data, product)
                save_product_subcategories(data, product)
                save_product_images(data, product)  # DB errors re-raised
                save_product_attributes(data, product)
                save_product_cards(data, product)
            return Response(
                {"success": True, "product_id": product.product_id},
                status=status.HTTP_200_OK
            )

        except IntegrityError as e:
            logger.exception("SaveProduct IntegrityError (rolled back)")
            return Response(
                {"error": "Integrity error while saving product", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except DatabaseError as e:
            logger.exception("SaveProduct DatabaseError (rolled back)")
            return Response(
                {"error": "Database error while saving product", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.exception("SaveProduct failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def delete(self, request):
        try:
            data = _parse_payload(request)
            ids = data.get('ids', [])
            _ = data.get('confirm', False)

            if not ids:
                return Response({'error': 'No product IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

            products = list(Product.objects.filter(product_id__in=ids))
            deleted_count = 0
            failed_deletes = []
            
            for product in products:
                product_id = product.product_id
                try:
                    VariantCombination.objects.filter(variant__product=product).delete()
                    ProductVariant.objects.filter(product=product).delete()
                    ProductInventory.objects.filter(product=product).delete()
                    ShippingInfo.objects.filter(product=product).delete()
                    ProductSEO.objects.filter(product=product).delete()
                    ProductSubCategoryMap.objects.filter(product=product).delete()
                    ProductImage.objects.filter(product=product).delete()
                    
                    # Delete images using raw SQL to bypass ORM cascade checks for missing BlogImage table
                    # Using raw SQL directly to avoid Django ORM trying to check related BlogImage objects
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "DELETE FROM admin_backend_final_image WHERE linked_table = %s AND linked_id = %s",
                                ['product', product.product_id]
                            )
                            # Verify deletion
                            rows_deleted = cursor.rowcount
                            if rows_deleted > 0:
                                logger.info(f"Deleted {rows_deleted} image(s) for product {product.product_id}")
                    except Exception as sql_error:
                        # If raw SQL fails, log but continue (image might not exist or table might not exist)
                        logger.error(f"Failed to delete images for product {product.product_id}: {sql_error}", exc_info=True)
                    
                    # Delete carousel images that reference this product
                    # FirstCarouselImage and SecondCarouselImage have on_delete=SET_NULL,
                    # but we want to actually delete them to clean up carousels
                    from .models import FirstCarouselImage, SecondCarouselImage
                    FirstCarouselImage.objects.filter(product=product).delete()
                    SecondCarouselImage.objects.filter(product=product).delete()
                    logger.info(f"Cleaned up carousel images for product {product_id}")
                    
                    product.delete()
                    deleted_count += 1
                    logger.info(f"Successfully deleted product {product_id}")
                except Exception as product_error:
                    failed_deletes.append(product_id)
                    logger.error(f"Failed to delete product {product_id}: {product_error}", exc_info=True)
                    # Continue with other products instead of raising
                    continue

            # After loop, verify deletions
            if failed_deletes:
                logger.warning(f"Failed to delete {len(failed_deletes)} product(s): {failed_deletes}")
                return Response({
                    'success': False,
                    'message': f'Deleted {deleted_count} product(s), but {len(failed_deletes)} failed',
                    'deleted_count': deleted_count,
                    'failed_ids': failed_deletes
                }, status=status.HTTP_207_MULTI_STATUS)

            # Verify products are actually deleted
            remaining = Product.objects.filter(product_id__in=ids).count()
            if remaining > 0:
                logger.warning(f"Warning: {remaining} product(s) still exist after deletion attempt")
                return Response({
                    'success': False,
                    'message': f'Deleted {deleted_count} product(s), but {remaining} still exist in database',
                    'deleted_count': deleted_count,
                    'remaining_count': remaining
                }, status=status.HTTP_207_MULTI_STATUS)

            return Response({
                'success': True,
                'message': f'Successfully deleted {deleted_count} product(s)',
                'deleted_count': deleted_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("DeleteProduct failed")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ShowProductsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        # Extract search parameter
        search = request.GET.get('search', '').strip()
        
        # Start with base queryset - exclude test products and hidden/inactive/deleted products
        products_qs = Product.objects.exclude(
            Q(title__in=['fghjd', 'kela', 'amb kela', 'aaa', 'abid ali', 'amb amb kela', 'abid abid ali', 'amb kela kino'])
        ).exclude(
            Q(status__iexact='hidden') | 
            Q(status__iexact='inactive') |
            Q(status__iexact='deleted')  # Safety measure for soft-deleted products
        )
        
        # Apply search filter if provided
        if search:
            products_qs = products_qs.filter(
                Q(title__icontains=search) | 
                Q(product_id__icontains=search) |
                Q(long_description__icontains=search)
            )
        
        # Order the queryset
        products_qs = products_qs.order_by('order')

        # Check if pagination is requested
        page = request.GET.get('page')
        if page:
            paginator = PageNumberPagination()
            paginator.page_size = int(request.GET.get('page_size', 20))
            products_page = paginator.paginate_queryset(products_qs, request)
            products = list(products_page) if products_page is not None else []
            is_paginated = True
        else:
            products = list(products_qs)
            is_paginated = False
        
        if not products:
            response = Response([], status=status.HTTP_200_OK)
            response["Cache-Control"] = "public, max-age=60, stale-while-revalidate=120"
            return response

        # --- images (first/primary) ---
        first_image_by_pk = {}
        for rel in (
            ProductImage.objects
            .filter(product__in=products)
            .select_related('image')
            .order_by('-is_primary', 'id')
        ):
            if rel.product_id not in first_image_by_pk:
                first_image_by_pk[rel.product_id] = rel

        # --- subcategory maps: first AND all ---
        first_submap_by_pk = {}
        all_submaps_by_pk = defaultdict(list)
        for sm in (
            ProductSubCategoryMap.objects
            .filter(product__in=products)
            .select_related('subcategory')
            .order_by('id')
        ):
            if sm.product_id not in first_submap_by_pk:
                first_submap_by_pk[sm.product_id] = sm
            all_submaps_by_pk[sm.product_id].append(sm)

        # --- inventory ---
        inv_by_pk = {}
        for inv in ProductInventory.objects.filter(product__in=products).only(
            'product_id', 'stock_status', 'stock_quantity', 'low_stock_alert'
        ):
            inv_by_pk[inv.product_id] = inv

        # --- variants → printing methods ---
        pm_by_pk = defaultdict(set)
        for v in ProductVariant.objects.filter(product__in=products).only('product_id', 'printing_methods'):
            for m in (v.printing_methods or []):
                pm_by_pk[v.product_id].add(m)

        # --- build payload ---
        out = []
        for p in products:
            # image
            image_rel = first_image_by_pk.get(p.pk)
            img_dict = format_image_object(image_rel, request=request) if image_rel else None
            image_url = img_dict["url"] if img_dict else ""

            # first subcat (legacy)
            submap_first = first_submap_by_pk.get(p.pk)
            subcategory_legacy = {
                "id": getattr(getattr(submap_first, "subcategory", None), "subcategory_id", None),
                "name": getattr(getattr(submap_first, "subcategory", None), "name", None),
            }

            # all subcats (new) — de-dup on id
            subs_all = all_submaps_by_pk.get(p.pk, [])
            seen_ids = set()
            subcategories = []
            for sm in subs_all:
                if getattr(sm, "subcategory", None):
                    sid = sm.subcategory.subcategory_id
                    if sid and sid not in seen_ids:
                        seen_ids.add(sid)
                        subcategories.append({
                            "id": sid,
                            "name": sm.subcategory.name,
                        })

            # inventory
            inv = inv_by_pk.get(p.pk)
            stock_status = getattr(inv, "stock_status", None)
            stock_quantity = getattr(inv, "stock_quantity", None)
            low_stock_alert = getattr(inv, "low_stock_alert", None)

            out.append({
                "id": p.product_id,
                "name": p.title,
                "image": image_url,
                "subcategory": subcategory_legacy,     # kept for compatibility
                "subcategories": subcategories,        # unique list
                "stock_status": stock_status,
                "stock_quantity": stock_quantity,
                "low_stock_alert": low_stock_alert,
                "price": str(p.price),
                "printing_methods": list(pm_by_pk.get(p.pk, set())),
                # NEW
                "rating": float(getattr(p, "rating", 0.0)) if getattr(p, "rating", None) is not None else 0.0,
                "rating_count": int(getattr(p, "rating_count", 0)),
                "long_description": getattr(p, "long_description", ""), 
            })

        if is_paginated:
            return paginator.get_paginated_response(out)

        response = Response(out, status=status.HTTP_200_OK)
        return response

class ShowSpecificProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)
            product_id = data.get('product_id')
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("ShowSpecificProduct lookup failed")
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

        subcategory_map = ProductSubCategoryMap.objects.filter(product=product).select_related('subcategory').first()
        subcategory_data = {
            "id": subcategory_map.subcategory.subcategory_id if subcategory_map else None,
            "name": subcategory_map.subcategory.name if subcategory_map else None
        }

        # CHANGED: expose the HTML as-is via `fit_description` (keeps frontend compatibility)
        response = {
            "id": product.product_id,
            "name": product.title,
            "brand_title": product.brand,
            "price": str(product.price),
            "discounted_price": str(product.discounted_price) if product.discounted_price is not None else None,
            "tax_rate": str(product.tax_rate) if product.tax_rate is not None else None,
            "price_calculator": product.price_calculator,
            "video_url": product.video_url,
            "fit_description": product.description,  # raw HTML round-trips
            "long_description": product.long_description,
            "stock_status": stock_status,
            "stock_quantity": stock_quantity,
            "low_stock_alert": low_stock_alert,
            "subcategory": subcategory_data,
            "rating": float(getattr(product, "rating", 0.0)) if getattr(product, "rating", None) is not None else 0.0,
            "rating_count": int(getattr(product, "rating_count", 0)),
        }

        return Response(response, status=status.HTTP_200_OK)

class ShowProductVariantAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)
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
            logger.exception("ShowProductVariant failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShowProductShippingInfoAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)
            product_id = data.get('product_id')
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            shipping = ShippingInfo.objects.get(product__product_id=product_id)

            data_out = {
                "shipping_class": shipping.shipping_class,
                "processing_time": shipping.processing_time
            }
            return Response(data_out, status=status.HTTP_200_OK)
        except ShippingInfo.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("ShowProductShippingInfo failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShowProductOtherDetailsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)
            product_id = data.get("product_id")
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            product = get_object_or_404(Product, product_id=product_id)

            images = (
                ProductImage.objects
                .filter(product=product)
                .select_related('image')
                .order_by('-is_primary', 'id')
            )

            image_urls = []
            images_with_ids = []
            seen_image_ids = set()
            for rel in images:
                d = format_image_object(rel, request=request)
                if not d:
                    continue
                url = d.get("url")
                img = getattr(rel, "image", None)
                iid = getattr(img, "image_id", None)
                if url and iid and iid not in seen_image_ids:
                    seen_image_ids.add(iid)
                    image_urls.append(url)

                    # read metadata
                    alt_text = getattr(img, "alt_text", "") if img else ""
                    # NEW: caption comes from the ProductImage relation
                    caption = getattr(rel, "caption", "") or ""
                    tags_val = getattr(img, "tags", "") if img else ""
                    # normalize tags to list for FE
                    if isinstance(tags_val, str):
                        norm = [t.strip() for t in tags_val.replace("|", ",").split(",") if t.strip()]
                    elif isinstance(tags_val, (list, tuple, set)):
                        norm = [str(t).strip() for t in tags_val if str(t).strip()]
                    else:
                        norm = []

                    images_with_ids.append({
                        "id": iid,
                        "url": url,
                        "is_primary": bool(rel.is_primary),
                        "alt": alt_text,
                        "caption": caption,   # relation-based caption
                        "tags": norm,
                    })

            subcategory_ids = list(
                ProductSubCategoryMap.objects
                .filter(product=product)
                .values_list('subcategory__subcategory_id', flat=True)
            )
            seen = set()
            subcategory_ids = [sid for sid in subcategory_ids if not (sid in seen or seen.add(sid))]

            return Response({
                "images": image_urls,                 # legacy: list[str]
                "images_with_ids": images_with_ids,   # includes alt/caption/tags
                "subcategory_ids": subcategory_ids
            }, status=status.HTTP_200_OK)

        except Http404:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("ShowProductOtherDetails failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShowProductSEOAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)
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
                "custom_tags": seo.custom_tags,
                "grouped_filters": seo.grouped_filters
            }
            return Response(data_out, status=status.HTTP_200_OK)
        except ProductSEO.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("ShowProductSEO failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShowVariantCombinationsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)
            product_id = data.get("product_id")
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.get(product_id=product_id)

            combos_qs = VariantCombination.objects.filter(
                variant__product=product
            ).values("description", "price_override")

            combos = [
                {"description": c["description"], "price_override": str(c["price_override"])}
                for c in combos_qs
            ]
            return Response({"variant_combinations": combos}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("ShowVariantCombinations failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShowProductAttributesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)
        except Exception:
            return Response({"error": "Invalid JSON body"}, status=status.HTTP_400_BAD_REQUEST)

        product_id = data.get("product_id")
        if not product_id:
            return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

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
            seen_opt_ids = set()
            for opt in p.options.all():
                if opt.attr_id in seen_opt_ids:
                    continue
                seen_opt_ids.add(opt.attr_id)

                # Build URL directly from Image model
                image_id = None
                image_url = None
                img = getattr(opt, "image", None)
                if img:
                    image_id = getattr(img, "image_id", None)
                    try:
                        rel_url = getattr(img, "url", None)  # Image.url @property
                        if rel_url:
                            # Make absolute for the frontend
                            image_url = (
                                request.build_absolute_uri(rel_url)
                                if isinstance(rel_url, str) and rel_url.startswith("/")
                                else rel_url
                            )
                    except Exception:
                        image_url = None

                opts.append({
                    "id": opt.attr_id,
                    "label": opt.label,
                    "description": getattr(opt, "description", "") or "",
                    "image_id": image_id,
                    "image_url": image_url,
                    "price_delta": float(opt.price_delta) if opt.price_delta is not None else 0.0,
                    "is_default": bool(opt.is_default),
                })

            out.append({
                "id": p.attr_id,
                "name": p.name,
                "description": getattr(p, "description", "") or "",
                "options": opts,
            })

        return Response(out, status=status.HTTP_200_OK)

class ShowProductCardAPIView(APIView):
    """
    Return ProductCards (Card 1/2/3 titles + HTML) for a given product.

    Request (JSON):
      { "product_id": "PROD-..." }

    Success (200):
      {
        "card1_title": "...", "card1": "<p>...</p>",
        "card2_title": "...", "card2": "<p>...</p>",
        "card3_title": "...", "card3": "<p>...</p>",
        "updated_at": "2025-10-01T12:34:56Z"
      }

    Not found (404):
      {}
    """
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)
        except Exception:
            return Response({"error": "Invalid JSON body"}, status=status.HTTP_400_BAD_REQUEST)

        product_id = data.get("product_id")
        if not product_id:
            return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Ensure product exists (keeps 404 parity with other endpoints)
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("ShowProductCard product lookup failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            cards = ProductCards.objects.get(product=product)
        except ProductCards.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("ShowProductCard fetch failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "card1_title": cards.card1_title or "",
                "card1": cards.card1 or "",
                "card2_title": cards.card2_title or "",
                "card2": cards.card2 or "",
                "card3_title": cards.card3_title or "",
                "card3": cards.card3 or "",
                "updated_at": cards.updated_at.isoformat() if cards.updated_at else None,
            },
            status=status.HTTP_200_OK,
        )

class SetProductThumbnailAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        try:
            data = _parse_payload(request)
            product_id = data.get("product_id")
            image_id = data.get("image_id")

            if not product_id or not image_id:
                return Response({"error": "Missing product_id or image_id"}, status=status.HTTP_400_BAD_REQUEST)

            product = get_object_or_404(Product, product_id=product_id)
            image = get_object_or_404(Image, pk=image_id)

            rel_qs = ProductImage.objects.select_for_update().filter(product=product)
            if not rel_qs.filter(image=image).exists():
                return Response({"error": "Image does not belong to this product"}, status=status.HTTP_400_BAD_REQUEST)

            rel_qs.update(is_primary=False)
            rel = rel_qs.get(image=image)
            rel.is_primary = True
            rel.save(update_fields=["is_primary"])

            d = format_image_object(rel, request=request)
            thumb_url = d["url"] if d and d.get("url") else None

            return Response({"success": True, "thumbnail_url": thumb_url}, status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "Product or Image not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("SetProductThumbnail failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateProductOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        try:
            data = _parse_payload(request)
            updates = data.get("products", []) or []

            order_map = {item.get("id"): idx for idx, item in enumerate(updates) if item.get("id")}
            if not order_map:
                return Response({"success": True}, status=status.HTTP_200_OK)

            products = list(Product.objects.filter(product_id__in=order_map.keys()))
            for p in products:
                p.order = order_map.get(p.product_id, p.order)
            if products:
                Product.objects.bulk_update(products, ["order"])

            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("UpdateProductOrder failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EditProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = _parse_payload(request)

            product_ids = data.get('product_ids') or []
            if isinstance(product_ids, str):
                product_ids = [product_ids]
            if not product_ids:
                return Response({'error': 'No product_ids provided'}, status=status.HTTP_400_BAD_REQUEST)

            force_replace = bool(data.get('force_replace_images'))
            incoming_images_raw = data.get('images') or []
            incoming_images = [
                s for s in incoming_images_raw
                if isinstance(s, str) and s.startswith('data:image/')
            ]
            has_new_images = len(incoming_images) > 0

            images_with_meta = data.get("images_with_meta") or []  # NEW

            def _coerce_rating(val, fallback):
                try:
                    v = float(val)
                except (TypeError, ValueError):
                    return fallback
                v = max(0.0, min(5.0, round(v * 2) / 2.0))
                return v

            updated_products = []

            # Use context manager for better transaction control
            try:
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

                        # Title is editable if a non-empty name is provided
                        if 'name' in data and (data.get('name') or '').strip():
                            product.title = data.get('name').strip()

                        # Respect rich HTML; do not blank unless explicitly sent non-empty
                        if 'description' in data:
                            desc = data.get('description')
                            if desc is not None and desc != '':
                                product.description = desc
                        if 'long_description' in data:
                            ldesc = data.get('long_description')
                            if ldesc is not None and ldesc != '':
                                product.long_description = ldesc

                        product.brand = data.get('brand_title', product.brand)
                        if 'price' in data:
                            product.price = _to_decimal(data.get('price', product.price))
                        if 'discounted_price' in data:
                            product.discounted_price = _to_decimal(data.get('discounted_price', product.discounted_price))
                        if 'tax_rate' in data:
                            product.tax_rate = float(_to_decimal(data.get('tax_rate', product.tax_rate)))
                        product.price_calculator = data.get('price_calculator', product.price_calculator)
                        product.video_url = data.get('video_url', product.video_url)
                        product.status = data.get('status', product.status)

                        # Optional rating fields
                        if 'rating' in data:
                            product.rating = _coerce_rating(data.get('rating'), getattr(product, "rating", 0.0))
                        if 'rating_count' in data:
                            try:
                                rc = int(data.get('rating_count'))
                                product.rating_count = max(0, rc)
                            except (TypeError, ValueError):
                                pass

                        product.updated_at = _now()
                        product.save()

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

                        # Delegate to existing helpers
                        save_product_seo(data, product)
                        save_shipping_info(data, product)
                        save_product_variants(data, product)
                        save_product_subcategories(data, product)
                        save_product_attributes(data, product)
                        save_product_cards(data, product)
                        # Images:
                        # - If replacing and we have new images (legacy flow), keep supporting that.
                        # - Independently, if images_with_meta is provided, upsert metadata and/or add new images from dataUrls.
                        if (force_replace and has_new_images) or images_with_meta:
                            payload_for_images = {
                                # keep legacy support if caller used images list
                                'images': incoming_images if (force_replace and has_new_images) else [],
                                'image_alt_text': (data.get('image_alt_text') or 'Alt-text').strip(),
                                # NEW preferred structure
                                'images_with_meta': images_with_meta,
                                'force_replace_images': bool(force_replace and has_new_images),
                            }
                            save_product_images(payload_for_images, product)

                        updated_products.append(product.product_id)

                return Response({'success': True, 'updated': updated_products}, status=status.HTTP_200_OK)

            except (IntegrityError, DatabaseError) as e:
                # Transaction is automatically rolled back when exception exits atomic block
                logger.exception("EditProduct database error (rolled back)")
                return Response(
                    {'error': 'Database error while saving product', 'detail': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            # For non-database errors outside the transaction
            logger.exception("EditProduct failed")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _delete_product_full(product):
    """Hard-delete product and all dependent rows (parity with DeleteProductAPIView)."""
    VariantCombination.objects.filter(variant__product=product).delete()
    ProductVariant.objects.filter(product=product).delete()
    ProductInventory.objects.filter(product=product).delete()
    ShippingInfo.objects.filter(product=product).delete()
    ProductSEO.objects.filter(product=product).delete()
    ProductSubCategoryMap.objects.filter(product=product).delete()
    ProductImage.objects.filter(product=product).delete()
    Image.objects.filter(linked_table='product', linked_id=product.product_id).delete()
    product.delete()

class LinkProductToSubcategoriesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        try:
            data = _parse_payload(request)
            product_id = data.get("product_id")
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            sub_ids = data.get("subcategory_ids")
            if not sub_ids:
                single = data.get("subcategory_id")
                if isinstance(single, str):
                    sub_ids = [single]
                elif isinstance(single, list):
                    sub_ids = single
                else:
                    sub_ids = []

            replace = bool(data.get("replace", False))

            product = get_object_or_404(Product, product_id=product_id)

            valid_subs = list(SubCategory.objects.filter(subcategory_id__in=sub_ids))
            found_ids = {s.subcategory_id for s in valid_subs}
            missing_ids = [sid for sid in (sub_ids or []) if sid not in found_ids]

            existing_maps = list(
                ProductSubCategoryMap.objects.select_for_update().filter(product=product)
            )
            existing_ids = {m.subcategory.subcategory_id for m in existing_maps}

            to_add_ids = found_ids - existing_ids
            to_remove_ids = set()
            if replace:
                to_remove_ids = existing_ids - found_ids

            to_add = [ProductSubCategoryMap(product=product, subcategory=s) for s in valid_subs if s.subcategory_id in to_add_ids]
            if to_add:
                ProductSubCategoryMap.objects.bulk_create(to_add, ignore_conflicts=True)

            removed = 0
            if to_remove_ids:
                removed = ProductSubCategoryMap.objects.filter(
                    product=product, subcategory__subcategory_id__in=to_remove_ids
                ).delete()[0]

            current_ids = list(
                ProductSubCategoryMap.objects.filter(product=product)
                .values_list("subcategory__subcategory_id", flat=True)
            )
            seen = set()
            current_ids = [sid for sid in current_ids if not (sid in seen or seen.add(sid))]

            return Response(
                {
                    "success": True,
                    "product_id": product_id,
                    "added": sorted(list(to_add_ids)),
                    "removed": sorted(list(to_remove_ids)) if replace else [],
                    "skipped_missing": sorted(missing_ids),
                    "linked_subcategory_ids": sorted(current_ids),
                },
                status=status.HTTP_200_OK,
            )
        except Http404:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("LinkProductToSubcategories failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnlinkProductFromSubcategoriesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    @transaction.atomic
    def post(self, request):
        try:
            data = _parse_payload(request)
            product_id = data.get("product_id")
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            sub_ids = data.get("subcategory_ids")
            if not sub_ids:
                single = data.get("subcategory_id")
                if isinstance(single, str):
                    sub_ids = [single]
                elif isinstance(single, list):
                    sub_ids = single
                else:
                    return Response({"error": "Provide subcategory_ids to unlink."},
                                    status=status.HTTP_400_BAD_REQUEST)

            product = get_object_or_404(Product, product_id=product_id)

            valid_ids = set(
                SubCategory.objects.filter(subcategory_id__in=sub_ids)
                .values_list("subcategory_id", flat=True)
            )
            skipped_missing = [sid for sid in sub_ids if sid not in valid_ids]

            existing_qs = ProductSubCategoryMap.objects.select_for_update().filter(product=product)
            existing_ids = set(
                existing_qs.values_list("subcategory__subcategory_id", flat=True)
            )

            to_remove_ids = valid_ids & existing_ids
            skipped_not_linked = sorted(list(valid_ids - existing_ids))

            removed_count = 0
            if to_remove_ids:
                removed_count = ProductSubCategoryMap.objects.filter(
                    product=product,
                    subcategory__subcategory_id__in=to_remove_ids
                ).delete()[0]

            remaining_ids = list(
                ProductSubCategoryMap.objects.filter(product=product)
                .values_list("subcategory__subcategory_id", flat=True)
            )
            seen = set()
            remaining_ids = [sid for sid in remaining_ids if not (sid in seen or seen.add(sid))]

            product_deleted = False
            if len(remaining_ids) == 0:
                _delete_product_full(product)
                product_deleted = True

            return Response(
                {
                    "success": True,
                    "product_id": product_id,
                    "removed": sorted(list(to_remove_ids)),
                    "removed_count": int(removed_count),
                    "skipped_missing": sorted(skipped_missing),
                    "skipped_not_linked": skipped_not_linked,
                    "remaining_subcategory_ids": sorted(remaining_ids),
                    "product_deleted": product_deleted,
                },
                status=status.HTTP_200_OK,
            )
        except Http404:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("UnlinkProductFromSubcategories failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)