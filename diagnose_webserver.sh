#!/bin/bash
# Diagnose which web server is running and where config files are

echo "=========================================="
echo "Web Server Diagnostic"
echo "=========================================="
echo ""

echo "1. Checking what's listening on ports 80 and 443..."
echo ""
netstat -tlnp 2>/dev/null | grep -E ':(80|443)' || ss -tlnp 2>/dev/null | grep -E ':(80|443)' || echo "Could not check ports"
echo ""

echo "2. Checking for nginx..."
if command -v nginx &> /dev/null; then
    echo "  ✓ nginx found: $(which nginx)"
    nginx -v 2>&1
elif [ -f /usr/sbin/nginx ]; then
    echo "  ✓ nginx found: /usr/sbin/nginx"
    /usr/sbin/nginx -v 2>&1
elif [ -d /etc/nginx ]; then
    echo "  ✓ nginx config directory exists: /etc/nginx"
    echo "  Config files:"
    find /etc/nginx -name "*.conf" -type f 2>/dev/null | head -10
else
    echo "  ✗ nginx not found"
fi
echo ""

echo "3. Checking for Apache..."
if command -v apache2 &> /dev/null; then
    echo "  ✓ apache2 found: $(which apache2)"
    apache2 -v 2>&1 | head -1
elif command -v httpd &> /dev/null; then
    echo "  ✓ httpd found: $(which httpd)"
    httpd -v 2>&1 | head -1
elif [ -d /etc/apache2 ]; then
    echo "  ✓ Apache config directory exists: /etc/apache2"
elif [ -d /etc/httpd ]; then
    echo "  ✓ Apache config directory exists: /etc/httpd"
else
    echo "  ✗ Apache not found"
fi
echo ""

echo "4. Checking for control panels..."
if [ -d /usr/local/cpanel ]; then
    echo "  ✓ cPanel detected"
elif [ -d /usr/local/directadmin ]; then
    echo "  ✓ DirectAdmin detected"
elif [ -d /usr/local/vesta ]; then
    echo "  ✓ VestaCP detected"
fi
echo ""

echo "5. Checking running web server processes..."
ps aux | grep -E '(nginx|apache|httpd)' | grep -v grep | head -5
echo ""

echo "6. Checking for reverse proxy setup..."
if [ -f /etc/nginx/nginx.conf ]; then
    echo "  Checking /etc/nginx/nginx.conf for proxy settings..."
    grep -i "proxy_pass\|proxy_set_header" /etc/nginx/nginx.conf 2>/dev/null | head -5
fi
echo ""

echo "=========================================="
echo "Summary:"
echo "=========================================="
echo "Please share the output above to determine the correct configuration method."

































