# LiteSpeed Web Server WebSocket Configuration

## Problem
LiteSpeed Web Server needs special configuration for WebSocket connections.

## Solution 1: Via LiteSpeed Admin Panel (Recommended)

1. **Access LiteSpeed Admin Panel:**
   - Usually at: `https://your-server-ip:7080` or `https://your-server-ip:8443`
   - Login with admin credentials

2. **Navigate to Virtual Host:**
   - Go to: **Virtual Hosts** → **api.crm.click2print.store**

3. **Add WebSocket Context:**
   - Click **Add** under **Contexts**
   - **URI:** `/ws/`
   - **Type:** `proxy`
   - **Address:** `http://127.0.0.1:9000`
   - **Enable WebSocket:** `Yes`
   - **WebSocket Timeout:** `86400`
   - Click **Save**

4. **Reload Configuration:**
   - Click **Graceful Restart** or use command: `/usr/local/lsws/bin/lswsctrl reload`

## Solution 2: Manual Configuration File Edit

1. **Edit vhost configuration:**
   ```bash
   nano /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
   ```

2. **Add this context block inside the virtualhost section:**
   ```
   context /ws/ {
     type                    proxy
     handler                 lsphp
     addDefaultCharset       off
     proxy                   http://127.0.0.1:9000
     enableWebsocket         1
     websocketTimeout        86400
   }
   ```

3. **Reload LiteSpeed:**
   ```bash
   /usr/local/lsws/bin/lswsctrl reload
   ```

## Solution 3: Use the Script

Run the automated script:
```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
bash fix_websocket_litespeed.sh
```

## Verify Configuration

After configuration, test the agent connection. The "Invalid WebSocket Header" error should be resolved.

## Troubleshooting

If WebSocket still doesn't work:

1. **Check LiteSpeed error logs:**
   ```bash
   tail -f /usr/local/lsws/logs/error.log
   ```

2. **Verify proxy settings in Admin Panel:**
   - Make sure the context `/ws/` is set to proxy type
   - Ensure WebSocket is enabled
   - Check that the proxy address is correct: `http://127.0.0.1:9000`

3. **Check if Django is listening:**
   ```bash
   netstat -tlnp | grep 9000
   ```

4. **Test direct connection (bypass LiteSpeed):**
   ```bash
   # From server, test direct connection
   wscat -c ws://127.0.0.1:9000/ws/monitoring/?token=YOUR_TOKEN
   ```

































