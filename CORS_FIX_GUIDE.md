# CORS Error Fix Guide

## Problem
Frontend at `https://app.click2print.store` cannot access backend API at `https://api.click2print.store` due to CORS policy errors.

## Error Message
```
Access to fetch at 'https://api.click2print.store/api/...' from origin 'https://app.click2print.store' 
has been blocked by CORS policy: Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Solution Steps

### 1. Verify Backend Configuration

The CORS configuration in `backend/settings.py` has been updated to include:
- `https://app.click2print.store` ✅
- `https://app.crm.click2print.store` ✅ (added)

### 2. Check Environment Variables

**On the production server**, check your `.env` file:

```bash
# If CORS_ALLOW_ALL_ORIGINS is set to False, ensure origins are listed
CORS_ALLOW_ALL_ORIGINS=False

# Add extra origins if needed
CORS_ALLOWED_ORIGINS_EXTRA=https://app.click2print.store,https://app.crm.click2print.store
```

**OR** (for development/testing):
```bash
# Allow all origins (less secure, but easier for testing)
CORS_ALLOW_ALL_ORIGINS=True
```

### 3. Restart Backend Server

**Critical:** After changing CORS settings, you MUST restart the Django server:

```bash
# If using systemd
sudo systemctl restart your-django-service

# If using supervisor
sudo supervisorctl restart django

# If running manually
# Stop the server (Ctrl+C) and restart:
python manage.py runserver 0.0.0.0:8000
```

### 4. Check Reverse Proxy Configuration (Nginx/Apache)

If you're using a reverse proxy (Nginx/Apache), ensure it's not stripping CORS headers.

#### Nginx Configuration Example:

```nginx
server {
    listen 443 ssl;
    server_name api.click2print.store;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # IMPORTANT: Don't strip CORS headers
        # Let Django handle CORS, don't override
    }
}
```

**DO NOT** add CORS headers in Nginx if Django is handling them - this can cause conflicts.

### 5. Verify CORS Middleware Order

The CORS middleware must be at the **top** of the middleware list:

```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # MUST be first
    "django.middleware.security.SecurityMiddleware",
    # ... rest of middleware
]
```

### 6. Test CORS Configuration

#### Test 1: Check CORS Headers

```bash
curl -X OPTIONS https://api.click2print.store/api/show_nav_items/ \
  -H "Origin: https://app.click2print.store" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: x-frontend-key" \
  -v
```

**Expected Response Headers:**
```
Access-Control-Allow-Origin: https://app.click2print.store
Access-Control-Allow-Methods: GET, POST, OPTIONS, ...
Access-Control-Allow-Headers: x-frontend-key, ...
Access-Control-Allow-Credentials: true
```

#### Test 2: Actual API Request

```bash
curl -X GET https://api.click2print.store/api/show_nav_items/ \
  -H "Origin: https://app.click2print.store" \
  -H "X-Frontend-Key: YOUR_KEY" \
  -v
```

### 7. Check Django Logs

Check your Django server logs for CORS-related errors:

```bash
# If using systemd
sudo journalctl -u your-django-service -f

# If using supervisor
sudo tail -f /var/log/supervisor/django.log

# If running manually
# Check the terminal where Django is running
```

### 8. Verify Settings Are Loaded

Add temporary logging to verify settings:

```python
# In backend/settings.py, add at the end:
import logging
logger = logging.getLogger(__name__)
logger.info(f"CORS_ALLOW_ALL_ORIGINS: {CORS_ALLOW_ALL_ORIGINS}")
if not CORS_ALLOW_ALL_ORIGINS:
    logger.info(f"CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
```

Then check logs to confirm settings are correct.

## Common Issues

### Issue 1: CORS headers not present
**Cause:** Backend server not restarted after config changes
**Fix:** Restart Django server

### Issue 2: Preflight (OPTIONS) request fails
**Cause:** CORS middleware not processing OPTIONS requests
**Fix:** Ensure `CORS_ALLOW_METHODS` includes `'OPTIONS'` (it does)

### Issue 3: Headers blocked
**Cause:** Custom headers not in `CORS_ALLOW_HEADERS`
**Fix:** Verify `x-frontend-key` is in the list (it is)

### Issue 4: Reverse proxy stripping headers
**Cause:** Nginx/Apache removing CORS headers
**Fix:** Don't add CORS headers in proxy, let Django handle it

### Issue 5: Environment variable override
**Cause:** `.env` file has `CORS_ALLOW_ALL_ORIGINS=False` but origins not listed
**Fix:** Either set to `True` or add all origins to `CORS_ALLOWED_ORIGINS`

## Quick Fix Checklist

- [ ] Updated `backend/settings.py` with correct origins
- [ ] Added `https://app.crm.click2print.store` to allowed origins
- [ ] Checked `.env` file for `CORS_ALLOW_ALL_ORIGINS` setting
- [ ] Restarted Django backend server
- [ ] Verified CORS middleware is first in middleware list
- [ ] Checked reverse proxy config (if using one)
- [ ] Tested with curl to verify CORS headers
- [ ] Checked Django logs for errors

## Production Deployment

For production, it's recommended to:

1. **Set `CORS_ALLOW_ALL_ORIGINS=False`** for security
2. **Explicitly list all allowed origins** in `CORS_ALLOWED_ORIGINS`
3. **Use environment variables** for easy updates:
   ```bash
   CORS_ALLOW_ALL_ORIGINS=False
   CORS_ALLOWED_ORIGINS_EXTRA=https://app.click2print.store,https://app.crm.click2print.store
   ```

## Testing After Fix

1. Clear browser cache
2. Open browser DevTools (F12)
3. Go to Network tab
4. Navigate to `https://app.click2print.store`
5. Check that API requests succeed (no CORS errors)
6. Verify response headers include `Access-Control-Allow-Origin`

## Still Having Issues?

1. Check Django version: `python -m django --version`
2. Check django-cors-headers version: `pip show django-cors-headers`
3. Verify middleware order in `settings.py`
4. Check for any custom middleware that might interfere
5. Review server logs for detailed error messages

