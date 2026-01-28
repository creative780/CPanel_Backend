# Quick Fix: WebSocket Proxy Configuration

## Problem
Agent getting "Invalid WebSocket Header" error when trying to connect to WebSocket server.

## Solution: Run the Fix Script

### Option 1: Python Script (Recommended)

```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
sudo python3 fix_websocket_proxy.py
```

### Option 2: Bash Script

```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
chmod +x fix_websocket_proxy.sh
sudo ./fix_websocket_proxy.sh
```

## What the Script Does

1. ✅ Detects your web server (nginx/apache)
2. ✅ Finds your nginx configuration file
3. ✅ Creates a backup of the config
4. ✅ Adds WebSocket proxy configuration
5. ✅ Tests the nginx configuration
6. ✅ Reloads nginx
7. ✅ Restarts Django application

## Manual Configuration (If Script Fails)

If the script doesn't work, manually add this to your nginx config:

```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:9000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
    proxy_send_timeout 86400;
    proxy_connect_timeout 60;
    proxy_buffering off;
}
```

Then:
```bash
sudo nginx -t
sudo systemctl reload nginx
pm2 restart app.crm.click2print.store
```

## Verify It Works

After running the script, test the agent connection again. You should see:
- ✅ No more "Invalid WebSocket Header" errors
- ✅ WebSocket connection successful
- ✅ Live stream working

































