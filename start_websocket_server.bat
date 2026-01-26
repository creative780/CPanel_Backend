@echo off
REM Start Django server with WebSocket support using Daphne ASGI server
REM This replaces 'python manage.py runserver' which doesn't support WebSocket

echo ========================================
echo Starting Django Server with WebSocket Support
echo ========================================
echo.

REM Check if Redis is available
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
echo Starting server on http://0.0.0.0:8000
echo WebSocket endpoint: ws://localhost:8000/ws/monitoring/
echo.
echo Press Ctrl+C to stop the server
echo.

REM Change to CRM_BACKEND directory
cd /d "%~dp0"

REM Start Daphne ASGI server using Python module (works even if daphne command is not in PATH)
python -m daphne -p 8000 -b 0.0.0.0 crm_backend.asgi:application

