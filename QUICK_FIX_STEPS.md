# Quick Fix Steps - Copy Missing Migrations

## Current Situation
- ✅ Local: 27 migration files
- ❌ Production: 19 migration files  
- ⚠️ Missing: 8 files causing `NodeNotFoundError`

## Action Plan

### Step 1: Copy Migration Files to Production

**Choose ONE method that works for you:**

#### Method A: Using SCP (if you have SSH access from Windows)
```powershell
# In PowerShell on your Windows machine
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"
scp orders/migrations/00*.py root@srv959898:/home/api.crm.click2print.store/public_html/orders/migrations/
```

#### Method B: Using WinSCP (GUI - Easiest)
1. Open WinSCP
2. Connect to: `srv959898` (or your server IP)
3. Navigate to: `/home/api.crm.click2print.store/public_html/orders/migrations/`
4. Select all files from: `D:\Abdullah\CRM Backup\12\CRM_BACKEND\orders\migrations\00*.py`
5. Upload them

#### Method C: Using Git (if files are committed)
```bash
# On production server
cd /home/api.crm.click2print.store/public_html
git pull origin main
```

#### Method D: Manual Copy via cPanel/File Manager
1. Log into cPanel
2. Go to File Manager
3. Navigate to: `public_html/orders/migrations/`
4. Upload all `00*.py` files from your local `orders/migrations/` folder

### Step 2: Verify Files on Production

**On production server, run:**
```bash
# Should show 27 files
ls -la orders/migrations/00*.py | wc -l

# List all to verify
ls -la orders/migrations/00*.py | tail -10
```

### Step 3: Test Migration Graph

```bash
# This should pass without errors
python manage.py migrate --check
```

### Step 4: Apply Migrations

```bash
# Apply all pending migrations
python manage.py migrate
```

### Step 5: Verify Success

```bash
# Check migration status
python manage.py showmigrations orders | tail -5

# Should show all migrations as [X] (applied)
```

## Expected Results

✅ **27 migration files** in production  
✅ **`migrate --check` passes** without errors  
✅ **`migrate` applies** successfully  
✅ **No more `NodeNotFoundError`**

## If You Get Errors

### "Permission denied"
```bash
chmod 644 orders/migrations/00*.py
```

### "File already exists"
- That's fine! SCP will overwrite safely

### Still getting NodeNotFoundError
- Double-check all 27 files are present
- Verify file names match exactly
- Check for typos in filenames


