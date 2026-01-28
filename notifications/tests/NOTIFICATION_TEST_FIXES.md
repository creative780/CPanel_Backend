# Notification Test Fixes

## Issues Fixed

### 1. URL Routing Conflicts (405 Method Not Allowed)

**Problem**: Tests calling GET `/api/notifications/{id}/` were getting 405 errors because the ViewSet's retrieve action wasn't accessible due to URL routing conflicts.

**Solution**: 
- The ViewSet now properly handles GET requests via `retrieve` method
- URL routing has been updated to prioritize ViewSet routes for detail views
- The ViewSet supports both GET (retrieve) and PATCH (partial_update) on `/api/notifications/{id}/`

### 2. Permission Logic - Approval/Rejection Notifications

**Problem**: Admins were seeing approval/rejection notifications that should only be visible to the requester.

**Solution**: 
- Updated `get_notification_queryset()` to properly exclude approval/rejection notifications from admin views
- Admins only see their own notifications plus request notifications (leave_requested, design_submitted)
- Approval/rejection notifications are only visible to the recipient (the requester)

### 3. Mark as Unread Functionality

**Problem**: The `MarkReadView` was hardcoded to only set `is_read=True`, preventing marking notifications as unread.

**Solution**: 
- Updated `MarkReadView` to accept any `is_read` value (True or False)
- The ViewSet's `partial_update` also supports updating `is_read` to any value

## URL Patterns

### Current URL Structure:
- `GET /api/notifications/` → `NotificationListView` (list with filtering)
- `GET /api/notifications/{id}/` → `NotificationViewSet.retrieve()` (detail view)
- `PATCH /api/notifications/{id}/` → `NotificationViewSet.partial_update()` (update, e.g., mark read/unread)
- `GET /api/notifications/unread-count/` → `UnreadCountView` (unread count)
- `PATCH /api/notifications/{id}/mark-read/` → `MarkReadView` (legacy endpoint, optional)

## Test Updates Required

Tests should use:
- **GET detail**: `/api/notifications/{id}/` (ViewSet retrieve)
- **PATCH update**: `/api/notifications/{id}/` (ViewSet partial_update)
- **List**: `/api/notifications/` (NotificationListView)
- **Unread count**: `/api/notifications/unread-count/` (UnreadCountView)

## Permission Rules

1. **Employees**: See only their own notifications
2. **Admins**: See their own notifications + all request notifications (leave_requested, design_submitted)
3. **Approval/Rejection**: Only visible to the requester (not to admins unless they are the requester)

