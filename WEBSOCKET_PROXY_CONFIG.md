# WebSocket Proxy Configuration Guide

## Problem: "Invalid WebSocket Header" Error

The "Invalid WebSocket Header" error occurs when the reverse proxy (nginx/apache) is not properly configured to forward WebSocket connections to Django Channels.

## Solution: Configure Nginx for WebSocket

### Nginx Configuration

Add this to your nginx configuration file (usually in `/etc/nginx/sites-available/api.crm.click2print.store` or similar):

```nginx
server {
    listen 443 ssl http2;
    server_name api.crm.click2print.store;

    # SSL configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # WebSocket proxy configuration
    location /ws/ {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        
        # WebSocket upgrade headers
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket specific timeouts
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60;
        
        # Disable buffering for WebSocket
        proxy_buffering off;
    }

    # Regular HTTP API proxy
    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apache Configuration (if using Apache)

If you're using Apache instead of nginx, add this to your virtual host configuration:

```apache
<VirtualHost *:443>
    ServerName api.crm.click2print.store
    
    # SSL configuration
    SSLEngine on
    SSLCertificateFile /path/to/ssl/cert.pem
    SSLCertificateKeyFile /path/to/ssl/key.pem

    # WebSocket proxy configuration
    <Location /ws/>
        ProxyPass ws://127.0.0.1:9000/ws/
        ProxyPassReverse ws://127.0.0.1:9000/ws/
        
        # WebSocket upgrade headers
        RewriteEngine on
        RewriteCond %{HTTP:Upgrade} websocket [NC]
        RewriteCond %{HTTP:Connection} upgrade [NC]
        RewriteRule ^/?(.*) "ws://127.0.0.1:9000/$1" [P,L]
        
        # Standard proxy headers
        ProxyPreserveHost On
        RequestHeader set X-Real-IP %{REMOTE_ADDR}s
        RequestHeader set X-Forwarded-For %{REMOTE_ADDR}s
        RequestHeader set X-Forwarded-Proto https
    </Location>

    # Regular HTTP API proxy
    ProxyPass / http://127.0.0.1:9000/
    ProxyPassReverse / http://127.0.0.1:9000/
    ProxyPreserveHost On
</VirtualHost>
```

## Verification Steps

1. **Test WebSocket connection directly (bypassing proxy):**
   ```bash
   # On the server, test direct connection
   wscat -c ws://127.0.0.1:9000/ws/monitoring/?token=YOUR_TOKEN
   ```

2. **Check nginx error logs:**
   ```bash
   tail -f /var/log/nginx/error.log
   ```

3. **Check Django Channels logs:**
   ```bash
   # Check gunicorn logs for WebSocket connection attempts
   pm2 logs app.crm.click2print.store
   ```

4. **Test from browser console:**
   ```javascript
   const ws = new WebSocket('wss://api.crm.click2print.store/ws/monitoring/?token=YOUR_TOKEN');
   ws.onopen = () => console.log('Connected!');
   ws.onerror = (e) => console.error('Error:', e);
   ```

## Common Issues

1. **Missing Upgrade header**: The proxy must forward the `Upgrade: websocket` header
2. **Connection header**: Must be set to `upgrade` (not `Upgrade`)
3. **Timeouts**: WebSocket connections need longer timeouts than regular HTTP
4. **Buffering**: Must be disabled for WebSocket connections

## After Configuration

1. Reload nginx/apache:
   ```bash
   # Nginx
   sudo nginx -t  # Test configuration
   sudo systemctl reload nginx
   
   # Apache
   sudo apachectl configtest  # Test configuration
   sudo systemctl reload apache2
   ```

2. Restart Django application:
   ```bash
   pm2 restart app.crm.click2print.store
   ```

3. Test the agent connection again

































