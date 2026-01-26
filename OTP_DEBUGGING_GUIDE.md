# OTP Email Sending - Debugging Guide

## Current Status

✅ **Backend is working correctly:**

- API returns 200 OK
- OTP records are being created in database
- Email configuration is correct
- Email sending test succeeds

## What to Check When "Nothing Happens"

### 1. Check Browser Console (Frontend)

Open browser DevTools (F12) → Console tab:

- Look for JavaScript errors
- Check if API call is being made
- Verify response is received
- Check for toast notification errors

### 2. Check Email Inbox

- Check **Spam/Junk folder** - Gmail might filter OTP emails
- Check **All Mail** folder
- Verify email address: `maffanilahi@gmail.com`
- Wait 1-2 minutes for email delivery

### 3. Check Backend Logs

Look for these log messages in Django console:

- `[Email] OTP sent successfully to {email}` - ✅ Email sent
- `[Email] Failed to send OTP email` - ❌ Email failed
- `[Email] SMTP error` - ❌ SMTP connection issue

### 4. Verify OTP in Database

Run this command to see recent OTPs:

```bash
python manage.py shell
>>> from hr.models import OTPVerification
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> recent = OTPVerification.objects.filter(sent_at__gte=timezone.now() - timedelta(minutes=5))
>>> for otp in recent:
...     print(f"Email: {otp.email}, Code: {otp.otp_code}, Sent: {otp.sent_at}")
```

### 5. Test Email Sending Directly

```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Test body', settings.DEFAULT_FROM_EMAIL, ['maffanilahi@gmail.com'], fail_silently=False)
```

## Common Issues

### Issue 1: Email Goes to Spam

**Solution**:

- Check Gmail spam folder
- Mark as "Not Spam" if found
- Add sender email to contacts

### Issue 2: Gmail App Password Issues

**Symptoms**: Authentication errors in logs
**Solution**:

- Verify App Password is correct (16 characters, no spaces)
- Ensure 2-Step Verification is enabled
- Regenerate App Password if needed

### Issue 3: Frontend Not Showing Success

**Symptoms**: API returns 200 but no toast message
**Solution**:

- Check browser console for errors
- Verify `react-hot-toast` is working
- Check if frontend code is updated (refresh page)

### Issue 4: Rate Limiting

**Symptoms**: "Too many OTP requests" error
**Solution**:

- Wait 15 minutes between requests
- Maximum 3 OTPs per 15 minutes per employee

## Next Steps

1. **Check your email inbox** (including spam) for OTP code: `977393`
2. **Check browser console** for frontend errors
3. **Check Django logs** for email sending messages
4. **Try sending OTP again** and watch the logs

## Expected Behavior

When you click "Send OTP":

1. ✅ Button shows "Sending..." state
2. ✅ API call is made to `/api/hr/employees/4/send-phone-otp`
3. ✅ Backend creates OTP record in database
4. ✅ Backend sends email via Gmail SMTP
5. ✅ Backend returns 200 OK with success message
6. ✅ Frontend shows "OTP sent via email" toast
7. ✅ Email arrives in inbox (check spam folder)

## If Email Still Doesn't Arrive

1. **Check Gmail Security Settings**:

   - Go to: https://myaccount.google.com/security
   - Check "Less secure app access" (if using regular password)
   - Verify App Password is active

2. **Test with Console Backend** (for debugging):

   - In `.env`, change: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
   - Restart Django server
   - OTP code will print to console instead of sending email
   - This confirms the system works, just email delivery issue

3. **Check Gmail Activity**:

   - Go to: https://myaccount.google.com/security
   - Check "Recent security activity"
   - See if blocked login attempts

4. **Verify Email Address**:
   - Ensure employee email is correct
   - Test with a different email address
