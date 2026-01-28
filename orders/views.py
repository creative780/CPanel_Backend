import re
import uuid
import os
import logging
from typing import Any, Mapping, Optional
from decimal import Decimal, DecimalException
from django.utils.crypto import get_random_string
from django.db import transaction
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from .models import (
    Order, OrderItem, Quotation, DesignStage, PrintingStage, 
    ApprovalStage, DeliveryStage, Upload
)
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderUpdateSerializer, OrderListSerializer,
    StageTransitionSerializer, MarkPrintedSerializer, SendDeliveryCodeSerializer,
    RiderPhotoUploadSerializer, QuotationSerializer, DesignStageSerializer,
    PrintingStageSerializer, ApprovalStageSerializer, DeliveryStageSerializer
)
from accounts.permissions import RolePermission
from drf_spectacular.utils import extend_schema, extend_schema_view
from notifications.services import notify_admins, create_notification
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_order_code() -> str:
    """Generate a human-readable order code like ORD-ABC123"""
    prefix = "ORD"
    suffix = get_random_string(6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    return f"{prefix}-{suffix}"


def _derive_status_from_stage(stage: str, payload: Optional[Mapping[str, Any]] = None) -> str:
    """Return the desired order.status for a given stage transition."""
    stage_status_map = {
        "order_intake": "new",
        "quotation": "active",
        "design": "active",
        "printing": "active",
        "approval": "active",
        "delivery": "sent_for_delivery",  # Delivery stage should set status to sent_for_delivery
    }
    
    if stage == "delivery" and payload:
        delivered_at = payload.get("delivered_at")
        if delivered_at:
            return "delivered"  # If delivered_at is set, order is delivered

    return stage_status_map.get(stage, "new")


def create_stage_models(order: Order, stage: str, payload: dict = None):
    """Create or update stage-specific models"""
    try:
        print(f"Creating stage models for {stage} with payload: {payload}")
        
        if stage == "quotation" and payload:
            quotation, created = Quotation.objects.get_or_create(order=order)
            # Handle numeric fields (convert to Decimal)
            numeric_fields = ['labour_cost', 'finishing_cost', 'paper_cost', 'machine_cost', 
                             'design_cost', 'delivery_cost', 'other_charges', 'discount', 'advance_paid']
            for field in numeric_fields:
                if field in payload:
                    value = payload[field]
                    if isinstance(value, str):
                        try:
                            # Handle empty strings and whitespace-only strings
                            if not value or value.strip() == '':
                                value = Decimal('0.00')
                            else:
                                value = Decimal(value)
                        except (ValueError, TypeError, DecimalException):
                            value = Decimal('0.00')
                    setattr(quotation, field, value)
            
            # Handle string fields (no conversion needed)
            string_fields = ['sales_person']
            for field in string_fields:
                if field in payload:
                    setattr(quotation, field, payload[field])
            
            # Handle finalPrice field (maps to grand_total)
            if 'finalPrice' in payload:
                value = payload['finalPrice']
                if isinstance(value, str):
                    try:
                        value = Decimal(value)
                    except (ValueError, TypeError):
                        value = Decimal('0.00')
                quotation.grand_total = value
            
            quotation.save(skip_calculation=True)  # Skip auto-calculation for manual updates
            print(f"Quotation model saved: {created}")
            
            # Calculate remaining if grand_total and advance_paid are set (since skip_calculation=True)
            if quotation.grand_total is not None and quotation.advance_paid is not None:
                quotation.remaining = quotation.grand_total - quotation.advance_paid
            
            # Notify admins for high-value B2B orders (AED 10,000+)
            if order.channel == 'b2b_customers' and quotation.grand_total and quotation.grand_total > Decimal('10000'):
                notify_admins(
                    title="High-Value B2B Order",
                    message=f"B2B order {order.order_code} worth AED {quotation.grand_total} created",
                    notification_type="order_created",
                    actor=None,  # System notification
                    related_object_type="order",
                    related_object_id=str(order.id),
                    metadata={'order_value': float(quotation.grand_total), 'channel': 'b2b_customers'}
                )
            
            # Notify finance users for unpaid walk-in invoices
            if order.channel == 'walk_in_orders' and quotation.remaining and quotation.remaining > Decimal('0'):
                finance_users = User.objects.filter(roles__contains=['finance'])
                for finance_user in finance_users:
                    create_notification(
                        recipient=finance_user,
                        title="Unpaid Walk-In Invoice",
                        message=f"Walk-in order {order.order_code} has unpaid invoice (Remaining: AED {quotation.remaining})",
                        notification_type="order_created",
                        actor=None,  # System notification
                        related_object_type="order",
                        related_object_id=str(order.id)
                    )
            
            # Update order model fields if provided
            order_updated = False
            for field in ['clientName', 'companyName', 'phone', 'trn', 'email', 'address', 'specifications']:
                if field in payload:
                    # Map frontend field names to backend field names
                    if field == 'clientName':
                        backend_field = 'client_name'
                    elif field == 'companyName':
                        backend_field = 'company_name'
                    elif field == 'specifications':
                        backend_field = 'specs'
                    else:
                        backend_field = field  # trn, phone, email, address remain the same
                    
                    print(f"Updating order field: {field} -> {backend_field} = {payload[field]}")
                    setattr(order, backend_field, payload[field])
                    order_updated = True
            
            if order_updated:
                order.save()
                print(f"Order model updated with new fields")
        
        elif stage == "design" and payload:
            design, created = DesignStage.objects.get_or_create(order=order)
            old_designer = design.assigned_designer if design.assigned_designer else None
            for field in ['assigned_designer', 'requirements_files_manifest', 'design_status', 'internal_comments']:
                if field in payload:
                    print(f"Setting {field} = {payload[field]}")
                    setattr(design, field, payload[field])
            design.save()
            print(f"Design model saved: {created}")
            
            # Update order.assigned_designer if provided in payload
            if 'assigned_designer' in payload and payload['assigned_designer']:
                order.assigned_designer = payload['assigned_designer']
                order.save(update_fields=['assigned_designer'])
            
            # Notify designer if assigned/changed
            if 'assigned_designer' in payload and payload['assigned_designer']:
                new_designer = payload['assigned_designer']
                # Only notify if designer changed
                if new_designer != old_designer:
                    designer_user = User.objects.filter(username=new_designer).first()
                    if designer_user:
                        create_notification(
                            recipient=designer_user,
                            title="Order Assigned to You",
                            message=f"Order {order.order_code} has been assigned to you",
                            notification_type="order_assigned",
                            actor=None,  # System assignment via stage transition
                            related_object_type="order",
                            related_object_id=str(order.id)
                        )
        
        elif stage == "printing" and payload:
            printing, created = PrintingStage.objects.get_or_create(order=order)
            for field in ['print_operator', 'print_time', 'batch_info', 'print_status', 'qa_checklist', 'printing_technique', 'colors_in_print']:
                if field in payload:
                    print(f"Setting {field} = {payload[field]}")
                    setattr(printing, field, payload[field])
            printing.save()
            print(f"Printing model saved: {created}")
        
        elif stage == "approval" and payload:
            approval, created = ApprovalStage.objects.get_or_create(order=order)
            for field in ['client_approval_files', 'approved_at']:
                if field in payload:
                    print(f"Setting {field} = {payload[field]}")
                    setattr(approval, field, payload[field])
            approval.save()
            print(f"Approval model saved: {created}")
        
        elif stage == "delivery" and payload:
            delivery, created = DeliveryStage.objects.get_or_create(order=order)
            
            # Handle delivery_code at order level since it's in Order model
            if 'delivery_code' in payload:
                print(f"Setting delivery_code = {payload['delivery_code']}")
                order.delivery_code = payload['delivery_code']
                order.save(update_fields=['delivery_code'])
            
            # Handle delivery-specific fields in DeliveryStage model
            for field in ['rider_photo_path', 'delivered_at', 'delivery_option', 'expected_delivery_date']:
                if field in payload:
                    value = payload[field]
                    # Skip empty strings and None values
                    if value is None or (isinstance(value, str) and not value.strip()):
                        continue
                    
                    print(f"Setting {field} = {value}")
                    # Handle date parsing for expected_delivery_date
                    if field == 'expected_delivery_date' and isinstance(value, str):
                        from django.utils.dateparse import parse_date
                        parsed_date = parse_date(value)
                        if parsed_date:
                            setattr(delivery, field, parsed_date)
                        else:
                            print(f"Warning: Could not parse date {value}")
                    else:
                        setattr(delivery, field, value)
            delivery.save()
            print(f"Delivery model saved: {created}")
            
    except Exception as e:
        import traceback
        print(f"Error in create_stage_models: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        print(f"Stage: {stage}, Payload: {payload}")
        raise


@extend_schema_view(
    create=extend_schema(
        summary="Create Order",
        description="Create a new order with items",
        request=OrderCreateSerializer,
        responses={201: OrderSerializer}
    ),
    list=extend_schema(
        summary="List Orders",
        description="List orders with optional filtering by stage and status",
        responses={200: OrderListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Get Order",
        description="Get detailed order information including all stage data",
        responses={200: OrderSerializer}
    ),
    partial_update=extend_schema(
        summary="Update Order",
        description="Update order base fields or transition to a new stage",
        request=OrderUpdateSerializer,
        responses={200: OrderSerializer}
    ),
    mark_printed=extend_schema(
        summary="Mark Printed",
        description="Mark order items as printed",
        request=MarkPrintedSerializer,
        responses={200: {"ok": True}}
    )
)
class OrdersViewSet(ModelViewSet):
    """Main ViewSet for Order CRUD operations and stage transitions"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    
    def get_queryset(self):
        """
        Get queryset for orders with visibility filtering:
        - Admins see ALL orders
        - Designers see orders assigned to them
        - Production users see orders assigned to them
        - Others see no restricted orders (or all if no assignment)
        """
        user = self.request.user
        user_username = getattr(user, 'username', None)
        user_roles = getattr(user, 'roles', []) or []
        is_admin = 'admin' in user_roles or getattr(user, 'is_superuser', False)
        
        # Workaround: Use defer() to prevent loading client field
        # However, Django still selects client_id column for ForeignKey fields
        # The proper fix is to apply the database migration that adds the client_id column
        # For now, we use defer() and ensure serializers don't access obj.client
        queryset = Order.objects.all().defer('client').prefetch_related('items', 'uploads', 'quotation', 'delivery_stage')
        
        # Admins see all orders
        if not is_admin:
            # Filter by user assignment
            # Users see orders if:
            # 1. They are assigned as designer (assigned_designer matches their username)
            # 2. They are assigned as production person (assigned_production_person matches their username)
            # 3. OR the order has no assignment (backward compatibility: assigned_designer is null/empty AND assigned_production_person is null/empty)
            if 'designer' in user_roles or 'production' in user_roles:
                queryset = queryset.filter(
                    Q(assigned_designer=user_username) |
                    Q(assigned_production_person=user_username) |
                    Q(assigned_designer__isnull=True, assigned_production_person__isnull=True) |
                    Q(assigned_designer='', assigned_production_person='')
                )
        
        # Filter by stage
        stage = self.request.query_params.get('stage')
        if stage:
            queryset = queryset.filter(stage=stage)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by urgency
        urgency_filter = self.request.query_params.get('urgency')
        if urgency_filter:
            queryset = queryset.filter(urgency=urgency_filter)
        
        # Filter for delayed orders: expected_delivery_date < today AND status != 'delivered'
        delayed = self.request.query_params.get('delayed')
        if delayed == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                delivery_stage__expected_delivery_date__lt=today
            ).exclude(status='delivered')
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'partial_update':
            return OrderUpdateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new order - matches frontend contract"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Create order
            order_data = serializer.validated_data
            items_data = order_data.pop('items')
            
            # Get channel from request data if provided (not in serializer)
            channel = request.data.get('channel')
            
            # Create order - client_id column should now exist after migration
            # Keeping workaround as fallback in case column doesn't exist in some environments
            order = Order(
                order_code=generate_order_code(),
                client_name=order_data['clientName'],
                company_name=order_data.get('companyName', ''),
                phone=order_data.get('phone', ''),
                trn=order_data.get('trn', ''),
                email=order_data.get('email', ''),
                address=order_data.get('address', ''),
                specs=order_data.get('specs', ''),
                urgency=order_data.get('urgency', 'Normal'),
                sales_person=order_data.get('salesPerson', None),
                assigned_sales_person=request.user.username,  # Assign to current user
                created_by=request.user if request.user.is_authenticated else None,
                channel=channel if channel in dict(Order.CHANNEL_CHOICES) else None,
                sample_approval_required=order_data.get('sampleApprovalRequired', False),
            )
            # Explicitly set client to None
            order.client = None
            
            # Try normal save first (should work now that migration is applied)
            try:
                order.save()
            except Exception as e:
                # Fallback: If client_id column doesn't exist, use raw SQL workaround
                if 'client_id' in str(e).lower() or 'does not exist' in str(e).lower():
                    from django.db import connection
                    # Use raw SQL to insert without client_id
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO orders_order (
                                order_code, client_name, company_name, phone, trn, email, address,
                                specs, urgency, sales_person, assigned_sales_person, created_by_id,
                                channel, sample_approval_required, status, stage, pricing_status,
                                created_at, updated_at
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                            ) RETURNING id
                        """, [
                            order.order_code, order.client_name, order.company_name, order.phone,
                            order.trn, order.email, order.address, order.specs, order.urgency,
                            order.sales_person, order.assigned_sales_person, order.created_by_id if order.created_by else None,
                            order.channel, order.sample_approval_required, order.status, order.stage, order.pricing_status
                        ])
                        order.id = cursor.fetchone()[0]
                        # Refresh the order instance to get all fields
                        order.refresh_from_db()
                else:
                    raise
            
            # Import utility function for copying product images
            from .utils import copy_product_image_to_storage
            logger = logging.getLogger(__name__)
            
            # Create order items
            for item_data in items_data:
                # Explicitly extract image_url to ensure it's saved
                original_image_url = item_data.get('image_url')  # Get image_url (can be None)
                # Remove image_url from item_data if present to avoid conflicts
                item_data_without_image = {k: v for k, v in item_data.items() if k != 'image_url'}
                
                # Create the order item
                order_item = OrderItem.objects.create(order=order, **item_data_without_image)
                
                # Copy product image to permanent storage if available
                if original_image_url:
                    try:
                        copied_image_url = copy_product_image_to_storage(
                            image_url=original_image_url,
                            order_id=order.id,
                            product_name=item_data.get('name')
                        )
                        # Use copied URL if successful, otherwise keep original
                        order_item.image_url = copied_image_url or original_image_url
                    except Exception as e:
                        # Log error but don't fail order creation
                        logger.warning(f"Failed to copy product image for order {order.id}: {e}")
                        # Keep original URL as fallback
                        order_item.image_url = original_image_url
                else:
                    order_item.image_url = None
                
                order_item.save(update_fields=['image_url'])
            
            # Handle designer and production assignments
            assigned_designer = order_data.get('assignedDesigner')
            assigned_production_person = order_data.get('assignedProductionPerson')
            
            # Filter out empty strings and None values for assignments
            assigned_designer = assigned_designer if assigned_designer and str(assigned_designer).strip() else None
            assigned_production_person = assigned_production_person if assigned_production_person and str(assigned_production_person).strip() else None
            
            # Handle designer assignment
            if assigned_designer:
                order.assigned_designer = assigned_designer.strip()
                order.save(update_fields=['assigned_designer'])
            
            # Handle production assignment
            if assigned_production_person:
                order.assigned_production_person = assigned_production_person.strip()
                order.save(update_fields=['assigned_production_person'])
            
            # Handle delivery stage fields if provided
            delivery_date = order_data.get('deliveryDate')
            delivery_option = order_data.get('deliveryOption')
            assigned_department = order_data.get('assignedDepartment')
            handled_by = order_data.get('handledBy')
            
            # Filter out empty strings and None values
            delivery_date = delivery_date if delivery_date and str(delivery_date).strip() else None
            delivery_option = delivery_option if delivery_option and str(delivery_option).strip() else None
            assigned_department = assigned_department if assigned_department and str(assigned_department).strip() else None
            handled_by = handled_by if handled_by and str(handled_by).strip() else None
            
            # Create delivery stage if delivery date or option is provided
            if delivery_date or delivery_option:
                delivery_stage, created = DeliveryStage.objects.get_or_create(order=order)
                if delivery_date:
                    from django.utils.dateparse import parse_date
                    parsed_date = parse_date(delivery_date) if isinstance(delivery_date, str) else delivery_date
                    if parsed_date:
                        delivery_stage.expected_delivery_date = parsed_date
                if delivery_option:
                    # Map frontend values to backend choices
                    delivery_option_map = {
                        'Pickup': 'pickup',
                        'Home/Office Delivery': 'home_office',
                        'Courier': 'courier',
                    }
                    mapped_option = delivery_option_map.get(delivery_option)
                    if mapped_option:
                        delivery_stage.delivery_option = mapped_option
                delivery_stage.save()
            
            # Store assigned department and handled by in order (keep delivery/handledBy logic unchanged)
            if assigned_department and handled_by and assigned_department == 'Delivery':
                # Store in internal_notes for delivery department
                order.internal_notes = f"Delivery handled by: {handled_by}\n" + (order.internal_notes or '')
                order.save(update_fields=['internal_notes'])
            elif handled_by and not assigned_designer and not assigned_production_person:
                # If only handled_by is provided without designer/production assignment, store in internal_notes
                order.internal_notes = f"Handled by: {handled_by}\n" + (order.internal_notes or '')
                order.save(update_fields=['internal_notes'])
            
            # Notify admins about the new order
            notify_admins(
                title="New Order Created",
                message=f"New order {order.order_code} created for {order.client_name}",
                notification_type="order_created",
                actor=request.user if request.user.is_authenticated else None,
                related_object_type="order",
                related_object_id=str(order.id)
            )
            
            # Notify assigned salesperson if this is an online order
            if order.channel == 'online_store' and order.assigned_sales_person:
                salesperson_user = User.objects.filter(username=order.assigned_sales_person).first()
                if salesperson_user:
                    create_notification(
                        recipient=salesperson_user,
                        title="Online Order Received",
                        message=f"New online order {order.order_code} assigned to you",
                        notification_type="order_created",
                        actor=request.user if request.user.is_authenticated else None,
                        related_object_type="order",
                        related_object_id=str(order.id)
                    )
        
        response_serializer = OrderSerializer(order, context={'request': request})
        return Response({
            'ok': True,
            'data': {
                'id': order.id,
                'order_code': order.order_code,
                'items': response_serializer.data['items']
            }
        }, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """Update order or transition stage - matches frontend contract"""
        try:
            instance = self.get_object()
            
            # Check if this is a stage transition
            if 'stage' in request.data:
                return self._handle_stage_transition(instance, request.data)
            
            # Regular order update
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                validated_data = serializer.validated_data
                serializer.save()
                
                # Notify assigned salesperson if channel is set to 'online_store'
                if 'channel' in validated_data and validated_data['channel'] == 'online_store':
                    # Refresh instance to get updated channel
                    instance.refresh_from_db()
                    if instance.assigned_sales_person:
                        salesperson_user = User.objects.filter(username=instance.assigned_sales_person).first()
                        if salesperson_user:
                            create_notification(
                                recipient=salesperson_user,
                                title="Online Order Received",
                                message=f"New online order {instance.order_code} assigned to you",
                                notification_type="order_created",
                                actor=request.user if request.user.is_authenticated else None,
                                related_object_type="order",
                                related_object_id=str(instance.id)
                            )
            
            response_serializer = OrderSerializer(instance, context={'request': request})
            return Response({
                'ok': True,
                'data': response_serializer.data
            })
        except Exception as e:
            import traceback
            print(f"Error in partial_update: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            print(f"Request data: {request.data}")
            raise
    
    def _handle_stage_transition(self, order: Order, data: dict):
        """Handle stage transitions with payload"""
        try:
            stage_serializer = StageTransitionSerializer(data=data)
            stage_serializer.is_valid(raise_exception=True)
            
            new_stage = stage_serializer.validated_data['stage']
            payload = stage_serializer.validated_data.get('payload', {})
            
            print(f"Stage transition: {new_stage}, payload: {payload}")
            
            with transaction.atomic():
                # Update order stage and status
                order.stage = new_stage
                new_status = _derive_status_from_stage(new_stage, payload)
                order.status = new_status
                order.save(update_fields=['stage', 'status'])
                
                # Create/update stage-specific models
                create_stage_models(order, new_stage, payload)
                
                # Notify if order is delivered (status is "completed")
                if new_status == 'completed' or new_status == 'delivered':
                    # Notify order creator if exists
                    if order.created_by:
                        create_notification(
                            recipient=order.created_by,
                            title="Order Delivered",
                            message=f"Order {order.order_code} has been delivered",
                            notification_type="delivery_status_updated",
                            actor=None,  # System notification
                            related_object_type="order",
                            related_object_id=str(order.id)
                        )
                    
                    # Notify assigned sales person if exists
                    if order.assigned_sales_person:
                        sales_person_user = User.objects.filter(username=order.assigned_sales_person).first()
                        if sales_person_user:
                            create_notification(
                                recipient=sales_person_user,
                                title="Order Delivered",
                                message=f"Order {order.order_code} has been delivered",
                                notification_type="delivery_status_updated",
                                actor=None,  # System notification
                                related_object_type="order",
                                related_object_id=str(order.id)
                            )
            
            response_serializer = OrderSerializer(order, context={'request': self.request})
            return Response({
                'ok': True,
                'data': response_serializer.data
            })
        except Exception as e:
            import traceback
            print(f"Error in _handle_stage_transition: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            print(f"Stage data: {data}")
            raise
    
    @action(detail=True, methods=['post'])
    def mark_printed(self, request, pk=None):
        """Mark order items as printed - matches frontend contract"""
        order = self.get_object()
        serializer = MarkPrintedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sku = serializer.validated_data['sku']
        qty = serializer.validated_data['qty']
        print_operator = serializer.validated_data.get('print_operator', '')
        print_time = serializer.validated_data.get('print_time')
        batch_info = serializer.validated_data.get('batch_info', '')
        qa_checklist = serializer.validated_data.get('qa_checklist', '')
        
        with transaction.atomic():
            # Update printing stage with all details
            printing, created = PrintingStage.objects.get_or_create(order=order)
            printing.print_status = 'Printed'
            printing.print_operator = print_operator
            if print_time:
                printing.print_time = print_time
            printing.batch_info = batch_info
            printing.qa_checklist = qa_checklist
            printing.save()
            
            # Update order status if needed
            if order.stage == 'printing':
                order.status = 'Active'
                order.save(update_fields=['status'])
            
            # Log the printing completion
            print(f"Order {order.order_code} marked as printed by {print_operator}")
            print(f"SKU: {sku}, Quantity: {qty}")
        
        return Response({
            'ok': True, 
            'message': f'Order {order.order_code} marked as printed successfully',
            'print_status': 'Printed',
            'order_status': order.status
        })


class SendDeliveryCodeView(APIView):
    """Send delivery code via SMS - matches frontend contract"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'delivery']
    
    @extend_schema(
        summary="Send Delivery Code",
        description="Send a 6-digit delivery code via SMS",
        request=SendDeliveryCodeSerializer,
        responses={200: {"ok": True}}
    )
    def post(self, request):
        serializer = SendDeliveryCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        phone = serializer.validated_data['phone']
        
        # TODO: Integrate with Twilio for production
        # For now, just log the SMS
        print(f"SMS to {phone}: Your delivery code is {code}")
        
        return Response({'ok': True})


class RiderPhotoUploadView(APIView):
    """Upload rider photo for delivery proof - matches frontend contract"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'delivery']
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        summary="Upload Rider Photo",
        description="Upload proof of delivery photo",
        request=RiderPhotoUploadSerializer,
        responses={200: {"url": "string"}}
    )
    def post(self, request):
        serializer = RiderPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        photo = serializer.validated_data['photo']
        order_id = serializer.validated_data['orderId']
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Save the file
        file_path = default_storage.save(f'rider_photos/{order_id}_{photo.name}', photo)
        file_url = default_storage.url(file_path)
        
        # Update delivery stage
        delivery, created = DeliveryStage.objects.get_or_create(order=order)
        delivery.rider_photo_path = file_path
        delivery.save()
        
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
        
        # Build absolute URL
        if request:
            file_url = request.build_absolute_uri(file_url)
        
        return Response({'url': file_url})


# Legacy views for backward compatibility - can be removed after frontend migration
class OrdersListView(ListAPIView):
    """
    Legacy list view for orders.
    NOTE: Returns ALL orders regardless of creator or assigned_sales_person.
    Sales person can see all orders including those created by admin.
    """
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    serializer_class = OrderListSerializer
    
    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_field = 'id'


class LeaderboardView(APIView):
    """Salesperson leaderboard by month/year"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    
    @extend_schema(
        summary="Get Salesperson Leaderboard",
        description="Get monthly salesperson leaderboard with orders count, total sales, and conversion rate",
        responses={200: {
            'type': 'object',
            'properties': {
                'month': {'type': 'string'},
                'leaderboard': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'salesperson': {'type': 'string'},
                            'orders_count': {'type': 'integer'},
                            'total_sales': {'type': 'number'},
                            'conversion_rate': {'type': 'number'},
                            'rank': {'type': 'integer'}
                        }
                    }
                }
            }
        }}
    )
    def get(self, request):
        from django.db.models import Sum, Count, Q, F, DecimalField
        from django.db.models.functions import Coalesce
        from datetime import datetime
        from calendar import month_name
        from decimal import Decimal
        
        # Get month and year from query params
        # If month is not provided, return yearly data
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        now = datetime.now()
        if not year:
            year = str(now.year)
        
        try:
            year_int = int(year)
            # Validate year range
            if year_int < 2000 or year_int > 2100:
                year_int = now.year
        except (ValueError, TypeError):
            year_int = now.year
        
        # Filter orders - if month is provided, filter by month; otherwise, filter by year only
        orders = Order.objects.filter(
            created_at__year=year_int
        )
        
        # If month is provided, also filter by month
        if month:
            try:
                month_int = int(month)
                if 1 <= month_int <= 12:
                    orders = orders.filter(created_at__month=month_int)
            except (ValueError, TypeError):
                pass  # Ignore invalid month, use year-only filter
        
        orders = orders.exclude(
            Q(assigned_sales_person='') | Q(assigned_sales_person__isnull=True)
        ).prefetch_related('items')
        
        # Aggregate by salesperson - ensure we only count orders with valid sales data
        leaderboard_data = orders.values('assigned_sales_person').annotate(
            orders_count=Count('id', distinct=True),
            # Use Coalesce to handle null values and ensure we only sum valid line_totals
            total_sales=Coalesce(
                Sum('items__line_total', filter=Q(items__line_total__isnull=False)),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            completed_orders=Count(
                'id',
                distinct=True,
                filter=Q(status__in=['completed', 'delivered']) | Q(stage='delivery')
            )
        ).filter(
            assigned_sales_person__isnull=False
        ).exclude(
            assigned_sales_person=''
        ).order_by('-total_sales')
        
        # Calculate conversion rate and format data
        leaderboard = []
        rank = 1
        for entry in leaderboard_data:
            salesperson = entry['assigned_sales_person'] or 'Unassigned'
            orders_count = entry['orders_count'] or 0
            total_sales_decimal = entry.get('total_sales') or Decimal('0.00')
            total_sales = float(total_sales_decimal)
            completed_orders = entry['completed_orders'] or 0
            
            # Only include salespeople with actual sales (orders that have items with line_total > 0)
            if total_sales <= 0 or orders_count == 0:
                continue
            
            # Calculate conversion rate (completed orders / total orders * 100)
            conversion_rate = (completed_orders / orders_count * 100) if orders_count > 0 else 0.0
            
            leaderboard.append({
                'salesperson': salesperson,
                'orders_count': orders_count,
                'total_sales': total_sales,
                'conversion_rate': round(conversion_rate, 2),
                'rank': rank
            })
            rank += 1
        
        # Format period name - if month was provided, show month; otherwise show year
        if month:
            try:
                month_int = int(month)
                if 1 <= month_int <= 12:
                    month_name_str = month_name[month_int]
                    period_str = f"{month_name_str} {year_int}"
                else:
                    period_str = f"Year {year_int}"
            except (ValueError, TypeError):
                period_str = f"Year {year_int}"
        else:
            period_str = f"Year {year_int}"
        
        return Response({
            'month': period_str,
            'leaderboard': leaderboard
        })


class ChannelAnalyticsView(APIView):
    """Channel analytics endpoint"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    
    @extend_schema(
        summary="Get Channel Analytics",
        description="Get analytics breakdown by order channel",
        responses={200: {
            'type': 'object',
            'properties': {
                'channel_distribution': {'type': 'array'},
                'sales_by_salesperson': {'type': 'array'},
                'daily_trends': {'type': 'array'}
            }
        }}
    )
    
    def get(self, request):
        from django.db.models import Sum, Count, Q, DecimalField
        from django.db.models.functions import Coalesce
        from django.utils import timezone
        from datetime import timedelta
        from decimal import Decimal
        
        # Get all orders with prefetch for better performance
        orders = Order.objects.select_related().prefetch_related('items').defer('client')  # Exclude client field to avoid client_id column error
        
        # Channel distribution - only count orders with valid channels
        channel_distribution = orders.exclude(
            Q(channel__isnull=True) | Q(channel='')
        ).values('channel').annotate(
            count=Count('id', distinct=True)
        )
        
        # Count unassigned orders separately
        unassigned_count = orders.filter(
            Q(channel__isnull=True) | Q(channel='')
        ).count()
        
        total_orders = orders.count()
        channel_dist = []
        
        # Process channel distribution
        for entry in channel_distribution:
            channel = entry['channel']
            count = entry['count'] or 0
            
            if channel and channel != '' and count > 0:
                percentage = (count / total_orders * 100) if total_orders > 0 else 0
                channel_dist.append({
                    'channel': channel,
                    'count': count,
                    'percentage': round(percentage, 2)
                })
        
        # Add unassigned channel if there are orders without channels
        if unassigned_count > 0:
            percentage = (unassigned_count / total_orders * 100) if total_orders > 0 else 0
            channel_dist.append({
                'channel': 'unassigned',
                'count': unassigned_count,
                'percentage': round(percentage, 2)
            })
        
        # Sort channels by count (descending) for better presentation
        channel_dist.sort(key=lambda x: x['count'], reverse=True)
        
        # Sales by salesperson - ensure we only count orders with items and valid sales data
        sales_by_salesperson = orders.exclude(
            Q(assigned_sales_person__isnull=True) | Q(assigned_sales_person='')
        ).annotate(
            total_aed=Coalesce(
                Sum('items__line_total', filter=Q(items__line_total__isnull=False)),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).filter(
            total_aed__gt=0  # Only include salespeople with actual sales
        ).values('assigned_sales_person').annotate(
            total_aed=Sum('items__line_total')
        ).order_by('-total_aed')
        
        sales_data = []
        for entry in sales_by_salesperson:
            total_aed = entry.get('total_aed') or Decimal('0.00')
            if total_aed > 0:
                sales_data.append({
                    'name': entry['assigned_sales_person'] or 'Unassigned',
                    'total_aed': float(total_aed)
                })
        
        # Daily trends (last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        daily_orders = orders.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('created_at__date', 'channel').annotate(
            count=Count('id', distinct=True)
        )
        
        # Collect all unique channels from the data (including unassigned)
        unique_channels = set()
        for entry in daily_orders:
            channel = entry['channel']
            if channel and channel != '':
                unique_channels.add(channel)
            else:
                unique_channels.add('unassigned')
        
        # Group by date
        trends_dict = {}
        for entry in daily_orders:
            date_str = entry['created_at__date'].strftime('%Y-%m-%d')
            channel = entry['channel'] or ''
            channel_key = channel if channel and channel != '' else 'unassigned'
            
            if date_str not in trends_dict:
                # Initialize with all unique channels found
                trends_dict[date_str] = {'date': date_str}
                for ch in unique_channels:
                    trends_dict[date_str][ch] = 0
            
            # Add count for this channel on this date
            if channel_key in trends_dict[date_str]:
                trends_dict[date_str][channel_key] = entry['count']
        
        daily_trends = list(trends_dict.values())
        daily_trends.sort(key=lambda x: x['date'])
        
        return Response({
            'channel_distribution': channel_dist,
            'sales_by_salesperson': sales_data,
            'daily_trends': daily_trends
        })


class TagAnalyticsView(APIView):
    """Tag analytics endpoint - aggregates by client profile_tag"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    
    @extend_schema(
        summary="Get Tag Analytics",
        description="Get analytics breakdown by client profile tags",
        responses={200: {
            'type': 'object',
            'properties': {
                'tag_distribution': {'type': 'array'},
                'revenue_by_tag': {'type': 'array'},
                'daily_trends': {'type': 'array'}
            }
        }}
    )
    
    def get(self, request):
        from django.db.models import Sum, Count, Q
        from django.utils import timezone
        from datetime import timedelta
        from clients.models import Client
        
        # Get date range from query params
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        orders = Order.objects.all()
        
        if start_date_str:
            try:
                from datetime import datetime
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date__gte=start_date)
            except ValueError:
                pass
        
        if end_date_str:
            try:
                from datetime import datetime
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                orders = orders.filter(created_at__date__lte=end_date)
            except ValueError:
                pass
        
        # Since orders don't directly link to clients, we'll use channel as a proxy
        # Map channel to profile_tag
        channel_to_tag = {
            'b2b_customers': 'b2b',
            'b2c_customers': 'b2c',
            'walk_in_orders': 'walk_in',
            'online_store': 'online',
            'salesperson_generated': None
        }
        
        # Tag distribution (using channel as proxy)
        channel_distribution = orders.values('channel').annotate(
            count=Count('id'),
            revenue=Sum('items__line_total')
        ).exclude(channel__isnull=True).exclude(channel='')
        
        total_orders = orders.count()
        tag_dist = []
        revenue_by_tag = []
        
        for entry in channel_distribution:
            channel = entry['channel']
            tag = channel_to_tag.get(channel)
            if tag:
                count = entry['count'] or 0
                percentage = (count / total_orders * 100) if total_orders > 0 else 0
                revenue = float(entry['revenue'] or 0)
                
                tag_dist.append({
                    'tag': tag,
                    'count': count,
                    'percentage': round(percentage, 2)
                })
                
                revenue_by_tag.append({
                    'tag': tag,
                    'revenue_aed': revenue
                })
        
        # Daily trends
        if not start_date_str or not end_date_str:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        daily_orders = orders.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('created_at__date', 'channel').annotate(
            count=Count('id')
        )
        
        # Group by date and tag
        trends_dict = {}
        for entry in daily_orders:
            date_str = entry['created_at__date'].strftime('%Y-%m-%d')
            channel = entry['channel']
            tag = channel_to_tag.get(channel, 'unknown')
            
            if date_str not in trends_dict:
                trends_dict[date_str] = {
                    'date': date_str,
                    'b2b': 0,
                    'b2c': 0,
                    'walk_in': 0,
                    'online': 0
                }
            
            if tag and tag in trends_dict[date_str]:
                trends_dict[date_str][tag] = entry['count']
        
        daily_trends = list(trends_dict.values())
        daily_trends.sort(key=lambda x: x['date'])
        
        return Response({
            'tag_distribution': tag_dist,
            'revenue_by_tag': revenue_by_tag,
            'daily_trends': daily_trends
        })

class QuotationView(APIView):
    """Dedicated view for quotation operations"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales']
    
    def get(self, request, order_id):
        """Get quotation for an order"""
        try:
            order = Order.objects.get(id=order_id)
            quotation, created = Quotation.objects.get_or_create(order=order)
            
            serializer = QuotationSerializer(quotation)
            return Response({
                'ok': True,
                'data': serializer.data
            })
        except Order.DoesNotExist:
            return Response({
                'ok': False,
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'ok': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, order_id):
        """Update quotation for an order"""
        try:
            order = Order.objects.get(id=order_id)
            quotation, created = Quotation.objects.get_or_create(order=order)
            
            # Validate and update quotation fields
            serializer = QuotationSerializer(quotation, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                # Update the quotation
                quotation = serializer.save()
                
                # Only recalculate totals if grand_total or finalPrice was not manually set
                if 'grand_total' not in request.data and 'finalPrice' not in request.data:
                    quotation.calculate_totals()
                    quotation.save()
                else:
                    # If grand_total or finalPrice was manually set, use that value and save without recalculating
                    if 'finalPrice' in request.data:
                        quotation.grand_total = Decimal(str(request.data['finalPrice']))
                    elif 'grand_total' in request.data:
                        quotation.grand_total = Decimal(str(request.data['grand_total']))
                    quotation.save(skip_calculation=True)
                
                # Don't change order stage/status when updating quotations
                # This allows quotations to be updated without affecting order workflow
            
            return Response({
                'ok': True,
                'data': QuotationSerializer(quotation).data
            })
        except Order.DoesNotExist:
            return Response({
                'ok': False,
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'ok': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductImageServeView(APIView):
    """
    Serve product images securely through endpoint
    Features:
    - Access control by role
    - Proper headers for image preview
    - Cache control
    """
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery']
    
    @extend_schema(
        summary="Serve Product Image",
        description="Securely serve product images with access control",
        responses={
            200: {'image_served': 'success'},
            404: {'error': 'Image not found'},
            403: {'error': 'Access denied'}
        }
    )
    def get(self, request, order_id, item_id):
        """Serve product image with security check"""
        try:
            order = Order.objects.get(id=order_id)
            order_item = OrderItem.objects.get(id=item_id, order_id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except OrderItem.DoesNotExist:
            return Response({'error': 'Order item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if item has an image_url
        if not order_item.image_url:
            return Response({'error': 'No image URL for this item'}, status=status.HTTP_404_NOT_FOUND)
        
        # Extract file path from image_url
        # Handle both /media/product_images/... and product_images/... formats
        image_url = order_item.image_url
        if image_url.startswith('/media/'):
            file_path = image_url[len('/media/'):]
        elif image_url.startswith('product_images/'):
            file_path = image_url
        elif image_url.startswith('http://') or image_url.startswith('https://'):
            # External URL - redirect to it
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(image_url)
        else:
            # Try to extract path from URL
            if '/product_images/' in image_url:
                file_path = image_url.split('/product_images/')[1]
                file_path = f'product_images/{file_path}'
            else:
                return Response({'error': 'Invalid image URL format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Serve file securely
        try:
            if default_storage.exists(file_path):
                # Open file from storage
                file_content = default_storage.open(file_path, 'rb')
                
                # Determine content type from file extension
                import mimetypes
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type or not content_type.startswith('image/'):
                    content_type = 'image/jpeg'  # Default fallback
                
                # Create response with proper headers for image preview
                from django.http import FileResponse
                response = FileResponse(
                    file_content,
                    content_type=content_type
                )
                
                # Set headers to allow browser preview
                response['Content-Disposition'] = 'inline'
                response['Cache-Control'] = 'public, max-age=3600'
                
                return response
            else:
                # Try alternative path if file.name is a full path
                if hasattr(order_item, 'image_path'):
                    try:
                        import os
                        alt_path = order_item.image_path
                        if os.path.exists(alt_path):
                            with open(alt_path, 'rb') as f:
                                import mimetypes
                                content_type, _ = mimetypes.guess_type(alt_path)
                                if not content_type or not content_type.startswith('image/'):
                                    content_type = 'image/jpeg'
                                from django.http import FileResponse
                                response = FileResponse(f, content_type=content_type)
                                response['Content-Disposition'] = 'inline'
                                response['Cache-Control'] = 'public, max-age=3600'
                                return response
                    except Exception:
                        pass
                
                return Response({'error': 'Image not found on storage'}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({'error': f'Image serving error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
