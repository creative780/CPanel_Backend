# PowerShell script to start Django backend server with Daphne (ASGI)
Write-Host "Starting Django Backend Server with Daphne (ASGI)..." -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Using Daphne instead of runserver for proper ASGI support" -ForegroundColor Yellow
Write-Host "This prevents timeout warnings and properly handles WebSocket connections" -ForegroundColor Yellow
Write-Host ""

# Get the directory where this script is located
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Check if Redis is available (required for Channels)
Write-Host "Checking Redis connection..." -ForegroundColor Cyan
try {
    python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True); r.ping(); print('Redis is running!')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Redis is not running or not accessible!" -ForegroundColor Yellow
        Write-Host "WebSocket functionality may not work properly." -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "WARNING: Could not check Redis connection" -ForegroundColor Yellow
}

# Start the server with Daphne
Write-Host "Starting Daphne server on http://0.0.0.0:8000" -ForegroundColor Cyan
Write-Host "Application close timeout: 30 seconds" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m daphne -p 8000 -b 0.0.0.0 --application-close-timeout 30 crm_backend.asgi:application

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to start Daphne server" -ForegroundColor Red
    Write-Host "Make sure Daphne is installed: pip install daphne" -ForegroundColor Yellow
    Write-Host ""
}

