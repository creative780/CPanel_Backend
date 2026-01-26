#!/bin/bash
# Check LiteSpeed WebSocket configuration

echo "=========================================="
echo "LiteSpeed WebSocket Configuration Check"
echo "=========================================="
echo ""

VHOST_CONFIG="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

if [ ! -f "$VHOST_CONFIG" ]; then
    echo "❌ Config not found: $VHOST_CONFIG"
    exit 1
fi

echo "Current configuration for /ws/ context:"
echo "----------------------------------------"
grep -A 10 "context /ws/" "$VHOST_CONFIG" || echo "❌ No /ws/ context found"
echo ""

echo "Full vhost config:"
echo "----------------------------------------"
cat "$VHOST_CONFIG"
echo ""

































