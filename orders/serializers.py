from rest_framework import serializers
from decimal import Decimal
from .models import (
    Order, OrderItem, Quotation, DesignStage, PrintingStage, 
    ApprovalStage, DeliveryStage, Upload, DesignApproval,
    ProductMachineAssignment, OrderFile
)


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


class OrderItemSerializer(serializers.ModelSerializer):
    customRequirements = serializers.CharField(source='custom_requirements', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'name', 'sku', 'attributes', 
            'quantity', 'unit_price', 'line_total', 'custom_requirements', 'customRequirements',
            'design_ready', 'design_need_custom', 'design_files_manifest',
            'design_completed_at', 'design_commented_by', 'image_url'
        ]
        read_only_fields = ['id', 'line_total']
    
    def get_image_url(self, obj):
        """Get product image URL - returns secure endpoint URL for product images"""
        # First check if image_url is stored in the model (for new orders)
        if obj.image_url:
            request = self.context.get('request')
            
            # Check if this is a product image stored in our media (needs secure endpoint)
            if obj.image_url.startswith('/media/product_images/') or obj.image_url.startswith('product_images/'):
                # Return secure endpoint URL instead of direct media URL
                if request:
                    try:
                        # Get order_id from obj.order or obj.order_id
                        order_id = obj.order.id if hasattr(obj, 'order') and obj.order else getattr(obj, 'order_id', None)
                        if order_id:
                            secure_url = f'/api/orders/{order_id}/items/{obj.id}/product-image/'
                            return request.build_absolute_uri(secure_url)
                    except Exception:
                        pass
                # Fallback to relative URL if request context unavailable
                order_id = obj.order.id if hasattr(obj, 'order') and obj.order else getattr(obj, 'order_id', None)
                if order_id:
                    return f'/api/orders/{order_id}/items/{obj.id}/product-image/'
            
            # For external URLs (http:// or https://), return as-is
            if obj.image_url.startswith('http://') or obj.image_url.startswith('https://'):
                return obj.image_url
            
            # For other relative URLs, build absolute URI if request available
            if request:
                try:
                    return request.build_absolute_uri(obj.image_url) if obj.image_url.startswith('/') else obj.image_url
                except:
                    return obj.image_url
            
            return obj.image_url
        
        # For existing orders without image_url, return None
        # Frontend already handles this with a fallback icon
        return None


class OrderItemCreateSerializer(serializers.ModelSerializer):
    customRequirements = serializers.CharField(source='custom_requirements', required=False, allow_blank=True)
    image_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'product_id', 'name', 'sku', 'attributes', 'quantity', 'unit_price', 'line_total',
            'custom_requirements', 'customRequirements',
            'design_ready', 'design_need_custom', 'design_files_manifest',
            'design_completed_at', 'design_commented_by', 'image_url'
        ]
    
    def validate_image_url(self, value):
        """Validate image_url - allow both absolute and relative URLs."""
        if not value or value == '':
            return value
        
        # Allow relative URLs (starting with /)
        if value.startswith('/'):
            return value
        
        # For absolute URLs, validate they're proper URLs
        from urllib.parse import urlparse
        parsed = urlparse(value)
        if parsed.scheme and parsed.netloc:
            return value
        
        # If it's not a valid URL format, raise validation error
        raise serializers.ValidationError("Enter a valid URL.")
    
    def validate(self, attrs):
        # Log image_url for debugging
        if 'image_url' in attrs:
            print(f"🔍 DEBUG: OrderItemCreateSerializer - image_url in validated_data: {attrs.get('image_url')}")
        else:
            print(f"⚠️ DEBUG: OrderItemCreateSerializer - image_url NOT in validated_data")
        return attrs
    
    def validate_sku(self, value):
        """Truncate SKU if it exceeds maximum length"""
        if value and len(value) > 255:
            return value[:255]
        return value
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value
    
    def validate_design_files_manifest(self, value):
        """Validate that design files are mandatory for products requiring design"""
        # Check if this is a context where design files are required
        # Only enforce validation during design production or later stages
        order = self.context.get('order')
        if order:
            # Only require design files for design production stage and later
            design_required_stages = ['design_production', 'printing', 'approval', 'delivery', 'completed']
            if order.stage in design_required_stages:
                # Only require design files if the product actually needs custom design
                design_need_custom = self.initial_data.get('design_need_custom', False)
                if design_need_custom:
                    # Check both old and new file storage systems
                    has_old_files = value and len(value) > 0
                    has_new_files = False
                    
                    # Check if there are design files in the new OrderFile system
                    try:
                        from .models import OrderFile
                        product_id = self.initial_data.get('product_id')
                        if product_id:
                            has_new_files = OrderFile.objects.filter(
                                order=order,
                                file_type='design',
                                product_related__icontains=product_id
                            ).exists()
                        else:
                            # Check for any design files for this order
                            has_new_files = OrderFile.objects.filter(
                                order=order,
                                file_type='design'
                            ).exists()
                    except Exception:
                        pass
                    
                    if not has_old_files and not has_new_files:
                        raise serializers.ValidationError("Design files are mandatory for products that need custom design at this stage. Please upload at least one design file.")
        return value


class QuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = [
            'labour_cost', 'finishing_cost', 'paper_cost', 'machine_cost',
            'design_cost', 'delivery_cost', 'other_charges', 'discount',
            'advance_paid', 'quotation_notes', 'custom_field', 'sales_person',
            'products_subtotal', 'other_subtotal', 'subtotal', 'vat_3pct',
            'grand_total', 'remaining'
        ]


class DesignStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignStage
        fields = ['assigned_designer', 'requirements_files_manifest', 'design_status', 'internal_comments']


class PrintingStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintingStage
        fields = ['print_operator', 'print_time', 'batch_info', 'print_status', 'qa_checklist', 'printing_technique', 'colors_in_print']
    
    def validate_print_time(self, value):
        """Ensure print_time is timezone-aware"""
        from django.utils import timezone
        if value and timezone.is_naive(value):
            return timezone.make_aware(value)
        return value


class ApprovalStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalStage
        fields = ['client_approval_files', 'approved_at']


class DeliveryStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStage
        fields = ['rider_photo_path', 'delivered_at', 'delivery_option', 'expected_delivery_date']


class UploadSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Upload
        fields = ['id', 'kind', 'original_name', 'mime', 'size', 'url', 'created_at']
        read_only_fields = ['id', 'url', 'created_at']
    
    def get_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


# New serializers for workflow models

class DesignApprovalSerializer(serializers.ModelSerializer):
    """Serializer for design approval requests"""
    order_code = serializers.CharField(source='order.order_code', read_only=True)
    client_name = serializers.CharField(source='order.client_name', read_only=True)
    
    class Meta:
        model = DesignApproval
        fields = [
            'id', 'order', 'order_code', 'client_name',
            'designer', 'sales_person', 'approval_status',
            'design_files_manifest', 'approval_notes', 'rejection_reason',
            'submitted_at'
        ]
        read_only_fields = ['id', 'submitted_at']


class DesignApprovalCreateSerializer(serializers.Serializer):
    """Serializer for creating design approval requests"""
    designer = serializers.CharField()
    sales_person = serializers.CharField()
    design_files_manifest = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    approval_notes = serializers.CharField(required=False, allow_blank=True)


class ApproveDesignSerializer(serializers.Serializer):
    """Serializer for approving or rejecting designs"""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['action'] == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Rejection reason is required when rejecting a design'
            })
        return data


class ProductMachineAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for machine assignments"""
    order_code = serializers.CharField(source='order.order_code', read_only=True)
    
    class Meta:
        model = ProductMachineAssignment
        fields = [
            'id', 'order', 'order_code', 'product_name', 'product_sku',
            'product_quantity', 'machine_id', 'machine_name',
            'estimated_time_minutes', 'started_at', 'completed_at', 'status', 'assigned_by', 'notes'
        ]
        read_only_fields = ['id']


class MachineAssignmentCreateSerializer(serializers.Serializer):
    """Serializer for creating machine assignments"""
    product_name = serializers.CharField()
    product_sku = serializers.CharField(required=False, allow_blank=True)
    product_quantity = serializers.IntegerField(min_value=1)
    machine_id = serializers.CharField()
    machine_name = serializers.CharField()
    estimated_time_minutes = serializers.IntegerField(min_value=1)
    assigned_by = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class OrderFileSerializer(serializers.ModelSerializer):
    """Serializer for order files"""
    order_code = serializers.CharField(source='order.order_code', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderFile
        fields = [
            'id', 'order', 'order_code', 'file', 'file_url', 'file_name',
            'file_type', 'file_size', 'mime_type', 'uploaded_by',
            'uploaded_by_role', 'uploaded_at', 'stage', 'visible_to_roles',
            'description', 'product_related'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def to_representation(self, instance):
        """Ensure critical fields are never null/missing"""
        data = super().to_representation(instance)
        
        # Ensure file_name is always present
        if not data.get('file_name'):
            data['file_name'] = instance.file.name if instance.file else 'Unknown File'
            print(f"⚠️ DEBUG: File {instance.id} missing file_name, using fallback: {data['file_name']}")
        
        # Ensure file_size is always present (should not be None per model, but validate)
        if data.get('file_size') is None:
            data['file_size'] = instance.file.size if instance.file and hasattr(instance.file, 'size') else 0
            print(f"⚠️ DEBUG: File {instance.id} missing file_size, using fallback: {data['file_size']}")
        
        # file_url can be None for edge cases, which is handled by frontend
        # But log if it's missing when it shouldn't be
        if not data.get('file_url') and instance.file and instance.id and instance.order_id:
            print(f"⚠️ DEBUG: File {instance.id} missing file_url despite having file, id, and order_id")
        
        return data
    
    def get_file_url(self, obj):
        """Return secure download endpoint URL instead of direct media URL"""
        if not obj.file or not obj.id or not obj.order_id:
            print(f"⚠️ DEBUG: File {obj.id if obj else 'unknown'} missing required data for URL: file={bool(obj.file if obj else False)}, id={obj.id if obj else None}, order_id={obj.order_id if obj else None}")
            return None
        
        try:
            # Return secure download endpoint URL
            request = self.context.get('request')
            if request:
                try:
                    # Build the secure download endpoint URL
                    secure_url = f'/api/orders/{obj.order_id}/files/{obj.id}/download/'
                    return request.build_absolute_uri(secure_url)
                except Exception as uri_error:
                    # If building absolute URI fails, return relative URL
                    print(f"⚠️ DEBUG: Could not build absolute URI for file {obj.id}: {str(uri_error)}")
                    return f'/api/orders/{obj.order_id}/files/{obj.id}/download/'
            else:
                # If no request context, return relative URL
                return f'/api/orders/{obj.order_id}/files/{obj.id}/download/'
        except Exception as e:
            # Catch any unexpected errors and return None instead of crashing
            print(f"❌ DEBUG: Unexpected error getting file URL for {obj.id}: {str(e)}")
            return None


class FileUploadSerializer(serializers.Serializer):
    """Serializer for file uploads"""
    file = serializers.FileField()
    file_type = serializers.ChoiceField(choices=OrderFile.FILE_TYPE_CHOICES)
    stage = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    product_related = serializers.CharField(required=False, allow_blank=True)
    visible_to_roles = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    
    def validate_visible_to_roles(self, value):
        """Handle both list and JSON string formats"""
        if isinstance(value, str):
            try:
                import json
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return [value]  # Treat as single role
        elif isinstance(value, list):
            return value
        else:
            return ['admin']  # Default fallback


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders - matches frontend contract"""
    clientName = serializers.CharField(max_length=255)
    companyName = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    trn = serializers.CharField(max_length=50, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    specs = serializers.CharField(required=False, allow_blank=True)
    urgency = serializers.ChoiceField(choices=Order.URGENCY_CHOICES, default='Normal')
    salesPerson = serializers.CharField(max_length=255, required=False, allow_blank=True)
    sampleApprovalRequired = serializers.BooleanField(required=False, default=False)
    items = OrderItemCreateSerializer(many=True)
    deliveryDate = serializers.DateField(required=False, allow_null=True)
    assignedDesigner = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    assignedProductionPerson = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    assignedDepartment = serializers.CharField(max_length=50, required=False, allow_blank=True)
    deliveryOption = serializers.CharField(max_length=50, required=False, allow_blank=True)
    handledBy = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        return value


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order base fields"""
    items = OrderItemCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Order
        fields = [
            'client_name', 'company_name', 'phone', 'trn', 'email', 'address',
            'specs', 'urgency', 'pricing_status', 'status', 'items',
            'assigned_sales_person', 'assigned_designer', 'assigned_production_person',
            'internal_notes', 'channel', 'sample_approval_required'
        ]
    
    def update(self, instance, validated_data):
        import logging
        from .utils import copy_product_image_to_storage
        
        logger = logging.getLogger(__name__)
        
        items_data = validated_data.pop('items', None)
        
        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items if provided and not empty
        if items_data is not None and len(items_data) > 0:
            # Clear existing items and create new ones
            instance.items.all().delete()
            for item_data in items_data:
                # Pass order context for validation
                item_serializer = OrderItemCreateSerializer(data=item_data, context={'order': instance})
                item_serializer.is_valid(raise_exception=True)
                
                # Explicitly extract image_url to ensure it's saved
                original_image_url = item_serializer.validated_data.get('image_url')
                # Remove image_url from validated_data to avoid conflicts
                item_data_without_image = {k: v for k, v in item_serializer.validated_data.items() if k != 'image_url'}
                
                # Create the order item
                order_item = OrderItem.objects.create(order=instance, **item_data_without_image)
                
                # Copy product image to permanent storage if available
                # Only copy if the URL doesn't already point to our storage (to avoid re-copying)
                if original_image_url:
                    # Check if image URL already points to our product_images storage
                    if '/product_images/' not in original_image_url:
                        try:
                            copied_image_url = copy_product_image_to_storage(
                                image_url=original_image_url,
                                order_id=instance.id,
                                product_name=item_data.get('name')
                            )
                            # Use copied URL if successful, otherwise keep original
                            order_item.image_url = copied_image_url or original_image_url
                        except Exception as e:
                            # Log error but don't fail order update
                            logger.warning(f"Failed to copy product image for order {instance.id}: {e}")
                            # Keep original URL as fallback
                            order_item.image_url = original_image_url
                    else:
                        # Already copied, use as-is
                        order_item.image_url = original_image_url
                else:
                    order_item.image_url = None
                
                order_item.save(update_fields=['image_url'])
        
        return instance


class OrderSerializer(serializers.ModelSerializer):
    """Main order serializer with nested relationships"""
    items = OrderItemSerializer(many=True, read_only=True)
    quotation = QuotationSerializer(read_only=True)
    design_stage = DesignStageSerializer(read_only=True)
    printing_stage = PrintingStageSerializer(read_only=True)
    approval_stage = ApprovalStageSerializer(read_only=True)
    delivery_stage = DeliveryStageSerializer(read_only=True)
    uploads = UploadSerializer(many=True, read_only=True)
    files = serializers.SerializerMethodField()
    design_approvals = DesignApprovalSerializer(many=True, read_only=True)
    machine_assignments = ProductMachineAssignmentSerializer(many=True, read_only=True)
    
    # Computed fields for frontend compatibility
    products = serializers.SerializerMethodField()
    lineItems = serializers.SerializerMethodField()
    profile_tag = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'client_name', 'company_name', 'phone', 'trn', 'email',
            'address', 'specs', 'urgency', 'status', 'stage', 'pricing_status', 'delivery_code',
            'delivered_at', 'created_at', 'updated_at',
            'assigned_sales_person', 'assigned_designer', 'assigned_production_person',
            'internal_notes', 'channel', 'sample_approval_required', 'profile_tag',
            'items', 'products', 'lineItems',  # Frontend compatibility
            'quotation', 'design_stage', 'printing_stage', 'approval_stage',
            'delivery_stage', 'uploads', 'files', 'design_approvals', 'machine_assignments'
        ]
        read_only_fields = ['id', 'order_code', 'created_at', 'updated_at']
    
    def get_products(self, obj):
        """Alias for items - frontend compatibility"""
        return OrderItemSerializer(obj.items.all(), many=True).data
    
    def get_lineItems(self, obj):
        """Alias for items - frontend compatibility"""
        return OrderItemSerializer(obj.items.all(), many=True).data
    
    def get_profile_tag(self, obj):
        """Get profile_tag from related client or derive from channel"""
        # Skip client access since client field is deferred to avoid client_id column error
        # Fallback: derive from channel field
        if obj.channel:
            channel_to_tag = {
                'b2b_customers': 'b2b',
                'b2c_customers': 'b2c',
                'walk_in_orders': 'walk_in',
                'online_store': 'online',
            }
            return channel_to_tag.get(obj.channel)
        
        return None
    
    def get_files(self, obj):
        """Get files filtered by user role, consistent with OrderFilesListView"""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            # If no request context, return all files (backward compatibility)
            return OrderFileSerializer(obj.files.all(), many=True, context=self.context).data
        
        # Get all files
        all_files = obj.files.all()
        
        # Check if user is admin
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
        
        # Admin sees all files
        if is_admin:
            return OrderFileSerializer(all_files, many=True, context=self.context).data
        
        # Other roles see only files visible to them
        user_roles = getattr(request.user, 'roles', []) or []
        normalized_user_roles = [str(r).lower().strip() for r in user_roles if r]
        
        visible_files = []
        for file_obj in all_files:
            file_visible_roles = normalize_visible_to_roles(file_obj.visible_to_roles)
            
            # If file has no visible_to_roles set, make it visible to all (backward compatibility)
            if not file_visible_roles or len(file_visible_roles) == 0:
                visible_files.append(file_obj)
                continue
            
            # Check if any of the user's roles match any of the file's visible roles
            has_access = any(user_role in file_visible_roles for user_role in normalized_user_roles)
            
            if has_access:
                visible_files.append(file_obj)
        
        return OrderFileSerializer(visible_files, many=True, context=self.context).data


class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for order lists"""
    items_count = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    quotation = QuotationSerializer(read_only=True)
    machine_assignments = ProductMachineAssignmentSerializer(many=True, read_only=True)
    profile_tag = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'client_name', 'company_name', 'phone', 'trn', 'email',
            'address', 'specs', 'urgency', 'status', 'stage', 'pricing_status',
            'delivery_code', 'delivered_at', 'created_at', 'updated_at',
            'assigned_sales_person', 'assigned_designer', 'assigned_production_person',
            'channel', 'sample_approval_required', 'profile_tag', 'items_count', 'items', 'quotation',
            'machine_assignments'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_profile_tag(self, obj):
        """Get profile_tag from related client or derive from channel"""
        # Skip client access since client field is deferred to avoid client_id column error
        # Fallback: derive from channel field
        if obj.channel:
            channel_to_tag = {
                'b2b_customers': 'b2b',
                'b2c_customers': 'b2c',
                'walk_in_orders': 'walk_in',
                'online_store': 'online',
            }
            return channel_to_tag.get(obj.channel)
        
        return None


class StageTransitionSerializer(serializers.Serializer):
    """Serializer for stage transitions"""
    stage = serializers.ChoiceField(choices=Order.STAGE_CHOICES)
    payload = serializers.DictField(required=False, allow_empty=True)


class MarkPrintedSerializer(serializers.Serializer):
    """Serializer for mark printed action"""
    sku = serializers.CharField()
    qty = serializers.IntegerField(min_value=1)
    print_operator = serializers.CharField(required=False, allow_blank=True)
    print_time = serializers.DateTimeField(required=False)
    batch_info = serializers.CharField(required=False, allow_blank=True)
    qa_checklist = serializers.CharField(required=False, allow_blank=True)


class SendDeliveryCodeSerializer(serializers.Serializer):
    """Serializer for sending delivery codes"""
    code = serializers.CharField(max_length=6, min_length=6)
    phone = serializers.CharField(max_length=20)


class RiderPhotoUploadSerializer(serializers.Serializer):
    """Serializer for rider photo upload"""
    photo = serializers.ImageField()
    orderId = serializers.CharField()  # Accept as string, convert to int in view
    
    def validate_orderId(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError("Order ID must be a valid integer")
