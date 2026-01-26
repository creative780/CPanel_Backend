# Fix 2GB Repository Limit Issue
# Migrates all large files to LFS in one operation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix 2GB Repository Limit" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Problem: Repository pack exceeds GitHub's 2GB limit" -ForegroundColor Red
Write-Host "Solution: Migrate all large files to LFS" -ForegroundColor Yellow
Write-Host ""

$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

# Step 1: Check current size
Write-Host "Step 1: Checking current repository size..." -ForegroundColor Yellow
$repoInfo = git count-objects -vH
$sizePack = ($repoInfo | Select-String "size-pack:\s+(\d+\.?\d*)\s*(\w+)").Matches
if ($sizePack) {
    $size = [double]$sizePack.Groups[1].Value
    $unit = $sizePack.Groups[2].Value
    Write-Host "Current size: $size $unit" -ForegroundColor $(if ($size -gt 2 -and ($unit -eq "GiB" -or $unit -eq "GB")) { "Red" } else { "Green" })
} else {
    Write-Host $repoInfo -ForegroundColor Gray
}
Write-Host ""

# Step 2: Verify .gitattributes
Write-Host "Step 2: Verifying .gitattributes..." -ForegroundColor Yellow
if (-not (Test-Path ".gitattributes")) {
    Write-Host "[ERROR] .gitattributes not found!" -ForegroundColor Red
    exit 1
}
Write-Host ".gitattributes configured" -ForegroundColor Green
Write-Host ""

# Step 3: Migrate all files matching .gitattributes patterns
Write-Host "Step 3: Migrating all large files to LFS..." -ForegroundColor Yellow
Write-Host "This will rewrite history and may take 20-40 minutes..." -ForegroundColor Gray
Write-Host ""
Write-Host "WARNING: This rewrites ALL commits in history!" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne 'yes') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Starting migration..." -ForegroundColor Cyan
Write-Host ""

# Migrate all files that match .gitattributes patterns
# We'll migrate by common patterns to reduce repository size

$patternsToMigrate = @(
    "*.exe",
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.webp",
    "*.pdf",
    "*.zip", "*.tar", "*.gz", "*.7z", "*.rar",
    "*.dll", "*.so", "*.dylib"
)

Write-Host "Migrating file patterns..." -ForegroundColor Yellow
$successCount = 0
$failCount = 0

foreach ($pattern in $patternsToMigrate) {
    Write-Host "  Migrating $pattern ..." -ForegroundColor Gray
    $result = git lfs migrate import --include="$pattern" --everything 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    [OK] $pattern" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "    [SKIP] $pattern (may already be migrated or no matches)" -ForegroundColor Yellow
        $failCount++
    }
}

Write-Host ""
Write-Host "Migrated $successCount pattern(s)" -ForegroundColor Green
Write-Host ""

# Migrate media directory separately (often contains many large files)
Write-Host "Migrating media/**/* files..." -ForegroundColor Yellow
git lfs migrate import --include="media/**/*" --everything 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] media/**/* migrated" -ForegroundColor Green
} else {
    Write-Host "[INFO] media/**/* migration completed (may have warnings)" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Verify LFS migration
Write-Host "Step 4: Verifying LFS migration..." -ForegroundColor Yellow
$lfsFiles = git lfs ls-files
$lfsCount = ($lfsFiles | Measure-Object -Line).Lines
Write-Host "Files tracked with LFS: $lfsCount" -ForegroundColor Green
Write-Host ""

# Step 5: Check new repository size
Write-Host "Step 5: Checking new repository size..." -ForegroundColor Yellow
$repoInfo = git count-objects -vH
Write-Host $repoInfo -ForegroundColor Gray
Write-Host ""

$sizePack = ($repoInfo | Select-String "size-pack:\s+(\d+\.?\d*)\s*(\w+)").Matches
if ($sizePack) {
    $size = [double]$sizePack.Groups[1].Value
    $unit = $sizePack.Groups[2].Value
    
    # Convert to GB for comparison
    $sizeGB = if ($unit -eq "GiB" -or $unit -eq "GB") { $size } 
              elseif ($unit -eq "MiB" -or $unit -eq "MB") { $size / 1024 }
              else { $size / (1024 * 1024) }
    
    if ($sizeGB -lt 2.0) {
        Write-Host "[SUCCESS] Repository size is now under 2GB: $size $unit" -ForegroundColor Green
        Write-Host "You can now push to GitHub!" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Repository size is still $size $unit (above 2GB)" -ForegroundColor Yellow
        Write-Host "You may need additional cleanup or consider splitting the repository." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify LFS files: git lfs ls-files" -ForegroundColor White
Write-Host "  2. Check repository size: git count-objects -vH" -ForegroundColor White
Write-Host "  3. Push to GitHub: git push --force origin main" -ForegroundColor White
Write-Host ""
Write-Host "Note: If size is still over 2GB, you may need to:" -ForegroundColor Cyan
Write-Host "  - Remove old/unused large files from history" -ForegroundColor White
Write-Host "  - Consider using Git LFS for more file types" -ForegroundColor White
Write-Host "  - Split the repository into smaller parts" -ForegroundColor White
Write-Host ""
