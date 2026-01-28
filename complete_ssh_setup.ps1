# Complete SSH Setup - Add Key to GitHub and Test
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Complete SSH Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the public key
$publicKeyPath = Join-Path $env:USERPROFILE ".ssh\id_ed25519.pub"
if (-not (Test-Path $publicKeyPath)) {
    Write-Host "[ERROR] SSH public key not found: $publicKeyPath" -ForegroundColor Red
    Write-Host "Run setup_ssh_github.ps1 first to generate the key." -ForegroundColor Yellow
    exit 1
}

$publicKey = Get-Content $publicKeyPath
Write-Host "Your SSH Public Key:" -ForegroundColor Yellow
Write-Host ""
Write-Host $publicKey -ForegroundColor Cyan
Write-Host ""

# Copy to clipboard
try {
    $publicKey | Set-Clipboard
    Write-Host "[SUCCESS] Public key copied to clipboard!" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Could not copy to clipboard" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "IMPORTANT: Add Key to GitHub" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Follow these steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open this URL in your browser:" -ForegroundColor White
Write-Host "   https://github.com/settings/keys" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Click the green 'New SSH key' button" -ForegroundColor White
Write-Host ""
Write-Host "3. Fill in the form:" -ForegroundColor White
Write-Host "   Title: Windows PC - CRM Project" -ForegroundColor Gray
Write-Host "   Key type: Authentication Key" -ForegroundColor Gray
Write-Host "   Key: Paste the key above (Ctrl+V - it's in your clipboard)" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Click 'Add SSH key'" -ForegroundColor White
Write-Host ""
Write-Host "5. You may be asked to enter your GitHub password" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter AFTER you've added the key to GitHub..." -ForegroundColor Yellow
Write-Host "(Don't paste anything - just press Enter)" -ForegroundColor Gray
Read-Host

Write-Host ""
Write-Host "Testing SSH connection to GitHub..." -ForegroundColor Yellow
Write-Host ""

# Test connection
$testResult = ssh -T git@github.com 2>&1

if ($testResult -match "successfully authenticated") {
    Write-Host "[SUCCESS] SSH connection works!" -ForegroundColor Green
    Write-Host $testResult -ForegroundColor Gray
    Write-Host ""
    
    # Switch remote to SSH
    Write-Host "Switching repository to use SSH..." -ForegroundColor Yellow
    $repoPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    if (Test-Path (Join-Path $repoPath ".git")) {
        Set-Location $repoPath
        git remote set-url origin git@github.com:creative780/CRM_BACKEND.git
        
        Write-Host "[SUCCESS] Remote URL switched to SSH" -ForegroundColor Green
        Write-Host ""
        Write-Host "Current remote:" -ForegroundColor Cyan
        git remote -v
        Write-Host ""
        
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Setup Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "You can now push using SSH:" -ForegroundColor Green
        Write-Host "  git push --force origin main" -ForegroundColor White
        Write-Host ""
    }
} else {
    Write-Host "[FAILED] SSH connection test failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error output:" -ForegroundColor Yellow
    Write-Host $testResult -ForegroundColor Gray
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Make sure you added the key to GitHub" -ForegroundColor White
    Write-Host "  2. Check that you copied the ENTIRE key (starts with ssh-ed25519)" -ForegroundColor White
    Write-Host "  3. Verify the key is on GitHub: https://github.com/settings/keys" -ForegroundColor White
    Write-Host "  4. Try verbose test: ssh -T -v git@github.com" -ForegroundColor White
    Write-Host ""
    Write-Host "Your public key (for reference):" -ForegroundColor Cyan
    Write-Host $publicKey -ForegroundColor Gray
    Write-Host ""
}
