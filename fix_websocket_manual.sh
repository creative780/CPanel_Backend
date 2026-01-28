#!/bin/bash
# Manual WebSocket Configuration - Finds and configures nginx directly

echo "=========================================="
echo "WebSocket Proxy Configuration"
echo "=========================================="
echo ""

# Find nginx config files
echo "Searching for nginx configuration files..."
echo ""

# Search common locations
SEARCH_PATHS=(
    "/etc/nginx/sites-available"
    "/etc/nginx/conf.d"
    "/etc/nginx"
)

FOUND_CONFIGS=()

for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        while IFS= read -r file; do
            if grep -q "api.crm.click2print.store" "$file" 2>/dev/null; then
                FOUND_CONFIGS+=("$file")
            fi
        done < <(find "$path" -name "*.conf" -type f 2>/dev/null)
    fi
done

# Also check main nginx.conf
if [ -f "/etc/nginx/nginx.conf" ]; then
    if grep -q "api.crm.click2print.store" "/etc/nginx/nginx.conf" 2>/dev/null; then
        FOUND_CONFIGS+=("/etc/nginx/nginx.conf")
    fi
fi

if [ ${#FOUND_CONFIGS[@]} -eq 0 ]; then
    echo "❌ Could not find nginx config with api.crm.click2print.store"
    echo ""
    echo "Please provide the path manually:"
    read -p "Nginx config file path: " MANUAL_PATH
    if [ -f "$MANUAL_PATH" ]; then
        FOUND_CONFIGS=("$MANUAL_PATH")
    else
        echo "❌ File not found: $MANUAL_PATH"
        exit 1
    fi
elif [ ${#FOUND_CONFIGS[@]} -eq 1 ]; then
    NGINX_CONF="${FOUND_CONFIGS[0]}"
    echo "✓ Found config: $NGINX_CONF"
else
    echo "Found multiple config files:"
    for i in "${!FOUND_CONFIGS[@]}"; do
        echo "  $((i+1)). ${FOUND_CONFIGS[$i]}"
    done
    read -p "Select config file (1-${#FOUND_CONFIGS[@]}): " SELECTION
    NGINX_CONF="${FOUND_CONFIGS[$((SELECTION-1))]}"
fi

echo ""
echo "Using: $NGINX_CONF"
echo ""

# Create backup
BACKUP="${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$NGINX_CONF" "$BACKUP"
echo "✓ Backup created: $BACKUP"
echo ""

# Check if WebSocket config exists
if grep -q "location /ws/" "$NGINX_CONF"; then
    echo "⚠ WebSocket configuration already exists"
    read -p "Replace it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing
        sed -i '/location \/ws\/ {/,/^[[:space:]]*}/d' "$NGINX_CONF"
        echo "✓ Removed existing WebSocket config"
    else
        echo "Keeping existing configuration"
        exit 0
    fi
fi

# WebSocket configuration block
WS_BLOCK='    # WebSocket proxy configuration
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

# Add WebSocket config to server block
TEMP_FILE=$(mktemp)
IN_SERVER=0
WS_ADDED=0
BRACE_COUNT=0

while IFS= read -r line; do
    # Detect server block start
    if [[ $line =~ server_name.*api.crm.click2print.store ]]; then
        IN_SERVER=1
        BRACE_COUNT=0
    fi
    
    # Count braces in server block
    if [ $IN_SERVER -eq 1 ]; then
        BRACE_COUNT=$((BRACE_COUNT + $(echo "$line" | grep -o '{' | wc -l)))
        BRACE_COUNT=$((BRACE_COUNT - $(echo "$line" | grep -o '}' | wc -l)))
        
        # If we hit the closing brace of server block and haven't added WS config
        if [ $BRACE_COUNT -eq 0 ] && [ $WS_ADDED -eq 0 ] && [[ $line =~ ^[[:space:]]*\} ]]; then
            echo "$WS_BLOCK" >> "$TEMP_FILE"
            WS_ADDED=1
        fi
    fi
    
    echo "$line" >> "$TEMP_FILE"
done < "$NGINX_CONF"

# If we didn't find server block, append to end
if [ $WS_ADDED -eq 0 ]; then
    echo "" >> "$TEMP_FILE"
    echo "$WS_BLOCK" >> "$TEMP_FILE"
    echo "⚠ Could not find server block, appended to end of file"
fi

mv "$TEMP_FILE" "$NGINX_CONF"
echo "✓ WebSocket configuration added"
echo ""

# Test configuration
echo "Testing nginx configuration..."
if nginx -t 2>&1; then
    echo "✓ Configuration test passed"
    echo ""
    echo "Reloading nginx..."
    
    # Try different reload methods
    if command -v systemctl &> /dev/null; then
        systemctl reload nginx 2>/dev/null && echo "✓ Nginx reloaded" || service nginx reload && echo "✓ Nginx reloaded"
    elif command -v service &> /dev/null; then
        service nginx reload && echo "✓ Nginx reloaded"
    else
        echo "⚠ Please reload nginx manually: nginx -s reload"
    fi
else
    echo "❌ Configuration test failed!"
    echo "Restoring backup..."
    mv "$BACKUP" "$NGINX_CONF"
    echo "Backup restored. Please check the configuration manually."
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Configuration complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Restart Django: pm2 restart app.crm.click2print.store"
echo "  2. Test agent connection"
echo "  3. Check logs: pm2 logs app.crm.click2print.store"
echo ""

































