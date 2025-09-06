# FastMCP Quickstart

FastMCP is a Python framework that simplifies building MCP servers with decorators and async support.

## Installation

```bash
pip install fastmcp>=2.0.0
```

## Basic Server

```python
from fastmcp import FastMCP

# Create server instance
mcp = FastMCP("my-server", version="1.0.0")

# Define a tool
@mcp.tool()
async def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"

# Define a resource
@mcp.resource("config://app/{key}")
async def get_config(key: str) -> Dict:
    """Get configuration value"""
    return {
        "uri": f"config://app/{key}",
        "mimeType": "application/json",
        "text": json.dumps({"key": key, "value": "example"})
    }

# Run the server
if __name__ == "__main__":
    mcp.run()
```

## Key Features

- **Decorator-based**: Simple tool and resource definition
- **Type hints**: Full typing support
- **Async support**: Built-in async handling
- **Error handling**: Automatic error wrapping
- **STDIO transport**: Standard MCP communication