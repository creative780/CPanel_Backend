"""
Management command to test WebSocket connection for debugging
"""
import asyncio
import websockets
import sys
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Test WebSocket connection to verify proxy configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='wss://api.crm.click2print.store/ws/monitoring/stream/agent/test_device/?token=test_token',
            help='WebSocket URL to test'
        )

    def handle(self, *args, **options):
        url = options['url']
        self.stdout.write(f'Testing WebSocket connection to: {url}')
        
        async def test_connection():
            try:
                async with websockets.connect(url) as websocket:
                    self.stdout.write(self.style.SUCCESS('✓ WebSocket connection successful!'))
                    # Send a test message
                    await websocket.send('{"type": "ping", "timestamp": 1234567890}')
                    response = await websocket.recv()
                    self.stdout.write(f'Response: {response}')
            except websockets.exceptions.InvalidStatusCode as e:
                self.stdout.write(self.style.ERROR(f'✗ Invalid status code: {e.status_code}'))
                self.stdout.write(self.style.WARNING('This usually means the proxy is not configured for WebSocket'))
            except websockets.exceptions.InvalidHandshake as e:
                self.stdout.write(self.style.ERROR(f'✗ Invalid handshake: {e}'))
                self.stdout.write(self.style.WARNING('This usually means "Invalid WebSocket Header"'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Connection failed: {e}'))
        
        asyncio.run(test_connection())

































