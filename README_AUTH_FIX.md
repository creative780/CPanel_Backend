# Authentication Fix for Frontend API Access

## Problem
The frontend was getting HTTP 401 errors when accessing `/api/show_nav_items/` endpoint.

## Root Cause
The `ShowNavItemsAPIView` uses `FrontendOnlyPermission` which checks for the `X-Frontend-Key` header. When this header doesn't match or is missing, the permission class returns `False`, causing DRF to return a 401 error.

## Solution
Updated `FrontendOnlyPermission` to:
1. **Allow access if `FRONTEND_KEY` environment variable is not set** (development mode)
2. **Check headers in multiple formats** (case-insensitive, both `request.headers` and `request.META`)
3. **Strip whitespace** from both the header value and the expected key

## Configuration

### Backend (.env file)
Add to `CPanel_Backend/.env`:
```env
FRONTEND_KEY=your-secret-key-here
```

### Frontend (.env.local file)
Add to `CPanel_FrontEnd/.env.local`:
```env
NEXT_PUBLIC_FRONTEND_KEY=your-secret-key-here
```

**Important:** Both values must match exactly!

## Development Mode
If `FRONTEND_KEY` is not set in the backend, the permission class will allow all requests (useful for development).

## Testing
After setting the environment variables, restart both:
- Backend: `python manage.py runserver`
- Frontend: `npm run dev`

The `/api/show_nav_items/` endpoint should now work without authentication errors.

