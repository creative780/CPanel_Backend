#!/bin/bash
# More robust method to add wsProxy to OpenLiteSpeed config

VHOST="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

echo "Checking current config structure..."
echo ""

# Show the structure around virtualhost
echo "Virtualhost block structure:"
grep -A 20 "virtualhost" "$VHOST" | head -25
echo ""

# Backup
cp "$VHOST" "${VHOST}.backup.$(date +%Y%m%d_%H%M%S)"
echo "✓ Backup created"
echo ""

# Try simpler approach - find last closing brace of virtualhost and insert before it
# Count lines to find where to insert
TOTAL_LINES=$(wc -l < "$VHOST")
echo "Total lines in config: $TOTAL_LINES"
echo ""

# Use a more reliable Python script
python3 << 'PYEOF'
import sys

vhost_file = "/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

try:
    with open(vhost_file, 'r') as f:
        lines = f.readlines()
    
    # Check if already exists
    content = ''.join(lines)
    if 'wsProxy' in content:
        print("⚠ WebSocket Proxy already exists")
        sys.exit(0)
    
    # Find virtualhost block
    in_vhost = False
    brace_level = 0
    insert_pos = -1
    
    for i, line in enumerate(lines):
        if 'virtualhost' in line.lower() and '{' in line:
            in_vhost = True
            brace_level = 1
            continue
        
        if in_vhost:
            # Count braces
            for char in line:
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
                    # When we hit brace_level 1, we're about to close virtualhost
                    if brace_level == 1:
                        insert_pos = i
                        break
            
            if insert_pos != -1:
                break
    
    if insert_pos == -1:
        print("❌ Could not find virtualhost closing brace")
        print("Please add manually via web panel or edit file directly")
        sys.exit(1)
    
    # Insert wsProxy block
    ws_config = [
        "  wsProxy {\n",
        "    uri                     /ws/\n",
        "    address                 127.0.0.1:9000\n",
        "  }\n"
    ]
    
    # Insert before the closing brace
    new_lines = lines[:insert_pos] + ws_config + lines[insert_pos:]
    
    with open(vhost_file, 'w') as f:
        f.writelines(new_lines)
    
    print("✓ WebSocket Proxy added successfully")
    print("")
    print("Added configuration:")
    for line in ws_config:
        print(line.rstrip())
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo "Verifying:"
    grep -A 3 "wsProxy" "$VHOST"
else
    echo ""
    echo "❌ Automatic insertion failed"
    echo "Please add manually - see instructions below"
fi

































