"""
WebSocket URL patterns for health app.
"""

from django.urls import path
from . import views

websocket_urlpatterns = [
    path('ws/health/', views.HealthConsumer.as_asgi()),
]

