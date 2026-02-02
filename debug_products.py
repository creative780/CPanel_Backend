import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from admin_backend_final.models import Product, Attribute

print(f"TOTAL_PRODUCTS:{Product.objects.count()}")

# Filtering logic used in ShowProductsAPIView
EXCLUDED_TITLES = ['fghjd', 'kela', 'amb kela', 'aaa', 'abid ali', 'amb amb kela', 'abid abid ali', 'amb kela kino']
EXCLUDED_STATUSES = ['hidden', 'inactive', 'deleted']

print("-" * 50)
print(f"{'ID':<15} {'STATUS':<10} {'VISIBLE':<8} {'TITLE'}")
print("-" * 50)

for p in Product.objects.all():
    is_excluded_title = p.title in EXCLUDED_TITLES
    is_excluded_status = (p.status or "").lower() in EXCLUDED_STATUSES
    visible = not (is_excluded_title or is_excluded_status)
    
    print(f"{p.product_id:<15} {str(p.status):<10} {str(visible):<8} {p.title}")

print("-" * 50)
print("TOTAL_ATTRIBUTES:", Attribute.objects.count())

# Count attributes for visible vs hidden products
visible_p_ids = [p.product_id for p in Product.objects.all() if not (p.title in EXCLUDED_TITLES or (p.status or "").lower() in EXCLUDED_STATUSES)]
hidden_p_ids = [p.product_id for p in Product.objects.all() if (p.title in EXCLUDED_TITLES or (p.status or "").lower() in EXCLUDED_STATUSES)]

visible_attr_count = Attribute.objects.filter(product_id__in=visible_p_ids).count()
hidden_attr_count = Attribute.objects.filter(product_id__in=hidden_p_ids).count()

print(f"Attributes for VISIBLE products: {visible_attr_count}")
print(f"Attributes for HIDDEN products: {hidden_attr_count}")
