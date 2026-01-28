"""
Unit tests for orders models.
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from orders.models import Order, OrderItem, Quotation, DesignStage, PrintingStage, ApprovalStage, DeliveryStage, DesignApproval, ProductMachineAssignment
from tests.factories import (
    OrderFactory, OrderItemFactory, QuotationFactory, DesignStageFactory,
    PrintingStageFactory, ApprovalStageFactory, DeliveryStageFactory,
    DesignApprovalFactory, ProductMachineAssignmentFactory, UserFactory
)


@pytest.mark.django_db
@pytest.mark.unit
class TestOrderModel:
    """Test Order model."""
    
    def test_order_creation(self):
        """Test basic order creation."""
        order = OrderFactory()
        assert order.order_code is not None
        assert order.client_name is not None
        assert order.status == 'draft'
        assert order.stage == 'order_intake'
    
    def test_order_code_generation(self):
        """Test order code is generated."""
        order = OrderFactory()
        assert order.order_code.startswith('ORD-')
        assert len(order.order_code) > 4
    
    def test_order_status_choices(self):
        """Test order status choices."""
        order = OrderFactory(status='draft')
        assert order.status == 'draft'
        
        order.status = 'sent_to_designer'
        order.save()
        assert order.status == 'sent_to_designer'
    
    def test_order_stage_choices(self):
        """Test order stage choices."""
        order = OrderFactory(stage='order_intake')
        assert order.stage == 'order_intake'
        
        order.stage = 'quotation'
        order.save()
        assert order.stage == 'quotation'
    
    def test_order_urgency_choices(self):
        """Test order urgency choices."""
        order = OrderFactory(urgency='Normal')
        assert order.urgency == 'Normal'
        
        order.urgency = 'Urgent'
        order.save()
        assert order.urgency == 'Urgent'
    
    def test_order_string_representation(self):
        """Test order string representation."""
        order = OrderFactory(client_name='Test Client', order_code='ORD-123')
        assert str(order) == 'ORD-123 - Test Client'
    
    def test_order_created_by_relationship(self):
        """Test order created_by relationship."""
        user = UserFactory()
        order = OrderFactory(created_by=user)
        assert order.created_by == user


@pytest.mark.django_db
@pytest.mark.unit
class TestOrderItemModel:
    """Test OrderItem model."""
    
    def test_order_item_creation(self):
        """Test basic order item creation."""
        order = OrderFactory()
        item = OrderItemFactory(order=order)
        assert item.order == order
        assert item.quantity > 0
        assert item.unit_price >= 0
    
    def test_order_item_line_total_calculation(self):
        """Test line total is calculated automatically."""
        item = OrderItemFactory(quantity=5, unit_price=Decimal('10.00'))
        assert item.line_total == Decimal('50.00')
    
    def test_order_item_save_recalculates_total(self):
        """Test line total is recalculated on save."""
        item = OrderItemFactory(quantity=2, unit_price=Decimal('5.00'))
        assert item.line_total == Decimal('10.00')
        
        item.quantity = 3
        item.save()
        assert item.line_total == Decimal('15.00')
    
    def test_order_item_string_representation(self):
        """Test order item string representation."""
        order = OrderFactory(order_code='ORD-123')
        item = OrderItemFactory(order=order, name='Test Product', quantity=10)
        assert 'ORD-123' in str(item)
        assert 'Test Product' in str(item)
        assert 'x10' in str(item)


@pytest.mark.django_db
@pytest.mark.unit
class TestQuotationModel:
    """Test Quotation model."""
    
    def test_quotation_creation(self):
        """Test basic quotation creation."""
        order = OrderFactory()
        quotation = QuotationFactory(order=order)
        assert quotation.order == order
        assert quotation.labour_cost >= 0
    
    def test_quotation_calculate_totals(self):
        """Test quotation totals calculation."""
        order = OrderFactory()
        OrderItemFactory(order=order, quantity=10, unit_price=Decimal('5.00'))
        quotation = QuotationFactory(
            order=order,
            labour_cost=Decimal('100.00'),
            paper_cost=Decimal('50.00'),
            discount=Decimal('10.00')
        )
        
        quotation.calculate_totals()
        assert quotation.products_subtotal == Decimal('50.00')
        assert quotation.other_subtotal >= Decimal('100.00')
        assert quotation.vat_3pct > 0
        assert quotation.grand_total > 0
    
    def test_quotation_string_representation(self):
        """Test quotation string representation."""
        order = OrderFactory(order_code='ORD-123')
        quotation = QuotationFactory(order=order)
        assert 'ORD-123' in str(quotation)


@pytest.mark.django_db
@pytest.mark.unit
class TestDesignStageModel:
    """Test DesignStage model."""
    
    def test_design_stage_creation(self):
        """Test basic design stage creation."""
        order = OrderFactory()
        design_stage = DesignStageFactory(order=order)
        assert design_stage.order == order
        assert design_stage.assigned_designer is not None


@pytest.mark.django_db
@pytest.mark.unit
class TestPrintingStageModel:
    """Test PrintingStage model."""
    
    def test_printing_stage_creation(self):
        """Test basic printing stage creation."""
        order = OrderFactory()
        printing_stage = PrintingStageFactory(order=order)
        assert printing_stage.order == order
        assert printing_stage.print_status in ['Pending', 'Printing', 'Printed']


@pytest.mark.django_db
@pytest.mark.unit
class TestApprovalStageModel:
    """Test ApprovalStage model."""
    
    def test_approval_stage_creation(self):
        """Test basic approval stage creation."""
        order = OrderFactory()
        approval_stage = ApprovalStageFactory(order=order)
        assert approval_stage.order == order
        assert isinstance(approval_stage.client_approval_files, list)


@pytest.mark.django_db
@pytest.mark.unit
class TestDeliveryStageModel:
    """Test DeliveryStage model."""
    
    def test_delivery_stage_creation(self):
        """Test basic delivery stage creation."""
        order = OrderFactory()
        delivery_stage = DeliveryStageFactory(order=order)
        assert delivery_stage.order == order


@pytest.mark.django_db
@pytest.mark.unit
class TestDesignApprovalModel:
    """Test DesignApproval model."""
    
    def test_design_approval_creation(self):
        """Test basic design approval creation."""
        order = OrderFactory()
        approval = DesignApprovalFactory(order=order)
        assert approval.order == order
        assert approval.approval_status in ['pending', 'approved', 'rejected']
    
    def test_design_approval_string_representation(self):
        """Test design approval string representation."""
        order = OrderFactory(order_code='ORD-123')
        approval = DesignApprovalFactory(order=order, approval_status='pending')
        assert 'ORD-123' in str(approval)
        assert 'pending' in str(approval)


@pytest.mark.django_db
@pytest.mark.unit
class TestProductMachineAssignmentModel:
    """Test ProductMachineAssignment model."""
    
    def test_machine_assignment_creation(self):
        """Test basic machine assignment creation."""
        order = OrderFactory()
        assignment = ProductMachineAssignmentFactory(order=order)
        assert assignment.order == order
        assert assignment.status in ['queued', 'in_progress', 'completed', 'on_hold']
        assert assignment.estimated_time_minutes > 0
    
    def test_machine_assignment_string_representation(self):
        """Test machine assignment string representation."""
        order = OrderFactory(order_code='ORD-123')
        assignment = ProductMachineAssignmentFactory(
            order=order,
            product_name='Test Product',
            machine_name='Test Machine'
        )
        assert 'ORD-123' in str(assignment)
        assert 'Test Product' in str(assignment)
        assert 'Test Machine' in str(assignment)













































