# OTP Frontend Fixes Required

## Problem Summary
When clicking "Send OTP" button in the Verification Wizard, nothing happens. The frontend is still configured for SMS/Email dual mode, but the backend has been updated to **email-only**. This creates a mismatch causing silent failures.

---

## Issues Identified

### 1. **Frontend API Call Mismatch** (CRITICAL)
**Location**: `CRM_FRONTEND/lib/hr.ts` lines 69-74

**Problem**: 
- Frontend sends `delivery_method`, `phone_number`, and `email` in request body
- Backend `SendPhoneOTPView` only accepts optional `email` parameter
- Backend ignores `delivery_method` and `phone_number` completely

**Current Frontend Code**:
```typescript
async sendPhoneOTP(employeeId: number, deliveryMethod: 'sms' | 'email', phoneNumber?: string, email?: string): Promise<any> {
  return api.post(`/api/hr/employees/${employeeId}/send-phone-otp`, {
    delivery_method: deliveryMethod,  // ❌ Backend doesn't use this
    phone_number: phoneNumber,        // ❌ Backend doesn't use this
    email: email,                     // ✅ Only this is used (optional)
  });
}
```

**Backend Expects**:
```python
# Only accepts optional 'email' in request.data
email = request.data.get('email', employee.email)
```

**Fix Required**: Update `sendPhoneOTP` to only send `email` parameter (optional)

---

### 2. **SMS Option Still Visible in UI** (UI ISSUE)
**Location**: `CRM_FRONTEND/app/components/employee/VerificationWizard.tsx` lines 451-470

**Problem**:
- Radio buttons still show "SMS" and "Email" options
- SMS option should be removed entirely
- Users can select SMS but backend will fail silently

**Current Code**:
```typescript
<div className="flex gap-4 mt-2">
  <label className="flex items-center gap-2">
    <input
      type="radio"
      value="sms"  // ❌ Should be removed
      checked={otpDeliveryMethod === 'sms'}
      onChange={(e) => setOtpDeliveryMethod(e.target.value as 'sms' | 'email')}
    />
    SMS  // ❌ Should be removed
  </label>
  <label className="flex items-center gap-2">
    <input
      type="radio"
      value="email"
      checked={otpDeliveryMethod === 'email'}
      onChange={(e) => setOtpDeliveryMethod(e.target.value as 'sms' | 'email')}
    />
    Email
  </label>
</div>
```

**Fix Required**: 
- Remove SMS radio button
- Remove `otpDeliveryMethod` state (always use email)
- Simplify UI to just show "Send OTP" button

---

### 3. **Default State is SMS** (STATE ISSUE)
**Location**: `CRM_FRONTEND/app/components/employee/VerificationWizard.tsx` line 51

**Problem**:
- `otpDeliveryMethod` defaults to `'sms'`
- Should default to `'email'` or be removed entirely

**Current Code**:
```typescript
const [otpDeliveryMethod, setOtpDeliveryMethod] = useState<'sms' | 'email'>('sms'); // ❌
```

**Fix Required**: Change default to `'email'` or remove the state entirely

---

### 4. **Modal Title Still Says "Phone"** (UI ISSUE)
**Location**: `CRM_FRONTEND/app/components/employee/VerificationWizard.tsx` line 441

**Problem**:
- Modal title says "Verify Phone Number" 
- Should say "Verify Email" or "Verify Contact"

**Current Code**:
```typescript
<DialogTitle>
  {otpModal.type === 'phone' ? 'Verify Phone Number' : 'Verify Reference'}  // ❌
</DialogTitle>
```

**Fix Required**: Change to "Verify Email" or "Verify Contact Information"

---

### 5. **Reference OTP API Mismatch** (CRITICAL)
**Location**: `CRM_FRONTEND/lib/hr.ts` lines 83-86

**Problem**:
- Frontend still sends `delivery_method` for reference OTP
- Backend `SendReferenceOTPView` no longer accepts `delivery_method`

**Current Frontend Code**:
```typescript
async sendReferenceOTP(employeeId: number, referenceId: number, deliveryMethod: 'sms' | 'email'): Promise<any> {
  return api.post(`/api/hr/employees/${employeeId}/references/${referenceId}/send-otp`, {
    delivery_method: deliveryMethod,  // ❌ Backend doesn't use this
  });
}
```

**Backend Expects**:
```python
# Backend automatically uses reference.email - no delivery_method needed
email = reference.email
```

**Fix Required**: Remove `deliveryMethod` parameter from `sendReferenceOTP` function

---

### 6. **Error Handling May Be Silent** (DEBUGGING ISSUE)
**Location**: `CRM_FRONTEND/app/components/employee/VerificationWizard.tsx` lines 239-254

**Problem**:
- Errors are caught but may not show helpful messages
- Network errors might be swallowed
- Backend validation errors might not be displayed

**Current Code**:
```typescript
const handleSendOTP = async () => {
  try {
    setSendingOtp(true);
    if (otpModal?.type === 'phone') {
      await hrApi.sendPhoneOTP(employeeId, otpDeliveryMethod);  // ❌ Wrong parameters
      toast.success(`OTP sent via ${otpDeliveryMethod.toUpperCase()}`);
    } else if (otpModal?.type === 'reference' && otpModal.referenceId) {
      await hrApi.sendReferenceOTP(employeeId, otpModal.referenceId, otpDeliveryMethod);  // ❌ Wrong parameters
      toast.success(`OTP sent to reference via ${otpDeliveryMethod.toUpperCase()}`);
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to send OTP');  // ⚠️ May not show detailed errors
  } finally {
    setSendingOtp(false);
  }
};
```

**Fix Required**: 
- Update function calls to match new backend API
- Add better error logging
- Show more detailed error messages

---

### 7. **Type Definitions Still Include SMS** (TYPE SAFETY)
**Location**: `CRM_FRONTEND/lib/hr.ts` line 69

**Problem**:
- TypeScript types still allow `'sms' | 'email'`
- Should be `'email'` only or removed

**Current Code**:
```typescript
async sendPhoneOTP(employeeId: number, deliveryMethod: 'sms' | 'email', ...): Promise<any> {
  // ❌ Type allows 'sms' but backend doesn't support it
}
```

**Fix Required**: Update types to remove `'sms'` option

---

## Required Changes Summary

### File 1: `CRM_FRONTEND/lib/hr.ts`

**Change 1**: Update `sendPhoneOTP` function
```typescript
// BEFORE
async sendPhoneOTP(employeeId: number, deliveryMethod: 'sms' | 'email', phoneNumber?: string, email?: string): Promise<any> {
  return api.post(`/api/hr/employees/${employeeId}/send-phone-otp`, {
    delivery_method: deliveryMethod,
    phone_number: phoneNumber,
    email: email,
  });
}

// AFTER
async sendPhoneOTP(employeeId: number, email?: string): Promise<any> {
  return api.post(`/api/hr/employees/${employeeId}/send-phone-otp`, {
    email: email,  // Optional - backend will use employee.email if not provided
  });
}
```

**Change 2**: Update `sendReferenceOTP` function
```typescript
// BEFORE
async sendReferenceOTP(employeeId: number, referenceId: number, deliveryMethod: 'sms' | 'email'): Promise<any> {
  return api.post(`/api/hr/employees/${employeeId}/references/${referenceId}/send-otp`, {
    delivery_method: deliveryMethod,
  });
}

// AFTER
async sendReferenceOTP(employeeId: number, referenceId: number): Promise<any> {
  return api.post(`/api/hr/employees/${employeeId}/references/${referenceId}/send-otp`, {
    // No body needed - backend uses reference.email automatically
  });
}
```

---

### File 2: `CRM_FRONTEND/app/components/employee/VerificationWizard.tsx`

**Change 1**: Remove `otpDeliveryMethod` state (line 51)
```typescript
// REMOVE THIS LINE:
const [otpDeliveryMethod, setOtpDeliveryMethod] = useState<'sms' | 'email'>('sms');
```

**Change 2**: Update `handleSendOTP` function (lines 239-254)
```typescript
// BEFORE
const handleSendOTP = async () => {
  try {
    setSendingOtp(true);
    if (otpModal?.type === 'phone') {
      await hrApi.sendPhoneOTP(employeeId, otpDeliveryMethod);
      toast.success(`OTP sent via ${otpDeliveryMethod.toUpperCase()}`);
    } else if (otpModal?.type === 'reference' && otpModal.referenceId) {
      await hrApi.sendReferenceOTP(employeeId, otpModal.referenceId, otpDeliveryMethod);
      toast.success(`OTP sent to reference via ${otpDeliveryMethod.toUpperCase()}`);
    }
  } catch (error: any) {
    toast.error(error.message || 'Failed to send OTP');
  } finally {
    setSendingOtp(false);
  }
};

// AFTER
const handleSendOTP = async () => {
  try {
    setSendingOtp(true);
    if (otpModal?.type === 'phone') {
      // Get employee email from wizard data or use undefined (backend will use employee.email)
      const email = wizardData.personal?.email || undefined;
      await hrApi.sendPhoneOTP(employeeId, email);
      toast.success('OTP sent via email');
    } else if (otpModal?.type === 'reference' && otpModal.referenceId) {
      await hrApi.sendReferenceOTP(employeeId, otpModal.referenceId);
      toast.success('OTP sent to reference via email');
    }
  } catch (error: any) {
    console.error('OTP send error:', error);
    const errorMessage = error.message || error.error || 'Failed to send OTP. Please check email configuration.';
    toast.error(errorMessage);
  } finally {
    setSendingOtp(false);
  }
};
```

**Change 3**: Remove SMS/Email radio buttons (lines 448-471)
```typescript
// REMOVE THIS ENTIRE SECTION:
<div>
  <Label>Delivery Method</Label>
  <div className="flex gap-4 mt-2">
    <label className="flex items-center gap-2">
      <input type="radio" value="sms" ... />
      SMS
    </label>
    <label className="flex items-center gap-2">
      <input type="radio" value="email" ... />
      Email
    </label>
  </div>
</div>

// REPLACE WITH:
<div className="bg-blue-50 p-3 rounded-lg mb-4">
  <p className="text-sm text-gray-600">
    OTP will be sent to your email address
  </p>
</div>
```

**Change 4**: Update modal title (line 441)
```typescript
// BEFORE
<DialogTitle>
  {otpModal.type === 'phone' ? 'Verify Phone Number' : 'Verify Reference'}
</DialogTitle>

// AFTER
<DialogTitle>
  {otpModal.type === 'phone' ? 'Verify Email' : 'Verify Reference'}
</DialogTitle>
```

**Change 5**: Update success messages (lines 244, 247)
```typescript
// Change from:
toast.success(`OTP sent via ${otpDeliveryMethod.toUpperCase()}`);

// To:
toast.success('OTP sent via email');
```

---

## Testing Checklist

After making these changes, test:

- [ ] Click "Send OTP" button - should show loading state
- [ ] Check browser console for any errors
- [ ] Verify OTP email is received in employee's inbox
- [ ] Check backend logs for successful email sending
- [ ] Test with employee that has email
- [ ] Test with employee that doesn't have email (should use default)
- [ ] Test reference OTP sending
- [ ] Verify error messages are clear when email fails
- [ ] Check that SMS option is completely removed from UI
- [ ] Verify modal title says "Verify Email" not "Verify Phone Number"

---

## Additional Debugging Steps

If OTP still doesn't work after fixes:

1. **Check Browser Console**:
   - Open DevTools (F12)
   - Go to Console tab
   - Look for errors when clicking "Send OTP"
   - Check Network tab for failed requests

2. **Check Backend Logs**:
   - Look for email sending errors
   - Check if `send_otp_email` function is being called
   - Verify Gmail credentials are correct

3. **Check Network Request**:
   - In DevTools Network tab, find the POST request to `/api/hr/employees/{id}/send-phone-otp`
   - Check request payload (should only have `email` or be empty)
   - Check response status and body

4. **Verify Email Configuration**:
   - Ensure `.env` has correct Gmail credentials
   - Test email sending manually via Django shell
   - Check if `EMAIL_BACKEND` is set correctly

---

## Files to Modify

1. ✅ `CRM_FRONTEND/lib/hr.ts` - Update API functions
2. ✅ `CRM_FRONTEND/app/components/employee/VerificationWizard.tsx` - Update UI and handlers

---

## Priority

- **CRITICAL**: Fix API calls (items 1, 5) - OTP won't work without these
- **HIGH**: Remove SMS UI (items 2, 3) - Prevents user confusion
- **MEDIUM**: Update titles and messages (items 4, 7) - Better UX
- **LOW**: Improve error handling (item 6) - Better debugging

---

## Estimated Time

- API fixes: 15 minutes
- UI cleanup: 20 minutes
- Testing: 15 minutes
- **Total: ~50 minutes**

