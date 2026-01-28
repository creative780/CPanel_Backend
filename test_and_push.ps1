# Test Authentication and Push
# This script tests authentication and attempts to push

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Authentication and Push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to CRM_BACKEND directory
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

# Step 1: Verify remote URL
Write-Host "Step 1: Verifying remote URL..." -ForegroundColor Yellow
$remoteUrl = git remote get-url origin
Write-Host "Remote URL: $remoteUrl" -ForegroundColor Gray
Write-Host ""

# Step 2: Test authentication
Write-Host "Step 2: Testing authentication..." -ForegroundColor Yellow
$testResult = git ls-remote origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Authentication is working!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[FAILED] Authentication test failed" -ForegroundColor Red
    Write-Host "Error: $testResult" -ForegroundColor Gray
    Write-Host ""
    Write-Host "You may need to:" -ForegroundColor Yellow
    Write-Host "  1. Run: git push" -ForegroundColor White
    Write-Host "  2. Complete browser authentication when prompted" -ForegroundColor White
    Write-Host "  3. Or use: .\fix_git_auth.ps1 to set up authentication" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Step 3: Check git status
Write-Host "Step 3: Checking git status..." -ForegroundColor Yellow
git status
Write-Host ""

# Step 4: Check if there are commits to push
Write-Host "Step 4: Checking commits to push..." -ForegroundColor Yellow
$statusOutput = git status -sb
if ($statusOutput -match 'ahead') {
    Write-Host "[INFO] Local branch is ahead of remote" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ready to push. Run the following command:" -ForegroundColor Yellow
    Write-Host "  git push origin main" -ForegroundColor White
    Write-Host ""
    Write-Host "Or push now? (y/n)" -ForegroundColor Yellow
    $pushNow = Read-Host
    
    if ($pushNow -eq 'y') {
        Write-Host ""
        Write-Host "Pushing to remote..." -ForegroundColor Yellow
        git push origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "[SUCCESS] Push completed successfully!" -ForegroundColor Green
            Write-Host ""
            git status
        } else {
            Write-Host ""
            Write-Host "[FAILED] Push failed. Check the error above." -ForegroundColor Red
            Write-Host ""
            Write-Host "If you see authentication errors, run: .\fix_git_auth.ps1" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[INFO] No commits to push - branch is up to date" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
