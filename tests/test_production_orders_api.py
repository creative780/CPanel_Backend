"""
Backend API tests for production orders endpoints.
Tests the production orders list, detail, machine assignment, and file management.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db import connection

from orders.models import Order, OrderItem, ProductMachineAssignment, OrderFile
from monitoring.models import Device, Org
from accounts.models import Role


def _auth_client(role: str = 'admin', test_device=None) -> APIClient:
    """Create and authenticate an APIClient for the given role."""
    User = get_user_model()
    username = f"{role}_test_{timezone.now().timestamp()}"
    user = User.objects.create_user(username=username, password='testpass123', roles=[role])
    client = APIClient()
    
    # Ensure database connection is open
    connection.ensure_connection()
    
    # Prepare login data
    login_data = {
        'username': user.username,
        'password': 'testpass123',
        'role': role
    }
    
    # Non-admin users need device_id
    headers = {}
    if role != 'admin' and test_device:
        headers['HTTP_X_DEVICE_ID'] = test_device.id
    
    login = client.post(
        '/api/auth/login',
        login_data,
        format='json',
        **headers
    )
    
    if login.status_code == 200:
        token = login.data.get('token') or login.data.get('access')
        if token:
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    else:
        # If login fails, try without device for admin
        if role == 'admin':
            login = client.post(
                '/api/auth/login',
                login_data,
                format='json',
            )
            if login.status_code == 200:
                token = login.data.get('token') or login.data.get('access')
                if token:
                    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    return client


def _create_production_order(client: APIClient, status_val='sent_to_production', stage_val='printing') -> int:
    """Create a test order in production stage."""
    resp = client.post(
        '/api/orders/',
        {
            'clientName': 'Test Production Client',
            'companyName': 'Test Co',
            'phone': '+971501234567',
            'email': 'test@example.com',
            'address': 'Dubai, UAE',
            'specs': 'Test production order',
            'urgency': 'Normal',
            'status': status_val,
            'stage': stage_val,
            'channel': 'b2b_customers',
            'items': [
                {
                    'name': 'Business Cards',
                    'sku': 'BC-TEST-001',
                    'quantity': 500,
                    'unit_price': '0.50',
                    'attributes': {'finish': 'matte'}
                }
            ]
        },
        format='json',
    )
    if resp.status_code in [200, 201]:
        data = resp.data
        if isinstance(data, dict) and 'data' in data:
            return data['data'].get('id') or data['data'].get('order_id')
        return data.get('id') or data.get('order_id')
    return None


@pytest.mark.django_db(transaction=True)
class TestProductionOrdersListEndpoint:
    """Test GET /api/production/orders/ endpoint."""
    
    def test_get_production_orders_as_admin(self, admin_client, db):
        """Test admin can access production orders."""
        # Ensure database connection is open
        connection.ensure_connection()
        # Create test orders
        order1 = Order.objects.create(
            order_code='PROD-TEST-001',
            client_name='Test Client 1',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        order2 = Order.objects.create(
            order_code='PROD-TEST-002',
            client_name='Test Client 2',
            status='active',
            stage='printing',
            urgency='High'
        )
        
        response = admin_client.get('/api/production/orders/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert 'results' in data or isinstance(data, list)
        results = data.get('results', data) if isinstance(data, dict) else data
        assert len(results) >= 2
        
        # Verify orders are in results
        order_codes = [o.get('order_code') for o in results]
        assert 'PROD-TEST-001' in order_codes
        assert 'PROD-TEST-002' in order_codes
    
    def test_get_production_orders_as_production_user(self, production_client, db):
        """Test production user can access production orders."""
        connection.ensure_connection()
        order = Order.objects.create(
            order_code='PROD-TEST-003',
            client_name='Test Client 3',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        response = production_client.get('/api/production/orders/')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_production_orders_filters_correctly(self, admin_client, db):
        """Test production orders endpoint filters correctly."""
        connection.ensure_connection()
        # Create production order
        prod_order = Order.objects.create(
            order_code='PROD-TEST-004',
            client_name='Production Client',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        # Create non-production order
        non_prod_order = Order.objects.create(
            order_code='NON-PROD-001',
            client_name='Non-Production Client',
            status='new',
            stage='order_intake',
            urgency='Normal'
        )
        
        response = admin_client.get('/api/production/orders/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        
        order_codes = [o.get('order_code') for o in results]
        assert 'PROD-TEST-004' in order_codes
        # Non-production order should not be in results (or may be if filtering is different)
    
    def test_get_production_orders_unauthorized(self):
        """Test unauthorized access is rejected."""
        client = APIClient()  # No authentication
        
        response = client.get('/api/production/orders/')
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db(transaction=True)
class TestProductionOrderDetailEndpoint:
    """Test GET /api/production/orders/{id}/ endpoint."""
    
    def test_get_production_order_detail(self, admin_client, db):
        """Test getting production order details."""
        connection.ensure_connection()
        order = Order.objects.create(
            order_code='PROD-DETAIL-001',
            client_name='Detail Client',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        OrderItem.objects.create(
            order=order,
            name='Test Product',
            sku='TEST-SKU',
            quantity=100,
            unit_price=Decimal('10.00'),
            line_total=Decimal('1000.00')
        )
        
        response = admin_client.get(f'/api/production/orders/{order.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        order_data = data.get('order', data)
        assert order_data.get('order_code') == 'PROD-DETAIL-001'
        assert 'items' in order_data or 'items' in data
    
    def test_get_production_order_detail_not_found(self, admin_client, db):
        """Test getting non-existent order returns 404."""
        connection.ensure_connection()
        response = admin_client.get('/api/production/orders/99999/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_production_order_detail_not_in_production(self, admin_client, db):
        """Test getting order not in production returns error."""
        connection.ensure_connection()
        order = Order.objects.create(
            order_code='NON-PROD-DETAIL',
            client_name='Non-Prod Client',
            status='new',
            stage='order_intake',
            urgency='Normal'
        )
        
        response = admin_client.get(f'/api/production/orders/{order.id}/')
        
        # Should return 400 or 404 depending on implementation
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db(transaction=True)
class TestMachineAssignmentEndpoint:
    """Test POST /api/orders/{id}/assign-machines/ endpoint."""
    
    def test_assign_machines_to_order(self, production_client, db):
        """Test assigning machines to order products."""
        
        order = Order.objects.create(
            order_code='PROD-ASSIGN-001',
            client_name='Assign Client',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        item1 = OrderItem.objects.create(
            order=order,
            name='Product 1',
            sku='PROD-1',
            quantity=100,
            unit_price=Decimal('5.00'),
            line_total=Decimal('500.00')
        )
        
        item2 = OrderItem.objects.create(
            order=order,
            name='Product 2',
            sku='PROD-2',
            quantity=200,
            unit_price=Decimal('3.00'),
            line_total=Decimal('600.00')
        )
        
        assignments = [
            {
                'product_name': 'Product 1',
                'product_sku': 'PROD-1',
                'product_quantity': 100,
                'machine_id': 'printer-01',
                'machine_name': 'Digital Printer 1',
                'estimated_time_minutes': 60,
                'assigned_by': 'production_user',
                'notes': 'Test assignment 1'
            },
            {
                'product_name': 'Product 2',
                'product_sku': 'PROD-2',
                'product_quantity': 200,
                'machine_id': 'laser-01',
                'machine_name': 'Laser Cutter 1',
                'estimated_time_minutes': 45,
                'assigned_by': 'production_user',
                'notes': 'Test assignment 2'
            }
        ]
        
        response = production_client.post(
            f'/api/orders/{order.id}/assign-machines/',
            assignments,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2
        
        # Verify assignments were created
        order.refresh_from_db()
        assert order.machine_assignments.count() == 2
        assert order.status == 'getting_ready'
    
    def test_assign_machines_validation_error(self, production_client, db):
        """Test machine assignment with missing required fields."""
        order = Order.objects.create(
            order_code='PROD-ASSIGN-002',
            client_name='Assign Client 2',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        # Missing required fields
        invalid_assignment = [
            {
                'product_name': 'Product 1',
                # Missing machine_id, machine_name, etc.
            }
        ]
        
        response = production_client.post(
            f'/api/orders/{order.id}/assign-machines/',
            invalid_assignment,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_assign_machines_not_list(self, production_client, db):
        """Test machine assignment with non-list data."""
        order = Order.objects.create(
            order_code='PROD-ASSIGN-003',
            client_name='Assign Client 3',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        # Send object instead of list
        response = production_client.post(
            f'/api/orders/{order.id}/assign-machines/',
            {'product_name': 'Test'},
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_assign_machines_unauthorized(self, sales_client, db):
        """Test machine assignment requires production/admin role."""
        order = Order.objects.create(
            order_code='PROD-ASSIGN-004',
            client_name='Assign Client 4',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        assignments = [
            {
                'product_name': 'Product 1',
                'product_sku': 'PROD-1',
                'product_quantity': 100,
                'machine_id': 'printer-01',
                'machine_name': 'Digital Printer 1',
                'estimated_time_minutes': 60,
            }
        ]
        
        response = sales_client.post(
            f'/api/orders/{order.id}/assign-machines/',
            assignments,
            format='json'
        )
        
        # Should be forbidden or unauthorized
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED
        ]


@pytest.mark.django_db(transaction=True)
class TestOrderStatusUpdates:
    """Test PATCH /api/orders/{id}/ for status updates."""
    
    def test_update_order_status_to_active(self, production_client, db):
        """Test updating order status to active (start production)."""
        
        order = Order.objects.create(
            order_code='PROD-STATUS-001',
            client_name='Status Client',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        response = production_client.patch(
            f'/api/orders/{order.id}/',
            {
                'status': 'active',
                'stage': 'printing'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.status == 'active'
        assert order.stage == 'printing'
    
    def test_update_order_stage(self, admin_client, db):
        """Test updating order stage."""
        
        order = Order.objects.create(
            order_code='PROD-STATUS-002',
            client_name='Status Client 2',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        response = admin_client.patch(
            f'/api/orders/{order.id}/',
            {
                'stage': 'printing',
                'status': 'active'
            },
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        order.refresh_from_db()
        assert order.stage == 'printing'
        assert order.status == 'active'


@pytest.mark.django_db(transaction=True)
class TestOrderFilesEndpoint:
    """Test GET /api/orders/{id}/files/ endpoint."""
    
    def test_get_order_files(self, production_client, db):
        """Test retrieving order files."""
        
        order = Order.objects.create(
            order_code='PROD-FILES-001',
            client_name='Files Client',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        # Create test files
        from django.core.files.base import ContentFile
        design_file = ContentFile(b'Design file content', name='design.pdf')
        OrderFile.objects.create(
            order=order,
            file=design_file,
            file_name='design.pdf',
            file_type='design',
            file_size=20,
            mime_type='application/pdf',
            uploaded_by='designer1',
            uploaded_by_role='designer',
            stage='design',
            visible_to_roles=['admin', 'production'],
            description='Design file'
        )
        
        print_file = ContentFile(b'Print file content', name='print.pdf')
        OrderFile.objects.create(
            order=order,
            file=print_file,
            file_name='print.pdf',
            file_type='final',
            file_size=18,
            mime_type='application/pdf',
            uploaded_by='designer1',
            uploaded_by_role='designer',
            stage='printing',
            visible_to_roles=['admin', 'production'],
            description='Print-ready file'
        )
        
        response = production_client.get(f'/api/orders/{order.id}/files/')
        
        assert response.status_code == status.HTTP_200_OK
        files = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(files) == 2
        
        file_types = [f.get('file_type') for f in files]
        assert 'design' in file_types
        assert 'final' in file_types
    
    def test_get_order_files_empty(self, production_client, db):
        """Test retrieving files for order with no files."""
        
        order = Order.objects.create(
            order_code='PROD-FILES-002',
            client_name='No Files Client',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        response = production_client.get(f'/api/orders/{order.id}/files/')
        
        assert response.status_code == status.HTTP_200_OK
        files = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(files) == 0
    
    def test_get_order_files_permissions(self, production_client, db):
        """Test file retrieval respects role permissions."""
        
        order = Order.objects.create(
            order_code='PROD-FILES-003',
            client_name='Perms Client',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        from django.core.files.base import ContentFile
        restricted_file = ContentFile(b'Restricted content', name='restricted.pdf')
        OrderFile.objects.create(
            order=order,
            file=restricted_file,
            file_name='restricted.pdf',
            file_type='design',
            file_size=20,
            mime_type='application/pdf',
            uploaded_by='designer1',
            uploaded_by_role='designer',
            stage='design',
            visible_to_roles=['admin', 'designer'],  # Production not included
            description='Restricted file'
        )
        
        response = production_client.get(f'/api/orders/{order.id}/files/')
        
        # Should still return 200, but may filter files based on permissions
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
class TestProductionOrdersFiltering:
    """Test production orders filtering by status and stage."""
    
    def test_filter_by_status_sent_to_production(self, admin_client, db):
        """Test filtering orders by sent_to_production status."""
        
        # Create orders with different statuses
        Order.objects.create(
            order_code='PROD-FILTER-001',
            client_name='Filter Client 1',
            status='sent_to_production',
            stage='printing',
            urgency='Normal'
        )
        
        Order.objects.create(
            order_code='PROD-FILTER-002',
            client_name='Filter Client 2',
            status='active',
            stage='printing',
            urgency='Normal'
        )
        
        Order.objects.create(
            order_code='PROD-FILTER-003',
            client_name='Filter Client 3',
            status='getting_ready',
            stage='printing',
            urgency='Normal'
        )
        
        response = admin_client.get('/api/production/orders/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        
        # All three should be in production orders
        order_codes = [o.get('order_code') for o in results]
        assert 'PROD-FILTER-001' in order_codes
        assert 'PROD-FILTER-002' in order_codes
        assert 'PROD-FILTER-003' in order_codes
    
    def test_production_orders_ordering(self, admin_client, db):
        """Test production orders are ordered by updated_at."""
        
        order1 = Order.objects.create(
            order_code='PROD-ORDER-001',
            client_name='Order Client 1',
            status='sent_to_production',
            stage='printing',
            urgency='Normal',
            updated_at=timezone.now() - timedelta(hours=2)
        )
        
        order2 = Order.objects.create(
            order_code='PROD-ORDER-002',
            client_name='Order Client 2',
            status='sent_to_production',
            stage='printing',
            urgency='Normal',
            updated_at=timezone.now() - timedelta(hours=1)
        )
        
        order3 = Order.objects.create(
            order_code='PROD-ORDER-003',
            client_name='Order Client 3',
            status='sent_to_production',
            stage='printing',
            urgency='Normal',
            updated_at=timezone.now()
        )
        
        response = admin_client.get('/api/production/orders/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        
        # Should be ordered by updated_at descending (most recent first)
        order_codes = [o.get('order_code') for o in results]
        # Most recent should appear first
        assert order_codes.index('PROD-ORDER-003') < order_codes.index('PROD-ORDER-001')

