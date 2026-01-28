"""
ASGI config for crm_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings')

# Initialize Django ASGI application early to ensure Django setup is done
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
import monitoring.routing
import notifications.routing
import logging

logger = logging.getLogger(__name__)

# Log WebSocket routes for debugging
all_websocket_routes = (
    chat.routing.websocket_urlpatterns +
    monitoring.routing.websocket_urlpatterns +
    notifications.routing.websocket_urlpatterns
)

# Log monitoring routes specifically (using stderr for immediate visibility)
import sys
sys.stderr.write("=" * 50 + "\n")
sys.stderr.write("Loading WebSocket routes...\n")
for pattern in monitoring.routing.websocket_urlpatterns:
    sys.stderr.write(f"Monitoring route: {pattern.pattern}\n")
sys.stderr.write("=" * 50 + "\n")
sys.stderr.flush()


# Wrap Django ASGI app to ensure proper database connection cleanup
# This prevents "Application instance took too long to shut down" warnings
class DatabaseCleanupMiddleware:
    """
    Middleware to ensure database connections are properly closed after each request.
    This is critical when running synchronous views under ASGI with Channels.
    """
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            # Create a wrapper for send that ensures cleanup after response
            response_sent = False
            
            async def send_wrapper(message):
                nonlocal response_sent
                await send(message)
                # Mark response as sent when we get the first response message
                if message.get('type') == 'http.response.start':
                    response_sent = True
                # Clean up database connections after response body is sent
                if message.get('type') == 'http.response.body' and response_sent:
                    # Close database connections after response is complete
                    from django.db import connections
                    for conn in connections.all():
                        if conn.connection is not None:
                            try:
                                conn.close()
                            except Exception:
                                pass  # Ignore errors during cleanup
            
            try:
                # Call the Django ASGI app with wrapped send
                await self.app(scope, receive, send_wrapper)
            finally:
                # Final cleanup - ensure all connections are closed
                from django.db import connections
                for conn in connections.all():
                    if conn.connection is not None:
                        try:
                            conn.close()
                        except Exception:
                            pass  # Ignore errors during cleanup
        else:
            # For non-HTTP requests (like websockets), just pass through
            await self.app(scope, receive, send)


# Wrap the Django ASGI app with database cleanup middleware
django_asgi_app = DatabaseCleanupMiddleware(django_asgi_app)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(all_websocket_routes)
    ),
})