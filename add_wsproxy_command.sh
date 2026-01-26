#!/bin/bash
# Add WebSocket Proxy to OpenLiteSpeed vhost.conf

VHOST="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

echo "Adding WebSocket Proxy configuration..."

# Backup
cp "$VHOST" "${VHOST}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✓ Backup created"

# Use Python for more reliable insertion
python3 << 'PYTHON_SCRIPT'
import re

vhost_file = "/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

with open(vhost_file, 'r') as f:
    content = f.read()

# Check if already exists
if 'wsProxy' in content:
    print("⚠ WebSocket Proxy already exists")
    exit(0)

# Find virtualhost block and insert before closing brace
pattern = r'(virtualhost\s*\{[^}]*)(\})'
ws_config = '''  wsProxy {
    uri                     /ws/
    address                 127.0.0.1:9000
  }
'''

def replacer(match):
    return match.group(1) + ws_config + match.group(2)

new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

if new_content != content:
    with open(vhost_file, 'w') as f:
        f.write(new_content)
    print("✓ WebSocket Proxy added")
else:
    print("❌ Failed to add WebSocket Proxy - manual edit required")
    exit(1)
PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo ""
    echo "Verifying configuration:"
    grep -A 3 "wsProxy" "$VHOST"
    echo ""
    echo "✓ Configuration added successfully"
else
    echo "❌ Failed to add configuration"
    exit 1
fi

































