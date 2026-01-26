# Notification System Test Fixes Applied

## Issues Fixed

### 1. Import Errors ✅

#### Fixed `RiderPhoto` Import Error
- **File**: `CRM_BACKEND/tests/factories.py`
- **Issue**: Trying to import `RiderPhoto` which doesn't exist in `delivery.models`
- **Fix**: Removed `RiderPhoto` from import statement
- **Changed**: `from delivery.models import DeliveryCode, RiderPhoto`
- **To**: `from delivery.models import DeliveryCode`

#### Fixed `InventoryMovement` Import Error
- **File**: `CRM_BACKEND/tests/factories.py`
- **Issue**: `InventoryMovementFactory` uses `InventoryMovement` but it wasn't imported
- **Fix**: Added `InventoryMovement` to import statement
- **Changed**: `from inventory.models import InventoryItem`
- **To**: `from inventory.models import InventoryItem, InventoryMovement`

### 2. `notify_admins` Function Fix ✅

- **File**: `CRM_BACKEND/notifications/services.py`
- **Issue**: Using `roles__contains=['admin']` which is not supported for JSONField
- **Error**: `django.db.utils.NotSupportedError: contains lookup...`
- **Fix**: Changed to filter manually using `has_role()` method
- **Changed**:
  ```python
  admins = User.objects.filter(roles__contains=['admin'])
  ```
- **To**:
  ```python
  all_users = User.objects.all()
  admins = [user for user in all_users if user.has_role('admin')]
  ```

### 3. URL Routing Fix ✅

- **File**: `CRM_BACKEND/notifications/urls.py`
- **Issue**: Router URLs were matching before direct paths, causing 404s for `/api/notifications/unread-count/`
- **Fix**: Reordered URL patterns to put specific routes before router
- **Changed**: Router included first
- **To**: Direct paths (unread-count, list, mark-read) come before router

### 4. URL Path Fixes in Tests ✅

- **Files**: 
  - `CRM_BACKEND/notifications/tests/test_api_endpoints.py`
  - `CRM_BACKEND/notifications/tests/test_unread_count.py`
- **Issue**: Tests using wrong URL path
- **Fix**: Changed from `/api/notifications/notifications/unread-count/` back to `/api/notifications/unread-count/` (after URL reordering fix)

### 5. Redis Connection Errors (Expected) ⚠️

- **Issue**: Redis connection errors when Redis is not running
- **Status**: These are expected and handled gracefully
- **Behavior**: Signal logs error but doesn't crash - notifications still created successfully
- **Note**: For full functionality, Redis should be running, but tests can run without it

## Remaining Test Failures to Address

### 1. Filter Tests (test_1_1_2, test_1_1_3)
- **Issue**: Filtering by `is_read` parameter not working as expected
- **Possible Cause**: Tests hitting ViewSet endpoint which may not support query params
- **Status**: Needs investigation - check if ViewSet supports filtering

### 2. Notification Limit Test (test_1_1_8)
- **Issue**: Expected 50 notifications but got 60
- **Possible Cause**: Limit not being applied correctly
- **Status**: Needs investigation - check limit implementation

### 3. Admin Visibility Tests (test_1_3_4, test_1_3_5)
- **Issue**: Approval/rejection notifications visible to admin when they shouldn't be
- **Possible Cause**: Permission logic issue
- **Status**: Needs investigation - check `get_notification_queryset` function

## Next Steps

1. ✅ Fix import errors - **COMPLETED**
2. ✅ Fix `notify_admins` function - **COMPLETED**
3. ✅ Fix URL routing - **COMPLETED**
4. ⚠️ Fix filter query parameter handling
5. ⚠️ Fix notification limit
6. ⚠️ Fix admin visibility logic

## Testing

Run tests again:
```bash
cd CRM_BACKEND
python -m pytest notifications/tests/ -v
```

Most import and URL issues should be resolved. Remaining failures need code logic fixes.

