import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_backend_final.models import Product, Attribute, AttributeSubCategory, DeletedItemsCache

print("--- VISIBLE PRODUCTS ATTRIBUTES ---")
EXCLUDED_TITLES = ['fghjd', 'kela', 'amb kela', 'aaa', 'abid ali', 'amb amb kela', 'abid abid ali', 'amb kela kino']
visible_products = Product.objects.exclude(title__in=EXCLUDED_TITLES)

for p in visible_products:
    parents = Attribute.objects.filter(product=p, parent__isnull=True).count()
    options = Attribute.objects.filter(product=p, parent__isnull=False).count()
    print(f"Product: {p.product_id} ({p.title}) | Parent Attrs: {parents} | Options: {options}")

print("\n--- ATTRIBUTE SUBCATEGORY (GLOBAL/SUB) ---")
print(f"Total AttributeSubCategory: {AttributeSubCategory.objects.count()}")
for asc in AttributeSubCategory.objects.all():
    name = getattr(asc, 'name', 'Unknown')
    print(f"PK: {asc.pk} | Name: {name}")

print("\n--- RECENTLY DELETED CACHE ---")
print(f"Total Cached Deleted Items: {DeletedItemsCache.objects.count()}")
for item in DeletedItemsCache.objects.all().order_by('-deleted_at')[:10]:
    print(f"Table: {item.table_name:<15} | Deleted At: {item.deleted_at} | Reason: {item.deleted_reason[:30]}...")
