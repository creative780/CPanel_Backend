# Standard Library
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

# Django REST Framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Local Imports
from .models import Favorite, Product, Image
from .permissions import FrontendOnlyPermission


class SaveFavoriteAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            # Parse payload safely
            if isinstance(request.data, dict):
                data = request.data
            else:
                try:
                    data = json.loads(request.body or "{}")
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON payload."}, status=status.HTTP_400_BAD_REQUEST)

            device_uuid = data.get("device_uuid") or request.headers.get("X-Device-UUID")
            product_id = data.get("product_id")
            
            if not product_id:
                return Response({"error": "Missing product_id."}, status=status.HTTP_400_BAD_REQUEST)

            product = get_object_or_404(Product, product_id=product_id)

            # Check if user is authenticated
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            elif data.get("user_id"):
                try:
                    DjangoUser = get_user_model()
                    user = DjangoUser.objects.get(user_id=data.get("user_id"))
                except DjangoUser.DoesNotExist:
                    pass

            # Check if favorite already exists
            if user:
                favorite, created = Favorite.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={"device_uuid": device_uuid}
                )
            elif device_uuid:
                favorite, created = Favorite.objects.get_or_create(
                    device_uuid=device_uuid,
                    product=product,
                    defaults={"user": user}
                )
            else:
                return Response({"error": "Missing device_uuid or user authentication."}, status=status.HTTP_400_BAD_REQUEST)

            if not created:
                return Response({"message": "Product already in favorites.", "favorite_id": str(favorite.favorite_id)}, status=status.HTTP_200_OK)

            return Response({
                "message": "Product added to favorites.",
                "favorite_id": str(favorite.favorite_id),
                "product_id": product_id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteFavoriteAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def post(self, request):
        try:
            # Parse payload safely
            if isinstance(request.data, dict):
                data = request.data
            else:
                try:
                    data = json.loads(request.body or "{}")
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON payload."}, status=status.HTTP_400_BAD_REQUEST)

            device_uuid = data.get("device_uuid") or request.headers.get("X-Device-UUID")
            product_id = data.get("product_id")
            
            if not product_id:
                return Response({"error": "Missing product_id."}, status=status.HTTP_400_BAD_REQUEST)

            product = get_object_or_404(Product, product_id=product_id)

            # Try to find favorite by user or device_uuid
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            elif data.get("user_id"):
                try:
                    DjangoUser = get_user_model()
                    user = DjangoUser.objects.get(user_id=data.get("user_id"))
                except DjangoUser.DoesNotExist:
                    pass

            if user:
                favorite = Favorite.objects.filter(user=user, product=product).first()
            elif device_uuid:
                favorite = Favorite.objects.filter(device_uuid=device_uuid, product=product).first()
            else:
                return Response({"error": "Missing device_uuid or user authentication."}, status=status.HTTP_400_BAD_REQUEST)

            if not favorite:
                return Response({"error": "Favorite not found."}, status=status.HTTP_404_NOT_FOUND)

            favorite.delete()
            return Response({"message": "Product removed from favorites."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShowFavoritesAPIView(APIView):
    permission_classes = [FrontendOnlyPermission]

    def _get_favorites(self, request, device_uuid=None, user_id=None):
        """Get favorites for user or device, return list of product IDs"""
        favorites = Favorite.objects.none()
        
        if user_id:
            try:
                DjangoUser = get_user_model()
                user = DjangoUser.objects.get(user_id=user_id)
                favorites = Favorite.objects.filter(user=user).select_related("product")
            except DjangoUser.DoesNotExist:
                pass
        
        if device_uuid and not favorites.exists():
            favorites = Favorite.objects.filter(device_uuid=device_uuid).select_related("product")
        
        # Return product IDs
        product_ids = [fav.product.product_id for fav in favorites]
        return product_ids

    def get(self, request):
        device_uuid = request.headers.get("X-Device-UUID")
        user_id = request.GET.get("user_id")
        
        product_ids = self._get_favorites(request, device_uuid=device_uuid, user_id=user_id)
        
        return Response({"favorites": product_ids}, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            # Parse payload safely
            if isinstance(request.data, dict):
                data = request.data
            else:
                try:
                    data = json.loads(request.body or "{}")
                except json.JSONDecodeError:
                    return Response({"error": "Invalid JSON payload."}, status=status.HTTP_400_BAD_REQUEST)

            device_uuid = data.get("device_uuid") or request.headers.get("X-Device-UUID")
            user_id = data.get("user_id")
            
            product_ids = self._get_favorites(request, device_uuid=device_uuid, user_id=user_id)
            
            # Optionally return full product details with images
            include_details = data.get("include_details", False)
            if include_details:
                products = Product.objects.filter(product_id__in=product_ids)
                products_data = []
                for product in products:
                    # Get first product image
                    image_rel = Image.objects.filter(
                        linked_table='product',
                        linked_id=product.product_id
                    ).first()
                    image_url = request.build_absolute_uri(image_rel.url) if image_rel and getattr(image_rel, "url", None) else None
                    
                    products_data.append({
                        "product_id": product.product_id,
                        "title": product.title,
                        "price": str(product.price or "0.00"),
                        "discounted_price": str(product.discounted_price or "0.00") if product.discounted_price else None,
                        "image_url": image_url,
                    })
                
                return Response({
                    "favorites": product_ids,
                    "products": products_data
                }, status=status.HTTP_200_OK)
            
            return Response({"favorites": product_ids}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

