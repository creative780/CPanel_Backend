#!/bin/bash
# Production startup script for Django/Daphne server
# This script is designed for production use with proper error handling and logging

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Change to backend directory
cd "$BACKEND_DIR"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found in $BACKEND_DIR" >&2
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo "WARNING: .env file not found. Using system environment variables." >&2
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "WARNING: Virtual environment not found. Using system Python." >&2
fi

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Verify environment
echo "Verifying production settings..."
python manage.py check --deploy || {
    echo "ERROR: Production settings check failed!" >&2
    exit 1
}

# Start Daphne server
echo "Starting Daphne ASGI server on 127.0.0.1:8000..."
echo "Server is ready to receive requests."

exec python -m daphne \
    -p 8000 \
    -b 127.0.0.1 \
    --application-close-timeout 30 \
    crm_backend.asgi:application

