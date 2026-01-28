#!/usr/bin/env python3
"""
Simple script to add WebSocket configuration to LiteSpeed vhost.conf
"""

import os
import sys
from datetime import datetime

VHOST_CONFIG = "/usr/local/lsws/conf/vhosts/api.crm.click2print.store/vhost.conf"

WS_CONFIG = """  context /ws/ {
    type                    proxy
    handler                 lsphp
    addDefaultCharset       off
    proxy                   http://127.0.0.1:9000
    enableWebsocket         1
    websocketTimeout        86400
    addHeader               X-Real-IP $remote_addr
    addHeader               X-Forwarded-For $proxy_add_x_forwarded_for
    addHeader               X-Forwarded-Proto $scheme
  }"""

def main():
    print("=" * 50)
    print("LiteSpeed WebSocket Configuration Fix")
    print("=" * 50)
    print()
    
    if not os.path.exists(VHOST_CONFIG):
        print(f"❌ Config file not found: {VHOST_CONFIG}")
        sys.exit(1)
    
    print(f"✓ Found config: {VHOST_CONFIG}")
    print()
    
    # Backup
    backup_file = f"{VHOST_CONFIG}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(VHOST_CONFIG, 'r') as f:
        original_content = f.read()
    
    with open(backup_file, 'w') as f:
        f.write(original_content)
    print(f"✓ Backup created: {backup_file}")
    print()
    
    # Check if already exists
    if "context /ws/" in original_content:
        print("⚠ WebSocket context already exists. Removing old one...")
        lines = original_content.split('\n')
        new_lines = []
        skip = False
        for line in lines:
            if 'context /ws/' in line:
                skip = True
                continue
            if skip and line.strip() == '}':
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        original_content = '\n'.join(new_lines)
    
    # Find insertion point (before closing virtualhost brace)
    lines = original_content.split('\n')
    new_lines = []
    in_vhost = False
    brace_count = 0
    inserted = False
    
    for i, line in enumerate(lines):
        # Detect virtualhost block start
        if 'virtualhost' in line.lower() and '{' in line:
            in_vhost = True
            brace_count = 1
        
        # Track braces
        if in_vhost:
            brace_count += line.count('{') - line.count('}')
            
            # Insert before closing virtualhost brace
            if brace_count == 1 and line.strip() == '}' and not inserted:
                new_lines.append(WS_CONFIG)
                inserted = True
        
        new_lines.append(line)
    
    # If not inserted, append at end
    if not inserted:
        print("⚠ Could not find virtualhost closing brace, appending to end...")
        new_lines.append("")
        new_lines.append(WS_CONFIG)
    
    # Write new content
    new_content = '\n'.join(new_lines)
    with open(VHOST_CONFIG, 'w') as f:
        f.write(new_content)
    
    print("✓ WebSocket context added")
    print()
    print("Added configuration:")
    print("-" * 50)
    print(WS_CONFIG)
    print("-" * 50)
    print()
    
    # Verify
    print("Verifying configuration...")
    with open(VHOST_CONFIG, 'r') as f:
        content = f.read()
        if "context /ws/" in content and "enableWebsocket" in content:
            print("✓ Configuration verified")
        else:
            print("❌ Configuration verification failed!")
            sys.exit(1)
    
    print()
    print("=" * 50)
    print("Configuration complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("  1. Reload LiteSpeed: /usr/local/lsws/bin/lswsctrl reload")
    print("  2. Restart Django: pm2 restart app.crm.click2print.store")
    print("  3. Test agent connection")
    print()

if __name__ == "__main__":
    main()

































