"""
Comprehensive unit tests for production dashboard endpoints.
Tests all 8 production dashboard API endpoints with various scenarios.
"""
import pytest
import random
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, datetime, time
from decimal import Decimal
from orders.models import Order, OrderItem, ProductMachineAssignment
from inventory.models import InventoryItem, InventoryMovement
from accounts.models import Role


@pytest.fixture
def production_user(db):
    """Create a production user for testing"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='production_test',
        email='production@test.com',
        password='testpass123',
        roles=[Role.PRODUCTION],
        first_name='Production',
        last_name='User',
    )


@pytest.fixture
def authenticated_client(production_user):
    """Create authenticated API client"""
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    client = APIClient()
    refresh = RefreshToken.for_user(production_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def test_orders(db):
    """Create test orders for various scenarios"""
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    
    orders = []
    
    # WIP orders
    for i in range(5):
        order, created = Order.objects.get_or_create(
            order_code=f'TEST-WIP-{i+1:03d}',
            defaults={
                'client_name': f'Test Client {i+1}',
                'company_name': f'Test Company {i+1}',
                'phone': f'+9715012345{i:02d}',
                'email': f'client{i+1}@test.com',
                'address': 'Dubai, UAE',
                'specs': f'Test order {i+1}',
                'status': 'sent_to_production',
                'stage': 'printing',
                'created_at': timezone.make_aware(datetime.combine(today, time(9, 0, 0)))
            }
        )
        if created or not order.items.exists():
            OrderItem.objects.get_or_create(
                order=order,
                product_id=f'PROD-{i+1}',
                defaults={
                    'name': f'Product {i+1}',
                    'sku': f'SKU-{i+1}',
                    'quantity': 50,
                    'unit_price': Decimal('10.00'),
                    'line_total': Decimal('100.00')
                }
            )
        orders.append(order)
    
    # Getting ready orders
    for i in range(3):
        order, created = Order.objects.get_or_create(
            order_code=f'TEST-READY-{i+1:03d}',
            defaults={
                'client_name': f'Test Client Ready {i+1}',
                'company_name': f'Test Company Ready {i+1}',
                'phone': f'+9715012346{i:02d}',
                'email': f'ready{i+1}@test.com',
                'address': 'Dubai, UAE',
                'specs': f'Test order ready {i+1}',
                'status': 'getting_ready',
                'stage': 'printing',
                'created_at': timezone.make_aware(datetime.combine(today, time(10, 0, 0)))
            }
        )
        if created or not order.items.exists():
            OrderItem.objects.get_or_create(
                order=order,
                product_id=f'PROD-READY-{i+1}',
                defaults={
                    'name': f'Product Ready {i+1}',
                    'sku': f'SKU-READY-{i+1}',
                    'quantity': 50,
                    'unit_price': Decimal('10.00'),
                    'line_total': Decimal('100.00')
                }
            )
        orders.append(order)
    
    # Completed orders for turnaround time
    for i in range(10):
        days_ago = i % 7
        delivered_date = now - timedelta(days=days_ago)
        created_date = delivered_date - timedelta(days=random.randint(1, 5))
        
        # Dates are already timezone-aware from now - timedelta
        # Use get_or_create to avoid duplicates if test database is reused
        order, created = Order.objects.get_or_create(
            order_code=f'TEST-DEL-{i+1:03d}',
            defaults={
                'client_name': f'Test Client Del {i+1}',
                'company_name': f'Test Company Del {i+1}',
                'phone': f'+9715012347{i:02d}',
                'email': f'del{i+1}@test.com',
                'address': 'Dubai, UAE',
                'specs': f'Test order delivered {i+1}',
                'status': 'delivered',
                'stage': 'delivery',
                'created_at': created_date,
                'delivered_at': delivered_date
            }
        )
        if created or not order.items.exists():
            OrderItem.objects.get_or_create(
                order=order,
                product_id=f'PROD-DEL-{i+1}',
                defaults={
                    'name': f'Product Del {i+1}',
                    'sku': f'SKU-DEL-{i+1}',
                    'quantity': 50,
                    'unit_price': Decimal('10.00'),
                    'line_total': Decimal('100.00')
                }
            )
        orders.append(order)
    
    return orders


@pytest.fixture
def test_machine_assignments(db, test_orders):
    """Create test machine assignments"""
    machines = [
        ('HP-LATEX-570', 'HP Latex 570'),
        ('HP-LATEX-800W', 'HP Latex 800W'),
        ('MIMAKI-JV150', 'Mimaki JV150'),
        ('EPSON-S80600', 'Epson S80600'),
        ('SUMMA-CUTTER', 'Summa Cutter'),
    ]
    
    assignments = []
    now = timezone.now()
    today = now.date()
    
    for i, order in enumerate(test_orders[:5]):
        if order.items.exists():
            order_item = order.items.first()
            machine_id, machine_name = machines[i % len(machines)]
            status = ['queued', 'in_progress', 'completed'][i % 3]
            
            started_at = None
            completed_at = None
            
            if status == 'in_progress':
                started_at = timezone.make_aware(datetime.combine(today, time(9, 0, 0)))
            elif status == 'completed':
                started_at = timezone.make_aware(datetime.combine(today, time(8, 0, 0)))
                completed_at = started_at + timedelta(minutes=60)
            
            assignment = ProductMachineAssignment.objects.create(
                order=order,
                product_name=order_item.name,
                product_sku=order_item.sku,
                product_quantity=order_item.quantity,
                machine_id=machine_id,
                machine_name=machine_name,
                estimated_time_minutes=60,
                started_at=started_at,
                completed_at=completed_at,
                status=status,
                assigned_by='test_user'
            )
            assignments.append(assignment)
    
    return assignments


@pytest.fixture
def test_reprint_orders(db):
    """Create test reprint orders"""
    now = timezone.now()
    week_start = now - timedelta(days=now.weekday())
    last_week_start = week_start - timedelta(days=7)
    
    # Create original orders
    original = Order.objects.create(
        order_code='TEST-ORIG-001',
        client_name='Original Client',
        company_name='Original Company',
        phone='+971501111111',
        email='original@test.com',
        address='Dubai, UAE',
        specs='Original order',
        status='delivered',
        created_at=now - timedelta(days=20),
        delivered_at=now - timedelta(days=10),
        is_reprint=False
    )
    OrderItem.objects.create(
        order=original,
        product_id='PROD-ORIG',
        name='Original Product',
        sku='SKU-ORIG',
        quantity=100,
        unit_price=Decimal('10.00'),
        line_total=Decimal('100.00')
    )
    
    # Create reprint this week
    reprint1 = Order.objects.create(
        order_code='TEST-REPRINT-001',
        client_name='Original Client',
        company_name='Original Company',
        phone='+971501111111',
        email='original@test.com',
        address='Dubai, UAE',
        specs='Reprint order',
        status='sent_to_production',
        created_at=week_start + timedelta(days=2),
        is_reprint=True,
        original_order=original
    )
    OrderItem.objects.create(
        order=reprint1,
        product_id='PROD-REPRINT',
        name='Reprint Product',
        sku='SKU-REPRINT',
        quantity=100,
        unit_price=Decimal('10.00'),
        line_total=Decimal('100.00')
    )
    
    # Create reprint last week
    reprint2 = Order.objects.create(
        order_code='TEST-REPRINT-LW-001',
        client_name='Original Client',
        company_name='Original Company',
        phone='+971501111111',
        email='original@test.com',
        address='Dubai, UAE',
        specs='Reprint order last week',
        status='delivered',
        created_at=last_week_start + timedelta(days=3),
        delivered_at=last_week_start + timedelta(days=5),
        is_reprint=True,
        original_order=original
    )
    OrderItem.objects.create(
        order=reprint2,
        product_id='PROD-REPRINT-LW',
        name='Reprint Product LW',
        sku='SKU-REPRINT-LW',
        quantity=100,
        unit_price=Decimal('10.00'),
        line_total=Decimal('100.00')
    )
    
    return [original, reprint1, reprint2]


@pytest.fixture
def test_inventory_data(db):
    """Create test inventory movements"""
    materials = [
        ('VINYL-001', 'Vinyl Roll', 100),
        ('FABRIC-001', 'Fabric Material', 50),
        ('PAPER-001', 'Paper Stock', 200),
    ]
    
    # Create inventory items
    for sku, name, min_stock in materials:
        InventoryItem.objects.get_or_create(
            sku=sku,
            defaults={
                'name': name,
                'quantity': 200,
                'minimum_stock': min_stock,
                'category': 'raw_materials'
            }
        )
    
    # Create movements
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    
    movements = []
    for i in range(10):
        sku, name, _ = materials[i % len(materials)]
        movement = InventoryMovement.objects.create(
            order_id=1000 + i,
            sku=sku,
            delta=-random.randint(5, 50),
            reason=f'Test consumption {i+1}',
            created_at=last_7_days + timedelta(days=i % 7, hours=8)
        )
        movements.append(movement)
    
    return movements


@pytest.fixture
def test_delivery_orders(db):
    """Create test delivery ready orders"""
    now = timezone.now()
    orders = []
    
    for i in range(3):
        order = Order.objects.create(
            order_code=f'TEST-DELIVERY-{i+1:03d}',
            client_name=f'Delivery Client {i+1}',
            company_name=f'Delivery Company {i+1}',
            phone=f'+9715012350{i:02d}',
            email=f'delivery{i+1}@test.com',
            address='Dubai, UAE',
            specs=f'Delivery order {i+1}',
            status='sent_for_delivery',
            stage='delivery',
            delivery_code=f'{100000 + i}' if i < 2 else None,
            created_at=now - timedelta(days=i+1),
            updated_at=now - timedelta(hours=i+1)
        )
        OrderItem.objects.create(
            order=order,
            product_id=f'PROD-DELIVERY-{i+1}',
            name=f'Product {i+1}',
            sku=f'SKU-DELIVERY-{i+1}',
            quantity=50,
            unit_price=Decimal('10.00'),
            line_total=Decimal('100.00')
        )
        orders.append(order)
    
    return orders


@pytest.mark.django_db
class TestProductionWIPCount:
    """Test production_wip_count endpoint"""
    
    def test_wip_count_basic(self, authenticated_client, test_orders):
        """Test basic WIP count calculation"""
        url = reverse('production-wip-count')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert 'current' in response.data
        assert 'change' in response.data
        assert 'change_direction' in response.data
        assert response.data['current'] >= 0
    
    def test_wip_count_includes_sent_to_production(self, authenticated_client, db):
        """Test that orders with status='sent_to_production' are counted"""
        order = Order.objects.create(
            order_code='TEST-WIP-STATUS',
            client_name='Test Client',
            company_name='Test Company',
            phone='+971501111111',
            email='test@test.com',
            status='sent_to_production',
            stage='printing'
        )
        
        url = reverse('production-wip-count')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['current'] >= 1
    
    def test_wip_count_includes_getting_ready(self, authenticated_client, db):
        """Test that orders with status='getting_ready' are counted"""
        order = Order.objects.create(
            order_code='TEST-WIP-READY',
            client_name='Test Client',
            company_name='Test Company',
            phone='+971501111111',
            email='test@test.com',
            status='getting_ready',
            stage='printing'
        )
        
        url = reverse('production-wip-count')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['current'] >= 1
    
    def test_wip_count_empty(self, authenticated_client, db):
        """Test WIP count with no WIP orders"""
        # Ensure no WIP orders exist
        Order.objects.filter(
            status__in=['sent_to_production', 'getting_ready']
        ).delete()
        
        url = reverse('production-wip-count')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['current'] == 0


@pytest.mark.django_db
class TestProductionTurnaroundTime:
    """Test production_turnaround_time endpoint"""
    
    def test_turnaround_time_basic(self, authenticated_client, test_orders):
        """Test basic turnaround time calculation"""
        url = reverse('production-turnaround')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert 'average_days' in response.data
        assert 'period' in response.data
        assert response.data['average_days'] >= 0
    
    def test_turnaround_time_calculation(self, authenticated_client, db):
        """Test turnaround time calculation accuracy"""
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        
        # Clear any existing delivered orders in the last 7 days to isolate this test
        Order.objects.filter(
            delivered_at__gte=last_7_days,
            delivered_at__isnull=False
        ).delete()
        
        # Create order created 5 days ago, delivered 2 days ago (3 day turnaround)
        # Ensure delivered_at is within last 7 days for the endpoint filter
        # created_at must be BEFORE delivered_at
        delivered_at = now - timedelta(days=2)  # 2 days ago
        created_at = delivered_at - timedelta(days=3)  # 3 days before delivery = 5 days ago total
        
        # Verify dates are correct
        assert delivered_at >= last_7_days, f"delivered_at ({delivered_at}) must be >= last_7_days ({last_7_days})"
        assert delivered_at > created_at, f"delivered_at ({delivered_at}) must be > created_at ({created_at})"
        assert (delivered_at - created_at).days == 3, f"Expected 3 day turnaround, got {(delivered_at - created_at).days} days"
        
        # Create order and then update dates (since created_at has auto_now_add)
        order = Order.objects.create(
            order_code='TEST-TAT-001',
            client_name='Test Client',
            company_name='Test Company',
            phone='+971501111111',
            email='test@test.com',
            status='delivered'
        )
        # Update dates after creation to override auto_now_add
        order.created_at = created_at
        order.delivered_at = delivered_at
        order.save(update_fields=['created_at', 'delivered_at'])
        
        # Refresh from database
        order.refresh_from_db()
        
        # Verify order was created correctly
        assert order.delivered_at is not None
        assert order.created_at is not None
        assert order.delivered_at >= last_7_days
        assert order.delivered_at > order.created_at, f"delivered_at ({order.delivered_at}) must be > created_at ({order.created_at})"
        
        # Verify the endpoint query would find it
        matching_orders = Order.objects.filter(
            delivered_at__gte=last_7_days,
            delivered_at__isnull=False,
            created_at__isnull=False
        )
        assert matching_orders.filter(id=order.id).exists(), "Order should be found by endpoint query"
        
        url = reverse('production-turnaround')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        # Should be approximately 3 days (allowing for rounding)
        # The calculation is (delivered_at - created_at).total_seconds() / 86400
        # 5 days ago to 2 days ago = 3 days
        assert response.data['average_days'] > 0, f"Expected positive turnaround, got {response.data['average_days']}. Order: {order.id}, delivered_at: {order.delivered_at}, created_at: {order.created_at}"
        assert 2.5 <= response.data['average_days'] <= 3.5, f"Expected ~3 days, got {response.data['average_days']}"
    
    def test_turnaround_time_empty(self, authenticated_client, db):
        """Test turnaround time with no delivered orders"""
        Order.objects.filter(status='delivered').delete()
        
        url = reverse('production-turnaround')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['average_days'] == 0.0
    
    def test_turnaround_time_never_negative(self, authenticated_client, db):
        """Test that turnaround time is never negative, even with bad data"""
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        
        # Clear any existing delivered orders in the last 7 days
        Order.objects.filter(
            delivered_at__gte=last_7_days,
            delivered_at__isnull=False
        ).delete()
        
        # Create order with INVALID data: delivered_at BEFORE created_at
        # This should be filtered out and not cause negative result
        order = Order.objects.create(
            order_code='TEST-BAD-DATA-001',
            client_name='Test Client',
            company_name='Test Company',
            phone='+971501111111',
            email='test@test.com',
            status='delivered'
        )
        # Set delivered_at BEFORE created_at (invalid scenario)
        order.delivered_at = now - timedelta(days=2)
        order.created_at = now - timedelta(days=1)  # Created AFTER delivery (impossible but could happen with bad data)
        order.save(update_fields=['delivered_at', 'created_at'])
        
        url = reverse('production-turnaround')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        # Should return 0, not negative, even with bad data
        assert response.data['average_days'] >= 0, f"Turnaround time should never be negative, got {response.data['average_days']}"
        assert response.data['average_days'] == 0, "Bad data should result in 0, not negative"


@pytest.mark.django_db
class TestProductionMachineUtilization:
    """Test production_machine_utilization endpoint"""
    
    def test_machine_utilization_basic(self, authenticated_client, test_machine_assignments):
        """Test basic machine utilization calculation"""
        url = reverse('production-machine-util')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert 'overall_utilization' in response.data
        assert 'peak_today' in response.data
        assert 'machines' in response.data
        assert isinstance(response.data['machines'], list)
    
    def test_machine_utilization_percentage(self, authenticated_client, db):
        """Test utilization percentage calculation"""
        now = timezone.now()
        today = now.date()
        
        order = Order.objects.create(
            order_code='TEST-UTIL-001',
            client_name='Test Client',
            company_name='Test Company',
            phone='+971501111111',
            email='test@test.com',
            status='sent_to_production'
        )
        OrderItem.objects.create(
            order=order,
            product_id='PROD-001',
            name='Product',
            sku='SKU-001',
            quantity=50,
            unit_price=Decimal('10.00'),
            line_total=Decimal('100.00')
        )
        
        # Create assignment that started today and completed (60 minutes)
        started_at = timezone.make_aware(datetime.combine(today, time(9, 0, 0)))
        completed_at = started_at + timedelta(minutes=60)
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Product',
            product_sku='SKU-001',
            product_quantity=50,
            machine_id='TEST-MACHINE',
            machine_name='Test Machine',
            estimated_time_minutes=60,
            started_at=started_at,
            completed_at=completed_at,
            status='completed',
            assigned_by='test_user'
        )
        
        url = reverse('production-machine-util')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        # 60 minutes / 480 minutes (8 hours) = 12.5%
        assert 10 <= response.data['overall_utilization'] <= 15


@pytest.mark.django_db
class TestProductionReprintRate:
    """Test production_reprint_rate endpoint"""
    
    def test_reprint_rate_basic(self, authenticated_client, test_reprint_orders):
        """Test basic reprint rate calculation"""
        url = reverse('production-reprint-rate')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert 'current_rate' in response.data
        assert 'change' in response.data
        assert 'change_direction' in response.data
        assert 0 <= response.data['current_rate'] <= 100
    
    def test_reprint_rate_calculation(self, authenticated_client, db):
        """Test reprint rate calculation accuracy"""
        now = timezone.now()
        week_start = now - timedelta(days=now.weekday())
        
        # Create 10 orders this week, 2 are reprints (20% rate)
        for i in range(10):
            is_reprint = i < 2
            Order.objects.create(
                order_code=f'TEST-RATE-{i+1:03d}',
                client_name='Test Client',
                company_name='Test Company',
                phone='+971501111111',
                email='test@test.com',
                status='sent_to_production',
                created_at=week_start + timedelta(days=i % 7),
                is_reprint=is_reprint
            )
        
        url = reverse('production-reprint-rate')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        # Should be approximately 20%
        assert 15 <= response.data['current_rate'] <= 25


@pytest.mark.django_db
class TestProductionQueue:
    """Test production_queue endpoint"""
    
    def test_production_queue_basic(self, authenticated_client, test_machine_assignments):
        """Test basic production queue"""
        url = reverse('production-queue')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert isinstance(response.data, list)
    
    def test_production_queue_eta_formatting(self, authenticated_client, db):
        """Test ETA formatting (Today/Tomorrow)"""
        now = timezone.now()
        today = now.date()
        
        order = Order.objects.create(
            order_code='TEST-QUEUE-001',
            client_name='Test Client',
            company_name='Test Company',
            phone='+971501111111',
            email='test@test.com',
            status='sent_to_production'
        )
        OrderItem.objects.create(
            order=order,
            product_id='PROD-001',
            name='Product',
            sku='SKU-001',
            quantity=50,
            unit_price=Decimal('10.00'),
            line_total=Decimal('100.00')
        )
        
        # Create assignment that started today
        started_at = timezone.make_aware(datetime.combine(today, time(14, 0, 0)))
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Product',
            product_sku='SKU-001',
            product_quantity=50,
            machine_id='TEST-MACHINE',
            machine_name='Test Machine',
            estimated_time_minutes=60,
            started_at=started_at,
            status='in_progress',
            assigned_by='test_user'
        )
        
        url = reverse('production-queue')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) > 0
        assert 'eta' in response.data[0]
        assert 'Today' in response.data[0]['eta'] or 'Tomorrow' in response.data[0]['eta']


@pytest.mark.django_db
class TestProductionJobsByStage:
    """Test production_jobs_by_stage endpoint"""
    
    def test_jobs_by_stage_basic(self, authenticated_client, test_machine_assignments):
        """Test basic jobs by stage"""
        url = reverse('production-jobs-by-stage')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert 'Printing' in response.data
        assert 'Cutting' in response.data
        assert 'Lamination' in response.data
        assert 'Mounting' in response.data
        assert 'QA' in response.data
    
    def test_jobs_by_stage_machine_mapping(self, authenticated_client, db):
        """Test stage mapping based on machine names"""
        order = Order.objects.create(
            order_code='TEST-STAGE-001',
            client_name='Test Client',
            company_name='Test Company',
            phone='+971501111111',
            email='test@test.com',
            status='sent_to_production'
        )
        OrderItem.objects.create(
            order=order,
            product_id='PROD-001',
            name='Product',
            sku='SKU-001',
            quantity=50,
            unit_price=Decimal('10.00'),
            line_total=Decimal('100.00')
        )
        
        # Create assignment with printer machine name
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Product',
            product_sku='SKU-001',
            product_quantity=50,
            machine_id='HP-LATEX',
            machine_name='HP Latex 570 Printer',
            estimated_time_minutes=60,
            status='in_progress',
            assigned_by='test_user'
        )
        
        url = reverse('production-jobs-by-stage')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.data['Printing'] >= 1


@pytest.mark.django_db
class TestProductionMaterialUsage:
    """Test production_material_usage endpoint"""
    
    def test_material_usage_basic(self, authenticated_client, test_inventory_data):
        """Test basic material usage"""
        url = reverse('production-material-usage')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert isinstance(response.data, list)
    
    def test_material_usage_grouping(self, authenticated_client, db):
        """Test material grouping by name"""
        # Create inventory item
        item = InventoryItem.objects.create(
            sku='TEST-MAT-001',
            name='Test Material',
            quantity=100,
            minimum_stock=50
        )
        
        # Create multiple movements for same material
        now = timezone.now()
        for i in range(3):
            InventoryMovement.objects.create(
                order_id=1000 + i,
                sku='TEST-MAT-001',
                delta=-10,
                reason='Test consumption',
                created_at=now - timedelta(days=i)
            )
        
        url = reverse('production-material-usage')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        # Should have one entry with 30 total used
        test_material = next((m for m in response.data if m['material'] == 'Test Material'), None)
        assert test_material is not None
        assert test_material['used'] == 30
        assert test_material['reorder_threshold'] == 50


@pytest.mark.django_db
class TestProductionDeliveryHandoff:
    """Test production_delivery_handoff endpoint"""
    
    def test_delivery_handoff_basic(self, authenticated_client, test_delivery_orders):
        """Test basic delivery handoff"""
        url = reverse('production-delivery-handoff')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert isinstance(response.data, list)
    
    def test_delivery_handoff_filtering(self, authenticated_client, db):
        """Test that only sent_for_delivery orders are returned"""
        # Create order with sent_for_delivery status
        order = Order.objects.create(
            order_code='TEST-DELIVERY-FILTER',
            client_name='Test Client',
            company_name='Test Company',
            phone='+971501111111',
            email='test@test.com',
            status='sent_for_delivery',
            stage='delivery'
        )
        OrderItem.objects.create(
            order=order,
            product_id='PROD-001',
            name='Product',
            sku='SKU-001',
            quantity=50,
            unit_price=Decimal('10.00'),
            line_total=Decimal('100.00')
        )
        
        url = reverse('production-delivery-handoff')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.data) > 0
        assert any(item['order_code'] == 'TEST-DELIVERY-FILTER' for item in response.data)

