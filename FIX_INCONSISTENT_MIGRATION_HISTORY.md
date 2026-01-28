# Fix Inconsistent Migration History

## Problem
The database has `attendance.0007_merge_0005_0006` marked as applied, but its dependency `attendance.0002_attendancerule_attendance_device_info_and_more` is not marked as applied.

## Solution: Fake-Apply the Missing Migration

On **production server**, run:

### Step 1: Check Current Migration Status

```bash
python manage.py showmigrations attendance
```

This will show which migrations are marked as applied `[X]` and which are not `[ ]`.

### Step 2: Fake-Apply the Missing Migration

If `0002_attendancerule_attendance_device_info_and_more` shows as `[ ]` (not applied), fake-apply it:

```bash
python manage.py migrate attendance 0002_attendancerule_attendance_device_info_and_more --fake
```

This marks the migration as applied in the database without actually running it (assuming the database changes were already applied).

### Step 3: Verify and Continue

```bash
# Check migration status again
python manage.py showmigrations attendance

# Test migration graph
python manage.py migrate --check

# Apply any remaining migrations
python manage.py migrate
```

## Alternative: Check What's Actually in the Database

If you're not sure if the migration was actually applied, you can check:

```bash
# Connect to database and check if the tables/fields exist
python manage.py dbshell

# Then check if attendance_attendancerule table exists
# Or check if attendance_attendance table has device_info field
```

If the database changes are already there, use `--fake`. If not, apply normally without `--fake`.


