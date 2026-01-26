from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta
from decimal import Decimal
from orders.models import (
    Order, OrderItem, ProductMachineAssignment, OrderFile, PrintingStage
)


class Command(BaseCommand):
    help = 'Seed the database with production-specific test orders for testing the production dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing seeded orders (orders with codes starting with PROD-) before seeding',
        )

    def get_or_create_order(self, order_code, **kwargs):
        """Get or create an order, skipping if it already exists.
        Returns: (order, created) tuple where created is True if order was created, False if it already existed.
        """
        try:
            order = Order.objects.get(order_code=order_code)
            # Order exists, skip creation
            return order, False
        except Order.DoesNotExist:
            # Create the order
            order = Order.objects.create(order_code=order_code, **kwargs)
            return order, True

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing seeded orders...')
            orders = Order.objects.filter(order_code__startswith='PROD-')
            deleted_count = 0
            for order in orders:
                order.delete()
                deleted_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {deleted_count} existing seeded orders')
            )
        
        self.stdout.write('Creating production test orders...')
        
        # Create new orders (sent_to_production, no assignments)
        self.create_new_order_single_product()
        self.create_new_order_multiple_products()
        self.create_new_order_urgent()
        self.create_new_order_b2b_channel()
        self.create_new_order_b2c_channel()
        self.create_new_order_walk_in()
        self.create_new_order_online()
        self.create_new_order_with_files()
        self.create_new_order_high_urgency()
        self.create_new_order_low_urgency()
        
        # Create in-progress orders (active, with assignments)
        self.create_in_progress_order_with_timer()
        self.create_in_progress_order_partial_complete()
        self.create_in_progress_order_all_active()
        self.create_in_progress_order_multiple_machines()
        
        # Create completed orders (getting_ready or sent_to_admin)
        self.create_completed_order_ready_for_admin()
        self.create_completed_order_sent_to_admin()
        self.create_completed_order_all_done()
        self.create_completed_order_with_files()
        
        # Create history orders (delivered or sent_for_delivery)
        self.create_history_order_delivered()
        self.create_history_order_sent_for_delivery()
        self.create_history_order_recent()
        self.create_history_order_old()
        self.create_history_order_multiple()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {Order.objects.filter(stage="printing").count()} production test orders!')
        )

    def create_new_order_single_product(self):
        """New order with single product"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-001',
            client_name='Single Product Client',
            company_name='Single Product Co',
            phone='+971501111111',
            email='single@example.com',
            address='Dubai, UAE',
            specs='Business cards printing',
            urgency='Normal',
            status='sent_to_production',
            stage='printing',
            channel='b2b_customers',
            assigned_sales_person='Sales Person 1',
            created_at=timezone.now() - timedelta(hours=2)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='BC-001',
                name='Business Cards',
                sku='BC-001',
                attributes={'finish': 'matte', 'size': 'standard'},
                quantity=500,
                unit_price=Decimal('0.50'),
                line_total=Decimal('250.00')
            )
            self.stdout.write(f'Created new order (single product): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (single product): {order.order_code}')

    def create_new_order_multiple_products(self):
        """New order with multiple products"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-002',
            client_name='Multi Product Client',
            company_name='Multi Product Corp',
            phone='+971502222222',
            email='multi@example.com',
            address='Abu Dhabi, UAE',
            specs='Complete marketing package',
            urgency='Normal',
            status='sent_to_production',
            stage='printing',
            channel='b2c_customers',
            created_at=timezone.now() - timedelta(hours=1)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='BR-001',
                name='Marketing Brochures',
                sku='BR-001',
                attributes={'size': 'A4', 'pages': 8},
                quantity=1000,
                unit_price=Decimal('2.50'),
                line_total=Decimal('2500.00')
            )
            
            OrderItem.objects.create(
                order=order,
                product_id='FL-001',
                name='Promotional Flyers',
                sku='FL-001',
                attributes={'size': 'A5'},
                quantity=2000,
                unit_price=Decimal('0.75'),
                line_total=Decimal('1500.00')
            )
            
            OrderItem.objects.create(
                order=order,
                product_id='BC-002',
                name='Business Cards',
                sku='BC-002',
                attributes={'finish': 'glossy'},
                quantity=1000,
                unit_price=Decimal('0.60'),
                line_total=Decimal('600.00')
            )
            self.stdout.write(f'Created new order (multiple products): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (multiple products): {order.order_code}')

    def create_new_order_urgent(self):
        """New order with urgent priority"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-003',
            client_name='Urgent Client',
            company_name='Urgent Business',
            phone='+971503333333',
            email='urgent@example.com',
            address='Sharjah, UAE',
            specs='Rush order for event',
            urgency='Urgent',
            status='sent_to_production',
            stage='printing',
            channel='walk_in_orders',
            created_at=timezone.now() - timedelta(minutes=30)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='BN-001',
                name='Event Banners',
                sku='BN-001',
                attributes={'size': '3x6ft', 'material': 'vinyl'},
                quantity=5,
                unit_price=Decimal('45.00'),
                line_total=Decimal('225.00')
            )
            self.stdout.write(f'Created new order (urgent): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (urgent): {order.order_code}')

    def create_new_order_b2b_channel(self):
        """New order from B2B channel"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-004',
            client_name='B2B Corporation',
            company_name='B2B Corp Ltd',
            phone='+971504444444',
            email='b2b@example.com',
            address='Dubai, UAE',
            specs='Corporate printing order',
            urgency='High',
            status='sent_to_production',
            stage='printing',
            channel='b2b_customers',
            created_at=timezone.now() - timedelta(hours=3)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='LT-001',
                name='Letterheads',
                sku='LT-001',
                attributes={'size': 'A4', 'paper': 'premium'},
                quantity=2000,
                unit_price=Decimal('0.40'),
                line_total=Decimal('800.00')
            )
            self.stdout.write(f'Created new order (B2B channel): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (B2B channel): {order.order_code}')

    def create_new_order_b2c_channel(self):
        """New order from B2C channel"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-005',
            client_name='B2C Customer',
            company_name='',
            phone='+971505555555',
            email='b2c@example.com',
            address='Ajman, UAE',
            specs='Personal printing order',
            urgency='Normal',
            status='sent_to_production',
            stage='printing',
            channel='b2c_customers',
            created_at=timezone.now() - timedelta(hours=4)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='PH-001',
                name='Photo Prints',
                sku='PH-001',
                attributes={'size': '4x6', 'finish': 'glossy'},
                quantity=100,
                unit_price=Decimal('0.25'),
                line_total=Decimal('25.00')
            )
            self.stdout.write(f'Created new order (B2C channel): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (B2C channel): {order.order_code}')

    def create_new_order_walk_in(self):
        """New order from walk-in channel"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-006',
            client_name='Walk-In Customer',
            company_name='',
            phone='+971506666666',
            email='walkin@example.com',
            address='Ras Al Khaimah, UAE',
            specs='Walk-in order',
            urgency='Normal',
            status='sent_to_production',
            stage='printing',
            channel='walk_in_orders',
            created_at=timezone.now() - timedelta(minutes=45)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='ST-001',
                name='Stickers',
                sku='ST-001',
                attributes={'size': 'custom', 'material': 'vinyl'},
                quantity=500,
                unit_price=Decimal('0.15'),
                line_total=Decimal('75.00')
            )
            self.stdout.write(f'Created new order (walk-in): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (walk-in): {order.order_code}')

    def create_new_order_online(self):
        """New order from online channel"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-007',
            client_name='Online Customer',
            company_name='Online Store',
            phone='+971507777777',
            email='online@example.com',
            address='Fujairah, UAE',
            specs='Online store order',
            urgency='Normal',
            status='sent_to_production',
            stage='printing',
            channel='online_store',
            created_at=timezone.now() - timedelta(hours=5)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='PO-001',
                name='Posters',
                sku='PO-001',
                attributes={'size': 'A3', 'finish': 'matte'},
                quantity=50,
                unit_price=Decimal('3.00'),
                line_total=Decimal('150.00')
            )
            self.stdout.write(f'Created new order (online): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (online): {order.order_code}')

    def create_new_order_with_files(self):
        """New order with design files attached"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-008',
            client_name='Files Client',
            company_name='Files Co',
            phone='+971508888888',
            email='files@example.com',
            address='Dubai, UAE',
            specs='Order with design files',
            urgency='High',
            status='sent_to_production',
            stage='printing',
            channel='b2b_customers',
            created_at=timezone.now() - timedelta(hours=1, minutes=30)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='BR-002',
                name='Custom Brochures',
                sku='BR-002',
                attributes={'size': 'A4', 'pages': 12},
                quantity=500,
                unit_price=Decimal('3.00'),
                line_total=Decimal('1500.00')
            )
            
            # Add design files
            design_file_content = b'%PDF-1.4\n% Design file content for testing\n'
            design_file = ContentFile(design_file_content, name='design_file.pdf')
            OrderFile.objects.create(
                order=order,
                file=design_file,
                file_name='design_file.pdf',
                file_type='design',
                file_size=len(design_file_content),
                mime_type='application/pdf',
                uploaded_by='designer1',
                uploaded_by_role='designer',
                stage='design',
                visible_to_roles=['admin', 'sales', 'designer', 'production'],
                description='Design file for production',
                product_related='BR-002'
            )
            
            # Add print-ready file
            print_file_content = b'%PDF-1.4\n% Print-ready file content\n'
            print_file = ContentFile(print_file_content, name='print_ready.pdf')
            OrderFile.objects.create(
                order=order,
                file=print_file,
                file_name='print_ready.pdf',
                file_type='final',
                file_size=len(print_file_content),
                mime_type='application/pdf',
                uploaded_by='designer1',
                uploaded_by_role='designer',
                stage='printing',
                visible_to_roles=['admin', 'production'],
                description='Print-ready file',
                product_related='BR-002'
            )
            self.stdout.write(f'Created new order (with files): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (with files): {order.order_code}')

    def create_new_order_high_urgency(self):
        """New order with high urgency"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-009',
            client_name='High Priority Client',
            company_name='Priority Corp',
            phone='+971509999999',
            email='high@example.com',
            address='Dubai, UAE',
            specs='High priority order',
            urgency='High',
            status='sent_to_production',
            stage='printing',
            channel='b2b_customers',
            created_at=timezone.now() - timedelta(minutes=15)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='SG-001',
                name='Signage',
                sku='SG-001',
                attributes={'size': '2x4ft', 'material': 'acrylic'},
                quantity=10,
                unit_price=Decimal('120.00'),
                line_total=Decimal('1200.00')
            )
            self.stdout.write(f'Created new order (high urgency): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (high urgency): {order.order_code}')

    def create_new_order_low_urgency(self):
        """New order with low urgency"""
        order, created = self.get_or_create_order(
            order_code='PROD-NEW-010',
            client_name='Low Priority Client',
            company_name='Low Priority Co',
            phone='+971500000000',
            email='low@example.com',
            address='Abu Dhabi, UAE',
            specs='Low priority order',
            urgency='Low',
            status='sent_to_production',
            stage='printing',
            channel='online_store',
            created_at=timezone.now() - timedelta(days=1)
        )
        
        if created:
            OrderItem.objects.create(
                order=order,
                product_id='MN-001',
                name='Menus',
                sku='MN-001',
                attributes={'size': 'A4', 'pages': 8},
                quantity=100,
                unit_price=Decimal('5.00'),
                line_total=Decimal('500.00')
            )
            self.stdout.write(f'Created new order (low urgency): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (low urgency): {order.order_code}')

    def create_in_progress_order_with_timer(self):
        """In-progress order with active timer"""
        order, created = self.get_or_create_order(
            order_code='PROD-PROG-001',
            client_name='In Progress Client 1',
            company_name='Progress Co',
            phone='+971511111111',
            email='progress1@example.com',
            address='Dubai, UAE',
            specs='Order in production',
            urgency='Normal',
            status='active',
            stage='printing',
            channel='b2b_customers',
            created_at=timezone.now() - timedelta(hours=6)
        )
        
        if created:
            item1 = OrderItem.objects.create(
                order=order,
                product_id='BC-003',
                name='Business Cards',
                sku='BC-003',
                attributes={'finish': 'matte'},
                quantity=1000,
                unit_price=Decimal('0.50'),
                line_total=Decimal('500.00')
            )
            
            # Create machine assignments with started_at (active timer)
            ProductMachineAssignment.objects.create(
                order=order,
                product_name='Business Cards',
                product_sku='BC-003',
                product_quantity=1000,
                machine_id='printer-01',
                machine_name='Digital Printer 1',
                estimated_time_minutes=60,
                started_at=timezone.now() - timedelta(minutes=30),  # Started 30 min ago
                status='in_progress',
                assigned_by='production_user',
                notes='In progress'
            )
            self.stdout.write(f'Created in-progress order (with timer): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (with timer): {order.order_code}')

    def create_in_progress_order_partial_complete(self):
        """In-progress order with some assignments completed"""
        order, created = self.get_or_create_order(
            order_code='PROD-PROG-002',
            client_name='In Progress Client 2',
            company_name='Progress Corp',
            phone='+971522222222',
            email='progress2@example.com',
            address='Abu Dhabi, UAE',
            specs='Order with partial completion',
            urgency='High',
            status='active',
            stage='printing',
            channel='b2c_customers',
            created_at=timezone.now() - timedelta(hours=4)
        )
        
        if created:
            item1 = OrderItem.objects.create(
                order=order,
                product_id='BR-003',
                name='Brochures',
                sku='BR-003',
                attributes={'size': 'A4'},
                quantity=500,
                unit_price=Decimal('2.50'),
                line_total=Decimal('1250.00')
            )
            
            item2 = OrderItem.objects.create(
                order=order,
                product_id='FL-002',
                name='Flyers',
                sku='FL-002',
                attributes={'size': 'A5'},
                quantity=1000,
                unit_price=Decimal('0.75'),
                line_total=Decimal('750.00')
            )
            
            # One completed, one in progress
            ProductMachineAssignment.objects.create(
                order=order,
                product_name='Brochures',
                product_sku='BR-003',
                product_quantity=500,
                machine_id='printer-01',
                machine_name='Digital Printer 1',
                estimated_time_minutes=45,
                started_at=timezone.now() - timedelta(hours=1),
                completed_at=timezone.now() - timedelta(minutes=15),
                status='completed',
                assigned_by='production_user',
                notes='Completed'
            )
            
            ProductMachineAssignment.objects.create(
                order=order,
                product_name='Flyers',
                product_sku='FL-002',
                product_quantity=1000,
                machine_id='printer-02',
                machine_name='Digital Printer 2',
                estimated_time_minutes=30,
                started_at=timezone.now() - timedelta(minutes=20),
                status='in_progress',
                assigned_by='production_user',
                notes='In progress'
            )
            self.stdout.write(f'Created in-progress order (partial complete): {order.order_code}')
        else:
            self.stdout.write(f'Skipped existing order (partial complete): {order.order_code}')

    def create_in_progress_order_all_active(self):
        """In-progress order with all assignments active"""
        order, created = self.get_or_create_order(
            order_code='PROD-PROG-003',
            client_name='In Progress Client 3',
            company_name='Active Co',
            phone='+971533333333',
            email='progress3@example.com',
            address='Sharjah, UAE',
            specs='All assignments active',
            urgency='Normal',
            status='active',
            stage='printing',
            channel='walk_in_orders',
            created_at=timezone.now() - timedelta(hours=3)
        )
        
        item1 = OrderItem.objects.create(
            order=order,
            product_id='BN-002',
            name='Banners',
            sku='BN-002',
            attributes={'size': '3x6ft'},
            quantity=5,
            unit_price=Decimal('45.00'),
            line_total=Decimal('225.00')
        )
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Banners',
            product_sku='BN-002',
            product_quantity=5,
            machine_id='uv-01',
            machine_name='UV Flatbed Printer',
            estimated_time_minutes=90,
            started_at=timezone.now() - timedelta(minutes=45),
            status='in_progress',
            assigned_by='production_user',
            notes='Printing in progress'
        )
        
        self.stdout.write(f'Created in-progress order (all active): {order.order_code}')

    def create_in_progress_order_multiple_machines(self):
        """In-progress order using multiple machines"""
        order, created = self.get_or_create_order(
            order_code='PROD-PROG-004',
            client_name='Multi Machine Client',
            company_name='Multi Machine Corp',
            phone='+971544444444',
            email='multimachine@example.com',
            address='Dubai, UAE',
            specs='Order using multiple machines',
            urgency='Urgent',
            status='active',
            stage='printing',
            channel='b2b_customers',
            created_at=timezone.now() - timedelta(hours=2)
        )
        
        item1 = OrderItem.objects.create(
            order=order,
            product_id='BC-004',
            name='Business Cards',
            sku='BC-004',
            attributes={'finish': 'glossy'},
            quantity=2000,
            unit_price=Decimal('0.60'),
            line_total=Decimal('1200.00')
        )
        
        item2 = OrderItem.objects.create(
            order=order,
            product_id='ST-002',
            name='Stickers',
            sku='ST-002',
            attributes={'material': 'vinyl'},
            quantity=1000,
            unit_price=Decimal('0.20'),
            line_total=Decimal('200.00')
        )
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Business Cards',
            product_sku='BC-004',
            product_quantity=2000,
            machine_id='printer-01',
            machine_name='Digital Printer 1',
            estimated_time_minutes=75,
            started_at=timezone.now() - timedelta(minutes=40),
            status='in_progress',
            assigned_by='production_user',
            notes='Printing on printer 1'
        )
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Stickers',
            product_sku='ST-002',
            product_quantity=1000,
            machine_id='plotter-01',
            machine_name='Vinyl Plotter',
            estimated_time_minutes=45,
            started_at=timezone.now() - timedelta(minutes=25),
            status='in_progress',
            assigned_by='production_user',
            notes='Cutting on plotter'
        )
        
        self.stdout.write(f'Created in-progress order (multiple machines): {order.order_code}')

    def create_completed_order_ready_for_admin(self):
        """Completed order ready for admin review"""
        order, created = self.get_or_create_order(
            order_code='PROD-COMP-001',
            client_name='Completed Client 1',
            company_name='Completed Co',
            phone='+971555555555',
            email='completed1@example.com',
            address='Dubai, UAE',
            specs='Order ready for admin',
            urgency='Normal',
            status='getting_ready',
            stage='printing',
            channel='b2b_customers',
            created_at=timezone.now() - timedelta(hours=12)
        )
        
        item1 = OrderItem.objects.create(
            order=order,
            product_id='BC-005',
            name='Business Cards',
            sku='BC-005',
            attributes={'finish': 'matte'},
            quantity=500,
            unit_price=Decimal('0.50'),
            line_total=Decimal('250.00')
        )
        
        # All assignments completed
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Business Cards',
            product_sku='BC-005',
            product_quantity=500,
            machine_id='printer-01',
            machine_name='Digital Printer 1',
            estimated_time_minutes=60,
            started_at=timezone.now() - timedelta(hours=2),
            completed_at=timezone.now() - timedelta(hours=1),
            status='completed',
            assigned_by='production_user',
            notes='Completed'
        )
        
        self.stdout.write(f'Created completed order (ready for admin): {order.order_code}')

    def create_completed_order_sent_to_admin(self):
        """Completed order sent to admin"""
        order, created = self.get_or_create_order(
            order_code='PROD-COMP-002',
            client_name='Completed Client 2',
            company_name='Admin Co',
            phone='+971566666666',
            email='completed2@example.com',
            address='Abu Dhabi, UAE',
            specs='Order sent to admin',
            urgency='High',
            status='sent_to_admin',
            stage='printing',
            channel='b2c_customers',
            created_at=timezone.now() - timedelta(hours=10)
        )
        
        item1 = OrderItem.objects.create(
            order=order,
            product_id='BR-004',
            name='Brochures',
            sku='BR-004',
            attributes={'size': 'A4', 'pages': 8},
            quantity=1000,
            unit_price=Decimal('2.50'),
            line_total=Decimal('2500.00')
        )
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Brochures',
            product_sku='BR-004',
            product_quantity=1000,
            machine_id='printer-02',
            machine_name='Digital Printer 2',
            estimated_time_minutes=90,
            started_at=timezone.now() - timedelta(hours=3),
            completed_at=timezone.now() - timedelta(hours=1, minutes=30),
            status='completed',
            assigned_by='production_user',
            notes='All done'
        )
        
        self.stdout.write(f'Created completed order (sent to admin): {order.order_code}')

    def create_completed_order_all_done(self):
        """Completed order with all work done"""
        order, created = self.get_or_create_order(
            order_code='PROD-COMP-003',
            client_name='All Done Client',
            company_name='Done Corp',
            phone='+971577777777',
            email='alldone@example.com',
            address='Sharjah, UAE',
            specs='All production complete',
            urgency='Normal',
            status='getting_ready',
            stage='printing',
            channel='walk_in_orders',
            created_at=timezone.now() - timedelta(hours=8)
        )
        
        item1 = OrderItem.objects.create(
            order=order,
            product_id='BN-003',
            name='Banners',
            sku='BN-003',
            attributes={'size': '3x6ft'},
            quantity=10,
            unit_price=Decimal('45.00'),
            line_total=Decimal('450.00')
        )
        
        item2 = OrderItem.objects.create(
            order=order,
            product_id='SG-002',
            name='Signage',
            sku='SG-002',
            attributes={'size': '2x4ft'},
            quantity=5,
            unit_price=Decimal('120.00'),
            line_total=Decimal('600.00')
        )
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Banners',
            product_sku='BN-003',
            product_quantity=10,
            machine_id='uv-01',
            machine_name='UV Flatbed Printer',
            estimated_time_minutes=120,
            started_at=timezone.now() - timedelta(hours=3),
            completed_at=timezone.now() - timedelta(hours=1),
            status='completed',
            assigned_by='production_user',
            notes='Banners completed'
        )
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Signage',
            product_sku='SG-002',
            product_quantity=5,
            machine_id='laser-01',
            machine_name='Laser Cutter 1',
            estimated_time_minutes=60,
            started_at=timezone.now() - timedelta(hours=2),
            completed_at=timezone.now() - timedelta(hours=1),
            status='completed',
            assigned_by='production_user',
            notes='Signage completed'
        )
        
        self.stdout.write(f'Created completed order (all done): {order.order_code}')

    def create_completed_order_with_files(self):
        """Completed order with files"""
        order, created = self.get_or_create_order(
            order_code='PROD-COMP-004',
            client_name='Files Completed Client',
            company_name='Files Done Co',
            phone='+971588888888',
            email='filesdone@example.com',
            address='Dubai, UAE',
            specs='Completed order with files',
            urgency='Normal',
            status='getting_ready',
            stage='printing',
            channel='online_store',
            created_at=timezone.now() - timedelta(hours=6)
        )
        
        item1 = OrderItem.objects.create(
            order=order,
            product_id='PO-002',
            name='Posters',
            sku='PO-002',
            attributes={'size': 'A2'},
            quantity=20,
            unit_price=Decimal('5.00'),
            line_total=Decimal('100.00')
        )
        
        ProductMachineAssignment.objects.create(
            order=order,
            product_name='Posters',
            product_sku='PO-002',
            product_quantity=20,
            machine_id='printer-01',
            machine_name='Digital Printer 1',
            estimated_time_minutes=45,
            started_at=timezone.now() - timedelta(hours=2),
            completed_at=timezone.now() - timedelta(hours=1, minutes=15),
            status='completed',
            assigned_by='production_user',
            notes='Posters printed'
        )
        
        # Add completed production file
        complete_file_content = b'%PDF-1.4\n% Production completed file\n'
        complete_file = ContentFile(complete_file_content, name='production_complete.pdf')
        OrderFile.objects.create(
            order=order,
            file=complete_file,
            file_name='production_complete.pdf',
            file_type='final',
            file_size=len(complete_file_content),
            mime_type='application/pdf',
            uploaded_by='production_user',
            uploaded_by_role='production',
            stage='printing',
            visible_to_roles=['admin', 'production'],
            description='Production completed file',
            product_related='PO-002'
        )
        
        self.stdout.write(f'Created completed order (with files): {order.order_code}')

    def create_history_order_delivered(self):
        """History order that was delivered"""
        order, created = self.get_or_create_order(
            order_code='PROD-HIST-001',
            client_name='Delivered Client 1',
            company_name='Delivered Co',
            phone='+971599999999',
            email='delivered1@example.com',
            address='Dubai, UAE',
            specs='Delivered order',
            urgency='Normal',
            status='delivered',
            stage='delivery',
            delivery_code='123456',
            delivered_at=timezone.now() - timedelta(days=1),
            created_at=timezone.now() - timedelta(days=3)
        )
        
        OrderItem.objects.create(
            order=order,
            product_id='BC-006',
            name='Business Cards',
            sku='BC-006',
            attributes={'finish': 'glossy'},
            quantity=1000,
            unit_price=Decimal('0.60'),
            line_total=Decimal('600.00')
        )
        
        self.stdout.write(f'Created history order (delivered): {order.order_code}')

    def create_history_order_sent_for_delivery(self):
        """History order sent for delivery"""
        order, created = self.get_or_create_order(
            order_code='PROD-HIST-002',
            client_name='Delivery Client',
            company_name='Delivery Co',
            phone='+971510101010',
            email='delivery@example.com',
            address='Abu Dhabi, UAE',
            specs='Order sent for delivery',
            urgency='High',
            status='sent_for_delivery',
            stage='delivery',
            created_at=timezone.now() - timedelta(days=2)
        )
        
        OrderItem.objects.create(
            order=order,
            product_id='BR-005',
            name='Brochures',
            sku='BR-005',
            attributes={'size': 'A4'},
            quantity=500,
            unit_price=Decimal('2.50'),
            line_total=Decimal('1250.00')
        )
        
        self.stdout.write(f'Created history order (sent for delivery): {order.order_code}')

    def create_history_order_recent(self):
        """Recent history order"""
        order, created = self.get_or_create_order(
            order_code='PROD-HIST-003',
            client_name='Recent History Client',
            company_name='Recent Co',
            phone='+971511111110',
            email='recent@example.com',
            address='Sharjah, UAE',
            specs='Recent delivery',
            urgency='Normal',
            status='delivered',
            stage='delivery',
            delivery_code='234567',
            delivered_at=timezone.now() - timedelta(hours=12),
            created_at=timezone.now() - timedelta(days=2)
        )
        
        OrderItem.objects.create(
            order=order,
            product_id='FL-003',
            name='Flyers',
            sku='FL-003',
            attributes={'size': 'A5'},
            quantity=2000,
            unit_price=Decimal('0.75'),
            line_total=Decimal('1500.00')
        )
        
        self.stdout.write(f'Created history order (recent): {order.order_code}')

    def create_history_order_old(self):
        """Old history order"""
        order, created = self.get_or_create_order(
            order_code='PROD-HIST-004',
            client_name='Old History Client',
            company_name='Old Co',
            phone='+971512121212',
            email='old@example.com',
            address='Ajman, UAE',
            specs='Old delivery',
            urgency='Low',
            status='delivered',
            stage='delivery',
            delivery_code='345678',
            delivered_at=timezone.now() - timedelta(days=7),
            created_at=timezone.now() - timedelta(days=10)
        )
        
        OrderItem.objects.create(
            order=order,
            product_id='MN-002',
            name='Menus',
            sku='MN-002',
            attributes={'size': 'A4', 'pages': 12},
            quantity=200,
            unit_price=Decimal('8.50'),
            line_total=Decimal('1700.00')
        )
        
        self.stdout.write(f'Created history order (old): {order.order_code}')

    def create_history_order_multiple(self):
        """History order with multiple items"""
        order, created = self.get_or_create_order(
            order_code='PROD-HIST-005',
            client_name='Multi History Client',
            company_name='Multi History Corp',
            phone='+971513131313',
            email='multihist@example.com',
            address='Dubai, UAE',
            specs='Multiple items delivered',
            urgency='Normal',
            status='delivered',
            stage='delivery',
            delivery_code='456789',
            delivered_at=timezone.now() - timedelta(days=3),
            created_at=timezone.now() - timedelta(days=5)
        )
        
        OrderItem.objects.create(
            order=order,
            product_id='BC-007',
            name='Business Cards',
            sku='BC-007',
            attributes={'finish': 'matte'},
            quantity=1000,
            unit_price=Decimal('0.50'),
            line_total=Decimal('500.00')
        )
        
        OrderItem.objects.create(
            order=order,
            product_id='LT-002',
            name='Letterheads',
            sku='LT-002',
            attributes={'size': 'A4'},
            quantity=500,
            unit_price=Decimal('0.40'),
            line_total=Decimal('200.00')
        )
        
        OrderItem.objects.create(
            order=order,
            product_id='EN-001',
            name='Envelopes',
            sku='EN-001',
            attributes={'size': 'DL'},
            quantity=500,
            unit_price=Decimal('0.30'),
            line_total=Decimal('150.00')
        )
        
        self.stdout.write(f'Created history order (multiple items): {order.order_code}')

