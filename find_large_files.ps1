# Find Large Files in Git Repository
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Finding Large Files in Git Repository" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

Write-Host "Scanning git history for large files..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

# Find all blobs larger than 10MB
$largeBlobs = git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | Where-Object { 
    $_ -match '^blob (\d+)' 
} | ForEach-Object {
    $size = [int]$matches[1]
    $rest = $_.Substring($_.IndexOf(' ', $_.IndexOf(' ') + 1) + 1)
    if ($size -gt 10MB) {
        [PSCustomObject]@{
            Size = $size
            SizeMB = [math]::Round($size / 1MB, 2)
            Path = $rest
        }
    }
} | Sort-Object -Property Size -Descending

Write-Host "Large files found (over 10MB):" -ForegroundColor Yellow
Write-Host ""
$totalSize = 0
$count = 0

foreach ($blob in $largeBlobs) {
    $count++
    $totalSize += $blob.Size
    Write-Host "$($blob.SizeMB) MB - $($blob.Path)" -ForegroundColor $(if ($blob.SizeMB -gt 50) { "Red" } elseif ($blob.SizeMB -gt 20) { "Yellow" } else { "Gray" })
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Total large files: $count" -ForegroundColor White
Write-Host "  Total size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor White
Write-Host ""

# Check repository size
Write-Host "Repository size check:" -ForegroundColor Yellow
$repoSize = git count-objects -vH | Select-String "size-pack"
Write-Host $repoSize -ForegroundColor Gray
Write-Host ""
