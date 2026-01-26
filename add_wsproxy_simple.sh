#!/bin/bash
# Simple method to add wsProxy - shows structure first

VHOST="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

echo "First, let's see the file structure:"
echo "=========================================="
grep -n "virtualhost" "$VHOST" | head -5
echo ""
echo "Last 20 lines of file:"
tail -20 "$VHOST"
echo ""
echo "=========================================="
echo ""

# Backup
cp "$VHOST" "${VHOST}.backup.$(date +%Y%m%d_%H%M%S)"

# Simple approach: append before the last closing brace
# This works if virtualhost is the last block
python3 << 'PYEOF'
vhost_file = "/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

with open(vhost_file, 'r') as f:
    content = f.read()

if 'wsProxy' in content:
    print("Already exists")
    exit(0)

# Find the last closing brace (likely end of virtualhost)
lines = content.split('\n')
last_brace_line = -1
for i in range(len(lines) - 1, -1, -1):
    if lines[i].strip() == '}':
        last_brace_line = i
        break

if last_brace_line == -1:
    print("Could not find closing brace")
    exit(1)

# Insert wsProxy before last brace
ws_config = [
    "  wsProxy {",
    "    uri                     /ws/",
    "    address                 127.0.0.1:9000",
    "  }"
]

new_lines = lines[:last_brace_line] + ws_config + [''] + lines[last_brace_line:]

with open(vhost_file, 'w') as f:
    f.write('\n'.join(new_lines))

print("✓ Added before last closing brace")
PYEOF

echo ""
echo "Verifying:"
grep -A 3 "wsProxy" "$VHOST" || echo "Not found - manual edit needed"

































