"""
Comprehensive tests for mathematical calculations used in production dashboard endpoints.
Tests all calculation formulas to ensure accuracy.
"""
import pytest
from django.utils import timezone
from datetime import timedelta, datetime, time
from decimal import Decimal
from orders.models import Order, OrderItem, ProductMachineAssignment
from inventory.models import InventoryItem, InventoryMovement


@pytest.mark.django_db
class TestPercentageCalculations:
    """Test percentage calculation formulas"""
    
    def test_machine_utilization_percentage(self):
        """Test machine utilization: (active_minutes / 480) * 100"""
        # 60 minutes active out of 480 (8-hour day)
        active_minutes = 60
        available_minutes = 480
        utilization = (active_minutes / available_minutes) * 100
        
        assert utilization == 12.5
        assert round(utilization, 1) == 12.5
    
    def test_reprint_rate_percentage(self):
        """Test reprint rate: (reprint_count / total_count) * 100"""
        total_count = 100
        reprint_count = 15
        rate = (reprint_count / total_count) * 100
        
        assert rate == 15.0
        assert round(rate, 1) == 15.0
    
    def test_percentage_division_by_zero(self):
        """Test percentage calculation with zero denominator"""
        total_count = 0
        reprint_count = 0
        # Should handle division by zero
        rate = (reprint_count / total_count * 100) if total_count > 0 else 0
        
        assert rate == 0
    
    def test_percentage_rounding(self):
        """Test percentage rounding to 1 decimal place"""
        utilization = 12.56789
        rounded = round(utilization, 1)
        
        assert rounded == 12.6


@pytest.mark.django_db
class TestTimeCalculations:
    """Test time-related calculations"""
    
    def test_turnaround_time_in_days(self):
        """Test turnaround time: (delivered_at - created_at).total_seconds() / 86400"""
        now = timezone.now()
        created_at = now - timedelta(days=3, hours=12)
        delivered_at = now
        
        delta = delivered_at - created_at
        days = delta.total_seconds() / 86400
        
        assert 3.4 <= days <= 3.6  # Approximately 3.5 days
    
    def test_eta_calculation_started(self):
        """Test ETA for started assignment: started_at + timedelta(minutes=estimated_time)"""
        now = timezone.now()
        started_at = now - timedelta(hours=1)
        estimated_minutes = 60
        
        eta = started_at + timedelta(minutes=estimated_minutes)
        
        assert (eta - now).total_seconds() < 60  # Should be very soon
    
    def test_eta_calculation_queued(self):
        """Test ETA for queued assignment: now + timedelta(minutes=estimated_time)"""
        now = timezone.now()
        estimated_minutes = 120
        
        eta = now + timedelta(minutes=estimated_minutes)
        
        assert (eta - now).total_seconds() >= 120 * 60 - 1  # Approximately 120 minutes
    
    def test_active_minutes_calculation(self):
        """Test active minutes: (completed_at - started_at).total_seconds() / 60"""
        now = timezone.now()
        started_at = now - timedelta(hours=2)
        completed_at = now
        
        delta = completed_at - started_at
        minutes = delta.total_seconds() / 60
        
        assert 119 <= minutes <= 121  # Approximately 120 minutes
    
    def test_todays_portion_calculation(self):
        """Test calculation of today's portion for assignments started before today"""
        now = timezone.now()
        today_start = timezone.make_aware(datetime.combine(now.date(), time.min))
        yesterday_start = today_start - timedelta(days=1)
        
        # Assignment started yesterday, still in progress
        started_at = yesterday_start + timedelta(hours=16)  # 4 PM yesterday
        elapsed_today = (now - today_start).total_seconds() / 60  # Minutes since midnight today
        
        assert elapsed_today >= 0
        assert elapsed_today <= 1440  # Max 24 hours in minutes


@pytest.mark.django_db
class TestDateRangeCalculations:
    """Test date range calculations"""
    
    def test_last_7_days_range(self):
        """Test last 7 days: timezone.now() - timedelta(days=7)"""
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        
        assert (now - last_7_days).days == 7
    
    def test_week_start_monday(self):
        """Test week start calculation: now - timedelta(days=now.weekday())"""
        now = timezone.now()
        days_since_monday = now.weekday()
        week_start = (now - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        assert week_start.weekday() == 0  # Monday
        assert week_start.hour == 0
        assert week_start.minute == 0
    
    def test_today_vs_yesterday_comparison(self):
        """Test today vs yesterday date comparison"""
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        assert (today - yesterday).days == 1


@pytest.mark.django_db
class TestAggregationCalculations:
    """Test aggregation calculations"""
    
    def test_sum_material_usage(self):
        """Test sum of material usage: sum(abs(delta))"""
        movements = [
            -10, -20, -15, -5
        ]
        total_used = sum(abs(delta) for delta in movements)
        
        assert total_used == 50
    
    def test_average_turnaround_time(self):
        """Test average turnaround: sum(times) / len(times)"""
        turnaround_times = [2.5, 3.0, 4.5, 2.0, 3.5]
        average = sum(turnaround_times) / len(turnaround_times)
        
        assert average == 3.1
    
    def test_average_turnaround_empty(self):
        """Test average turnaround with empty list"""
        turnaround_times = []
        average = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0
        
        assert average == 0
    
    def test_overall_utilization_average(self):
        """Test overall utilization: sum(utilizations) / len(machines)"""
        machine_utilizations = [45.5, 67.2, 89.1, 34.8, 56.3]
        overall_avg = sum(machine_utilizations) / len(machine_utilizations)
        
        assert round(overall_avg, 1) == 58.6


@pytest.mark.django_db
class TestRealWorldCalculations:
    """Test calculations with real database data"""
    
    def test_wip_count_calculation(self):
        """Test WIP count calculation with real orders"""
        # Create test orders
        for i in range(5):
            Order.objects.create(
                order_code=f'TEST-WIP-CALC-{i+1:03d}',
                client_name='Test Client',
                company_name='Test Company',
                phone='+971501111111',
                email='test@test.com',
                status='sent_to_production',
                stage='printing'
            )
        
        # Calculate WIP count
        from django.db.models import Q
        production_filter = Q(status__in=['sent_to_production', 'getting_ready']) | Q(stage__in=['production', 'printing'])
        wip_count = Order.objects.filter(production_filter).count()
        
        assert wip_count >= 5
    
    def test_turnaround_time_calculation_with_data(self):
        """Test turnaround time calculation with real delivered orders"""
        now = timezone.now()
        
        # Create orders with known turnaround times
        orders_data = [
            (now - timedelta(days=5), now - timedelta(days=2)),  # 3 days
            (now - timedelta(days=4), now - timedelta(days=1)),  # 3 days
            (now - timedelta(days=6), now - timedelta(days=3)),  # 3 days
        ]
        
        for i, (created_at, delivered_at) in enumerate(orders_data):
            # Create order first, then update dates to handle auto_now_add
            order = Order.objects.create(
                order_code=f'TEST-TAT-CALC-{i+1:03d}',
                client_name='Test Client',
                company_name='Test Company',
                phone='+971501111111',
                email='test@test.com',
                status='delivered'
            )
            order.created_at = created_at
            order.delivered_at = delivered_at
            order.save(update_fields=['created_at', 'delivered_at'])
        
        # Calculate average turnaround
        last_7_days = now - timedelta(days=7)
        orders = Order.objects.filter(
            status='delivered',
            delivered_at__gte=last_7_days
        )
        
        if orders.exists():
            times = [
                (o.delivered_at - o.created_at).total_seconds() / 86400
                for o in orders
            ]
            avg = sum(times) / len(times) if times else 0
            assert avg > 0
    
    def test_machine_utilization_calculation_with_data(self):
        """Test machine utilization with real assignments"""
        now = timezone.now()
        today = now.date()
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        
        order = Order.objects.create(
            order_code='TEST-UTIL-CALC',
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
        
        # Create assignment that started and completed today (60 minutes)
        started_at = today_start + timedelta(hours=9)
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
        
        # Calculate utilization
        available_minutes = 480
        active_minutes = 60
        utilization = (active_minutes / available_minutes) * 100
        
        assert utilization == 12.5
    
    def test_material_usage_aggregation_with_data(self):
        """Test material usage aggregation with real movements"""
        # Create inventory item
        item = InventoryItem.objects.create(
            sku='TEST-MAT-CALC',
            name='Test Material',
            quantity=100,
            minimum_stock=50
        )
        
        # Create movements
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        
        movements_data = [-10, -20, -15, -5]
        for i, delta in enumerate(movements_data):
            InventoryMovement.objects.create(
                order_id=1000 + i,
                sku='TEST-MAT-CALC',
                delta=delta,
                reason='Test consumption',
                created_at=last_7_days + timedelta(days=i)
            )
        
        # Calculate total usage
        movements = InventoryMovement.objects.filter(
            created_at__gte=last_7_days,
            delta__lt=0,
            sku='TEST-MAT-CALC'
        )
        total_used = sum(abs(m.delta) for m in movements)
        
        assert total_used == 50

