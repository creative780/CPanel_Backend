# Fix Git Authentication Issue
# This script helps diagnose and fix GitHub authentication problems

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Authentication Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to CRM_BACKEND directory
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path (Join-Path $backendPath ".git"))) {
    Write-Host "[ERROR] Not in a git repository!" -ForegroundColor Red
    exit 1
}

Set-Location $backendPath

# Step 1: Check current remote configuration
Write-Host "Step 1: Checking current remote configuration..." -ForegroundColor Yellow
$remoteUrl = git remote get-url origin
Write-Host "Current remote URL: $remoteUrl" -ForegroundColor Gray

# Extract token if present
$tokenInUrl = $null
if ($remoteUrl -match 'ghp_[A-Za-z0-9]+') {
    $tokenInUrl = $matches[0]
    Write-Host "Token found in URL (first 10 chars): $($tokenInUrl.Substring(0, 10))..." -ForegroundColor Gray
} else {
    Write-Host "No token found in URL" -ForegroundColor Gray
}
Write-Host ""

# Step 2: Test current authentication
Write-Host "Step 2: Testing current authentication..." -ForegroundColor Yellow
$testResult = git ls-remote origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Authentication is working!" -ForegroundColor Green
    Write-Host "You can try pushing again: git push" -ForegroundColor Cyan
    Write-Host ""
    exit 0
} else {
    Write-Host "[FAILED] Authentication test failed" -ForegroundColor Red
    Write-Host "Error: $testResult" -ForegroundColor Gray
    Write-Host ""
}

# Step 3: Provide options to fix
Write-Host "Step 3: Choose authentication method to fix..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Available options:" -ForegroundColor Cyan
Write-Host "  1. Update token in URL (if you have a new GitHub Personal Access Token)" -ForegroundColor White
Write-Host "  2. Remove token and use credential manager (browser authentication)" -ForegroundColor White
Write-Host "  3. Switch to SSH authentication (requires SSH key setup)" -ForegroundColor White
Write-Host "  4. Exit without changes" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Option 1: Update Token in URL" -ForegroundColor Yellow
        Write-Host "You need a GitHub Personal Access Token (PAT) with 'repo' scope." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To create a new token:" -ForegroundColor Yellow
        Write-Host "  1. Go to: https://github.com/settings/tokens" -ForegroundColor White
        Write-Host "  2. Click 'Generate new token' -> 'Generate new token (classic)'" -ForegroundColor White
        Write-Host "  3. Give it a name (e.g., 'CRM_BACKEND_Push')" -ForegroundColor White
        Write-Host "  4. Select 'repo' scope (full control)" -ForegroundColor White
        Write-Host "  5. Set expiration (or no expiration)" -ForegroundColor White
        Write-Host "  6. Click 'Generate token'" -ForegroundColor White
        Write-Host "  7. Copy the token immediately (you won't see it again)" -ForegroundColor White
        Write-Host ""
        
        $newToken = Read-Host "Enter your new GitHub Personal Access Token (ghp_...)"
        
        if ([string]::IsNullOrWhiteSpace($newToken)) {
            Write-Host "[ERROR] Token cannot be empty!" -ForegroundColor Red
            exit 1
        }
        
        if (-not $newToken.StartsWith('ghp_')) {
            Write-Host "[WARNING] Token should start with 'ghp_'. Continuing anyway..." -ForegroundColor Yellow
        }
        
        # Update remote URL with new token
        $newUrl = "https://$newToken@github.com/creative780/CRM_BACKEND.git"
        Write-Host ""
        Write-Host "Updating remote URL..." -ForegroundColor Yellow
        git remote set-url origin $newUrl
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Remote URL updated" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Failed to update remote URL" -ForegroundColor Red
            exit 1
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Option 2: Use Credential Manager" -ForegroundColor Yellow
        Write-Host "Removing token from URL. Git will prompt for authentication." -ForegroundColor Cyan
        Write-Host ""
        
        # Remove token from URL
        $cleanUrl = "https://github.com/creative780/CRM_BACKEND.git"
        Write-Host "Updating remote URL to: $cleanUrl" -ForegroundColor Yellow
        git remote set-url origin $cleanUrl
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Remote URL updated (token removed)" -ForegroundColor Green
            Write-Host ""
            Write-Host "When you run 'git push', you will be prompted to authenticate." -ForegroundColor Cyan
            Write-Host "You can authenticate via:" -ForegroundColor Yellow
            Write-Host "  - Browser (recommended)" -ForegroundColor White
            Write-Host "  - Personal Access Token" -ForegroundColor White
            Write-Host "  - Username/Password (if 2FA disabled)" -ForegroundColor White
        } else {
            Write-Host "[ERROR] Failed to update remote URL" -ForegroundColor Red
            exit 1
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "Option 3: SSH Authentication" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "This option requires:" -ForegroundColor Cyan
        Write-Host "  1. SSH key generated on this machine" -ForegroundColor White
        Write-Host "  2. SSH key added to your GitHub account" -ForegroundColor White
        Write-Host ""
        
        # Check if SSH key exists
        $sshKeyPath = Join-Path $env:USERPROFILE ".ssh\id_rsa.pub"
        if (Test-Path $sshKeyPath) {
            Write-Host "[INFO] Found SSH public key: $sshKeyPath" -ForegroundColor Green
            Write-Host ""
            Write-Host "SSH public key content:" -ForegroundColor Cyan
            Get-Content $sshKeyPath | Write-Host -ForegroundColor Gray
            Write-Host ""
            Write-Host "Make sure this key is added to your GitHub account:" -ForegroundColor Yellow
            Write-Host "  https://github.com/settings/keys" -ForegroundColor White
            Write-Host ""
        } else {
            Write-Host "[WARNING] SSH public key not found at: $sshKeyPath" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "To generate an SSH key:" -ForegroundColor Yellow
            Write-Host "  ssh-keygen -t ed25519 -C 'your_email@example.com'" -ForegroundColor White
            Write-Host ""
            Write-Host "Then add it to GitHub: https://github.com/settings/keys" -ForegroundColor White
            Write-Host ""
            $continue = Read-Host "Do you want to continue anyway? (y/n)"
            if ($continue -ne 'y') {
                exit 0
            }
        }
        
        # Update remote URL to SSH
        $sshUrl = "git@github.com:creative780/CRM_BACKEND.git"
        Write-Host "Updating remote URL to: $sshUrl" -ForegroundColor Yellow
        git remote set-url origin $sshUrl
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Remote URL updated to SSH" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Failed to update remote URL" -ForegroundColor Red
            exit 1
        }
    }
    
    "4" {
        Write-Host ""
        Write-Host "Exiting without changes." -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "[ERROR] Invalid choice!" -ForegroundColor Red
        exit 1
    }
}

# Step 4: Test new authentication
Write-Host ""
Write-Host "Step 4: Testing new authentication..." -ForegroundColor Yellow
$testResult = git ls-remote origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Authentication is now working!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now push your changes:" -ForegroundColor Cyan
    Write-Host "  git push origin main" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[FAILED] Authentication test still failing" -ForegroundColor Red
    Write-Host "Error: $testResult" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  - For token method: Verify token has 'repo' scope and is not expired" -ForegroundColor White
    Write-Host "  - For credential manager: Try 'git push' and complete browser authentication" -ForegroundColor White
    Write-Host "  - For SSH: Verify SSH key is added to GitHub and test with 'ssh -T git@github.com'" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
