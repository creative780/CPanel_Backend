"""
Custom middleware for database connection cleanup.
This ensures database connections are properly closed after each request,
which is critical when running under ASGI with Channels.
"""
import logging
from django.db import connections

logger = logging.getLogger(__name__)


class DatabaseConnectionCleanupMiddleware:
    """
    Middleware to ensure database connections are closed after each request.
    This prevents "Application instance took too long to shut down" warnings
    when using Django Channels with synchronous views.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        finally:
            # Close all database connections after request processing
            # This is especially important when running under ASGI
            for conn in connections.all():
                if conn.connection is not None:
                    try:
                        conn.close()
                    except Exception as e:
                        logger.debug(f"Error closing database connection: {e}")

