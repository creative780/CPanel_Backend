# Manual LiteSpeed WebSocket Fix

Since the web panel didn't save the configuration, here's how to fix it manually:

## Step 1: View Current Config

```bash
cat /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

## Step 2: Edit the Config File

```bash
nano /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

## Step 3: Find the `virtualhost` Block

Look for a section that starts with:
```
virtualhost {
```

## Step 4: Add WebSocket Context

**Inside** the `virtualhost { ... }` block (before the closing `}`), add:

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

**Important:** 
- Must be **inside** the `virtualhost { ... }` block
- Use proper indentation (2 spaces)
- Make sure it's before the closing `}` of the virtualhost block

## Step 5: Save and Exit

- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

## Step 6: Reload LiteSpeed

```bash
/usr/local/lsws/bin/lswsctrl reload
```

## Step 7: Restart Django

```bash
pm2 restart app.crm.click2print.store
```

## Step 8: Verify

```bash
grep -A 10 "context /ws/" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

You should see the WebSocket configuration.

## Alternative: Use the Python Script

If you prefer automation:

```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
python3 fix_litespeed_websocket_simple.py
/usr/local/lsws/bin/lswsctrl reload
pm2 restart app.crm.click2print.store
```

































