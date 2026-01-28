"""
WebSocket routing for monitoring application
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/monitoring/$', consumers.MonitoringConsumer.as_asgi()),
    re_path(r'ws/monitoring/device/(?P<device_id>[^/]+)/$', consumers.DeviceConsumer.as_asgi()),
    re_path(r'ws/monitoring/stream/viewer/(?P<device_id>[^/]+)/$', consumers.StreamViewerConsumer.as_asgi()),
    re_path(r'ws/monitoring/stream/agent/(?P<device_id>[^/]+)/$', consumers.AgentStreamConsumer.as_asgi()),
]

# Debug: Print routes when module is loaded
import sys
print(f"[MONITORING ROUTING] Loaded {len(websocket_urlpatterns)} routes", file=sys.stderr)
for i, route in enumerate(websocket_urlpatterns):
    print(f"[MONITORING ROUTING] Route {i}: {route.pattern}", file=sys.stderr)

