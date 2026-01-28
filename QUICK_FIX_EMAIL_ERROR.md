# Quick Fix: "EMAIL_HOST_USER is not configured" Error

## The Problem

You're seeing this error because the Django server is running but hasn't loaded the email configuration from your `.env` file.

## Solution: Restart Django Server

**Django only reads the `.env` file when the server starts.** If you just created or updated the `.env` file, you must restart the server.

### Steps:

1. **Stop the Django server**
   - Press `Ctrl+C` in the terminal where it's running
   - Or close the terminal window

2. **Start the Django server again**
   ```bash
   cd D:\CRM-Final\CRM_BACKEND
   python manage.py runserver
   ```

3. **Verify configuration is loaded**
   ```bash
   python manage.py check_email_config
   ```
   
   You should see:
   - ✓ Configuration is VALID
   - User: you***@gmail.com (configured)
   - Password: **************** (configured)

4. **Test OTP sending again**
   - Go to Employee Verification Wizard
   - Click "Send OTP"
   - Should work now!

## If Still Not Working

### Check .env file location:
- Make sure `.env` is in `CRM_BACKEND/` directory (same folder as `manage.py`)
- Not in `CRM_BACKEND/crm_backend/` or root directory

### Check .env file contents:
Open `.env` and verify these lines exist:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

### Verify .env is being read:
After restarting, check Django startup logs. You should see:
- "Email configuration validated successfully" (if valid)
- Or warnings about missing configuration (if invalid)

## Common Mistakes

1. ❌ Editing `.env` but not restarting server
2. ❌ `.env` file in wrong location
3. ❌ Typo in variable names (e.g., `EMAIL_HOST_USR` instead of `EMAIL_HOST_USER`)
4. ❌ Spaces around `=` sign (should be `EMAIL_HOST_USER=value`, not `EMAIL_HOST_USER = value`)

## Still Having Issues?

Run this diagnostic command:
```bash
python manage.py check_email_config
```

This will show exactly what's configured and what's missing.

