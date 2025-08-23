# Standard Library
import json
import uuid
import traceback
from decimal import Decimal


# Django
from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.db import transaction
from django.db.models import Prefetch

# Django REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utilities import format_image_object, generate_product_id, generate_unique_seo_id, generate_unique_slug, save_image
# Local Imports
from .models import *  # Consider specifying models instead of wildcard import
from .permissions import FrontendOnlyPermission




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
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
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
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
            ids = data.get('ids', [])
            confirm = data.get('confirm', False)  # kept for parity, not used in original delete flow

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

class ShowProductsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        products = Product.objects.all().order_by('order')
        product_list = []

        for product in products:
            # first image (through-model)
            image_rel = (
                ProductImage.objects
                .filter(product=product)
                .select_related('image')
                .first()
            )
            img_dict = format_image_object(image_rel, request=request)
            image_url = img_dict["url"] if img_dict else ""

            subcategory_map = (
                ProductSubCategoryMap.objects
                .filter(product=product)
                .select_related('subcategory')
                .first()
            )
            subcategory_data = {
                "id": subcategory_map.subcategory.subcategory_id if subcategory_map else None,
                "name": subcategory_map.subcategory.name if subcategory_map else None,
            }

            try:
                inventory = ProductInventory.objects.get(product=product)
                stock_status = inventory.stock_status
                stock_quantity = inventory.stock_quantity
            except ProductInventory.DoesNotExist:
                stock_status = None
                stock_quantity = None

            variants = ProductVariant.objects.filter(product=product)
            printing_methods = set()
            for variant in variants:
                methods = variant.printing_methods or []
                if isinstance(methods, list):
                    printing_methods.update(methods)

            product_list.append({
                "id": product.product_id,
                "name": product.title,
                "image": image_url,  # string URL
                "subcategory": subcategory_data,
                "stock_status": stock_status,
                "stock_quantity": stock_quantity,
                "price": str(product.price),
                "printing_methods": list(printing_methods),
            })

        return Response(product_list, status=status.HTTP_200_OK)

class ShowSpecificProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
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
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
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

class ShowProductShippingInfoAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
            product_id = data.get('product_id')
            if not product_id:
                return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

            shipping = ShippingInfo.objects.get(product_id=product_id)

            data_out = {
                "shipping_class": shipping.shipping_class,
                "processing_time": shipping.processing_time
            }

            return Response(data_out, status=status.HTTP_200_OK)
        except ShippingInfo.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ShowProductOtherDetailsAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
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
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
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
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
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
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
        except Exception:
            return Response({"error": "Invalid JSON body"}, status=status.HTTP_400_BAD_REQUEST)

        product_id = data.get("product_id")
        if not product_id:
            return Response({"error": "Missing product_id"}, status=status.HTTP_400_BAD_REQUEST)

        # if your Product uses "product_id" (string SKU), keep this:
        product = get_object_or_404(Product, product_id=product_id)
        # if the PK is "id" instead, use: product = get_object_or_404(Product, id=product_id)

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
    
class UpdateProductOrderAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")
            updates = data.get("products", [])

            for idx, item in enumerate(updates):
                product_id = item.get("id")
                product = Product.objects.filter(product_id=product_id).first()
                if product:
                    product.order = idx
                    product.save()

            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EditProductAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            data = request.data if isinstance(request.data, dict) else json.loads(request.body or "{}")

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
                    save_product_attributes(data, product)   # ✅ THIS WAS MISSING

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

