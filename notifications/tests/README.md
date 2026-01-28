# Notification System Test Suite

## Overview

This directory contains comprehensive tests for the notification system covering:

1. **Backend API Tests** - CRUD operations, filtering, permissions
2. **Service Function Tests** - `create_notification`, `notify_admins`
3. **Model Tests** - Model creation, ordering, string representation
4. **Serializer Tests** - Serializer output and validation
5. **Unread Count Tests** - Accurate counting and updates
6. **Permission Tests** - Role-based visibility (admin vs employee)
7. **WebSocket Tests** - Real-time notification delivery (requires async testing)
8. **Signal Tests** - WebSocket event triggering
9. **Celery Task Tests** - Automated notification generation

## Test Files

### Core Tests

- `test_api_endpoints.py` - API endpoint tests (CRUD, filtering, permissions)
- `test_services.py` - Service function tests
- `test_model.py` - Model tests
- `test_serializers.py` - Serializer tests
- `test_unread_count.py` - Unread count accuracy tests

### Fixtures

- `conftest.py` - Shared fixtures for all tests

## Running Tests

### Run All Notification Tests

```bash
cd CRM_BACKEND
python -m pytest notifications/tests/ -v
```

### Run Specific Test File

```bash
python -m pytest notifications/tests/test_api_endpoints.py -v
python -m pytest notifications/tests/test_services.py -v
```

### Run Specific Test Case

```bash
python -m pytest notifications/tests/test_api_endpoints.py::TestNotificationCRUD::test_1_1_1_list_notifications -v
```

### Run with Coverage

```bash
python -m pytest notifications/tests/ --cov=notifications --cov-report=html
```

## Test Categories

### 1. API Endpoint Tests (`test_api_endpoints.py`)

- **Test Case 1.1**: Notification CRUD Operations
  - List notifications
  - Filter by read status
  - Get notification detail
  - Mark as read/unread
  - Get unread count
  - Notification limit (50 most recent)

- **Test Case 1.2**: Permission and Access Control
  - Employee sees only own notifications
  - Admin sees own + request notifications
  - Admin does NOT see approval/rejection notifications of others
  - Unauthenticated user cannot access

- **Test Case 1.3**: Notification Types
  - Order notifications
  - Leave notifications (requested, approved, rejected)
  - Design notifications (submitted, approved, rejected)
  - Delivery notifications
  - Monitoring notifications

### 2. Service Function Tests (`test_services.py`)

- **Test Case 1.4**: Service Functions
  - `create_notification()` with all parameters
  - `create_notification()` with optional fields
  - `notify_admins()` creates notifications for all admins
  - Edge case handling

### 3. Model Tests (`test_model.py`)

- Model creation with required fields
- Model creation with optional fields
- String representation
- Model ordering (newest first)
- Default values

### 4. Serializer Tests (`test_serializers.py`)

- **Test Case 12**: Serializer Testing
  - NotificationListSerializer fields
  - NotificationDetailSerializer fields
  - NotificationUpdateSerializer validation
  - Actor name serialization
  - Null actor handling

### 5. Unread Count Tests (`test_unread_count.py`)

- **Test Case 9**: Unread Count Is Accurate
  - Excludes read notifications
  - Includes only own notifications (for employees)
  - Includes own + request notifications (for admins)
  - Updates when marked as read
  - Accurate after creating new notifications

## Fixtures

Shared fixtures in `conftest.py`:

- `admin_user` - Admin user instance
- `sales_user` - Sales user (employee) instance
- `employee_user` - Alias for sales_user
- `designer_user` - Designer user instance
- `finance_user` - Finance user instance
- `api_client` - Unauthenticated API client

## Test Environment Setup

### Prerequisites

1. **Backend server** running (`python manage.py runserver`)
2. **Test database** configured
3. **Redis server** running (for WebSocket tests - if implemented)
4. **Celery worker** running (for task tests - if implemented)

### Running with Docker

If using Docker, ensure all services are running:

```bash
docker-compose up -d
```

## Known Limitations

1. **WebSocket Tests** - Currently not implemented as they require async testing infrastructure
2. **Signal Tests** - Currently not implemented as they require channel layer configuration
3. **Celery Task Tests** - Currently not implemented as they require Celery test setup
4. **Integration Tests** - Currently not implemented, covered by existing `tests.py` file

## Future Enhancements

- Add WebSocket integration tests
- Add signal tests with channel layer mocking
- Add Celery task tests
- Add performance tests (load testing)
- Add security tests (SQL injection, XSS)
- Add error handling tests
- Add edge case tests

## Test Results

Run tests and check results:

```bash
python -m pytest notifications/tests/ -v --tb=short
```

## Coverage Goals

Target coverage for notification system:
- API endpoints: 90%+
- Service functions: 95%+
- Models: 100%
- Serializers: 90%+

## Notes

- All tests use `@pytest.mark.django_db` to ensure database access
- Tests are organized by test case categories matching the comprehensive testing plan
- Test IDs follow the pattern `test_{category}_{number}_{description}` for easy reference

