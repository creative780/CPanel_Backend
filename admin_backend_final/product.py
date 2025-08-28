# Standard Library
import json
import uuid
import logging
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from django.db import DatabaseError
# Django
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.db import transaction, IntegrityError
from django.db.models import Prefetch

# Django REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Utilities / Local
from .utilities import (
    format_image_object,
    generate_product_id,
    generate_unique_seo_id,
    generate_unique_slug,
    save_image,
)
from .models import *  # keeping wildcard to avoid interface changes
from .permissions import FrontendOnlyPermission

logger = logging.getLogger(__name__)

# -----------------------
# Helpers
# -----------------------
def _parse_payload(request):
    """Consistent, tolerant request payload parsing."""
    if isinstance(request.data, dict):
        return request.data
    try:
        body = request.body.decode("utf-8") if request.body else "{}"
        return json.loads(body or "{}")
    except Exception:
        return {}

def _now():
    return timezone.now()

def _to_decimal(val, default="0"):
    try:
        return Decimal(str(val))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)

def _as_list(val):
    """Coerce incoming field to list[str] safely."""
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x) for x in val if str(x).strip()]
    if isinstance(val, str):
        return [v.strip() for v in val.split(",") if v.strip()]
    return []

# -----------------------
# Save/Update Functions
# -----------------------
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
    description = data.get('description', '')
    status_val = data.get('status', 'active')
    quantity = int(data.get('quantity', 0) or 0)
    low_stock_alert = int(data.get('low_stock_alert', 0) or 0)
    stock_status = data.get('stock_status') or ('In Stock' if quantity > 0 else 'Out Of Stock')
    subcategory_ids = data.get('subcategory_ids', ['DW-DEFAULTSUB-001'])

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
    product.brand = brand
    product.price = price
    product.discounted_price = discounted_price
    product.tax_rate = float(tax_rate)
    product.price_calculator = price_calculator
    product.video_url = video_url
    product.status = status_val
    product.updated_at = now
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

    seo, _created = ProductSEO.objects.get_or_create(
        product=product,
        defaults={
            "seo_id": unique_seo_id,
            "meta_keywords": [],
            "slug": slugify(product.title) or product.product_id.lower(),
            "created_at": now,
            "updated_at": now,
        }
    )

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

    try:
        desired_slug = slugify(product.title) or product.product_id.lower()
        seo.slug = generate_unique_slug(desired_slug, instance=product)
    except Exception:
        logger.exception("Slug generation failed")
        seo.slug = slugify(product.title) or product.product_id.lower()

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
    Robust image save:
      - Never swallow DatabaseError/IntegrityError (re-raise to rollback atomic block)
      - Tolerate non-DB per-image errors and continue
    """
    image_data_list = data.get('images', []) or []

    # Delete existing images mapped to this product
    try:
        ProductImage.objects.filter(product=product).delete()
        Image.objects.filter(linked_table='product', linked_id=product.product_id).delete()
    except (DatabaseError, IntegrityError):
        logger.exception("Image cleanup DB error")
        raise
    except Exception:
        logger.exception("Non-DB error during image cleanup; continuing")

    for img_data in image_data_list:
        if not isinstance(img_data, str) or not img_data.strip():
            continue
        try:
            # Per-image savepoint: tolerate non-DB failures without poisoning the outer atomic
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
                    ProductImage.objects.create(product=product, image=image)
        except (DatabaseError, IntegrityError):
            logger.exception("DB error while saving an image; aborting whole save")
            raise
        except Exception:
            logger.exception("Image save error (non-DB); skipping this image")

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
    attrs = (
        data.get("attributes")
        or data.get("custom_attributes")
        or data.get("customAttributes")
        or []
    )
    if not isinstance(attrs, list):
        attrs = []

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

            try:
                price_delta = _to_decimal(opt.get("price_delta", 0))
            except Exception:
                price_delta = Decimal("0")

            img_obj = None
            try:
                if opt.get("image_id"):
                    img_obj = Image.objects.filter(image_id=opt["image_id"]).first()
                if not img_obj and isinstance(opt.get("image"), str) and opt["image"].startswith("data:image/"):
                    with transaction.atomic():
                        img_obj = save_image(
                            opt["image"],
                            alt_text=f"{name} - {label}",
                            tags="attribute,option",
                            linked_table="product_attribute",
                            linked_page="product-detail",
                            linked_id=parent.attr_id,
                        )
            except (DatabaseError, IntegrityError):
                logger.exception("DB error while saving attribute image; aborting")
                raise
            except Exception:
                logger.exception("Non-DB error while saving attribute image; skipping image")

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

# -----------------------
# API Views
# -----------------------

class SaveProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        data = _parse_payload(request)

        if not (data.get('name') or '').strip():
            return Response({"error": "Field 'name' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                product = save_product_basic(data)
                save_product_seo(data, product)
                save_shipping_info(data, product)
                save_product_variants(data, product)
                save_product_subcategories(data, product)
                save_product_images(data, product)  # DB errors re-raised
                save_product_attributes(data, product)

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
            for product in products:
                VariantCombination.objects.filter(variant__product=product).delete()
                ProductVariant.objects.filter(product=product).delete()
                ProductInventory.objects.filter(product=product).delete()
                ShippingInfo.objects.filter(product=product).delete()
                ProductSEO.objects.filter(product=product).delete()
                ProductSubCategoryMap.objects.filter(product=product).delete()
                ProductImage.objects.filter(product=product).delete()
                Image.objects.filter(linked_table='product', linked_id=product.product_id).delete()
                product.delete()

            return Response({'success': True, 'message': 'Products deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("DeleteProduct failed")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShowProductsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        products = list(Product.objects.all().order_by('order'))
        if not products:
            return Response([], status=status.HTTP_200_OK)

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
            'product_id', 'stock_status', 'stock_quantity'
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

            out.append({
                "id": p.product_id,
                "name": p.title,
                "image": image_url,
                "subcategory": subcategory_legacy,     # kept for compatibility
                "subcategories": subcategories,        # unique list
                "stock_status": stock_status,
                "stock_quantity": stock_quantity,
                "price": str(p.price),
                "printing_methods": list(pm_by_pk.get(p.pk, set())),
            })

        return Response(out, status=status.HTTP_200_OK)

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

        response = {
            "id": product.product_id,
            "name": product.title,
            "brand_title": product.brand,
            "price": str(product.price),
            "discounted_price": str(product.discounted_price),
            "tax_rate": str(product.tax_rate) if product.tax_rate is not None else None,
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
                iid = getattr(rel.image, "image_id", None)
                if url and iid and iid not in seen_image_ids:
                    seen_image_ids.add(iid)
                    image_urls.append(url)
                    images_with_ids.append({
                        "id": iid,
                        "url": url,
                        "is_primary": bool(rel.is_primary),
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
                "images_with_ids": images_with_ids,   # new: [{id,url,is_primary}]
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
                "slug": seo.slug,
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

    @transaction.atomic
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

            updated_products = []

            for product_id in product_ids:
                product = (
                    Product.objects
                    .filter(product_id=product_id)
                    .select_for_update()
                    .first()
                )
                if not product:
                    continue

                if 'name' in data and (data.get('name') or '').strip():
                    product.title = data.get('name').strip()
                product.description = data.get('description', product.description)
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

                save_product_seo(data, product)
                save_shipping_info(data, product)
                save_product_variants(data, product)
                save_product_subcategories(data, product)
                save_product_attributes(data, product)

                if force_replace and has_new_images:
                    save_product_images(
                        {
                            'images': incoming_images,
                            'image_alt_text': (data.get('image_alt_text') or 'Alt-text').strip(),
                        },
                        product
                    )

                updated_products.append(product.product_id)

            return Response({'success': True, 'updated': updated_products}, status=status.HTTP_200_OK)

        except Exception as e:
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
