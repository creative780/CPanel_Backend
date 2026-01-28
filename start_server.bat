@echo off
echo Starting Django Backend Server with Daphne (ASGI)...
echo.
echo IMPORTANT: Using Daphne instead of runserver for proper ASGI support
echo This prevents timeout warnings and properly handles WebSocket connections
echo.
echo Make sure you're in the CRM_BACKEND directory
echo.
cd /d %~dp0

REM Check if Redis is available (required for Channels)
echo Checking Redis connection...
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True); r.ping(); print('Redis is running!')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Redis is not running or not accessible!
    echo WebSocket functionality may not work properly.
    echo.
)

echo.
echo Starting Daphne server on http://0.0.0.0:8000
echo Press Ctrl+C to stop the server
echo.

REM Start Daphne with proper timeout configuration
python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start Daphne server
    echo Make sure Daphne is installed: pip install daphne
    echo.
)

pause

