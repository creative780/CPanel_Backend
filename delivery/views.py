import random
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from orders.models import Order, DeliveryStage, OrderFile
from .models import DeliveryCode
from accounts.permissions import RolePermission
from drf_spectacular.utils import extend_schema
from notifications.services import create_notification
from django.contrib.auth import get_user_model

User = get_user_model()


logger = logging.getLogger(__name__)


def _generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


class SendCodeView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'delivery']
    @extend_schema(responses={200: None})
    def post(self, request):
        order_id = request.data.get('orderId')
        phone = request.data.get('phone')
        if not order_id or not phone:
            return Response({'detail': 'orderId and phone required'}, status=400)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=404)
        code = _generate_code()
        ttl = timezone.now() + timedelta(minutes=15)
        DeliveryCode.objects.update_or_create(order=order, defaults={'code': code, 'expires_at': ttl})
        od, _ = DeliveryStage.objects.get_or_create(order=order)
        # Note: delivery_code is now on Order model, not DeliveryStage
        order.delivery_code = code
        order.save(update_fields=['delivery_code'])
        
        # Notify assigned sales person or order creator
        recipient = None
        if order.assigned_sales_person:
            recipient = User.objects.filter(username=order.assigned_sales_person).first()
        elif order.created_by:
            recipient = order.created_by
        
        if recipient:
            create_notification(
                recipient=recipient,
                title="Delivery Code Sent",
                message=f"Delivery code sent for order {order.order_code}",
                notification_type="delivery_code_sent",
                actor=request.user if request.user.is_authenticated else None,
                related_object_type="order",
                related_object_id=str(order.id)
            )
        
        # SMS provider abstraction (console)
        provider = getattr(settings, 'SMS_PROVIDER', 'console')
        if provider == 'console' and settings.DEBUG:
            logger.info("[SMS] to %s: Your delivery code is %s", phone, code)
        return Response({'code': code, 'sent': True})


class RiderPhotoUploadView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'delivery']
    parser_classes = [MultiPartParser]
    @extend_schema(responses={200: None})
    def post(self, request):
        order_id = request.data.get('orderId')
        photo = request.FILES.get('photo') or request.FILES.get('file')
        if not order_id or not photo:
            return Response({'detail': 'orderId and photo required'}, status=400)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=404)
        # Create OrderFile first (this will save the file)
        username = request.user.username if request.user.is_authenticated else 'unknown'
        user_roles = getattr(request.user, 'roles', []) or []
        user_role = ', '.join(user_roles) if user_roles else 'unknown'
        
        # Create OrderFile record - this will save the file via FileField
        order_file = OrderFile.objects.create(
            order=order,
            file=photo,  # Pass the uploaded file directly
            file_name=photo.name,
            file_type='delivery',
            file_size=photo.size,
            mime_type=photo.content_type or 'image/jpeg',
            uploaded_by=username,
            uploaded_by_role=user_role,
            stage='delivery',
            visible_to_roles=['admin', 'sales', 'designer', 'production', 'delivery'],
            description='Delivery rider photo',
            product_related=''
        )
        
        # Update DeliveryStage to reference the OrderFile's URL
        # Refresh to ensure file path is saved
        order_file.refresh_from_db()
        from django.core.files.storage import default_storage
        file_url = default_storage.url(order_file.file.name)
        od, _ = DeliveryStage.objects.get_or_create(order=order)
        od.rider_photo_path = file_url
        od.save(update_fields=['rider_photo_path'])
        
        # Notify assigned sales person or order creator
        recipient = None
        if order.assigned_sales_person:
            recipient = User.objects.filter(username=order.assigned_sales_person).first()
        elif order.created_by:
            recipient = order.created_by
        
        if recipient:
            create_notification(
                recipient=recipient,
                title="Delivery Photo Uploaded",
                message=f"Rider uploaded delivery photo for order {order.order_code}",
                notification_type="delivery_photo_uploaded",
                actor=request.user if request.user.is_authenticated else None,
                related_object_type="order",
                related_object_id=str(order.id)
            )
        
        return Response({'url': file_url})

# Create your views here.
