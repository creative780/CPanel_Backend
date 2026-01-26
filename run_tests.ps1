# PowerShell script to run HR tests
# This script handles pytest installation and execution

Write-Host "=== HR Test Suite Runner ===" -ForegroundColor Cyan

# Check if we're in a virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "Warning: No virtual environment detected. Consider activating one." -ForegroundColor Yellow
}

# Navigate to CRM_BACKEND directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if pytest is installed
Write-Host "`nChecking for pytest..." -ForegroundColor Cyan
$pytestCheck = python -m pytest --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "pytest not found. Installing pytest and dependencies..." -ForegroundColor Yellow
    python -m pip install -q pytest pytest-django pytest-cov pytest-mock pytest-factoryboy
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install pytest. Please run: pip install -r requirements.txt" -ForegroundColor Red
        exit 1
    }
    Write-Host "pytest installed successfully!" -ForegroundColor Green
} else {
    Write-Host "pytest is installed: $pytestCheck" -ForegroundColor Green
}

# Run the tests
Write-Host "`nRunning HR tests..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

if ($args.Count -eq 0) {
    # Run all HR tests
    python -m pytest hr/tests/ -v --tb=short
} else {
    # Run with provided arguments
    python -m pytest hr/tests/ $args
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Test execution complete!" -ForegroundColor Green

