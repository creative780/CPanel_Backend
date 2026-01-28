from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
from decimal import Decimal
from orders.models import Order, OrderItem, Quotation
from inventory.models import InventoryItem, InventoryMovement
from attendance.models import Attendance
from monitoring.models import Employee
import random
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed test data for dashboard cards: sales stats, low stock, attendance, top products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding dashboard test data...')
        
        # Create sales statistics data
        self.create_sales_data()
        
        # Create low stock inventory items
        self.create_low_stock_items()
        
        # Create attendance data for today
        self.create_today_attendance()
        
        # Create top products data for this week
        self.create_top_products_data()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded dashboard test data!')
        )

    def create_sales_data(self):
        """Create orders and quotations across different months for sales statistics"""
        self.stdout.write('Creating sales statistics data...')
        
        now = timezone.now()
        current_year = now.year
        
        # Create orders for each month of current year
        for month in range(1, 13):
            month_start = timezone.make_aware(datetime(current_year, month, 1))
            
            # Create 3-5 orders per month
            for i in range(random.randint(3, 5)):
                order_date = month_start + timedelta(days=random.randint(0, 27))
                
                # Use a more unique order code to avoid conflicts (max 20 chars)
                unique_suffix = str(uuid.uuid4())[:4].upper()
                order_code = f'D{month:02d}{i:03d}{unique_suffix}'
                
                order, created = Order.objects.get_or_create(
                    order_code=order_code,
                    client_name=f'Client {month}-{i}',
                    company_name=f'Company {month}-{i}',
                    phone=f'+9715{random.randint(10000000, 99999999)}',
                    email=f'client{month}{i}@example.com',
                    address='Dubai, UAE',
                    specs=f'Sample order for month {month}',
                    urgency=random.choice(['Normal', 'High', 'Urgent']),
                    status=random.choice(['delivered', 'completed', 'sent_for_delivery']),
                    stage='delivery',
                    created_at=order_date,
                    delivered_at=order_date + timedelta(days=random.randint(5, 15)) if random.random() > 0.3 else None
                )
                
                if not created:
                    # Order already exists, skip
                    continue
                
                # Create order items
                products = ['Business Cards', 'Brochures', 'Flyers', 'Banners', 'Posters']
                product = random.choice(products)
                quantity = random.randint(100, 1000)
                unit_price = Decimal(str(random.uniform(0.5, 5.0)))
                
                OrderItem.objects.create(
                    order=order,
                    product_id=f'PROD-{month}-{i}',
                    name=product,
                    sku=f'SKU-{month}-{i}',
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=quantity * unit_price
                )
                
                # Create quotation with realistic values
                products_subtotal = quantity * unit_price
                labour_cost = Decimal(str(random.uniform(50, 300)))
                finishing_cost = Decimal(str(random.uniform(100, 500)))
                paper_cost = Decimal(str(random.uniform(200, 800)))
                machine_cost = Decimal(str(random.uniform(50, 200)))
                design_cost = Decimal(str(random.uniform(100, 400)))
                delivery_cost = Decimal(str(random.uniform(20, 100)))
                other_subtotal = labour_cost + finishing_cost + paper_cost + machine_cost + design_cost + delivery_cost
                subtotal = products_subtotal + other_subtotal
                discount = Decimal(str(random.uniform(0, float(subtotal * Decimal('0.1')))))
                vat_3pct = (subtotal - discount) * Decimal('0.03')
                grand_total = subtotal - discount + vat_3pct
                
                Quotation.objects.create(
                    order=order,
                    labour_cost=labour_cost,
                    finishing_cost=finishing_cost,
                    paper_cost=paper_cost,
                    machine_cost=machine_cost,
                    design_cost=design_cost,
                    delivery_cost=delivery_cost,
                    discount=discount,
                    advance_paid=grand_total * Decimal('0.5'),
                    products_subtotal=products_subtotal,
                    other_subtotal=other_subtotal,
                    subtotal=subtotal,
                    vat_3pct=vat_3pct,
                    grand_total=grand_total,
                    remaining=grand_total - (grand_total * Decimal('0.5'))
                )
        
        self.stdout.write('  ✓ Created sales statistics data')

    def create_low_stock_items(self):
        """Create inventory items with low stock levels"""
        self.stdout.write('Creating low stock inventory items...')
        
        low_stock_items = [
            ('PAPER-A4', 'A4 Paper', 5, 20),
            ('INK-BLK', 'Black Ink Cartridge', 3, 15),
            ('INK-CMYK', 'CMYK Ink Set', 2, 10),
            ('VINYL-WHT', 'White Vinyl Roll', 8, 25),
            ('LAMINATE-GLS', 'Glossy Laminate Sheet', 4, 20),
            ('CARDSTOCK', 'Premium Cardstock', 10, 30),
            ('RIBBON', 'Ribbon Roll', 6, 20),
            ('BINDING-WIRE', 'Binding Wire', 1, 10),
            ('ENVELOPES', 'Business Envelopes', 7, 25),
            ('STICKERS', 'Sticker Sheets', 9, 30),
            ('BANNER-FAB', 'Fabric Banner Material', 5, 20),
            ('FOAM-BOARD', 'Foam Board Sheet', 3, 15),
        ]
        
        for sku, name, quantity, minimum in low_stock_items:
            item, created = InventoryItem.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'quantity': quantity,
                    'minimum_stock': minimum,
                    'category': 'raw_materials',
                    'unit': 'pcs',
                    'cost_price': Decimal(str(random.uniform(10, 100))),
                    'selling_price': Decimal(str(random.uniform(15, 150))),
                }
            )
            
            if not created:
                item.quantity = quantity
                item.minimum_stock = minimum
                item.save()
            
            # Create a restock movement record (some time ago)
            restock_date = timezone.now() - timedelta(days=random.randint(15, 60))
            InventoryMovement.objects.get_or_create(
                sku=sku,
                delta=minimum + random.randint(10, 50),
                reason='Restock',
                created_at=restock_date,
                defaults={'order_id': None}
            )
        
        self.stdout.write('  ✓ Created low stock inventory items')

    def create_today_attendance(self):
        """Create attendance records for today"""
        self.stdout.write('Creating today\'s attendance data...')
        
        # Ensure we have employees
        employees = []
        for i in range(20):
            emp, created = Employee.objects.get_or_create(
                email=f'employee{i}@company.com',
                defaults={
                    'name': f'Employee {i+1}',
                    'department': f'Dept {(i % 5) + 1}',
                    'status': 'active',
                    'salary': Decimal(str(3000 + i * 100))
                }
            )
            employees.append(emp)
        
        # Get or create users for employees (needed for attendance)
        today = timezone.now().date()
        work_start = timezone.make_aware(datetime.combine(today, datetime.min.time().replace(hour=9, minute=0)))
        
        # Create attendance for 14 employees (some on-time, some late)
        checked_in_count = 0
        on_time_count = 0
        late_count = 0
        
        for i, emp in enumerate(employees[:14]):
            # Get or create user for employee
            user, created = User.objects.get_or_create(
                username=emp.email.split('@')[0],
                defaults={
                    'email': emp.email,
                    'roles': ['production'] if i < 10 else ['sales'],
                }
            )
            
            # Determine if on-time (before 9:10 AM) or late (after 9:10 AM)
            if i < 10:  # 10 on-time
                check_in_time = work_start + timedelta(minutes=random.randint(-5, 10))
                status = Attendance.STATUS_PRESENT
                on_time_count += 1
            else:  # 4 late
                check_in_time = work_start + timedelta(minutes=random.randint(15, 45))
                status = Attendance.STATUS_LATE
                late_count += 1
            
            Attendance.objects.get_or_create(
                employee=user,
                date=today,
                defaults={
                    'check_in': check_in_time,
                    'status': status,
                    'total_hours': Decimal(str(random.uniform(7.5, 9.0))),
                }
            )
            checked_in_count += 1
        
        self.stdout.write(f'  ✓ Created attendance data: {checked_in_count} checked-in ({on_time_count} on-time, {late_count} late), {len(employees)} total employees')

    def create_top_products_data(self):
        """Create order items for this week for top products"""
        self.stdout.write('Creating top products data for this week...')
        
        now = timezone.now()
        days_since_monday = now.weekday()
        this_week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Product names and their sales quantities
        products_data = [
            ('Canvas Print A3', 124),
            ('Custom Mug', 98),
            ('Business Card Gold', 85),
            ('Banner 3x6ft', 67),
            ('Flyer A4', 156),
            ('Poster 24x36', 43),
            ('Brochure A5', 89),
            ('Sticker Sheet', 112),
            ('T-Shirt Print', 76),
            ('Logo Design', 54),
        ]
        
        for product_name, total_quantity in products_data:
            # Create multiple orders this week with this product
            orders_count = random.randint(5, 15)
            quantity_per_order = total_quantity // orders_count
            remainder = total_quantity % orders_count
            
            for i in range(orders_count):
                order_date = this_week_start + timedelta(days=random.randint(0, days_since_monday), hours=random.randint(9, 17))
                qty = quantity_per_order + (remainder if i == orders_count - 1 else 0)
                
                # Use unique order code (max 20 chars)
                unique_suffix = str(uuid.uuid4())[:4].upper()
                order_code = f'W{product_name[:2].upper()}{i:03d}{unique_suffix}'
                
                order, created = Order.objects.get_or_create(
                    order_code=order_code,
                    client_name=f'Client {product_name[:5]}',
                    company_name=f'Company {i}',
                    phone=f'+9715{random.randint(10000000, 99999999)}',
                    email=f'client{product_name[:3]}{i}@example.com',
                    address='Dubai, UAE',
                    specs=f'Order for {product_name}',
                    urgency='Normal',
                    status='sent_to_production',
                    stage='printing',
                    created_at=order_date
                )
                
                if not created:
                    # Order already exists, skip
                    continue
                
                unit_price = Decimal(str(random.uniform(5.0, 50.0)))
                OrderItem.objects.create(
                    order=order,
                    product_id=f'PROD-{product_name[:5]}',
                    name=product_name,
                    sku=f'SKU-{product_name[:5]}',
                    quantity=qty,
                    unit_price=unit_price,
                    line_total=qty * unit_price
                )
        
        self.stdout.write('  ✓ Created top products data for this week')

