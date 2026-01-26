# Migration Deployment Checklist

## Problem
Production server is missing migration files (specifically `0010_add_design_fields_to_orderitem.py`), causing `NodeNotFoundError` when running migrations.

## Solution: Deploy All Migration Files

### Step 1: Verify Local Migration Files
All migration files exist locally (verified):
- ✅ 0001_initial.py through 0027_merge_all_branches.py
- Total: 27 migration files

### Step 2: Deploy to Production

**Option A: Using Git (Recommended)**
```bash
# On production server
cd /home/api.crm.click2print.store/public_html
git pull origin main  # or your branch name
```

**Option B: Manual Copy via SCP/FTP**
```bash
# From your local machine
scp -r ./orders/migrations/*.py user@production:/home/api.crm.click2print.store/public_html/orders/migrations/
```

**Option C: Using rsync**
```bash
rsync -avz ./orders/migrations/ user@production:/home/api.crm.click2print.store/public_html/orders/migrations/
```

### Step 3: Verify Files on Production
```bash
# On production server
ls -la orders/migrations/00*.py | wc -l
# Should show 27 files
```

### Step 4: Run Migrations
```bash
# On production server
cd /home/api.crm.click2print.store/public_html
source venv/bin/activate
python manage.py migrate --check  # Verify graph builds
python manage.py migrate          # Apply migrations
```

### Step 5: Verify Success
```bash
python manage.py showmigrations orders
# All migrations should show [X] (applied) or [ ] (pending)
```

## Critical Migration Files to Deploy

These files must exist in production for `0027_merge_all_branches` to work:

1. ✅ `0010_add_design_fields_to_orderitem.py`
2. ✅ `0011_fix_delivery_stage_id_field.py`
3. ✅ `0012_fix_delivery_stage_id_with_sql.py`
4. ✅ `0013_fix_field_conflicts.py`
5. ✅ `0014_rename_quantity_to_product_quantity.py`
6. ✅ `0015_fix_designapproval_reviewed_at_field.py`
7. ✅ `0026_merge_0015_0025.py`
8. ✅ `0027_merge_all_branches.py`

## Troubleshooting

### If migration files are missing:
1. Check git status: `git status orders/migrations/`
2. Ensure files are committed: `git add orders/migrations/*.py`
3. Push to repository: `git push origin main`

### If database changes were already applied manually:
Only use fake-apply as a last resort:
```bash
python manage.py migrate orders 0010 --fake
python manage.py migrate orders 0011 --fake
# ... repeat for each missing migration
python manage.py migrate
```

## Prevention

To prevent this in the future:
1. ✅ Always commit migration files to git
2. ✅ Include migrations in deployment process
3. ✅ Run `python manage.py migrate --check` before deployment
4. ✅ Verify all migration files exist in production after deployment


