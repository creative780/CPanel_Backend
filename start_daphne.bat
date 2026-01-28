@echo off
REM Start Django server with Daphne ASGI server
REM This properly handles ASGI applications with Channels and prevents timeout issues

echo ========================================
echo Starting Django Server with Daphne (ASGI)
echo ========================================
echo.
echo IMPORTANT: This uses Daphne instead of runserver
echo Daphne properly handles ASGI applications and prevents timeout warnings
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Please run this script from the CRM_BACKEND directory
    pause
    exit /b 1
)

REM Check if Redis is available (required for Channels)
echo Checking Redis connection...
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True); r.ping(); print('Redis is running!')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Redis is not running or not accessible!
    echo.
    echo Please install and start Redis/Memurai:
    echo 1. Install Memurai: https://www.memurai.com/get-memurai
    echo 2. Or see REDIS_SETUP_WINDOWS.md for other options
    echo.
    echo Press any key to continue anyway (WebSocket may not work)...
    pause >nul
)

echo.
echo Starting Daphne server on http://0.0.0.0:8000
echo Application close timeout: 30 seconds
echo.
echo Press Ctrl+C to stop the server
echo.

REM Change to script directory
cd /d "%~dp0"

REM Start Daphne with proper timeout configuration
REM --application-close-timeout: Time to wait for application cleanup (prevents timeout warnings)
python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start Daphne server
    echo.
    echo Make sure Daphne is installed:
    echo   pip install daphne
    echo.
    pause
)





























