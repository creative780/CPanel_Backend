
# Standard Library
import json
import uuid
import traceback
from urllib.parse import urlparse, urlunparse
# Django REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utilities import save_image
# Local Imports
from .models import *  # Consider specifying models instead of wildcard import
from .permissions import FrontendOnlyPermission

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
import json, traceback

class FirstCarouselAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def get(self, request):
        try:
            carousel = FirstCarousel.objects.last()
            if not carousel:
                return Response({
                    'title': 'Default First Carousel Title',
                    'description': 'Default First Carousel Description',
                    'images': []
                }, status=status.HTTP_200_OK)

            images = (
                carousel.images
                .order_by("order")
                .select_related("image", "subcategory", "product")
                .filter(product__isnull=False)  # Only include images with valid (non-deleted) products
                .all()
            )

            image_data = []
            for img in images:
                # Skip if product is null (safety check)
                if not img.product:
                    continue
                    
                subcategory_obj = None
                if img.subcategory:
                    subcategory_obj = {
                        'id': img.subcategory.pk,                          # CharField PK (subcategory_id)
                        'name': getattr(img.subcategory, 'name', ''),
                        'slug': getattr(img.subcategory, 'slug', ''),      # present if you add slug later
                    }

                # Add product info and get latest product image if available
                product_obj = None
                # Use Image.url property which includes cache-busting parameter
                image_src = img.image.url if img.image else ''
                
                if img.product:
                    product_obj = {
                        'id': img.product.product_id,
                        'name': img.product.title,
                    }
                    # If product is linked, try to get the latest primary image
                    try:
                        product_image = ProductImage.objects.filter(
                            product=img.product,
                            is_primary=True
                        ).select_related('image').first()
                        if product_image and product_image.image:
                            # Use the product's latest primary image instead of stored carousel image
                            # Image.url property includes cache-busting parameter
                            image_src = product_image.image.url or ''
                    except Exception as e:
                        # If there's an error fetching product image, fall back to stored image
                        print(f"⚠️  Error fetching product image for {img.product.product_id}: {e}")

                image_data.append({
                    'src': image_src,
                    'title': img.title,
                    'subcategory': subcategory_obj,  # keep for backward compatibility
                    'product': product_obj,  # NEW
                })

            return Response({
                'title': carousel.title,
                'description': carousel.description,
                'images': image_data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ GET Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body or "{}")
            title = data.get('title', '')
            description = data.get('description', '')
            # Accept both 'images' (legacy) and 'items' (new format) for smooth transition
            raw_images = data.get('images', []) or data.get('items', [])

            print(f"📥 POST /api/first-carousel/ - Received {len(raw_images)} items")
            print(f"   Title: {title}")
            print(f"   Description: {description[:50]}..." if description else "   Description: (empty)")

            # Deduplicate by product_id - keep the last occurrence (most recent/updated)
            # This ensures if a product is updated, only the latest version is in the carousel
            seen_products = {}  # Maps product_id to (index, img_data)
            deduplicated_images = []
            
            for idx, img_data in enumerate(raw_images):
                if isinstance(img_data, dict):
                    product_id = img_data.get('product_id')
                    if product_id:
                        # Track the latest occurrence of each product_id
                        seen_products[product_id] = (idx, img_data)
                    else:
                        # Items without product_id are always added (custom images)
                        deduplicated_images.append((idx, img_data))
            
            # Combine custom items and product items, sorted by original index to preserve order
            all_items = list(seen_products.values()) + deduplicated_images
            all_items.sort(key=lambda x: x[0])  # Sort by original index
            deduplicated_images = [img_data for _, img_data in all_items]
            
            print(f"🔄 Deduplicated: {len(raw_images)} → {len(deduplicated_images)} items (removed {len(raw_images) - len(deduplicated_images)} duplicates)")

            # Single-instance reset (unchanged)
            deleted_count = FirstCarousel.objects.all().count()
            FirstCarousel.objects.all().delete()
            print(f"🗑️  Deleted {deleted_count} existing carousel(s)")

            carousel = FirstCarousel.objects.create(
                title=title,
                description=description
            )
            print(f"✅ Created new carousel (ID: {carousel.id})")

            saved_count = 0
            skipped_count = 0

            for i, img_data in enumerate(deduplicated_images):
                if not isinstance(img_data, dict):
                    print(f"   ⚠️  Item {i}: Skipped (not a dict)")
                    skipped_count += 1
                    continue

                img_src = img_data.get('src')
                img_title = img_data.get('title') or f'Product {i + 1}'
                product_id = img_data.get('product_id')
                
                print(f"   📦 Item {i}: title='{img_title}', product_id={product_id}, src_length={len(str(img_src)) if img_src else 0}")

                # Prefer subcategory_id; accept legacy category_id if client hasn't updated yet
                subcategory_key = img_data.get('subcategory_id') or img_data.get('category_id')
                subcategory = None
                if subcategory_key:
                    subcategory = SubCategory.objects.filter(pk=subcategory_key).first()

                # Handle product_id (NEW)
                product = None
                if product_id:
                    # Try exact match first
                    product = Product.objects.filter(product_id=product_id).first()
                    # If not found, try case-insensitive match
                    if not product:
                        product = Product.objects.filter(product_id__iexact=str(product_id).strip()).first()
                    if not product:
                        print(f"      ⚠️  Product {product_id} not found in database - carousel item will be saved without product link")
                    else:
                        print(f"      ✅ Found product: {product.product_id} - {product.title}")

                # Reuse existing /uploads/ or /media/uploads/ optimization
                # Handle both /uploads/ and /media/uploads/ paths
                if isinstance(img_src, str) and (img_src.startswith('/uploads/') or img_src.startswith('/media/uploads/')):
                    # Normalize path: /media/uploads/xxx -> uploads/xxx, /uploads/xxx -> uploads/xxx
                    normalized_path = img_src.replace('/media/uploads/', 'uploads/').replace('/uploads/', 'uploads/')
                    existing_image = Image.objects.filter(image_file=normalized_path).first()
                    
                    if existing_image:
                        FirstCarouselImage.objects.create(
                            carousel=carousel,
                            image=existing_image,
                            title=img_title,
                            subcategory=subcategory,  # keep for backward compatibility
                            product=product,  # NEW
                            order=i
                        )
                        saved_count += 1
                        print(f"      ✅ Saved using existing image (ID: {existing_image.image_id})")
                    else:
                        # Try to construct full URL and fetch it
                        base_url = getattr(settings, 'DATA_API_BASE', 'http://127.0.0.1:8000').rstrip('/api')
                        full_url = f"{base_url}{img_src}"
                        print(f"      🔄 Image not in DB, trying to fetch from URL: {full_url}")
                        
                        # Try to save from URL
                        saved_image = save_image(
                            file_or_base64=full_url,
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
                                subcategory=subcategory,
                                product=product,
                                order=i
                            )
                            saved_count += 1
                            print(f"      ✅ Saved by fetching from URL (ID: {saved_image.image_id if hasattr(saved_image, 'image_id') else 'N/A'})")
                        else:
                            print(f"      ⚠️  Failed to fetch/save image from URL: {full_url}")
                            skipped_count += 1
                    continue

                # If no image source but product is provided, try to get product's primary image
                if not img_src and product:
                    try:
                        product_image = ProductImage.objects.filter(
                            product=product,
                            is_primary=True
                        ).select_related('image').first()
                        if product_image and product_image.image:
                            # Use Image.url property which includes cache-busting parameter
                            img_src = product_image.image.url
                            if img_src:
                                print(f"      📷 Using product's primary image: {img_src}")
                    except Exception as e:
                        print(f"      ⚠️  Error fetching product image: {e}")
                
                if not img_src:
                    print(f"      ⚠️  No image source provided and no product image available - skipping item")
                    skipped_count += 1
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
                        subcategory=subcategory,  # keep for backward compatibility
                        product=product,  # NEW
                        order=i
                    )
                    saved_count += 1
                    print(f"      ✅ Saved new image (ID: {saved_image.image_id if hasattr(saved_image, 'image_id') else 'N/A'})")
                else:
                    print(f"      ❌ Image save failed")
                    skipped_count += 1

            print(f"📊 Summary: {saved_count} saved, {skipped_count} skipped out of {len(raw_images)} total")
            return Response({
                'message': '✅ First Carousel data saved successfully',
                'saved_count': saved_count,
                'skipped_count': skipped_count,
                'total_count': len(raw_images)
            }, status=status.HTTP_200_OK)

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
                    'title': 'Default Second Carousel Title',
                    'description': 'Default Second Carousel Description',
                    'images': []
                }, status=status.HTTP_200_OK)

            images = (
                carousel.images
                .order_by("order")
                .select_related("image", "subcategory", "product")
                .filter(product__isnull=False)  # Only include images with valid (non-deleted) products
                .all()
            )

            image_data = []
            for img in images:
                # Skip if product is null (safety check)
                if not img.product:
                    continue
                    
                subcategory_obj = None
                if img.subcategory:
                    try:
                        # Ensure ID is a string for consistent frontend handling
                        subcategory_id = str(img.subcategory.pk) if img.subcategory.pk else None
                        subcategory_name = str(getattr(img.subcategory, 'name', '')) if getattr(img.subcategory, 'name', None) else ''
                        
                        # Only create subcategory_obj if we have at least an ID or name (not empty strings)
                        if (subcategory_id and subcategory_id.strip()) or (subcategory_name and subcategory_name.strip()):
                            subcategory_obj = {
                                'id': subcategory_id,
                                'name': subcategory_name,
                                # Removed slug since SubCategory model doesn't have slug field
                            }
                        else:
                            # If subcategory exists but has no valid data, set to None
                            subcategory_obj = None
                    except Exception as e:
                        print(f"❌ Error getting subcategory for SecondCarouselImage {img.id}: {e}")
                        subcategory_obj = None

                # Add product info and get latest product image if available
                product_obj = None
                # Use Image.url property which includes cache-busting parameter
                image_src = img.image.url if img.image else ''
                
                if img.product:
                    product_obj = {
                        'id': img.product.product_id,
                        'name': img.product.title,
                    }
                    # If product is linked, try to get the latest primary image
                    try:
                        product_image = ProductImage.objects.filter(
                            product=img.product,
                            is_primary=True
                        ).select_related('image').first()
                        if product_image and product_image.image:
                            # Use the product's latest primary image instead of stored carousel image
                            # Image.url property includes cache-busting parameter
                            image_src = product_image.image.url or ''
                    except Exception as e:
                        # If there's an error fetching product image, fall back to stored image
                        print(f"⚠️  Error fetching product image for {img.product.product_id}: {e}")

                image_data.append({
                    'src': image_src,
                    'title': img.title,
                    'subcategory': subcategory_obj,  # keep for backward compatibility
                    'product': product_obj,  # NEW
                })

            return Response({
                'title': carousel.title,
                'description': carousel.description,
                'images': image_data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ GET Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body or "{}")
            title = data.get('title', '')
            description = data.get('description', '')
            raw_images = data.get('images', []) or data.get('items', [])

            print(f"📥 POST /api/second-carousel/ - Received {len(raw_images)} items")
            print(f"   Title: {title}")
            print(f"   Description: {description[:50]}...")

            # Deduplicate by product_id - keep the last occurrence (most recent/updated)
            # This ensures if a product is updated, only the latest version is in the carousel
            seen_products = {}  # Maps product_id to (index, img_data)
            deduplicated_images = []
            
            for idx, img_data in enumerate(raw_images):
                if isinstance(img_data, dict):
                    product_id = img_data.get('product_id')
                    if product_id:
                        # Track the latest occurrence of each product_id
                        seen_products[product_id] = (idx, img_data)
                    else:
                        # Items without product_id are always added (custom images)
                        deduplicated_images.append((idx, img_data))
            
            # Combine custom items and product items, sorted by original index to preserve order
            all_items = list(seen_products.values()) + deduplicated_images
            all_items.sort(key=lambda x: x[0])  # Sort by original index
            deduplicated_images = [img_data for _, img_data in all_items]
            
            print(f"🔄 Deduplicated: {len(raw_images)} → {len(deduplicated_images)} items (removed {len(raw_images) - len(deduplicated_images)} duplicates)")

            deleted_count = SecondCarousel.objects.all().count()
            SecondCarousel.objects.all().delete()
            print(f"🗑️  Deleted {deleted_count} existing carousel(s)")

            carousel = SecondCarousel.objects.create(
                title=title,
                description=description
            )
            print(f"✅ Created new carousel (ID: {carousel.id})")

            saved_count = 0
            skipped_count = 0

            for i, img_data in enumerate(deduplicated_images):
                if not isinstance(img_data, dict):
                    print(f"      ⚠️  Item {i}: Invalid data format, skipping.")
                    skipped_count += 1
                    continue

                img_src = img_data.get('src')
                img_title = img_data.get('title') or f'Product {i + 1}'
                product_id = img_data.get('product_id')

                print(f"   📦 Item {i}: title='{img_title}', product_id={product_id}, src_length={len(str(img_src)) if img_src else 0}")

                subcategory_key = img_data.get('subcategory_id') or img_data.get('category_id')
                subcategory = None
                if subcategory_key:
                    subcategory = SubCategory.objects.filter(pk=subcategory_key).first()

                product = None
                if product_id:
                    product = Product.objects.filter(product_id=product_id).first()
                    if not product:
                        print(f"      ⚠️  Product {product_id} not found in database")

                # Reuse existing /uploads/ or /media/uploads/ optimization
                if isinstance(img_src, str) and (img_src.startswith('/uploads/') or img_src.startswith('/media/uploads/')):
                    normalized_path = img_src.replace('/media/uploads/', 'uploads/').replace('/uploads/', 'uploads/')
                    existing_image = Image.objects.filter(image_file=normalized_path).first()
                    
                    if existing_image:
                        SecondCarouselImage.objects.create(
                            carousel=carousel,
                            image=existing_image,
                            title=img_title,
                            subcategory=subcategory,
                            product=product,
                            order=i
                        )
                        saved_count += 1
                        print(f"      ✅ Saved using existing image (ID: {existing_image.image_id})")
                    else:
                        base_url = getattr(settings, 'DATA_API_BASE', 'http://127.0.0.1:8000').rstrip('/api')
                        full_url = f"{base_url}{img_src}"
                        print(f"      🔄 Image not in DB, trying to fetch from URL: {full_url}")
                        
                        saved_image = save_image(
                            file_or_base64=full_url,
                            alt_text="Carousel Image",
                            tags="carousel",
                            linked_table="SecondCarousel",
                            linked_id=str(carousel.id),
                            linked_page="second-carousel"
                        )
                        if saved_image:
                            SecondCarouselImage.objects.create(
                                carousel=carousel,
                                image=saved_image,
                                title=img_title,
                                subcategory=subcategory,
                                product=product,
                                order=i
                            )
                            saved_count += 1
                            print(f"      ✅ Saved by fetching from URL (ID: {saved_image.image_id if hasattr(saved_image, 'image_id') else 'N/A'})")
                        else:
                            print(f"      ⚠️  Failed to fetch/save image from URL: {full_url}")
                            skipped_count += 1
                    continue

                if not img_src:
                    print(f"      ⚠️  No image source provided")
                    skipped_count += 1
                    continue

                saved_image = save_image(
                    file_or_base64=img_src,
                    alt_text="Carousel Image",
                    tags="carousel",
                    linked_table="SecondCarousel",
                    linked_id=str(carousel.id),
                    linked_page="second-carousel"
                )
                if saved_image:
                    SecondCarouselImage.objects.create(
                        carousel=carousel,
                        image=saved_image,
                        title=img_title,
                        subcategory=subcategory,
                        product=product,
                        order=i
                    )
                    saved_count += 1
                    print(f"      ✅ Saved new image (ID: {saved_image.image_id if hasattr(saved_image, 'image_id') else 'N/A'})")
                else:
                    print(f"      ❌ Image save failed")
                    skipped_count += 1

            print(f"📊 Summary: {saved_count} saved, {skipped_count} skipped out of {len(raw_images)} total")
            return Response({
                'message': '✅ Second Carousel data saved successfully',
                'saved_count': saved_count,
                'skipped_count': skipped_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("❌ POST Error:", traceback.format_exc())
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def absolutize_media_url(request, path_or_url: str) -> str:
    """
    Normalize media URLs:
    - If host is localhost/127.0.0.1 -> force http (dev server has no TLS)
    - Otherwise keep https (or whatever request.scheme is in prod)
    - Works with both relative and absolute inputs
    """
    host = request.get_host()
    is_local = host.startswith("127.0.0.1") or host.startswith("localhost") or host.startswith("[::1]")

    # Already absolute?
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        p = urlparse(path_or_url)
        if p.hostname in ("127.0.0.1", "localhost", "::1"):
            p = p._replace(scheme="http")
            return urlunparse(p)
        return path_or_url

    # Relative path → make it absolute
    scheme = "http" if is_local else request.scheme
    path = path_or_url if path_or_url.startswith("/") else f"/{path_or_url}"
    return f"{scheme}://{host}{path}"

class HeroBannerAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]
    def get(self, request):
        try:
            hero = HeroBanner.objects.last()
            if not hero:
                response = Response({
                    "images": [
                        {
                            "url": absolutize_media_url(request, "/media/uploads/desktop_default.jpg"),
                            "device_type": "desktop",
                        },
                        {
                            "url": absolutize_media_url(request, "/media/uploads/mobile_default.jpg"),
                            "device_type": "mobile",
                        },
                    ]
                }, status=status.HTTP_200_OK)
                response["Cache-Control"] = "public, max-age=60, stale-while-revalidate=120"
                return response

            images = hero.images.order_by("order").all()
            image_urls = []

            for hi in images:
                raw_url = getattr(hi.image.image_file, "url", "")
                if raw_url and not raw_url.startswith("/"):
                    if raw_url.startswith("uploads/"):
                        raw_url = f"/media/{raw_url}"
                    elif raw_url.startswith("media/"):
                        raw_url = f"/{raw_url}"

                image_urls.append({
                    "url": absolutize_media_url(request, raw_url),
                    "device_type": hi.device_type,
                })

            response = Response({"images": image_urls}, status=status.HTTP_200_OK)
            response["Cache-Control"] = "public, max-age=60, stale-while-revalidate=120"
            return response

        except Exception as e:
            print("❌ HeroBanner GET Error:", traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        