"""
Unit tests for orders serializers.
"""
import pytest
from orders.serializers import OrderSerializer
from tests.factories import OrderFactory, ClientFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestOrderSerializer:
    """Test OrderSerializer."""
    
    def test_profile_tag_from_client(self):
        """Test profile_tag is retrieved from client when client has profile_tag."""
        # Create client with profile_tag
        from clients.models import Client
        client = ClientFactory()
        if hasattr(Client, 'profile_tag'):
            client.profile_tag = 'b2b'
            client.save()
        
        # Create order linked to client
        order = OrderFactory(channel='b2c_customers')
        if hasattr(order, 'client'):
            order.client = client
            order.save()
        
        # Serialize order - reload to ensure client relationship is loaded
        from orders.models import Order
        order = Order.objects.select_related('client').get(pk=order.pk)
        serializer = OrderSerializer(order)
        
        # Client's profile_tag should take priority over channel
        if hasattr(Client, 'profile_tag') and hasattr(order, 'client') and order.client:
            assert serializer.data['profile_tag'] == 'b2b'
        else:
            # Fall back to channel if client relationship not available
            assert serializer.data['profile_tag'] == 'b2c'
        assert 'profile_tag' in serializer.data
    
    def test_profile_tag_from_channel_when_client_has_none(self):
        """Test profile_tag falls back to channel when client exists but has no profile_tag."""
        # Create client without profile_tag
        from clients.models import Client
        client = ClientFactory()
        # Ensure profile_tag is None
        if hasattr(Client, 'profile_tag'):
            client.profile_tag = None
            client.save()
        
        # Create order linked to client with channel
        order = OrderFactory(channel='b2c_customers')
        if hasattr(order, 'client'):
            order.client = client
            order.save()
        
        # Serialize order - reload to ensure client relationship is loaded
        from orders.models import Order
        order = Order.objects.select_related('client').get(pk=order.pk)
        serializer = OrderSerializer(order)
        
        # Should fall back to channel mapping
        assert serializer.data['profile_tag'] == 'b2c'
        assert 'profile_tag' in serializer.data
    
    def test_profile_tag_from_channel_when_no_client(self):
        """Test profile_tag is derived from channel when no client exists."""
        # Create order without client, with channel
        order = OrderFactory(channel='walk_in_orders')
        if hasattr(order, 'client'):
            order.client = None
            order.save()
        
        # Serialize order
        serializer = OrderSerializer(order)
        
        # Should derive from channel
        assert serializer.data['profile_tag'] == 'walk_in'
        assert 'profile_tag' in serializer.data
    
    @pytest.mark.parametrize('channel,expected_tag', [
        ('b2b_customers', 'b2b'),
        ('b2c_customers', 'b2c'),
        ('walk_in_orders', 'walk_in'),
        ('online_store', 'online'),
    ])
    def test_profile_tag_channel_mappings(self, channel, expected_tag):
        """Test all channel to profile_tag mappings."""
        # Create order without client, with specific channel
        order = OrderFactory(channel=channel)
        if hasattr(order, 'client'):
            order.client = None
            order.save()
        
        # Serialize order
        serializer = OrderSerializer(order)
        
        # Should map channel to correct profile_tag
        assert serializer.data['profile_tag'] == expected_tag
        assert 'profile_tag' in serializer.data
    
    def test_profile_tag_none_when_no_client_no_channel(self):
        """Test profile_tag returns None when no client and no channel."""
        # Create order without client and without channel
        order = OrderFactory(channel=None)
        if hasattr(order, 'client'):
            order.client = None
            order.save()
        
        # Serialize order
        serializer = OrderSerializer(order)
        
        # Should return None when no data available
        assert serializer.data['profile_tag'] is None
        assert 'profile_tag' in serializer.data
    
    def test_profile_tag_none_for_unmapped_channel(self):
        """Test profile_tag returns None for unmapped channel."""
        # Create order with unmapped channel
        order = OrderFactory(channel='salesperson_generated')
        if hasattr(order, 'client'):
            order.client = None
            order.save()
        
        # Serialize order
        serializer = OrderSerializer(order)
        
        # Unmapped channels should return None
        assert serializer.data['profile_tag'] is None
        assert 'profile_tag' in serializer.data
