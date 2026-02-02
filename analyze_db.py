import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_backend_final.models import Product, Attribute

print("--- PRODUCT STATUS COUNTS ---")
from django.db.models import Count
status_counts = Product.objects.values('status').annotate(total=Count('status'))
for sc in status_counts:
    print(f"Status: {sc['status']} | Count: {sc['total']}")

print("\n--- ATTRIBUTES ANALYSIS ---")
total_attrs = Attribute.objects.count()
# Attributes with valid products
attr_with_product = Attribute.objects.filter(product__isnull=False).count()
# Attributes without products (should be 0 due to CASCADE, but let's check)
attr_without_product = Attribute.objects.filter(product__isnull=True).count()

print(f"Total Attributes: {total_attrs}")
print(f"Attributes with valid Product: {attr_with_product}")
print(f"Attributes without Product: {attr_without_product}")

print("\n--- ATTRIBUTES PER PRODUCT ---")
for p in Product.objects.all():
    count = Attribute.objects.filter(product=p).count()
    print(f"Product: {p.product_id} ({p.title}) | Attributes: {count}")
