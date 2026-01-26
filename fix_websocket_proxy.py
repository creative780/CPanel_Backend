#!/usr/bin/env python3
"""
WebSocket Proxy Configuration Fix Script
Automatically configures nginx/apache to properly forward WebSocket connections
"""

import os
import sys
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.NC}")

def print_info(msg):
    print(f"ℹ {msg}")

def detect_web_server():
    """Detect which web server is running"""
    # Method 1: Check systemctl
    for server in ['nginx', 'apache2', 'httpd']:
        try:
            result = subprocess.run(['systemctl', 'is-active', server], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return server
        except:
            pass
    
    # Method 2: Check running processes
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'nginx' in result.stdout and 'master' in result.stdout:
            return 'nginx'
        if 'apache2' in result.stdout or 'httpd' in result.stdout:
            if 'apache2' in result.stdout:
                return 'apache2'
            return 'httpd'
    except:
        pass
    
    # Method 3: Check if nginx binary exists and config exists
    if os.path.exists('/usr/sbin/nginx') or os.path.exists('/usr/bin/nginx'):
        if os.path.exists('/etc/nginx/nginx.conf'):
            return 'nginx'
    
    # Method 4: Check if apache binary exists
    if os.path.exists('/usr/sbin/apache2') or os.path.exists('/usr/sbin/httpd'):
        return 'apache2'
    
    # Method 5: Check for common control panel configs
    if os.path.exists('/etc/nginx'):
        return 'nginx'
    if os.path.exists('/etc/apache2') or os.path.exists('/etc/httpd'):
        return 'apache2'
    
    return None

def find_nginx_config():
    """Find nginx configuration file for the domain"""
    domain = "api.crm.click2print.store"
    possible_paths = [
        f"/etc/nginx/sites-available/{domain}",
        "/etc/nginx/sites-available/api.crm.click2print.store",
        f"/etc/nginx/conf.d/{domain}.conf",
        "/etc/nginx/nginx.conf",
        "/usr/local/nginx/conf/nginx.conf",
        # Common control panel paths
        "/etc/nginx/conf.d/vhost.conf",
        "/etc/nginx/conf.d/default.conf",
        # cPanel paths
        "/usr/local/apache/conf/userdata/std/2/*/api.crm.click2print.store.conf",
    ]
    
    for path in possible_paths:
        if '*' in path:
            # Handle glob patterns
            import glob
            matches = glob.glob(path)
            if matches:
                return matches[0]
        elif os.path.exists(path):
            return path
    
    # Try to find by searching for domain in config files
    search_dirs = ['/etc/nginx', '/usr/local/nginx/conf']
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        try:
            result = subprocess.run(
                ['grep', '-r', '--include=*.conf', domain, search_dir],
                capture_output=True, text=True, stderr=subprocess.DEVNULL, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        file_path = line.split(':')[0].strip()
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            return file_path
        except:
            continue
    
    # Last resort: check main nginx.conf
    main_configs = ['/etc/nginx/nginx.conf', '/usr/local/nginx/conf/nginx.conf']
    for config in main_configs:
        if os.path.exists(config):
            return config
    
    return None

def configure_nginx(config_file):
    """Add WebSocket configuration to nginx config file"""
    print_info(f"Configuring nginx config: {config_file}")
    
    # Create backup
    backup_file = f"{config_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(config_file, backup_file)
    print_success(f"Backup created: {backup_file}")
    
    # Read current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Check if WebSocket config already exists
    if 'location /ws/' in content:
        print_warning("WebSocket configuration already exists")
        response = input("Do you want to update it? (y/n): ").strip().lower()
        if response != 'y':
            print_info("Skipping configuration update")
            return True
        
        # Remove existing /ws/ location block
        pattern = r'location /ws/ \{.*?\n\s*\}'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # WebSocket configuration block
    ws_config = """    # WebSocket proxy configuration
    location /ws/ {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        
        # WebSocket upgrade headers
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket timeouts
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60;
        
        # Disable buffering for WebSocket
        proxy_buffering off;
    }
"""
    
    # Find server block for the domain
    if 'server_name' in content and 'api.crm.click2print.store' in content:
        # Find the server block and insert before the closing brace
        lines = content.split('\n')
        new_lines = []
        in_server_block = False
        brace_count = 0
        ws_added = False
        
        for i, line in enumerate(lines):
            # Track if we're in the server block
            if 'server_name' in line and 'api.crm.click2print.store' in line:
                in_server_block = True
                brace_count = 0
            
            if in_server_block:
                # Count braces to find the end of server block
                brace_count += line.count('{')
                brace_count -= line.count('}')
                
                # If we're at the end of server block and haven't added WS config
                if brace_count == 0 and not ws_added and line.strip() == '}':
                    # Add WebSocket config before closing brace
                    new_lines.append(ws_config)
                    ws_added = True
            
            new_lines.append(line)
        
        if ws_added:
            content = '\n'.join(new_lines)
            print_success("WebSocket configuration added")
        else:
            # Fallback: append before the last closing brace
            if content.rstrip().endswith('}'):
                content = content.rstrip()[:-1] + ws_config + '\n}\n'
                print_success("WebSocket configuration added (fallback method)")
            else:
                print_error("Could not find insertion point for WebSocket config")
                return False
    else:
        print_warning("Could not find server block for api.crm.click2print.store")
        print_info("Appending WebSocket config to end of file")
        content += '\n' + ws_config
    
    # Write updated config
    with open(config_file, 'w') as f:
        f.write(content)
    
    return True

def test_nginx():
    """Test nginx configuration"""
    try:
        result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Nginx configuration test passed")
            return True
        else:
            print_error("Nginx configuration test failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print_error(f"Failed to test nginx: {e}")
        return False

def reload_nginx():
    """Reload nginx"""
    try:
        result = subprocess.run(['systemctl', 'reload', 'nginx'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Nginx reloaded successfully")
            return True
    except:
        pass
    
    try:
        result = subprocess.run(['service', 'nginx', 'reload'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Nginx reloaded successfully")
            return True
    except:
        pass
    
    print_error("Failed to reload nginx")
    return False

def restart_django():
    """Restart Django application"""
    print_info("Restarting Django application...")
    
    # Try PM2
    try:
        result = subprocess.run(['pm2', 'list'], capture_output=True, text=True)
        if 'app.crm.click2print.store' in result.stdout:
            subprocess.run(['pm2', 'restart', 'app.crm.click2print.store'])
            print_success("Django application restarted via PM2")
            return True
    except:
        pass
    
    # Try to find and restart gunicorn
    try:
        result = subprocess.run(['pgrep', '-f', 'gunicorn.*asgi'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print_warning("Found gunicorn process")
            print_info("Please restart gunicorn manually:")
            print_info("  cd /home/api.crm.click2print.store/public_html")
            print_info("  source venv/bin/activate")
            print_info("  pkill -f gunicorn")
            print_info("  gunicorn crm_backend.asgi:application --bind 0.0.0.0:9000 --workers 4 --timeout 120 --worker-class uvicorn.workers.UvicornWorker")
            return False
    except:
        pass
    
    print_warning("Could not automatically restart Django application")
    return False

def main():
    print("=" * 50)
    print("WebSocket Proxy Configuration Fix Script")
    print("=" * 50)
    print()
    
    # Check if running as root (skip on Windows)
    try:
        if os.geteuid() != 0:
            print_warning("Not running as root. Some operations may fail.")
            print_info("Consider running with: sudo python3 fix_websocket_proxy.py")
            response = input("Continue anyway? (y/n): ").strip().lower()
            if response != 'y':
                sys.exit(0)
    except AttributeError:
        # Windows doesn't have geteuid
        pass
    
    # Detect web server
    print_info("Detecting web server...")
    web_server = detect_web_server()
    
    if not web_server:
        print_warning("Could not automatically detect web server")
        print_info("Checking for nginx configuration files...")
        
        # Try to find nginx config directly
        if os.path.exists('/etc/nginx') or os.path.exists('/usr/local/nginx'):
            print_info("Found nginx directory, assuming nginx")
            web_server = 'nginx'
        elif os.path.exists('/etc/apache2') or os.path.exists('/etc/httpd'):
            print_info("Found apache directory, assuming apache")
            web_server = 'apache2'
        else:
            print_error("Could not detect web server")
            print_info("Please specify manually:")
            print("  1. nginx")
            print("  2. apache2")
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == '1':
                web_server = 'nginx'
            elif choice == '2':
                web_server = 'apache2'
            else:
                print_error("Invalid choice")
                sys.exit(1)
    
    print_success(f"Using web server: {web_server}")
    print()
    
    if web_server == 'nginx':
        # Find config file
        print_info("Searching for nginx configuration file...")
        config_file = find_nginx_config()
        
        if not config_file:
            print_warning("Could not automatically find nginx configuration file")
            print_info("Common locations:")
            print_info("  - /etc/nginx/sites-available/api.crm.click2print.store")
            print_info("  - /etc/nginx/conf.d/api.crm.click2print.store.conf")
            print_info("  - /etc/nginx/nginx.conf")
            print()
            config_file = input("Enter nginx config file path (or press Enter to skip): ").strip()
            if not config_file:
                print_warning("Skipping automatic configuration")
                print_info("Please configure manually. See WEBSOCKET_PROXY_CONFIG.md")
                sys.exit(0)
            if not os.path.exists(config_file):
                print_error(f"File not found: {config_file}")
                sys.exit(1)
        
        # Configure nginx
        if configure_nginx(config_file):
            print()
            print_info("Testing nginx configuration...")
            if test_nginx():
                print()
                print_info("Reloading nginx...")
                if reload_nginx():
                    print_success("Nginx configured and reloaded successfully")
                else:
                    print_error("Failed to reload nginx")
                    sys.exit(1)
            else:
                print_error("Nginx configuration test failed")
                print_info("Please check the configuration manually")
                sys.exit(1)
        else:
            print_error("Failed to configure nginx")
            sys.exit(1)
    else:
        print_warning(f"Apache configuration requires manual editing")
        print_info("Please see WEBSOCKET_PROXY_CONFIG.md for Apache configuration")
        sys.exit(1)
    
    print()
    print_info("Restarting Django application...")
    restart_django()
    
    print()
    print("=" * 50)
    print_success("Configuration complete!")
    print("=" * 50)
    print()
    print_info("Next steps:")
    print("  1. Test the agent connection again")
    print("  2. Check logs: pm2 logs app.crm.click2print.store")
    print("  3. Check nginx logs: tail -f /var/log/nginx/error.log")
    print()

if __name__ == '__main__':
    main()

