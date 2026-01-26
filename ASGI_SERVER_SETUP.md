# ASGI Server Setup Guide

## Why Use Daphne Instead of runserver?

This project uses Django Channels for WebSocket support and async functionality. **You MUST use an ASGI server (Daphne) instead of Django's development server (`runserver`)**.

### Problems with `runserver`:
- ❌ Does not properly support ASGI applications
- ❌ Causes "Application instance took too long to shut down" warnings
- ❌ Login requests may timeout or fail
- ❌ WebSocket connections may not work properly
- ❌ Database connections may not close properly, causing memory leaks

### Benefits of Daphne:
- ✅ Proper ASGI support for Django Channels
- ✅ Handles async cleanup correctly
- ✅ No timeout warnings
- ✅ Reliable WebSocket connections
- ✅ Proper database connection management

## Quick Start

### Windows

**Option 1: Use the startup script (Recommended)**
```batch
start_daphne.bat
```

**Option 2: Manual command**
```batch
python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application
```

### Linux/Mac

**Option 1: Use the startup script (Recommended)**
```bash
chmod +x start_daphne.sh
./start_daphne.sh
```

**Option 2: Manual command**
```bash
python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application
```

## Installation

If Daphne is not installed:

```bash
pip install daphne
```

Or if using requirements.txt:
```bash
pip install -r requirements.txt
```

## Command Line Options

- `-p 8000`: Port number (default: 8000)
- `-b 0.0.0.0`: Bind address (0.0.0.0 = all interfaces)
- `--application-close-timeout 30`: Timeout for application cleanup (prevents timeout warnings)
- `crm_backend.asgi:application`: ASGI application path

## Verification

After starting Daphne, you should see:
- Server running on `http://0.0.0.0:8000`
- No "Application instance took too long to shut down" warnings
- WebSocket connections work properly
- Login requests complete successfully

## Testing

Use the provided test script to verify everything works:

```bash
python test_login.py
```

This will:
- Test server connectivity
- Test admin login
- Test non-admin login (if configured)
- Measure response times
- Verify no timeout errors

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'daphne'"
**Solution**: Install Daphne
```bash
pip install daphne
```

### Issue: "Redis connection error"
**Solution**: Start Redis/Memurai
- Windows: Install Memurai from https://www.memurai.com/get-memurai
- Linux: `sudo systemctl start redis`
- Mac: `brew services start redis`

### Issue: Still getting timeout warnings
**Solution**: 
1. Make sure you're using Daphne, not runserver
2. Check that `--application-close-timeout 30` is set
3. Verify database connections are closing (check middleware)

### Issue: Login still times out
**Solution**:
1. Verify you're using Daphne
2. Check server logs for errors
3. Run `python test_login.py` to diagnose
4. Ensure Redis is running (required for Channels)

## Production Deployment

For production, consider using:
- **Gunicorn with Uvicorn workers**: `gunicorn crm_backend.asgi:application --worker-class uvicorn.workers.UvicornWorker`
- **Uvicorn directly**: `uvicorn crm_backend.asgi:application --host 0.0.0.0 --port 8000`
- **Daphne with process manager**: Use systemd, supervisor, or similar

## Additional Resources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Daphne Documentation](https://github.com/django/daphne)
- [ASGI Specification](https://asgi.readthedocs.io/)





























