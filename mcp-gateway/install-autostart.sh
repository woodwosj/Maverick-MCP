#!/bin/bash

# MCP Gateway Auto-Start Installation Script
# This script sets up the MCP Gateway to automatically start on system boot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="mcp-gateway"
SERVICE_FILE="$SCRIPT_DIR/$SERVICE_NAME.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "🚀 Installing MCP Gateway Auto-Start Service..."

# Check if running as root for systemd operations
if [[ $EUID -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
    echo "ℹ️  This script requires sudo privileges to install systemd service"
fi

# Verify docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Check if service file exists
if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

# Stop any running containers first
echo "🛑 Stopping any running MCP Gateway containers..."
cd "$SCRIPT_DIR"
docker-compose down --remove-orphans || true

# Build the Context7 image if it doesn't exist
echo "🔨 Building Context7 Docker image..."
cd "$SCRIPT_DIR/servers/context7"
docker build -t mcp-context7 . --quiet

# Return to main directory
cd "$SCRIPT_DIR"

# Create logs directory
mkdir -p logs

# Copy service file to systemd directory
echo "📋 Installing systemd service..."
$SUDO cp "$SERVICE_FILE" "$SYSTEMD_DIR/"

# Update the WorkingDirectory in the service file to use absolute path
$SUDO sed -i "s|WorkingDirectory=.*|WorkingDirectory=$SCRIPT_DIR|g" "$SYSTEMD_DIR/$SERVICE_NAME.service"

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
$SUDO systemctl daemon-reload

# Enable the service to start on boot
echo "✅ Enabling MCP Gateway service for auto-start..."
$SUDO systemctl enable "$SERVICE_NAME"

# Start the service now
echo "▶️  Starting MCP Gateway service..."
$SUDO systemctl start "$SERVICE_NAME"

# Wait a moment for startup
sleep 3

# Check service status
echo "📊 Service Status:"
$SUDO systemctl status "$SERVICE_NAME" --no-pager -l

echo ""
echo "✅ MCP Gateway Auto-Start Installation Complete!"
echo ""
echo "🎯 Service Commands:"
echo "   Start:   sudo systemctl start $SERVICE_NAME"
echo "   Stop:    sudo systemctl stop $SERVICE_NAME" 
echo "   Restart: sudo systemctl restart $SERVICE_NAME"
echo "   Status:  sudo systemctl status $SERVICE_NAME"
echo "   Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🌐 Gateway URL: http://localhost:8000"
echo ""
echo "🧪 Test the service:"
echo "   curl http://localhost:8000/tools/list"

# Test connectivity
echo ""
echo "🔍 Testing gateway connectivity..."
sleep 2
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Gateway is responding on port 8000"
else
    echo "⚠️  Gateway may still be starting up. Check with:"
    echo "   sudo systemctl status $SERVICE_NAME"
    echo "   sudo journalctl -u $SERVICE_NAME -f"
fi