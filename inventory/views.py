from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import InventoryItem, InventoryMovement, Machine
from .serializers import InventoryItemSerializer, InventoryAdjustSerializer, MachineSerializer
from accounts.permissions import RolePermission
from drf_spectacular.utils import extend_schema
import logging

logger = logging.getLogger(__name__)


class InventoryItemsView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    
    @extend_schema(responses={200: InventoryItemSerializer(many=True)})
    def get(self, request):
        """Get all inventory items"""
        items = InventoryItem.objects.all().order_by('sku')
        return Response(InventoryItemSerializer(items, many=True).data)
    
    @extend_schema(request=InventoryItemSerializer, responses={201: InventoryItemSerializer})
    def post(self, request):
        """Create a new inventory item"""
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            # Generate SKU if not provided
            if not serializer.validated_data.get('sku'):
                import time
                sku = f"SKU-{int(time.time() * 1000)}"
                serializer.validated_data['sku'] = sku
            
            item = serializer.save()
            return Response(InventoryItemSerializer(item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryItemDetailView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    
    def get_object(self, sku):
        return get_object_or_404(InventoryItem, sku=sku)
    
    @extend_schema(responses={200: InventoryItemSerializer})
    def get(self, request, sku):
        """Get a specific inventory item"""
        item = self.get_object(sku)
        return Response(InventoryItemSerializer(item).data)
    
    @extend_schema(request=InventoryItemSerializer, responses={200: InventoryItemSerializer})
    def put(self, request, sku):
        """Update an inventory item"""
        item = self.get_object(sku)
        serializer = InventoryItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            updated_item = serializer.save()
            return Response(InventoryItemSerializer(updated_item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(responses={204: None})
    def delete(self, request, sku):
        """Delete an inventory item"""
        item = self.get_object(sku)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InventoryAdjustView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin']
    @extend_schema(request=InventoryAdjustSerializer, responses={200: None})
    def post(self, request):
        s = InventoryAdjustSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = s.validated_data
        with transaction.atomic():
            item, _ = InventoryItem.objects.get_or_create(sku=data['sku'], defaults={'name': data['sku']})
            item.quantity = item.quantity + data['delta']
            item.save(update_fields=['quantity'])
            InventoryMovement.objects.create(order_id=None, sku=data['sku'], delta=data['delta'], reason=data['reason'])
        return Response({'ok': True})


class MachinesView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    
    @extend_schema(responses={200: MachineSerializer(many=True)})
    def get(self, request):
        """Get all machines"""
        machines = Machine.objects.all().order_by('machine_code')
        return Response(MachineSerializer(machines, many=True).data)
    
    @extend_schema(request=MachineSerializer, responses={201: MachineSerializer})
    def post(self, request):
        """Create a new machine"""
        serializer = MachineSerializer(data=request.data)
        if serializer.is_valid():
            machine = serializer.save()
            return Response(MachineSerializer(machine).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MachineDetailView(APIView):
    permission_classes = [RolePermission]
    allowed_roles = ['admin', 'sales', 'designer', 'production', 'delivery', 'finance']
    
    def get_object(self, id):
        return get_object_or_404(Machine, id=id)
    
    @extend_schema(responses={200: MachineSerializer})
    def get(self, request, id):
        """Get a specific machine"""
        machine = self.get_object(id)
        return Response(MachineSerializer(machine).data)
    
    @extend_schema(request=MachineSerializer, responses={200: MachineSerializer})
    def put(self, request, id):
        """Update a machine"""
        machine = self.get_object(id)
        serializer = MachineSerializer(machine, data=request.data, partial=True)
        if serializer.is_valid():
            updated_machine = serializer.save()
            return Response(MachineSerializer(updated_machine).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(responses={204: None})
    def delete(self, request, id):
        """Delete a machine"""
        machine = self.get_object(id)
        machine.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Create your views here.
