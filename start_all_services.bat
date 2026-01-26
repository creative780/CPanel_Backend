@echo off
REM Start all services: Daphne, Celery Worker, and Celery Beat
REM Note: This opens separate windows for each service
REM Press Ctrl+C in each window to stop that service

echo ========================================
echo Starting All CRM Services
echo ========================================
echo.
echo This will open 3 separate windows:
echo 1. Daphne Server (main API server)
echo 2. Celery Worker (background tasks)
echo 3. Celery Beat (scheduled tasks)
echo.
echo Press any key to continue...
pause >nul

REM Change to CRM_BACKEND directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at .venv
    echo Please ensure you're in the CRM_BACKEND directory with a virtual environment
    pause
    exit /b 1
)

REM Start Daphne in a new window
echo Starting Daphne server...
start "CRM - Daphne Server" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python -m daphne -p 8000 -b 0.0.0.0 crm_backend.asgi:application"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Celery Worker in a new window
echo Starting Celery Worker...
start "CRM - Celery Worker" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python -m celery -A crm_backend worker --loglevel=info --pool=solo"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Celery Beat in a new window
echo Starting Celery Beat scheduler...
start "CRM - Celery Beat" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python -m celery -A crm_backend beat -l info"

echo.
echo All services started in separate windows!
echo.
echo To stop services, press Ctrl+C in each window
echo.
pause














































