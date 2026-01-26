#!/bin/bash

# WebSocket Proxy Configuration Fix Script
# This script configures nginx/apache to properly forward WebSocket connections

set -e  # Exit on error

echo "=========================================="
echo "WebSocket Proxy Configuration Fix Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "ℹ $1"
}

# Detect which web server is being used
detect_web_server() {
    if command -v nginx &> /dev/null; then
        if systemctl is-active --quiet nginx 2>/dev/null || service nginx status &> /dev/null; then
            echo "nginx"
            return 0
        fi
    fi
    
    if command -v apache2 &> /dev/null; then
        if systemctl is-active --quiet apache2 2>/dev/null || service apache2 status &> /dev/null; then
            echo "apache2"
            return 0
        fi
    fi
    
    if command -v httpd &> /dev/null; then
        if systemctl is-active --quiet httpd 2>/dev/null || service httpd status &> /dev/null; then
            echo "httpd"
            return 0
        fi
    fi
    
    echo "unknown"
    return 1
}

# Find nginx configuration file for the domain
find_nginx_config() {
    local domain="api.crm.click2print.store"
    local possible_paths=(
        "/etc/nginx/sites-available/${domain}"
        "/etc/nginx/sites-available/api.crm.click2print.store"
        "/etc/nginx/conf.d/${domain}.conf"
        "/etc/nginx/nginx.conf"
        "/usr/local/nginx/conf/nginx.conf"
    )
    
    for path in "${possible_paths[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # Try to find any config file that mentions the domain
    local found=$(grep -r "$domain" /etc/nginx/ 2>/dev/null | head -1 | cut -d: -f1)
    if [ -n "$found" ] && [ -f "$found" ]; then
        echo "$found"
        return 0
    fi
    
    echo ""
    return 1
}

# Configure nginx for WebSocket
configure_nginx() {
    local config_file=$1
    local backup_file="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    
    print_info "Found nginx config: $config_file"
    
    # Create backup
    print_info "Creating backup: $backup_file"
    cp "$config_file" "$backup_file"
    print_success "Backup created"
    
    # Check if WebSocket configuration already exists
    if grep -q "location /ws/" "$config_file"; then
        print_warning "WebSocket configuration already exists in $config_file"
        read -p "Do you want to update it? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Skipping nginx configuration update"
            return 0
        fi
        # Remove existing /ws/ location block
        sed -i '/location \/ws\/ {/,/^[[:space:]]*}/d' "$config_file"
    fi
    
    # Find the server block and add WebSocket configuration
    # Look for the server block that contains the domain
    if grep -q "server_name.*api.crm.click2print.store" "$config_file"; then
        # Insert WebSocket config before the closing brace of the server block
        # Find a good insertion point (before the last closing brace in server block)
        local temp_file=$(mktemp)
        
        # Read the file and insert WebSocket config
        awk '
        /server_name.*api.crm.click2print.store/ { in_server=1 }
        in_server && /^[[:space:]]*}/ && !ws_added {
            print "    # WebSocket proxy configuration"
            print "    location /ws/ {"
            print "        proxy_pass http://127.0.0.1:9000;"
            print "        proxy_http_version 1.1;"
            print "        "
            print "        # WebSocket upgrade headers"
            print "        proxy_set_header Upgrade $http_upgrade;"
            print "        proxy_set_header Connection \"upgrade\";"
            print "        "
            print "        # Standard proxy headers"
            print "        proxy_set_header Host $host;"
            print "        proxy_set_header X-Real-IP $remote_addr;"
            print "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;"
            print "        proxy_set_header X-Forwarded-Proto $scheme;"
            print "        "
            print "        # WebSocket timeouts"
            print "        proxy_read_timeout 86400;"
            print "        proxy_send_timeout 86400;"
            print "        proxy_connect_timeout 60;"
            print "        "
            print "        # Disable buffering for WebSocket"
            print "        proxy_buffering off;"
            print "    }"
            print ""
            ws_added=1
        }
        { print }
        ' "$config_file" > "$temp_file"
        
        mv "$temp_file" "$config_file"
        print_success "WebSocket configuration added to nginx config"
    else
        print_warning "Could not find server block for api.crm.click2print.store"
        print_info "Please manually add the WebSocket configuration. See WEBSOCKET_PROXY_CONFIG.md"
        return 1
    fi
}

# Configure Apache for WebSocket
configure_apache() {
    local config_file=$1
    print_warning "Apache configuration requires manual editing"
    print_info "Please see WEBSOCKET_PROXY_CONFIG.md for Apache configuration"
    print_info "Config file location: $config_file"
    return 1
}

# Test nginx configuration
test_nginx() {
    if nginx -t 2>&1; then
        print_success "Nginx configuration test passed"
        return 0
    else
        print_error "Nginx configuration test failed"
        return 1
    fi
}

# Reload nginx
reload_nginx() {
    if systemctl reload nginx 2>/dev/null; then
        print_success "Nginx reloaded successfully"
        return 0
    elif service nginx reload 2>/dev/null; then
        print_success "Nginx reloaded successfully"
        return 0
    else
        print_error "Failed to reload nginx"
        return 1
    fi
}

# Restart Django application
restart_django() {
    print_info "Restarting Django application..."
    
    if command -v pm2 &> /dev/null; then
        if pm2 list | grep -q "app.crm.click2print.store"; then
            pm2 restart app.crm.click2print.store
            print_success "Django application restarted via PM2"
            return 0
        fi
    fi
    
    # Try to find and restart gunicorn
    if pgrep -f "gunicorn.*asgi" > /dev/null; then
        print_info "Found gunicorn process, restarting..."
        pkill -f "gunicorn.*asgi"
        sleep 2
        print_warning "Gunicorn stopped. Please restart it manually:"
        print_info "cd /home/api.crm.click2print.store/public_html"
        print_info "source venv/bin/activate"
        print_info "gunicorn crm_backend.asgi:application --bind 0.0.0.0:9000 --workers 4 --timeout 120 --worker-class uvicorn.workers.UvicornWorker"
        return 1
    fi
    
    print_warning "Could not automatically restart Django application"
    print_info "Please restart it manually"
    return 1
}

# Main execution
main() {
    print_info "Detecting web server..."
    WEB_SERVER=$(detect_web_server)
    
    if [ "$WEB_SERVER" = "unknown" ]; then
        print_error "Could not detect web server (nginx/apache)"
        print_info "Please configure WebSocket manually. See WEBSOCKET_PROXY_CONFIG.md"
        exit 1
    fi
    
    print_success "Detected web server: $WEB_SERVER"
    echo ""
    
    if [ "$WEB_SERVER" = "nginx" ]; then
        print_info "Configuring nginx for WebSocket..."
        CONFIG_FILE=$(find_nginx_config)
        
        if [ -z "$CONFIG_FILE" ]; then
            print_error "Could not find nginx configuration file"
            print_info "Please specify the path manually or configure it manually"
            exit 1
        fi
        
        if configure_nginx "$CONFIG_FILE"; then
            echo ""
            print_info "Testing nginx configuration..."
            if test_nginx; then
                echo ""
                print_info "Reloading nginx..."
                if reload_nginx; then
                    print_success "Nginx configured and reloaded successfully"
                else
                    print_error "Failed to reload nginx"
                    exit 1
                fi
            else
                print_error "Nginx configuration test failed"
                print_info "Restoring backup..."
                mv "${CONFIG_FILE}.backup."* "$CONFIG_FILE" 2>/dev/null || true
                exit 1
            fi
        else
            print_error "Failed to configure nginx"
            exit 1
        fi
    elif [ "$WEB_SERVER" = "apache2" ] || [ "$WEB_SERVER" = "httpd" ]; then
        configure_apache ""
        exit 1
    fi
    
    echo ""
    print_info "Restarting Django application..."
    restart_django
    
    echo ""
    echo "=========================================="
    print_success "Configuration complete!"
    echo "=========================================="
    echo ""
    print_info "Next steps:"
    echo "1. Test the agent connection again"
    echo "2. Check logs: pm2 logs app.crm.click2print.store"
    echo "3. Check nginx logs: tail -f /var/log/nginx/error.log"
    echo ""
    print_info "If issues persist, check WEBSOCKET_PROXY_CONFIG.md for manual configuration"
}

# Run main function
main

































