"""
Integration tests for product image copying in order creation and updates.

Tests that product images are properly copied to permanent storage when orders
are created or updated via the API.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from PIL import Image as PILImage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework import status

from orders.models import Order, OrderItem
from tests.factories import OrderFactory


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderCreationWithImages:
    """Test order creation with product images."""
    
    def test_create_order_with_image_absolute_url(self, admin_client):
        """Test order creation with product image (absolute URL)."""
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
        
        image_url = 'https://example.com/product.jpg'
        
        # Mock storage save and url
        saved_paths = []
        
        def capture_save(path, content_file):
            saved_paths.append(path)
            return path
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            with patch('orders.utils.default_storage.save', side_effect=capture_save):
                with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/1/test.jpg'):
                    # Create order via API
                    response = admin_client.post(
                        '/api/orders/',
                        {
                            'clientName': 'Test Client',
                            'companyName': 'Test Co',
                            'phone': '+971501234567',
                            'email': 'test@example.com',
                            'address': 'Test Address',
                            'specs': 'Test specifications',
                            'urgency': 'Normal',
                            'items': [
                                {
                                    'name': 'Test Product',
                                    'sku': 'TEST-001',
                                    'quantity': 10,
                                    'unit_price': '5.00',
                                    'attributes': {'color': 'red'},
                                    'image_url': image_url
                                }
                            ]
                        },
                        format='json'
                    )
        
        # Verify order creation succeeded
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        order_data = response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        assert order_id is not None
        
        # Verify order item was created
        order = Order.objects.get(id=order_id)
        items = order.items.all()
        assert len(items) == 1
        
        item = items[0]
        assert item.name == 'Test Product'
        
        # Verify image was copied (saved path should contain product_images)
        assert len(saved_paths) > 0
        saved_path = saved_paths[0]
        assert saved_path.startswith(f'product_images/{order_id}/')
        
        # Verify image_url points to copied location
        assert item.image_url is not None
        assert 'product_images' in item.image_url
    
    def test_create_order_with_image_relative_url(self, admin_client):
        """Test order creation with product image (relative URL)."""
        # Create a test image
        img = PILImage.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        image_data = img_bytes.getvalue()
        
        # Save image to media storage first
        test_media_path = 'uploads/test_product.png'
        default_storage.save(test_media_path, ContentFile(image_data))
        
        image_url = f'/media/{test_media_path}'
        
        # Mock storage operations for copying
        saved_paths = []
        
        def capture_save(path, content_file):
            saved_paths.append(path)
            return path
        
        with patch('orders.utils.default_storage.exists', return_value=True):
            with patch('orders.utils.default_storage.open') as mock_open:
                mock_file = Mock()
                mock_file.read.return_value = image_data
                mock_file.__enter__ = Mock(return_value=mock_file)
                mock_file.__exit__ = Mock(return_value=None)
                mock_open.return_value = mock_file
                
                with patch('orders.utils.default_storage.save', side_effect=capture_save):
                    with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/1/test.png'):
                        # Create order via API
                        response = admin_client.post(
                            '/api/orders/',
                            {
                                'clientName': 'Test Client',
                                'companyName': 'Test Co',
                                'phone': '+971501234567',
                                'email': 'test@example.com',
                                'address': 'Test Address',
                                'specs': 'Test specifications',
                                'urgency': 'Normal',
                                'items': [
                                    {
                                        'name': 'Test Product',
                                        'sku': 'TEST-002',
                                        'quantity': 5,
                                        'unit_price': '10.00',
                                        'attributes': {'color': 'blue'},
                                        'image_url': image_url
                                    }
                                ]
                            },
                            format='json'
                        )
        
        # Verify order creation succeeded
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        order_data = response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        assert order_id is not None
        
        # Verify image was copied
        assert len(saved_paths) > 0
        saved_path = saved_paths[0]
        assert saved_path.startswith(f'product_images/{order_id}/')
    
    def test_create_order_with_multiple_items_some_with_images(self, admin_client):
        """Test order creation with multiple items (some with images)."""
        # Create test images
        img1 = PILImage.new('RGB', (100, 100), color='red')
        img_bytes1 = BytesIO()
        img1.save(img_bytes1, format='JPEG')
        img_bytes1.seek(0)
        image_data1 = img_bytes1.getvalue()
        
        # Mock requests
        mock_response = Mock()
        mock_response.content = image_data1
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [image_data1]
        
        image_url = 'https://example.com/product1.jpg'
        
        saved_paths = []
        
        def capture_save(path, content_file):
            saved_paths.append(path)
            return path
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            with patch('orders.utils.default_storage.save', side_effect=capture_save):
                with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/1/test.jpg'):
                    # Create order via API with 2 items, one with image
                    response = admin_client.post(
                        '/api/orders/',
                        {
                            'clientName': 'Test Client',
                            'companyName': 'Test Co',
                            'phone': '+971501234567',
                            'email': 'test@example.com',
                            'address': 'Test Address',
                            'specs': 'Test specifications',
                            'urgency': 'Normal',
                            'items': [
                                {
                                    'name': 'Product With Image',
                                    'sku': 'TEST-003',
                                    'quantity': 10,
                                    'unit_price': '5.00',
                                    'attributes': {},
                                    'image_url': image_url
                                },
                                {
                                    'name': 'Product Without Image',
                                    'sku': 'TEST-004',
                                    'quantity': 5,
                                    'unit_price': '10.00',
                                    'attributes': {}
                                }
                            ]
                        },
                        format='json'
                    )
        
        # Verify order creation succeeded
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        order_data = response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        assert order_id is not None
        
        # Verify order items
        order = Order.objects.get(id=order_id)
        items = order.items.all()
        assert len(items) == 2
        
        # Verify only one image was copied
        assert len(saved_paths) == 1
        
        # Verify items have correct image_url values
        item_with_image = items.get(name='Product With Image')
        item_without_image = items.get(name='Product Without Image')
        
        assert item_with_image.image_url is not None
        assert item_without_image.image_url is None
    
    def test_create_order_when_image_copy_fails(self, admin_client):
        """Test order creation when image copy fails (graceful degradation)."""
        original_image_url = 'https://example.com/broken.jpg'
        
        # Mock copy function to fail
        with patch('orders.utils.copy_product_image_to_storage', side_effect=Exception('Copy failed')):
            # Create order via API
            response = admin_client.post(
                '/api/orders/',
                {
                    'clientName': 'Test Client',
                    'companyName': 'Test Co',
                    'phone': '+971501234567',
                    'email': 'test@example.com',
                    'address': 'Test Address',
                    'specs': 'Test specifications',
                    'urgency': 'Normal',
                    'items': [
                        {
                            'name': 'Test Product',
                            'sku': 'TEST-005',
                            'quantity': 10,
                            'unit_price': '5.00',
                            'attributes': {},
                            'image_url': original_image_url
                        }
                    ]
                },
                format='json'
            )
        
        # Verify order creation still succeeded (graceful degradation)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        order_data = response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        assert order_id is not None
        
        # Verify order item was created
        order = Order.objects.get(id=order_id)
        items = order.items.all()
        assert len(items) == 1
        
        item = items[0]
        # Verify original URL is kept (fallback)
        assert item.image_url == original_image_url
    
    def test_create_order_with_invalid_image_url(self, admin_client):
        """Test order creation with invalid image URL."""
        invalid_image_url = 'https://example.com/not_an_image.txt'
        
        # Mock requests to return non-image data
        mock_response = Mock()
        mock_response.content = b'This is not an image'
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [b'This is not an image']
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            # Create order via API
            response = admin_client.post(
                '/api/orders/',
                {
                    'clientName': 'Test Client',
                    'companyName': 'Test Co',
                    'phone': '+971501234567',
                    'email': 'test@example.com',
                    'address': 'Test Address',
                    'specs': 'Test specifications',
                    'urgency': 'Normal',
                    'items': [
                        {
                            'name': 'Test Product',
                            'sku': 'TEST-006',
                            'quantity': 10,
                            'unit_price': '5.00',
                            'attributes': {},
                            'image_url': invalid_image_url
                        }
                    ]
                },
                format='json'
            )
        
        # Verify order creation still succeeded
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        order_data = response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        
        assert order_id is not None
        
        # Verify order item was created
        order = Order.objects.get(id=order_id)
        items = order.items.all()
        assert len(items) == 1
        
        item = items[0]
        # Verify original URL is kept (fallback)
        assert item.image_url == invalid_image_url


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderUpdateWithImages:
    """Test order updates with product images."""
    
    def test_update_order_with_new_images(self, admin_client):
        """Test order update with new product images."""
        # Create order without images
        order = OrderFactory()
        OrderItem.objects.create(
            order=order,
            name='Original Product',
            sku='ORIG-001',
            quantity=10,
            unit_price=5.00
        )
        
        # Create test image
        img = PILImage.new('RGB', (100, 100), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        image_data = img_bytes.getvalue()
        
        # Mock requests
        mock_response = Mock()
        mock_response.content = image_data
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.raise_for_status = Mock()
        mock_response.iter_content.return_value = [image_data]
        
        image_url = 'https://example.com/new_product.jpg'
        
        saved_paths = []
        
        def capture_save(path, content_file):
            saved_paths.append(path)
            return path
        
        with patch('orders.utils.requests.get', return_value=mock_response):
            with patch('orders.utils.default_storage.save', side_effect=capture_save):
                with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order.id}/new.jpg'):
                    # Update order via API with image
                    response = admin_client.patch(
                        f'/api/orders/{order.id}/',
                        {
                            'items': [
                                {
                                    'name': 'Updated Product',
                                    'sku': 'UPD-001',
                                    'quantity': 20,
                                    'unit_price': '10.00',
                                    'attributes': {},
                                    'image_url': image_url
                                }
                            ]
                        },
                        format='json'
                    )
        
        # Verify update succeeded
        assert response.status_code == status.HTTP_200_OK
        
        # Verify image was copied
        assert len(saved_paths) > 0
        saved_path = saved_paths[0]
        assert saved_path.startswith(f'product_images/{order.id}/')
        
        # Verify order item was updated
        order.refresh_from_db()
        items = order.items.all()
        assert len(items) == 1
        
        item = items[0]
        assert item.name == 'Updated Product'
        assert item.image_url is not None
        assert 'product_images' in item.image_url
    
    def test_update_order_avoids_re_copying(self, admin_client):
        """Test order update avoids re-copying already copied images."""
        # Create order with copied image
        order = OrderFactory()
        copied_image_url = f'/media/product_images/{order.id}/already_copied.jpg'
        OrderItem.objects.create(
            order=order,
            name='Product With Copied Image',
            sku='COPY-001',
            quantity=10,
            unit_price=5.00,
            image_url=copied_image_url
        )
        
        saved_paths = []
        
        def capture_save(path, content_file):
            saved_paths.append(path)
            return path
        
        # Mock copy function (should not be called)
        with patch('orders.utils.copy_product_image_to_storage') as mock_copy:
            # Update order with same image URL
            response = admin_client.patch(
                f'/api/orders/{order.id}/',
                {
                    'items': [
                        {
                            'name': 'Product With Copied Image',
                            'sku': 'COPY-001',
                            'quantity': 10,
                            'unit_price': '5.00',
                            'attributes': {},
                            'image_url': copied_image_url
                        }
                    ]
                },
                format='json'
            )
        
        # Verify update succeeded
        assert response.status_code == status.HTTP_200_OK
        
        # Verify copy function was NOT called (image already copied)
        mock_copy.assert_not_called()
        
        # Verify order item still has copied image URL
        order.refresh_from_db()
        items = order.items.all()
        assert len(items) == 1
        
        item = items[0]
        assert item.image_url == copied_image_url
    
    def test_update_order_replaces_old_images(self, admin_client):
        """Test order update replaces old images with new ones."""
        # Create order with image A
        order = OrderFactory()
        image_url_a = 'https://example.com/product_a.jpg'
        
        # Mock first image
        img_a = PILImage.new('RGB', (100, 100), color='red')
        img_bytes_a = BytesIO()
        img_a.save(img_bytes_a, format='JPEG')
        img_bytes_a.seek(0)
        image_data_a = img_bytes_a.getvalue()
        
        mock_response_a = Mock()
        mock_response_a.content = image_data_a
        mock_response_a.headers = {'Content-Type': 'image/jpeg'}
        mock_response_a.raise_for_status = Mock()
        mock_response_a.iter_content.return_value = [image_data_a]
        
        saved_paths_a = []
        
        def capture_save_a(path, content_file):
            saved_paths_a.append(path)
            return path
        
        with patch('orders.utils.requests.get', return_value=mock_response_a):
            with patch('orders.utils.default_storage.save', side_effect=capture_save_a):
                with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order.id}/a.jpg'):
                    # Create order with image A
                    response = admin_client.post(
                        '/api/orders/',
                        {
                            'clientName': 'Test Client',
                            'items': [
                                {
                                    'name': 'Product',
                                    'sku': 'PROD-001',
                                    'quantity': 10,
                                    'unit_price': '5.00',
                                    'attributes': {},
                                    'image_url': image_url_a
                                }
                            ]
                        },
                        format='json'
                    )
        
        order_data = response.data
        if isinstance(order_data, dict) and 'data' in order_data:
            order_id = order_data['data'].get('id') or order_data['data'].get('order_id')
        else:
            order_id = order_data.get('id') or order_data.get('order_id')
        order = Order.objects.get(id=order_id)
        
        # Now update with image B
        image_url_b = 'https://example.com/product_b.jpg'
        
        img_b = PILImage.new('RGB', (100, 100), color='blue')
        img_bytes_b = BytesIO()
        img_b.save(img_bytes_b, format='PNG')
        img_bytes_b.seek(0)
        image_data_b = img_bytes_b.getvalue()
        
        mock_response_b = Mock()
        mock_response_b.content = image_data_b
        mock_response_b.headers = {'Content-Type': 'image/png'}
        mock_response_b.raise_for_status = Mock()
        mock_response_b.iter_content.return_value = [image_data_b]
        
        saved_paths_b = []
        
        def capture_save_b(path, content_file):
            saved_paths_b.append(path)
            return path
        
        with patch('orders.utils.requests.get', return_value=mock_response_b):
            with patch('orders.utils.default_storage.save', side_effect=capture_save_b):
                with patch('orders.utils.default_storage.url', return_value=f'/media/product_images/{order.id}/b.png'):
                    # Update order with image B
                    response = admin_client.patch(
                        f'/api/orders/{order.id}/',
                        {
                            'items': [
                                {
                                    'name': 'Product',
                                    'sku': 'PROD-001',
                                    'quantity': 10,
                                    'unit_price': '5.00',
                                    'attributes': {},
                                    'image_url': image_url_b
                                }
                            ]
                        },
                        format='json'
                    )
        
        # Verify update succeeded
        assert response.status_code == status.HTTP_200_OK
        
        # Verify new image was copied
        assert len(saved_paths_b) > 0
        
        # Verify order item has new image URL
        order.refresh_from_db()
        items = order.items.all()
        assert len(items) == 1
        
        item = items[0]
        assert item.image_url is not None
        assert 'product_images' in item.image_url
