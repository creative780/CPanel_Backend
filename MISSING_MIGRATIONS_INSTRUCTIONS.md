# Missing Migration Files - Production Fix

## Current Status
- **Local**: 27 migration files ✅
- **Production**: 19 migration files ❌
- **Missing**: 8 migration files

## Missing Files (Critical)

Based on the error and migration dependencies, these 8 files are likely missing:

1. `0010_add_design_fields_to_orderitem.py` ⚠️ **CRITICAL** (causes the error)
2. `0011_fix_delivery_stage_id_field.py`
3. `0012_fix_delivery_stage_id_with_sql.py`
4. `0013_fix_field_conflicts.py`
5. `0014_rename_quantity_to_product_quantity.py`
6. `0015_fix_designapproval_reviewed_at_field.py`
7. `0026_merge_0015_0025.py`
8. `0027_merge_all_branches.py`

## Quick Fix - Copy Missing Files

### Option 1: SCP (Recommended - Fastest)

From your **local machine**, run:

```bash
# Navigate to your local CRM_BACKEND directory
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"

# Copy all migration files (will overwrite existing ones safely)
scp orders/migrations/00*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
```

Or copy only the missing ones:

```bash
scp orders/migrations/0010_*.py \
    orders/migrations/0011_*.py \
    orders/migrations/0012_*.py \
    orders/migrations/0013_*.py \
    orders/migrations/0014_*.py \
    orders/migrations/0015_*.py \
    orders/migrations/0026_*.py \
    orders/migrations/0027_*.py \
    root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
```

### Option 2: rsync (Best for syncing)

```bash
rsync -avz --progress orders/migrations/00*.py \
    root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
```

### Option 3: Manual FTP/SFTP

1. Connect to your production server via FTP/SFTP
2. Navigate to: `/home/api.crm.click2print.store/public_html/orders/migrations/`
3. Upload all files from: `D:\Abdullah\CRM Backup\12\CRM_BACKEND\orders\migrations\00*.py`

### Option 4: Git (If files are committed)

On **production server**:

```bash
cd /home/api.crm.click2print.store/public_html
git pull origin main  # or your branch name
```

## Verify After Copying

On **production server**, run:

```bash
# Count files (should show 27)
ls -la orders/migrations/00*.py | wc -l

# List all files to verify
ls -la orders/migrations/00*.py

# Check migration graph
python manage.py migrate --check

# If check passes, apply migrations
python manage.py migrate
```

## Expected Result

After copying, you should see:
- ✅ 27 migration files in production
- ✅ `python manage.py migrate --check` passes
- ✅ `python manage.py migrate` applies successfully

## Troubleshooting

### If SCP asks for password:
```bash
# Use SSH key or provide password when prompted
# Or set up SSH key authentication for passwordless access
```

### If files already exist:
- SCP/rsync will safely overwrite them
- This is fine - ensures files are up to date

### If permission errors:
```bash
# On production server, ensure correct permissions
chmod 644 orders/migrations/00*.py
chown www-data:www-data orders/migrations/00*.py  # or your web server user
```


