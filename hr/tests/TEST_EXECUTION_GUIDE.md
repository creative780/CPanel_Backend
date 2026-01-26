# Test Execution Guide

This guide provides step-by-step instructions for executing the comprehensive test suite for the HR Employee Management system.

## Prerequisites

### 1. Environment Setup

1. **Backend Server**
   ```bash
   cd CRM_BACKEND
   python manage.py runserver
   ```

2. **Frontend Server**
   ```bash
   cd CRM_FRONTEND
   npm run dev
   ```

3. **Database Setup**
   ```bash
   cd CRM_BACKEND
   python manage.py migrate
   python manage.py createsuperuser  # Create admin user
   ```

### 2. Test Users

Create test users for different roles:

**Option A: Use Django Admin**
1. Navigate to `http://localhost:8000/admin`
2. Create users with roles: admin, sales, designer, finance

**Option B: Use Django Shell**
```python
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from accounts.models import Role

User = get_user_model()

# Create admin user
admin = User.objects.create_user(
    username='admin_test',
    email='admin@test.com',
    password='testpass123',
    roles=[Role.ADMIN],
    is_staff=True
)

# Create employee user
employee = User.objects.create_user(
    username='employee_test',
    email='employee@test.com',
    password='testpass123',
    roles=[Role.SALES]
)

# Create finance user
finance = User.objects.create_user(
    username='finance_test',
    email='finance@test.com',
    password='testpass123',
    roles=[Role.FINANCE]
)
```

### 3. Email Configuration

**For Testing with Console Backend (Development)**
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEBUG=True
```

**For Testing with SMTP (Production-like)**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

## Running Automated Tests

### Quick Start (Windows PowerShell)

**Option 1: Use the helper script (Recommended)**
```powershell
cd CRM_BACKEND
.\run_tests.ps1
```

**Option 2: Use Python module directly**
```powershell
cd CRM_BACKEND
python -m pytest hr/tests/ -v
```

**Option 3: Install dependencies first**
```powershell
cd CRM_BACKEND
pip install -r requirements.txt
python -m pytest hr/tests/ -v
```

### Unit Tests with Pytest

```bash
cd CRM_BACKEND

# Run all HR tests (Windows - use python -m pytest)
python -m pytest hr/tests/ -v

# Or if pytest is in PATH:
pytest hr/tests/ -v

# Run specific test file
python -m pytest hr/tests/test_security_and_permissions.py -v

# Run specific test class
pytest hr/tests/test_security_and_permissions.py::TestEmployeeCreationAccessControl -v

# Run specific test
pytest hr/tests/test_security_and_permissions.py::TestEmployeeCreationAccessControl::test_1_1_1_admin_can_create_employee -v

# Run with coverage
pytest hr/tests/ --cov=hr --cov-report=html --cov-report=term
```

### Test Categories

```bash
# Run only security tests
pytest hr/tests/ -m "unit" -k "security" -v

# Run only OTP tests
pytest hr/tests/test_otp_system.py -v

# Run only employee management tests
pytest hr/tests/test_employee_management.py -v
```

## Manual Testing Checklist

### 1. Security & Authorization Testing

#### Test Case 1.1.1: Admin Can Create Employee

**Steps:**
1. Log in as admin user in frontend
2. Navigate to `/admin/hr/employee-management`
3. Click "Add Employee" button
4. Fill in all required fields:
   - Name: Test Employee
   - Email: test@example.com
   - Salary: 5000
   - Designation: Software Engineer
   - Role: sales
   - Branch: dubai
   - Username: testuser
   - Password: testpass123
5. Click "Save" or "Submit"

**Expected:** Employee created successfully, success message displayed

**OR via API:**
```bash
curl -X POST http://localhost:8000/api/hr/employees \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Employee",
    "email": "test@example.com",
    "salary": "5000.00",
    "designation": "Software Engineer",
    "status": "Active",
    "role": "sales",
    "branch": "dubai",
    "username": "testuser",
    "password": "testpass123"
  }'
```

#### Test Case 1.1.2: Employee Cannot Create Employee

**Steps:**
1. Log in as regular employee (non-admin)
2. Attempt to access `/admin/hr/employee-management`
3. Check if "Add Employee" button is visible

**Expected:** Button should NOT be visible

**OR via API:**
```bash
curl -X POST http://localhost:8000/api/hr/employees \
  -H "Authorization: Bearer <employee_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Unauthorized Employee",
    "email": "unauthorized@example.com",
    ...
  }'
```

**Expected:** 403 Forbidden response

### 2. OTP System Testing

#### Test Case 2.1.1: Send OTP with SMTP Backend

**Prerequisites:** SMTP configured in .env

**Steps:**
1. Log in as admin or employee
2. Navigate to employee verification page
3. Open verification wizard
4. Navigate to phone verification step
5. Click "Send OTP" button
6. Enter email address (if prompted)
7. Click "Send"

**Expected:**
- Success message displayed
- OTP received in email inbox
- OTP code is 6 digits

#### Test Case 2.1.2: Send OTP with Console Backend

**Prerequisites:** Console backend configured, DEBUG=True

**Steps:**
1. Same as above

**Expected:**
- Error message about console backend
- OTP code displayed in error message (DEBUG mode only)
- OTP printed in Django console output

### 3. Frontend UI Testing

#### Test Case 5.1.1: Page Loads for Admin

**Steps:**
1. Log in as admin
2. Navigate to `/admin/hr/employee-management`
3. Check if page loads

**Expected:** Page loads with employee list

#### Test Case 5.1.2: Add Employee Modal Opens

**Steps:**
1. Click "Add Employee" button
2. Check if modal opens

**Expected:** Modal opens with form fields

## API Testing with Postman

### Collection Setup

1. **Environment Variables**
   - `base_url`: `http://localhost:8000`
   - `admin_token`: (Get from login)
   - `employee_token`: (Get from login)

2. **Get Admin Token**
   ```
   POST {{base_url}}/api/auth/login
   Body:
   {
     "username": "admin_test",
     "password": "testpass123",
     "role": "admin"
   }
   ```

3. **Save Token**
   - Copy token from response
   - Set as `admin_token` in environment

### Test Requests

**Create Employee (Admin Only)**
```
POST {{base_url}}/api/hr/employees
Headers:
  Authorization: Bearer {{admin_token}}
  Content-Type: application/json
Body: { ... employee data ... }
```

**List Employees (Admin)**
```
GET {{base_url}}/api/hr/employees
Headers:
  Authorization: Bearer {{admin_token}}
```

**Send OTP**
```
POST {{base_url}}/api/hr/employees/1/send-phone-otp
Headers:
  Authorization: Bearer {{admin_token}}
Body:
{
  "email": "employee@example.com"
}
```

## Troubleshooting

### Common Issues

1. **Tests Failing: Permission Denied**
   - Check if test user has correct role
   - Verify authentication in test fixtures

2. **OTP Not Sending**
   - Check email backend configuration
   - Verify SMTP credentials
   - Check Django console for errors

3. **Rate Limiting Issues**
   - Clear rate limit cache:
     ```python
     from django.core.cache import cache
     cache.delete('otp_rate_limit:EMPLOYEE_ID')
     ```

4. **Database Errors**
   - Run migrations: `python manage.py migrate`
   - Reset test database if needed

## Test Results Documentation

After completing tests, fill out the `TEST_RESULTS_TEMPLATE.md` file with:
- Test case status (Pass/Fail/Blocked)
- Notes and observations
- Screenshots
- Error details

## Performance Testing

### Load Testing

```bash
# Using Apache Bench
ab -n 100 -c 10 -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/hr/employees

# Using curl for rate limit testing
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/hr/employees/1/send-phone-otp \
    -H "Authorization: Bearer TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com"}'
  echo "Request $i completed"
done
```

## Security Testing Tools

### SQL Injection Testing
```bash
# Test with SQL injection payload
curl -X GET "http://localhost:8000/api/hr/employees?search=' OR '1'='1" \
  -H "Authorization: Bearer TOKEN"
```

### XSS Testing
```bash
# Test with XSS payload
curl -X POST http://localhost:8000/api/hr/employees \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name": "<script>alert(1)</script>"}'
```

## Reporting Issues

When reporting test failures:

1. **Include Test Case ID** (e.g., 1.1.1)
2. **Describe Steps to Reproduce**
3. **Expected vs Actual Results**
4. **Screenshots/Logs**
5. **Environment Details**

## Next Steps

After completing all tests:

1. Review test results
2. Document critical issues
3. Create bug reports for failures
4. Update test cases if needed
5. Re-test after fixes

