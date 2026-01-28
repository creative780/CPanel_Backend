# Start Server - Database Fixed

## What I Fixed

I commented out the PostgreSQL DATABASE_URL in your `.env` file because it had placeholder credentials that were causing the connection error.

Django will now automatically use SQLite (`db.sqlite3`) which already exists in your project.

## Start the Server

**IMPORTANT**: Use Daphne (ASGI server) instead of runserver for proper WebSocket and async support.

**Windows:**
```batch
cd D:\CRM-Final\CRM_BACKEND
start_daphne.bat
```

Or manually:
```bash
python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application
```

**Linux/Mac:**
```bash
cd CRM_BACKEND
./start_daphne.sh
```

The server should start successfully without database errors or timeout warnings.

**Why Daphne?** This project uses Django Channels for WebSocket support. Using `runserver` causes timeout warnings and login failures. See `ASGI_SERVER_SETUP.md` for details.

## After Server Starts

1. **Verify email configuration is loaded:**
   ```bash
   python manage.py check_email_config
   ```

2. **Test OTP sending** from the Employee Verification Wizard

## If You Need PostgreSQL Later

If you want to use PostgreSQL instead of SQLite:

1. Update `.env` with your actual PostgreSQL credentials:
   ```env
   DATABASE_URL=postgresql://your_username:your_password@localhost:5432/crm_db
   ```

2. Make sure PostgreSQL is running and the database exists

3. Restart Django server

For now, SQLite is fine for development and testing the email functionality.

