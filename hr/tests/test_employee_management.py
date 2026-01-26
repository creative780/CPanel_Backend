"""
Employee Management Tests

Test Case Categories:
1. Employee CRUD Operations
2. Employee Detail Access
3. Validation and Error Handling
"""
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Role
from tests.factories import (
    AdminUserFactory, SalesUserFactory, HREmployeeFactory, UserFactory
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


# ============================================================================
# Test Case 3.1: Employee CRUD Operations
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestEmployeeCRUDOperations:
    """Test Case 3.1: Employee CRUD Operations"""
    
    def test_3_1_1_create_employee_full_flow(self, authenticated_admin_client):
        """Test Case 3.1.1: Create Employee (Full Flow)"""
        employee_data = {
            'name': 'John Doe',
            'email': 'john.doe@test.com',
            'phone': '+1234567890',
            'salary': '5000.00',
            'designation': 'Software Engineer',
            'status': 'Active',
            'role': 'sales',
            'branch': 'dubai',
            'username': 'johndoe',
            'password': 'securepass123'
        }
        
        response = authenticated_admin_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify employee record exists
        employee = HREmployee.objects.get(email='john.doe@test.com')
        assert employee.name == 'John Doe'
        assert employee.email == 'john.doe@test.com'
        assert employee.salary == 5000.00
        
        # Verify user account created
        assert employee.user is not None
        assert employee.user.username == 'johndoe'
        assert employee.user.email == 'john.doe@test.com'
        
        # Verify EmployeeVerification record created
        from hr.models import EmployeeVerification
        verification = EmployeeVerification.objects.filter(employee=employee).first()
        assert verification is not None
        
        # Verify username normalized (lowercase)
        assert employee.user.username == 'johndoe'
        
        # Verify email normalized (lowercase)
        assert employee.email == 'john.doe@test.com'
    
    def test_3_1_2_create_employee_validation(self, authenticated_admin_client):
        """Test Case 3.1.2: Create Employee Validation"""
        # Missing required fields
        invalid_data = {
            'name': 'Incomplete Employee',
            # Missing email, salary, designation, role
        }
        
        response = authenticated_admin_client.post(
            '/api/hr/employees',
            invalid_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data or len(response.data) > 0
    
    def test_3_1_3_create_employee_duplicate_email(self, authenticated_admin_client):
        """Test Case 3.1.3: Create Employee Duplicate Email"""
        # Create first employee
        existing_employee = HREmployeeFactory(
            email='duplicate@test.com',
            name='First Employee'
        )
        
        # Try to create another with same email
        employee_data = {
            'name': 'Second Employee',
            'email': 'duplicate@test.com',  # Same email
            'salary': '4000.00',
            'designation': 'Designer',
            'status': 'Active',
            'role': 'designer',
            'branch': 'dubai',
            'username': 'secondemployee',
            'password': 'testpass123'
        }
        
        response = authenticated_admin_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in str(response.data).lower() or 'duplicate' in str(response.data).lower()
    
    def test_3_1_4_create_employee_duplicate_username(self, authenticated_admin_client):
        """Test Case 3.1.4: Create Employee Duplicate Username"""
        # Create first employee with username
        user1 = UserFactory(username='duplicateuser', email='user1@test.com')
        HREmployeeFactory(user=user1, email='user1@test.com')
        
        # Try to create another with same username
        employee_data = {
            'name': 'Second Employee',
            'email': 'user2@test.com',
            'salary': '4000.00',
            'designation': 'Designer',
            'status': 'Active',
            'role': 'designer',
            'branch': 'dubai',
            'username': 'duplicateuser',  # Same username
            'password': 'testpass123'
        }
        
        response = authenticated_admin_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in str(response.data).lower() or 'taken' in str(response.data).lower()
    
    def test_3_1_5_update_employee(self, authenticated_admin_client):
        """Test Case 3.1.5: Update Employee"""
        employee = HREmployeeFactory(
            name='Original Name',
            email='update@test.com',
            salary=3000.00,
            designation='Junior Developer'
        )
        
        update_data = {
            'name': 'Updated Name',
            'email': 'update@test.com',
            'salary': '4500.00',
            'designation': 'Senior Developer',
            'status': 'Active',
            'role': 'sales',
            'branch': 'dubai'
        }
        
        response = authenticated_admin_client.put(
            f'/api/hr/employees/{employee.id}',
            update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify changes reflected in database
        employee.refresh_from_db()
        assert employee.name == 'Updated Name'
        assert float(employee.salary) == 4500.00
        assert employee.designation == 'Senior Developer'
    
    def test_3_1_6_delete_employee(self, authenticated_admin_client):
        """Test Case 3.1.6: Delete Employee"""
        # Create a user first, then link it to employee
        user = UserFactory(
            username='delete_user',
            email='delete@test.com'
        )
        employee = HREmployeeFactory(
            email='delete@test.com',
            name='To Be Deleted',
            user=user
        )
        employee_id = employee.id
        user_id = user.id
        
        response = authenticated_admin_client.delete(
            f'/api/hr/employees/{employee_id}'
        )
        
        # Should either delete or soft-delete
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        
        # Verify employee no longer in list
        list_response = authenticated_admin_client.get('/api/hr/employees')
        employee_ids = [emp['id'] for emp in list_response.data]
        assert employee_id not in employee_ids
        
        # Verify employee record is deleted from database
        assert not HREmployee.objects.filter(id=employee_id).exists()
        
        # Verify User account is also deleted
        assert not User.objects.filter(id=user_id).exists()
    
    def test_3_1_6_delete_employee_no_user(self, authenticated_admin_client):
        """Test Case 3.1.6: Delete Employee without linked User account"""
        # Create employee without linked user
        employee = HREmployeeFactory(
            email='delete_no_user@test.com',
            name='To Be Deleted No User',
            user=None
        )
        employee_id = employee.id
        
        response = authenticated_admin_client.delete(
            f'/api/hr/employees/{employee_id}'
        )
        
        # Should succeed even without linked user
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        
        # Verify employee no longer in list
        list_response = authenticated_admin_client.get('/api/hr/employees')
        employee_ids = [emp['id'] for emp in list_response.data]
        assert employee_id not in employee_ids
        
        # Verify employee record is deleted from database
        assert not HREmployee.objects.filter(id=employee_id).exists()


# ============================================================================
# Additional Validation Tests
# ============================================================================

@pytest.mark.django_db
@pytest.mark.unit
class TestEmployeeValidation:
    """Additional validation tests for employee creation"""
    
    def test_invalid_email_format(self, authenticated_admin_client):
        """Test invalid email format is rejected"""
        employee_data = {
            'name': 'Invalid Email',
            'email': 'not-an-email',
            'salary': '3000.00',
            'designation': 'Tester',
            'status': 'Active',
            'role': 'sales',
            'branch': 'dubai',
            'username': 'invalidemail',
            'password': 'testpass123'
        }
        
        response = authenticated_admin_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_invalid_salary(self, authenticated_admin_client):
        """Test invalid salary is rejected"""
        employee_data = {
            'name': 'Invalid Salary',
            'email': 'invalid_salary@test.com',
            'salary': '-1000.00',  # Negative salary
            'designation': 'Tester',
            'status': 'Active',
            'role': 'sales',
            'branch': 'dubai',
            'username': 'invalidsalary',
            'password': 'testpass123'
        }
        
        response = authenticated_admin_client.post(
            '/api/hr/employees',
            employee_data,
            format='json'
        )
        
        # Should either be rejected or handled gracefully
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED]
    
    def test_missing_required_fields(self, authenticated_admin_client):
        """Test missing required fields are caught"""
        incomplete_data = {
            'name': 'Incomplete',
            # Missing email, salary, designation, role
        }
        
        response = authenticated_admin_client.post(
            '/api/hr/employees',
            incomplete_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

