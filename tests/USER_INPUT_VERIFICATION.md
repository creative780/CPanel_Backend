# User Input Field Verification for Production Dashboard

This document verifies that all required user input fields are present in the UI to update production dashboard graphs.

## Required Fields by Metric

### 1. Jobs in WIP Count
**Status**: ✅ **PRESENT**
- **Fields**: 
  - Order status update: `status='sent_to_production'` or `status='getting_ready'`
  - Order stage update: `stage='printing'`
- **Location**: 
  - Order workflow endpoints (`/api/orders/{id}/`)
  - Production dashboard (`/admin/order-lifecycle/table/production`)
  - Order lifecycle page (`/admin/order-lifecycle`)

### 2. Average Turnaround Time
**Status**: ✅ **PRESENT**
- **Fields**:
  - Order delivery: `delivered_at` timestamp
  - Order status: `status='delivered'`
- **Location**:
  - Delivery endpoints (`/api/orders/{id}/`)
  - Delivery workflow (`/admin/order-lifecycle/table`)
  - Order lifecycle page (delivery stage)

### 3. Machine Utilization
**Status**: ✅ **PRESENT**
- **Fields**:
  - Machine assignment: `ProductMachineAssignment` creation
  - Assignment start: `started_at` timestamp (when status='in_progress')
  - Assignment completion: `completed_at` timestamp (when status='completed')
  - Estimated time: `estimated_time_minutes`
- **Location**:
  - Machine assignment endpoints (`/api/orders/{id}/assign-machines/`)
  - Production dashboard (`/admin/order-lifecycle/table/production`)
  - Machine assignment modal in production table

### 4. Reprint Rate
**Status**: ⚠️ **MISSING - NEEDS TO BE ADDED**
- **Fields**:
  - ⚠️ **MISSING**: User input field to mark order as reprint (`is_reprint`)
  - ⚠️ **MISSING**: User input field to link to original order (`original_order`)
- **Backend**: ✅ Fields exist in `Order` model
- **Frontend**: ❌ No UI fields in order creation/edit forms
- **Action Required**: Add checkbox and dropdown to order forms

### 5. Production Queue
**Status**: ✅ **PRESENT**
- **Fields**:
  - Machine assignment creation (same as utilization)
  - Assignment status updates
- **Location**:
  - Production dashboard (`/admin/order-lifecycle/table/production`)
  - Machine assignment modal

### 6. Jobs by Stage
**Status**: ✅ **PRESENT**
- **Fields**:
  - Machine assignment with machine names
  - Assignment status updates
- **Location**:
  - Production dashboard (`/admin/order-lifecycle/table/production`)
  - Machine assignment modal

### 7. Material Usage
**Status**: ✅ **PRESENT**
- **Fields**:
  - Inventory movement creation: `InventoryMovement` with negative delta
  - Inventory item creation: `InventoryItem` with `minimum_stock`
- **Location**:
  - Inventory management endpoints (`/api/inventory/`)
  - Order completion (should auto-create movements)

### 8. Delivery Handoff
**Status**: ✅ **PRESENT**
- **Fields**:
  - Order status: `status='sent_for_delivery'` (auto-set when all assignments complete)
  - Delivery code: `delivery_code` field
- **Location**:
  - Order completion (auto-set via signals)
  - Delivery workflow (`/admin/order-lifecycle/table`)
  - Order lifecycle page (delivery stage)

## Summary

- **Present**: 7 out of 8 metrics have all required user input fields
- **Missing**: Reprint Rate metric needs UI fields added
- **Action Items**:
  1. Add `is_reprint` checkbox to order creation/edit forms
  2. Add `original_order` dropdown to order creation/edit forms
  3. Update order API to accept these fields
  4. Test reprint rate updates when fields are used

## Files to Update

1. **Frontend Order Form**: `CRM_FRONTEND/app/components/order-stages/OrderIntakeForm.tsx`
   - Add checkbox for "Is Reprint"
   - Add dropdown for "Original Order" (filtered to delivered orders)

2. **Frontend Order Type**: `CRM_FRONTEND/app/stores/useOrderStore.ts`
   - Add `is_reprint?: boolean` and `original_order?: number` to `SharedFormData`

3. **Backend API**: Already supports these fields via `Order` model
   - Verify order creation/update endpoints accept these fields



























