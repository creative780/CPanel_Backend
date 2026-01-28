@echo off
REM Windows batch script to run HR tests

echo === HR Test Suite Runner ===

REM Navigate to script directory
cd /d "%~dp0"

REM Check if pytest is available
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo pytest not found. Installing pytest and dependencies...
    python -m pip install -q pytest pytest-django pytest-cov pytest-mock pytest-factoryboy
    if errorlevel 1 (
        echo Failed to install pytest. Please run: pip install -r requirements.txt
        exit /b 1
    )
    echo pytest installed successfully!
) else (
    echo pytest is installed.
)

REM Run the tests
echo.
echo Running HR tests...
echo ================================

if "%1"=="" (
    REM Run all HR tests
    python -m pytest hr/tests/ -v --tb=short
) else (
    REM Run with provided arguments
    python -m pytest hr/tests/ %*
)

echo.
echo ================================
echo Test execution complete!
pause

