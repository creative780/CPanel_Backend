# Fix Migration History Directly in Database

## Problem
Django won't allow fake-apply because of inconsistent history. We need to directly update the database.

## Solution: Update Django Migrations Table

On **production server**, run:

### Step 1: Connect to Database

```bash
python manage.py dbshell
```

### Step 2: Insert the Missing Migration Record

In the database shell, run:

```sql
-- For MySQL/MariaDB
INSERT INTO django_migrations (app, name, applied) 
VALUES ('attendance', '0002_attendancerule_attendance_device_info_and_more', NOW())
ON DUPLICATE KEY UPDATE applied = applied;

-- Exit the database shell
exit
```

Or if using PostgreSQL:

```sql
INSERT INTO django_migrations (app, name, applied) 
VALUES ('attendance', '0002_attendancerule_attendance_device_info_and_more', NOW())
ON CONFLICT (app, name) DO NOTHING;

-- Exit the database shell
exit
```

### Step 3: Verify and Continue

```bash
# Check migration status
python manage.py showmigrations attendance

# Test migration graph
python manage.py migrate --check

# Apply remaining migrations
python manage.py migrate
```

## Alternative: Python Script

If dbshell doesn't work, create a temporary script:

```python
# fix_migration_history.py
from django.db import connection
from django.utils import timezone

with connection.cursor() as cursor:
    cursor.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
        ['attendance', '0002_attendancerule_attendance_device_info_and_more', timezone.now()]
    )

print("Migration history fixed!")
```

Then run:
```bash
python manage.py shell < fix_migration_history.py
```


