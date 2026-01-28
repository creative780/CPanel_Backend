from django.core.management.base import BaseCommand
from orders.models import OrderFile, Order


class Command(BaseCommand):
    help = 'Check files in database for specific orders'

    def add_arguments(self, parser):
        parser.add_argument('--order-ids', nargs='+', type=int, help='Order IDs to check')

    def handle(self, *args, **options):
        # Check total files
        total_files = OrderFile.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total files in database: {total_files}'))

        # Check specific orders
        order_ids = options.get('order_ids') or [29, 366]
        for order_id in order_ids:
            try:
                order = Order.objects.get(id=order_id)
                files = OrderFile.objects.filter(order_id=order_id)
                self.stdout.write(f'\nOrder {order_id} ({order.order_code}): {files.count()} files')
                for f in files:
                    self.stdout.write(f'  - File {f.id}: {f.file_name}')
                    self.stdout.write(f'    Product: {f.product_related or "None"}')
                    self.stdout.write(f'    Visible to: {f.visible_to_roles}')
            except Order.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'\nOrder {order_id}: Not found'))

        # Show recent files
        if total_files > 0:
            self.stdout.write(f'\nRecent 5 files:')
            recent = OrderFile.objects.order_by('-id')[:5]
            for f in recent:
                self.stdout.write(f'  File {f.id}: Order {f.order_id}, {f.file_name}, Product: {f.product_related or "None"}')

