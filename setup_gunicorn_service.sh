#!/bin/bash
# Setup script for Gunicorn systemd service
# This script installs and starts gunicorn as a systemd service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="crm-backend-gunicorn"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SOURCE_FILE="$(dirname "$(readlink -f "$0")")/crm-backend-gunicorn.service"
PROJECT_DIR="/home/api.crm.click2print.store/public_html"
LOG_DIR="${PROJECT_DIR}/logs"

echo -e "${GREEN}=== Gunicorn Systemd Service Setup ===${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}Note: This script needs sudo privileges. You'll be prompted for password.${NC}\n"
fi

# Step 1: Stop existing gunicorn processes
echo -e "${YELLOW}[1/6] Stopping existing gunicorn processes...${NC}"
if pgrep -f "gunicorn.*asgi" > /dev/null; then
    echo "Found running gunicorn processes, stopping them..."
    sudo pkill -f "gunicorn.*asgi" || true
    sleep 3
    echo -e "${GREEN}✓ Stopped existing processes${NC}\n"
else
    echo -e "${GREEN}✓ No existing processes found${NC}\n"
fi

# Step 2: Verify source file exists
echo -e "${YELLOW}[2/6] Verifying service file...${NC}"
if [ ! -f "$SOURCE_FILE" ]; then
    echo -e "${RED}✗ Error: Service file not found at $SOURCE_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Service file found${NC}\n"

# Step 3: Create logs directory
echo -e "${YELLOW}[3/6] Creating logs directory...${NC}"
sudo mkdir -p "$LOG_DIR"
sudo chmod 755 "$LOG_DIR"
echo -e "${GREEN}✓ Logs directory ready${NC}\n"

# Step 4: Copy service file
echo -e "${YELLOW}[4/6] Installing service file...${NC}"
sudo cp "$SOURCE_FILE" "$SERVICE_FILE"
sudo chmod 644 "$SERVICE_FILE"
echo -e "${GREEN}✓ Service file installed${NC}\n"

# Step 5: Reload systemd
echo -e "${YELLOW}[5/6] Reloading systemd...${NC}"
sudo systemctl daemon-reload
echo -e "${GREEN}✓ Systemd reloaded${NC}\n"

# Step 6: Start and enable service
echo -e "${YELLOW}[6/6] Starting service...${NC}"
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# Wait a moment for service to start
sleep 3

# Check status
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✓ Service started successfully!${NC}\n"
else
    echo -e "${RED}✗ Service failed to start. Checking status...${NC}\n"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    exit 1
fi

# Display status
echo -e "${GREEN}=== Service Status ===${NC}"
sudo systemctl status "$SERVICE_NAME" --no-pager -l | head -n 20

echo -e "\n${GREEN}=== Setup Complete! ===${NC}\n"
echo -e "Useful commands:"
echo -e "  View logs:     ${YELLOW}sudo journalctl -u $SERVICE_NAME -f${NC}"
echo -e "  Check status:  ${YELLOW}sudo systemctl status $SERVICE_NAME${NC}"
echo -e "  Restart:       ${YELLOW}sudo systemctl restart $SERVICE_NAME${NC}"
echo -e "  Stop:          ${YELLOW}sudo systemctl stop $SERVICE_NAME${NC}"
echo -e "  Start:         ${YELLOW}sudo systemctl start $SERVICE_NAME${NC}"
echo ""
echo -e "Log files are located at:"
echo -e "  Access log:    ${YELLOW}${LOG_DIR}/gunicorn_access.log${NC}"
echo -e "  Error log:     ${YELLOW}${LOG_DIR}/gunicorn_error.log${NC}"
echo ""

























