# Setup SSH for GitHub - Automated Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub SSH Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check for existing SSH key
Write-Host "Step 1: Checking for existing SSH keys..." -ForegroundColor Yellow
$ed25519Key = Join-Path $env:USERPROFILE ".ssh\id_ed25519"
$rsaKey = Join-Path $env:USERPROFILE ".ssh\id_rsa"

$hasKey = $false
$keyPath = $null

if (Test-Path $ed25519Key) {
    Write-Host "[FOUND] Ed25519 key exists" -ForegroundColor Green
    $hasKey = $true
    $keyPath = $ed25519Key
} elseif (Test-Path $rsaKey) {
    Write-Host "[FOUND] RSA key exists" -ForegroundColor Green
    $hasKey = $true
    $keyPath = $rsaKey
} else {
    Write-Host "[NOT FOUND] No SSH keys found" -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Generate key if needed
if (-not $hasKey) {
    Write-Host "Step 2: Generating new SSH key..." -ForegroundColor Yellow
    Write-Host "Press Enter when prompted (for default location and no passphrase)" -ForegroundColor Cyan
    Write-Host ""
    
    # Ensure .ssh directory exists
    $sshDir = Join-Path $env:USERPROFILE ".ssh"
    if (-not (Test-Path $sshDir)) {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    }
    
    ssh-keygen -t ed25519 -C "abdullah.work027@gmail.com" -f $ed25519Key -N '""'
    
    if ($LASTEXITCODE -eq 0) {
        $keyPath = $ed25519Key
        Write-Host "[SUCCESS] SSH key generated!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to generate SSH key" -ForegroundColor Red
        Write-Host "You may need to run this interactively:" -ForegroundColor Yellow
        Write-Host "  ssh-keygen -t ed25519 -C `"abdullah.work027@gmail.com`"" -ForegroundColor White
        exit 1
    }
    Write-Host ""
} else {
    Write-Host "Step 2: Using existing SSH key" -ForegroundColor Yellow
    Write-Host ""
}

# Step 3: Start SSH agent and add key
Write-Host "Step 3: Starting SSH agent..." -ForegroundColor Yellow
try {
    Get-Service ssh-agent -ErrorAction Stop | Set-Service -StartupType Manual -ErrorAction SilentlyContinue
    Start-Service ssh-agent -ErrorAction Stop
    Write-Host "[SUCCESS] SSH agent started" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Could not start ssh-agent service automatically" -ForegroundColor Yellow
    Write-Host "You may need to start it manually or install OpenSSH" -ForegroundColor Yellow
    Write-Host "Trying to continue anyway..." -ForegroundColor Gray
}

Write-Host "Adding key to SSH agent..." -ForegroundColor Gray
$addResult = ssh-add $keyPath 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Key added to SSH agent" -ForegroundColor Green
} else {
    Write-Host "[INFO] Key may already be added or needs passphrase" -ForegroundColor Yellow
    if ($addResult) {
        Write-Host $addResult -ForegroundColor Gray
    }
}
Write-Host ""

# Step 4: Display and copy public key
Write-Host "Step 4: Your public SSH key:" -ForegroundColor Yellow
Write-Host ""
$publicKeyPath = "$keyPath.pub"
if (Test-Path $publicKeyPath) {
    $publicKey = Get-Content $publicKeyPath
    Write-Host $publicKey -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $publicKey | Set-Clipboard
        Write-Host "[SUCCESS] Public key copied to clipboard!" -ForegroundColor Green
    } catch {
        Write-Host "[INFO] Please copy the key above manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] Public key file not found: $publicKeyPath" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 5: Instructions
Write-Host "Step 5: Add key to GitHub" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to: https://github.com/settings/keys" -ForegroundColor Cyan
Write-Host "2. Click 'New SSH key'" -ForegroundColor White
Write-Host "3. Title: Enter a name (e.g., 'Windows PC')" -ForegroundColor White
Write-Host "4. Key: Paste the key (already in clipboard if possible)" -ForegroundColor White
Write-Host "5. Click 'Add SSH key'" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter after you've added the key to GitHub..." -ForegroundColor Yellow
Read-Host

# Step 6: Test connection
Write-Host ""
Write-Host "Step 6: Testing SSH connection..." -ForegroundColor Yellow
$testResult = ssh -T git@github.com 2>&1

if ($testResult -match "successfully authenticated") {
    Write-Host "[SUCCESS] SSH connection works!" -ForegroundColor Green
    Write-Host $testResult -ForegroundColor Gray
} else {
    Write-Host "[FAILED] SSH connection test failed" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Gray
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  - Make sure you added the key to GitHub" -ForegroundColor White
    Write-Host "  - Check that the key matches what's on GitHub" -ForegroundColor White
    Write-Host "  - Try: ssh -T -v git@github.com (for verbose output)" -ForegroundColor White
    Write-Host ""
    Write-Host "You can retry the test manually after fixing the issue." -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 7: Switch remote to SSH
Write-Host "Step 7: Switching repository to use SSH..." -ForegroundColor Yellow
$repoPath = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $repoPath ".git")) {
    Set-Location $repoPath
    git remote set-url origin git@github.com:creative780/CRM_BACKEND.git
    
    Write-Host "[SUCCESS] Remote URL switched to SSH" -ForegroundColor Green
    Write-Host ""
    Write-Host "Current remote:" -ForegroundColor Cyan
    git remote -v
} else {
    Write-Host "[WARNING] Not in a git repository" -ForegroundColor Yellow
    Write-Host "Run this script from the CRM_BACKEND directory" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "SSH is now configured! You can push without authentication." -ForegroundColor Green
Write-Host ""
Write-Host "Try pushing now:" -ForegroundColor Yellow
Write-Host "  git push --force origin main" -ForegroundColor White
Write-Host ""
