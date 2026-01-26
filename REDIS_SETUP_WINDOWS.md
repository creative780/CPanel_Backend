# Redis Setup for Windows - WebSocket Support

## Problem
WebSocket connections require Redis for Django Channels. Redis is not natively available on Windows.

## Solution Options

### Option 1: Install Memurai (Recommended - Easiest)
Memurai is a Redis-compatible server for Windows.

1. **Download Memurai:**
   - Visit: https://www.memurai.com/get-memurai
   - Download the Windows installer (Community Edition is free)

2. **Install Memurai:**
   - Run the installer
   - Follow the installation wizard
   - Memurai will automatically start as a Windows service

3. **Verify Installation:**
   ```powershell
   # After installation, Redis commands should work:
   redis-cli ping
   # Should return: PONG
   ```

### Option 2: Use WSL (Windows Subsystem for Linux)
If you have WSL installed:

1. **Open WSL terminal:**
   ```powershell
   wsl
   ```

2. **Install Redis in WSL:**
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo service redis-server start
   ```

3. **Verify:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

### Option 3: Install Docker Desktop (Alternative)
1. Download Docker Desktop for Windows: https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Run Redis container:
   ```powershell
   docker run -d -p 6379:6379 --name redis redis:7-alpine
   ```

### Option 4: Use In-Memory Channel Layer (Temporary - Limited)
For quick testing without Redis, you can temporarily use in-memory channel layer.
**Warning:** This won't work with multiple processes or production.

See `settings_development_no_redis.py` for this configuration.

## After Installing Redis

1. **Verify Redis is running:**
   ```powershell
   redis-cli ping
   # Should return: PONG
   ```

2. **Start Django server with WebSocket support:**
   ```powershell
   cd CRM_BACKEND
   daphne -p 8000 -b 0.0.0.0 crm_backend.asgi:application
   ```

3. **Or use the startup script:**
   ```powershell
   .\start_websocket_server.bat
   ```

## Troubleshooting

- **"redis-cli: command not found"**
  - Redis/Memurai is not installed or not in PATH
  - Install Memurai (Option 1) or restart terminal after installation

- **"Connection refused" error**
  - Redis is not running
  - Start Redis service or Docker container

- **"WebSocket connection failed"**
  - Make sure you're using `daphne` or `uvicorn`, NOT `runserver`
  - Check that Redis is running and accessible




