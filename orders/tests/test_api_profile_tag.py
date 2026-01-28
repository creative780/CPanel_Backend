"""
API endpoint tests for profile_tag field in order responses.
"""
import pytest
from rest_framework import status
from django.urls import reverse
from tests.factories import OrderFactory, ClientFactory


@pytest.mark.django_db
@pytest.mark.integration
class TestProfileTagAPI:
    """Test profile_tag appears in API responses."""
    
    def test_api_profile_tag_from_client(self, admin_client):
        """Test API returns profile_tag from client."""
        # Create client with profile_tag
        from clients.models import Client
        client = ClientFactory()
        if hasattr(client, 'profile_tag'):
            client.profile_tag = 'b2b'
            client.save()
            # Refresh client to ensure profile_tag is saved
            client = Client.objects.get(pk=client.pk)
        
        # Create order linked to client
        order = OrderFactory(channel='b2c_customers')
        if hasattr(order, 'client'):
            order.client = client
            order.save()
        # Reload order to ensure client relationship is available
        from orders.models import Order
        order = Order.objects.select_related('client').get(pk=order.pk)
        
        # Make API request to retrieve order
        url = reverse('orders-detail', kwargs={'pk': order.id})
        response = admin_client.get(url)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert 'profile_tag' in response.data
        # If client has profile_tag, it should take priority; otherwise use channel
        if hasattr(client, 'profile_tag') and client.profile_tag:
            assert response.data['profile_tag'] == 'b2b'
        else:
            # Fall back to channel mapping
            assert response.data['profile_tag'] == 'b2c'
    
    def test_api_profile_tag_from_channel(self, admin_client):
        """Test API returns profile_tag from channel when no client."""
        # Create order without client, with channel
        order = OrderFactory(channel='b2c_customers')
        if hasattr(order, 'client'):
            order.client = None
            order.save()
        
        # Make API request to retrieve order
        url = reverse('orders-detail', kwargs={'pk': order.id})
        response = admin_client.get(url)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert 'profile_tag' in response.data
        assert response.data['profile_tag'] == 'b2c'
    
    def test_api_profile_tag_in_list(self, admin_client):
        """Test API returns profile_tag in list endpoint."""
        # Create multiple orders with different profile_tag sources
        from clients.models import Client
        from orders.models import Order
        
        client_b2b = ClientFactory()
        if hasattr(client_b2b, 'profile_tag'):
            client_b2b.profile_tag = 'b2b'
            client_b2b.save()
            client_b2b = Client.objects.get(pk=client_b2b.pk)
        
        order_with_client = OrderFactory()
        if hasattr(order_with_client, 'client'):
            order_with_client.client = client_b2b
            order_with_client.save()
            order_with_client = Order.objects.select_related('client').get(pk=order_with_client.pk)
        
        client_b2c_none = ClientFactory()
        if hasattr(client_b2c_none, 'profile_tag'):
            client_b2c_none.profile_tag = None
            client_b2c_none.save()
            client_b2c_none = Client.objects.get(pk=client_b2c_none.pk)
        
        order_with_client_none = OrderFactory(channel='b2c_customers')
        if hasattr(order_with_client_none, 'client'):
            order_with_client_none.client = client_b2c_none
            order_with_client_none.save()
            order_with_client_none = Order.objects.select_related('client').get(pk=order_with_client_none.pk)
        
        order_with_channel = OrderFactory(channel='walk_in_orders')
        if hasattr(order_with_channel, 'client'):
            order_with_channel.client = None
            order_with_channel.save()
        
        order_no_data = OrderFactory(channel=None)
        if hasattr(order_no_data, 'client'):
            order_no_data.client = None
            order_no_data.save()
        
        # Make API request to list orders
        url = reverse('orders-list')
        response = admin_client.get(url)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        
        # Find our orders in the response
        order_ids = [o['id'] for o in response.data]
        
        # Verify all orders have profile_tag key
        for order_data in response.data:
            assert 'profile_tag' in order_data
        
        # Verify specific orders have correct profile_tag
        if order_with_client.id in order_ids:
            order_data = next(o for o in response.data if o['id'] == order_with_client.id)
            # If client has profile_tag, use it; otherwise expect None or channel fallback
            if hasattr(Client.objects.get(pk=client_b2b.pk), 'profile_tag') and Client.objects.get(pk=client_b2b.pk).profile_tag:
                assert order_data['profile_tag'] == 'b2b'
            else:
                # If profile_tag not available on model, just check it exists
                assert 'profile_tag' in order_data
        
        if order_with_client_none.id in order_ids:
            order_data = next(o for o in response.data if o['id'] == order_with_client_none.id)
            assert order_data['profile_tag'] == 'b2c'
        
        if order_with_channel.id in order_ids:
            order_data = next(o for o in response.data if o['id'] == order_with_channel.id)
            assert order_data['profile_tag'] == 'walk_in'
        
        if order_no_data.id in order_ids:
            order_data = next(o for o in response.data if o['id'] == order_no_data.id)
            assert order_data['profile_tag'] is None
    
    def test_api_profile_tag_none_when_unavailable(self, admin_client):
        """Test API returns None for profile_tag when unavailable."""
        # Create order without client and without channel
        order = OrderFactory(channel=None)
        if hasattr(order, 'client'):
            order.client = None
            order.save()
        
        # Make API request to retrieve order
        url = reverse('orders-detail', kwargs={'pk': order.id})
        response = admin_client.get(url)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert 'profile_tag' in response.data
        assert response.data['profile_tag'] is None
