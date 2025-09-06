#!/bin/bash

# MCP Gateway Auto-Start Uninstallation Script
# This script removes the MCP Gateway auto-start service

set -e

SERVICE_NAME="mcp-gateway"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_PATH="$SYSTEMD_DIR/$SERVICE_NAME.service"

echo "🗑️  Uninstalling MCP Gateway Auto-Start Service..."

# Check if running as root for systemd operations
if [[ $EUID -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
    echo "ℹ️  This script requires sudo privileges to remove systemd service"
fi

# Stop the service if it's running
echo "🛑 Stopping MCP Gateway service..."
$SUDO systemctl stop "$SERVICE_NAME" 2>/dev/null || true

# Disable the service
echo "❌ Disabling auto-start..."
$SUDO systemctl disable "$SERVICE_NAME" 2>/dev/null || true

# Remove the service file
if [[ -f "$SERVICE_PATH" ]]; then
    echo "📋 Removing service file..."
    $SUDO rm "$SERVICE_PATH"
else
    echo "ℹ️  Service file not found: $SERVICE_PATH"
fi

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
$SUDO systemctl daemon-reload

# Stop any running containers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/docker-compose.yml" ]]; then
    echo "🐳 Stopping Docker containers..."
    cd "$SCRIPT_DIR"
    docker-compose down --remove-orphans || true
fi

echo ""
echo "✅ MCP Gateway Auto-Start Service Uninstalled!"
echo ""
echo "ℹ️  The MCP Gateway files are still available in:"
echo "   $SCRIPT_DIR"
echo ""
echo "🔧 To manually run the gateway:"
echo "   cd \"$SCRIPT_DIR\""
echo "   docker-compose up -d"