# Copy Migration Files - Exact Commands

## Server Information
- **IP Address**: `31.97.191.155`
- **User**: `root`
- **Destination**: `/home/api.crm.click2print.store/public_html/orders/migrations/`

## Method 1: SCP from PowerShell (Recommended)

Open **PowerShell** on your Windows machine and run:

```powershell
# Navigate to your project directory
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"

# Copy ALL migration files (easiest - overwrites existing safely)
scp orders/migrations/00*.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
```

**Or copy only the 8 missing files:**

```powershell
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"

scp orders/migrations/0010_add_design_fields_to_orderitem.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0011_fix_delivery_stage_id_field.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0012_fix_delivery_stage_id_with_sql.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0013_fix_field_conflicts.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0014_rename_quantity_to_product_quantity.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0015_fix_designapproval_reviewed_at_field.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0026_merge_0015_0025.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
scp orders/migrations/0027_merge_all_branches.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
```

## Method 2: WinSCP (GUI - Easiest)

1. **Open WinSCP**
2. **New Session**:
   - **File protocol**: SFTP
   - **Host name**: `31.97.191.155`
   - **Port number**: `22`
   - **User name**: `root`
   - **Password**: (enter your password)
   - Click **Login**

3. **Navigate to**:
   - Left panel (local): `D:\Abdullah\CRM Backup\12\CRM_BACKEND\orders\migrations\`
   - Right panel (remote): `/home/api.crm.click2print.store/public_html/orders/migrations/`

4. **Select and upload**:
   - In left panel, select all `00*.py` files
   - Drag and drop to right panel, or click **Upload** button

## Method 3: Using rsync (if available)

```powershell
cd "D:\Abdullah\CRM Backup\12\CRM_BACKEND"
rsync -avz orders/migrations/00*.py root@31.97.191.155:/home/api.crm.click2print.store/public_html/orders/migrations/
```

## After Copying - Verify on Production

SSH into the server:
```bash
ssh root@31.97.191.155
```

Then run:
```bash
cd /home/api.crm.click2print.store/public_html

# Should show 27 files now
ls -la orders/migrations/00*.py | wc -l

# Test migration graph
python manage.py migrate --check

# Apply migrations
python manage.py migrate
```

## Troubleshooting

### If SCP asks for password:
- Enter your root password when prompted
- Or set up SSH key authentication for passwordless access

### If "command not found" (SCP not in PATH):
- Use WinSCP instead (GUI method)
- Or install OpenSSH client on Windows

### If permission denied:
```bash
# On production server
chmod 644 orders/migrations/00*.py
```


