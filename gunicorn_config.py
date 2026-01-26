"""
Gunicorn configuration file for production deployment
"""
import multiprocessing
import os
from pathlib import Path

# Server socket
bind = "0.0.0.0:8003"
backlog = 2048

# Worker processes
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
# Get the base directory (parent of crm_backend)
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Access log - records all HTTP requests
accesslog = str(LOGS_DIR / 'gunicorn_access.log')
# Error log - records all errors and exceptions
errorlog = str(LOGS_DIR / 'gunicorn_error.log')
# Log level
loglevel = 'info'

# Process naming
proc_name = 'crm_backend_gunicorn'

# Server mechanics
daemon = False
pidfile = str(LOGS_DIR / 'gunicorn.pid')
umask = 0
user = None
group = None
tmp_redirect = False

# SSL (if needed in future)
# keyfile = None
# certfile = None

# Process management
max_requests = 1000
max_requests_jitter = 50
preload_app = False

# Logging format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down: Master")

def worker_int(worker):
    """Called when a worker receives INT or QUIT signal."""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker times out."""
    worker.log.info("Worker timeout (pid: %s)", worker.pid)

















