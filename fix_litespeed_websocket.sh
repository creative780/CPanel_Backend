#!/bin/bash
# LiteSpeed WebSocket Configuration Script

echo "=========================================="
echo "LiteSpeed WebSocket Configuration"
echo "=========================================="
echo ""

VHOST_CONFIG="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

if [ ! -f "$VHOST_CONFIG" ]; then
    echo "❌ VHost config not found: $VHOST_CONFIG"
    echo ""
    echo "Searching for LiteSpeed config..."
    find /usr/local/lsws/conf -name "vhost.conf" 2>/dev/null | head -3
    echo ""
    read -p "Enter vhost.conf path: " VHOST_CONFIG
    if [ ! -f "$VHOST_CONFIG" ]; then
        echo "❌ File not found"
        exit 1
    fi
fi

echo "✓ Using config: $VHOST_CONFIG"
echo ""

# Backup
BACKUP="${VHOST_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$VHOST_CONFIG" "$BACKUP"
echo "✓ Backup: $BACKUP"
echo ""

# Check if already exists
if grep -q "context /ws/" "$VHOST_CONFIG"; then
    echo "⚠ WebSocket context already exists"
    read -p "Replace? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    # Remove existing
    sed -i '/context \/ws\/ {/,/^[[:space:]]*}/d' "$VHOST_CONFIG"
fi

# Read and add context
TEMP=$(mktemp)
IN_VHOST=0
BRACE=0
ADDED=0

while IFS= read -r line; do
    if [[ $line =~ virtualhost ]]; then
        IN_VHOST=1
        BRACE=0
    fi
    
    if [ $IN_VHOST -eq 1 ]; then
        BRACE=$((BRACE + $(echo "$line" | grep -o '{' | wc -l)))
        BRACE=$((BRACE - $(echo "$line" | grep -o '}' | wc -l)))
        
        # Add before closing virtualhost brace
        if [ $BRACE -eq 1 ] && [ $ADDED -eq 0 ] && [[ $line =~ ^[[:space:]]*\}$ ]]; then
            echo "  context /ws/ {" >> "$TEMP"
            echo "    type                    proxy" >> "$TEMP"
            echo "    handler                 lsphp" >> "$TEMP"
            echo "    addDefaultCharset       off" >> "$TEMP"
            echo "    proxy                   http://127.0.0.1:9000" >> "$TEMP"
            echo "    enableWebsocket         1" >> "$TEMP"
            echo "    websocketTimeout        86400" >> "$TEMP"
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
    echo "  }" >> "$TEMP"
fi

mv "$TEMP" "$VHOST_CONFIG"
echo "✓ WebSocket context added"
echo ""

# Reload LiteSpeed
echo "Reloading LiteSpeed..."
if [ -f /usr/local/lsws/bin/lswsctrl ]; then
    /usr/local/lsws/bin/lswsctrl reload
    echo "✓ LiteSpeed reloaded"
else
    echo "⚠ Please reload LiteSpeed manually: /usr/local/lsws/bin/lswsctrl reload"
fi

echo ""
echo "=========================================="
echo "✓ Complete!"
echo "=========================================="
echo ""
echo "Restart Django: pm2 restart app.crm.click2print.store"
echo ""

































