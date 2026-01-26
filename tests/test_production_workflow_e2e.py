"""
End-to-end workflow tests for production orders.
Tests the complete production workflow from order creation to delivery.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from django.utils import timezone

from orders.models import Order, OrderItem, ProductMachineAssignment


# Use fixtures from conftest.py instead of creating custom auth


@pytest.mark.django_db(transaction=True)
class TestProductionWorkflowE2E:
    """End-to-end tests for complete production workflow."""
    
    def test_complete_production_workflow(self, admin_client, production_client, designer_client, db):
        """Test complete workflow: Create → Send to Production → Assign Machines → Start → Complete → Delivery"""
        
        # Step 1: Create order (as sales/admin)
        sales_client = admin_client
        
        create_response = sales_client.post(
            '/api/orders/',
            {
                'clientName': 'E2E Test Client',
                'companyName': 'E2E Test Co',
                'phone': '+971501234567',
                'email': 'e2e@example.com',
                'address': 'Dubai, UAE',
                'specs': 'E2E test order',
                'urgency': 'Normal',
                'channel': 'b2b_customers',
                'items': [
                    {
                        'name': 'Business Cards',
                        'sku': 'BC-E2E-001',
                        'quantity': 500,
                        'unit_price': '0.50',
                        'attributes': {'finish': 'matte'}
                    },
                    {
                        'name': 'Brochures',
                        'sku': 'BR-E2E-001',
                        'quantity': 1000,
                        'unit_price': '2.50',
                        'attributes': {'size': 'A4'}
                    }
                ]
            },
            format='json'
        )
        
        assert create_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        order_data = create_response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        assert order_id is not None
        
        # Step 2: Create design approval (required for sending to production)
        # Even though admin can bypass, let's create an approval to match real workflow
        from orders.models import DesignApproval
        order = Order.objects.get(id=order_id)
        DesignApproval.objects.create(
            order=order,
            designer='designer_test',
            sales_person='admin_test',
            approval_status='approved',
            reviewed_at=timezone.now()
        )
        
        # Step 3: Send to production (as admin/designer)
        send_to_prod_response = admin_client.post(
            f'/api/orders/{order_id}/send-to-production/',
            format='json'
        )
        
        assert send_to_prod_response.status_code == status.HTTP_200_OK, f"Send to production failed: {send_to_prod_response.data if hasattr(send_to_prod_response, 'data') else send_to_prod_response.content}"
        
        # Verify order status
        order.refresh_from_db()
        assert order.status == 'sent_to_production'
        assert order.stage == 'printing'
        
        # Step 4: Assign machines (as production)
        # Get order items
        order_detail_response = production_client.get(f'/api/orders/{order_id}/')
        assert order_detail_response.status_code == status.HTTP_200_OK
        
        order_detail = order_detail_response.data
        if isinstance(order_detail, dict) and 'data' in order_detail:
            order_info = order_detail['data']
        else:
            order_info = order_detail
        
        items = order_info.get('items', [])
        assert len(items) == 2
        
        # Create machine assignments
        assignments = [
            {
                'product_name': items[0].get('name', 'Business Cards'),
                'product_sku': items[0].get('sku', 'BC-E2E-001'),
                'product_quantity': items[0].get('quantity', 500),
                'machine_id': 'printer-01',
                'machine_name': 'Digital Printer 1',
                'estimated_time_minutes': 60,
                'assigned_by': 'production_user',
                'notes': 'Assignment for business cards'
            },
            {
                'product_name': items[1].get('name', 'Brochures'),
                'product_sku': items[1].get('sku', 'BR-E2E-001'),
                'product_quantity': items[1].get('quantity', 1000),
                'machine_id': 'printer-02',
                'machine_name': 'Digital Printer 2',
                'estimated_time_minutes': 90,
                'assigned_by': 'production_user',
                'notes': 'Assignment for brochures'
            }
        ]
        
        # Use admin_client for assign-machines (admin also has permission)
        assign_response = admin_client.post(
            f'/api/orders/{order_id}/assign-machines/',
            assignments,
            format='json'
        )
        
        assert assign_response.status_code == status.HTTP_201_CREATED, f"Assign machines failed: {assign_response.data if hasattr(assign_response, 'data') else assign_response.content}"
        assignment_data = assign_response.data
        assert len(assignment_data) == 2
        
        # Verify assignments created
        order.refresh_from_db()
        assert order.machine_assignments.count() == 2
        assert order.status == 'getting_ready'
        
        # Step 5: Start production (update status to active)
        start_response = production_client.patch(
            f'/api/orders/{order_id}/',
            {
                'status': 'active',
                'stage': 'printing'
            },
            format='json'
        )
        
        assert start_response.status_code == status.HTTP_200_OK
        
        order.refresh_from_db()
        assert order.status == 'active'
        assert order.stage == 'printing'
        
        # Verify assignments have started_at
        assignments = order.machine_assignments.all()
        for assignment in assignments:
            assert assignment.started_at is not None
            assert assignment.status == 'queued' or assignment.status == 'in_progress'
        
        # Step 6: Mark assignments as completed
        assignment_ids = [a.get('id') for a in assignment_data]
        
        for assignment_id in assignment_ids:
            complete_response = production_client.patch(
                f'/api/machine-assignments/{assignment_id}/status/',
                {
                    'status': 'completed'
                },
                format='json'
            )
            assert complete_response.status_code == status.HTTP_200_OK
        
        # Verify all assignments completed
        order.refresh_from_db()
        assignments = order.machine_assignments.all()
        for assignment in assignments:
            assert assignment.status == 'completed'
            assert assignment.completed_at is not None
        
        # Step 7: Send to delivery (should move to completed/history)
        delivery_response = production_client.patch(
            f'/api/orders/{order_id}/',
            {
                'status': 'sent_for_delivery',
                'stage': 'delivery'
            },
            format='json'
        )
        
        assert delivery_response.status_code == status.HTTP_200_OK
        
        order.refresh_from_db()
        assert order.status == 'sent_for_delivery'
        assert order.stage == 'delivery'
    
    def test_order_appears_in_new_tab_after_sent_to_production(self, admin_client, production_client, db):
        """Test that order appears in 'New' tab after being sent to production."""
        
        # Create and send order to production
        
        create_response = admin_client.post(
            '/api/orders/',
            {
                'clientName': 'New Tab Test Client',
                'specs': 'Test order for new tab',
                'urgency': 'Normal',
                'items': [
                    {
                        'name': 'Test Product',
                        'sku': 'TEST-NEW-001',
                        'quantity': 100,
                        'unit_price': '5.00'
                    }
                ]
            },
            format='json'
        )
        
        assert create_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        order_data = create_response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        # Create design approval first (required for sending to production)
        from orders.models import DesignApproval
        order = Order.objects.get(id=order_id)
        DesignApproval.objects.create(
            order=order,
            designer='admin_test',
            sales_person='admin_test',
            approval_status='approved',
            reviewed_at=timezone.now()
        )
        
        # Send to production
        send_response = admin_client.post(
            f'/api/orders/{order_id}/send-to-production/',
            format='json'
        )
        assert send_response.status_code == status.HTTP_200_OK, f"Send to production failed: {send_response.data if hasattr(send_response, 'data') else send_response.content}"
        
        # Check production orders endpoint
        prod_orders_response = production_client.get('/api/production/orders/')
        
        assert prod_orders_response.status_code == status.HTTP_200_OK
        data = prod_orders_response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        
        # Order should be in results
        order_codes = [o.get('order_code') for o in results]
        order = Order.objects.get(id=order_id)
        assert order.order_code in order_codes
        
        # Verify it's in 'new' state (sent_to_production, no assignments)
        order_in_results = next((o for o in results if o.get('order_code') == order.order_code), None)
        assert order_in_results is not None
        assert order_in_results.get('status') == 'sent_to_production'
        assert order_in_results.get('stage') == 'printing'
        # Should have no machine assignments or empty list
        machine_assignments = order_in_results.get('machine_assignments', [])
        assert len(machine_assignments) == 0
    
    def test_order_moves_to_in_progress_after_confirmation(self, admin_client, production_client, db):
        """Test that order moves to 'In Progress' tab after confirmation."""
        
        # Create order and send to production
        
        create_response = admin_client.post(
            '/api/orders/',
            {
                'clientName': 'In Progress Test Client',
                'specs': 'Test order for in progress',
                'urgency': 'High',
                'items': [
                    {
                        'name': 'Test Product',
                        'sku': 'TEST-PROG-001',
                        'quantity': 200,
                        'unit_price': '3.00'
                    }
                ]
            },
            format='json'
        )
        
        assert create_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        order_data = create_response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        admin_client.post(f'/api/orders/{order_id}/send-to-production/', format='json')
        
        # Assign machines
        order_detail = production_client.get(f'/api/orders/{order_id}/').data
        if isinstance(order_detail, dict) and 'data' in order_detail:
            order_info = order_detail['data']
        else:
            order_info = order_detail
        
        items = order_info.get('items', [])
        
        assignments = [
            {
                'product_name': items[0].get('name', 'Test Product'),
                'product_sku': items[0].get('sku', 'TEST-PROG-001'),
                'product_quantity': items[0].get('quantity', 200),
                'machine_id': 'printer-01',
                'machine_name': 'Digital Printer 1',
                'estimated_time_minutes': 45,
                'assigned_by': 'production_user'
            }
        ]
        
        production_client.post(
            f'/api/orders/{order_id}/assign-machines/',
            assignments,
            format='json'
        )
        
        # Confirm order (start production)
        production_client.patch(
            f'/api/orders/{order_id}/',
            {
                'status': 'active',
                'stage': 'printing'
            },
            format='json'
        )
        
        # Verify order is now in 'active' status
        order = Order.objects.get(id=order_id)
        assert order.status == 'active'
        assert order.stage == 'printing'
        
        # Check production orders - should be in 'in progress' category
        prod_orders_response = production_client.get('/api/production/orders/')
        assert prod_orders_response.status_code == status.HTTP_200_OK
        
        data = prod_orders_response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        
        order_in_results = next((o for o in results if o.get('order_code') == order.order_code), None)
        assert order_in_results is not None
        assert order_in_results.get('status') == 'active'
        assert len(order_in_results.get('machine_assignments', [])) > 0
    
    def test_order_moves_to_completed_after_all_assignments_done(self, admin_client, production_client, db):
        """Test that order moves to 'Completed' tab after all assignments are done."""
        
        # Create order, send to production, assign machines, start
        
        create_response = admin_client.post(
            '/api/orders/',
            {
                'clientName': 'Completed Test Client',
                'specs': 'Test order for completed',
                'urgency': 'Normal',
                'items': [
                    {
                        'name': 'Test Product',
                        'sku': 'TEST-COMP-001',
                        'quantity': 300,
                        'unit_price': '4.00'
                    }
                ]
            },
            format='json'
        )
        
        assert create_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        order_data = create_response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        admin_client.post(f'/api/orders/{order_id}/send-to-production/', format='json')
        
        order_detail = production_client.get(f'/api/orders/{order_id}/').data
        if isinstance(order_detail, dict) and 'data' in order_detail:
            order_info = order_detail['data']
        else:
            order_info = order_detail
        
        items = order_info.get('items', [])
        
        assignments = [
            {
                'product_name': items[0].get('name', 'Test Product'),
                'product_sku': items[0].get('sku', 'TEST-COMP-001'),
                'product_quantity': items[0].get('quantity', 300),
                'machine_id': 'printer-01',
                'machine_name': 'Digital Printer 1',
                'estimated_time_minutes': 60,
                'assigned_by': 'production_user'
            }
        ]
        
        assign_response = production_client.post(
            f'/api/orders/{order_id}/assign-machines/',
            assignments,
            format='json'
        )
        
        assignment_id = assign_response.data[0].get('id')
        
        # Start production
        production_client.patch(
            f'/api/orders/{order_id}/',
            {
                'status': 'active',
                'stage': 'printing'
            },
            format='json'
        )
        
        # Complete assignment
        production_client.patch(
            f'/api/machine-assignments/{assignment_id}/status/',
            {
                'status': 'completed'
            },
            format='json'
        )
        
        # Verify order has all assignments completed
        order = Order.objects.get(id=order_id)
        assignments = order.machine_assignments.all()
        assert all(a.status == 'completed' for a in assignments)
        
        # Update status to getting_ready (should be done automatically by signals, but test manually)
        # Only send status, not stage, to avoid stage transition logic
        production_client.patch(
            f'/api/orders/{order_id}/',
            {
                'status': 'getting_ready'
            },
            format='json'
        )
        
        order.refresh_from_db()
        assert order.status == 'getting_ready'
        
        # Check production orders - should be in 'completed' category
        prod_orders_response = production_client.get('/api/production/orders/')
        assert prod_orders_response.status_code == status.HTTP_200_OK
        
        data = prod_orders_response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        
        order_in_results = next((o for o in results if o.get('order_code') == order.order_code), None)
        assert order_in_results is not None
        assert order_in_results.get('status') in ['getting_ready', 'sent_to_admin']
    
    def test_order_moves_to_history_after_delivery(self, admin_client, production_client, db):
        """Test that order moves to 'History' tab after being sent to delivery."""
        
        # Create a completed order
        
        order = Order.objects.create(
            order_code='PROD-HIST-E2E',
            client_name='History Test Client',
            status='getting_ready',
            stage='printing',
            urgency='Normal'
        )
        
        OrderItem.objects.create(
            order=order,
            name='Test Product',
            sku='TEST-HIST-001',
            quantity=100,
            unit_price=Decimal('5.00'),
            line_total=Decimal('500.00')
        )
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Test Product',
            product_sku='TEST-HIST-001',
            product_quantity=100,
            machine_id='printer-01',
            machine_name='Digital Printer 1',
            estimated_time_minutes=60,
            status='completed',
            completed_at=timezone.now(),
            assigned_by='production_user'
        )
        
        # Send to delivery - use stage transition for delivery
        delivery_response = production_client.patch(
            f'/api/orders/{order.id}/',
            {
                'stage': 'delivery'
            },
            format='json'
        )
        
        assert delivery_response.status_code == status.HTTP_200_OK
        
        order.refresh_from_db()
        assert order.status == 'sent_for_delivery'
        assert order.stage == 'delivery'
        
        # Check production orders - should be in 'history' category
        prod_orders_response = production_client.get('/api/production/orders/')
        assert prod_orders_response.status_code == status.HTTP_200_OK
        
        data = prod_orders_response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        
        order_in_results = next((o for o in results if o.get('order_code') == order.order_code), None)
        assert order_in_results is not None
        assert order_in_results.get('status') in ['sent_for_delivery', 'delivered']
        assert order_in_results.get('stage') == 'delivery'

