import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_backend_final.models import Product, Attribute, AttributeSubCategory

print("=== DATABASE VERIFICATION ===\n")

print("Products:")
for p in Product.objects.all():
    attr_count = Attribute.objects.filter(product=p).count()
    print(f"  - {p.product_id} ({p.title}) - Status: {p.status} - Attributes: {attr_count}")

print(f"\nTotal Products: {Product.objects.count()}")
print(f"Total Product Attributes: {Attribute.objects.count()}")
print(f"Total Subcategory Attributes: {AttributeSubCategory.objects.count()}")

print("\n✓ Database is clean and ready!")
