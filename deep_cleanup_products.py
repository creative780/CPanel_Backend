import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

PRODUCT_IDS = ["TE-K-001", "TE-T-004", "AF-T-001"]

TABLES_WITH_PRODUCT_ID = [
    "admin_backend_final_productinventory",
    "admin_backend_final_productvariant",
    "admin_backend_final_shippinginfo",
    "admin_backend_final_productseo",
    "admin_backend_final_productsubcategorymap",
    "admin_backend_final_productimage",
    "admin_backend_final_producttestimonial",
    "admin_backend_final_productcards",
    "admin_backend_final_attribute",
    "admin_backend_final_cartitem",
    "admin_backend_final_favorite",
    "admin_backend_final_firstcarouselimage",
    "admin_backend_final_secondcarouselimage",
    "admin_backend_final_orderitem",
]

def raw_deep_delete(product_ids):
    with connection.cursor() as cursor:
        existing_tables = connection.introspection.table_names()
        
        for pid in product_ids:
            print(f"--- Raw Deleting Product: {pid} ---")
            
            # 1. Delete from related tables
            for table in TABLES_WITH_PRODUCT_ID:
                if table in existing_tables:
                    try:
                        cursor.execute(f"DELETE FROM {table} WHERE product_id = %s", [pid])
                        if cursor.rowcount: print(f"  Deleted {cursor.rowcount} from {table}")
                    except Exception as e:
                        # Some tables might have 'product' instead of 'product_id' column if they are not using standard FK attnames
                        try:
                            cursor.execute(f"DELETE FROM {table} WHERE product = %s", [pid])
                            if cursor.rowcount: print(f"  Deleted {cursor.rowcount} from {table}")
                        except Exception:
                            print(f"  Failed for {table}: {e}")

            # 2. Cleanup VariantCombination (depends on ProductVariant)
            if "admin_backend_final_variantcombination" in existing_tables and "admin_backend_final_productvariant" in existing_tables:
                cursor.execute("""
                    DELETE FROM admin_backend_final_variantcombination 
                    WHERE variant_id IN (SELECT variant_id FROM admin_backend_final_productvariant WHERE product_id = %s)
                """, [pid])
                if cursor.rowcount: print(f"  Deleted {cursor.rowcount} Variant Combinations")

            # 3. Cleanup Images from Image table
            if "admin_backend_final_image" in existing_tables:
                cursor.execute("DELETE FROM admin_backend_final_image WHERE linked_table = 'product' AND linked_id = %s", [pid])
                if cursor.rowcount: print(f"  Deleted {cursor.rowcount} records from Image table")

            # 4. Cleanup Trash
            if "admin_backend_final_recentlydeleteditem" in existing_tables:
                cursor.execute("DELETE FROM admin_backend_final_recentlydeleteditem WHERE record_id = %s AND table_name = 'Product'", [pid])
                if cursor.rowcount: print(f"  Deleted trash entries for {pid}")

            # 5. Final Product Delete
            if "admin_backend_final_product" in existing_tables:
                cursor.execute("DELETE FROM admin_backend_final_product WHERE product_id = %s", [pid])
                if cursor.rowcount:
                    print(f"  SUCCESS: Deleted Product {pid}")
                else:
                    print(f"  Product {pid} not found or already deleted.")

if __name__ == "__main__":
    raw_deep_delete(PRODUCT_IDS)
    
    # Final check
    from admin_backend_final.models import Product
    print("\n--- Final Audit ---")
    print(f"Remaining Products: {Product.objects.count()}")
    for p in Product.objects.all():
        print(f"ID: {p.product_id}, Title: {p.title}")
