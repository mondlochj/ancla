#!/bin/bash
#
# Setup script for Ancla Gunicorn systemd service
#

set -e

# Configuration
APP_NAME="ancla"
APP_DIR="/opt/ancla"
USER="administrator"
GROUP="administrator"
WORKERS=4
BIND="0.0.0.0:5003"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Gunicorn systemd service for Ancla...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Note: This script needs sudo to install the systemd service.${NC}"
    echo -e "${YELLOW}You may be prompted for your password.${NC}"
fi

# Add gunicorn to requirements.txt if not present
if ! grep -q "gunicorn" "$APP_DIR/requirements.txt"; then
    echo -e "${YELLOW}Adding gunicorn to requirements.txt...${NC}"
    echo "gunicorn==21.2.0" >> "$APP_DIR/requirements.txt"
    echo -e "${GREEN}Added gunicorn to requirements.txt${NC}"
else
    echo -e "${GREEN}gunicorn already in requirements.txt${NC}"
fi

# Create the systemd service file
SERVICE_FILE="/tmp/${APP_NAME}.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Gunicorn instance to serve Ancla application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
User=${USER}
Group=${GROUP}
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=/home/administrator/.local/bin/gunicorn --workers ${WORKERS} --bind ${BIND} wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Created service file${NC}"

# Install the service file
echo -e "${YELLOW}Installing systemd service file...${NC}"
sudo cp "$SERVICE_FILE" /etc/systemd/system/${APP_NAME}.service
sudo chmod 644 /etc/systemd/system/${APP_NAME}.service

# Reload systemd
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
sudo systemctl daemon-reload

# Enable the service
echo -e "${YELLOW}Enabling ${APP_NAME} service...${NC}"
sudo systemctl enable ${APP_NAME}.service

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Service installed at: /etc/systemd/system/${APP_NAME}.service"
echo ""
echo -e "${YELLOW}Commands to manage the service:${NC}"
echo -e "  Start:   sudo systemctl start ${APP_NAME}"
echo -e "  Stop:    sudo systemctl stop ${APP_NAME}"
echo -e "  Restart: sudo systemctl restart ${APP_NAME}"
echo -e "  Status:  sudo systemctl status ${APP_NAME}"
echo -e "  Logs:    sudo journalctl -u ${APP_NAME} -f"
echo ""
echo -e "${YELLOW}Want to start the service now? Run:${NC}"
echo -e "  sudo systemctl start ${APP_NAME}"
