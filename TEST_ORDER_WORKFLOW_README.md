# Complete Order Lifecycle Workflow Test

This document describes how to run the automated test for the complete order lifecycle workflow.

## Overview

The test script (`test_complete_order_workflow.py`) automates the entire order workflow from creation through delivery:

1. **Sales**: Creates a custom order with products
2. **Sales**: Sends order to designer
3. **Designer**: Uploads design files and requests approval
4. **Sales**: Approves the design
5. **Designer**: Sends approved order to production
6. **Production**: Assigns machines and estimated time to each product
7. **Production**: Marks all machine assignments as complete (triggers auto-transition)
8. **Delivery**: Generates delivery code, uploads photo, and marks order delivered

## Prerequisites

1. **Backend Server Running**
   ```bash
   cd Backend
   python manage.py runserver
   ```

2. **Create Test Users**
   The script will automatically create test users if they don't exist, but you can also use the management command:
   ```bash
   python manage.py setup_test_users
   ```
   
   This creates:
   - `sales@test.com` / `sales123` (sales role)
   - `designer@test.com` / `designer123` (designer role)
   - `production@test.com` / `production123` (production role)
   - `delivery@test.com` / `delivery123` (delivery role) - created by test script

## Running the Test

### Option 1: Direct Python Execution

```bash
cd Backend
python test_complete_order_workflow.py
```

### Option 2: With Custom API Base URL

```bash
cd Backend
API_BASE_URL=https://api.crm.click2print.store python test_complete_order_workflow.py
```

## Test Output

The script provides detailed output for each step:

```
======================================================================
COMPLETE ORDER LIFECYCLE WORKFLOW TEST
======================================================================

→ Creating test users...
✓ Created user: sales@test.com (role: sales)
✓ User already exists: designer@test.com (role: designer)
...

→ STEP 1: Sales creates custom order
✓ Logged in as sales@test.com (sales)
✓ Order created: ORD-ABC123 (ID: 1)
✓ Order status: draft (expected)

→ STEP 2: Sales sends order to designer
✓ Order sent to designer: sent_to_designer / design
✓ Order status verified: sent_to_designer / design

...

======================================================================
TEST SUMMARY
======================================================================
✓ PASS: Create Order
✓ PASS: Send to Designer
✓ PASS: Designer Requests Approval
✓ PASS: Sales Approves Design
✓ PASS: Designer Sends to Production
✓ PASS: Production Assigns Machines
✓ PASS: Mark Assignments Complete
✓ PASS: Delivery Completes Order

Total: 8/8 steps passed
```

## What Gets Tested

### API Endpoints Tested

1. `POST /api/orders/` - Create order
2. `POST /api/orders/{id}/send-to-designer/` - Send to designer
3. `POST /api/orders/{id}/files/upload/` - Upload files (simulated)
4. `POST /api/orders/{id}/request-approval/` - Request design approval
5. `POST /api/approvals/{id}/decision/` - Approve/reject design
6. `POST /api/orders/{id}/send-to-production/` - Send to production
7. `POST /api/orders/{id}/assign-machines/` - Assign machines
8. `PATCH /api/machine-assignments/{id}/status/` - Mark assignment complete
9. `POST /api/send-delivery-code` - Generate delivery code
10. `PATCH /api/orders/{id}/` - Update order status to delivered

## Automatic Status Transitions

The test verifies:

1. **Design Approval Signal**: When design is approved, order status should allow sending to production
2. **Machine Completion Signal**: When ALL machine assignments are completed, order automatically transitions to `sent_for_delivery` (from `Backend/orders/signals.py`)

## Troubleshooting

### Test Users Not Created

If you get authentication errors, manually create users:

```bash
python manage.py createsuperuser  # For admin
python manage.py setup_test_users  # For test roles
```

Then manually create delivery user:
```python
python manage.py shell
>>> from accounts.models import User
>>> User.objects.create_user('delivery@test.com', password='delivery123', roles=['delivery'])
```

### API Connection Issues

If you get connection errors:
- Verify backend is running: `curl http://127.0.0.1:8000/api/`
- Check API_BASE_URL environment variable
- Verify CORS settings allow requests

### Order Status Not Updating

If order statuses don't transition correctly:
- Check Django signals are registered (see `Backend/orders/signals.py`)
- Verify signal handlers are being called (check logs)
- Ensure all conditions for transitions are met

### Machine Assignments Not Completing

If assignments don't mark complete:
- Verify assignment IDs are correct
- Check that status field accepts 'completed' value
- Ensure all assignments for the order are marked complete (signal checks ALL)

## Test Data

The script uses the following test data:

**Client**: John's Printing Shop  
**Products**: 
- Business Card Gold (100 qty)
- Canvas Print A3 (5 qty)

**Machines**:
- HP Indigo Press 1 (60 min estimated)
- Roland Eco-Solvent Printer (120 min estimated)

## Manual Testing Checklist

For manual UI testing, follow the checklist in `fix-api-route-404.plan.md`:

1. [ ] Sales creates order via UI
2. [ ] Designer uploads files via UI
3. [ ] Sales reviews and approves via UI
4. [ ] Production assigns machines via UI
5. [ ] Mark assignments complete (via API or UI if available)
6. [ ] Delivery completes order via UI

## Notes

- File uploads are simulated in the API test (using manifest data)
- For complete testing, also test file uploads manually via UI
- Delivery photo upload is not fully automated (requires actual file)
- SMS delivery code sending depends on Twilio configuration


