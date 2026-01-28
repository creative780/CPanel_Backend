# Behavior Monitoring System - Manual Testing Guide

## Prerequisites

- Admin user account with access to Activity Logs page
- Browser with DevTools access (F12)
- Backend server running
- Database with test data (or ability to create test events)

## Test Scenarios

### Scenario 1: Failed Login Attempts

**Objective**: Verify that failed login attempts are detected and displayed correctly.

**Steps**:
1. Open browser DevTools (F12) → Console tab
2. Navigate to Activity Logs page (`/admin/activity-logs`)
3. Click on "Behavior Monitoring" tab
4. Open a new incognito/private window or use a different browser
5. Navigate to login page
6. Attempt to login with incorrect credentials (wrong password)
7. Check backend logs for message: `"Successfully logged failed login attempt"`
8. Return to Activity Logs page → Behavior Monitoring tab
9. Refresh the page or wait for auto-refresh
10. Check browser console for logs:
    - `"Fetching behavior monitoring data..."`
    - `"Behavior monitoring data received:"`
    - `"Failed logins count: X"` (where X > 0)
    - `"Failed logins:"` (should show array with failed login data)

**Expected Results**:
- Failed login appears in "Failed Login Attempts" table
- Table shows:
  - Username (the attempted username)
  - IP Address
  - Device information
  - Timestamp (formatted date/time)
  - Count (number of attempts from same username+IP)
- Summary card at top shows count of failed logins

**Verification Points**:
- [ ] Failed login event is created in database
- [ ] Backend logs show successful logging
- [ ] Frontend console shows data received
- [ ] Failed login appears in table
- [ ] All fields are populated correctly
- [ ] Multiple attempts from same username+IP are grouped and counted

---

### Scenario 2: Suspicious Logins

**Objective**: Verify detection of multiple logins from different locations within short time.

**Steps**:
1. Create test scenario (requires backend access or API):
   - Same user logs in from 3+ different IP addresses
   - All logins occur within 1 hour window
   - Each login should have different IP in context
2. Navigate to Behavior Monitoring tab
3. Check "Suspicious Logins" section

**Expected Results**:
- Suspicious login card appears in summary section
- Detailed card shows:
  - Username
  - Login count (e.g., "3 logins in 1 hour")
  - Unique IPs list
  - Unique locations (if available)
  - First login timestamp

**Verification Points**:
- [ ] Suspicious login is detected
- [ ] Unique IPs are listed correctly
- [ ] Login count is accurate
- [ ] Time window is displayed
- [ ] User is only flagged once (no duplicates)

---

### Scenario 3: Unauthorized Access

**Objective**: Verify detection of unauthorized access attempts and failed exports.

**Steps**:
1. Create test events (via API or backend):
   - Event with `context.status_code=403`
   - Event with error message containing "unauthorized"
   - Event with error message containing "forbidden"
   - Event with error message containing "access denied"
   - Failed export event (`verb="EXPORT"`, `context.status="failed"`)
2. Navigate to Behavior Monitoring tab
3. Check "Unauthorized Access" section

**Expected Results**:
- Unauthorized access appears in table
- Table shows:
  - User who attempted access
  - Action type
  - Target (resource attempted)
  - IP Address
  - Timestamp
  - Error message

**Verification Points**:
- [ ] All unauthorized access types are detected
- [ ] Error messages are displayed
- [ ] Failed exports are included
- [ ] All fields are populated

---

### Scenario 4: High-Risk Edits

**Objective**: Verify detection of frequent edits to sensitive records.

**Steps**:
1. Create test scenario:
   - Multiple UPDATE or DELETE events on:
     - Payroll records
     - Salary records
     - Financial records
     - Bank records
     - Payment records
   - At least 4 edits within 1 hour on same target
2. Navigate to Behavior Monitoring tab
3. Check "High-Risk Edits" section

**Expected Results**:
- High-risk edits appear in table
- Table shows:
  - Username
  - Target (e.g., "Payroll:payroll1")
  - Edit count
  - Time window (1 hour)
  - Severity badge (Medium or High)
    - High: 6+ edits
    - Medium: 4-5 edits

**Verification Points**:
- [ ] High-risk edits are detected
- [ ] Edit count is accurate
- [ ] Severity is classified correctly
- [ ] Only one entry per target (no duplicates)
- [ ] Time window is correct

---

### Scenario 5: Inactive User Access

**Objective**: Verify detection of login attempts from inactive user accounts.

**Steps**:
1. Deactivate a user account (set `is_active=False` in database or via admin)
2. Attempt to login with that user's credentials
3. Navigate to Behavior Monitoring tab
4. Check "Inactive Users" section

**Expected Results**:
- Inactive user access appears in table
- Table shows:
  - Username
  - IP Address
  - Device
  - Timestamp
  - Attempt count

**Verification Points**:
- [ ] Inactive user access is detected
- [ ] All fields are populated
- [ ] Attempt count is accurate

---

### Scenario 6: Date Range Filtering

**Objective**: Verify that date range filters work correctly.

**Steps**:
1. Navigate to Activity Logs page
2. Set date range filter:
   - From Date: 7 days ago
   - To Date: Today
3. Switch to Behavior Monitoring tab
4. Verify only events within date range are shown
5. Change date range to last 30 days
6. Verify more events appear (if they exist)

**Expected Results**:
- Only events within selected date range are displayed
- Changing date range updates the results
- Events outside date range are excluded

**Verification Points**:
- [ ] Date range filter is applied
- [ ] Events outside range are excluded
- [ ] Events within range are included
- [ ] Filter persists when switching tabs

---

### Scenario 7: Error Handling

**Objective**: Verify error handling and user feedback.

**Steps**:
1. Navigate to Behavior Monitoring tab
2. Disconnect network (or block API requests)
3. Verify error message is displayed
4. Reconnect network
5. Click "Retry" button
6. Verify data loads successfully

**Expected Results**:
- Error message is displayed when request fails
- Error message is user-friendly
- Retry button is functional
- Loading states are shown during fetch

**Verification Points**:
- [ ] Error message appears on failure
- [ ] Retry button works
- [ ] Loading spinner appears during fetch
- [ ] Error state is cleared on success

---

### Scenario 8: Empty States

**Objective**: Verify behavior when no data is available.

**Steps**:
1. Navigate to Behavior Monitoring tab with no matching events
2. Verify empty states are displayed correctly

**Expected Results**:
- Summary cards show "0" for each category
- Tables show "No [category] found" messages
- No errors are displayed

**Verification Points**:
- [ ] Empty states are handled gracefully
- [ ] No errors or exceptions
- [ ] UI is still functional

---

### Scenario 9: Permission Testing

**Objective**: Verify that only admin users can access Behavior Monitoring.

**Steps**:
1. Log in as non-admin user (e.g., sales, designer)
2. Navigate to Activity Logs page
3. Verify Behavior Monitoring tab is not visible or accessible
4. Try to access API directly (if possible)
5. Verify 403 Forbidden response

**Expected Results**:
- Non-admin users cannot access Behavior Monitoring
- API returns 403 Forbidden for non-admin users
- Admin users can access all features

**Verification Points**:
- [ ] Non-admin users are restricted
- [ ] Admin users have full access
- [ ] Permission checks work correctly

---

## Integration Testing

### Test API Endpoint Directly

**Using curl**:

```bash
# 1. Get admin token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password","role":"admin"}'

# Response will include access token:
# {"access": "eyJ0eXAiOiJKV1QiLCJhbGc...", ...}

# 2. Test behavior monitoring endpoint
curl -X GET "http://localhost:8000/api/activity-logs/behavior-monitoring" \
  -H "Authorization: Bearer <access_token_from_step_1>"

# 3. Test with date range filter
curl -X GET "http://localhost:8000/api/activity-logs/behavior-monitoring?since=2025-01-01T00:00:00Z&until=2025-01-31T23:59:59Z" \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response Structure**:
```json
{
  "failed_logins": [
    {
      "id": "uuid",
      "username": "testuser",
      "ip_address": "192.168.1.1",
      "device": "Test Device",
      "timestamp": "2025-01-20T10:30:00Z",
      "count": 2
    }
  ],
  "suspicious_logins": [...],
  "unauthorized_access": [...],
  "high_risk_edits": [...],
  "inactive_users": [...]
}
```

**Verification Points**:
- [ ] All 5 categories are present in response
- [ ] Timestamps are ISO format strings
- [ ] All required fields are present
- [ ] Response is valid JSON
- [ ] Status code is 200

---

## Performance Testing

### Test with Large Dataset

**Steps**:
1. Create 1000+ activity events (mix of all types)
2. Navigate to Behavior Monitoring tab
3. Measure:
   - Time to load data
   - Browser memory usage
   - API response time

**Expected Results**:
- Page loads within reasonable time (< 5 seconds)
- Memory usage is acceptable
- API response time is reasonable (< 3 seconds)
- No browser freezing or crashes

**Verification Points**:
- [ ] Performance is acceptable with large dataset
- [ ] Limits are enforced (200 events per category)
- [ ] No memory leaks
- [ ] UI remains responsive

---

## Edge Cases

### Test Edge Cases

1. **Empty Database**:
   - Verify all categories return empty arrays
   - Verify no errors are thrown

2. **Missing Context Fields**:
   - Create events with missing context fields
   - Verify system handles gracefully with defaults

3. **Null/None Values**:
   - Create events with null values in context
   - Verify system handles null values correctly

4. **Very Old Events**:
   - Create events from months/years ago
   - Verify date filtering excludes them correctly

5. **Malformed JSON**:
   - Verify system handles malformed context gracefully

---

## Troubleshooting

### Common Issues

1. **Failed logins not appearing**:
   - Check backend logs for "Successfully logged failed login attempt"
   - Verify event was created in database
   - Check date range filters
   - Verify RBAC is not filtering out events

2. **API returns 403**:
   - Verify user has admin role
   - Check IsAdmin permission is working
   - Verify JWT token is valid

3. **Empty results**:
   - Check date range filters
   - Verify events exist in database
   - Check RBAC filtering
   - Verify query conditions match event data

4. **Performance issues**:
   - Check database indexes
   - Verify query limits are applied
   - Check network latency
   - Review backend logs for slow queries

---

## Test Checklist

Use this checklist to ensure all scenarios are tested:

- [ ] Scenario 1: Failed Login Attempts
- [ ] Scenario 2: Suspicious Logins
- [ ] Scenario 3: Unauthorized Access
- [ ] Scenario 4: High-Risk Edits
- [ ] Scenario 5: Inactive User Access
- [ ] Scenario 6: Date Range Filtering
- [ ] Scenario 7: Error Handling
- [ ] Scenario 8: Empty States
- [ ] Scenario 9: Permission Testing
- [ ] Integration Testing (API)
- [ ] Performance Testing
- [ ] Edge Cases

---

## Notes

- All timestamps should be in ISO 8601 format
- Date range filters use `since` and `until` query parameters
- Failed logins are grouped by username+IP combination
- Suspicious logins require 3+ unique IPs within 1 hour
- High-risk edits require 4+ edits within 1 hour
- All tests should be performed with admin user account




