#!/bin/bash
# Production startup script for Celery worker
# This script starts the Celery worker process for background task processing

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

# Check Redis connection (required for Celery)
echo "Checking Redis connection..."
python -c "
import os
import sys
import redis
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')
import django
django.setup()

try:
    r = redis.from_url(settings.CELERY_BROKER_URL)
    r.ping()
    print('Redis connection successful!')
except Exception as e:
    print(f'ERROR: Redis connection failed: {e}', file=sys.stderr)
    sys.exit(1)
" || {
    echo "ERROR: Cannot connect to Redis. Please ensure Redis is running." >&2
    exit 1
}

# Start Celery worker
echo "Starting Celery worker..."
echo "Worker is ready to process tasks."

exec celery -A crm_backend worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --time-limit=300 \
    --soft-time-limit=240

