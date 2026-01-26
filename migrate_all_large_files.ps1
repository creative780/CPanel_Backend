# Migrate All Large Files to LFS
# This script migrates multiple file types to LFS to reduce repository size below 2GB

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migrate All Large Files to LFS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will migrate multiple file types to LFS to reduce repository size." -ForegroundColor Yellow
Write-Host "WARNING: This rewrites git history!" -ForegroundColor Red
Write-Host ""

$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

# Check Git LFS
Write-Host "Step 1: Checking Git LFS..." -ForegroundColor Yellow
$lfsVersion = git lfs version 2>$null
if (-not $lfsVersion) {
    Write-Host "[ERROR] Git LFS is not installed!" -ForegroundColor Red
    exit 1
}
Write-Host "Git LFS: $lfsVersion" -ForegroundColor Green
Write-Host ""

# Verify .gitattributes
Write-Host "Step 2: Verifying .gitattributes..." -ForegroundColor Yellow
if (-not (Test-Path ".gitattributes")) {
    Write-Host "[ERROR] .gitattributes not found!" -ForegroundColor Red
    exit 1
}
Write-Host ".gitattributes found" -ForegroundColor Green
Write-Host ""

# Show what will be migrated
Write-Host "Step 3: File types that will be migrated to LFS:" -ForegroundColor Yellow
Get-Content ".gitattributes" | Where-Object { $_ -match 'filter=lfs' -and $_ -notmatch '^#' } | ForEach-Object {
    $pattern = ($_ -split ' ')[0]
    Write-Host "  $pattern" -ForegroundColor Gray
}
Write-Host ""

# Confirm
Write-Host "This will:" -ForegroundColor Cyan
Write-Host "  1. Migrate all matching files to LFS" -ForegroundColor White
Write-Host "  2. Rewrite all commits in history" -ForegroundColor White
Write-Host "  3. Update all commit hashes" -ForegroundColor White
Write-Host "  4. Take 10-30 minutes depending on repository size" -ForegroundColor White
Write-Host ""
$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne 'yes') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}
Write-Host ""

# Migrate files by pattern
Write-Host "Step 4: Migrating files to LFS..." -ForegroundColor Yellow
Write-Host "This will take a while. Please be patient..." -ForegroundColor Gray
Write-Host ""

$patterns = @(
    "*.exe",
    "*.jpg",
    "*.jpeg", 
    "*.png",
    "*.pdf",
    "*.zip",
    "*.dll",
    "*.so"
)

$migratedCount = 0
foreach ($pattern in $patterns) {
    Write-Host "Migrating $pattern ..." -ForegroundColor Cyan
    git lfs migrate import --include="$pattern" --everything 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [SUCCESS] $pattern migrated" -ForegroundColor Green
        $migratedCount++
    } else {
        Write-Host "  [WARNING] $pattern migration had issues" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Migrated $migratedCount pattern(s)" -ForegroundColor $(if ($migratedCount -gt 0) { "Green" } else { "Yellow" })
Write-Host ""

# Migrate media directory
Write-Host "Migrating media/**/* files..." -ForegroundColor Cyan
git lfs migrate import --include="media/**/*" --everything 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [SUCCESS] media/**/* migrated" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] media/**/* migration had issues" -ForegroundColor Yellow
}
Write-Host ""

# Verify migration
Write-Host "Step 5: Verifying migration..." -ForegroundColor Yellow
$lfsFiles = git lfs ls-files
$lfsCount = ($lfsFiles | Measure-Object -Line).Lines
Write-Host "Files now tracked with LFS: $lfsCount" -ForegroundColor Green
Write-Host ""

# Check repository size
Write-Host "Step 6: Checking repository size..." -ForegroundColor Yellow
$repoInfo = git count-objects -vH
Write-Host $repoInfo -ForegroundColor Gray
Write-Host ""

# Check if under 2GB
$sizePack = ($repoInfo | Select-String "size-pack:\s+(\d+\.?\d*)\s*(\w+)").Matches
if ($sizePack) {
    $size = [double]$sizePack.Groups[1].Value
    $unit = $sizePack.Groups[2].Value
    
    $sizeGB = if ($unit -eq "GiB" -or $unit -eq "GB") { $size } 
              elseif ($unit -eq "MiB" -or $unit -eq "MB") { $size / 1024 }
              else { $size / (1024 * 1024) }
    
    if ($sizeGB -lt 2.0) {
        Write-Host "[SUCCESS] Repository size is under 2GB: $size $unit" -ForegroundColor Green
        Write-Host "You can now push to GitHub!" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Repository size is still large: $size $unit" -ForegroundColor Yellow
        Write-Host "You may need to migrate more files or clean history." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify: git lfs ls-files" -ForegroundColor White
Write-Host "  2. Check size: git count-objects -vH" -ForegroundColor White
Write-Host "  3. Push: git push --force origin main" -ForegroundColor White
Write-Host ""
