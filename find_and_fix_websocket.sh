#!/bin/bash
# Find and fix WebSocket proxy configuration - Works with any setup

echo "=========================================="
echo "WebSocket Proxy Configuration Fix"
echo "=========================================="
echo ""

# Detect what's actually running
echo "Detecting web server setup..."
echo ""

# Check for nginx
if command -v nginx &> /dev/null || [ -f /usr/sbin/nginx ] || [ -f /usr/local/nginx/sbin/nginx ]; then
    NGINX_BIN=$(which nginx 2>/dev/null || echo "/usr/sbin/nginx" || echo "/usr/local/nginx/sbin/nginx")
    echo "✓ Found nginx: $NGINX_BIN"
    WEB_SERVER="nginx"
elif [ -d /etc/nginx ]; then
    echo "✓ Found nginx directory"
    WEB_SERVER="nginx"
    NGINX_BIN="nginx"
# Check for Apache
elif command -v apache2 &> /dev/null || command -v httpd &> /dev/null; then
    echo "✓ Found Apache"
    WEB_SERVER="apache"
# Check for cPanel/DirectAdmin
elif [ -d /usr/local/apache ] || [ -d /etc/httpd ]; then
    echo "✓ Found Apache (cPanel/DirectAdmin style)"
    WEB_SERVER="apache"
else
    echo "⚠ Could not detect web server"
    echo ""
    echo "Checking what's listening on port 80/443..."
    netstat -tlnp 2>/dev/null | grep -E ':(80|443)' || ss -tlnp 2>/dev/null | grep -E ':(80|443)'
    echo ""
    read -p "What web server are you using? (nginx/apache/other): " WEB_SERVER
fi

echo ""
echo "Using web server: $WEB_SERVER"
echo ""

# Find configuration files
if [ "$WEB_SERVER" = "nginx" ]; then
    echo "Searching for nginx configuration files..."
    
    # Search in common locations
    SEARCH_DIRS=(
        "/etc/nginx"
        "/usr/local/nginx/conf"
        "/opt/nginx/conf"
    )
    
    CONFIG_FILES=()
    
    for dir in "${SEARCH_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            while IFS= read -r file; do
                if [ -f "$file" ]; then
                    CONFIG_FILES+=("$file")
                fi
            done < <(find "$dir" -name "*.conf" -type f 2>/dev/null | head -20)
        fi
    done
    
    if [ ${#CONFIG_FILES[@]} -eq 0 ]; then
        echo "❌ No nginx config files found"
        echo ""
        echo "Please provide the path to your nginx configuration file:"
        read -p "Config file path: " MANUAL_CONFIG
        if [ -f "$MANUAL_CONFIG" ]; then
            CONFIG_FILES=("$MANUAL_CONFIG")
        else
            echo "❌ File not found"
            exit 1
        fi
    else
        echo "Found ${#CONFIG_FILES[@]} config file(s):"
        for i in "${!CONFIG_FILES[@]}"; do
            echo "  $((i+1)). ${CONFIG_FILES[$i]}"
        done
        
        if [ ${#CONFIG_FILES[@]} -eq 1 ]; then
            NGINX_CONF="${CONFIG_FILES[0]}"
        else
            read -p "Select config file (1-${#CONFIG_FILES[@]}): " SELECTION
            NGINX_CONF="${CONFIG_FILES[$((SELECTION-1))]}"
        fi
    fi
    
    echo ""
    echo "Using: $NGINX_CONF"
    echo ""
    
    # Create backup
    BACKUP="${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$NGINX_CONF" "$BACKUP"
    echo "✓ Backup created: $BACKUP"
    echo ""
    
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
    
    # Check if already exists
    if grep -q "location /ws/" "$NGINX_CONF"; then
        echo "⚠ WebSocket config already exists"
        read -p "Replace it? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sed -i '/location \/ws\/ {/,/^[[:space:]]*}/d' "$NGINX_CONF"
        else
            echo "Keeping existing config"
            exit 0
        fi
    fi
    
    # Add to config - try to find server block, otherwise append
    if grep -q "server {" "$NGINX_CONF"; then
        # Try to insert in server block
        TEMP=$(mktemp)
        awk -v ws="$WS_CONFIG" '
        /server \{/ { in_server=1; brace=0 }
        in_server { 
            brace += gsub(/\{/, "")
            brace -= gsub(/\}/, "")
            if (brace == 0 && in_server && !added) {
                print ws
                added=1
            }
        }
        { print }
        ' "$NGINX_CONF" > "$TEMP" && mv "$TEMP" "$NGINX_CONF"
    else
        # Append to end
        echo "" >> "$NGINX_CONF"
        echo "$WS_CONFIG" >> "$NGINX_CONF"
    fi
    
    echo "✓ WebSocket configuration added"
    echo ""
    
    # Test and reload
    echo "Testing configuration..."
    if $NGINX_BIN -t 2>&1; then
        echo "✓ Configuration test passed"
        echo ""
        echo "Reloading nginx..."
        
        # Try different reload methods
        if systemctl reload nginx 2>/dev/null; then
            echo "✓ Nginx reloaded via systemctl"
        elif service nginx reload 2>/dev/null; then
            echo "✓ Nginx reloaded via service"
        elif $NGINX_BIN -s reload 2>/dev/null; then
            echo "✓ Nginx reloaded via signal"
        else
            echo "⚠ Could not reload nginx automatically"
            echo "Please reload manually: $NGINX_BIN -s reload"
        fi
    else
        echo "❌ Configuration test failed!"
        echo "Restoring backup..."
        mv "$BACKUP" "$NGINX_CONF"
        exit 1
    fi
    
elif [ "$WEB_SERVER" = "apache" ]; then
    echo "⚠ Apache configuration requires manual editing"
    echo ""
    echo "Please add this to your Apache virtual host configuration:"
    echo ""
    echo "<Location /ws/>"
    echo "    ProxyPass ws://127.0.0.1:9000/ws/"
    echo "    ProxyPassReverse ws://127.0.0.1:9000/ws/"
    echo "    RewriteEngine on"
    echo "    RewriteCond %{HTTP:Upgrade} websocket [NC]"
    echo "    RewriteCond %{HTTP:Connection} upgrade [NC]"
    echo "    RewriteRule ^/?(.*) \"ws://127.0.0.1:9000/\$1\" [P,L]"
    echo "</Location>"
    echo ""
    echo "Then reload Apache:"
    echo "  systemctl reload apache2  # or httpd"
    exit 0
else
    echo "⚠ Unknown web server"
    echo "Please configure WebSocket manually. See WEBSOCKET_PROXY_CONFIG.md"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Configuration complete!"
echo "=========================================="
echo ""
echo "Next: Restart Django application"
echo "  pm2 restart app.crm.click2print.store"
echo ""

































