#!/bin/bash
# Script to copy missing migration files to production
# Run this from your local machine

echo "📋 Missing Migration Files Deployment Script"
echo "=============================================="
echo ""
echo "This script will help you copy the missing 8 migration files to production."
echo ""

# List of all migration files that should exist (27 total)
MIGRATION_FILES=(
    "0001_initial.py"
    "0002_rename_orders_order_stage_status_idx_orders_orde_stage_72c51f_idx_and_more.py"
    "0003_order_pricing_status_quotation_custom_field_and_more.py"
    "0004_add_trn_field.py"
    "0005_add_sales_person_field.py"
    "0006_add_workflow_models.py"
    "0007_add_custom_requirements.py"
    "0008_alter_quotation_id.py"
    "0009_add_trn_and_sales_person_fields.py"
    "0010_add_design_fields_to_orderitem.py"
    "0011_fix_delivery_stage_id_field.py"
    "0012_fix_delivery_stage_id_with_sql.py"
    "0013_fix_field_conflicts.py"
    "0014_rename_quantity_to_product_quantity.py"
    "0015_fix_designapproval_reviewed_at_field.py"
    "0016_fix_deliverystage_rider_photo_path_nullable.py"
    "0017_increase_sku_max_length.py"
    "0018_merge_20251031_0107.py"
    "0019_add_design_completed_fields_and_fix_productmachine.py"
    "0020_alter_productmachineassignment_options_and_more.py"
    "0021_force_sku_length_patch.py"
    "0022_merge_0016_0021.py"
    "0023_merge_0015_0022.py"
    "0024_fix_field_rename_detection.py"
    "0025_alter_productmachineassignment_product_sku.py"
    "0026_merge_0015_0025.py"
    "0027_merge_all_branches.py"
)

# Critical files that are likely missing (based on error)
CRITICAL_MISSING=(
    "0010_add_design_fields_to_orderitem.py"
    "0011_fix_delivery_stage_id_field.py"
    "0012_fix_delivery_stage_id_with_sql.py"
    "0013_fix_field_conflicts.py"
    "0014_rename_quantity_to_product_quantity.py"
    "0015_fix_designapproval_reviewed_at_field.py"
    "0026_merge_0015_0025.py"
    "0027_merge_all_branches.py"
)

echo "🔍 Critical migration files that need to be copied:"
echo "---------------------------------------------------"
for file in "${CRITICAL_MISSING[@]}"; do
    echo "  - $file"
done
echo ""

echo "📤 To copy these files to production, use one of these methods:"
echo ""
echo "Method 1: Using SCP (from your local machine)"
echo "---------------------------------------------"
echo "scp orders/migrations/0010_add_design_fields_to_orderitem.py \\"
echo "    orders/migrations/0011_fix_delivery_stage_id_field.py \\"
echo "    orders/migrations/0012_fix_delivery_stage_id_with_sql.py \\"
echo "    orders/migrations/0013_fix_field_conflicts.py \\"
echo "    orders/migrations/0014_rename_quantity_to_product_quantity.py \\"
echo "    orders/migrations/0015_fix_designapproval_reviewed_at_field.py \\"
echo "    orders/migrations/0026_merge_0015_0025.py \\"
echo "    orders/migrations/0027_merge_all_branches.py \\"
echo "    root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/"
echo ""
echo "Method 2: Using rsync (from your local machine)"
echo "-----------------------------------------------"
echo "rsync -avz orders/migrations/00*.py \\"
echo "    root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/"
echo ""
echo "Method 3: Manual copy via FTP/SFTP"
echo "-----------------------------------"
echo "Copy all files from: orders/migrations/00*.py"
echo "To: /home/api.crm.click2print.store/public_html/orders/migrations/"
echo ""
echo "Method 4: Using Git (if files are committed)"
echo "---------------------------------------------"
echo "# On production server:"
echo "cd /home/api.crm.click2print.store/public_html"
echo "git pull origin main  # or your branch name"
echo ""


