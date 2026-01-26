"""
Integration tests for complete order workflow.
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from orders.models import Order, OrderItem, DesignApproval, ProductMachineAssignment
from tests.factories import (
    OrderFactory, OrderItemFactory, DesignApprovalFactory,
    ProductMachineAssignmentFactory, SalesUserFactory, DesignerUserFactory,
    ProductionUserFactory, DeliveryUserFactory
)


@pytest.mark.django_db
@pytest.mark.integration
class TestCompleteOrderWorkflow:
    """Test complete order lifecycle workflow."""
    
    def test_order_creation_to_delivery_workflow(self, sales_client, designer_client, production_client, delivery_client):
        """Test complete order workflow from creation to delivery."""
        # Step 1: Sales creates order
        response = sales_client.post(
            '/api/orders',
            {
                'clientName': 'Test Client',
                'companyName': 'Test Company',
                'phone': '1234567890',
                'email': 'test@example.com',
                'urgency': 'Normal',
                'items': [
                    {
                        'name': 'Test Product',
                        'quantity': 10,
                        'unit_price': '50.00',
                        'attributes': {}
                    }
                ]
            },
            format='json'
        )
        
        assert response.status_code == 201
        order_id = response.data['data']['id']
        
        # Step 2: Sales sends to designer
        order = Order.objects.get(id=order_id)
        order.status = 'sent_to_designer'
        order.stage = 'design'
        order.save()
        
        # Step 3: Designer requests approval
        approval = DesignApprovalFactory(
            order=order,
            approval_status='pending'
        )
        order.status = 'sent_for_approval'
        order.save()
        
        # Step 4: Sales approves design
        approval.approval_status = 'approved'
        approval.save()
        order.refresh_from_db()
        assert order.status == 'sent_to_production'
        
        # Step 5: Production assigns machines
        assignment = ProductMachineAssignmentFactory(
            order=order,
            status='queued'
        )
        
        # Step 6: Production completes assignment
        assignment.completed_at = timezone.now()
        assignment.status = 'completed'
        assignment.save()
        order.refresh_from_db()
        assert order.status == 'sent_for_delivery'
        
        # Step 7: Delivery completes order
        order.status = 'delivered'
        order.delivered_at = timezone.now()
        order.save()
        
        assert order.status == 'delivered'
        assert order.delivered_at is not None













































