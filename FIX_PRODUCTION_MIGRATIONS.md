# Fix Production Migrations - Direct Solution

## Problem
Production has 19 migration files, but needs 27. Git pull didn't bring the missing files.

## Solution: Force Pull or Manual Copy

The migration files exist in your local repository but may not be in the remote, or production's git is out of sync.

### Option 1: Check What's in Remote (Recommended First)

On **production server**, run:
```bash
# Check what migration files are in the remote
git ls-tree -r --name-only origin/main orders/migrations/00*.py | wc -l

# If it shows less than 27, the files aren't pushed to remote yet
```

### Option 2: Commit and Push Missing Files (If Not in Remote)

On **your local machine**:
```bash
# Check if files are committed
git status orders/migrations/00*.py

# If any are untracked, add and commit them
git add orders/migrations/00*.py
git commit -m "Add missing migration files for orders app"
git push origin main
```

Then on **production**:
```bash
git pull origin main
```

### Option 3: Direct Copy (Fastest - Use This Now)

Since git pull didn't work, **copy files directly**:

**From your local Windows machine:**

#### Using WinSCP:
1. Connect to `srv959898`
2. Navigate to: `/home/api.crm.click2print.store/public_html/orders/migrations/`
3. Upload these 8 files:
   - `0010_add_design_fields_to_orderitem.py`
   - `0011_fix_delivery_stage_id_field.py`
   - `0012_fix_delivery_stage_id_with_sql.py`
   - `0013_fix_field_conflicts.py`
   - `0014_rename_quantity_to_product_quantity.py`
   - `0015_fix_designapproval_reviewed_at_field.py`
   - `0026_merge_0015_0025.py`
   - `0027_merge_all_branches.py`

#### Using SCP (PowerShell):
```powershell
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"

# Copy the 8 missing files
scp orders/migrations/0010_*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0011_*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0012_*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0013_*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0014_*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0015_*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0026_*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0027_*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
```

Or copy all at once:
```powershell
scp orders/migrations/00*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
```

### Option 4: Check Git Status on Production

On **production server**:
```bash
# Check if files are untracked locally
git status orders/migrations/

# If files show as untracked, they exist but aren't in git
# In that case, you can:
git checkout origin/main -- orders/migrations/00*.py
```

## After Copying Files

On **production server**:
```bash
# Verify count (should be 27)
ls -la orders/migrations/00*.py | wc -l

# Test migration graph
python manage.py migrate --check

# Apply migrations
python manage.py migrate
```

## Quick Command Reference

**Copy all migration files (easiest):**
```powershell
# From Windows PowerShell
scp "D:\Abdullah\CRM Backup\12\CRM_BACKEND\orders\migrations\00*.py" root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
```

**Verify on production:**
```bash
ls -la orders/migrations/00*.py | wc -l  # Should be 27
python manage.py migrate --check        # Should pass
python manage.py migrate                 # Apply migrations
```


