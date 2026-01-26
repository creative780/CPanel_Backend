# Fix Large Repository - Migrate More Files to LFS or Clean History
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Large Repository (2GB Limit)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

Write-Host "Problem: Repository pack exceeds GitHub's 2GB limit" -ForegroundColor Red
Write-Host "Solution: Migrate more large files to LFS or clean history" -ForegroundColor Yellow
Write-Host ""

# Step 1: Check current .gitattributes
Write-Host "Step 1: Checking current .gitattributes..." -ForegroundColor Yellow
if (Test-Path ".gitattributes") {
    Write-Host "Current .gitattributes:" -ForegroundColor Gray
    Get-Content ".gitattributes" | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "[WARNING] No .gitattributes file found" -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Find large files
Write-Host "Step 2: Finding large files (this may take a while)..." -ForegroundColor Yellow
Write-Host ""

$largeFiles = @()
$largeBlobs = git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | Where-Object { 
    $_ -match '^blob (\d+)' 
} | ForEach-Object {
    $size = [int]$matches[1]
    $rest = $_.Substring($_.IndexOf(' ', $_.IndexOf(' ') + 1) + 1)
    if ($size -gt 10MB) {
        $largeFiles += [PSCustomObject]@{
            Size = $size
            SizeMB = [math]::Round($size / 1MB, 2)
            Path = $rest
        }
    }
}

$largeFiles = $largeFiles | Sort-Object -Property Size -Descending

Write-Host "Large files found:" -ForegroundColor Cyan
$totalSize = 0
foreach ($file in $largeFiles | Select-Object -First 20) {
    $totalSize += $file.Size
    $color = if ($file.SizeMB -gt 100) { "Red" } elseif ($file.SizeMB -gt 50) { "Yellow" } else { "Gray" }
    Write-Host "  $($file.SizeMB) MB - $($file.Path)" -ForegroundColor $color
}

if ($largeFiles.Count -gt 20) {
    Write-Host "  ... and $($largeFiles.Count - 20) more files" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Total size of large files: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Yellow
Write-Host ""

# Step 3: Identify file types to migrate
Write-Host "Step 3: Identifying file types to migrate to LFS..." -ForegroundColor Yellow

$fileTypes = @{}
foreach ($file in $largeFiles) {
    $ext = [System.IO.Path]::GetExtension($file.Path).ToLower()
    if ([string]::IsNullOrWhiteSpace($ext)) {
        $ext = "(no extension)"
    }
    if (-not $fileTypes.ContainsKey($ext)) {
        $fileTypes[$ext] = @{
            Count = 0
            TotalSize = 0
            Files = @()
        }
    }
    $fileTypes[$ext].Count++
    $fileTypes[$ext].TotalSize += $file.Size
    $fileTypes[$ext].Files += $file
}

Write-Host ""
Write-Host "Large files by type:" -ForegroundColor Cyan
foreach ($type in $fileTypes.Keys | Sort-Object) {
    $info = $fileTypes[$type]
    $sizeMB = [math]::Round($info.TotalSize / 1MB, 2)
    Write-Host "  $type : $($info.Count) files, $sizeMB MB" -ForegroundColor Gray
}
Write-Host ""

# Step 4: Recommend LFS patterns
Write-Host "Step 4: Recommended LFS patterns to add:" -ForegroundColor Yellow
Write-Host ""

$recommendations = @()
if ($fileTypes.ContainsKey('.jpg') -or $fileTypes.ContainsKey('.jpeg')) {
    $recommendations += "*.jpg filter=lfs diff=lfs merge=lfs -text"
    $recommendations += "*.jpeg filter=lfs diff=lfs merge=lfs -text"
}
if ($fileTypes.ContainsKey('.png')) {
    $recommendations += "*.png filter=lfs diff=lfs merge=lfs -text"
}
if ($fileTypes.ContainsKey('.pdf')) {
    $recommendations += "*.pdf filter=lfs diff=lfs merge=lfs -text"
}
if ($fileTypes.ContainsKey('.zip')) {
    $recommendations += "*.zip filter=lfs diff=lfs merge=lfs -text"
}
if ($fileTypes.ContainsKey('.dll')) {
    $recommendations += "*.dll filter=lfs diff=lfs merge=lfs -text"
}
if ($fileTypes.ContainsKey('.so')) {
    $recommendations += "*.so filter=lfs diff=lfs merge=lfs -text"
}

# Check for large media files
$mediaFiles = $largeFiles | Where-Object { $_.Path -match 'media/|uploads/' }
if ($mediaFiles.Count -gt 0) {
    $mediaSize = ($mediaFiles | Measure-Object -Property Size -Sum).Sum
    $mediaSizeMB = [math]::Round($mediaSize / 1MB, 2)
    Write-Host "[IMPORTANT] Found $($mediaFiles.Count) large files in media/ directories ($mediaSizeMB MB)" -ForegroundColor Yellow
    $recommendations += "media/**/* filter=lfs diff=lfs merge=lfs -text"
}

if ($recommendations.Count -gt 0) {
    Write-Host "Add these to .gitattributes:" -ForegroundColor Cyan
    foreach ($rec in $recommendations) {
        Write-Host "  $rec" -ForegroundColor White
    }
} else {
    Write-Host "No obvious file types to migrate. May need to clean history instead." -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Options
Write-Host "Step 5: Choose an option:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Migrate more file types to LFS (recommended)" -ForegroundColor White
Write-Host "  - Add patterns to .gitattributes" -ForegroundColor Gray
Write-Host "  - Run: git lfs migrate import --include='pattern' --everything" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Remove large files from history (destructive)" -ForegroundColor White
Write-Host "  - Use git filter-repo or BFG Repo-Cleaner" -ForegroundColor Gray
Write-Host "  - Removes files from all commits" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 3: Create a fresh repository (nuclear option)" -ForegroundColor White
Write-Host "  - Start fresh with current code" -ForegroundColor Gray
Write-Host "  - Loses all history" -ForegroundColor Gray
Write-Host ""

Write-Host "For now, let's try Option 1 - migrate common large file types to LFS" -ForegroundColor Cyan
Write-Host ""
