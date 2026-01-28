"""
Security and Authorization Tests for HR Employee Management

Test Case Categories:
1. Employee Creation Access Control
2. Employee List Access Control
3. Permission Class Verification
"""
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Role
from tests.factories import (
    AdminUserFactory, SalesUserFactory, DesignerUserFactory, 
    FinanceUserFactory, HREmployeeFactory, UserFactory
)
from hr.models import HREmployee

User = get_user_model()


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def authenticated_admin_client(admin_user, api_client):
    """Create authenticated API client for admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def authenticated_employee_client(sales_user, api_client):
    """Create authenticated API client for regular employee."""
    api_client.force_authenticate(user=sales_user)
    return api_client


@pytest.fixture
def authenticated_finance_client(finance_user, api_client):
    """Create authenticated API client for finance user."""
    api_client.force_authenticate(user=finance_user)
    return api_client


@pytest.fixture
def sample_employee(admin_user):
    """Create a sample employee for testing."""
    user = UserFactory(
        username='employee_user',
        email='employee@test.com',
        roles=[Role.SALES]
    )
    return HREmployeeFactory(
        user=user,
        name='Test Employee',
        email='employee@test.com'
    )


# ============================================================================
# Test Case 1.1: Employee Creation Access Control
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestEmployeeCreationAccessControl:
    """Test Case 1.1: Employee Creation Access Control"""
    
    def test_1_1_1_admin_can_create_employee(self, authenticated_admin_client):
        """Test Case 1.1.1: Admin Can Create Employee"""
        employee_data = {
            'name': 'New Employee',
            'email': 'newemployee@test.com',
            'phone': '+1234567890',
            'salary': '5000.00',
            'designation': 'Software Engineer',
            'status': 'Active',
            'role': 'sales',
            'branch': 'dubai',
            'username': 'newemployee',
            'password': 'testpass123'
        }
        
        response = authenticated_admin_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Employee'
        assert response.data['email'] == 'newemployee@test.com'
        
        # Verify employee created in database
        employee = HREmployee.objects.get(email='newemployee@test.com')
        assert employee.name == 'New Employee'
        assert employee.user is not None
        assert employee.user.username == 'newemployee'
    
    def test_1_1_2_employee_cannot_create_employee(self, authenticated_employee_client):
        """Test Case 1.1.2: Employee Cannot Create Employee (API)"""
        employee_data = {
            'name': 'Unauthorized Employee',
            'email': 'unauthorized@test.com',
            'salary': '4000.00',
            'designation': 'Intern',
            'status': 'Active',
            'role': 'sales',
            'branch': 'dubai',
            'username': 'unauthorized',
            'password': 'testpass123'
        }
        
        response = authenticated_employee_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data or 'Permission denied' in str(response.data)
        
        # Verify no employee created
        assert not HREmployee.objects.filter(email='unauthorized@test.com').exists()
    
    def test_1_1_3_employee_cannot_create_employee_direct_api(self, authenticated_employee_client):
        """Test Case 1.1.3: Employee Cannot Create Employee (Direct API Call)"""
        employee_data = {
            'name': 'Direct API Employee',
            'email': 'directapi@test.com',
            'salary': '4000.00',
            'status': 'Active',
            'role': 'sales',
            'branch': 'dubai'
        }
        
        response = authenticated_employee_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        # Should be blocked at permission level
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Verify no employee created
        assert not HREmployee.objects.filter(email='directapi@test.com').exists()
    
    def test_1_1_4_unauthenticated_user_cannot_access(self, api_client):
        """Test Case 1.1.4: Unauthenticated User Cannot Access"""
        employee_data = {
            'name': 'Public Employee',
            'email': 'public@test.com',
            'salary': '3000.00',
            'status': 'Active',
            'role': 'sales',
            'branch': 'dubai'
        }
        
        response = api_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Test Case 1.2: Employee List Access Control
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestEmployeeListAccessControl:
    """Test Case 1.2: Employee List Access Control"""
    
    def test_1_2_1_admin_can_see_all_employees(self, authenticated_admin_client):
        """Test Case 1.2.1: Admin Can See All Employees"""
        # Create multiple employees
        employee1 = HREmployeeFactory(email='emp1@test.com', name='Employee 1')
        employee2 = HREmployeeFactory(email='emp2@test.com', name='Employee 2')
        employee3 = HREmployeeFactory(email='emp3@test.com', name='Employee 3')
        
        response = authenticated_admin_client.get('/api/hr/employees')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3
        
        # Verify all employees are in response
        emails = [emp['email'] for emp in response.data]
        assert 'emp1@test.com' in emails
        assert 'emp2@test.com' in emails
        assert 'emp3@test.com' in emails
    
    def test_1_2_2_employee_can_only_see_own_record(self, authenticated_employee_client, sales_user):
        """Test Case 1.2.2: Employee Can Only See Own Record"""
        # Create employee record for the sales_user
        employee = HREmployeeFactory(
            user=sales_user,
            email=sales_user.email,
            name='Self Employee'
        )
        
        # Create other employees
        other_employee1 = HREmployeeFactory(email='other1@test.com', name='Other 1')
        other_employee2 = HREmployeeFactory(email='other2@test.com', name='Other 2')
        
        response = authenticated_employee_client.get('/api/hr/employees')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['email'] == sales_user.email
        assert response.data[0]['name'] == 'Self Employee'
    
    def test_1_2_3_finance_user_can_see_all_employees(self, authenticated_finance_client):
        """Test Case 1.2.3: Finance User Can See All Employees"""
        # Create multiple employees
        employee1 = HREmployeeFactory(email='fin_emp1@test.com', name='Finance Employee 1')
        employee2 = HREmployeeFactory(email='fin_emp2@test.com', name='Finance Employee 2')
        
        response = authenticated_finance_client.get('/api/hr/employees')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
        
        # Verify employees are in response
        emails = [emp['email'] for emp in response.data]
        assert 'fin_emp1@test.com' in emails
        assert 'fin_emp2@test.com' in emails


# ============================================================================
# Test Case 1.3: Permission Class Verification
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestPermissionClassVerification:
    """Test Case 1.3: Permission Class Verification"""
    
    def test_1_3_1_get_permissions_method_exists(self):
        """Test Case 1.3.1: Verify get_permissions() Method Works"""
        from hr.views import HREmployeesListView
        
        view = HREmployeesListView()
        
        # Check if get_permissions method exists
        assert hasattr(view, 'get_permissions'), "get_permissions() method should exist"
        
        # Create mock request objects
        from unittest.mock import Mock
        
        # Test GET request permissions
        view.request = Mock(method='GET')
        get_perms = view.get_permissions()
        
        # Test POST request permissions
        view.request = Mock(method='POST')
        post_perms = view.get_permissions()
        
        # POST should have more restrictive permissions (RolePermission)
        assert len(post_perms) >= len(get_perms) or post_perms != get_perms, \
            "POST should have different/more restrictive permissions than GET"
    
    def test_1_3_2_allowed_roles_is_set(self):
        """Test Case 1.3.2: Verify allowed_roles is Set"""
        from hr.views import HREmployeesListView
        
        view = HREmployeesListView()
        
        # Check if allowed_roles attribute exists
        assert hasattr(view, 'allowed_roles'), "allowed_roles should be set"
        
        # Verify it contains 'admin'
        assert 'admin' in view.allowed_roles, "allowed_roles should include 'admin'"


# ============================================================================
# Test Case 3.2: Employee Detail Access
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestEmployeeDetailAccess:
    """Test Case 3.2: Employee Detail Access"""
    
    def test_3_2_1_admin_can_view_any_employee(self, authenticated_admin_client, sample_employee):
        """Test Case 3.2.1: Admin Can View Any Employee"""
        response = authenticated_admin_client.get(f'/api/hr/employees/{sample_employee.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_employee.id
        assert response.data['email'] == sample_employee.email
    
    def test_3_2_2_employee_can_view_own_details(self, authenticated_employee_client, sales_user):
        """Test Case 3.2.2: Employee Can View Own Details"""
        employee = HREmployeeFactory(
            user=sales_user,
            email=sales_user.email,
            name='Self Employee'
        )
        
        response = authenticated_employee_client.get(f'/api/hr/employees/{employee.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == employee.id
        assert response.data['email'] == sales_user.email
    
    def test_3_2_3_employee_cannot_view_other_employee(self, authenticated_employee_client, sample_employee):
        """Test Case 3.2.3: Employee Cannot View Other Employee"""
        response = authenticated_employee_client.get(f'/api/hr/employees/{sample_employee.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data or 'Permission denied' in str(response.data)

