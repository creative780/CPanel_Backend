# Gunicorn Daemon Setup Guide

## Problem
When you run gunicorn in a terminal and the terminal disconnects, the process gets killed and your backend stops working.

## Solution: Run as a Systemd Service (Recommended)

This is the best solution for production. The service will:
- Start automatically on boot
- Restart automatically if it crashes
- Survive terminal disconnections
- Run in the background as a daemon

### Step 1: Install the Service File

```bash
# Copy the service file to systemd directory
sudo cp /home/api.crm.click2print.store/public_html/crm-backend-gunicorn.service /etc/systemd/system/

# Or if you're in the CRM_BACKEND directory:
sudo cp crm-backend-gunicorn.service /etc/systemd/system/
```

### Step 2: Reload Systemd

```bash
sudo systemctl daemon-reload
```

### Step 3: Stop Current Gunicorn Process

```bash
# Find and stop the current gunicorn process
pkill -f "gunicorn.*asgi"

# Or kill specific PIDs if needed
kill 839651 859392 859393 859394 859395
```

### Step 4: Start the Service

```bash
# Start the service
sudo systemctl start crm-backend-gunicorn

# Enable it to start on boot
sudo systemctl enable crm-backend-gunicorn

# Check status
sudo systemctl status crm-backend-gunicorn
```

### Step 5: Verify It's Running

```bash
# Check if gunicorn is running
ps aux | grep gunicorn

# Check service status
sudo systemctl status crm-backend-gunicorn

# Check logs
sudo journalctl -u crm-backend-gunicorn -f
```

## Managing the Service

### Start/Stop/Restart

```bash
# Start
sudo systemctl start crm-backend-gunicorn

# Stop
sudo systemctl stop crm-backend-gunicorn

# Restart
sudo systemctl restart crm-backend-gunicorn

# Reload (graceful restart - reloads workers without dropping connections)
sudo systemctl reload crm-backend-gunicorn
```

### View Logs

```bash
# View all logs
sudo journalctl -u crm-backend-gunicorn

# Follow logs in real-time
sudo journalctl -u crm-backend-gunicorn -f

# View last 100 lines
sudo journalctl -u crm-backend-gunicorn -n 100

# View logs since today
sudo journalctl -u crm-backend-gunicorn --since today

# View logs from a specific time
sudo journalctl -u crm-backend-gunicorn --since "2025-12-12 21:00:00"
```

### Check Status

```bash
# Detailed status
sudo systemctl status crm-backend-gunicorn

# Check if service is enabled (will start on boot)
sudo systemctl is-enabled crm-backend-gunicorn

# Check if service is active (currently running)
sudo systemctl is-active crm-backend-gunicorn
```

## Alternative Solutions

### Option 2: Using Screen (Quick Fix)

Screen allows you to detach from a terminal session:

```bash
# Install screen if not installed
sudo yum install screen  # CentOS/RHEL
# or
sudo apt-get install screen  # Debian/Ubuntu

# Start a screen session
screen -S gunicorn

# Inside screen, start gunicorn
cd /home/api.crm.click2print.store/public_html
source venv/bin/activate
gunicorn crm_backend.asgi:application \
    --bind 0.0.0.0:9000 \
    --workers 4 \
    --timeout 120 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log

# Detach from screen: Press Ctrl+A, then D
# Reattach later: screen -r gunicorn
```

### Option 3: Using Tmux (Similar to Screen)

```bash
# Install tmux if not installed
sudo yum install tmux  # CentOS/RHEL
# or
sudo apt-get install tmux  # Debian/Ubuntu

# Start a tmux session
tmux new -s gunicorn

# Inside tmux, start gunicorn (same command as above)

# Detach: Press Ctrl+B, then D
# Reattach: tmux attach -t gunicorn
```

### Option 4: Using nohup (Simple Background Process)

```bash
cd /home/api.crm.click2print.store/public_html
source venv/bin/activate

# Run with nohup (no hang up)
nohup gunicorn crm_backend.asgi:application \
    --bind 0.0.0.0:9000 \
    --workers 4 \
    --timeout 120 \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log \
    > logs/gunicorn_nohup.log 2>&1 &

# Note the process ID (PID) that's printed
# To stop later: kill <PID>
```

### Option 5: Using Gunicorn's Built-in Daemon Mode

**Note:** This is less recommended than systemd, but works:

```bash
# Edit gunicorn_config.py and set:
# daemon = True

# Then run:
gunicorn crm_backend.asgi:application -c gunicorn_config.py

# To stop:
pkill -f "gunicorn.*asgi"
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status for errors
sudo systemctl status crm-backend-gunicorn

# Check logs for errors
sudo journalctl -u crm-backend-gunicorn -n 50

# Verify paths in service file are correct
cat /etc/systemd/system/crm-backend-gunicorn.service

# Test the gunicorn command manually
cd /home/api.crm.click2print.store/public_html
source venv/bin/activate
gunicorn crm_backend.asgi:application --bind 0.0.0.0:9000 --workers 4 --timeout 120 --worker-class uvicorn.workers.UvicornWorker
```

### Permission Issues

```bash
# Ensure log directory exists and is writable
mkdir -p /home/api.crm.click2print.store/public_html/logs
chmod 755 /home/api.crm.click2print.store/public_html/logs

# If running as different user, adjust ownership
chown -R root:root /home/api.crm.click2print.store/public_html/logs
```

### Port Already in Use

```bash
# Check what's using port 9000
sudo netstat -tulpn | grep 9000
# or
sudo ss -tulpn | grep 9000

# Kill the process if needed
sudo kill <PID>
```

### Service Keeps Restarting

```bash
# Check why it's failing
sudo journalctl -u crm-backend-gunicorn -n 100 --no-pager

# Check if there are too many restart attempts
sudo systemctl status crm-backend-gunicorn
```

## Recommended: Systemd Service

**Why systemd is best:**
- ✅ Automatic restart on failure
- ✅ Automatic start on boot
- ✅ Proper logging integration
- ✅ Process management
- ✅ Resource limits (can be configured)
- ✅ Security hardening options

## Quick Setup Script

Save this as `setup_gunicorn_service.sh`:

```bash
#!/bin/bash
set -e

SERVICE_FILE="/etc/systemd/system/crm-backend-gunicorn.service"
SOURCE_FILE="/home/api.crm.click2print.store/public_html/crm-backend-gunicorn.service"

echo "Stopping existing gunicorn processes..."
pkill -f "gunicorn.*asgi" || true
sleep 2

echo "Copying service file..."
sudo cp "$SOURCE_FILE" "$SERVICE_FILE"

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Starting service..."
sudo systemctl start crm-backend-gunicorn
sudo systemctl enable crm-backend-gunicorn

echo "Checking status..."
sleep 2
sudo systemctl status crm-backend-gunicorn

echo ""
echo "Service installed and started!"
echo "View logs with: sudo journalctl -u crm-backend-gunicorn -f"
```

Make it executable and run:
```bash
chmod +x setup_gunicorn_service.sh
sudo ./setup_gunicorn_service.sh
```

























