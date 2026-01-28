"""
Unit tests for product image copying utility function.

Tests the copy_product_image_to_storage() function to ensure images are
properly copied to permanent storage.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from PIL import Image as PILImage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import requests

from orders.utils import copy_product_image_to_storage


@pytest.mark.django_db
@pytest.mark.unit
class TestImageCopyingUtility:
    """Test copy_product_image_to_storage utility function."""
    
    def test_copy_from_absolute_url_success(self):
        """Test successful image copy from absolute URL."""
        # Create a test image
        img = PILImage.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        image_data = img_bytes.getvalue()
        
        # Mock requests.get to return the image
        mock_response = Mock()
        mock_response.content = image_data
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [image_data]
        
        order_id = 123
        image_url = 'https://example.com/product.jpg'
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            with patch('orders.utils.default_storage.save') as mock_save:
                mock_save.return_value = f'product_images/{order_id}/test.jpg'
                with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order_id}/test.jpg'):
                    result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify result
        assert result is not None
        assert 'product_images' in result
        
        # Verify save was called with correct path
        mock_save.assert_called_once()
        saved_path = mock_save.call_args[0][0]
        assert saved_path.startswith(f'product_images/{order_id}/')
    
    def test_copy_from_relative_url_success(self):
        """Test successful image copy from relative URL (/media/...)."""
        # Create a test image
        img = PILImage.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        image_data = img_bytes.getvalue()
        
        order_id = 456
        image_url = '/media/uploads/test_product.png'
        file_path = 'uploads/test_product.png'
        
        # Mock storage to return existing file
        with patch('orders.utils.default_storage.exists', return_value=True):
            with patch('orders.utils.default_storage.open') as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = image_data
                mock_file.__enter__ = Mock(return_value=mock_file)
                mock_file.__exit__ = Mock(return_value=None)
                mock_open.return_value = mock_file
                
                with patch('orders.utils.default_storage.save') as mock_save:
                    mock_save.return_value = f'product_images/{order_id}/test.png'
                    with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order_id}/test.png'):
                        result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify result
        assert result is not None
        assert 'product_images' in result
        
        # Verify file was read from storage
        mock_open.assert_called_once_with(file_path, 'rb')
        
        # Verify save was called
        mock_save.assert_called_once()
    
    def test_copy_with_valid_image_formats(self):
        """Test copying with various valid image formats."""
        formats = ['JPEG', 'PNG', 'GIF', 'WEBP']
        order_id = 789
        
        for img_format in formats:
            # Create test image
            if img_format == 'GIF':
                img = PILImage.new('P', (100, 100), color=0)
            else:
                img = PILImage.new('RGB', (100, 100), color='green')
            img_bytes = BytesIO()
            img.save(img_bytes, format=img_format)
            img_bytes.seek(0)
            image_data = img_bytes.getvalue()
            
            # Mock requests
            mock_response = Mock()
            mock_response.content = image_data
            mock_response.headers = {'Content-Type': f'image/{img_format.lower()}'}
            mock_response.raise_for_status = Mock()
            mock_response.iter_content.return_value = [image_data]
            
            image_url = f'https://example.com/product.{img_format.lower()}'
            
            with patch('orders.utils.requests.get', return_value=mock_response):
                with patch('orders.utils.default_storage.save') as mock_save:
                    mock_save.return_value = f'product_images/{order_id}/test.{img_format.lower()}'
                    with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order_id}/test.{img_format.lower()}'):
                        result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
            
            # Verify result
            assert result is not None
    
    def test_copy_with_invalid_image_data(self):
        """Test copying with invalid image data returns None."""
        order_id = 999
        image_url = 'https://example.com/not_an_image.txt'
        
        # Mock requests to return non-image data
        mock_response = Mock()
        mock_response.content = b'This is not an image'
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [b'This is not an image']
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify result is None (invalid image)
        assert result is None
    
    def test_copy_with_network_failure(self):
        """Test handling of network failures."""
        order_id = 111
        image_url = 'https://example.com/product.jpg'
        
        # Mock requests.get to raise exception
        with patch('orders.utils.requests.get', side_effect=requests.exceptions.RequestException('Network error')):
            result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify result is None (graceful degradation)
        assert result is None
    
    def test_copy_with_404_error(self):
        """Test handling of 404 errors."""
        order_id = 222
        image_url = 'https://example.com/missing.jpg'
        
        # Mock requests.get to raise HTTPError (404)
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError('404 Not Found')
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify result is None (graceful degradation)
        assert result is None
    
    def test_copy_with_empty_url(self):
        """Test handling of empty URL."""
        order_id = 333
        image_url = None
        
        result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify result is None
        assert result is None
        
        # Test with empty string
        result = copy_product_image_to_storage('', order_id, 'Test Product')
        assert result is None
    
    def test_storage_path_generation(self):
        """Test that storage path follows correct pattern."""
        # Create a test image
        img = PILImage.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        image_data = img_bytes.getvalue()
        
        order_id = 444
        image_url = 'https://example.com/product.jpg'
        
        # Mock requests
        mock_response = Mock()
        mock_response.content = image_data
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [image_data]
        
        saved_paths = []
        
        def capture_save(path, content_file):
            saved_paths.append(path)
            return path
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            with patch('orders.utils.default_storage.save', side_effect=capture_save):
                with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order_id}/test.jpg'):
                    result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify path pattern
        assert len(saved_paths) > 0
        saved_path = saved_paths[0]
        assert saved_path.startswith(f'product_images/{order_id}/')
        assert saved_path.endswith('.jpg')
        
        # Verify unique filename (should have UUID-like hex)
        filename = saved_path.split('/')[-1]
        assert len(filename) > 10  # UUID hex (32 chars) + extension
    
    def test_storage_path_uniqueness(self):
        """Test that storage paths are unique."""
        # Create a test image
        img = PILImage.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        image_data = img_bytes.getvalue()
        
        order_id = 555
        image_url = 'https://example.com/product.jpg'
        
        # Mock requests
        mock_response = Mock()
        mock_response.content = image_data
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [image_data]
        
        saved_paths = []
        
        def capture_save(path, content_file):
            saved_paths.append(path)
            return path
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            with patch('orders.utils.default_storage.save', side_effect=capture_save):
                with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order_id}/test.jpg'):
                    # Call twice to verify unique paths
                    copy_product_image_to_storage(image_url, order_id, 'Product 1')
                    copy_product_image_to_storage(image_url, order_id, 'Product 2')
        
        # Verify paths are unique
        assert len(saved_paths) == 2
        assert saved_paths[0] != saved_paths[1]
    
    def test_copy_with_timeout(self):
        """Test handling of timeout errors."""
        order_id = 666
        image_url = 'https://example.com/slow.jpg'
        
        # Mock requests.get to raise Timeout
        with patch('orders.utils.requests.get', side_effect=requests.exceptions.Timeout('Request timeout')):
            result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify result is None (graceful degradation)
        assert result is None
    
    def test_copy_from_nonexistent_relative_url(self):
        """Test copying from non-existent relative URL falls back to download."""
        # Create a test image
        img = PILImage.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        image_data = img_bytes.getvalue()
        
        order_id = 777
        image_url = '/media/nonexistent.jpg'
        
        # Mock storage.exists to return False (file doesn't exist)
        mock_response = Mock()
        mock_response.content = image_data
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [image_data]
        
        with patch('orders.utils.default_storage.exists', return_value=False):
            with patch('orders.utils.requests.get', return_value=mock_response):
                with patch('orders.utils.default_storage.save') as mock_save:
                    mock_save.return_value = f'product_images/{order_id}/test.jpg'
                    with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order_id}/test.jpg'):
                        result = copy_product_image_to_storage(image_url, order_id, 'Test Product')
        
        # Verify it falls back to HTTP download
        assert result is not None
        assert 'product_images' in result
