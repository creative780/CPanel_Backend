# Email Setup Guide for Scheduled Reports

This guide explains how to configure email for sending scheduled activity log reports.

## Quick Setup

### For Development (Testing)

If you just want to test without sending real emails, use the console backend. Emails will be printed to the console instead of being sent.

In your `.env` file:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Or set `DEBUG=True` - the system will automatically use console backend if no SMTP is configured.

### For Production (Real Email Sending)

## Gmail Setup

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the generated 16-character password
3. **Configure in `.env` file**:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-character-app-password
   EMAIL_FROM=your-email@gmail.com
   ```

**Important**: Use the App Password, not your regular Gmail password!

## Office 365 / Outlook Setup

1. **Configure in `.env` file**:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.office365.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@outlook.com
   EMAIL_HOST_PASSWORD=your-password
   EMAIL_FROM=your-email@outlook.com
   ```

2. **If you have 2FA enabled**, you may need to use an App Password

## Custom SMTP Server Setup

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourserver.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-username
EMAIL_HOST_PASSWORD=your-password
EMAIL_FROM=noreply@yourdomain.com
```

### Common SMTP Ports:
- **587** - TLS (recommended, use with `EMAIL_USE_TLS=True`)
- **465** - SSL (use with `EMAIL_USE_SSL=True`)
- **25** - Usually blocked by ISPs, not recommended

## Testing Email Configuration

After configuring, test your email setup:

```bash
python manage.py test_email recipient@example.com
```

This will send a test email to verify your configuration works.

## Troubleshooting

### "Authentication failed"
- **Gmail**: Make sure you're using an App Password, not your regular password
- **Office 365**: Ensure 2FA app password is used if 2FA is enabled
- **Custom SMTP**: Verify username and password are correct

### "Connection refused" or "Connection timeout"
- Check if firewall is blocking the SMTP port
- Verify EMAIL_HOST and EMAIL_PORT are correct
- Try using port 587 with TLS instead of 465 with SSL

### Emails not sending
- Check Django logs for error messages
- Verify EMAIL_FROM address matches EMAIL_HOST_USER (some providers require this)
- Test with console backend first to ensure code works

### "SMTP AUTH extension not supported"
- Try using `EMAIL_USE_TLS=True` with port 587
- Or use `EMAIL_USE_SSL=True` with port 465

## Security Best Practices

1. **Never commit passwords to git** - Use `.env` file and add it to `.gitignore`
2. **Use App Passwords** instead of main account passwords when possible
3. **Use environment variables** in production instead of hardcoding
4. **Rotate passwords regularly**
5. **Use separate email account** for system emails (don't use personal email)

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `EMAIL_BACKEND` | Django email backend class | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP server port | `587` |
| `EMAIL_USE_TLS` | Enable TLS encryption | `True` |
| `EMAIL_USE_SSL` | Enable SSL encryption | `False` |
| `EMAIL_HOST_USER` | SMTP username/email | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password/app password | `abcdefghijklmnop` |
| `EMAIL_FROM` | From email address | `noreply@crm.click2print.store` |














































