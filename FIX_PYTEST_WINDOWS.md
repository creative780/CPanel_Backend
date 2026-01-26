# Fix: pytest Not Recognized on Windows

## Quick Fix

Instead of running:
```powershell
pytest hr/tests/ -v
```

Use:
```powershell
python -m pytest hr/tests/ -v
```

## Explanation

On Windows, `pytest` may not be in your PATH even if it's installed. Using `python -m pytest`:
- Uses Python's module runner
- Works regardless of PATH settings
- Ensures the correct Python environment

## Step-by-Step Solution

### Step 1: Navigate to Backend Directory
```powershell
cd D:\CRM-Final\CRM_BACKEND
```

### Step 2: Install Dependencies (if needed)
```powershell
pip install -r requirements.txt
```

### Step 3: Run Tests Using Python Module Syntax
```powershell
# Run all HR tests
python -m pytest hr/tests/ -v

# Run specific test file
python -m pytest hr/tests/test_security_and_permissions.py -v

# Run with coverage
python -m pytest hr/tests/ --cov=hr --cov-report=html
```

## Alternative: Use Helper Script

I've created helper scripts for you:

**PowerShell Script:**
```powershell
.\run_tests.ps1
```

**Batch Script:**
```cmd
run_tests.bat
```

These scripts automatically:
- Check if pytest is installed
- Install it if missing
- Run the tests properly

## Verify Installation

Check if pytest is installed:
```powershell
python -m pip list | findstr pytest
```

Should show:
```
pytest              8.3.2
pytest-cov          5.0.0
pytest-django       4.9.0
pytest-factoryboy   2.7.0
pytest-mock         3.14.0
```

If not installed, run:
```powershell
pip install pytest pytest-django pytest-cov pytest-mock pytest-factoryboy
```

## Test Commands

### Run All Tests
```powershell
python -m pytest hr/tests/ -v
```

### Run Security Tests Only
```powershell
python -m pytest hr/tests/test_security_and_permissions.py -v
```

### Run OTP Tests Only
```powershell
python -m pytest hr/tests/test_otp_system.py -v
```

### Run Employee Management Tests
```powershell
python -m pytest hr/tests/test_employee_management.py -v
```

### Run with Verbose Output
```powershell
python -m pytest hr/tests/ -vv --tb=short
```

### Run with Coverage
```powershell
python -m pytest hr/tests/ --cov=hr --cov-report=term --cov-report=html
```

## Common Issues

### Issue: "No module named pytest"
**Solution:** Install pytest
```powershell
pip install pytest pytest-django
```

### Issue: "Django not configured"
**Solution:** Make sure you're in the CRM_BACKEND directory and Django settings are configured

### Issue: "Permission denied"
**Solution:** Run PowerShell as Administrator, or use `--user` flag:
```powershell
pip install --user pytest
```

## Why This Happens

1. **PATH Issues**: pytest executable may not be in Windows PATH
2. **Virtual Environment**: pytest may be installed in venv but venv not activated
3. **Installation Location**: pytest installed in user site-packages, not system

Using `python -m pytest` bypasses all these issues by using Python's module runner directly.

## Summary

✅ **Use**: `python -m pytest hr/tests/ -v`  
❌ **Don't use**: `pytest hr/tests/ -v` (on Windows)

For more details, see:
- `RUN_TESTS_WINDOWS.md` - Comprehensive Windows testing guide
- `hr/tests/TEST_EXECUTION_GUIDE.md` - Full test execution guide

