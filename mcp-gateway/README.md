# MCP Gateway Server

A unified MCP API endpoint that manages multiple sub-MCP servers hosted through Docker instances. The gateway provides tool discovery while preserving context, with on-demand server lifecycle management.

## Features

- **Unified API**: Single endpoint for multiple MCP servers
- **On-demand spawning**: Servers start only when needed
- **Automatic cleanup**: Idle servers shut down after configurable timeout
- **Context preservation**: Tool descriptions exposed without revealing implementation
- **Docker isolation**: Each MCP server runs in isolated container
- **STDIO bridge**: Handles Docker container communication

## Quick Start

### Option 1: Auto-Start Installation (Recommended)

```bash
# Install as system service (auto-starts on boot)
./install-autostart.sh
```

This will:
- Build required Docker images
- Install systemd service
- Start the gateway automatically
- Enable auto-start on system boot

### Option 2: Manual Setup

#### 1. Build the Context7 image

```bash
cd servers/context7
docker build -t mcp-context7 .
cd ../..
```

#### 2. Start the gateway

```bash
docker-compose up -d
```

### 3. Test the gateway

```bash
# List available tools
curl http://localhost:8000/tools/list_available_tools

# Execute a tool
curl -X POST http://localhost:8000/tools/execute_tool \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "context7",
    "tool_name": "get_documentation", 
    "arguments": {"library": "react"}
  }'
```

## Configuration

### Server Registry (`servers.yaml`)

Define your MCP servers in `servers.yaml`:

```yaml
your_server:
  image: "your-mcp-image"
  command: ["node", "server.js"]
  description: "Your MCP server description"
  environment:
    API_KEY: "${YOUR_API_KEY}"
  idle_timeout: 300
  tools:
    - name: "your_tool"
      description: "Tool description"
      when_to_use: "When to use this tool"
      parameters:
        type: "object"
        properties:
          param1:
            type: "string"
        required: ["param1"]
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

## Available Endpoints

### Gateway Tools

- `list_available_tools()` - Lists all tools from all servers
- `execute_tool(server_id, tool_name, arguments)` - Executes a tool on specific server
- `list_active_servers()` - Shows currently running servers
- `stop_server(server_id)` - Manually stops a server

### HTTP API

The gateway runs as an HTTP server on port 8000:

- `GET /tools/list` - List all available tools
- `POST /tools/call` - Execute a specific tool

## Architecture

```
┌─────────────┐    HTTP     ┌─────────────┐    STDIO    ┌─────────────┐
│   Client    │ ──────────► │   Gateway   │ ──────────► │   Docker    │
│             │             │             │             │ MCP Server  │
└─────────────┘             └─────────────┘             └─────────────┘
                                   │
                                   ▼
                            ┌─────────────┐
                            │ servers.yaml│
                            │  Registry   │
                            └─────────────┘
```

1. **Client** sends tool request to gateway
2. **Gateway** checks if server is running, starts if needed
3. **Docker container** spawned with STDIO pipes
4. **JSON-RPC** messages exchanged via STDIO
5. **Response** returned to client
6. **Idle monitor** cleans up unused containers

## Adding New MCP Servers

1. **Create Docker image** for your MCP server
2. **Add entry** to `servers.yaml` 
3. **Build and tag** your Docker image
4. **Restart gateway** to reload configuration

### Example Server Structure

```
servers/your-server/
├── Dockerfile
├── server.py       # Your MCP server implementation  
└── requirements.txt
```

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run gateway directly
python gateway.py
```

### Building Custom Servers

Your MCP server must:

1. **Implement MCP protocol** with STDIO transport
2. **Accept JSON-RPC** messages on stdin
3. **Send responses** to stdout (one JSON object per line)
4. **Handle initialization** sequence properly

### Testing

```bash
# Check gateway health
curl http://localhost:8000/health

# Test tool discovery
curl http://localhost:8000/tools/list

# Monitor logs
docker-compose logs -f mcp-gateway
```

## Auto-Start Management

### Service Commands

```bash
# Check service status
sudo systemctl status mcp-gateway

# Start service
sudo systemctl start mcp-gateway

# Stop service  
sudo systemctl stop mcp-gateway

# Restart service
sudo systemctl restart mcp-gateway

# View logs
sudo journalctl -u mcp-gateway -f

# Disable auto-start
sudo systemctl disable mcp-gateway
```

### Uninstall Auto-Start

```bash
# Remove systemd service
./uninstall-autostart.sh
```

## Production Deployment

- Use environment variables for sensitive config
- Set appropriate resource limits in docker-compose.yml
- Monitor container resource usage
- Implement proper logging and metrics collection
- Consider using a reverse proxy (nginx/traefik)
- Service automatically restarts on failure and system boot

## Troubleshooting

### Common Issues

1. **Container won't start**: Check Docker image exists and is properly tagged
2. **STDIO communication fails**: Verify server implements MCP protocol correctly
3. **Tools not discovered**: Check servers.yaml syntax and tool definitions
4. **Permission denied**: Ensure gateway container has Docker socket access

### Debug Mode

Set `LOG_LEVEL=DEBUG` in environment to see detailed communication logs.

## License

MIT License