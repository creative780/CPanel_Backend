# OpenLiteSpeed WebSocket Proxy Configuration

## Important: OpenLiteSpeed vs LiteSpeed Enterprise

OpenLiteSpeed uses **WebSocket Proxy** (not Context blocks) for WebSocket support.

## Current Status Check

Run this to verify your configuration:

```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
bash verify_openlitespeed_websocket.sh
```

## If WebSocket Proxy is Missing

### Option 1: Use the Fix Script

```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
bash fix_openlitespeed_websocket.sh
pm2 restart app.crm.click2print.store
```

### Option 2: Manual Configuration via Web Panel

1. **Access OpenLiteSpeed Admin Panel**
   - URL: `https://your-server-ip:7080` or `https://your-server-ip:8443`

2. **Navigate to Virtual Host**
   - Left sidebar → **Virtual Hosts**
   - Click on **api.crm.click2print.store**

3. **Go to WebSocket Proxy Tab**
   - Click the **"WebSocket Proxy"** tab
   - (It's next to Basic / General / Log / Security / Context / Rewrite)

4. **Add WebSocket Proxy**
   - Click **Add** button
   - Enter:
     - **URI:** `/ws/`
     - **Backend:** `127.0.0.1:9000`
     - **Notes:** (optional, leave blank)
   - Click **Save**

5. **Remove Any Context /ws/ Block**
   - Go to **Context** tab
   - If you see a context with URI `/ws/`, **DELETE IT**
   - OpenLiteSpeed cannot use Context for WebSockets

6. **Graceful Restart**
   - Go to main dashboard
   - Click **Actions** → **Graceful Restart**

### Option 3: Manual Edit Config File

```bash
nano /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

**Remove any existing Context /ws/ block** (if present).

**Add this inside the `virtualhost { ... }` block:**

```
  wsProxy {
    uri                     /ws/
    address                 127.0.0.1:9000
  }
```

Save (Ctrl+X, Y, Enter), then:

```bash
/usr/local/lsws/bin/lswsctrl reload
pm2 restart app.crm.click2print.store
```

## Verify Configuration

After configuration, verify:

```bash
# Check for WebSocket Proxy
grep -A 3 "wsProxy" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf

# Make sure NO Context /ws/ exists
grep "context /ws/" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
# (Should return nothing)
```

## Expected Configuration

Your `vhost.conf` should have:

```
virtualhost {
  # ... other config ...
  
  wsProxy {
    uri                     /ws/
    address                 127.0.0.1:9000
  }
  
  # ... other config ...
}
```

**NOT:**

```
context /ws/ {
  # This won't work for WebSockets in OpenLiteSpeed
}
```

## Troubleshooting

### Still Getting "Invalid WebSocket Header"?

1. **Verify WebSocket Proxy exists:**
   ```bash
   grep -A 3 "wsProxy" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
   ```

2. **Check for conflicting Context:**
   ```bash
   grep "context /ws/" /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
   ```
   If found, remove it!

3. **Restart LiteSpeed:**
   ```bash
   /usr/local/lsws/bin/lswsctrl reload
   # Or via web panel: Actions → Graceful Restart
   ```

4. **Restart Django:**
   ```bash
   pm2 restart app.crm.click2print.store
   ```

5. **Check LiteSpeed logs:**
   ```bash
   tail -f /usr/local/lsws/logs/error.log
   ```

6. **Test direct connection (bypass LiteSpeed):**
   ```bash
   # From server
   wscat -c ws://127.0.0.1:9000/ws/monitoring/stream/agent/dev_YOUR_DEVICE_ID/?token=YOUR_TOKEN
   ```
   If this works, the issue is with LiteSpeed configuration.

## Quick Fix Command

Run this to check and fix everything:

```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
bash verify_openlitespeed_websocket.sh
bash fix_openlitespeed_websocket.sh
pm2 restart app.crm.click2print.store
```

































