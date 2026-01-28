# Fix Git LFS Push Issue
# This script sets up Git LFS and fixes the push issue with large .exe files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git LFS Setup and Push Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to CRM_BACKEND directory
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path (Join-Path $backendPath ".git"))) {
    Write-Host "[ERROR] Not in a git repository!" -ForegroundColor Red
    exit 1
}

Set-Location $backendPath

# Step 1: Check if Git LFS is installed
Write-Host "Step 1: Checking Git LFS installation..." -ForegroundColor Yellow
$lfsVersion = git lfs version 2>$null
if (-not $lfsVersion) {
    Write-Host "[ERROR] Git LFS is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git LFS:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://git-lfs.github.com/" -ForegroundColor White
    Write-Host "  2. Or use: winget install Git.GitLFS" -ForegroundColor White
    Write-Host "  3. Or use: choco install git-lfs" -ForegroundColor White
    exit 1
}

Write-Host "Git LFS is installed: $lfsVersion" -ForegroundColor Green
Write-Host ""

# Step 2: Initialize Git LFS
Write-Host "Step 2: Initializing Git LFS..." -ForegroundColor Yellow
git lfs install
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to initialize Git LFS!" -ForegroundColor Red
    exit 1
}
Write-Host "Git LFS initialized successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Verify .gitattributes file exists
Write-Host "Step 3: Verifying .gitattributes file..." -ForegroundColor Yellow
$gitattributesPath = Join-Path $backendPath ".gitattributes"
if (-not (Test-Path $gitattributesPath)) {
    Write-Host "[ERROR] .gitattributes file not found!" -ForegroundColor Red
    Write-Host "Please create .gitattributes file first." -ForegroundColor Yellow
    exit 1
}
Write-Host ".gitattributes file found" -ForegroundColor Green
Write-Host ""

# Step 4: Remove large .exe files from git cache (but keep them locally)
Write-Host "Step 4: Removing large .exe files from git cache..." -ForegroundColor Yellow
$exeFiles = @(
    "media/agents/crm-monitoring-agent-windows-amd64.exe",
    "media/uploads/agents/crm-monitoring-agent-windows-amd64.exe",
    "media/uploads/agents/crm-monitoring-agent.exe",
    "media/uploads/agents/agent-installer.exe",
    "agent-installer.exe",
    "crm-monitoring-agent.exe",
    "test-agent.exe"
)

$removedCount = 0
foreach ($file in $exeFiles) {
    $fullPath = Join-Path $backendPath $file
    if (Test-Path $fullPath) {
        # Check if file is tracked in git
        $isTracked = git ls-files --error-unmatch $file 2>$null
        if ($isTracked) {
            Write-Host "  Removing from cache: $file" -ForegroundColor Gray
            git rm --cached $file 2>$null
            if ($LASTEXITCODE -eq 0) {
                $removedCount++
            }
        }
    }
}
Write-Host "Removed $removedCount file(s) from git cache" -ForegroundColor Green
Write-Host ""

# Step 5: Add files back with LFS
Write-Host "Step 5: Adding files back with Git LFS..." -ForegroundColor Yellow
$addedCount = 0
foreach ($file in $exeFiles) {
    $fullPath = Join-Path $backendPath $file
    if (Test-Path $fullPath) {
        Write-Host "  Adding with LFS: $file" -ForegroundColor Gray
        git add $file
        if ($LASTEXITCODE -eq 0) {
            $addedCount++
        }
    }
}
Write-Host "Added $addedCount file(s) with Git LFS" -ForegroundColor Green
Write-Host ""

# Step 6: Add .gitattributes
Write-Host "Step 6: Adding .gitattributes..." -ForegroundColor Yellow
git add .gitattributes
if ($LASTEXITCODE -eq 0) {
    Write-Host ".gitattributes added successfully" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Failed to add .gitattributes" -ForegroundColor Yellow
}
Write-Host ""

# Step 7: Show status
Write-Host "Step 7: Current git status..." -ForegroundColor Yellow
git status --short
Write-Host ""

# Step 8: Instructions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the changes: git status" -ForegroundColor White
Write-Host "  2. Commit the changes: git commit -m 'Setup Git LFS for large .exe files'" -ForegroundColor White
Write-Host "  3. Push to remote: git push" -ForegroundColor White
Write-Host ""
Write-Host "Note: The large .exe files are now tracked with Git LFS." -ForegroundColor Cyan
Write-Host "      They will be stored separately and won't count against the 100MB limit." -ForegroundColor Cyan
Write-Host ""
