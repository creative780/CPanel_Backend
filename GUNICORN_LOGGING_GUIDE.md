# Gunicorn Logging Guide

## Current Situation

Your gunicorn process is running without explicit log file configuration, which means logs are going to stdout/stderr. If the process is running in the background or as a service, these logs might be lost or redirected.

## Quick Solutions

### Option 1: View Logs in Real-Time (If Running in Foreground)

If you started gunicorn in a terminal session, you can view logs directly in that terminal. If you need to restart it to see logs:

```bash
# Stop current gunicorn processes
pkill -f "gunicorn.*asgi"

# Start gunicorn with logging to files (using command line flags)
cd /home/api.crm.click2print.store/public_html
source venv/bin/activate
gunicorn crm_backend.asgi:application \
    --bind 0.0.0.0:9000 \
    --workers 4 \
    --timeout 120 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log \
    --log-level info \
    --pid logs/gunicorn.pid
```

### Option 2: Use the Gunicorn Config File (Recommended)

1. **Start gunicorn using the config file:**

```bash
cd /home/api.crm.click2print.store/public_html
source venv/bin/activate
gunicorn crm_backend.asgi:application -c gunicorn_config.py
```

2. **Or if you need to override some settings:**

```bash
gunicorn crm_backend.asgi:application -c gunicorn_config.py --bind 0.0.0.0:9000
```

### Option 3: Check System Logs

If gunicorn is running as a systemd service or through a process manager, check:

```bash
# For systemd services
journalctl -u your-service-name -f

# For general system logs
journalctl -f | grep gunicorn

# Check if there's a log file in common locations
find /var/log -name "*gunicorn*" 2>/dev/null
find /home/api.crm.click2print.store -name "*.log" 2>/dev/null
```

## Viewing Logs

Once logs are configured, you can view them using:

### View Access Logs (HTTP Requests)
```bash
# View entire file
cat /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log

# View last 100 lines
tail -n 100 /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log

# Follow logs in real-time (like tail -f)
tail -f /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log
```

### View Error Logs (Errors and Exceptions)
```bash
# View entire file
cat /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log

# View last 100 lines
tail -n 100 /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log

# Follow logs in real-time
tail -f /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log
```

### View Both Logs Simultaneously
```bash
# Using multitail (if installed)
multitail /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log \
          /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log

# Or using tail for both
tail -f /home/api.crm.click2print.store/public_html/logs/gunicorn_*.log
```

### Search Logs
```bash
# Search for errors
grep -i error /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log

# Search for specific endpoint
grep "/api/endpoint" /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log

# Search with context (5 lines before and after)
grep -C 5 "error" /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log

# Search with timestamps
grep "2025-01-11" /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log
```

## Log Rotation

The logs will grow over time. Consider setting up log rotation:

### Manual Rotation
```bash
# Rotate logs manually
mv /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log \
   /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log.old
mv /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log \
   /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log.old

# Restart gunicorn to create new log files
pkill -HUP -f "gunicorn.*asgi"
```

### Automatic Rotation with logrotate

Create `/etc/logrotate.d/gunicorn-crm`:

```
/home/api.crm.click2print.store/public_html/logs/gunicorn_*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        pkill -HUP -f "gunicorn.*asgi" || true
    endscript
}
```

## Restart Gunicorn with New Logging Configuration

```bash
# Stop current processes
pkill -f "gunicorn.*asgi"

# Wait a moment
sleep 2

# Start with new configuration
cd /home/api.crm.click2print.store/public_html
source venv/bin/activate
gunicorn crm_backend.asgi:application -c gunicorn_config.py

# Or with command line flags
gunicorn crm_backend.asgi:application \
    --bind 0.0.0.0:9000 \
    --workers 4 \
    --timeout 120 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log \
    --log-level info
```

## Log File Locations

With the configuration file, logs will be in:
- **Access logs**: `/home/api.crm.click2print.store/public_html/logs/gunicorn_access.log`
- **Error logs**: `/home/api.crm.click2print.store/public_html/logs/gunicorn_error.log`
- **PID file**: `/home/api.crm.click2print.store/public_html/logs/gunicorn.pid`

## Troubleshooting

### If logs directory doesn't exist:
```bash
mkdir -p /home/api.crm.click2print.store/public_html/logs
chmod 755 /home/api.crm.click2print.store/public_html/logs
```

### If permission errors:
```bash
# Check current user
whoami

# Check log directory permissions
ls -la /home/api.crm.click2print.store/public_html/logs

# Fix permissions if needed
chmod 755 /home/api.crm.click2print.store/public_html/logs
chown -R $(whoami):$(whoami) /home/api.crm.click2print.store/public_html/logs
```

### Check if gunicorn is writing to logs:
```bash
# Check if log files are being updated
ls -lh /home/api.crm.click2print.store/public_html/logs/gunicorn_*.log

# Check last modification time
stat /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log
```

## Quick Reference Commands

```bash
# View error logs in real-time
tail -f /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log

# View last 50 error lines
tail -n 50 /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log

# Search for specific error
grep -i "traceback" /home/api.crm.click2print.store/public_html/logs/gunicorn_error.log

# Count requests per minute (from access log)
awk '{print $4}' /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log | cut -d: -f1-2 | uniq -c

# View requests to specific endpoint
grep "/api/your-endpoint" /home/api.crm.click2print.store/public_html/logs/gunicorn_access.log
```

























