from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from orders.models import Order, OrderItem, OrderFile
from django.utils import timezone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create a test order with files for testing'

    def handle(self, *args, **options):
        # Create a test order
        order = Order.objects.create(
            order_code=f'TEST-{timezone.now().strftime("%Y%m%d%H%M%S")}',
            client_name='Test Client',
            company_name='Test Company',
            phone='1234567890',
            email='test@example.com',
            address='Test Address',
            specs='Test specifications',
            urgency='Normal',
            status='draft',
            stage='order_intake',
            channel='walk_in_orders'
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created test order: {order.order_code} (ID: {order.id})'))
        
        # Create a test order item
        item = OrderItem.objects.create(
            order=order,
            product_id='TEST-PROD-001',
            name='Test Product',
            sku='TEST-SKU-001',
            quantity=1,
            unit_price=Decimal('100.00'),
            line_total=Decimal('100.00')
        )
        self.stdout.write(self.style.SUCCESS(f'Created order item: {item.name}'))
        
        # Create test files
        test_files = [
            {
                'name': 'test_creation_file.pdf',
                'content': b'PDF content during creation',
                'file_type': 'requirement',
                'stage': 'order_intake',
                'description': 'File uploaded during order creation'
            },
            {
                'name': 'test_design_file.pdf',
                'content': b'PDF content from designer',
                'file_type': 'design',
                'stage': 'design',
                'description': 'File uploaded by designer'
            },
            {
                'name': 'test_sales_file.pdf',
                'content': b'PDF content from sales',
                'file_type': 'other',
                'stage': 'order_intake',
                'description': 'File uploaded by sales person'
            }
        ]
        
        created_files = []
        for file_info in test_files:
            # Create a simple uploaded file
            uploaded_file = SimpleUploadedFile(
                file_info['name'],
                file_info['content'],
                content_type='application/pdf'
            )
            
            order_file = OrderFile.objects.create(
                order=order,
                file=uploaded_file,
                file_name=file_info['name'],
                file_type=file_info['file_type'],
                file_size=len(file_info['content']),
                mime_type='application/pdf',
                uploaded_by='test_user',
                uploaded_by_role='admin',
                stage=file_info['stage'],
                visible_to_roles=['admin', 'sales', 'designer', 'production'],
                description=file_info['description'],
                product_related=''
            )
            
            created_files.append(order_file)
            self.stdout.write(self.style.SUCCESS(
                f'Created file: {order_file.file_name} (ID: {order_file.id}, stage: {order_file.stage})'
            ))
        
        # Verify files
        all_files = OrderFile.objects.filter(order_id=order.id)
        self.stdout.write(self.style.SUCCESS(f'\nTotal files for order {order.id}: {all_files.count()}'))
        
        for f in all_files:
            self.stdout.write(f'  - File {f.id}: {f.file_name} (stage: {f.stage}, type: {f.file_type})')
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Test order created successfully!\n'
            f'Order ID: {order.id}\n'
            f'Order Code: {order.order_code}\n'
            f'Files created: {len(created_files)}\n'
            f'\nYou can now test this order in the frontend.'
        ))

