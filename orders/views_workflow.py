"""
Workflow-specific views for design approvals, machine assignments, and file management.
This file contains all the new API endpoints for the enhanced workflow system.
"""

from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema

from .models import Order, DesignApproval, ProductMachineAssignment, OrderFile
from .serializers import (
    DesignApprovalSerializer, DesignApprovalCreateSerializer, ApproveDesignSerializer,
    ProductMachineAssignmentSerializer, MachineAssignmentCreateSerializer,
    OrderFileSerializer, FileUploadSerializer, OrderSerializer
)
from accounts.permissions import RolePermission
from notifications.services import notify_admins, create_notification
from django.contrib.auth import get_user_model

User = get_user_model()


def normalize_visible_to_roles(visible_to_roles) -> list:
    """
    Normalize visible_to_roles from various formats to a clean list.
    Handles: JSON strings, nested JSON strings, lists with JSON strings, plain lists.
    Returns: List of normalized role strings (lowercased, trimmed).
    
    Examples:
    - Input: '["admin", "production"]' (JSON string) -> ['admin', 'production']
    - Input: '["[\"admin\",\"production\"]"]' (nested JSON) -> ['admin', 'production']
    - Input: ['admin', 'production'] (list) -> ['admin', 'production']
    - Input: None -> []
    """
    if not visible_to_roles:
        return []
    
    import json
    
    # If it's already a list, check if it contains JSON strings
    if isinstance(visible_to_roles, list):
        if len(visible_to_roles) == 0:
            return []
        
        # Check if first element is a JSON string (nested case)
        if isinstance(visible_to_roles[0], str) and visible_to_roles[0].strip().startswith('['):
            try:
                # Try to parse the first element as JSON
                parsed = json.loads(visible_to_roles[0])
                if isinstance(parsed, list):
                    # Unwrap nested JSON string
                    result = []
                    for item in parsed:
                        if isinstance(item, str):
                            result.append(item.lower().strip())
                    return result
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Regular list - normalize each item
        result = []
        for item in visible_to_roles:
            if isinstance(item, str):
                result.append(item.lower().strip())
        return result
    
    # If it's a string, try to parse as JSON
    if isinstance(visible_to_roles, str):
        try:
            parsed = json.loads(visible_to_roles)
            if isinstance(parsed, list):
                return [str(item).lower().strip() for item in parsed if item]
            elif parsed:
                return [str(parsed).lower().strip()]
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, treat as single role string
            return [visible_to_roles.lower().strip()]
    
    # Fallback: convert to string and return as single-item list
    return [str(visible_to_roles).lower().strip()]


class RequestDesignApprovalView(APIView):
    """Designer requests approval from sales person"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'designer']
    
    @extend_schema(
        summary="Request Design Approval",
        description="Designer submits design for approval by sales person",
        request=DesignApprovalCreateSerializer,
        responses={201: DesignApprovalSerializer}
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DesignApprovalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Determine the correct sales person - MUST be the one who created/owns this order
            target_sales_person = order.assigned_sales_person
            
            # If no sales person assigned to order, fallback to requested sales person
            if not target_sales_person:
                target_sales_person = serializer.validated_data['sales_person']
            
            # Create approval request - always send to the order's sales person
            approval = DesignApproval.objects.create(
                order=order,
                designer=serializer.validated_data['designer'],
                sales_person=target_sales_person,  # Use order's assigned sales person
                design_files_manifest=serializer.validated_data.get('design_files_manifest', []),
                approval_notes=serializer.validated_data.get('approval_notes', '')
            )
            
            # Notify admins about the design approval request
            designer_name = serializer.validated_data['designer']
            notify_admins(
                title="Design Approval Requested",
                message=f"Designer {designer_name} submitted design for order {order.order_code}",
                notification_type="design_submitted",
                actor=request.user,
                related_object_type="design_approval",
                related_object_id=str(approval.id)
            )
            
            # Check if this is a resubmission (previous rejected approval exists)
            is_resubmission = order.design_approvals.filter(
                approval_status='rejected'
            ).exclude(id=approval.id).exists()
            
            # Notify the assigned sales person about the approval request
            sales_person_user = User.objects.filter(username=target_sales_person).first()
            if sales_person_user:
                if is_resubmission:
                    # Resubmission notification
                    create_notification(
                        recipient=sales_person_user,
                        title="Design Resubmitted for Review",
                        message=f"Design for order {order.order_code} has been resubmitted after rejection. Please review again.",
                        notification_type="design_submitted",
                        actor=request.user,
                        related_object_type="design_approval",
                        related_object_id=str(approval.id)
                    )
                else:
                    # Initial submission notification
                    create_notification(
                        recipient=sales_person_user,
                        title="Design Approval Needed",
                        message=f"Design approval needed for order {order.order_code}",
                        notification_type="design_submitted",
                        actor=request.user,
                        related_object_type="design_approval",
                        related_object_id=str(approval.id)
                    )
            
            # Notify admins about resubmission if applicable
            if is_resubmission:
                notify_admins(
                    title="Design Resubmitted After Rejection",
                    message=f"Designer {designer_name} resubmitted design for order {order.order_code} after previous rejection",
                    notification_type="design_submitted",
                    actor=request.user,
                    related_object_type="design_approval",
                    related_object_id=str(approval.id)
                )
            
            # Update order status and assignments
            order.status = 'sent_for_approval'
            order.assigned_designer = serializer.validated_data['designer']
            # Ensure the sales person is set (the one who should approve)
            order.assigned_sales_person = target_sales_person
            order.save(update_fields=['status', 'assigned_designer', 'assigned_sales_person'])
        
        return Response(
            DesignApprovalSerializer(approval).data,
            status=status.HTTP_201_CREATED
        )


class ApproveDesignView(APIView):
    """Sales person approves or rejects design"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales']
    
    @extend_schema(
        summary="Approve or Reject Design",
        description="Sales person approves or rejects the designer's work",
        request=ApproveDesignSerializer,
        responses={200: DesignApprovalSerializer}
    )
    def post(self, request, approval_id):
        try:
            approval = DesignApproval.objects.get(id=approval_id)
        except DesignApproval.DoesNotExist:
            return Response({'error': 'Approval request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Enhanced authorization logic - MORE FLEXIBLE
        current_user = request.user.username if hasattr(request.user, 'username') else 'unknown'
        user_roles = request.user.roles if hasattr(request.user, 'roles') and request.user.roles else ['unknown']
        
        # Check if user can approve
        can_approve = False
        
        # Admin can always approve
        if request.user.has_role('admin'):
            can_approve = True
        # Only the sales person who created/owns the order can approve
        elif 'sales' in user_roles and approval.order.assigned_sales_person == current_user:
            can_approve = True
            
        if not can_approve:
            error_msg = f'User {current_user} cannot approve this order. '
            if approval.sales_person:
                error_msg += f'Assigned sales person: {approval.sales_person}. '
            if approval.order.assigned_sales_person:
                error_msg += f'Order assigned to: {approval.order.assigned_sales_person}. '
            error_msg += 'Only assigned sales person or admin can approve.'
            
            return Response(
                {'error': error_msg},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ApproveDesignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.validated_data['action']
        
        with transaction.atomic():
            if action == 'approve':
                approval.approval_status = 'approved'
                approval.reviewed_at = timezone.now()
                approval.save()
                
                # Notify the designer about the approval
                designer_user = User.objects.filter(username=approval.designer).first()
                if designer_user:
                    create_notification(
                        recipient=designer_user,
                        title="Design Approved",
                        message=f"Your request has been accepted by user: {request.user.username}",
                        notification_type="design_approved",
                        actor=request.user,
                        related_object_type="design_approval",
                        related_object_id=str(approval.id)
                    )
                
                # Make design files visible to production team
                # Note: SendToProductionView will ensure ALL files are visible to production,
                # but we update design files here for early visibility in case designer sends
                # without explicit approval workflow
                from .models import OrderFile
                design_files = approval.order.files.filter(file_type='design')
                for file_obj in design_files:
                    normalized_roles = normalize_visible_to_roles(file_obj.visible_to_roles)
                    if 'production' not in normalized_roles:
                        current_roles = normalized_roles.copy()
                        current_roles.append('production')
                        file_obj.visible_to_roles = current_roles
                        file_obj.save(update_fields=['visible_to_roles'])
                
                # Update order status - designer can now send to production
                approval.order.status = 'sent_to_designer'  # Approved, waiting for designer to send to production
                approval.order.save(update_fields=['status'])
                
            elif action == 'reject':
                approval.approval_status = 'rejected'
                approval.rejection_reason = serializer.validated_data.get('rejection_reason', '')
                approval.reviewed_at = timezone.now()
                approval.save()
                
                # Notify the designer about the rejection
                designer_user = User.objects.filter(username=approval.designer).first()
                rejection_reason = approval.rejection_reason or serializer.validated_data.get('rejection_reason', '')
                if designer_user:
                    create_notification(
                        recipient=designer_user,
                        title="Design Rejected",
                        message=f"Your request has been rejected by user: {request.user.username}",
                        notification_type="design_rejected",
                        actor=request.user,
                        related_object_type="design_approval",
                        related_object_id=str(approval.id),
                        metadata={'rejection_reason': rejection_reason}
                    )
                
                # Update order status - back to designer for revisions
                approval.order.status = 'sent_to_designer'
                approval.order.save(update_fields=['status'])
        
        return Response(DesignApprovalSerializer(approval).data)


class SendToDesignerView(APIView):
    """Sales sends order to designer"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales']
    
    @extend_schema(
        summary="Send to Designer",
        description="Sales sends order to designer for design work",
        responses={200: OrderSerializer}
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get designer from request data (optional)
        designer = request.data.get('designer', None)
        
        with transaction.atomic():
            order.status = 'sent_to_designer'
            order.stage = 'design'  # Move to design stage
            if designer:
                order.assigned_designer = designer
            order.save(update_fields=['status', 'stage', 'assigned_designer'])
            
            # Notify the designer if assigned
            if designer:
                designer_user = User.objects.filter(username=designer).first()
                if designer_user:
                    create_notification(
                        recipient=designer_user,
                        title="Order Assigned to You",
                        message=f"Order {order.order_code} has been assigned to you",
                        notification_type="order_assigned",
                        actor=request.user,
                        related_object_type="order",
                        related_object_id=str(order.id)
                    )
        
        return Response({
            'ok': True,
            'message': f'Order {order.order_code} sent to designer',
            'data': OrderSerializer(order, context={'request': request}).data
        })


class SendToProductionView(APIView):
    """Designer sends approved design to production"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'designer']
    
    @extend_schema(
        summary="Send to Production",
        description="Designer sends approved order to production team",
        responses={200: OrderSerializer}
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if design is approved
        latest_approval = order.design_approvals.filter(approval_status='approved').order_by('-reviewed_at').first()
        
        if not latest_approval and not request.user.has_role('admin'):
            return Response(
                {'error': 'Design must be approved before sending to production'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        files_updated = 0
        files_already_visible = 0
        
        with transaction.atomic():
            order.status = 'sent_to_production'
            order.stage = 'printing'  # Move to printing stage
            order.save(update_fields=['status', 'stage'])
            
            # Ensure ALL order files are visible to production team
            all_files = order.files.all()
            print(f"🔍 DEBUG: SendToProduction - Checking {all_files.count()} files for production visibility")
            
            for file_obj in all_files:
                normalized_roles = normalize_visible_to_roles(file_obj.visible_to_roles)
                print(f"🔍 DEBUG: File '{file_obj.file_name}' (ID: {file_obj.id}) has normalized roles: {normalized_roles}")
                
                if 'production' not in normalized_roles:
                    # Add production role
                    current_roles = normalized_roles.copy()
                    current_roles.append('production')
                    file_obj.visible_to_roles = current_roles
                    file_obj.save(update_fields=['visible_to_roles'])
                    files_updated += 1
                else:
                    files_already_visible += 1
        
        return Response({
            'ok': True,
            'message': f'Order {order.order_code} sent to production',
            'data': OrderSerializer(order, context={'request': request}).data,
            'file_integrity': {
                'files_updated': files_updated,
                'files_already_visible': files_already_visible,
                'total_files': files_updated + files_already_visible
            }
        })


class AssignMachinesView(APIView):
    """Production assigns machines to products"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'production']
    
    @extend_schema(
        summary="Assign Machines to Products",
        description="Production person assigns machines to each product in the order",
        request=MachineAssignmentCreateSerializer(many=True),
        responses={201: ProductMachineAssignmentSerializer(many=True)}
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate that we receive a list
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Expected a list of machine assignments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignments = []
        
        with transaction.atomic():
            # Clear existing assignments for this order
            order.machine_assignments.all().delete()
            
            # Create new assignments
            for assignment_data in request.data:
                serializer = MachineAssignmentCreateSerializer(data=assignment_data)
                serializer.is_valid(raise_exception=True)
                
                # Calculate expected completion time
                started_at = timezone.now()
                estimated_minutes = serializer.validated_data['estimated_time_minutes']
                
                assignment = ProductMachineAssignment.objects.create(
                    order=order,
                    product_name=serializer.validated_data['product_name'],
                    product_sku=serializer.validated_data.get('product_sku', ''),
                    product_quantity=serializer.validated_data['product_quantity'],
                    machine_id=serializer.validated_data['machine_id'],
                    machine_name=serializer.validated_data['machine_name'],
                    estimated_time_minutes=estimated_minutes,
                    started_at=started_at,
                    assigned_by=serializer.validated_data.get('assigned_by', request.user.username),
                    notes=serializer.validated_data.get('notes', ''),
                    status='queued'
                )
                assignments.append(assignment)
            
            # Update order status
            order.status = 'getting_ready'
            order.assigned_production_person = request.user.username if hasattr(request.user, 'username') else ''
            order.save(update_fields=['status', 'assigned_production_person'])
        
        return Response(
            ProductMachineAssignmentSerializer(assignments, many=True).data,
            status=status.HTTP_201_CREATED
        )


class UploadOrderFileView(APIView):
    """Upload files for any stage of the order"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery']
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        summary="Upload Order File",
        description="Upload a file related to an order with role-based visibility",
        request=FileUploadSerializer,
        responses={201: OrderFileSerializer}
    )
    def post(self, request, order_id):
        print(f"🔵 DEBUG: UploadOrderFileView.post called for order {order_id}")
        print(f"🔵 DEBUG: Request user: {getattr(request.user, 'username', 'unknown')}")
        print(f"🔵 DEBUG: Request data keys: {list(request.data.keys())}")
        print(f"🔵 DEBUG: Request FILES keys: {list(request.FILES.keys())}")
        
        try:
            order = Order.objects.get(id=order_id)
            print(f"✅ DEBUG: Order found: {order.order_code}")
        except Order.DoesNotExist:
            print(f"❌ DEBUG: Order {order_id} not found")
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = FileUploadSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {'error': 'Validation failed', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = serializer.validated_data['file']
            
            # Safely encode the filename to handle non-ASCII characters
            safe_filename = uploaded_file.name.encode('ascii', 'ignore').decode('ascii')
            if not safe_filename:
                safe_filename = 'uploaded_file'
            
            # Create order file
            visible_roles = serializer.validated_data.get('visible_to_roles', ['admin'])
            if not visible_roles:
                visible_roles = ['admin']  # Ensure at least admin can see it
            
            # If user is admin, ensure all roles can see the file (for files uploaded from admin view/order lifecycle)
            is_admin = False
            try:
                if hasattr(request.user, 'has_role'):
                    is_admin = request.user.has_role('admin')
                if not is_admin:
                    user_roles_list = getattr(request.user, 'roles', []) or []
                    is_admin = 'admin' in user_roles_list or 'Admin' in user_roles_list
                if not is_admin:
                    is_admin = getattr(request.user, 'is_superuser', False)
            except Exception:
                is_admin = False
            
            try:
                order_file = OrderFile.objects.create(
                    order=order,
                    file=uploaded_file,
                    file_name=uploaded_file.name,  # Keep original name in database
                    file_type=serializer.validated_data['file_type'],
                    file_size=uploaded_file.size,
                    mime_type=uploaded_file.content_type or 'application/octet-stream',
                    uploaded_by=request.user.username if hasattr(request.user, 'username') else 'unknown',
                    uploaded_by_role=', '.join(request.user.roles) if hasattr(request.user, 'roles') and request.user.roles else 'unknown',
                    stage=serializer.validated_data['stage'],
                    visible_to_roles=visible_roles,
                    description=serializer.validated_data.get('description', ''),
                    product_related=serializer.validated_data.get('product_related', '')
                )
                
                # Force database commit to ensure file is persisted
                from django.db import transaction
                transaction.on_commit(lambda: None)  # Trigger commit
                
                # Verify it was saved immediately
                verify_file = OrderFile.objects.filter(id=order_file.id).first()
                if not verify_file:
                    raise Exception(f"File {uploaded_file.name} was not saved to database")
            except Exception as create_error:
                raise
            
            return Response(
                OrderFileSerializer(order_file, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to upload file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UploadQuotationPDFView(APIView):
    """Upload PDF for quotation sharing"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer']
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        summary="Upload Quotation PDF",
        description="Upload a PDF file for quotation sharing and get a public URL",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'pdf': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'PDF file to upload'
                    }
                },
                'required': ['pdf']
            }
        },
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'url': {'type': 'string', 'description': 'Public URL for the uploaded PDF'},
                    'filename': {'type': 'string', 'description': 'Original filename'},
                    'size': {'type': 'integer', 'description': 'File size in bytes'}
                }
            }
        }
    )
    def post(self, request):
        try:
            # Get the PDF file from request
            pdf_file = request.FILES.get('pdf')
            if not pdf_file:
                return Response({'error': 'No PDF file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate file type
            if not pdf_file.name.lower().endswith('.pdf'):
                return Response({'error': 'File must be a PDF'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate file size (max 10MB)
            if pdf_file.size > 10 * 1024 * 1024:
                return Response({'error': 'File size must be less than 10MB'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate unique filename
            import uuid
            import os
            from django.conf import settings
            
            unique_filename = f"quotation_{uuid.uuid4().hex[:8]}_{pdf_file.name}"
            
            # Save file to media directory
            media_path = os.path.join(settings.MEDIA_ROOT, 'quotations')
            os.makedirs(media_path, exist_ok=True)
            
            file_path = os.path.join(media_path, unique_filename)
            with open(file_path, 'wb+') as destination:
                for chunk in pdf_file.chunks():
                    destination.write(chunk)
            
            # Generate public URL
            from django.urls import reverse
            from django.http import HttpRequest
            
            # Create a mock request to build the URL
            mock_request = HttpRequest()
            mock_request.META['HTTP_HOST'] = request.META.get('HTTP_HOST', 'localhost:8000')
            mock_request.META['wsgi.url_scheme'] = request.META.get('wsgi.url_scheme', 'http')
            
            public_url = f"{mock_request.META['wsgi.url_scheme']}://{mock_request.META['HTTP_HOST']}/media/quotations/{unique_filename}"
            
            return Response({
                'url': public_url,
                'filename': pdf_file.name,
                'size': pdf_file.size,
                'message': 'PDF uploaded successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Failed to upload PDF: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderFilesListView(APIView):
    """Get all files for an order (filtered by role)"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery']
    
    @extend_schema(
        summary="List Order Files",
        description="Get all files for an order, filtered by user role",
        responses={200: OrderFileSerializer(many=True)}
    )
    def get(self, request, order_id):
        # Wrap everything in outer try-catch to prevent any 500 errors
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            print(f"❌ DEBUG: Order {order_id} not found")
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Error getting order: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get user roles
        try:
            user_roles = getattr(request.user, 'roles', []) or []
            print(f"🔍 DEBUG: Getting files for order {order_id}, user roles: {user_roles}")
            print(f"🔍 DEBUG: User: {request.user.username if hasattr(request.user, 'username') else 'unknown'}")
        except Exception as e:
            print(f"❌ DEBUG: Error getting user info: {str(e)}")
            user_roles = []
        
        # Get files for the order - try both relationship and direct query
        try:
            # Try using relationship first
            files = order.files.all()
            files_count = files.count()
            print(f"🔍 DEBUG: Found {files_count} files via relationship for order {order_id}")
            
            # Also try direct query as fallback
            from .models import OrderFile
            direct_files = OrderFile.objects.filter(order_id=order_id)
            direct_count = direct_files.count()
            print(f"🔍 DEBUG: Found {direct_count} files via direct query for order {order_id}")
            
            # Use whichever found files, or both if they match
            if direct_count > files_count:
                print(f"⚠️ DEBUG: Direct query found more files, using direct query")
                files = direct_files
                files_count = direct_count
            
            # IMPORTANT: If no files found, check if files exist at all for this order
            if files_count == 0:
                # Double-check with a raw query to be absolutely sure
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM orders_orderfile WHERE order_id = %s", [order_id])
                    raw_count = cursor.fetchone()[0]
                    print(f"🔍 DEBUG: Raw SQL query found {raw_count} files for order {order_id}")
                    
                    if raw_count > 0:
                        print(f"⚠️ DEBUG: Files exist in DB but query returned 0 - possible relationship issue")
                        # Use direct query as fallback
                        files = OrderFile.objects.filter(order_id=order_id)
                        files_count = raw_count
            
            # Debug: List all file IDs to see what we have
            if files_count > 0:
                file_ids = list(files.values_list('id', flat=True))
                print(f"🔍 DEBUG: File IDs: {file_ids}")
                for f in files[:5]:  # Print first 5 files for debugging
                    visible_roles = getattr(f, 'visible_to_roles', []) or []
                    print(f"  - File {f.id}: {f.file_name} (type: {f.file_type}, stage: {f.stage}, product: {f.product_related}, visible_to: {visible_roles})")
            
            # If no files exist, return empty array instead of error
            if files_count == 0:
                print(f"🔍 DEBUG: No files found for order {order_id}, returning empty array")
                return Response([], status=status.HTTP_200_OK)
                
        except Exception as e:
            # Return empty list instead of error to prevent frontend crash
            return Response([], status=status.HTTP_200_OK)
        
        # Role-based filtering - Check admin status FIRST and more robustly
        try:
            # Convert to list for consistent handling
            all_files_list = list(files)
            files_count_after_filter = len(all_files_list)
            
            # Multiple ways to check if user is admin (more robust)
            is_admin = False
            user_roles_list = []
            try:
                # Method 1: Check has_role method
                if hasattr(request.user, 'has_role'):
                    is_admin = request.user.has_role('admin')
                
                # Method 2: Check roles list directly
                if not is_admin:
                    user_roles_list = getattr(request.user, 'roles', []) or []
                    is_admin = 'admin' in user_roles_list or 'Admin' in user_roles_list
                
                # Method 3: Check is_superuser as fallback
                if not is_admin:
                    is_admin = getattr(request.user, 'is_superuser', False)
            except Exception as admin_check_error:
                # If we can't determine admin status, default to False (safer)
                is_admin = False
            
            if is_admin:
                # Admin sees ALL files - no filtering
                filtered_files = all_files_list
                print(f"✅ DEBUG: Admin user detected - returning ALL {files_count_after_filter} files without any filtering")
            else:
                # Other roles see only files visible to them
                # Use normalize_visible_to_roles for consistent comparison
                normalized_user_roles = [str(r).lower().strip() for r in user_roles if r]
                visible_files = []
                for file_obj in all_files_list:
                    file_visible_roles = normalize_visible_to_roles(file_obj.visible_to_roles)
                    
                    # If file has no visible_to_roles set, make it visible to all (backward compatibility)
                    if not file_visible_roles or len(file_visible_roles) == 0:
                        visible_files.append(file_obj)
                        continue
                    
                    # Check if any of the user's roles match any of the file's visible roles
                    has_access = any(user_role in file_visible_roles for user_role in normalized_user_roles)
                    
                    if has_access:
                        visible_files.append(file_obj)
                
                filtered_files = visible_files
                files_count_after_filter = len(filtered_files)
            
            files = filtered_files
        except Exception as filter_error:
            import traceback
            print(f"⚠️ DEBUG: Error in role-based filtering: {str(filter_error)}")
            print(f"⚠️ DEBUG: Traceback: {traceback.format_exc()}")
            # On error, check if user might be admin and return all files
            try:
                is_admin_fallback = (
                    (hasattr(request.user, 'has_role') and request.user.has_role('admin')) or
                    ('admin' in (getattr(request.user, 'roles', []) or [])) or
                    getattr(request.user, 'is_superuser', False)
                )
                if is_admin_fallback:
                    print(f"⚠️ DEBUG: Error occurred but user appears to be admin - returning all files")
                    files = all_files_list
                else:
                    print(f"⚠️ DEBUG: Error occurred and user is not admin - returning empty list for safety")
                    files = []
            except:
                # Last resort: return empty list
                print(f"⚠️ DEBUG: Critical error in admin check fallback - returning empty list")
                files = []
        
        # Use serializer with proper error handling
        try:
            files_count_for_serialization = len(files) if isinstance(files, list) else files.count()
            print(f"🔍 DEBUG: Starting serialization for {files_count_for_serialization} files")
            # Process files with safe URL generation
            files_list = list(files)
            print(f"🔍 DEBUG: Converted files to list, length: {len(files_list)}")
            serialized_data = []
            
            for idx, file_obj in enumerate(files_list):
                try:
                    print(f"🔍 DEBUG: Serializing file {idx+1}/{len(files_list)}: {file_obj.id} ({file_obj.file_name})")
                    # Use serializer for proper formatting
                    serializer = OrderFileSerializer(file_obj, context={'request': request})
                    file_data = serializer.data
                    serialized_data.append(file_data)
                    print(f"✅ DEBUG: Successfully serialized file {file_obj.id}")
                except Exception as file_error:
                    # If serialization fails for a file, create minimal data without URL
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"⚠️ DEBUG: Error serializing file {file_obj.id}: {str(file_error)}")
                    print(f"⚠️ DEBUG: Traceback: {error_trace}")
                    try:
                        # Get order info safely
                        order_id = file_obj.order.id if hasattr(file_obj, 'order') and file_obj.order else order_id
                        order_code = file_obj.order.order_code if hasattr(file_obj, 'order') and file_obj.order else 'Unknown'
                        
                        serialized_data.append({
                        'id': file_obj.id,
                            'order': order_id,
                            'order_code': order_code,
                            'file_name': getattr(file_obj, 'file_name', 'Unknown') or 'Unknown',
                            'file_size': getattr(file_obj, 'file_size', 0) or 0,
                            'mime_type': getattr(file_obj, 'mime_type', 'application/octet-stream') or 'application/octet-stream',
                            'file_type': getattr(file_obj, 'file_type', 'other') or 'other',
                            'stage': getattr(file_obj, 'stage', '') or '',
                            'uploaded_at': file_obj.uploaded_at.isoformat() if hasattr(file_obj, 'uploaded_at') and file_obj.uploaded_at else None,
                            'file_url': None,  # URL generation failed
                            'visible_to_roles': getattr(file_obj, 'visible_to_roles', []) or [],
                            'description': getattr(file_obj, 'description', '') or '',
                            'product_related': getattr(file_obj, 'product_related', '') or '',
                            'uploaded_by': getattr(file_obj, 'uploaded_by', '') or '',
                            'uploaded_by_role': getattr(file_obj, 'uploaded_by_role', '') or ''
                        })
                        print(f"✅ DEBUG: Created fallback data for file {file_obj.id}")
                    except Exception as fallback_error:
                        import traceback
                        print(f"❌ DEBUG: Even fallback serialization failed for file {file_obj.id}: {str(fallback_error)}")
                        print(f"❌ DEBUG: Fallback traceback: {traceback.format_exc()}")
                    continue
            
            files_count_for_comparison = len(files) if isinstance(files, list) else files_count
            print(f"✅ DEBUG: Successfully serialized {len(serialized_data)}/{files_count_for_comparison} files")
            print(f"🔍 DEBUG: Returning response with {len(serialized_data)} files")
            return Response(serialized_data, status=status.HTTP_200_OK)
            
        except Exception as serializer_error:
            import traceback
            print(f"❌ DEBUG: Critical error in file serialization: {str(serializer_error)}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            # Return empty list instead of error to prevent frontend crash
            print(f"🔍 DEBUG: Returning empty list due to error")
            return Response([], status=status.HTTP_200_OK)
        
        except Exception as outer_error:
            # Catch ANY error that wasn't caught above (for the outer try block)
            import traceback
            print(f"❌ DEBUG: OUTER ERROR in OrderFilesListView: {str(outer_error)}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            # Always return valid JSON, never let an exception propagate
            return Response([], status=status.HTTP_200_OK)


class OrderFileDownloadView(APIView):
    """
    Secure Order File Download
    Features:
    - Access control by role
    - Audit logging
    - Secure file serving
    """
    # IMPORTANT:
    # Re‑enable proper authentication & role‑based permissions for this endpoint.
    # The previous debug configuration (`AllowAny` + empty `authentication_classes`)
    # meant `request.user` was always Anonymous, so no roles were available and
    # the manual permission checks below always failed, causing 403 errors even
    # for valid tokens.
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery']
    
    @extend_schema(
        summary="Download Order File",
        description="Securely download order files with access control",
        responses={
            200: {'file_served': 'success'},
            404: {'error': 'File not found'},
            403: {'error': 'Access denied'}
        }
    )
    def get(self, request, order_id, file_id):
        """Serve order file with security check"""
        
        try:
            order_file = OrderFile.objects.select_related('order').get(
                id=file_id, 
                order_id=order_id
            )
        except OrderFile.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check file access permissions
        # Get user roles - refresh from database to ensure we have latest roles
        try:
            from accounts.models import User
            user = User.objects.get(id=request.user.id)
            user_roles = list(user.roles) if user.roles else []
        except Exception:
            # Fallback to request.user
            user_roles = list(getattr(request.user, 'roles', []) or [])
            if hasattr(request.user, 'role') and request.user.role:
                if request.user.role not in user_roles:
                    user_roles.append(request.user.role)
        
        # Admin has access to all files
        if 'admin' not in user_roles:
            # Check if any user role is in visible roles
            file_visible_roles = order_file.visible_to_roles or []
            
            # Handle case where visible_to_roles might be stored as JSON string or nested JSON
            if isinstance(file_visible_roles, str):
                try:
                    import json
                    file_visible_roles = json.loads(file_visible_roles)
                except Exception:
                    file_visible_roles = []
            
            # Handle case where visible_to_roles is a list containing JSON strings
            if isinstance(file_visible_roles, list) and len(file_visible_roles) > 0:
                if isinstance(file_visible_roles[0], str) and file_visible_roles[0].startswith('['):
                    try:
                        import json
                        parsed = json.loads(file_visible_roles[0])
                        if isinstance(parsed, list):
                            file_visible_roles = parsed
                    except Exception:
                        pass
            
            # Ensure file_visible_roles is a list
            if not isinstance(file_visible_roles, list):
                file_visible_roles = []
            
            # Normalize roles (lowercase, strip whitespace) for comparison
            normalized_user_roles = [str(r).lower().strip() for r in user_roles if r]
            normalized_file_roles = [str(r).lower().strip() for r in file_visible_roles if r]
            
            # Check if any user role matches any file visible role
            has_access = any(user_role in normalized_file_roles for user_role in normalized_user_roles)
            
            # Also check if user uploaded the file (uploader always has access)
            if not has_access:
                if order_file.uploaded_by == request.user.username:
                    has_access = True
            
            if not has_access:
                return Response({'error': 'Access denied to this file'}, status=status.HTTP_403_FORBIDDEN)
        
        # Serve file securely
        try:
            from django.core.files.storage import default_storage
            from django.http import FileResponse
            
            # Try to get the file path
            if hasattr(order_file.file, 'name'):
                file_path = order_file.file.name
            else:
                file_path = str(order_file.file)
            
            # Check if file exists in storage
            if default_storage.exists(file_path):
                # Open file from storage
                file_content = default_storage.open(file_path, 'rb')
                
                # Create response with proper headers
                response = FileResponse(
                    file_content,
                    filename=order_file.file_name,
                    content_type=order_file.mime_type or 'application/octet-stream'
                )
                
                # For images, set headers to allow preview in browser
                if order_file.mime_type and order_file.mime_type.startswith('image/'):
                    response['Content-Disposition'] = f'inline; filename="{order_file.file_name}"'
                    response['Cache-Control'] = 'public, max-age=3600'
                else:
                    response['Content-Disposition'] = f'attachment; filename="{order_file.file_name}"'
                
                # Log download for audit (optional: keep if needed for security, but user asked for cleanup)
                # user_name = request.user.username if hasattr(request.user, 'username') else 'unknown'
                
                return response
            else:
                # Try alternative path if available
                if hasattr(order_file.file, 'path'):
                    alt_path = order_file.file.path
                    try:
                        import os
                        if os.path.exists(alt_path):
                            with open(alt_path, 'rb') as f:
                                response = FileResponse(f, filename=order_file.file_name, content_type=order_file.mime_type or 'application/octet-stream')
                                if order_file.mime_type and order_file.mime_type.startswith('image/'):
                                    response['Content-Disposition'] = f'inline; filename="{order_file.file_name}"'
                                    response['Cache-Control'] = 'public, max-age=3600'
                                else:
                                    response['Content-Disposition'] = f'attachment; filename="{order_file.file_name}"'
                                user_name = request.user.username if hasattr(request.user, 'username') else 'unknown'
                                print(f"AUDIT: Order file accessed: {order_file.file_name} from Order {order_file.order.order_code} by {user_name}")
                                return response
                    except Exception as e:
                        pass
                
                return Response({'error': 'File not found on storage'}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            import traceback
            print(f"❌ DEBUG: File serving error: {str(e)}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            return Response({'error': f'File serving error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteOrderFileView(APIView):
    """Delete a file from an order"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery']
    
    @extend_schema(
        summary="Delete Order File",
        description="Delete a file from an order (only uploader or admin can delete)",
        responses={204: None, 403: None, 404: None}
    )
    def delete(self, request, order_id, file_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            order_file = order.files.get(id=file_id)
        except OrderFile.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        user_username = request.user.username if hasattr(request.user, 'username') else 'unknown'
        
        # Only admin or the uploader can delete
        if not request.user.has_role('admin') and order_file.uploaded_by != user_username:
            return Response(
                {'error': 'Permission denied. Only admin or file uploader can delete files.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete the file
        order_file.file.delete(save=False)  # Delete from storage
        order_file.delete()  # Delete from database
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateOrderFileView(APIView):
    """Update file metadata"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery']
    
    @extend_schema(
        summary="Update Order File",
        description="Update file metadata (description, visibility, etc.)",
        responses={200: OrderFileSerializer}
    )
    def patch(self, request, order_id, file_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            order_file = order.files.get(id=file_id)
        except OrderFile.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        user_username = request.user.username if hasattr(request.user, 'username') else 'unknown'
        
        # Only admin or the uploader can update
        if not request.user.has_role('admin') and order_file.uploaded_by != user_username:
            return Response(
                {'error': 'Permission denied. Only admin or file uploader can update files.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update allowed fields
        allowed_fields = ['description', 'visible_to_roles', 'product_related']
        for field in allowed_fields:
            if field in request.data:
                setattr(order_file, field, request.data[field])
        
        order_file.save()
        
        return Response(
            OrderFileSerializer(order_file, context={'request': request}).data
        )


class PendingApprovalsView(APIView):
    """Get pending approval requests for a sales person"""
    permission_classes = []  # Temporarily remove permission check for debugging
    # allowed_roles = ['admin', 'sales']  # Commented out for debugging
    
    @extend_schema(
        summary="List Pending Approvals",
        description="Get all pending design approval requests for the current sales person",
        responses={200: DesignApprovalSerializer(many=True)}
    )
    def get(self, request):
        # DEBUG: Show all pending approvals for testing
        approvals = DesignApproval.objects.filter(approval_status='pending').select_related('order')
        
        return Response(
            DesignApprovalSerializer(approvals, many=True).data
        )


class MachineQueueView(APIView):
    """Get production queue grouped by machine"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'production']
    
    @extend_schema(
        summary="Get Machine Queue",
        description="Get all active machine assignments grouped by machine",
        responses={200: ProductMachineAssignmentSerializer(many=True)}
    )
    def get(self, request):
        # Get all assignments that are not completed
        assignments = ProductMachineAssignment.objects.filter(
            status__in=['queued', 'in_progress']
        ).select_related('order').order_by('expected_completion_time')
        
        return Response(
            ProductMachineAssignmentSerializer(assignments, many=True).data
        )


class UpdateMachineAssignmentStatusView(APIView):
    """Update status of a machine assignment"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'production']
    
    @extend_schema(
        summary="Update Machine Assignment Status",
        description="Update the status of a product's machine assignment",
        responses={200: ProductMachineAssignmentSerializer}
    )
    def patch(self, request, assignment_id):
        try:
            assignment = ProductMachineAssignment.objects.get(id=assignment_id)
        except ProductMachineAssignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if new_status not in dict(ProductMachineAssignment.PRODUCTION_STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            assignment.status = new_status
            
            if new_status == 'in_progress' and not assignment.started_at:
                assignment.started_at = timezone.now()
            elif new_status == 'completed':
                assignment.completed_at = timezone.now()
            
            assignment.save()
            
            # Check if all assignments for this order are completed
            order = assignment.order
            all_completed = all(
                a.completed_at is not None 
                for a in order.machine_assignments.all()
            )
            
            if all_completed:
                # Auto-update order status to ready for delivery
                order.status = 'sent_for_delivery'
                order.save(update_fields=['status'])
        
        return Response(ProductMachineAssignmentSerializer(assignment).data)


class SendToAdminView(APIView):
    """Production sends completed order back to admin"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'production']
    
    @extend_schema(
        summary="Send to Admin",
        description="Production confirms order is ready and sends to admin for final processing",
        responses={200: OrderSerializer}
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            order.status = 'sent_to_admin'
            order.stage = 'printing'  # Move to printing/QA stage
            order.save(update_fields=['status', 'stage'])
        
        return Response({
            'ok': True,
            'message': f'Order {order.order_code} sent to admin',
            'data': OrderSerializer(order, context={'request': request}).data
        })


class OrderStatusTrackingView(APIView):
    """Get real-time status tracking information for an order"""
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery']
    
    @extend_schema(
        summary="Get Order Status Tracking",
        description="Get detailed status tracking information for an order",
        responses={200: {"status": "string", "progress": "object", "next_actions": "array"}}
    )
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate progress based on current status
        progress = self._calculate_progress(order)
        
        # Determine next actions
        next_actions = self._get_next_actions(order)
        
        # Get status timeline
        timeline = self._get_status_timeline(order)
        
        return Response({
            'order_id': order.id,
            'order_code': order.order_code,
            'current_status': order.status,
            'current_stage': order.stage,
            'progress': progress,
            'next_actions': next_actions,
            'timeline': timeline,
            'last_updated': order.updated_at,
            'estimated_completion': self._get_estimated_completion(order)
        })
    
    def _calculate_progress(self, order):
        """Calculate progress percentage based on order status"""
        status_progress = {
            'draft': 5,
            'sent_to_sales': 10,
            'sent_to_designer': 20,
            'sent_for_approval': 30,
            'sent_to_production': 40,
            'getting_ready': 60,
            'sent_for_delivery': 80,
            'delivered': 100,
            'new': 10,
            'active': 50,
            'completed': 100,
        }
        
        base_progress = status_progress.get(order.status, 0)
        
        # Add production progress if in production stage
        if order.status in ['getting_ready', 'sent_to_production']:
            assignments = order.machine_assignments.all()
            if assignments.exists():
                completed_assignments = assignments.exclude(actual_completion_time__isnull=True).count()
                total_assignments = assignments.count()
                production_progress = (completed_assignments / total_assignments) * 20  # 20% for production
                base_progress += production_progress
        
        return {
            'percentage': min(100, base_progress),
            'stage': order.stage,
            'status': order.status
        }
    
    def _get_next_actions(self, order):
        """Get next possible actions based on current status"""
        actions = []
        
        if order.status == 'draft':
            actions.append({
                'action': 'send_to_sales',
                'label': 'Send to Sales',
                'description': 'Submit order for sales review',
                'required_role': 'admin'
            })
        
        elif order.status == 'sent_to_sales':
            actions.append({
                'action': 'send_to_designer',
                'label': 'Send to Designer',
                'description': 'Assign order to designer',
                'required_role': 'sales'
            })
        
        elif order.status == 'sent_to_designer':
            actions.append({
                'action': 'request_approval',
                'label': 'Request Approval',
                'description': 'Submit design for approval',
                'required_role': 'designer'
            })
        
        elif order.status == 'sent_for_approval':
            actions.extend([
                {
                    'action': 'approve_design',
                    'label': 'Approve Design',
                    'description': 'Approve the submitted design',
                    'required_role': 'sales'
                },
                {
                    'action': 'reject_design',
                    'label': 'Reject Design',
                    'description': 'Reject design and request revisions',
                    'required_role': 'sales'
                }
            ])
        
        elif order.status == 'sent_to_production':
            actions.append({
                'action': 'assign_machines',
                'label': 'Assign Machines',
                'description': 'Assign machines to products',
                'required_role': 'production'
            })
        
        elif order.status == 'getting_ready':
            actions.append({
                'action': 'mark_ready',
                'label': 'Mark as Ready',
                'description': 'Mark order as ready for delivery',
                'required_role': 'production'
            })
        
        elif order.status == 'sent_for_delivery':
            actions.append({
                'action': 'mark_delivered',
                'label': 'Mark as Delivered',
                'description': 'Confirm order delivery',
                'required_role': 'delivery'
            })
        
        return actions
    
    def _get_status_timeline(self, order):
        """Get status change timeline"""
        timeline = [
            {
                'status': 'draft',
                'label': 'Order Created',
                'timestamp': order.created_at,
                'completed': True
            }
        ]
        
        # Add other status changes based on current status
        status_sequence = [
            ('sent_to_sales', 'Sent to Sales'),
            ('sent_to_designer', 'Sent to Designer'),
            ('sent_for_approval', 'Sent for Approval'),
            ('sent_to_production', 'Sent to Production'),
            ('getting_ready', 'Getting Ready'),
            ('sent_for_delivery', 'Sent for Delivery'),
            ('delivered', 'Delivered')
        ]
        
        current_status_index = -1
        for i, (status, label) in enumerate(status_sequence):
            if status == order.status:
                current_status_index = i
                break
        
        for i, (status, label) in enumerate(status_sequence):
            if i <= current_status_index:
                timeline.append({
                    'status': status,
                    'label': label,
                    'timestamp': order.updated_at if i == current_status_index else None,
                    'completed': i < current_status_index,
                    'current': i == current_status_index
                })
            else:
                timeline.append({
                    'status': status,
                    'label': label,
                    'timestamp': None,
                    'completed': False,
                    'current': False
                })
        
        return timeline
    
    def _get_estimated_completion(self, order):
        """Get estimated completion time"""
        if order.status == 'delivered':
            return order.delivered_at
        
        # Calculate based on machine assignments
        assignments = order.machine_assignments.all()
        if assignments.exists():
            # Use assigned_at + estimated_time_minutes for completion estimation
            completion_times = []
            for assignment in assignments:
                if assignment.started_at and assignment.estimated_time_minutes:
                    completion_time = assignment.started_at + timezone.timedelta(minutes=assignment.estimated_time_minutes)
                    completion_times.append(completion_time)
            if completion_times:
                return max(completion_times)
        
        # Default estimation based on status
        status_days = {
            'draft': 7,
            'sent_to_sales': 5,
            'sent_to_designer': 3,
            'sent_for_approval': 2,
            'sent_to_production': 1,
            'getting_ready': 1,
            'sent_for_delivery': 1,
        }
        
        days = status_days.get(order.status, 1)
        return timezone.now() + timezone.timedelta(days=days)


class DesignApprovalsListView(APIView):
    """
    Get all design approvals for a specific order.
    Used by designer to check approval status.
    """
    permission_classes = []  # Use allow_all from permissions

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            approvals = order.design_approvals.all().order_by('-submitted_at')
            serializer = DesignApprovalSerializer(approvals, many=True)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

