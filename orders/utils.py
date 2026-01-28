"""
Utility functions for order-related operations.
"""
import os
import uuid
import logging
import requests
from io import BytesIO
from urllib.parse import urlparse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

# Maximum image size: 10MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024
# Request timeout: 30 seconds
REQUEST_TIMEOUT = 30
# Allowed image formats
ALLOWED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}


def copy_product_image_to_storage(image_url, order_id, product_name=None):
    """
    Download and copy a product image to permanent storage.
    
    This function downloads an image from the given URL and saves it to
    permanent storage in the product_images directory. The image is validated
    before saving to ensure it's a valid image file.
    
    Args:
        image_url: Original product image URL (can be absolute or relative)
        order_id: Order ID for organizing files
        product_name: Optional product name for file naming
    
    Returns:
        str: URL of copied image file, or None if copy failed
    """
    if not image_url:
        return None
    
    try:
        # Check if it's a relative URL from our own server (/media/...)
        # In this case, we can copy directly from the file system
        if image_url.startswith('/media/'):
            # Remove /media/ prefix to get the file path
            file_path = image_url[len('/media/'):]
            
            # Try to copy from existing storage
            if default_storage.exists(file_path):
                try:
                    # Read the file
                    with default_storage.open(file_path, 'rb') as source_file:
                        image_data = source_file.read()
                    
                    # Validate the image
                    image_format = _validate_image(image_data, None)
                    if not image_format:
                        logger.warning(f"Invalid image format for file: {file_path}")
                        return None
                    
                    # Generate unique filename
                    unique_filename = f"{uuid.uuid4().hex}{image_format}"
                    
                    # Build storage path: product_images/{order_id}/{filename}
                    storage_path = f'product_images/{order_id}/{unique_filename}'
                    
                    # Save to storage
                    saved_path = default_storage.save(storage_path, ContentFile(image_data))
                    
                    # Generate URL for the saved file
                    file_url = default_storage.url(saved_path)
                    
                    logger.info(f"Successfully copied product image from {file_path} to {saved_path} for order {order_id}")
                    return file_url
                    
                except Exception as e:
                    logger.warning(f"Failed to copy file from storage {file_path}: {e}")
                    # Fall through to try downloading
            else:
                logger.warning(f"File not found in storage: {file_path}")
                # Fall through to try downloading (in case it's an external /media/ URL)
        
        # For absolute URLs or relative URLs we can't copy directly,
        # download the image
        absolute_url = _build_absolute_url(image_url)
        image_data, content_type = _download_image(absolute_url)
        
        # Validate the image
        image_format = _validate_image(image_data, content_type)
        if not image_format:
            logger.warning(f"Invalid image format for URL: {image_url}")
            return None
        
        # Generate unique filename
        file_extension = image_format
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Build storage path: product_images/{order_id}/{filename}
        storage_path = f'product_images/{order_id}/{unique_filename}'
        
        # Save to storage
        saved_path = default_storage.save(storage_path, ContentFile(image_data))
        
        # Generate URL for the saved file
        file_url = default_storage.url(saved_path)
        
        logger.info(f"Successfully copied product image to {saved_path} for order {order_id}")
        return file_url
        
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to download product image from {image_url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Failed to copy product image to storage: {e}", exc_info=True)
        return None


def _build_absolute_url(url):
    """
    Build absolute URL from relative or absolute URL.
    
    Handles both relative URLs (e.g., /media/uploads/image.jpg) and
    absolute URLs (e.g., https://example.com/image.jpg).
    Returns the URL as-is - the download function will handle relative URLs
    by copying directly from file system if they're from our server.
    """
    if not url:
        return None
    
    # If it's already an absolute URL, return as-is
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return url
    
    # For relative URLs, return as-is
    # The copy function will handle /media/ URLs by copying from file system
    return url


def _download_image(url):
    """
    Download image from URL.
    
    Args:
        url: Image URL to download
        
    Returns:
        tuple: (image_data as bytes, content_type as str)
        
    Raises:
        requests.exceptions.RequestException: If download fails
    """
    # Handle relative URLs - try to make them absolute if possible
    # If it's a relative URL starting with /, we might need to prepend the server URL
    # For now, we'll try to download as-is and let requests handle it
    
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        stream=True,
        headers={'User-Agent': 'Mozilla/5.0 (compatible; CRM-ImageFetcher/1.0)'}
    )
    response.raise_for_status()
    
    # Check content type
    content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
    
    # Read image data with size limit
    image_data = BytesIO()
    bytes_read = 0
    
    for chunk in response.iter_content(chunk_size=64 * 1024):  # 64KB chunks
        if chunk:
            bytes_read += len(chunk)
            if bytes_read > MAX_IMAGE_SIZE:
                raise ValueError(f"Image size exceeds maximum allowed size ({MAX_IMAGE_SIZE} bytes)")
            image_data.write(chunk)
    
    image_data.seek(0)
    return image_data.getvalue(), content_type


def _validate_image(image_data, content_type):
    """
    Validate that the downloaded data is a valid image.
    
    Args:
        image_data: Image data as bytes
        content_type: MIME type from HTTP response
        
    Returns:
        str: File extension (e.g., '.jpg') if valid, None otherwise
    """
    try:
        # Try to open with PIL to validate it's an image
        image = PILImage.open(BytesIO(image_data))
        # Get format before verify (verify makes image unusable)
        image_format = image.format.lower() if image.format else None
        image.verify()  # Verify it's a valid image
        
        # Map PIL format to file extension
        format_map = {
            'jpeg': '.jpg',
            'jpg': '.jpg',
            'png': '.png',
            'gif': '.gif',
            'webp': '.webp',
        }
        
        extension = format_map.get(image_format)
        if extension:
            return extension
        
        # Fallback: check content type
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
        }
        
        extension = content_type_map.get(content_type)
        if extension:
            return extension
        
        logger.warning(f"Unknown image format: {image_format} or content type: {content_type}")
        return None
        
    except Exception as e:
        logger.warning(f"Failed to validate image: {e}")
        return None
