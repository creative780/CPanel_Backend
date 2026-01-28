# HR Module Test Suite

Comprehensive test suite for the HR Employee Management system covering security, OTP system, employee management, and verification workflows.

## Test Files

### 1. `test_security_and_permissions.py`
Tests for security and authorization:
- Employee creation access control (admin vs employee)
- Employee list access control
- Permission class verification
- Employee detail access control

**Key Test Cases:**
- Test Case 1.1.1: Admin Can Create Employee
- Test Case 1.1.2: Employee Cannot Create Employee
- Test Case 1.2.1: Admin Can See All Employees
- Test Case 1.2.2: Employee Can Only See Own Record
- Test Case 1.3.1: Verify get_permissions() Method Works

### 2. `test_otp_system.py`
Tests for OTP (One-Time Password) system:
- OTP email sending (SMTP and console backend)
- OTP verification (valid, expired, invalid, used)
- Rate limiting functionality
- Reference OTP testing

**Key Test Cases:**
- Test Case 2.1.1: Send OTP with SMTP Backend
- Test Case 2.1.2: Send OTP with Console Backend
- Test Case 2.1.5: OTP Rate Limiting
- Test Case 2.2.1: Verify Valid OTP
- Test Case 2.2.2: Verify Expired OTP

### 3. `test_employee_management.py`
Tests for employee CRUD operations:
- Employee creation with validation
- Employee updates
- Employee deletion
- Duplicate email/username handling
- Field validation

**Key Test Cases:**
- Test Case 3.1.1: Create Employee (Full Flow)
- Test Case 3.1.3: Create Employee Duplicate Email
- Test Case 3.1.4: Create Employee Duplicate Username
- Test Case 3.1.5: Update Employee

## Documentation Files

### 1. `TEST_RESULTS_TEMPLATE.md`
Template for documenting test execution results. Use this to track:
- Test case status (Pass/Fail/Blocked)
- Notes and observations
- Screenshots
- Error details
- Issues found

### 2. `TEST_EXECUTION_GUIDE.md`
Step-by-step guide for:
- Setting up test environment
- Creating test users
- Running automated tests
- Manual testing procedures
- API testing with Postman
- Troubleshooting common issues

## Running Tests

### All Tests
```bash
cd CRM_BACKEND
pytest hr/tests/ -v
```

### Specific Test File
```bash
pytest hr/tests/test_security_and_permissions.py -v
```

### Specific Test Class
```bash
pytest hr/tests/test_security_and_permissions.py::TestEmployeeCreationAccessControl -v
```

### With Coverage
```bash
pytest hr/tests/ --cov=hr --cov-report=html --cov-report=term
```

### Specific Test Case
```bash
pytest hr/tests/test_security_and_permissions.py::TestEmployeeCreationAccessControl::test_1_1_1_admin_can_create_employee -v
```

## Test Categories

Tests are organized by markers and can be run selectively:

- **Unit Tests**: `pytest hr/tests/ -m unit`
- **Integration Tests**: `pytest hr/tests/ -m integration`
- **Security Tests**: `pytest hr/tests/ -k security`
- **OTP Tests**: `pytest hr/tests/test_otp_system.py`

## Test Data

Tests use Factory Boy factories from `tests.factories`:
- `AdminUserFactory` - Creates admin users
- `SalesUserFactory` - Creates sales employee users
- `HREmployeeFactory` - Creates HR employee records

## Fixtures

Common fixtures available:
- `authenticated_admin_client` - API client authenticated as admin
- `authenticated_employee_client` - API client authenticated as employee
- `authenticated_finance_client` - API client authenticated as finance user
- `employee_with_email` - Sample employee with email for OTP testing

## Prerequisites

1. **Django Backend Running**
   ```bash
   python manage.py runserver
   ```

2. **Test Database**
   - Tests use pytest-django which creates a test database
   - No manual database setup required

3. **Test Users**
   - Tests create users automatically using factories
   - Or use existing users if configured

## Coverage Goals

Target coverage:
- Security tests: 100%
- OTP system: 90%+
- Employee management: 85%+
- Overall: 80%+

## Continuous Integration

These tests should be run:
- Before every commit
- In CI/CD pipeline
- Before deployments
- After code changes

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Follow existing test patterns
3. Use factories for test data
4. Document test cases in plan
5. Update test results template

## Troubleshooting

### Common Issues

**Permission Denied Errors:**
- Verify user roles in fixtures
- Check authentication setup

**OTP Tests Failing:**
- Ensure email backend is configured
- Check cache is cleared between tests

**Database Errors:**
- Run migrations: `python manage.py migrate`
- Reset test database if needed

See `TEST_EXECUTION_GUIDE.md` for detailed troubleshooting.

## Test Plan Reference

These tests correspond to the test cases defined in:
- `fix-otp-system-critical-errors.plan.md`
- `EMPLOYEE_ACCESS_BUG_REPORT.md`

## Status

✅ Test files created
✅ Test fixtures configured
✅ Documentation provided
⬜ All tests passing
⬜ Coverage targets met
⬜ Manual testing completed

## Next Steps

1. Run all tests and verify they pass
2. Fill out test results template
3. Document any test failures
4. Create bug reports for failures
5. Update tests based on findings

