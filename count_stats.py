import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_backend_final.models import Product, Orders, Category, SubCategory, Attribute, AttributeSubCategory

print(f'Products: {Product.objects.count()}')
print(f'Orders: {Orders.objects.count()}')
print(f'Categories: {Category.objects.count()}')
print(f'SubCategories: {SubCategory.objects.count()}')
print(f'Attributes (Tree): {Attribute.objects.filter(parent__isnull=True).count()}')
print(f'Attributes (Scoped): {AttributeSubCategory.objects.count()}')
