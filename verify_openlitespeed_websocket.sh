#!/bin/bash
# Verify OpenLiteSpeed WebSocket Proxy Configuration

echo "=========================================="
echo "OpenLiteSpeed WebSocket Proxy Verification"
echo "=========================================="
echo ""

VHOST_CONFIG="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

if [ ! -f "$VHOST_CONFIG" ]; then
    echo "❌ Config not found: $VHOST_CONFIG"
    exit 1
fi

echo "Checking for WebSocket Proxy configuration..."
echo ""

# Check for WebSocket Proxy
if grep -q "wsProxy" "$VOST_CONFIG" || grep -q "websocketProxy" "$VHOST_CONFIG"; then
    echo "✓ WebSocket Proxy found:"
    grep -A 5 -i "wsProxy\|websocketProxy" "$VHOST_CONFIG" | head -10
else
    echo "❌ No WebSocket Proxy configuration found"
    echo ""
    echo "Checking for conflicting Context /ws/..."
    if grep -q "context /ws/" "$VHOST_CONFIG"; then
        echo "⚠ WARNING: Found Context /ws/ - this must be removed!"
        echo "OpenLiteSpeed cannot use Context for WebSockets"
        grep -A 5 "context /ws/" "$VHOST_CONFIG"
    fi
fi

echo ""
echo "Full vhost config (relevant sections):"
echo "----------------------------------------"
grep -E "wsProxy|websocketProxy|context /ws/" "$VHOST_CONFIG" || echo "No WebSocket config found"
echo ""

echo "Checking if LiteSpeed is running..."
if pgrep -l lshttpd > /dev/null; then
    echo "✓ LiteSpeed is running"
else
    echo "❌ LiteSpeed is not running"
fi

echo ""
echo "=========================================="

































