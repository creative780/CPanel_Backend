#!/bin/bash
# Final fix - add wsProxy inside virtualhost block

VHOST="/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

echo "Adding wsProxy configuration..."

# Backup
cp "$VHOST" "${VHOST}.backup.$(date +%Y%m%d_%H%M%S)"

# Use Python to insert before the closing brace of virtualhost
python3 << 'PYEOF'
vhost_file = "/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

with open(vhost_file, 'r') as f:
    lines = f.readlines()

# Check if already exists
if any('wsProxy' in line for line in lines):
    print("⚠ wsProxy already exists")
    exit(0)

# Find the closing brace of virtualhost block
# Look for the first standalone '}' after virtualhost that closes the virtualhost block
in_vhost = False
brace_count = 0
insert_pos = -1

for i, line in enumerate(lines):
    if 'virtualhost' in line.lower() and '{' in line:
        in_vhost = True
        brace_count = 1
        continue
    
    if in_vhost:
        # Count braces
        for char in line:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                # When brace_count reaches 1, we're about to close virtualhost
                if brace_count == 1 and line.strip() == '}':
                    insert_pos = i
                    break
        
        if insert_pos != -1:
            break

if insert_pos == -1:
    print("❌ Could not find virtualhost closing brace")
    exit(1)

# Insert wsProxy block before the closing brace
ws_config = [
    "  wsProxy {\n",
    "    uri                     /ws/\n",
    "    address                 127.0.0.1:9000\n",
    "  }\n",
    "\n"
]

new_lines = lines[:insert_pos] + ws_config + lines[insert_pos:]

with open(vhost_file, 'w') as f:
    f.writelines(new_lines)

print("✓ wsProxy added successfully")
print("")
print("Added configuration:")
for line in ws_config:
    print(line.rstrip())
PYEOF

if [ $? -eq 0 ]; then
    echo ""
    echo "Verifying:"
    grep -A 3 "wsProxy" "$VHOST"
    echo ""
    echo "✓ Configuration complete!"
else
    echo "❌ Failed - will try manual method"
fi

































