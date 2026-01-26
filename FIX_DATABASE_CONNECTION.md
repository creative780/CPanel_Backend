# Fix Database Connection Error

## The Problem

Django server can't start because PostgreSQL authentication is failing. The `.env` file has placeholder database credentials:

```
DATABASE_URL=postgresql://user:password@localhost:5432/crm_db
```

## Solution Options

### Option 1: Use SQLite for Development (Easiest)

If you don't need PostgreSQL, comment out or remove the DATABASE_URL line in `.env`:

```env
# DATABASE_URL=postgresql://user:password@localhost:5432/crm_db
```

Django will automatically use SQLite (`db.sqlite3`) as the default fallback.

### Option 2: Fix PostgreSQL Credentials

If you need PostgreSQL, update the DATABASE_URL in `.env` with your actual credentials:

```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/crm_db
```

Replace:

- `your_username` - Your PostgreSQL username (usually `postgres`)
- `your_password` - Your PostgreSQL password
- `crm_db` - Your database name (or create it if it doesn't exist)

### Option 3: Create PostgreSQL Database

If PostgreSQL is installed but database doesn't exist:

1. Open PostgreSQL command line or pgAdmin
2. Create database:
   ```sql
   CREATE DATABASE crm_db;
   ```
3. Update `.env` with correct credentials

## Quick Fix (Recommended for Development)

1. Open `CRM_BACKEND/.env` file
2. Comment out or remove the DATABASE_URL line:
   ```env
   # DATABASE_URL=postgresql://user:password@localhost:5432/crm_db
   ```
3. Restart Django server
4. Django will use SQLite automatically

## After Fixing

Restart the Django server:

```bash
cd D:\CRM-Final\CRM_BACKEND
python manage.py runserver
```

The server should start successfully, and then you can test the email configuration.
