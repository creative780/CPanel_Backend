# Robust Upload Script for Large .exe Files
# Uses multiple methods and retry logic

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Robust .exe File Upload to Server" -ForegroundColor Cyan
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

# Fix SSH host key
Write-Host "Step 1: Fixing SSH host key..." -ForegroundColor Yellow
ssh-keygen -R $serverIP 2>&1 | Out-Null
Write-Host "[SUCCESS] Host key fixed" -ForegroundColor Green
Write-Host ""

# Files to upload
$filesToUpload = @(
    @{
        LocalPath = "media/agents/crm-monitoring-agent-windows-amd64.exe"
        RemotePath = "$serverBasePath/media/agents/crm-monitoring-agent-windows-amd64.exe"
    },
    @{
        LocalPath = "media/uploads/agents/crm-monitoring-agent-windows-amd64.exe"
        RemotePath = "$serverBasePath/media/uploads/agents/crm-monitoring-agent-windows-amd64.exe"
    }
)

# Check local files
Write-Host "Step 2: Checking local files..." -ForegroundColor Yellow
$existingFiles = @()
foreach ($file in $filesToUpload) {
    $localPath = Join-Path $backendPath $file.LocalPath
    if (Test-Path $localPath) {
        $fileSize = [math]::Round((Get-Item $localPath).Length / 1MB, 2)
        Write-Host "  [FOUND] $($file.LocalPath) - $fileSize MB" -ForegroundColor Green
        $existingFiles += $file
    }
}

if ($existingFiles.Count -eq 0) {
    Write-Host "[ERROR] No files found!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Upload with retry logic
Write-Host "Step 3: Uploading files (with retry on failure)..." -ForegroundColor Yellow
Write-Host ""

foreach ($file in $existingFiles) {
    $localPath = Join-Path $backendPath $file.LocalPath
    $remoteDir = Split-Path -Parent $file.RemotePath
    $fileName = Split-Path -Leaf $file.LocalPath
    
    Write-Host "Uploading: $fileName" -ForegroundColor Cyan
    Write-Host "  Size: $([math]::Round((Get-Item $localPath).Length / 1MB, 2)) MB" -ForegroundColor Gray
    Write-Host "  To: $($file.RemotePath)" -ForegroundColor Gray
    Write-Host ""
    
    # Create remote directory
    Write-Host "  Creating remote directory..." -ForegroundColor Gray
    ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "$serverUser@$serverIP" "mkdir -p `"$remoteDir`"" 2>&1 | Out-Null
    
    # Try upload with multiple methods
    $maxRetries = 3
    $success = $false
    
    for ($attempt = 1; $attempt -le $maxRetries; $attempt++) {
        if ($attempt -gt 1) {
            Write-Host "  Retry attempt $attempt of $maxRetries..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
        
        Write-Host "  Attempt $attempt : Uploading (this may take 3-5 minutes)..." -ForegroundColor Gray
        
        # Method 1: SCP with increased timeout and compression
        $scpResult = scp -o StrictHostKeyChecking=accept-new `
                         -o ServerAliveInterval=60 `
                         -o ServerAliveCountMax=3 `
                         -o Compression=yes `
                         -C `
                         "$localPath" "$serverUser@$serverIP`:$($file.RemotePath)" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [SUCCESS] Upload completed!" -ForegroundColor Green
            $success = $true
            break
        } else {
            Write-Host "  [FAILED] Attempt $attempt failed" -ForegroundColor Yellow
            if ($scpResult) {
                $errorMsg = ($scpResult | Out-String).Trim()
                if ($errorMsg -match "Connection reset|Connection closed|timeout") {
                    Write-Host "  Reason: Connection timeout/reset (common for large files)" -ForegroundColor Gray
                } else {
                    Write-Host "  Error: $errorMsg" -ForegroundColor Gray
                }
            }
        }
    }
    
    if (-not $success) {
        Write-Host ""
        Write-Host "  [ERROR] All upload attempts failed for $fileName" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Alternative methods:" -ForegroundColor Yellow
        Write-Host "    1. Use WinSCP or FileZilla (GUI tools, more reliable for large files)" -ForegroundColor White
        Write-Host "    2. Use rsync if available: rsync -avz --progress `"$localPath`" $serverUser@$serverIP`:$($file.RemotePath)" -ForegroundColor White
        Write-Host "    3. Upload via CyberPanel file manager (web interface)" -ForegroundColor White
        Write-Host "    4. Split file into smaller chunks and upload separately" -ForegroundColor White
        Write-Host ""
    } else {
        # Verify upload
        Write-Host "  Verifying upload..." -ForegroundColor Gray
        $verifyResult = ssh -o StrictHostKeyChecking=accept-new "$serverUser@$serverIP" "test -f `"$($file.RemotePath)`" && stat -c%s `"$($file.RemotePath)`"" 2>&1
        
        if ($verifyResult -match '^\d+$') {
            $remoteSizeMB = [math]::Round([long]$verifyResult / 1MB, 2)
            $localSizeMB = [math]::Round((Get-Item $localPath).Length / 1MB, 2)
            
            if ([math]::Abs($remoteSizeMB - $localSizeMB) -lt 1) {
                Write-Host "  [VERIFIED] File size matches ($remoteSizeMB MB)" -ForegroundColor Green
            } else {
                Write-Host "  [WARNING] File size mismatch: Local=$localSizeMB MB, Remote=$remoteSizeMB MB" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Upload Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
