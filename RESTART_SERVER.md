# IMPORTANT: Restart Django Server After .env Changes

## The Issue

You're getting the error "EMAIL_HOST_USER is not configured" because:

**Django only loads environment variables from `.env` file when the server starts.**

If you:
- Created the `.env` file
- Updated the `.env` file
- Changed email settings in `.env`

**You MUST restart the Django server** for the changes to take effect.

## How to Restart

### Option 1: If running with `python manage.py runserver`
1. Stop the server (Ctrl+C in the terminal)
2. Start it again: `python manage.py runserver`

### Option 2: If running with a batch file
1. Stop the current server
2. Run: `start_server.bat` (or your start script)

### Option 3: If running in production
1. Restart your WSGI server (gunicorn, uwsgi, etc.)
2. Or restart the entire service

## Verify After Restart

After restarting, verify the configuration is loaded:

```bash
python manage.py check_email_config
```

You should see:
- ✓ Configuration is VALID
- User: you***@gmail.com (configured)
- Password: **************** (configured)

## Quick Test

After restarting, test OTP sending again from the frontend. The error should be resolved.

