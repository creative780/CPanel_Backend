# Configure WebSocket via LiteSpeed Web Admin Panel

## Step 1: Access LiteSpeed Admin Panel

1. **Open your browser** and go to:
   ```
   https://your-server-ip:7080
   ```
   OR
   ```
   https://your-server-ip:8443
   ```
   
   (Replace `your-server-ip` with your actual server IP address)

2. **Login** with your LiteSpeed admin credentials
   - Default username: `admin`
   - Default password: (check your server documentation or `/usr/local/lsws/admin/htpasswd`)

## Step 2: Navigate to Virtual Host

1. In the left sidebar, click **Virtual Hosts**
2. Find and click on **api.crm.click2print.store**
3. You should see the virtual host configuration page

## Step 3: Add WebSocket Context

1. **Scroll down** to the **Contexts** section
2. Click **Add** button (or **Edit** if a context already exists)
3. Fill in the following settings:

   **Basic Settings:**
   - **URI:** `/ws/`
   - **Type:** Select `proxy` from dropdown
   - **Location:** Leave empty or set to `/ws/`

   **Proxy Settings:**
   - **Address:** `http://127.0.0.1:9000`
   - **Retry:** `0` (optional)
   - **Max Connections:** `-1` (unlimited) or leave default

   **WebSocket Settings:**
   - **Enable WebSocket:** Check/Enable this option ✅
   - **WebSocket Timeout:** `86400` (24 hours in seconds)

   **Additional Settings (if available):**
   - **Add Default Charset:** `off` or leave default
   - **Handler:** `lsphp` (if required)

4. Click **Save** or **Apply**

## Step 4: Restart LiteSpeed

1. Go back to the main dashboard
2. Click **Actions** → **Graceful Restart** (or **Restart**)
   - This will apply the changes without dropping connections

## Step 5: Verify Configuration

After restarting, the configuration should be active. Test by:
1. Running your agent again
2. The "Invalid WebSocket Header" error should be gone
3. WebSocket connections should work

## Visual Guide

```
LiteSpeed Admin Panel
├── Virtual Hosts
│   └── api.crm.click2print.store
│       ├── General
│       ├── Security
│       ├── SSL
│       ├── Contexts  ← Click here
│       │   └── Add New Context
│       │       ├── URI: /ws/
│       │       ├── Type: proxy
│       │       ├── Address: http://127.0.0.1:9000
│       │       └── Enable WebSocket: Yes ✅
│       └── ...
```

## Troubleshooting

If you can't find the WebSocket option:
1. Make sure you're using LiteSpeed Enterprise (WebSocket support may require Enterprise license)
2. Check LiteSpeed version: `cat /usr/local/lsws/VERSION`
3. If WebSocket option is not available, you may need to edit the config file directly

## Alternative: Edit Config File Directly

If the web panel doesn't have WebSocket options, edit the file directly:

```bash
nano /usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf
```

Add this inside the `virtualhost` block:
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

Then restart:
```bash
/usr/local/lsws/bin/lswsctrl reload
```

