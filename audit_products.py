import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_backend_final.models import Product, ProductSubCategoryMap, SubCategory

products = Product.objects.all()
print(f"Total Products in DB: {products.count()}")
for p in products:
    maps = ProductSubCategoryMap.objects.filter(product=p)
    sub_names = [m.subcategory.name for m in maps if m.subcategory]
    print(f"ID: {p.product_id}, Name: {p.title}, Status: {p.status}, Subcategories: {sub_names}")

print("\nSubcategories:")
for s in SubCategory.objects.all():
    print(f"ID: {s.subcategory_id}, Name: {s.name}, Status: {s.status}")
