#!/bin/bash
# WebSocket Proxy Configuration for LiteSpeed Web Server

echo "=========================================="
echo "LiteSpeed WebSocket Proxy Configuration"
echo "=========================================="
echo ""

# Find LiteSpeed vhost config
VHOST_CONFIG="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

if [ ! -f "$VHOST_CONFIG" ]; then
    echo "❌ VHost config not found at: $VHOST_CONFIG"
    echo ""
    echo "Searching for LiteSpeed config files..."
    find /usr/local/lsws/conf -name "*api.crm*" -o -name "vhost.conf" 2>/dev/null | head -5
    echo ""
    read -p "Enter path to vhost.conf: " VHOST_CONFIG
    if [ ! -f "$VHOST_CONFIG" ]; then
        echo "❌ File not found: $VHOST_CONFIG"
        exit 1
    fi
fi

echo "✓ Found LiteSpeed vhost config: $VHOST_CONFIG"
echo ""

# Create backup
BACKUP="${VHOST_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$VHOST_CONFIG" "$BACKUP"
echo "✓ Backup created: $BACKUP"
echo ""

# Check if WebSocket config exists
if grep -q "map.*ws" "$VHOST_CONFIG" || grep -q "context.*ws" "$VHOST_CONFIG"; then
    echo "⚠ WebSocket configuration may already exist"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# LiteSpeed WebSocket configuration
# LiteSpeed uses a different format - we need to add a context for /ws/
WS_CONTEXT='  context /ws/ {
    type                    proxy
    handler                 lsphp
    addDefaultCharset       off
    
    # Proxy to Django Channels
    proxy                   http://127.0.0.1:9000
    
    # WebSocket support
    enableWebsocket         1
    websocketTimeout        86400
    
    # Additional proxy headers
    addHeader               X-Real-IP $remote_addr
    addHeader               X-Forwarded-For $proxy_add_x_forwarded_for
    addHeader               X-Forwarded-Proto $scheme
  }'

# Read current config
CONTENT=$(cat "$VHOST_CONFIG")

# Check if we need to add it inside a virtualhost block
if echo "$CONTENT" | grep -q "virtualhost"; then
    # Find virtualhost block and add context before closing brace
    TEMP_FILE=$(mktemp)
    
    awk -v ws="$WS_CONTEXT" '
    /virtualhost/ { in_vhost=1; brace=0 }
    in_vhost {
        brace += gsub(/\{/, "")
        brace -= gsub(/\}/, "")
        if (brace == 1 && in_vhost && !added) {
            print ws
            added=1
        }
    }
    { print }
    ' "$VHOST_CONFIG" > "$TEMP_FILE"
    
    mv "$TEMP_FILE" "$VHOST_CONFIG"
    echo "✓ WebSocket context added to virtualhost"
else
    # Append to end of file
    echo "" >> "$VHOST_CONFIG"
    echo "$WS_CONTEXT" >> "$VHOST_CONFIG"
    echo "✓ WebSocket context appended to config"
fi

echo ""

# Reload LiteSpeed
echo "Reloading LiteSpeed Web Server..."
if [ -f /usr/local/lsws/bin/lswsctrl ]; then
    /usr/local/lsws/bin/lswsctrl reload
    echo "✓ LiteSpeed reloaded"
elif command -v systemctl &> /dev/null && systemctl is-active --quiet lsws; then
    systemctl reload lsws
    echo "✓ LiteSpeed reloaded via systemctl"
else
    echo "⚠ Could not reload LiteSpeed automatically"
    echo "Please reload manually: /usr/local/lsws/bin/lswsctrl reload"
fi

echo ""
echo "=========================================="
echo "✓ Configuration complete!"
echo "=========================================="
echo ""
echo "Note: LiteSpeed WebSocket configuration may require additional settings."
echo "If issues persist, you may need to configure via LiteSpeed Admin Panel:"
echo "  1. Go to Virtual Hosts > api.crm.click2print.store"
echo "  2. Add a Context: /ws/"
echo "  3. Set Type: Proxy"
echo "  4. Set Address: http://127.0.0.1:9000"
echo "  5. Enable WebSocket: Yes"
echo ""

