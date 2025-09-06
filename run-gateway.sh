#!/bin/bash
# STDIO MCP Gateway for Claude Code integration via Docker container
# Runs gateway in STDIO mode inside Docker environment

cd "/home/loomworks3/MCP Library"

# Check if gateway container is running
CONTAINER_ID=$(docker ps -q -f name=mcp-gateway)
if [ -z "$CONTAINER_ID" ]; then
    echo "Error: MCP Gateway container not running" >&2
    exit 1
fi

# Copy STDIO gateway script to container and run it
docker cp mcp-stdio-gateway.py "$CONTAINER_ID":/app/mcp-stdio-gateway.py
exec docker exec -i "$CONTAINER_ID" python mcp-stdio-gateway.py