#!/bin/bash
# Simple WebSocket Proxy Fix - Direct nginx configuration

echo "=========================================="
echo "Simple WebSocket Proxy Configuration Fix"
echo "=========================================="
echo ""

# Find nginx config file
NGINX_CONF=""
DOMAIN="api.crm.click2print.store"

# Common locations
POSSIBLE_CONFS=(
    "/etc/nginx/sites-available/${DOMAIN}"
    "/etc/nginx/sites-available/api.crm.click2print.store"
    "/etc/nginx/conf.d/${DOMAIN}.conf"
    "/etc/nginx/nginx.conf"
)

for conf in "${POSSIBLE_CONFS[@]}"; do
    if [ -f "$conf" ]; then
        NGINX_CONF="$conf"
        break
    fi
done

# If not found, search for domain
if [ -z "$NGINX_CONF" ]; then
    FOUND=$(grep -r "$DOMAIN" /etc/nginx/ 2>/dev/null | head -1 | cut -d: -f1)
    if [ -n "$FOUND" ] && [ -f "$FOUND" ]; then
        NGINX_CONF="$FOUND"
    fi
fi

if [ -z "$NGINX_CONF" ]; then
    echo "❌ Could not find nginx config file"
    echo ""
    echo "Please provide the path to your nginx config file:"
    read -p "Config file path: " NGINX_CONF
    if [ ! -f "$NGINX_CONF" ]; then
        echo "❌ File not found: $NGINX_CONF"
        exit 1
    fi
fi

echo "✓ Found nginx config: $NGINX_CONF"
echo ""

# Create backup
BACKUP="${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$NGINX_CONF" "$BACKUP"
echo "✓ Backup created: $BACKUP"
echo ""

# Check if WebSocket config exists
if grep -q "location /ws/" "$NGINX_CONF"; then
    echo "⚠ WebSocket configuration already exists"
    read -p "Update it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping..."
        exit 0
    fi
    # Remove existing
    sed -i '/location \/ws\/ {/,/^[[:space:]]*}/d' "$NGINX_CONF"
fi

# WebSocket configuration
WS_CONFIG='    # WebSocket proxy configuration
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
    }'

# Add to config file (before last closing brace of server block)
if grep -q "server_name.*${DOMAIN}" "$NGINX_CONF"; then
    # Insert before the closing brace of server block
    awk -v ws="$WS_CONFIG" '
    /server_name.*api.crm.click2print.store/ { in_server=1 }
    in_server && /^[[:space:]]*}/ && !added {
        print ws
        added=1
    }
    { print }
    ' "$NGINX_CONF" > "${NGINX_CONF}.tmp" && mv "${NGINX_CONF}.tmp" "$NGINX_CONF"
    
    echo "✓ WebSocket configuration added"
else
    # Append to end
    echo "" >> "$NGINX_CONF"
    echo "$WS_CONFIG" >> "$NGINX_CONF"
    echo "✓ WebSocket configuration appended"
fi

echo ""

# Test configuration
echo "Testing nginx configuration..."
if nginx -t 2>&1; then
    echo "✓ Configuration test passed"
    echo ""
    echo "Reloading nginx..."
    if systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null; then
        echo "✓ Nginx reloaded successfully"
    else
        echo "❌ Failed to reload nginx"
        exit 1
    fi
else
    echo "❌ Configuration test failed"
    echo "Restoring backup..."
    mv "$BACKUP" "$NGINX_CONF"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Configuration complete!"
echo "=========================================="
echo ""
echo "Next: Restart Django application:"
echo "  pm2 restart app.crm.click2print.store"
echo ""

































