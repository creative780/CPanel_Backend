# Retry Push with Error Handling
# This script retries the push with better error handling and retry logic

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Retry Push with Error Handling" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to CRM_BACKEND directory
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

# Check current status
Write-Host "Current status:" -ForegroundColor Yellow
$statusLines = git status -sb
$statusLines | ForEach-Object { Write-Host $_ }
Write-Host ""

# Check if we need to push - get the first line which contains branch status
$statusLine = $statusLines[0]
$statusOutput = $statusLines | Out-String

if ($statusLine -notmatch 'diverged|ahead') {
    Write-Host "[INFO] Nothing to push - branch is up to date" -ForegroundColor Green
    exit 0
}

# Check if branch is ahead or diverged
$isAhead = $statusLine -match 'ahead'
$isDiverged = $statusLine -match 'diverged'
$isBehind = $statusLine -match 'behind'

if ($isDiverged) {
    Write-Host "[INFO] Branch has diverged - will force push" -ForegroundColor Yellow
} elseif ($isAhead) {
    Write-Host "[INFO] Branch is ahead of remote - will push" -ForegroundColor Yellow
} elseif ($isBehind) {
    Write-Host "[INFO] Branch is behind remote - consider pulling first" -ForegroundColor Yellow
}

Write-Host "Repository is large (2.55 GiB). Push may take 10-30 minutes." -ForegroundColor Yellow
Write-Host ""

# Retry logic
$maxRetries = 3
$retryCount = 0
$success = $false

while ($retryCount -lt $maxRetries -and -not $success) {
    $retryCount++
    
    if ($retryCount -gt 1) {
        Write-Host "Retry attempt $retryCount of $maxRetries..." -ForegroundColor Yellow
        Write-Host "Waiting 30 seconds before retry..." -ForegroundColor Gray
        Start-Sleep -Seconds 30
        Write-Host ""
    }
    
    Write-Host "Attempt $retryCount : Pushing to origin/main..." -ForegroundColor Yellow
    Write-Host ""
    
    # Try push
    $pushOutput = git push --force origin main 2>&1
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "[SUCCESS] Push completed successfully!" -ForegroundColor Green
        Write-Host ""
        git status
        $success = $true
    } else {
        Write-Host ""
        Write-Host "[FAILED] Push failed (attempt $retryCount)" -ForegroundColor Red
        
        # Check error type
        if ($pushOutput -match 'HTTP 500|500') {
            Write-Host "Error: GitHub server error (HTTP 500)" -ForegroundColor Yellow
            Write-Host "This is usually a temporary GitHub server issue." -ForegroundColor Gray
            Write-Host "The push may have partially succeeded - check GitHub." -ForegroundColor Gray
        } elseif ($pushOutput -match 'HTTP 401|401') {
            Write-Host "Error: Authentication failed (HTTP 401)" -ForegroundColor Yellow
            Write-Host "Run: .\fix_git_auth.ps1" -ForegroundColor White
            break
        } elseif ($pushOutput -match 'timeout|timed out') {
            Write-Host "Error: Connection timeout" -ForegroundColor Yellow
            Write-Host "Try using SSH or check your network connection." -ForegroundColor Gray
        } elseif ($pushOutput -match 'hung up|disconnect') {
            Write-Host "Error: Connection lost during push" -ForegroundColor Yellow
            Write-Host "This may be due to network instability or server timeout." -ForegroundColor Gray
        } elseif ($pushOutput -match '127\.0\.0\.1|Failed to connect|Could not connect') {
            Write-Host "Error: Network connection issue" -ForegroundColor Yellow
            Write-Host "Git is trying to connect to localhost (127.0.0.1) - check proxy settings." -ForegroundColor Gray
            Write-Host ""
            Write-Host "To fix proxy issues:" -ForegroundColor Yellow
            Write-Host "  git config --global --unset http.proxy" -ForegroundColor White
            Write-Host "  git config --global --unset https.proxy" -ForegroundColor White
        } else {
            Write-Host "Error: Unknown error" -ForegroundColor Yellow
            Write-Host $pushOutput -ForegroundColor Gray
        }
        
        Write-Host ""
        
        if ($retryCount -lt $maxRetries) {
            Write-Host "Will retry in 30 seconds..." -ForegroundColor Cyan
        } else {
            Write-Host "Max retries reached. Push failed." -ForegroundColor Red
            Write-Host ""
            Write-Host "Troubleshooting options:" -ForegroundColor Yellow
            Write-Host "  1. Check GitHub status: https://www.githubstatus.com/" -ForegroundColor White
            Write-Host "  2. Wait 10-15 minutes and try again" -ForegroundColor White
            Write-Host "  3. Switch to SSH: git remote set-url origin git@github.com:creative780/CRM_BACKEND.git" -ForegroundColor White
            Write-Host "  4. Run: .\fix_large_push.ps1 for more options" -ForegroundColor White
            Write-Host ""
            Write-Host "Note: LFS objects (1.1 GB) were uploaded successfully." -ForegroundColor Cyan
            Write-Host "      The issue is with the regular git push (2.55 GiB)." -ForegroundColor Cyan
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($success) {
    Write-Host "Push Complete!" -ForegroundColor Green
} else {
    Write-Host "Push Failed - See troubleshooting above" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
