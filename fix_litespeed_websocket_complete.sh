#!/bin/bash
# Complete LiteSpeed WebSocket Fix - Ensures proper configuration

echo "=========================================="
echo "Complete LiteSpeed WebSocket Configuration"
echo "=========================================="
echo ""

VHOST_CONFIG="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

if [ ! -f "$VHOST_CONFIG" ]; then
    echo "❌ Config not found: $VHOST_CONFIG"
    exit 1
fi

echo "✓ Found config: $VHOST_CONFIG"
echo ""

# Backup
BACKUP="${VHOST_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$VHOST_CONFIG" "$BACKUP"
echo "✓ Backup: $BACKUP"
echo ""

# Remove any existing /ws/ context
if grep -q "context /ws/" "$VHOST_CONFIG"; then
    echo "Removing existing /ws/ context..."
    sed -i '/context \/ws\/ {/,/^[[:space:]]*}/d' "$VHOST_CONFIG"
fi

# Read config to find insertion point
TEMP=$(mktemp)
IN_VHOST=0
BRACE=0
ADDED=0

while IFS= read -r line; do
    # Detect virtualhost block
    if [[ $line =~ virtualhost ]]; then
        IN_VHOST=1
        BRACE=0
    fi
    
    # Track braces in virtualhost
    if [ $IN_VHOST -eq 1 ]; then
        BRACE=$((BRACE + $(echo "$line" | grep -o '{' | wc -l)))
        BRACE=$((BRACE - $(echo "$line" | grep -o '}' | wc -l)))
        
        # Insert before closing virtualhost brace
        if [ $BRACE -eq 1 ] && [ $ADDED -eq 0 ] && [[ $line =~ ^[[:space:]]*\}$ ]]; then
            echo "  context /ws/ {" >> "$TEMP"
            echo "    type                    proxy" >> "$TEMP"
            echo "    handler                 lsphp" >> "$TEMP"
            echo "    addDefaultCharset       off" >> "$TEMP"
            echo "    proxy                   http://127.0.0.1:9000" >> "$TEMP"
            echo "    enableWebsocket         1" >> "$TEMP"
            echo "    websocketTimeout        86400" >> "$TEMP"
            echo "    addHeader               X-Real-IP \$remote_addr" >> "$TEMP"
            echo "    addHeader               X-Forwarded-For \$proxy_add_x_forwarded_for" >> "$TEMP"
            echo "    addHeader               X-Forwarded-Proto \$scheme" >> "$TEMP"
            echo "  }" >> "$TEMP"
            ADDED=1
        fi
    fi
    
    echo "$line" >> "$TEMP"
done < "$VHOST_CONFIG"

# If not added, append
if [ $ADDED -eq 0 ]; then
    echo "" >> "$TEMP"
    echo "  context /ws/ {" >> "$TEMP"
    echo "    type                    proxy" >> "$TEMP"
    echo "    handler                 lsphp" >> "$TEMP"
    echo "    addDefaultCharset       off" >> "$TEMP"
    echo "    proxy                   http://127.0.0.1:9000" >> "$TEMP"
    echo "    enableWebsocket         1" >> "$TEMP"
    echo "    websocketTimeout        86400" >> "$TEMP"
    echo "    addHeader               X-Real-IP \$remote_addr" >> "$TEMP"
    echo "    addHeader               X-Forwarded-For \$proxy_add_x_forwarded_for" >> "$TEMP"
    echo "    addHeader               X-Forwarded-Proto \$scheme" >> "$TEMP"
    echo "  }" >> "$TEMP"
fi

mv "$TEMP" "$VHOST_CONFIG"
echo "✓ WebSocket context configured"
echo ""

# Show what was added
echo "Added configuration:"
echo "----------------------------------------"
grep -A 12 "context /ws/" "$VHOST_CONFIG"
echo ""

# Reload LiteSpeed
echo "Reloading LiteSpeed..."
if [ -f /usr/local/lsws/bin/lswsctrl ]; then
    /usr/local/lsws/bin/lswsctrl reload
    if [ $? -eq 0 ]; then
        echo "✓ LiteSpeed reloaded successfully"
    else
        echo "❌ Failed to reload LiteSpeed"
        echo "Try manually: /usr/local/lsws/bin/lswsctrl reload"
    fi
else
    echo "⚠ LiteSpeed control script not found"
    echo "Please reload manually"
fi

echo ""
echo "=========================================="
echo "Configuration complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Restart Django: pm2 restart app.crm.click2print.store"
echo "  2. Test agent connection again"
echo "  3. Check LiteSpeed logs: tail -f /usr/local/lsws/logs/error.log"
echo ""

































