# Independent migration to enforce SKU field length without relying on
# intermediate order migrations that may be missing on some environments.

from django.db import migrations, models
from app.common.safe_migrations import SafeAlterField


def increase_sku_length_mysql(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return

    with schema_editor.connection.cursor() as cursor:
        try:
            cursor.execute(
                """
                ALTER TABLE orders_orderitem
                MODIFY COLUMN sku VARCHAR(255) NULL
                """
            )
        except Exception as exc:
            print(f"orders_orderitem.sku alteration skipped: {exc}")

        try:
            cursor.execute(
                """
                ALTER TABLE orders_productmachineassignment
                MODIFY COLUMN product_sku VARCHAR(255)
                """
            )
        except Exception as exc:
            print(f"orders_productmachineassignment.product_sku alteration skipped: {exc}")


def reverse_sku_length_mysql(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return

    with schema_editor.connection.cursor() as cursor:
        try:
            cursor.execute(
                """
                ALTER TABLE orders_orderitem
                MODIFY COLUMN sku VARCHAR(100) NULL
                """
            )
        except Exception:
            pass

        try:
            cursor.execute(
                """
                ALTER TABLE orders_productmachineassignment
                MODIFY COLUMN product_sku VARCHAR(100)
                """
            )
        except Exception:
            pass


class Migration(migrations.Migration):

    # Keep this independent so it runs even if later workflow migrations
    # were never applied in production.
    dependencies = [
        ("orders", "0020_alter_productmachineassignment_options_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    increase_sku_length_mysql,
                    reverse_sku_length_mysql,
                ),
            ],
            state_operations=[
                SafeAlterField(
                    model_name="orderitem",
                    name="sku",
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
                # Note: productmachineassignment.product_sku state change omitted
                # to avoid state conflicts. Database change via RunPython still applies.
            ],
        ),
    ]


