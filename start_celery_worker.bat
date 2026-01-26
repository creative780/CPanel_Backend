@echo off
REM Start Celery Worker for background task processing (exports, scheduled reports, etc.)
REM This should be run in a separate terminal from the main server and Celery Beat

echo ========================================
echo Starting Celery Worker
echo ========================================
echo.

REM Change to CRM_BACKEND directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at .venv
    echo Please ensure you're in the CRM_BACKEND directory with a virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if Redis is available
echo Checking Redis connection...
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True); r.ping(); print('Redis is running!')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Redis is not running or not accessible!
    echo.
    echo Please install and start Redis/Memurai:
    echo 1. Install Memurai: https://www.memurai.com/get-memurai
    echo 2. Or see REDIS_SETUP_WINDOWS.md for other options
    echo.
    echo Press any key to continue anyway...
    pause >nul
)

echo.
echo Starting Celery Worker...
echo Using solo pool (required for Windows)
echo.
echo Press Ctrl+C to stop
echo.

REM Start Celery Worker with Windows-compatible pool
python -m celery -A crm_backend worker --loglevel=info --pool=solo














































