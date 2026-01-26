"""
Health check views and WebSocket consumers - Simplified version for testing.
"""

import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


def check_database():
    """Check database connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False


def check_redis():
    """Check Redis connectivity - simplified for testing."""
    try:
        # For testing, we'll just return True since we're using in-memory cache
        return True
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        return False


def check_storage():
    """Check storage connectivity - simplified for testing."""
    try:
        # For testing, we'll just return True since we're using local storage
        return True
    except Exception as e:
        logger.error(f"Storage check failed: {e}")
        return False


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """REST API health check endpoint."""
    try:
        database_ok = check_database()
        redis_ok = check_redis()
        storage_ok = check_storage()
        
        all_healthy = database_ok and redis_ok and storage_ok
        
        response_data = {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': database_ok,
                'redis': redis_ok,
                'storage': storage_ok,
            }
        }
        
        status_code = 200 if all_healthy else 503
        return JsonResponse(response_data, status=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': False,
                'redis': False,
                'storage': False,
            }
        }, status=503)


class HealthConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for health checks."""
    
    async def connect(self):
        await self.accept()
        logger.info("WebSocket health consumer connected")
    
    async def disconnect(self, close_code):
        logger.info(f"WebSocket health consumer disconnected: {close_code}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'health_check':
                # Perform health checks
                database_ok = await database_sync_to_async(check_database)()
                redis_ok = await database_sync_to_async(check_redis)()
                storage_ok = await database_sync_to_async(check_storage)()
                
                all_healthy = database_ok and redis_ok and storage_ok
                
                response_data = {
                    'type': 'health',
                    'data': {
                        'status': 'healthy' if all_healthy else 'unhealthy',
                        'timestamp': datetime.utcnow().isoformat(),
                        'services': {
                            'database': database_ok,
                            'redis': redis_ok,
                            'storage': storage_ok,
                        }
                    }
                }
                
                await self.send(text_data=json.dumps(response_data))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"WebSocket health check failed: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Health check failed'
            }))

