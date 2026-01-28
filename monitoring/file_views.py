from django.http import HttpResponse, Http404
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts.permissions import RolePermission, user_has_any_role
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from monitoring.storage import storage
import os
import logging
import asyncio

logger = logging.getLogger(__name__)


class MonitoringFileView(APIView):
    """Serve monitoring files (screenshots, thumbnails, recordings, video files)"""
    # Remove authentication - files are already protected by admin-only API endpoints
    permission_classes = []
    
    @method_decorator(cache_control(max_age=3600))  # Cache for 1 hour
    def get(self, request, file_path):
        """Serve file from monitoring storage"""
        try:
            # Security: prevent directory traversal
            if '..' in file_path or file_path.startswith('/'):
                raise Http404("File not found")
            
            # Try to get file from storage interface first
            try:
                # For S3 storage, get signed URL and redirect
                if hasattr(storage, 's3_client'):
                    signed_url = asyncio.run(storage.get_signed_url(file_path, 3600))
                    return HttpResponse(status=302, headers={'Location': signed_url})
            except (AttributeError, FileNotFoundError):
                # Not S3 or file not found, try local storage
                pass
            
            # For local storage, check storage's base_path first, then fallback locations
            storage_paths = []
            
            # Add storage's base_path if it's LocalStorage
            if hasattr(storage, 'base_path'):
                storage_paths.append(storage.base_path)
            
            # Add fallback paths
            storage_paths.extend([
                getattr(settings, 'MONITORING_STORAGE_PATH', '/var/app/data'),
                os.path.join(settings.BASE_DIR, 'monitoring_data'),
                os.path.join(settings.BASE_DIR, 'media', 'uploads'),
                os.path.join(settings.BASE_DIR, 'media')
            ])
            
            logger.info(f"Looking for file: {file_path}")
            
            full_path = None
            for storage_path in storage_paths:
                # Try original path
                test_path = os.path.join(storage_path, file_path)
                if os.path.exists(test_path):
                    full_path = test_path
                    logger.info(f"Found file at: {full_path}")
                    break
                
                # Handle "None/" prefix in file paths
                if file_path.startswith('None/'):
                    corrected_path = file_path.replace('None/', 'default/', 1)
                    test_path = os.path.join(storage_path, corrected_path)
                    if os.path.exists(test_path):
                        full_path = test_path
                        break
            
            if not full_path or not os.path.exists(full_path):
                # If thumbnail is missing, try to serve the full-size image
                if file_path.endswith('-thumb.jpg'):
                    full_size_path = file_path.replace('-thumb.jpg', '.jpg')
                    for storage_path in storage_paths:
                        test_path = os.path.join(storage_path, full_size_path)
                        if os.path.exists(test_path):
                            full_path = test_path
                            break
                
                # If still not found, return placeholder (only for images)
                if not full_path or not os.path.exists(full_path):
                    if file_path.endswith(('.jpg', '.jpeg', '.png', '-thumb.jpg')):
                        placeholder_svg = b'''<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">
                            <rect width="200" height="150" fill="#f0f0f0"/>
                            <text x="100" y="75" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">
                                File Not Available
                            </text>
                        </svg>'''
                        response = HttpResponse(placeholder_svg, content_type='image/svg+xml')
                        response['Content-Length'] = len(placeholder_svg)
                        return response
                    else:
                        # For video files, return 404
                        raise Http404("File not found")
            
            # Determine content type
            if file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.mp4'):
                content_type = 'video/mp4'
            elif file_path.endswith('.webm'):
                content_type = 'video/webm'
            elif file_path.endswith('.mov'):
                content_type = 'video/quicktime'
            else:
                content_type = 'application/octet-stream'
            
            # For video files, use streaming response to support range requests
            if file_path.endswith(('.mp4', '.webm', '.mov')):
                from django.http import StreamingHttpResponse, FileResponse
                import mimetypes
                
                # Use FileResponse for efficient streaming
                response = FileResponse(
                    open(full_path, 'rb'),
                    content_type=content_type
                )
                response['Content-Length'] = os.path.getsize(full_path)
                # Enable range requests for video seeking
                response['Accept-Ranges'] = 'bytes'
                # CORS headers for video playback
                response['Access-Control-Allow-Origin'] = '*'
                response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Range'
                return response
            else:
                # Read and serve file for images
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                response = HttpResponse(content, content_type=content_type)
                response['Content-Length'] = len(content)
                return response
            
        except Exception as e:
            logger.error(f"Error serving monitoring file {file_path}: {e}", exc_info=True)
            raise Http404("File not found")
