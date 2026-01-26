from __future__ import annotations

import os
import sys
import logging
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm_backend.settings")

app = Celery("crm_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Configure Windows-compatible pool
if sys.platform == 'win32':
    # Use solo pool on Windows (prefork doesn't work)
    app.conf.worker_pool = 'solo'
    # Alternative: use threads pool for better performance (requires: pip install eventlet)
    # app.conf.worker_pool = 'threads'
    # app.conf.worker_concurrency = 4

# Beat scheduler configuration
# Celery Beat will use the schedule defined in CELERY_BEAT_SCHEDULE in settings.py
app.conf.beat_schedule_filename = 'celerybeat-schedule'
app.conf.beat_schedule = None  # Will be loaded from settings.py

# Logging configuration for Beat
logger = logging.getLogger('celery.beat')
logger.setLevel(logging.INFO)

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Verify task discovery works
if __name__ == '__main__':
    logger.info('Celery app initialized successfully')
    logger.info(f'Discovered {len(app.tasks)} tasks')