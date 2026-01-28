# Troubleshooting LiteSpeed WebSocket Issues

## Problem: Still Getting "Invalid WebSocket Header" After Configuration

If you've configured LiteSpeed via the web panel but still get errors, try these steps:

## Step 1: Verify Configuration Was Applied

```bash
# Check if /ws/ context exists
grep -A 10 "context /ws/" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

If nothing is found, the configuration wasn't saved properly.

## Step 2: Run the Complete Fix Script

```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
bash fix_litespeed_websocket_complete.sh
```

This script will:
- Remove any incomplete configurations
- Add the complete WebSocket context
- Reload LiteSpeed

## Step 3: Manual Configuration (If Script Fails)

Edit the config file directly:

```bash
nano /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

Find the `virtualhost` block and add this **inside** it (before the closing `}`):

```
  context /ws/ {
    type                    proxy
    handler                 lsphp
    addDefaultCharset       off
    proxy                   http://127.0.0.1:9000
    enableWebsocket         1
    websocketTimeout        86400
    addHeader               X-Real-IP $remote_addr
    addHeader               X-Forwarded-For $proxy_add_x_forwarded_for
    addHeader               X-Forwarded-Proto $scheme
  }
```

**Important:** Make sure this is inside the `virtualhost { ... }` block, not outside.

## Step 4: Verify LiteSpeed Version

Some LiteSpeed versions have different WebSocket support:

```bash
cat /usr/local/lsws/VERSION
```

If you're using LiteSpeed OpenLiteSpeed (free version), WebSocket support may be limited. You might need:
- LiteSpeed Enterprise (paid version) for full WebSocket support
- Or configure it differently

## Step 5: Check LiteSpeed Logs

```bash
# Error logs
tail -f /usr/local/lsws/logs/error.log

# Access logs
tail -f /usr/local/lsws/logs/access.log
```

Look for WebSocket connection attempts and any errors.

## Step 6: Test Direct Connection

From the server, test if Django Channels is working:

```bash
# Install wscat if needed
npm install -g wscat

# Test direct connection (bypass LiteSpeed)
wscat -c ws://127.0.0.1:9000/ws/monitoring/stream/agent/dev_f3c9831954ed/?token=YOUR_TOKEN
```

If this works, the issue is definitely with LiteSpeed configuration.

## Step 7: Alternative - Use Rewrite Rules

If `enableWebsocket` doesn't work, try using rewrite rules in LiteSpeed:

In the vhost config, add:

```
  rewrite  {
    enable                  1
    rules                   RewriteRule ^ws/(.*)$ ws://127.0.0.1:9000/ws/$1 [P,L]
  }
```

## Step 8: Check Django Channels Logs

```bash
pm2 logs app.crm.click2print.store | grep -i websocket
```

See if connections are reaching Django at all.

## Common Issues

1. **Context not inside virtualhost block** - Must be inside `virtualhost { ... }`
2. **Wrong proxy address** - Must be `http://127.0.0.1:9000` (not https)
3. **LiteSpeed not reloaded** - Must reload after changes
4. **WebSocket not enabled in LiteSpeed version** - Check if your version supports it

## Quick Fix Command

Run this to check and fix everything:

```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
bash check_litespeed_config.sh
bash fix_litespeed_websocket_complete.sh
pm2 restart app.crm.click2print.store
```

































