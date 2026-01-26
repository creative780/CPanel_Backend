# Add WebSocket Configuration - Step by Step

Since automatic detection failed, follow these steps:

## Step 1: Find Your Web Server Config

Run this diagnostic script:
```bash
cd /home/api.crm.click2print.store/public_html/CRM_BACKEND
bash diagnose_webserver.sh
```

## Step 2: Based on Output

### If you see nginx:

1. Find your nginx config:
   ```bash
   find /etc/nginx -name "*.conf" -type f | xargs grep -l "api.crm.click2print.store" 2>/dev/null
   ```
   
   Or check:
   ```bash
   ls -la /etc/nginx/sites-available/
   ls -la /etc/nginx/conf.d/
   ```

2. Edit the config file and add this **inside the server block**:

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

3. Test and reload:
   ```bash
   nginx -t
   nginx -s reload
   # OR
   systemctl reload nginx
   ```

### If you see Apache:

1. Find your Apache config:
   ```bash
   find /etc/apache2 -name "*.conf" -o -name "*api.crm*" 2>/dev/null
   find /etc/httpd -name "*.conf" -o -name "*api.crm*" 2>/dev/null
   ```

2. Add this to your virtual host:

   ```apache
   <Location /ws/>
       ProxyPass ws://127.0.0.1:9000/ws/
       ProxyPassReverse ws://127.0.0.1:9000/ws/
       RewriteEngine on
       RewriteCond %{HTTP:Upgrade} websocket [NC]
       RewriteCond %{HTTP:Connection} upgrade [NC]
       RewriteRule ^/?(.*) "ws://127.0.0.1:9000/$1" [P,L]
   </Location>
   ```

3. Enable required modules and reload:
   ```bash
   a2enmod proxy
   a2enmod proxy_http
   a2enmod proxy_wstunnel
   a2enmod rewrite
   systemctl reload apache2
   ```

### If using cPanel/DirectAdmin:

The config is usually in:
- cPanel: `/usr/local/apache/conf/userdata/std/2/*/api.crm.click2print.store.conf`
- DirectAdmin: `/usr/local/directadmin/data/users/*/httpd.conf`

Add the Apache configuration above to the virtual host.

## Step 3: Restart Django

```bash
pm2 restart app.crm.click2print.store
```

## Step 4: Test

Try the agent connection again. The "Invalid WebSocket Header" error should be gone.

































