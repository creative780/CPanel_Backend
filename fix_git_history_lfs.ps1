# Fix Git History - Migrate Large Files to LFS
# This script rewrites git history to convert large .exe files to LFS pointers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git History LFS Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WARNING: This will rewrite git history!" -ForegroundColor Yellow
Write-Host "All commit hashes will change." -ForegroundColor Yellow
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
    exit 1
}

Write-Host "Git LFS is installed: $lfsVersion" -ForegroundColor Green
Write-Host ""

# Step 2: Verify .gitattributes exists
Write-Host "Step 2: Verifying .gitattributes file..." -ForegroundColor Yellow
$gitattributesPath = Join-Path $backendPath ".gitattributes"
if (-not (Test-Path $gitattributesPath)) {
    Write-Host "[ERROR] .gitattributes file not found!" -ForegroundColor Red
    Write-Host "Please create .gitattributes file first." -ForegroundColor Yellow
    exit 1
}
Write-Host ".gitattributes file found" -ForegroundColor Green
Write-Host ""

# Step 3: Check current branch and commits
Write-Host "Step 3: Checking current state..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Gray

$statusOutput = git status -sb
if ($statusOutput -match 'ahead') {
    Write-Host "[INFO] Local branch is ahead of remote" -ForegroundColor Cyan
} else {
    Write-Host "[INFO] Branch is up to date with remote" -ForegroundColor Cyan
}
Write-Host ""

# Step 4: Check for large files in history
Write-Host "Step 4: Checking for large .exe files in git history..." -ForegroundColor Yellow
$largeFiles = git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | Where-Object { $_ -match '^blob (\d+)' } | ForEach-Object {
    if ([int]$matches[1] -gt 100MB) {
        $_.Substring($_.IndexOf(' ') + 1)
    }
}

if ($largeFiles) {
    Write-Host "Found large files in history:" -ForegroundColor Yellow
    $largeFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "No large files found in history (or already migrated)" -ForegroundColor Green
}
Write-Host ""

# Step 5: Confirm migration
Write-Host "Step 5: Ready to migrate .exe files to LFS in all commits" -ForegroundColor Yellow
Write-Host ""
Write-Host "This will:" -ForegroundColor Cyan
Write-Host "  1. Find all .exe files in git history" -ForegroundColor White
Write-Host "  2. Convert them to LFS pointers" -ForegroundColor White
Write-Host "  3. Rewrite all commits containing these files" -ForegroundColor White
Write-Host "  4. Update all commit hashes" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: This rewrites history. If you've already pushed commits," -ForegroundColor Yellow
Write-Host "you'll need to force push after this: git push --force" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Continue with migration? (yes/no)"
if ($confirm -ne 'yes') {
    Write-Host "Migration cancelled." -ForegroundColor Yellow
    exit 0
}

# Step 6: Check if git lfs migrate is available
Write-Host "Step 6: Checking for git lfs migrate command..." -ForegroundColor Yellow
$migrateAvailable = git lfs migrate --help 2>$null
if (-not $migrateAvailable) {
    Write-Host "[ERROR] 'git lfs migrate' command not available!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Your Git LFS version may not support 'migrate'." -ForegroundColor Yellow
    Write-Host "Please update Git LFS to the latest version:" -ForegroundColor Yellow
    Write-Host "  winget upgrade Git.GitLFS" -ForegroundColor White
    Write-Host "  Or download from: https://git-lfs.github.com/" -ForegroundColor White
    Write-Host ""
    Write-Host "Alternatively, you can use BFG Repo-Cleaner or git filter-repo." -ForegroundColor Yellow
    exit 1
}

Write-Host "git lfs migrate is available" -ForegroundColor Green
Write-Host ""

# Step 7: Run git lfs migrate
Write-Host "Step 7: Running git lfs migrate import..." -ForegroundColor Yellow
Write-Host "This will rewrite history and may take several minutes..." -ForegroundColor Gray
Write-Host ""

# Migrate all .exe files to LFS
Write-Host "Command: git lfs migrate import --include='*.exe' --everything" -ForegroundColor Gray
git lfs migrate import --include="*.exe" --everything

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Migration failed!" -ForegroundColor Red
    Write-Host "Error code: $LASTEXITCODE" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  - Make sure you have the latest Git LFS version" -ForegroundColor White
    Write-Host "  - Check if there are any uncommitted changes (git status)" -ForegroundColor White
    Write-Host "  - Try: git lfs migrate import --include='*.exe' --everything --verbose" -ForegroundColor White
    exit 1
}

Write-Host "[SUCCESS] Migration completed!" -ForegroundColor Green
Write-Host ""

# Step 8: Verify migration
Write-Host "Step 8: Verifying migration..." -ForegroundColor Yellow
$lfsFiles = git lfs ls-files
if ($lfsFiles) {
    Write-Host "Files now tracked with LFS:" -ForegroundColor Green
    $lfsFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "[WARNING] No LFS files found. Migration may not have worked." -ForegroundColor Yellow
}
Write-Host ""

# Step 9: Show status
Write-Host "Step 9: Current git status..." -ForegroundColor Yellow
git status
Write-Host ""

# Step 10: Instructions
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review changes: git log --oneline -5" -ForegroundColor White
Write-Host "  2. Verify LFS files: git lfs ls-files" -ForegroundColor White
Write-Host "  3. Push to remote: git push --force origin main" -ForegroundColor White
Write-Host ""
Write-Host "WARNING: Using --force will overwrite remote history!" -ForegroundColor Yellow
Write-Host "Make sure no one else is working on this branch." -ForegroundColor Yellow
Write-Host ""
