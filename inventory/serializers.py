from rest_framework import serializers
from .models import InventoryItem, InventoryMovement, Machine


class InventoryItemSerializer(serializers.ModelSerializer):
    available_stock = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()
    current_stock = serializers.IntegerField(source='quantity', required=False, write_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'sku', 'name', 'description', 'category', 'subcategory', 'barcode', 'unit',
            'quantity', 'current_stock', 'reserved', 'available_stock', 'minimum_stock', 'reorder_quantity', 
            'lead_time_days', 'cost_price', 'selling_price', 'warehouse', 'location', 
            'supplier_id', 'notes', 'total_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'available_stock', 'total_value']
    
    def create(self, validated_data):
        # Handle current_stock -> quantity mapping
        if 'current_stock' in validated_data:
            validated_data['quantity'] = validated_data.pop('current_stock')
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Handle current_stock -> quantity mapping
        if 'current_stock' in validated_data:
            validated_data['quantity'] = validated_data.pop('current_stock')
        return super().update(instance, validated_data)


class InventoryAdjustSerializer(serializers.Serializer):
    sku = serializers.CharField()
    delta = serializers.IntegerField()
    reason = serializers.CharField()


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = [
            'id', 'machine_code', 'name', 'type', 'brand', 'model', 'serial_number',
            'purchase_date', 'warranty_expiry', 'location', 'status', 'running_hours',
            'service_interval_hours', 'next_service_due', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['machine_code', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Auto-generate machine_code if not provided
        if 'machine_code' not in validated_data or not validated_data.get('machine_code'):
            machine_type = validated_data.get('type', '')
            if machine_type:
                type_code = machine_type[:3].upper() if len(machine_type) >= 3 else 'MCH'
            else:
                type_code = 'MCH'
            
            import random
            random_num = random.randint(0, 999)
            machine_code = f"{type_code}-{str(random_num).zfill(3)}"
            
            # Ensure uniqueness
            while Machine.objects.filter(machine_code=machine_code).exists():
                random_num = random.randint(0, 999)
                machine_code = f"{type_code}-{str(random_num).zfill(3)}"
            
            validated_data['machine_code'] = machine_code
        
        return super().create(validated_data)

