import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_backend_final.models import Product, Attribute

# List of test products to delete
EXCLUDED_TITLES = ['fghjd', 'kela', 'amb kela', 'aaa', 'abid ali', 'amb amb kela', 'abid abid ali', 'amb kela kino']

print("--- CLEANING UP TEST PRODUCTS ---")
print(f"Looking for products with titles: {EXCLUDED_TITLES}")

# Find products to delete
products_to_delete = Product.objects.filter(title__in=EXCLUDED_TITLES)
count = products_to_delete.count()

print(f"\nFound {count} products to delete:")
for p in products_to_delete:
    attr_count = Attribute.objects.filter(product=p).count()
    print(f"  - {p.product_id} ({p.title}) - {attr_count} attributes")

if count > 0:
    print(f"\nDeleting {count} products and their related data...")
    
    # Delete will cascade to related Attribute records
    deleted_count, details = products_to_delete.delete()
    
    print(f"\n✓ Successfully deleted {deleted_count} total records:")
    for model, del_count in details.items():
        print(f"  - {model}: {del_count}")
    
    # Verify deletion
    remaining = Product.objects.filter(title__in=EXCLUDED_TITLES).count()
    if remaining == 0:
        print(f"\n✓ Verification: All test products have been permanently removed")
    else:
        print(f"\n⚠ Warning: {remaining} products still remain")
else:
    print("\nNo products found to delete.")

print("\n--- FINAL DATABASE STATE ---")
print(f"Total Products: {Product.objects.count()}")
print(f"Total Attributes: {Attribute.objects.count()}")
