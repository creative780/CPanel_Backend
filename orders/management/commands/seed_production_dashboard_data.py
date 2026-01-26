from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime, time
from decimal import Decimal
from orders.models import Order, OrderItem, ProductMachineAssignment
from inventory.models import InventoryItem, InventoryMovement
import random


class Command(BaseCommand):
    help = 'Seed the database with comprehensive test data for production dashboard metrics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            # Clear test data (be careful in production!)
            # We'll only clear orders with specific test prefixes
            # Delete related objects first to avoid foreign key issues
            test_orders = list(Order.objects.filter(order_code__startswith='TEST-').values_list('id', flat=True))
            if test_orders:
                # Delete machine assignments first
                from orders.models import ProductMachineAssignment
                ProductMachineAssignment.objects.filter(order_id__in=test_orders).delete()
                # Delete order items
                from orders.models import OrderItem
                OrderItem.objects.filter(order_id__in=test_orders).delete()
                # Delete orders one by one to handle any other foreign key constraints
                for order_id in test_orders:
                    try:
                        Order.objects.filter(id=order_id).delete()
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Could not delete order {order_id}: {e}'))
            InventoryMovement.objects.filter(reason__icontains='test').delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing test data'))

        self.stdout.write('Creating production dashboard test data...')
        
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        last_7_days = now - timedelta(days=7)
        
        # Create test data for each metric
        wip_orders = self.create_wip_orders(today, yesterday)
        completed_orders = self.create_completed_orders(last_7_days, now)
        machine_assignments = self.create_machine_assignments(today, now)
        reprint_orders = self.create_reprint_orders(now)
        inventory_data = self.create_inventory_movements(last_7_days)
        delivery_orders = self.create_delivery_ready_orders(now)
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n=== Test Data Summary ==='))
        self.stdout.write(f'WIP Orders: {wip_orders}')
        self.stdout.write(f'Completed Orders (for turnaround): {completed_orders}')
        self.stdout.write(f'Machine Assignments: {machine_assignments}')
        self.stdout.write(f'Reprint Orders: {reprint_orders}')
        self.stdout.write(f'Inventory Movements: {inventory_data}')
        self.stdout.write(f'Delivery Ready Orders: {delivery_orders}')
        self.stdout.write(self.style.SUCCESS('\nSuccessfully created all test data!'))

    def create_wip_orders(self, today, yesterday):
        """Create orders in WIP status for Jobs in WIP count"""
        count = 0
        machines = [
            ('HP-LATEX-570', 'HP Latex 570'),
            ('HP-LATEX-800W', 'HP Latex 800W'),
            ('MIMAKI-JV150', 'Mimaki JV150'),
            ('EPSON-S80600', 'Epson S80600'),
            ('SUMMA-CUTTER', 'Summa Cutter'),
            ('LAMINATOR-1', 'Laminator 1'),
        ]
        
        # Create orders with status='sent_to_production'
        for i in range(5):
            order_code = f'TEST-WIP-{i+1:03d}'
            order, created = Order.objects.get_or_create(
                order_code=order_code,
                defaults={
                    'client_name': f'Test Client WIP {i+1}',
                    'company_name': f'Test Company {i+1}',
                    'phone': f'+9715012345{i:02d}',
                    'email': f'wip{i+1}@test.com',
                    'address': 'Dubai, UAE',
                    'specs': f'Test order for WIP metric {i+1}',
                    'urgency': random.choice(['Normal', 'High', 'Urgent']),
                    'status': 'sent_to_production',
                    'stage': 'printing',
                    'created_at': timezone.make_aware(datetime.combine(
                        today if i < 3 else yesterday, 
                        time(9, 0, 0)
                    )) - timedelta(hours=i)
                }
            )
            
            # Add order items (only if order was just created)
            if created or not order.items.exists():
                OrderItem.objects.get_or_create(
                    order=order,
                    product_id=f'PROD-WIP-{i+1}',
                    defaults={
                        'name': f'Product {i+1}',
                        'sku': f'SKU-WIP-{i+1}',
                        'quantity': random.randint(10, 100),
                        'unit_price': Decimal('10.00'),
                        'line_total': Decimal('100.00')
                    }
                )
            count += 1
        
        # Create orders with status='getting_ready'
        for i in range(3):
            order_code = f'TEST-READY-{i+1:03d}'
            order, created = Order.objects.get_or_create(
                order_code=order_code,
                defaults={
                    'client_name': f'Test Client Ready {i+1}',
                    'company_name': f'Test Company Ready {i+1}',
                    'phone': f'+9715012346{i:02d}',
                    'email': f'ready{i+1}@test.com',
                    'address': 'Dubai, UAE',
                    'specs': f'Test order for getting ready status {i+1}',
                    'urgency': 'Normal',
                    'status': 'getting_ready',
                    'stage': 'printing',
                    'created_at': timezone.make_aware(datetime.combine(today, time(10, 0, 0))) - timedelta(hours=i)
                }
            )
            
            if created or not order.items.exists():
                OrderItem.objects.get_or_create(
                    order=order,
                    product_id=f'PROD-READY-{i+1}',
                    defaults={
                        'name': f'Product Ready {i+1}',
                        'sku': f'SKU-READY-{i+1}',
                        'quantity': random.randint(20, 50),
                        'unit_price': Decimal('15.00'),
                        'line_total': Decimal('150.00')
                    }
                )
            count += 1
        
        return count

    def create_completed_orders(self, last_7_days, now):
        """Create completed orders for turnaround time calculation"""
        count = 0
        
        # Create orders delivered at different times in last 7 days
        for i in range(15):
            days_ago = random.randint(0, 7)
            delivered_date = now - timedelta(days=days_ago)
            created_date = delivered_date - timedelta(days=random.randint(1, 5))
            
            # Ensure dates are timezone-aware (they already are from now - timedelta)
            if timezone.is_naive(created_date):
                created_date = timezone.make_aware(created_date)
            if timezone.is_naive(delivered_date):
                delivered_date = timezone.make_aware(delivered_date)
            
            order_code = f'TEST-DEL-{i+1:03d}'
            order, created = Order.objects.get_or_create(
                order_code=order_code,
                defaults={
                    'client_name': f'Test Client Delivered {i+1}',
                    'company_name': f'Test Company Delivered {i+1}',
                    'phone': f'+9715012347{i:02d}',
                    'email': f'delivered{i+1}@test.com',
                    'address': 'Dubai, UAE',
                    'specs': f'Test order for turnaround time {i+1}',
                    'urgency': random.choice(['Normal', 'High']),
                    'status': 'delivered',
                    'stage': 'delivery',
                    'created_at': created_date,
                    'delivered_at': delivered_date,
                    'delivery_code': f'{random.randint(100000, 999999)}'
                }
            )
            
            OrderItem.objects.create(
                order=order,
                product_id=f'PROD-DEL-{i+1}',
                name=f'Product Delivered {i+1}',
                sku=f'SKU-DEL-{i+1}',
                quantity=random.randint(10, 200),
                unit_price=Decimal('20.00'),
                line_total=Decimal('200.00')
            )
            count += 1
        
        return count

    def create_machine_assignments(self, today, now):
        """Create machine assignments for utilization and queue"""
        count = 0
        machines = [
            ('HP-LATEX-570', 'HP Latex 570'),
            ('HP-LATEX-800W', 'HP Latex 800W'),
            ('MIMAKI-JV150', 'Mimaki JV150'),
            ('EPSON-S80600', 'Epson S80600'),
            ('SUMMA-CUTTER', 'Summa Cutter'),
            ('LAMINATOR-1', 'Laminator 1'),
        ]
        
        # Get or create WIP orders for assignments
        wip_orders = list(Order.objects.filter(order_code__startswith='TEST-WIP')[:6])
        if len(wip_orders) < 6:
            # Create additional orders if needed
            for i in range(6 - len(wip_orders)):
                order = Order.objects.create(
                    order_code=f'TEST-ASSIGN-{i+1:03d}',
                    client_name=f'Test Client Assign {i+1}',
                    company_name=f'Test Company Assign {i+1}',
                    phone=f'+9715012348{i:02d}',
                    email=f'assign{i+1}@test.com',
                    address='Dubai, UAE',
                    specs=f'Test order for assignments {i+1}',
                    status='sent_to_production',
                    stage='printing'
                )
                OrderItem.objects.create(
                    order=order,
                    product_id=f'PROD-ASSIGN-{i+1}',
                    name=f'Product Assign {i+1}',
                    sku=f'SKU-ASSIGN-{i+1}',
                    quantity=50,
                    unit_price=Decimal('10.00'),
                    line_total=Decimal('100.00')
                )
                wip_orders.append(order)
        
        # Create assignments with different statuses
        for i, (machine_id, machine_name) in enumerate(machines):
            if i < len(wip_orders):
                order = wip_orders[i]
                
                # Get first order item
                order_item = order.items.first()
                if not order_item:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product_id=f'PROD-{order.order_code}',
                        name='Test Product',
                        sku=f'SKU-{order.order_code}',
                        quantity=50,
                        unit_price=Decimal('10.00'),
                        line_total=Decimal('100.00')
                    )
                
                estimated_time = random.randint(30, 180)
                status = random.choice(['queued', 'in_progress', 'completed'])
                
                started_at = None
                completed_at = None
                
                if status == 'in_progress':
                    # Started today
                    started_at = timezone.make_aware(datetime.combine(today, time(9, 0, 0))) + timedelta(hours=i)
                elif status == 'completed':
                    # Started and completed today
                    started_at = timezone.make_aware(datetime.combine(today, time(8, 0, 0))) + timedelta(hours=i)
                    completed_at = started_at + timedelta(minutes=estimated_time)
                
                assignment = ProductMachineAssignment.objects.create(
                    order=order,
                    product_name=order_item.name,
                    product_sku=order_item.sku,
                    product_quantity=order_item.quantity,
                    machine_id=machine_id,
                    machine_name=machine_name,
                    estimated_time_minutes=estimated_time,
                    started_at=started_at,
                    completed_at=completed_at,
                    status=status,
                    assigned_by='test_production_user',
                    notes=f'Test assignment for {machine_name}'
                )
                count += 1
        
        # Create additional assignments for variety
        for i in range(4):
            order = wip_orders[i % len(wip_orders)] if wip_orders else wip_orders[0]
            order_item = order.items.first()
            
            machine_id, machine_name = random.choice(machines)
            estimated_time = random.randint(45, 120)
            
            assignment = ProductMachineAssignment.objects.create(
                order=order,
                product_name=order_item.name if order_item else 'Test Product',
                product_sku=order_item.sku if order_item else 'TEST-SKU',
                product_quantity=order_item.quantity if order_item else 50,
                machine_id=machine_id,
                machine_name=machine_name,
                estimated_time_minutes=estimated_time,
                status='queued',
                assigned_by='test_production_user',
                notes='Additional test assignment'
            )
            count += 1
        
        return count

    def create_reprint_orders(self, now):
        """Create reprint orders for reprint rate calculation"""
        count = 0
        
        # First, create some original orders
        original_orders = []
        for i in range(5):
            order = Order.objects.create(
                order_code=f'TEST-ORIG-{i+1:03d}',
                client_name=f'Test Client Original {i+1}',
                company_name=f'Test Company Original {i+1}',
                phone=f'+9715012349{i:02d}',
                email=f'original{i+1}@test.com',
                address='Dubai, UAE',
                specs=f'Original test order {i+1}',
                status='delivered',
                stage='delivery',
                created_at=now - timedelta(days=random.randint(10, 20)),
                delivered_at=now - timedelta(days=random.randint(5, 10)),
                is_reprint=False
            )
            OrderItem.objects.create(
                order=order,
                product_id=f'PROD-ORIG-{i+1}',
                name=f'Original Product {i+1}',
                sku=f'SKU-ORIG-{i+1}',
                quantity=100,
                unit_price=Decimal('25.00'),
                line_total=Decimal('250.00')
            )
            original_orders.append(order)
        
        # Create reprint orders (some this week, some last week)
        week_start = now - timedelta(days=now.weekday())
        last_week_start = week_start - timedelta(days=7)
        
        # This week reprints
        for i in range(3):
            original = original_orders[i]
            order = Order.objects.create(
                order_code=f'TEST-REPRINT-{i+1:03d}',
                client_name=original.client_name,
                company_name=original.company_name,
                phone=original.phone,
                email=original.email,
                address=original.address,
                specs=f'Reprint of {original.order_code}',
                status='sent_to_production',
                stage='printing',
                created_at=week_start + timedelta(days=random.randint(0, 6), hours=random.randint(9, 17)),
                is_reprint=True,
                original_order=original
            )
            OrderItem.objects.create(
                order=order,
                product_id=f'PROD-REPRINT-{i+1}',
                name=f'Reprint Product {i+1}',
                sku=f'SKU-REPRINT-{i+1}',
                quantity=100,
                unit_price=Decimal('25.00'),
                line_total=Decimal('250.00')
            )
            count += 1
        
        # Last week reprints
        for i in range(2):
            original = original_orders[i + 3]
            order = Order.objects.create(
                order_code=f'TEST-REPRINT-LW-{i+1:03d}',
                client_name=original.client_name,
                company_name=original.company_name,
                phone=original.phone,
                email=original.email,
                address=original.address,
                specs=f'Reprint of {original.order_code} (last week)',
                status='delivered',
                stage='delivery',
                created_at=last_week_start + timedelta(days=random.randint(0, 6), hours=random.randint(9, 17)),
                delivered_at=last_week_start + timedelta(days=random.randint(1, 6)),
                is_reprint=True,
                original_order=original
            )
            OrderItem.objects.create(
                order=order,
                product_id=f'PROD-REPRINT-LW-{i+1}',
                name=f'Reprint Product LW {i+1}',
                sku=f'SKU-REPRINT-LW-{i+1}',
                quantity=100,
                unit_price=Decimal('25.00'),
                line_total=Decimal('250.00')
            )
            count += 1
        
        return count

    def create_inventory_movements(self, last_7_days):
        """Create inventory movements for material usage"""
        count = 0
        materials = [
            ('VINYL-001', 'Vinyl Roll', 100),
            ('FABRIC-001', 'Fabric Material', 50),
            ('PAPER-001', 'Paper Stock', 200),
            ('INK-CMYK', 'Ink CMYK Set', 20),
            ('LAM-001', 'Lamination Film', 75),
        ]
        
        # Create inventory items
        for sku, name, min_stock in materials:
            InventoryItem.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'quantity': random.randint(50, 500),
                    'minimum_stock': min_stock,
                    'category': 'raw_materials'
                }
            )
        
        # Create movements (consumption = negative delta)
        for i in range(20):
            sku, name, _ = random.choice(materials)
            delta = -random.randint(5, 50)  # Negative for consumption
            movement_date = last_7_days + timedelta(
                days=random.randint(0, 6),
                hours=random.randint(8, 18)
            )
            
            # Create movement with custom created_at
            movement = InventoryMovement(
                order_id=random.randint(1, 1000) if random.random() > 0.3 else None,
                sku=sku,
                delta=delta,
                reason=f'Test consumption for {name}',
                created_at=movement_date
            )
            movement.save()
            count += 1
        
        return count

    def create_delivery_ready_orders(self, now):
        """Create orders ready for delivery"""
        count = 0
        
        for i in range(5):
            order = Order.objects.create(
                order_code=f'TEST-DELIVERY-{i+1:03d}',
                client_name=f'Test Client Delivery {i+1}',
                company_name=f'Test Company Delivery {i+1}',
                phone=f'+9715012350{i:02d}',
                email=f'delivery{i+1}@test.com',
                address='Dubai, UAE',
                specs=f'Test order ready for delivery {i+1}',
                urgency=random.choice(['Normal', 'High']),
                status='sent_for_delivery',
                stage='delivery',
                delivery_code=f'{random.randint(100000, 999999)}' if i < 3 else None,
                created_at=now - timedelta(days=random.randint(1, 5)),
                updated_at=now - timedelta(hours=random.randint(1, 12))
            )
            
            # Add multiple items to some orders
            num_items = random.randint(1, 3)
            for j in range(num_items):
                OrderItem.objects.create(
                    order=order,
                    product_id=f'PROD-DELIVERY-{i+1}-{j+1}',
                    name=f'Product {j+1} for Delivery {i+1}',
                    sku=f'SKU-DELIVERY-{i+1}-{j+1}',
                    quantity=random.randint(10, 100),
                    unit_price=Decimal('15.00'),
                    line_total=Decimal('150.00')
                )
            count += 1
        
        return count

