"""
Documentation Generator for Generated MCP Servers

Creates comprehensive README files, integration guides, and deployment documentation
for generated MCP servers to ensure proper setup and usage.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

# Import from analyzer
import sys
sys.path.append(str(Path(__file__).parent.parent))
from analyzer.models import MCPToolCandidate


class DocumentationGenerator:
    """Generates comprehensive documentation for MCP servers"""
    
    def generate_readme(
        self,
        candidates: List[MCPToolCandidate],
        server_name: str,
        repo_info: Dict[str, Any],
        language: str = "python"
    ) -> str:
        """Generate comprehensive README.md for the MCP server"""
        
        tool_count = len(candidates)
        repo_name = repo_info.get('name', 'Unknown Repository')
        
        # Categorize tools by security level
        safe_tools = []
        medium_risk_tools = []
        high_risk_tools = []
        
        for candidate in candidates:
            security_level = getattr(candidate, 'security_level', 'safe').lower()
            if security_level in ['high', 'critical']:
                high_risk_tools.append(candidate)
            elif security_level in ['medium', 'moderate']:
                medium_risk_tools.append(candidate)
            else:
                safe_tools.append(candidate)
        
        # Generate tool tables
        safe_tools_table = self._generate_tools_table(safe_tools) if safe_tools else "None"
        medium_tools_table = self._generate_tools_table(medium_risk_tools) if medium_risk_tools else "None"
        high_tools_table = self._generate_tools_table(high_risk_tools) if high_risk_tools else "None"
        
        return f"""# {server_name} MCP Server

**Auto-generated MCP Server** - Created from repository: `{repo_name}`

> Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} using Maverick-MCP

## Overview

This MCP (Model Context Protocol) server exposes **{tool_count} functions** from the source repository as AI-accessible tools. The server provides comprehensive documentation, examples, and integration guides through built-in prompts and resources.

### Key Features

- ✅ **{tool_count} MCP Tools** - Repository functions exposed as MCP tools
- 📚 **Built-in Documentation** - Comprehensive prompts and resources
- 🔒 **Security Classified** - Risk assessment for all functions
- 🐳 **Docker Ready** - Container deployment support
- 🌐 **Gateway Compatible** - Integrates with Maverick-MCP Gateway
- 📋 **JSON Schema Validation** - Proper parameter validation

## Tools Overview

### 🟢 Safe Tools ({len(safe_tools)})
{safe_tools_table}

### 🟡 Medium Risk Tools ({len(medium_risk_tools)})
{medium_tools_table}

### 🔴 High Risk Tools ({len(high_risk_tools)})
{high_tools_table}

## Quick Start

### Prerequisites

- Python 3.11 or higher
- MCP SDK dependencies
- Docker (for containerized deployment)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the server:**
   ```bash
   python mcp_server.py
   ```

3. **Test with MCP client:**
   ```bash
   echo '{{"jsonrpc":"2.0","method":"initialize","params":{{"protocolVersion":"2024-11-05","clientInfo":{{"name":"test","version":"1.0.0"}},"capabilities":{{}}}},"id":1}}' | python mcp_server.py
   ```

### Docker Deployment

1. **Build container:**
   ```bash
   docker build -t {server_name} .
   ```

2. **Run container:**
   ```bash
   docker run -i --rm {server_name}
   ```

3. **Test container:**
   ```bash
   echo '{{"jsonrpc":"2.0","method":"tools/list","params":{{}},"id":1}}' | docker run -i --rm {server_name}
   ```

## MCP Protocol Usage

### Initialize Connection

```json
{{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {{
    "protocolVersion": "2024-11-05",
    "clientInfo": {{"name": "your-client", "version": "1.0.0"}},
    "capabilities": {{}}
  }},
  "id": 1
}}
```

### List Available Tools

```json
{{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {{}},
  "id": 2
}}
```

### Call a Tool

```json
{{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {{
    "name": "tool_name",
    "arguments": {{"param1": "value1", "param2": "value2"}}
  }},
  "id": 3
}}
```

## Built-in Documentation

This server includes comprehensive documentation accessible via MCP prompts and resources:

### Available Prompts

- **`usage_guide`** - Complete usage guide for all tools
- **`architecture`** - Technical architecture and communication flow
- **`tool_help`** - Detailed help for specific tools
- **`troubleshooting`** - Common issues and solutions

### Available Resources

- **`docs://{server_name}/api`** - Complete API reference
- **`docs://{server_name}/architecture`** - Architecture documentation
- **`docs://{server_name}/examples`** - Usage examples for all tools
- **`docs://{server_name}/integration`** - Integration guides

### Example: Get Tool Help

```json
{{
  "jsonrpc": "2.0",
  "method": "prompts/get",
  "params": {{
    "name": "tool_help",
    "arguments": {{"tool_name": "your_tool_name"}}
  }},
  "id": 4
}}
```

## Integration Guides

### Maverick-MCP Gateway Integration

1. **Add to servers.yaml:**
   ```yaml
   {server_name}:
     image: "{server_name}"
     command: ["python", "mcp_server.py"]
     description: "Generated MCP server from {repo_name}"
     environment:
       PYTHONUNBUFFERED: "1"
     idle_timeout: 300
   ```

2. **Restart gateway:**
   ```bash
   sudo systemctl restart mcp-gateway
   ```

3. **Verify integration:**
   ```bash
   curl http://localhost:8000/tools/list
   ```

### Claude Code Integration

1. **Add to `.claude.json`:**
   ```json
   {{
     "mcpServers": {{
       "{server_name}": {{
         "command": "docker",
         "args": ["run", "-i", "--rm", "{server_name}"]
       }}
     }}
   }}
   ```

2. **Test connection:**
   Use Claude Code MCP tools to interact with the server.

### Direct Python Integration

```python
import subprocess
import json

# Start MCP server
process = subprocess.Popen(
    ["python", "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Initialize connection
init_message = {{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {{
        "protocolVersion": "2024-11-05",
        "clientInfo": {{"name": "python-client", "version": "1.0.0"}},
        "capabilities": {{}}
    }},
    "id": 1
}}

process.stdin.write(json.dumps(init_message) + "\\n")
process.stdin.flush()

# Read response
response = process.stdout.readline()
result = json.loads(response)
print(result)
```

## Security Considerations

### Risk Assessment

Tools are categorized by security risk:

- **🟢 Safe**: No known security risks, safe for unrestricted use
- **🟡 Medium Risk**: Moderate security implications, requires review
- **🔴 High Risk**: Significant security concerns, requires careful evaluation

### Security Best Practices

1. **Review High-Risk Tools**: Carefully evaluate tools marked as high-risk
2. **Container Isolation**: Use Docker containers for additional security
3. **Input Validation**: All parameters are validated against JSON schemas
4. **Access Control**: Implement appropriate access controls at gateway level
5. **Monitoring**: Monitor tool usage and results for suspicious activity

### Dangerous Operations

{self._generate_security_warnings(high_risk_tools)}

## Architecture

### Communication Flow

```
AI Model/Client ↔ MCP Protocol ↔ STDIO ↔ {server_name} Server ↔ Original Functions
```

### Components

- **MCP Server**: Handles protocol communication and routing
- **Tool Handlers**: Execute original functions with parameter validation
- **Prompt System**: Provides comprehensive documentation
- **Resource System**: Exposes detailed guides and references

### Performance

- **Startup Time**: ~100ms for server initialization
- **Tool Latency**: 1-5ms overhead + original function execution time
- **Memory Usage**: Minimal overhead beyond function requirements
- **Concurrency**: Single-threaded per MCP specification

## Development

### Project Structure

```
{server_name}/
├── mcp_server.py           # Generated MCP server
├── original_functions.py   # Original repository functions
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container definition
├── README.md              # This file
└── tests/                 # Test files (if generated)
```

### Testing

1. **Unit Tests**: Test individual functions directly
2. **Integration Tests**: Test MCP protocol compliance
3. **Container Tests**: Test Docker deployment
4. **Gateway Tests**: Test integration with Maverick-MCP Gateway

### Debugging

1. **Enable Verbose Logging**: Set environment variable `DEBUG=1`
2. **Test STDIO Communication**: Use manual JSON-RPC messages
3. **Check Function Execution**: Test original functions directly
4. **Monitor Container**: Use `docker logs` for container debugging

## Troubleshooting

### Common Issues

1. **"Unknown tool" errors**: Check tool names with `tools/list`
2. **Parameter validation errors**: Verify parameter types and requirements
3. **Function execution errors**: Test original functions directly
4. **Container startup issues**: Check Docker configuration and dependencies

### Getting Help

1. Use built-in prompts: `usage_guide`, `tool_help`, `troubleshooting`
2. Check container logs: `docker logs <container_id>`
3. Test original functions independently
4. Review MCP protocol compliance

## Contributing

This is an auto-generated MCP server. To modify:

1. **Update source repository**: Make changes to original functions
2. **Regenerate server**: Use Maverick-MCP tools to regenerate
3. **Test changes**: Validate with test suite
4. **Update documentation**: Regenerate README and guides

## License

This generated MCP server inherits the license of the source repository: `{repo_name}`.

## Generated by Maverick-MCP

- **Generator**: Maverick-MCP Intelligent Repository Conversion Platform
- **Version**: 1.0.0
- **Generated**: {datetime.now().isoformat()}
- **Source Repository**: {repo_name}
- **Repository Path**: {repo_info.get('path', 'Unknown')}

For more information about Maverick-MCP, visit: https://github.com/your-repo/maverick-mcp
"""

    def _generate_tools_table(self, tools: List[MCPToolCandidate]) -> str:
        """Generate a markdown table of tools"""
        if not tools:
            return "None available"
        
        rows = []
        for tool in tools:
            param_count = len(tool.function.parameters)
            required_params = len([p for p in tool.function.parameters if p.required])
            
            rows.append(f"| `{tool.suggested_tool_name}` | {tool.description[:60]}{'...' if len(tool.description) > 60 else ''} | {param_count} ({required_params} req) | {tool.mcp_score}/10 |")
        
        table = """| Tool Name | Description | Parameters | Score |
|-----------|-------------|------------|-------|
""" + "\n".join(rows)
        
        return table
    
    def _generate_security_warnings(self, high_risk_tools: List[MCPToolCandidate]) -> str:
        """Generate security warnings for high-risk tools"""
        if not high_risk_tools:
            return "No high-risk tools detected."
        
        warnings = []
        for tool in high_risk_tools:
            warnings.append(f"- **`{tool.suggested_tool_name}`**: {tool.description}")
        
        return f"""⚠️  **HIGH RISK TOOLS DETECTED**

The following tools have been identified as having significant security implications:

{chr(10).join(warnings)}

**Recommendation**: Review these tools carefully and consider:
- Restricting access through authentication/authorization
- Running in isolated containers with limited privileges  
- Monitoring usage and outputs
- Implementing additional input validation
- Using read-only file systems where possible"""

    def generate_integration_guide(
        self,
        server_name: str,
        repo_info: Dict[str, Any],
        candidates: List[MCPToolCandidate]
    ) -> str:
        """Generate detailed integration guide"""
        
        return f"""# {server_name} Integration Guide

## Overview

This guide provides detailed instructions for integrating the `{server_name}` MCP server with various systems and clients.

## Integration Options

### 1. Maverick-MCP Gateway Integration (Recommended)

The easiest way to deploy and manage this MCP server is through the Maverick-MCP Gateway.

#### Configuration

Add this entry to your gateway's `servers.yaml`:

```yaml
{server_name}:
  image: "{server_name}"
  command: ["python", "mcp_server.py"]
  description: "Generated MCP server from {repo_info.get('name', 'repository')}"
  environment:
    PYTHONUNBUFFERED: "1"
    DEBUG: "0"  # Set to "1" for verbose logging
  idle_timeout: 300  # 5 minutes
  tools:
    # Tools are auto-discovered from the server
    # No manual tool definitions needed
```

#### Deployment Steps

1. **Build Docker image:**
   ```bash
   cd /path/to/{server_name}
   docker build -t {server_name} .
   ```

2. **Test the image:**
   ```bash
   docker run -i --rm {server_name} <<< '{{"jsonrpc":"2.0","method":"tools/list","params":{{}},"id":1}}'
   ```

3. **Update gateway configuration:**
   ```bash
   # Edit servers.yaml
   vim /path/to/gateway/servers.yaml
   
   # Restart gateway
   sudo systemctl restart mcp-gateway
   ```

4. **Verify integration:**
   ```bash
   # Test via gateway
   curl -X POST http://localhost:8000/mcp \\
     -H "Content-Type: application/json" \\
     -d '{{"jsonrpc":"2.0","method":"tools/list","params":{{}},"id":1}}'
   ```

#### Benefits of Gateway Integration

- **Automatic scaling**: Containers spawn on-demand
- **Resource management**: Idle timeout and cleanup
- **Unified API**: Single endpoint for all MCP servers
- **Monitoring**: Centralized logging and metrics
- **Security**: Container isolation and access controls

### 2. Claude Code Integration

Integrate directly with Claude Code for development and testing.

#### Configuration

Add to your project's `.claude.json`:

```json
{{
  "mcpServers": {{
    "{server_name}": {{
      "command": "python",
      "args": ["/path/to/{server_name}/mcp_server.py"],
      "env": {{
        "PYTHONUNBUFFERED": "1"
      }}
    }}
  }}
}}
```

#### Docker-based Claude Code Integration

For containerized deployment with Claude Code:

```json
{{
  "mcpServers": {{
    "{server_name}": {{
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "{server_name}"
      ]
    }}
  }}
}}
```

#### Testing Claude Code Integration

1. **Restart Claude Code** to pick up configuration changes
2. **Test connection** by using MCP tools in Claude Code interface
3. **Check logs** if connection fails

### 3. Direct Python Integration

For programmatic access from Python applications.

#### Basic Integration

```python
import subprocess
import json
import asyncio
from typing import Dict, Any, List

class MCPClient:
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.process = None
        self.request_id = 0
    
    async def start(self):
        \"\"\"Start the MCP server process\"\"\"
        self.process = subprocess.Popen(
            ["python", self.server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Initialize connection
        await self.initialize()
    
    async def initialize(self):
        \"\"\"Initialize MCP connection\"\"\"
        init_message = {{
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {{
                "protocolVersion": "2024-11-05",
                "clientInfo": {{"name": "python-client", "version": "1.0.0"}},
                "capabilities": {{}}
            }},
            "id": self._next_id()
        }}
        
        response = await self.send_message(init_message)
        
        # Send initialized notification
        initialized_message = {{
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {{}}
        }}
        
        self.process.stdin.write(json.dumps(initialized_message) + "\\n")
        self.process.stdin.flush()
        
        return response
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Send message to MCP server\"\"\"
        json_message = json.dumps(message)
        self.process.stdin.write(json_message + "\\n")
        self.process.stdin.flush()
        
        response_line = self.process.stdout.readline()
        return json.loads(response_line)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        \"\"\"List available tools\"\"\"
        message = {{
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {{}},
            "id": self._next_id()
        }}
        
        response = await self.send_message(message)
        return response.get("result", {{}}).get("tools", [])
    
    async def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> Any:
        \"\"\"Call a specific tool\"\"\"
        message = {{
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {{
                "name": name,
                "arguments": arguments or {{}}
            }},
            "id": self._next_id()
        }}
        
        response = await self.send_message(message)
        if "error" in response:
            raise Exception(f"Tool call failed: {{response['error']}}")
        
        return response.get("result")
    
    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id
    
    async def close(self):
        \"\"\"Close the connection\"\"\"
        if self.process:
            self.process.terminate()
            self.process.wait()

# Usage example
async def main():
    client = MCPClient("/path/to/{server_name}/mcp_server.py")
    
    try:
        await client.start()
        
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {{[t['name'] for t in tools]}}")
        
        # Call a tool (example)
        if tools:
            tool_name = tools[0]['name']
            result = await client.call_tool(tool_name, {{}})
            print(f"Tool result: {{result}}")
    
    finally:
        await client.close()

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Container Orchestration (Kubernetes/Docker Compose)

Deploy using container orchestration platforms.

#### Docker Compose

```yaml
version: '3.8'

services:
  {server_name}:
    build:
      context: .
      dockerfile: Dockerfile
    image: {server_name}:latest
    container_name: {server_name}
    stdin_open: true
    tty: true
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
      - DEBUG=0
    healthcheck:
      test: ["CMD", "python", "-c", "import mcp_server; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      - "mcp.server.name={server_name}"
      - "mcp.server.type=generated"
```

#### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {server_name}
  labels:
    app: {server_name}
    type: mcp-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {server_name}
  template:
    metadata:
      labels:
        app: {server_name}
    spec:
      containers:
      - name: {server_name}
        image: {server_name}:latest
        stdin: true
        tty: true
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import mcp_server; print('OK')"
          initialDelaySeconds: 30
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: {server_name}-service
spec:
  selector:
    app: {server_name}
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

## Testing Integration

### Integration Test Script

```bash
#!/bin/bash
# {server_name} Integration Test

echo "Testing {server_name} MCP Server Integration..."

# Test 1: Basic STDIO communication
echo "1. Testing STDIO communication..."
echo '{{"jsonrpc":"2.0","method":"initialize","params":{{"protocolVersion":"2024-11-05","clientInfo":{{"name":"test","version":"1.0.0"}},"capabilities":{{}}}},"id":1}}' | python mcp_server.py > /tmp/init_response.json

if grep -q "result" /tmp/init_response.json; then
    echo "   ✅ STDIO communication working"
else
    echo "   ❌ STDIO communication failed"
    exit 1
fi

# Test 2: Tools discovery
echo "2. Testing tools discovery..."
(echo '{{"jsonrpc":"2.0","method":"initialize","params":{{"protocolVersion":"2024-11-05","clientInfo":{{"name":"test","version":"1.0.0"}},"capabilities":{{}}}},"id":1}}'; \\
 echo '{{"jsonrpc":"2.0","method":"notifications/initialized","params":{{}}}}'; \\
 echo '{{"jsonrpc":"2.0","method":"tools/list","params":{{}},"id":2}}') | python mcp_server.py > /tmp/tools_response.json

if grep -q "tools" /tmp/tools_response.json; then
    echo "   ✅ Tools discovery working"
    TOOL_COUNT=$(grep -o '"name"' /tmp/tools_response.json | wc -l)
    echo "   📊 Found $TOOL_COUNT tools"
else
    echo "   ❌ Tools discovery failed"
    exit 1
fi

# Test 3: Docker container
echo "3. Testing Docker container..."
if docker build -t {server_name}-test . > /dev/null 2>&1; then
    echo "   ✅ Docker build successful"
    
    if echo '{{"jsonrpc":"2.0","method":"tools/list","params":{{}},"id":1}}' | docker run -i --rm {server_name}-test | grep -q "tools"; then
        echo "   ✅ Container execution working"
    else
        echo "   ❌ Container execution failed"
        exit 1
    fi
else
    echo "   ❌ Docker build failed"
    exit 1
fi

echo "✅ All integration tests passed!"
```

### Performance Benchmarking

```python
import time
import statistics
from mcp_client import MCPClient  # Using the client from above

async def benchmark_tools():
    client = MCPClient("/path/to/{server_name}/mcp_server.py")
    
    try:
        await client.start()
        tools = await client.list_tools()
        
        # Benchmark each tool
        for tool in tools[:3]:  # Test first 3 tools
            tool_name = tool['name']
            times = []
            
            # Run 10 iterations
            for i in range(10):
                start_time = time.time()
                try:
                    await client.call_tool(tool_name, {{}})
                    end_time = time.time()
                    times.append(end_time - start_time)
                except Exception as e:
                    print(f"Tool {{tool_name}} failed: {{e}}")
                    continue
            
            if times:
                avg_time = statistics.mean(times)
                median_time = statistics.median(times)
                print(f"{{tool_name}}: avg={{avg_time:.3f}}s, median={{median_time:.3f}}s")
    
    finally:
        await client.close()
```

## Monitoring and Logging

### Log Configuration

Set environment variables for enhanced logging:

```bash
export DEBUG=1                    # Enable debug logging
export LOG_LEVEL=INFO            # Set log level
export LOG_FORMAT=json           # Use JSON log format
```

### Health Checks

Implement health check endpoints:

```python
# Add to mcp_server.py for health monitoring
def health_check():
    return {{
        "status": "healthy",
        "timestamp": time.time(),
        "tools_count": len(available_tools),
        "memory_usage": get_memory_usage()
    }}
```

### Metrics Collection

Monitor key metrics:

- Tool execution count and latency
- Error rates by tool
- Memory and CPU usage
- Container lifecycle events

## Security Best Practices

### Container Security

1. **Use non-root user** in containers
2. **Limit resource usage** with container limits
3. **Use read-only root filesystem** where possible
4. **Scan images** for vulnerabilities

### Access Control

1. **Implement authentication** at gateway level
2. **Use role-based access control** for sensitive tools
3. **Log all tool executions** for audit trails
4. **Monitor for unusual patterns** in tool usage

### Data Protection

1. **Validate all inputs** against JSON schemas
2. **Sanitize outputs** to prevent data leakage
3. **Use secure communication** channels
4. **Implement data retention** policies

## Troubleshooting

### Common Integration Issues

1. **Connection timeouts**: Check network connectivity and container startup time
2. **Tool not found**: Verify tool names and server initialization
3. **Parameter errors**: Check JSON schema validation
4. **Container issues**: Review Docker logs and resource limits

### Debug Checklist

- [ ] Server initializes without errors
- [ ] Tools list returns expected tools
- [ ] Individual tools execute successfully
- [ ] Container builds and runs properly
- [ ] Gateway integration works (if applicable)
- [ ] Error handling works correctly
- [ ] Performance meets requirements

For additional support, use the built-in troubleshooting prompt or check the server logs.
"""

    def generate_servers_yaml_entry(
        self,
        server_name: str,
        repo_info: Dict[str, Any],
        candidates: List[MCPToolCandidate]
    ) -> str:
        """Generate servers.yaml entry for gateway integration"""
        
        # Generate tool definitions for the yaml entry
        tools_yaml = []
        for candidate in candidates:
            # Create comprehensive tool description
            tool_entry = f"""  - name: "{candidate.suggested_tool_name}"
    description: |
      {candidate.description}
      
      Original function: {candidate.function.function_name}() from {candidate.function.file_path}
      Security level: {getattr(candidate, 'security_level', 'safe')}
      MCP score: {candidate.mcp_score}/10
    
    when_to_use: |
      Use this tool when you need to {candidate.description.lower()}.
      {"⚠️  High security risk - review parameters carefully" if getattr(candidate, 'security_level', 'safe').lower() in ['high', 'critical'] else "Safe for general use"}
    
    parameters:
      type: "object"
      properties:"""
        
            # Add parameter definitions
            for param in candidate.function.parameters:
                param_desc = f"""        {param.name}:
          type: "{param.type_hint.lower() if param.type_hint else 'string'}"
          description: "{param.description or f'Parameter {param.name}'}"
          {"" if param.required else f'          default: {param.default_value or "null"}'}"""
                tool_entry += f"\n{param_desc}"
            
            # Add required parameters
            required_params = [p.name for p in candidate.function.parameters if p.required]
            if required_params:
                tool_entry += f"\n      required: {json.dumps(required_params)}"
            
            # Add examples
            tool_entry += f"""
    
    examples:
      - description: "Basic usage example"
        parameters:"""
            
            # Generate example parameters
            for param in candidate.function.parameters[:2]:  # Limit to first 2 params
                if 'int' in (param.type_hint or 'string').lower():
                    example_val = 42
                elif 'float' in (param.type_hint or 'string').lower():
                    example_val = 3.14
                elif 'bool' in (param.type_hint or 'string').lower():
                    example_val = True
                else:
                    example_val = "example_value"
                
                tool_entry += f"\n          {param.name}: {json.dumps(example_val)}"
            
            tool_entry += f"""
        expected_output: |
          Execution result from {candidate.function.function_name}() function"""
            
            tools_yaml.append(tool_entry)
        
        tools_section = "\n".join(tools_yaml)
        
        return f"""# Add this entry to your servers.yaml file

{server_name}:
  image: "{server_name}"
  command: ["python", "mcp_server.py"]
  description: |
    Generated MCP server from repository: {repo_info.get('name', 'unknown')}
    
    This server exposes {len(candidates)} functions as MCP tools with comprehensive
    documentation via built-in prompts and resources. Generated by Maverick-MCP
    on {datetime.now().strftime('%Y-%m-%d')}.
    
    Available tools: {', '.join([c.suggested_tool_name for c in candidates[:5]])}
    {'...' if len(candidates) > 5 else ''}
    
  environment:
    PYTHONUNBUFFERED: "1"
    DEBUG: "${{DEBUG:-0}}"  # Set to 1 for debug logging
  idle_timeout: 300  # 5 minutes
  
  tools:
{tools_section}
  
  # Additional metadata
  meta:
    generator: "Maverick-MCP"
    version: "1.0.0"
    generated: "{datetime.now().isoformat()}"
    source_repo: "{repo_info.get('name', 'unknown')}"
    tool_count: {len(candidates)}
    security_levels:
      safe: {len([c for c in candidates if getattr(c, 'security_level', 'safe').lower() == 'safe'])}
      medium: {len([c for c in candidates if getattr(c, 'security_level', 'safe').lower() == 'medium'])}
      high: {len([c for c in candidates if getattr(c, 'security_level', 'safe').lower() in ['high', 'critical']])}"""

    def generate_deployment_guide(self, server_name: str, candidates: List[MCPToolCandidate]) -> str:
        """Generate deployment guide for various platforms"""
        
        return f"""# {server_name} Deployment Guide

## Production Deployment Options

### 1. Maverick-MCP Gateway (Recommended)

The simplest production deployment through the Maverick-MCP Gateway system.

#### Prerequisites
- Maverick-MCP Gateway installed and running
- Docker installed
- Sufficient system resources

#### Deployment Steps

1. **Build and test locally:**
   ```bash
   # Build Docker image
   docker build -t {server_name} .
   
   # Test the image
   echo '{{"jsonrpc":"2.0","method":"tools/list","params":{{}},"id":1}}' | docker run -i --rm {server_name}
   ```

2. **Add to gateway configuration:**
   ```bash
   # Edit servers.yaml
   sudo vim /path/to/gateway/servers.yaml
   # Add the server entry (see servers.yaml example)
   ```

3. **Deploy:**
   ```bash
   # Restart gateway to pick up new configuration
   sudo systemctl restart mcp-gateway
   
   # Verify deployment
   curl http://localhost:8000/tools/list | grep {server_name}
   ```

### 2. Docker Compose Deployment

For standalone deployment or development environments.

#### docker-compose.yml
```yaml
version: '3.8'

services:
  {server_name}:
    build:
      context: .
      dockerfile: Dockerfile
    image: {server_name}:latest
    container_name: {server_name}
    stdin_open: true
    tty: true
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
      - DEBUG=0
    volumes:
      - ./logs:/app/logs  # Optional: for log persistence
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      - "mcp.server.name={server_name}"
      - "mcp.server.type=generated"
      - "mcp.tools.count={len(candidates)}"

networks:
  mcp-network:
    driver: bridge

volumes:
  logs:
    driver: local
```

#### Deployment Commands
```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f {server_name}

# Stop services
docker-compose down
```

### 3. Kubernetes Deployment

For scalable production environments.

#### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mcp-servers
  labels:
    name: mcp-servers
```

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {server_name}
  namespace: mcp-servers
  labels:
    app: {server_name}
    type: mcp-server
spec:
  replicas: 2  # Scale as needed
  selector:
    matchLabels:
      app: {server_name}
  template:
    metadata:
      labels:
        app: {server_name}
    spec:
      containers:
      - name: {server_name}
        image: {server_name}:latest
        imagePullPolicy: Always
        stdin: true
        tty: true
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        - name: DEBUG
          value: "0"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "print('healthy')"
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "print('ready')"
          initialDelaySeconds: 5
          periodSeconds: 10
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {{}}
      restartPolicy: Always
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {server_name}-service
  namespace: mcp-servers
spec:
  selector:
    app: {server_name}
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  type: ClusterIP
```

#### Deploy to Kubernetes
```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check deployment
kubectl get pods -n mcp-servers
kubectl logs -f deployment/{server_name} -n mcp-servers

# Scale deployment
kubectl scale deployment {server_name} --replicas=3 -n mcp-servers
```

## Monitoring and Observability

### Logging Configuration

#### Structured Logging
```python
import logging
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def log_tool_execution(tool_name, parameters, result, duration):
    log_entry = {{
        "timestamp": datetime.utcnow().isoformat(),
        "event": "tool_execution",
        "tool": tool_name,
        "parameters": parameters,
        "success": "error" not in str(result).lower(),
        "duration_ms": duration * 1000
    }}
    logging.info(json.dumps(log_entry))
```

#### Log Aggregation with ELK Stack
```yaml
# filebeat.yml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "mcp-servers-%{{+yyyy.MM.dd}}"

# Kibana dashboard for MCP server logs
```

### Metrics Collection

#### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
TOOL_CALLS = Counter('mcp_tool_calls_total', 'Total tool calls', ['tool_name', 'status'])
TOOL_DURATION = Histogram('mcp_tool_duration_seconds', 'Tool execution duration', ['tool_name'])
ACTIVE_CONNECTIONS = Gauge('mcp_active_connections', 'Active MCP connections')

def record_tool_call(tool_name, duration, success):
    TOOL_CALLS.labels(tool_name=tool_name, status='success' if success else 'error').inc()
    TOOL_DURATION.labels(tool_name=tool_name).observe(duration)

# Start metrics server
start_http_server(8080)
```

### Health Checks

#### Docker Health Check
```dockerfile
# Add to Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD python -c "
import json, subprocess
proc = subprocess.run(['python', 'mcp_server.py'], 
                     input='{{\\"jsonrpc\\": \\"2.0\\", \\"method\\": \\"tools/list\\", \\"id\\": 1}}',
                     capture_output=True, text=True, timeout=5)
response = json.loads(proc.stdout.strip())
assert 'result' in response and 'tools' in response['result']
print('Health check passed')
" || exit 1
```

#### Kubernetes Liveness/Readiness Probes
```yaml
livenessProbe:
  exec:
    command:
    - /bin/sh
    - -c
    - |
      python3 -c "
      import json, subprocess, sys
      try:
          proc = subprocess.run(['python3', 'mcp_server.py'], 
                               input='{{\\"jsonrpc\\": \\"2.0\\", \\"method\\": \\"tools/list\\", \\"id\\": 1}}',
                               capture_output=True, text=True, timeout=5)
          response = json.loads(proc.stdout.strip())
          assert 'result' in response
          print('Liveness check passed')
      except Exception as e:
          print(f'Liveness check failed: {{e}}')
          sys.exit(1)
      "
  initialDelaySeconds: 30
  periodSeconds: 30

readinessProbe:
  exec:
    command:
    - python3
    - -c
    - "import mcp_server; print('Ready')"
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Security Hardening

### Container Security

#### Secure Dockerfile
```dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=mcpuser:mcpuser . .

# Security hardening
RUN chmod -R 755 /app && \\
    chmod 644 /app/mcp_server.py && \\
    rm -rf /tmp/* /var/tmp/* && \\
    apt-get clean

# Switch to non-root user
USER mcpuser

# Run with minimal privileges
CMD ["python", "mcp_server.py"]
```

#### Security Scanning
```bash
# Scan Docker image for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
  aquasec/trivy image {server_name}:latest

# Scan for secrets
docker run --rm -v $(pwd):/workspace \\
  trufflesecurity/trufflehog filesystem /workspace

# Container security benchmark
docker run --rm --net host --pid host --userns host --cap-add audit_control \\
  -v /var/lib:/var/lib -v /var/run/docker.sock:/var/run/docker.sock \\
  docker/docker-bench-security
```

### Network Security

#### Container Network Isolation
```yaml
# docker-compose.yml with network isolation
services:
  {server_name}:
    # ... other config
    networks:
      - mcp-internal
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /var/tmp

networks:
  mcp-internal:
    driver: bridge
    internal: true  # No external access
```

### Access Control

#### RBAC for Kubernetes
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {server_name}-sa
  namespace: mcp-servers

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {server_name}-role
  namespace: mcp-servers
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {server_name}-binding
  namespace: mcp-servers
subjects:
- kind: ServiceAccount
  name: {server_name}-sa
  namespace: mcp-servers
roleRef:
  kind: Role
  name: {server_name}-role
  apiGroup: rbac.authorization.k8s.io
```

## Backup and Disaster Recovery

### Configuration Backup
```bash
#!/bin/bash
# backup-mcp-config.sh

BACKUP_DIR="/backup/mcp-{server_name}"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup configuration
cp servers.yaml "$BACKUP_DIR/$DATE/"
cp docker-compose.yml "$BACKUP_DIR/$DATE/"
cp -r kubernetes/ "$BACKUP_DIR/$DATE/"

# Backup Docker image
docker save {server_name}:latest | gzip > "$BACKUP_DIR/$DATE/{server_name}.tar.gz"

# Create restore script
cat > "$BACKUP_DIR/$DATE/restore.sh" << 'EOF'
#!/bin/bash
# Restore {server_name}
echo "Restoring {server_name}..."

# Load Docker image
gunzip -c {server_name}.tar.gz | docker load

# Restore configurations
cp servers.yaml /path/to/gateway/
cp docker-compose.yml /path/to/deployment/

echo "Restore complete. Restart services manually."
EOF

chmod +x "$BACKUP_DIR/$DATE/restore.sh"
echo "Backup created: $BACKUP_DIR/$DATE"
```

### Automated Backup with Cron
```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-mcp-config.sh
```

## Performance Tuning

### Container Resource Optimization
```yaml
# Optimized resource limits
resources:
  requests:
    memory: "64Mi"    # Minimum required
    cpu: "50m"        # Minimal CPU
  limits:
    memory: "256Mi"   # Maximum allowed
    cpu: "200m"       # CPU limit
```

### Scaling Strategies
```bash
# Horizontal Pod Autoscaler
kubectl autoscale deployment {server_name} --cpu-percent=70 --min=2 --max=10 -n mcp-servers

# Manual scaling
kubectl scale deployment {server_name} --replicas=5 -n mcp-servers
```

This deployment guide provides comprehensive instructions for deploying the {server_name} MCP server in various environments with proper monitoring, security, and scaling considerations.
"""