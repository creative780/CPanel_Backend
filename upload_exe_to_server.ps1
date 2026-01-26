# Upload .exe Files Directly to Server via SSH
# Server path: /home/api.crm.click2print.store/public_html/

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Upload .exe Files to Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

# Server configuration
$serverIP = "31.97.191.155"
$serverUser = "root"
$serverBasePath = "/home/api.crm.click2print.store/public_html"

Write-Host "Server: $serverUser@$serverIP" -ForegroundColor Yellow
Write-Host "Target: $serverBasePath" -ForegroundColor Yellow
Write-Host ""

# Step 1: Fix SSH host key issue
Write-Host "Step 1: Fixing SSH host key..." -ForegroundColor Yellow
ssh-keygen -R $serverIP 2>&1 | Out-Null
Write-Host "[SUCCESS] Old host key removed" -ForegroundColor Green
Write-Host "You'll be prompted to accept the new host key on first connection" -ForegroundColor Gray
Write-Host ""

# Files to upload
$filesToUpload = @(
    @{
        LocalPath = "media/agents/crm-monitoring-agent-windows-amd64.exe"
        RemotePath = "$serverBasePath/media/agents/crm-monitoring-agent-windows-amd64.exe"
        Description = "Main agent executable (agents directory)"
    },
    @{
        LocalPath = "media/uploads/agents/crm-monitoring-agent-windows-amd64.exe"
        RemotePath = "$serverBasePath/media/uploads/agents/crm-monitoring-agent-windows-amd64.exe"
        Description = "Main agent executable (uploads/agents directory)"
    },
    @{
        LocalPath = "media/uploads/agents/crm-monitoring-agent.exe"
        RemotePath = "$serverBasePath/media/uploads/agents/crm-monitoring-agent.exe"
        Description = "Agent executable (uploads/agents)"
    },
    @{
        LocalPath = "media/uploads/agents/agent-installer.exe"
        RemotePath = "$serverBasePath/media/uploads/agents/agent-installer.exe"
        Description = "Agent installer (uploads/agents)"
    }
)

# Check which files exist locally
Write-Host "Step 2: Checking local files..." -ForegroundColor Yellow
$existingFiles = @()
foreach ($file in $filesToUpload) {
    $localPath = Join-Path $backendPath $file.LocalPath
    if (Test-Path $localPath) {
        $fileSize = (Get-Item $localPath).Length / 1MB
        Write-Host "  [FOUND] $($file.LocalPath) - $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
        $existingFiles += $file
    } else {
        Write-Host "  [SKIP] $($file.LocalPath) - not found" -ForegroundColor Gray
    }
}

if ($existingFiles.Count -eq 0) {
    Write-Host "[ERROR] No files found to upload!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Found $($existingFiles.Count) file(s) to upload" -ForegroundColor Cyan
Write-Host ""

# Upload files
Write-Host "Step 3: Uploading files to server..." -ForegroundColor Yellow
Write-Host "Note: You'll be prompted to accept the SSH host key (type 'yes')" -ForegroundColor Gray
Write-Host "      Then enter your server password when prompted" -ForegroundColor Gray
Write-Host ""

$uploadedCount = 0
$failedCount = 0

foreach ($file in $existingFiles) {
    $localPath = Join-Path $backendPath $file.LocalPath
    $remoteDir = Split-Path -Parent $file.RemotePath
    
    Write-Host "Uploading: $($file.Description)" -ForegroundColor Cyan
    Write-Host "  From: $($file.LocalPath)" -ForegroundColor Gray
    Write-Host "  To: $($file.RemotePath)" -ForegroundColor Gray
    
    # Create remote directory first
    Write-Host "  Creating remote directory..." -ForegroundColor Gray
    $mkdirResult = ssh -o StrictHostKeyChecking=accept-new "$serverUser@$serverIP" "mkdir -p `"$remoteDir`"" 2>&1
    
    if ($LASTEXITCODE -ne 0 -and $mkdirResult -notmatch "yes/no") {
        Write-Host "  [WARNING] Directory creation may have failed" -ForegroundColor Yellow
    }
    
    # Upload file
    Write-Host "  Uploading file (this may take 2-5 minutes for 192MB files)..." -ForegroundColor Gray
    $scpResult = scp -o StrictHostKeyChecking=accept-new "$localPath" "$serverUser@$serverIP`:$($file.RemotePath)" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [SUCCESS] Uploaded successfully" -ForegroundColor Green
        $uploadedCount++
        
        # Verify file on server
        Write-Host "  Verifying on server..." -ForegroundColor Gray
        $verifyResult = ssh -o StrictHostKeyChecking=accept-new "$serverUser@$serverIP" "test -f `"$($file.RemotePath)`" && stat -c%s `"$($file.RemotePath)`"" 2>&1
        
        if ($verifyResult -match '^\d+$') {
            $remoteSizeMB = [math]::Round([long]$verifyResult / 1MB, 2)
            Write-Host "  [VERIFIED] File exists on server ($remoteSizeMB MB)" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] Could not verify file size" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [FAILED] Upload failed" -ForegroundColor Red
        if ($scpResult) {
            Write-Host "  Error: $scpResult" -ForegroundColor Gray
        }
        $failedCount++
    }
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Upload Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Uploaded: $uploadedCount" -ForegroundColor $(if ($uploadedCount -gt 0) { "Green" } else { "Red" })
Write-Host "  Failed: $failedCount" -ForegroundColor $(if ($failedCount -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($uploadedCount -gt 0) {
    Write-Host "[SUCCESS] Files uploaded to server!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files are now on the server at:" -ForegroundColor Cyan
    Write-Host "  $serverBasePath/media/agents/" -ForegroundColor White
    Write-Host "  $serverBasePath/media/uploads/agents/" -ForegroundColor White
    Write-Host ""
    Write-Host "To verify on server, run:" -ForegroundColor Yellow
    Write-Host "  ssh $serverUser@$serverIP 'ls -lh $serverBasePath/media/agents/*.exe'" -ForegroundColor White
    Write-Host "  ssh $serverUser@$serverIP 'ls -lh $serverBasePath/media/uploads/agents/*.exe'" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Verify files are accessible via Django" -ForegroundColor White
    Write-Host "  2. Commit git changes (removed .exe files from git)" -ForegroundColor White
    Write-Host "  3. Push to GitHub (without large files)" -ForegroundColor White
} else {
    Write-Host "[ERROR] No files were uploaded. Check errors above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  - Make sure you have SSH access to the server" -ForegroundColor White
    Write-Host "  - Check that the server path is correct" -ForegroundColor White
    Write-Host "  - Verify you have write permissions on the server" -ForegroundColor White
}

Write-Host ""
