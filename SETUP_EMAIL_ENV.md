# Quick Email Setup Guide

## Step 1: Create .env File

The `.env` file is missing. Create it by copying from `env.example`:

```bash
cd CRM_BACKEND
copy env.example .env
```

Or on Linux/Mac:

```bash
cd CRM_BACKEND
cp env.example .env
```

## Step 2: Configure Gmail Settings

Edit the `.env` file and update these lines:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
EMAIL_FROM=your-email@gmail.com
```

**Important:**

- Replace `your-email@gmail.com` with your actual Gmail address
- Replace `your-16-character-app-password` with your Gmail App Password
- `EMAIL_FROM` must match `EMAIL_HOST_USER` exactly

## Step 3: Generate Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Enable 2FA first if not already enabled
3. Generate App Password for "Mail"
4. Copy the 16-character password (spaces optional)

## Step 4: Verify Configuration

After updating `.env`, restart Django server and run:

```bash
python manage.py check_email_config
```

This will show if your configuration is correct.

## Step 5: Test Email Sending

Test that emails work:

```bash
python manage.py test_email your-email@gmail.com
```

If successful, you should receive a test email.

## Troubleshooting

- **Configuration not loading?** Make sure `.env` is in `CRM_BACKEND/` directory (same level as `manage.py`)
- **Still showing "NOT SET"?** Restart Django server after editing `.env`
- **Authentication fails?** Make sure you're using App Password, not regular password
