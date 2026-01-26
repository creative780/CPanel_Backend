"""
Unit tests for orders signals.
"""
import pytest
from django.utils import timezone
from orders.models import Order, ProductMachineAssignment, DesignApproval
from tests.factories import (
    OrderFactory, ProductMachineAssignmentFactory, DesignApprovalFactory
)


@pytest.mark.django_db
@pytest.mark.unit
class TestOrderSignals:
    """Test order-related signals."""
    
    def test_machine_assignment_completion_transitions_order(self):
        """Test that completing all machine assignments transitions order to sent_for_delivery."""
        order = OrderFactory(status='getting_ready')
        
        # Create two machine assignments
        assignment1 = ProductMachineAssignmentFactory(order=order, status='queued')
        assignment2 = ProductMachineAssignmentFactory(order=order, status='queued')
        
        # Complete first assignment
        assignment1.completed_at = timezone.now()
        assignment1.status = 'completed'
        assignment1.save()
        
        # Order should still be getting_ready
        order.refresh_from_db()
        assert order.status == 'getting_ready'
        
        # Complete second assignment
        assignment2.completed_at = timezone.now()
        assignment2.status = 'completed'
        assignment2.save()
        
        # Order should now be sent_for_delivery
        order.refresh_from_db()
        assert order.status == 'sent_for_delivery'
    
    def test_design_approval_transitions_order(self):
        """Test that approving design transitions order to sent_to_production."""
        order = OrderFactory(status='sent_for_approval')
        
        approval = DesignApprovalFactory(
            order=order,
            approval_status='pending'
        )
        
        # Approve the design
        approval.approval_status = 'approved'
        approval.save()
        
        # Order should now be sent_to_production
        order.refresh_from_db()
        assert order.status == 'sent_to_production'
    
    def test_order_delivered_sets_delivered_at(self):
        """Test that setting order status to delivered sets delivered_at timestamp."""
        order = OrderFactory(status='sent_for_delivery')
        assert order.delivered_at is None
        
        # Change status to delivered
        order.status = 'delivered'
        order.save()
        
        # delivered_at should be set
        order.refresh_from_db()
        assert order.delivered_at is not None
    
    def test_order_status_change_logging(self, caplog):
        """Test that order status changes are logged."""
        import logging
        logger = logging.getLogger('orders.signals')
        
        order = OrderFactory(status='draft')
        
        # Change status
        order.status = 'sent_to_designer'
        order.save()
        
        # Check that status change was logged
        assert any('status changed' in record.message.lower() for record in caplog.records)













































