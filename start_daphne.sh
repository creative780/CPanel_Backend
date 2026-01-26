#!/bin/bash
# Start Django server with Daphne ASGI server
# This properly handles ASGI applications with Channels and prevents timeout issues

echo "========================================"
echo "Starting Django Server with Daphne (ASGI)"
echo "========================================"
echo ""
echo "IMPORTANT: This uses Daphne instead of runserver"
echo "Daphne properly handles ASGI applications and prevents timeout warnings"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found!"
    echo "Please run this script from the CRM_BACKEND directory"
    exit 1
fi

# Check if Redis is available (required for Channels)
echo "Checking Redis connection..."
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True); r.ping(); print('Redis is running!')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Redis is not running or not accessible!"
    echo ""
    echo "Please install and start Redis:"
    echo "  sudo apt-get install redis-server  # Ubuntu/Debian"
    echo "  brew install redis && brew services start redis  # macOS"
    echo ""
    read -p "Press Enter to continue anyway (WebSocket may not work)..."
fi

echo ""
echo "Starting Daphne server on http://0.0.0.0:8000"
echo "Application close timeout: 30 seconds"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Start Daphne with proper timeout configuration
# --application-close-timeout: Time to wait for application cleanup (prevents timeout warnings)
python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start Daphne server"
    echo ""
    echo "Make sure Daphne is installed:"
    echo "  pip install daphne"
    echo ""
    exit 1
fi





























