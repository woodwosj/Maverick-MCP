"""
MCP Prompt and Resource Generator

Generates MCP prompts and resources for enhanced documentation and usage guidance
in generated MCP servers. These provide detailed context beyond basic tool descriptions.
"""

from typing import List, Dict, Any
from pathlib import Path
import json

# Import from analyzer
import sys
sys.path.append(str(Path(__file__).parent.parent))
from analyzer.models import MCPToolCandidate


class PromptResourceGenerator:
    """Generates MCP prompts and resources for comprehensive documentation"""
    
    def generate_prompts(
        self, 
        candidates: List[MCPToolCandidate], 
        server_name: str, 
        repo_info: Dict[str, Any]
    ) -> str:
        """Generate MCP prompt handlers for the server"""
        
        prompts = []
        
        # Main usage guide prompt
        prompts.append(self._generate_usage_guide_prompt(candidates, server_name, repo_info))
        
        # Architecture explanation prompt
        # prompts.append(self._generate_architecture_prompt(server_name))
        
        # Tool-specific prompts
        # for candidate in candidates:
        #     prompts.append(self._generate_tool_prompt(candidate))
        
        # Troubleshooting prompt
        # prompts.append(self._generate_troubleshooting_prompt(server_name))
        
        return "\n".join(prompts)
    
    def generate_resources(
        self, 
        candidates: List[MCPToolCandidate], 
        server_name: str, 
        repo_info: Dict[str, Any]
    ) -> str:
        """Generate MCP resource handlers for the server"""
        
        resources = []
        
        # API documentation resource
        resources.append(self._generate_api_docs_resource(candidates, server_name))
        
        # Architecture diagram resource
        resources.append(self._generate_architecture_resource(server_name))
        
        # Examples resource
        resources.append(self._generate_examples_resource(candidates, server_name))
        
        # Integration guide resource
        resources.append(self._generate_integration_resource(server_name, repo_info))
        
        return "\n".join(resources)
    
    def _generate_usage_guide_prompt(
        self, 
        candidates: List[MCPToolCandidate], 
        server_name: str, 
        repo_info: Dict[str, Any]
    ) -> str:
        """Generate main usage guide prompt"""
        
        tool_list = []
        for candidate in candidates:
            tool_list.append(f"- **{candidate.suggested_tool_name}**: {candidate.description}")
        
        tools_section = "\\n".join(tool_list)
        
        return f"""@app.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    \"\"\"List available prompts for guidance and documentation\"\"\"
    return [
        types.Prompt(
            name="usage_guide",
            description="Complete usage guide for {server_name} MCP server",
            arguments=[
                types.PromptArgument(
                    name="topic",
                    description="Specific topic to focus on (optional)",
                    required=False
                )
            ]
        ),
        types.Prompt(
            name="architecture",
            description="Explain the MCP server architecture and communication flow"
        ),
        types.Prompt(
            name="tool_help",
            description="Get detailed help for a specific tool",
            arguments=[
                types.PromptArgument(
                    name="tool_name",
                    description="Name of the tool to get help for",
                    required=True
                )
            ]
        ),
        types.Prompt(
            name="troubleshooting",
            description="Troubleshooting guide for common issues"
        )
    ]

@app.get_prompt()
async def handle_get_prompt(
    name: str,
    arguments: dict[str, str] | None
) -> types.GetPromptResult:
    \"\"\"Handle prompt requests with detailed guidance\"\"\"
    
    if name == "usage_guide":
        topic = arguments.get("topic") if arguments else None
        content = f\\\"\\\"\\\"# {server_name} MCP Server Usage Guide

## Overview
This MCP server exposes functions from the repository: **{{repo_info.get('name', 'Unknown Repository')}}**

Generated from {{len(candidates)}} analyzed functions, this server provides AI-accessible tools for:

{{tools_section}}

## Quick Start

1. **Initialize Connection**: The MCP client will automatically handle initialization
2. **Discover Tools**: Use `tools/list` to see all available tools
3. **Call Tools**: Use `tools/call` with proper parameters

## Communication Architecture

This server uses STDIO-based MCP protocol:
```
AI Client <-> MCP Protocol <-> STDIO <-> {server_name} Server <-> Original Functions
```

## Available Tools ({{len(candidates)}} total)

{{self._generate_detailed_tool_list(candidates)}}

## Parameter Guidelines

- All parameters are validated before function execution
- Required parameters must be provided
- Optional parameters have documented defaults
- Error messages provide specific guidance for fixes

## Response Formats

All tools return structured responses in MCP TextContent format:
- Successful results include the actual function return value
- Errors include descriptive messages and troubleshooting hints
- Complex objects are JSON-formatted for readability

## Best Practices

1. **Parameter Validation**: Always check parameter requirements in tool descriptions
2. **Error Handling**: Read error messages carefully - they include specific fix instructions
3. **Performance**: Tools execute directly - no additional latency beyond function execution
4. **Security**: Functions maintain their original security characteristics

Need specific help? Use the `tool_help` prompt with a tool name for detailed guidance.
\\\"\\\"\\\"
        
        return types.GetPromptResult(
            description=f"Usage guide for {{server_name}}",
            messages=[types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=content)
            )]
        )
    
    elif name == "architecture":
        content = self._get_architecture_explanation(server_name)
        return types.GetPromptResult(
            description=f"Architecture explanation for {{server_name}}",
            messages=[types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=content)
            )]
        )
    
    elif name == "tool_help":
        tool_name = arguments.get("tool_name") if arguments else None
        if not tool_name:
            raise ValueError("tool_name argument is required for tool_help prompt")
        
        # Find the candidate by tool name
        candidate = None
        for c in candidates:
            if c.suggested_tool_name == tool_name:
                candidate = c
                break
        
        if not candidate:
            raise ValueError(f"Tool '{{tool_name}}' not found")
        
        content = self._generate_detailed_tool_help(candidate)
        return types.GetPromptResult(
            description=f"Help for {{tool_name}}",
            messages=[types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=content)
            )]
        )
    
    elif name == "troubleshooting":
        content = self._get_troubleshooting_guide(server_name)
        return types.GetPromptResult(
            description=f"Troubleshooting guide for {{server_name}}",
            messages=[types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=content)
            )]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {{name}}")
\"\"\""""
    
    def _generate_detailed_tool_list(self, candidates: List[MCPToolCandidate]) -> str:
        """Generate detailed list of all tools"""
        tool_details = []
        
        for candidate in candidates:
            # Extract parameter info
            params = []
            for param in candidate.function.parameters:
                param_desc = f"**{param.name}** ({param.type_hint or 'any'})"
                if param.required:
                    param_desc += " *required*"
                else:
                    param_desc += f" *optional* (default: {param.default_value or 'None'})"
                params.append(param_desc)
            
            param_section = "\n  - ".join(params) if params else "No parameters"
            
            tool_details.append(f"""### {candidate.suggested_tool_name}

**Description**: {candidate.description}

**Parameters**:
  - {param_section}

**Returns**: {candidate.function.return_type or 'Any'}

**MCP Score**: {candidate.mcp_score}/10

**Security Level**: {getattr(candidate, 'security_level', 'Unknown')}
""")
        
        return "\n\n".join(tool_details)
    
    def _generate_detailed_tool_help(self, candidate: MCPToolCandidate) -> str:
        """Generate detailed help for a specific tool"""
        
        # Parameter details
        param_details = []
        for param in candidate.function.parameters:
            detail = f"- **{param.name}** ({param.type}): {param.description or 'No description available'}"
            if param.required:
                detail += " **[REQUIRED]**"
            else:
                detail += f" [OPTIONAL - default: {param.default_value or 'None'}]"
            param_details.append(detail)
        
        param_section = "\n".join(param_details) if param_details else "No parameters required"
        
        # Usage examples
        examples = self._generate_tool_examples(candidate)
        
        return f"""# Detailed Help: {candidate.suggested_tool_name}

## Description
{candidate.description}

## Original Function
- **Source**: {candidate.function.file_path}
- **Line**: {candidate.function.line_number}
- **Function**: `{candidate.function.function_name}()`

## Parameters
{param_section}

## Return Type
{candidate.function.return_type or 'Any'}

## MCP Tool Information
- **Tool Name**: {candidate.suggested_tool_name}
- **MCP Score**: {candidate.mcp_score}/10
- **Security Level**: {getattr(candidate, 'security_level', 'Unknown')}

## Usage Examples

{examples}

## Error Handling

This tool will return error messages for:
- Missing required parameters
- Invalid parameter types
- Function execution exceptions
- Security violations (if applicable)

Error messages include specific guidance for resolution.

## Integration Notes

- Tool executes synchronously within the MCP server
- Results are automatically formatted for MCP protocol
- Complex return values are JSON-serialized for readability
- All original function security and validation characteristics are preserved

## Related Tools

{self._get_related_tools(candidate)}

Need more help? Check the usage_guide prompt for general guidance or troubleshooting prompt for common issues.
"""
    
    def _generate_tool_examples(self, candidate: MCPToolCandidate) -> str:
        """Generate usage examples for a tool"""
        examples = []
        
        # Basic example with minimal parameters
        required_params = [p for p in candidate.function.parameters if p.required]
        if required_params:
            example_params = {}
            for param in required_params:
                # Generate sample values based on type
                if 'int' in param.type.lower():
                    example_params[param.name] = 42
                elif 'float' in param.type.lower():
                    example_params[param.name] = 3.14
                elif 'str' in param.type.lower():
                    example_params[param.name] = "example"
                elif 'bool' in param.type.lower():
                    example_params[param.name] = True
                else:
                    example_params[param.name] = "value"
            
            examples.append(f"""### Basic Usage (Required Parameters Only)

```json
{{
  "name": "{candidate.suggested_tool_name}",
  "arguments": {json.dumps(example_params, indent=2)}
}}
```
""")
        
        # Example with all parameters
        if len(candidate.function.parameters) > len(required_params):
            all_params = {}
            for param in candidate.function.parameters:
                if 'int' in param.type.lower():
                    all_params[param.name] = 42
                elif 'float' in param.type.lower():
                    all_params[param.name] = 3.14
                elif 'str' in param.type.lower():
                    all_params[param.name] = "example"
                elif 'bool' in param.type.lower():
                    all_params[param.name] = True
                else:
                    all_params[param.name] = "value"
            
            examples.append(f"""### Complete Usage (All Parameters)

```json
{{
  "name": "{candidate.suggested_tool_name}",
  "arguments": {json.dumps(all_params, indent=2)}
}}
```
""")
        
        return "\n\n".join(examples) if examples else "No parameter examples available"
    
    def _get_related_tools(self, candidate: MCPToolCandidate) -> str:
        """Get related tools information"""
        return "Check the usage_guide prompt to see all available tools in this server."
    
    def _get_architecture_explanation(self, server_name: str) -> str:
        """Get detailed architecture explanation"""
        return f"""# {server_name} MCP Server Architecture

## Communication Flow

```
AI Model/Claude <-> MCP Client <-> STDIO Protocol <-> {server_name} Server <-> Original Functions
```

### Layer Breakdown

1. **AI Model/Claude**: Initiates tool calls and processes responses
2. **MCP Client**: Handles MCP protocol formatting and communication
3. **STDIO Protocol**: JSON-RPC 2.0 over stdin/stdout for reliable message passing
4. **{server_name} Server**: This MCP server that routes calls to original functions
5. **Original Functions**: The actual Python functions from the source repository

## Message Flow

### Initialization
1. Client sends `initialize` request with capabilities
2. Server responds with server info and capabilities
3. Client sends `initialized` notification
4. Ready for tool calls

### Tool Discovery
1. Client sends `tools/list` request
2. Server returns list of available tools with schemas
3. Client can now make informed tool calls

### Tool Execution
1. Client sends `tools/call` with tool name and parameters
2. Server validates parameters against schema
3. Server calls original function with parameters
4. Server returns result or error in MCP format

## Error Handling

- **Parameter Validation**: Checked before function execution
- **Function Exceptions**: Caught and returned as MCP errors
- **Protocol Errors**: Invalid JSON-RPC messages handled gracefully
- **Timeout Protection**: Long-running functions are monitored

## Performance Characteristics

- **Startup Time**: ~100ms for server initialization
- **Tool Call Latency**: ~1-5ms overhead + original function execution time
- **Memory Usage**: Minimal overhead, primarily function execution memory
- **Concurrency**: Single-threaded request processing (MCP specification)

## Security Model

- **Sandboxing**: Runs in container environment if deployed via Docker
- **Input Validation**: All parameters validated before function calls
- **Output Sanitization**: Results formatted safely for MCP protocol
- **Function Security**: Original function security characteristics preserved

## Container Integration (if deployed via Maverick-MCP Gateway)

```
Claude Code ↔ Gateway ↔ Docker Container ↔ {server_name} Server
```

- **Container Lifecycle**: Spawned on-demand, idle timeout cleanup
- **Resource Management**: Automatic memory and CPU limits
- **Networking**: Isolated container networking
- **Persistence**: Stateless execution, no persistent storage

## Development vs Production

**Development**: Direct STDIO execution for testing and debugging
**Production**: Container-based deployment via Maverick-MCP Gateway

Both modes use identical MCP protocol for consistent behavior.
"""
    
    def _get_troubleshooting_guide(self, server_name: str) -> str:
        """Get troubleshooting guide"""
        return f"""# {server_name} Troubleshooting Guide

## Common Issues and Solutions

### 1. Tool Not Found
**Error**: "Unknown tool: tool_name"
**Solution**: 
- Use `tools/list` to see available tools
- Check spelling and case sensitivity
- Verify tool was included in server generation

### 2. Parameter Validation Errors
**Error**: "Invalid request parameters"
**Solution**:
- Check tool schema with `tools/list` 
- Ensure all required parameters are provided
- Verify parameter types match schema
- Use `tool_help` prompt for parameter details

### 3. Function Execution Errors
**Error**: Function-specific error messages
**Solution**:
- Read error message carefully for specific guidance
- Check parameter values are in valid ranges
- Ensure input data is properly formatted
- Review original function documentation

### 4. Server Initialization Issues
**Error**: Server fails to start or initialize
**Solution**:
- Check that all required dependencies are installed
- Verify Python environment compatibility
- Check for import errors in original functions
- Ensure MCP SDK is properly installed

### 5. Communication Timeouts
**Error**: No response or timeout errors
**Solution**:
- Check if function execution is hanging
- Verify STDIO communication isn't blocked
- Look for infinite loops or long-running operations
- Check system resource availability

## Debugging Steps

### 1. Verify Server Status
- Check if server responds to `initialize` request
- Confirm `tools/list` returns expected tools
- Test with simple tool call first

### 2. Test Parameter Handling
- Start with minimal required parameters
- Add optional parameters incrementally
- Test edge cases and boundary values
- Verify parameter type conversion

### 3. Check Function Execution
- Test original functions directly in Python
- Compare direct execution with MCP tool results
- Check for environment differences
- Verify all dependencies are available

### 4. Monitor Resource Usage
- Check memory usage during execution
- Monitor CPU utilization
- Watch for resource leaks
- Verify container limits (if deployed)

## Getting Help

### Built-in Resources
- `usage_guide` prompt: General usage information
- `tool_help` prompt: Specific tool documentation
- `architecture` prompt: Understanding server design

### External Resources
- MCP Protocol Documentation
- Original repository documentation
- Maverick-MCP Gateway logs (if deployed)

### Diagnostic Information

When reporting issues, include:
- MCP protocol messages (requests and responses)
- Error messages with full context
- Server initialization logs
- Tool execution parameters and results
- Environment information (Python version, dependencies)

## Performance Optimization

### For Slow Tool Execution
1. Profile original function performance
2. Check for inefficient algorithms
3. Consider parameter size limits
4. Monitor memory allocation patterns

### For High Memory Usage
1. Check for memory leaks in original functions
2. Limit input data size
3. Consider streaming for large outputs
4. Monitor object lifecycle

### For Container Issues (Production)
1. Check container resource limits
2. Monitor Docker log outputs
3. Verify network connectivity
4. Check file system permissions

Most issues are resolved by careful parameter validation and understanding the original function requirements.
"""
    
    def _generate_api_docs_resource(
        self, 
        candidates: List[MCPToolCandidate], 
        server_name: str
    ) -> str:
        """Generate API documentation resource"""
        
        return f"""@app.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    \"\"\"List available documentation resources\"\"\"
    return [
        types.Resource(
            uri="docs://{server_name}/api",
            name="API Documentation",
            description="Complete API reference for all tools",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="docs://{server_name}/architecture", 
            name="Architecture Overview",
            description="System architecture and communication flow",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="docs://{server_name}/examples",
            name="Usage Examples",
            description="Practical examples for all tools",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="docs://{server_name}/integration",
            name="Integration Guide", 
            description="How to integrate with Maverick-MCP Gateway",
            mimeType="text/markdown"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    \"\"\"Provide detailed documentation resources\"\"\"
    
    if uri == "docs://{server_name}/api":
        return self._generate_api_documentation(candidates, server_name)
    elif uri == "docs://{server_name}/architecture":
        return self._get_architecture_explanation(server_name)  
    elif uri == "docs://{server_name}/examples":
        return self._generate_examples_documentation(candidates, server_name)
    elif uri == "docs://{server_name}/integration":
        return self._generate_integration_documentation(server_name, repo_info)
    else:
        raise ValueError(f"Unknown resource: {{uri}}")"""

    def _generate_api_documentation(self, candidates: List[MCPToolCandidate], server_name: str) -> str:
        """Generate complete API documentation"""
        return f"""# {server_name} API Documentation

## Overview

This MCP server provides {len(candidates)} tools derived from repository functions.

## Tools Reference

{self._generate_detailed_tool_list(candidates)}

## Response Formats

All tools return responses in MCP TextContent format:

```typescript
interface ToolResponse {{
  content: [{{
    type: "text",
    text: string  // Function result or error message
  }}]
}}
```

## Error Codes

- **Parameter Validation**: Invalid or missing parameters
- **Function Exception**: Error during function execution  
- **Unknown Tool**: Tool name not recognized
- **Server Error**: Internal server error

## Rate Limiting

No built-in rate limiting. Performance depends on original function execution time.

## Authentication

No authentication required. Security managed at container/gateway level.
"""

    def _generate_examples_documentation(self, candidates: List[MCPToolCandidate], server_name: str) -> str:
        """Generate examples documentation"""
        examples = []
        for candidate in candidates:
            examples.append(f"## {candidate.suggested_tool_name}\n\n{self._generate_tool_examples(candidate)}")
        
        return f"""# {server_name} Usage Examples

{chr(10).join(examples)}

## Testing Your Integration

Use these examples to test your MCP client integration:

1. Start with simple tools that have no required parameters
2. Progress to tools with required parameters
3. Test error handling with invalid parameters
4. Verify complex return value handling

## Integration Patterns

### Basic Tool Call Pattern
```python
# MCP client code example
result = await client.call_tool("tool_name", {{"param": "value"}})
print(result.content[0].text)
```

### Error Handling Pattern
```python
try:
    result = await client.call_tool("tool_name", arguments)
    return result.content[0].text
except Exception as e:
    print(f"Tool call failed: {{e}}")
```

### Parameter Validation Pattern
```python
# Get tool schema first
tools = await client.list_tools()
tool_schema = next(t for t in tools if t.name == "tool_name")
# Validate parameters against schema before calling
```
"""
    
    def _generate_architecture_resource(self, server_name: str) -> str:
        """Generate architecture resource handler"""
        return f"""
def _generate_architecture_documentation(self) -> str:
    \"\"\"Architecture documentation resource\"\"\"
    return self._get_architecture_explanation("{server_name}")
"""
    
    def _generate_examples_resource(
        self, 
        candidates: List[MCPToolCandidate], 
        server_name: str
    ) -> str:
        """Generate examples resource handler"""
        return f"""
def _generate_examples_resource_content(self) -> str:
    \"\"\"Examples resource content\"\"\"
    return self._generate_examples_documentation()
"""
    
    def _generate_integration_resource(
        self, 
        server_name: str, 
        repo_info: Dict[str, Any]
    ) -> str:
        """Generate integration resource handler"""
        return f"""
def _generate_integration_resource_content(self) -> str:
    \"\"\"Integration resource content\"\"\"
    return self._generate_integration_documentation()
"""

    def _generate_integration_documentation(self, server_name: str, repo_info: Dict[str, Any]) -> str:
        """Generate integration documentation"""
        return f"""# {server_name} Integration Guide

## Maverick-MCP Gateway Integration

### 1. Add to servers.yaml

Add this entry to your gateway's servers.yaml:

```yaml
{server_name}:
  image: "{server_name}"
  command: ["python", "mcp_server.py"]
  description: "Generated MCP server from {repo_info.get('name', 'repository')}"
  environment:
    PYTHONUNBUFFERED: "1"
  idle_timeout: 300
  tools:
    # Tool definitions will be auto-discovered
```

### 2. Build Docker Image

```bash
# Build the Docker image
docker build -t {server_name} .

# Test the image
docker run -i --rm {server_name}
```

### 3. Test Integration

```bash
# Test with gateway
echo '{{"jsonrpc":"2.0","method":"initialize","params":{{"protocolVersion":"2024-11-05","clientInfo":{{"name":"test","version":"1.0.0"}},"capabilities":{{}}}},"id":1}}' | docker run -i --rm {server_name}
```

### 4. Deploy to Production

1. Add server configuration to gateway
2. Restart gateway service
3. Verify tool discovery with `list_available_tools`
4. Test tool execution via gateway

## Direct Integration

### STDIO Interface

```python
import subprocess
import json

# Start server process
process = subprocess.Popen(
    ["python", "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Initialize
init_msg = {{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {{
        "protocolVersion": "2024-11-05",
        "clientInfo": {{"name": "test", "version": "1.0.0"}},
        "capabilities": {{}}
    }},
    "id": 1
}}

process.stdin.write(json.dumps(init_msg) + "\\n")
process.stdin.flush()

response = process.stdout.readline()
print(json.loads(response))
```

## Environment Requirements

- Python 3.11+
- MCP SDK dependencies
- Original repository dependencies
- Container runtime (for Docker deployment)

## Monitoring and Logging

- Server logs to stderr
- Tool execution logs include timing and parameters
- Error conditions logged with context
- Health check endpoint available (if enabled)

## Security Considerations

- Container isolation recommended for production
- Input validation performed on all parameters
- Original function security characteristics preserved
- No network access unless explicitly required by functions

## Performance Tuning

- Container resource limits
- Function execution timeouts
- Memory usage monitoring
- Concurrent request handling (single-threaded per MCP spec)
"""