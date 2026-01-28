# Fix Large Push Issues
# This script helps push large repositories with optimized settings

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Large Push Issues" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to CRM_BACKEND directory
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

# Step 1: Optimize git config for large pushes
Write-Host "Step 1: Optimizing git configuration for large pushes..." -ForegroundColor Yellow

# Increase HTTP buffer sizes
git config http.postBuffer 524288000
git config http.maxRequestBuffer 100M
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999

# Increase pack window memory
git config pack.windowMemory 256m
git config pack.packSizeLimit 2g

# Enable compression
git config core.compression 9

Write-Host "[SUCCESS] Git configuration optimized" -ForegroundColor Green
Write-Host ""

# Step 2: Check repository size
Write-Host "Step 2: Checking repository size..." -ForegroundColor Yellow
$repoSize = (git count-objects -vH | Select-String "size-pack").ToString()
Write-Host "Repository size: $repoSize" -ForegroundColor Gray
Write-Host ""

# Step 3: Check LFS status
Write-Host "Step 3: Checking LFS status..." -ForegroundColor Yellow
$lfsFiles = git lfs ls-files
$lfsCount = ($lfsFiles | Measure-Object -Line).Lines
Write-Host "LFS files tracked: $lfsCount" -ForegroundColor Gray
if ($lfsCount -gt 0) {
    Write-Host "[SUCCESS] LFS is properly configured" -ForegroundColor Green
} else {
    Write-Host "[WARNING] No LFS files found" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Check for large non-LFS files
Write-Host "Step 4: Checking for large non-LFS files..." -ForegroundColor Yellow
$largeBlobs = git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | Where-Object { 
    $_ -match '^blob (\d+)' -and [int]$matches[1] -gt 50MB 
} | ForEach-Object {
    $size = [int]$matches[1]
    $name = $_.Substring($_.IndexOf(' ', $_.IndexOf(' ') + 1) + 1)
    [PSCustomObject]@{Size=$size; Name=$name}
}

if ($largeBlobs) {
    Write-Host "[WARNING] Found large non-LFS files:" -ForegroundColor Yellow
    $largeBlobs | ForEach-Object { 
        $sizeMB = [math]::Round($_.Size / 1MB, 2)
        Write-Host "  $($_.Name) - $sizeMB MB" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Consider migrating these to LFS or removing them from history." -ForegroundColor Yellow
} else {
    Write-Host "[SUCCESS] No large non-LFS files found" -ForegroundColor Green
}
Write-Host ""

# Step 5: Prune and optimize repository
Write-Host "Step 5: Pruning and optimizing repository..." -ForegroundColor Yellow
Write-Host "Running git gc (this may take a while)..." -ForegroundColor Gray
git gc --aggressive --prune=now
Write-Host "[SUCCESS] Repository optimized" -ForegroundColor Green
Write-Host ""

# Step 6: Check remote status
Write-Host "Step 6: Checking remote status..." -ForegroundColor Yellow
$statusOutput = git status -sb
Write-Host $statusOutput -ForegroundColor Gray
Write-Host ""

# Step 7: Provide push options
Write-Host "Step 7: Push options..." -ForegroundColor Yellow
Write-Host ""
Write-Host "The repository is large (2.55 GiB). Here are your options:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Retry push with optimized settings (recommended first)" -ForegroundColor White
Write-Host "  git push --force origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Push with increased timeout" -ForegroundColor White
Write-Host "  git -c http.postBuffer=524288000 push --force origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 3: Push in chunks (if above fails)" -ForegroundColor White
Write-Host "  This requires more complex setup - see script comments" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 4: Use SSH instead of HTTPS (may be more reliable)" -ForegroundColor White
Write-Host "  git remote set-url origin git@github.com:creative780/CRM_BACKEND.git" -ForegroundColor Gray
Write-Host "  git push --force origin main" -ForegroundColor Gray
Write-Host ""

# Step 8: Ask user what to do
Write-Host "What would you like to do?" -ForegroundColor Yellow
Write-Host "  1. Try push now with optimized settings" -ForegroundColor White
Write-Host "  2. Switch to SSH and push" -ForegroundColor White
Write-Host "  3. Exit and push manually" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Pushing with optimized settings..." -ForegroundColor Yellow
        Write-Host "This may take 10-30 minutes due to repository size..." -ForegroundColor Gray
        Write-Host ""
        
        git push --force origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "[SUCCESS] Push completed!" -ForegroundColor Green
            git status
        } else {
            Write-Host ""
            Write-Host "[FAILED] Push failed. Try Option 2 (SSH) or retry later." -ForegroundColor Red
            Write-Host ""
            Write-Host "Common causes:" -ForegroundColor Yellow
            Write-Host "  - GitHub server timeout (HTTP 500)" -ForegroundColor White
            Write-Host "  - Network instability" -ForegroundColor White
            Write-Host "  - Repository too large for single push" -ForegroundColor White
            Write-Host ""
            Write-Host "Solutions:" -ForegroundColor Yellow
            Write-Host "  - Wait a few minutes and retry" -ForegroundColor White
            Write-Host "  - Switch to SSH: git remote set-url origin git@github.com:creative780/CRM_BACKEND.git" -ForegroundColor White
            Write-Host "  - Contact GitHub support if issue persists" -ForegroundColor White
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Switching to SSH..." -ForegroundColor Yellow
        
        # Check if SSH key exists
        $sshKeyPath = Join-Path $env:USERPROFILE ".ssh\id_rsa.pub"
        if (-not (Test-Path $sshKeyPath)) {
            Write-Host "[WARNING] SSH key not found at: $sshKeyPath" -ForegroundColor Yellow
            Write-Host "You may need to generate an SSH key first." -ForegroundColor Yellow
            Write-Host ""
        }
        
        git remote set-url origin git@github.com:creative780/CRM_BACKEND.git
        Write-Host "[SUCCESS] Remote URL updated to SSH" -ForegroundColor Green
        Write-Host ""
        Write-Host "Now try pushing:" -ForegroundColor Yellow
        Write-Host "  git push --force origin main" -ForegroundColor White
        Write-Host ""
    }
    
    "3" {
        Write-Host ""
        Write-Host "Exiting. You can push manually with:" -ForegroundColor Yellow
        Write-Host "  git push --force origin main" -ForegroundColor White
        Write-Host ""
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "[ERROR] Invalid choice!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
