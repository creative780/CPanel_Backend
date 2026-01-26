# Production Migration Steps - Final Phase

## ✅ Step 1: Files Copied (DONE)
- 27 migration files are now in production

## Step 2: Test Migration Graph

Run this to verify the migration graph builds correctly:

```bash
python manage.py migrate --check
```

**Expected result**: Should pass without errors (no output or "No changes detected")

## Step 3: Apply Migrations

If the check passes, apply the migrations:

```bash
python manage.py migrate
```

This will:
- Apply any pending migrations
- Update the database schema
- Mark migrations as applied in the database

## Step 4: Verify Success

Check that all migrations are applied:

```bash
# Show migration status
python manage.py showmigrations orders | tail -10

# Should show all migrations as [X] (applied)
```

## Step 5: Test the Application

After migrations are applied:
1. Restart your application server (if needed)
2. Test the attendance/overtime features
3. Verify no errors in logs

## Troubleshooting

### If `migrate --check` fails:
- Check the error message
- Verify all 27 files are present: `ls -la orders/migrations/00*.py | wc -l`
- Check file permissions: `ls -la orders/migrations/00*.py | head -5`

### If `migrate` fails:
- Check database connection
- Review error messages
- Check database user permissions

### If you see "No changes detected":
- This is good! It means migrations are already applied
- Run `python manage.py showmigrations orders` to verify


