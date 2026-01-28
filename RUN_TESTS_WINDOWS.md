# Running Tests on Windows - Quick Fix Guide

## Problem
If you see the error:
```
pytest : The term 'pytest' is not recognized as the name of a cmdlet...
```

## Solutions

### Solution 1: Use Python Module Syntax (Easiest)

Instead of `pytest`, use `python -m pytest`:

```powershell
cd CRM_BACKEND
python -m pytest hr/tests/ -v
```

### Solution 2: Use the Helper Script

Run the provided PowerShell script:

```powershell
cd CRM_BACKEND
.\run_tests.ps1
```

Or the batch file:
```cmd
cd CRM_BACKEND
run_tests.bat
```

### Solution 3: Install/Update Dependencies

Make sure all dependencies are installed:

```powershell
cd CRM_BACKEND
pip install -r requirements.txt
```

Then try:
```powershell
python -m pytest hr/tests/ -v
```

### Solution 4: Activate Virtual Environment

If you're using a virtual environment:

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1  # or .env\Scripts\Activate.ps1

# Then run tests
python -m pytest hr/tests/ -v
```

### Solution 5: Install pytest Directly

If pytest is missing:

```powershell
pip install pytest pytest-django pytest-cov pytest-mock pytest-factoryboy
```

## Common Commands

### Run All Tests
```powershell
python -m pytest hr/tests/ -v
```

### Run Specific Test File
```powershell
python -m pytest hr/tests/test_security_and_permissions.py -v
```

### Run Specific Test
```powershell
python -m pytest hr/tests/test_security_and_permissions.py::TestEmployeeCreationAccessControl::test_1_1_1_admin_can_create_employee -v
```

### Run with Coverage
```powershell
python -m pytest hr/tests/ --cov=hr --cov-report=html --cov-report=term
```

### Run Tests Matching Pattern
```powershell
python -m pytest hr/tests/ -k "security" -v
python -m pytest hr/tests/ -k "otp" -v
```

## Troubleshooting

### "pytest not found" even after installation
- Use `python -m pytest` instead of just `pytest`
- Make sure you're using the correct Python interpreter
- Check if virtual environment is activated

### "ModuleNotFoundError: No module named 'pytest'"
- Install pytest: `pip install pytest pytest-django`
- Or install all requirements: `pip install -r requirements.txt`

### Permission Denied
- Run PowerShell as Administrator
- Or install to user directory: `pip install --user pytest`

### Virtual Environment Issues
- Create new venv: `python -m venv venv`
- Activate it: `.\venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`

## Why Use `python -m pytest`?

Using `python -m pytest` instead of just `pytest`:
- Works even if pytest is not in PATH
- Uses the correct Python interpreter
- Ensures pytest runs in the correct environment
- More reliable on Windows systems

## Quick Test

To verify pytest is working:

```powershell
python -m pytest --version
```

Should output something like:
```
pytest 8.3.2
```

