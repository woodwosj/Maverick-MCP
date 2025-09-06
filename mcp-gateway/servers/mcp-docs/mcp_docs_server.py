#!/usr/bin/env python3
"""
MCP Documentation Server

Provides FastMCP and MCP Protocol documentation as MCP resources,
along with repository analyzer documentation and guides.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPDocumentationServer:
    """MCP server providing documentation as resources and tools"""
    
    def __init__(self):
        self.mcp = FastMCP("mcp-docs-server", version="1.0.0")
        self.docs_path = Path(__file__).parent / "documentation"
        self.setup_resources()
        self.setup_tools()
    
    def setup_resources(self):
        """Register documentation resources"""
        
        @self.mcp.resource("docs://mcp/concepts/{topic}")
        async def get_mcp_concept(topic: str) -> Dict[str, Any]:
            """Get MCP protocol concept documentation"""
            try:
                doc_file = self.docs_path / "mcp" / "concepts" / f"{topic}.md"
                if doc_file.exists():
                    content = doc_file.read_text()
                    return {
                        "uri": f"docs://mcp/concepts/{topic}",
                        "name": f"MCP Concept: {topic.title()}",
                        "description": f"Documentation for MCP {topic} concept",
                        "mimeType": "text/markdown",
                        "text": content
                    }
                else:
                    # Provide basic concept definitions if file doesn't exist
                    concepts = {
                        "tools": self._get_tools_concept(),
                        "resources": self._get_resources_concept(),
                        "prompts": self._get_prompts_concept(),
                        "protocol": self._get_protocol_concept(),
                    }
                    
                    if topic in concepts:
                        return {
                            "uri": f"docs://mcp/concepts/{topic}",
                            "name": f"MCP Concept: {topic.title()}",
                            "description": f"Documentation for MCP {topic} concept",
                            "mimeType": "text/markdown",
                            "text": concepts[topic]
                        }
                    
                    return {"error": f"Unknown MCP concept: {topic}"}
            except Exception as e:
                logger.error(f"Error retrieving MCP concept {topic}: {e}")
                return {"error": f"Error retrieving concept: {str(e)}"}
        
        @self.mcp.resource("docs://mcp/guides/{guide}")
        async def get_mcp_guide(guide: str) -> Dict[str, Any]:
            """Get MCP protocol guide documentation"""
            try:
                doc_file = self.docs_path / "mcp" / "guides" / f"{guide}.md"
                if doc_file.exists():
                    content = doc_file.read_text()
                    return {
                        "uri": f"docs://mcp/guides/{guide}",
                        "name": f"MCP Guide: {guide.replace('-', ' ').title()}",
                        "description": f"Guide for {guide.replace('-', ' ')}",
                        "mimeType": "text/markdown",
                        "text": content
                    }
                else:
                    # Provide basic guides if file doesn't exist
                    guides = {
                        "getting-started": self._get_getting_started_guide(),
                        "building-servers": self._get_building_servers_guide(),
                        "best-practices": self._get_best_practices_guide(),
                    }
                    
                    if guide in guides:
                        return {
                            "uri": f"docs://mcp/guides/{guide}",
                            "name": f"MCP Guide: {guide.replace('-', ' ').title()}",
                            "description": f"Guide for {guide.replace('-', ' ')}",
                            "mimeType": "text/markdown",
                            "text": guides[guide]
                        }
                    
                    return {"error": f"Unknown MCP guide: {guide}"}
            except Exception as e:
                logger.error(f"Error retrieving MCP guide {guide}: {e}")
                return {"error": f"Error retrieving guide: {str(e)}"}
        
        @self.mcp.resource("docs://fastmcp/{section}")
        async def get_fastmcp_docs(section: str) -> Dict[str, Any]:
            """Get FastMCP framework documentation"""
            try:
                doc_file = self.docs_path / "fastmcp" / f"{section}.md"
                if doc_file.exists():
                    content = doc_file.read_text()
                    return {
                        "uri": f"docs://fastmcp/{section}",
                        "name": f"FastMCP: {section.title()}",
                        "description": f"FastMCP documentation for {section}",
                        "mimeType": "text/markdown",
                        "text": content
                    }
                else:
                    # Provide basic FastMCP documentation if file doesn't exist
                    sections = {
                        "quickstart": self._get_fastmcp_quickstart(),
                        "decorators": self._get_fastmcp_decorators(),
                        "resources": self._get_fastmcp_resources(),
                        "tools": self._get_fastmcp_tools(),
                        "deployment": self._get_fastmcp_deployment(),
                    }
                    
                    if section in sections:
                        return {
                            "uri": f"docs://fastmcp/{section}",
                            "name": f"FastMCP: {section.title()}",
                            "description": f"FastMCP documentation for {section}",
                            "mimeType": "text/markdown",
                            "text": sections[section]
                        }
                    
                    return {"error": f"Unknown FastMCP section: {section}"}
            except Exception as e:
                logger.error(f"Error retrieving FastMCP section {section}: {e}")
                return {"error": f"Error retrieving section: {str(e)}"}
        
        @self.mcp.resource("docs://analyzer/{topic}")
        async def get_analyzer_docs(topic: str) -> Dict[str, Any]:
            """Get repository analyzer documentation"""
            try:
                doc_file = self.docs_path / "analyzer" / f"{topic}.md"
                if doc_file.exists():
                    content = doc_file.read_text()
                    return {
                        "uri": f"docs://analyzer/{topic}",
                        "name": f"Analyzer: {topic.replace('-', ' ').title()}",
                        "description": f"Repository analyzer documentation for {topic.replace('-', ' ')}",
                        "mimeType": "text/markdown",
                        "text": content
                    }
                else:
                    # Provide basic analyzer documentation if file doesn't exist
                    topics = {
                        "overview": self._get_analyzer_overview(),
                        "scoring": self._get_analyzer_scoring(),
                        "security": self._get_analyzer_security(),
                        "conversion": self._get_analyzer_conversion(),
                    }
                    
                    if topic in topics:
                        return {
                            "uri": f"docs://analyzer/{topic}",
                            "name": f"Analyzer: {topic.replace('-', ' ').title()}",
                            "description": f"Repository analyzer documentation for {topic.replace('-', ' ')}",
                            "mimeType": "text/markdown",
                            "text": topics[topic]
                        }
                    
                    return {"error": f"Unknown analyzer topic: {topic}"}
            except Exception as e:
                logger.error(f"Error retrieving analyzer topic {topic}: {e}")
                return {"error": f"Error retrieving topic: {str(e)}"}
    
    def setup_tools(self):
        """Register documentation tools"""
        
        @self.mcp.tool()
        async def search_documentation(query: str, category: Optional[str] = None) -> List[Dict[str, str]]:
            """Search across all documentation"""
            results = []
            search_query = query.lower()
            
            # Search in MCP concepts
            if not category or category == "mcp":
                concepts = ["tools", "resources", "prompts", "protocol"]
                for concept in concepts:
                    if search_query in concept or search_query in self._get_concept_content(concept).lower():
                        results.append({
                            "uri": f"docs://mcp/concepts/{concept}",
                            "title": f"MCP Concept: {concept.title()}",
                            "category": "mcp/concepts",
                            "relevance": "high" if search_query in concept else "medium"
                        })
            
            # Search in FastMCP sections
            if not category or category == "fastmcp":
                sections = ["quickstart", "decorators", "resources", "tools", "deployment"]
                for section in sections:
                    if search_query in section or search_query in self._get_fastmcp_content(section).lower():
                        results.append({
                            "uri": f"docs://fastmcp/{section}",
                            "title": f"FastMCP: {section.title()}",
                            "category": "fastmcp",
                            "relevance": "high" if search_query in section else "medium"
                        })
            
            # Search in analyzer topics
            if not category or category == "analyzer":
                topics = ["overview", "scoring", "security", "conversion"]
                for topic in topics:
                    if search_query in topic or search_query in self._get_analyzer_content(topic).lower():
                        results.append({
                            "uri": f"docs://analyzer/{topic}",
                            "title": f"Analyzer: {topic.replace('-', ' ').title()}",
                            "category": "analyzer",
                            "relevance": "high" if search_query in topic else "medium"
                        })
            
            # Sort by relevance
            results.sort(key=lambda x: x["relevance"], reverse=True)
            return results[:10]  # Return top 10 results
        
        @self.mcp.tool()
        async def list_documentation_topics() -> Dict[str, List[str]]:
            """List all available documentation topics"""
            return {
                "mcp": {
                    "concepts": ["tools", "resources", "prompts", "protocol"],
                    "guides": ["getting-started", "building-servers", "best-practices"]
                },
                "fastmcp": ["quickstart", "decorators", "resources", "tools", "deployment"],
                "analyzer": ["overview", "scoring", "security", "conversion"]
            }
        
        @self.mcp.tool()
        async def get_documentation_index() -> List[Dict[str, str]]:
            """Get a complete index of all documentation"""
            index = []
            
            # MCP documentation
            for concept in ["tools", "resources", "prompts", "protocol"]:
                index.append({
                    "uri": f"docs://mcp/concepts/{concept}",
                    "title": f"MCP Concept: {concept.title()}",
                    "category": "mcp/concepts",
                    "description": f"Learn about MCP {concept}"
                })
            
            for guide in ["getting-started", "building-servers", "best-practices"]:
                index.append({
                    "uri": f"docs://mcp/guides/{guide}",
                    "title": f"MCP Guide: {guide.replace('-', ' ').title()}",
                    "category": "mcp/guides",
                    "description": f"Guide for {guide.replace('-', ' ')}"
                })
            
            # FastMCP documentation
            for section in ["quickstart", "decorators", "resources", "tools", "deployment"]:
                index.append({
                    "uri": f"docs://fastmcp/{section}",
                    "title": f"FastMCP: {section.title()}",
                    "category": "fastmcp",
                    "description": f"FastMCP framework documentation for {section}"
                })
            
            # Analyzer documentation
            for topic in ["overview", "scoring", "security", "conversion"]:
                index.append({
                    "uri": f"docs://analyzer/{topic}",
                    "title": f"Analyzer: {topic.replace('-', ' ').title()}",
                    "category": "analyzer",
                    "description": f"Repository analyzer documentation for {topic.replace('-', ' ')}"
                })
            
            return index
    
    # Content generation methods
    def _get_tools_concept(self) -> str:
        return """# MCP Tools

Tools are executable functions that MCP servers expose to AI models. They allow models to perform actions and retrieve dynamic information.

## Key Characteristics

- **Executable**: Tools perform actions when called
- **Parameterized**: Accept input parameters with validation
- **Async**: Support asynchronous execution
- **Documented**: Include descriptions and parameter schemas

## Tool Definition Example

```python
@mcp.tool()
async def analyze_repository(repo_path: str, min_score: float = 5.0) -> Dict:
    \"\"\"Analyze a repository for MCP tool candidates\"\"\"
    # Implementation here
    return {"candidates": [], "total": 0}
```

## Best Practices

- Use clear, descriptive names
- Validate input parameters
- Handle errors gracefully
- Provide detailed docstrings
"""
    
    def _get_resources_concept(self) -> str:
        return """# MCP Resources

Resources are static or semi-static content that can be retrieved by AI models. Unlike tools, resources represent data rather than actions.

## Key Characteristics

- **URI-based**: Accessed via unique resource identifiers
- **Content-focused**: Return data, documents, or information
- **Cacheable**: Can be cached for performance
- **MIME-typed**: Support different content types

## Resource Definition Example

```python
@mcp.resource("docs://mcp/concepts/{topic}")
async def get_mcp_concept(topic: str) -> Dict:
    \"\"\"Get MCP protocol concept documentation\"\"\"
    return {
        "uri": f"docs://mcp/concepts/{topic}",
        "mimeType": "text/markdown",
        "text": concept_content
    }
```

## Use Cases

- Documentation and help content
- Configuration data
- Static reference information
- File contents
"""
    
    def _get_prompts_concept(self) -> str:
        return """# MCP Prompts

Prompts are pre-defined interaction templates that help AI models understand how to use MCP servers effectively.

## Key Characteristics

- **Template-based**: Define interaction patterns
- **Context-aware**: Provide relevant context
- **Reusable**: Can be used across sessions
- **Discoverable**: Listed by MCP servers

## Prompt Definition Example

```python
@mcp.prompt("analyze_repository_for_mcp")
async def analyze_repository_prompt() -> Dict:
    return {
        "name": "analyze_repository_for_mcp",
        "description": "Analyze a repository for MCP conversion potential",
        "arguments": [
            {"name": "repo_path", "description": "Path to repository"}
        ]
    }
```

## Benefits

- Consistent interaction patterns
- Reduced cognitive load for users
- Better tool discovery
- Standardized workflows
"""
    
    def _get_protocol_concept(self) -> str:
        return """# MCP Protocol

The Model Context Protocol (MCP) is a standardized protocol for AI model context management using JSON-RPC 2.0 over STDIO.

## Architecture

- **JSON-RPC 2.0**: Standard remote procedure call protocol
- **STDIO Transport**: Communication over stdin/stdout
- **Bidirectional**: Both client and server can initiate requests
- **Extensible**: Supports custom capabilities

## Message Flow

1. **Initialization**: Client and server exchange capabilities
2. **Discovery**: Client requests available tools, resources, prompts
3. **Execution**: Client invokes tools or retrieves resources
4. **Cleanup**: Proper session termination

## Core Methods

- `tools/list`: List available tools
- `tools/call`: Execute a tool
- `resources/list`: List available resources
- `resources/read`: Retrieve resource content
- `prompts/list`: List available prompts
- `prompts/get`: Get prompt template

## Implementation

MCP servers typically run as separate processes, communicating via STDIO. This allows for isolation and language independence.
"""
    
    def _get_getting_started_guide(self) -> str:
        return """# Getting Started with MCP

This guide helps you get started with the Model Context Protocol and building your first MCP server.

## Prerequisites

- Python 3.8+ or Node.js 16+
- Basic understanding of JSON-RPC
- Familiarity with async programming

## Quick Start

### 1. Install FastMCP (Python)

```bash
pip install fastmcp
```

### 2. Create Your First Server

```python
from fastmcp import FastMCP

mcp = FastMCP("my-first-server")

@mcp.tool()
async def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

### 3. Test Your Server

```bash
python my_server.py
```

## Next Steps

- Learn about [tools, resources, and prompts](docs://mcp/concepts/tools)
- Explore [FastMCP decorators](docs://fastmcp/decorators)
- Read [building servers guide](docs://mcp/guides/building-servers)
"""
    
    def _get_building_servers_guide(self) -> str:
        return """# Building MCP Servers

Learn how to build robust MCP servers with proper error handling, validation, and best practices.

## Server Architecture

A well-structured MCP server should:
- Separate concerns (tools, resources, prompts)
- Handle errors gracefully
- Validate inputs
- Provide comprehensive documentation

## Error Handling

```python
@mcp.tool()
async def safe_operation(data: str) -> Dict:
    try:
        # Validate input
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Process data
        result = process_data(data)
        return {"success": True, "result": result}
    except ValueError as e:
        return {"success": False, "error": str(e)}
```

## Input Validation

Use type hints and validation:

```python
from typing import Optional
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    repo_path: str
    min_score: float = 5.0
    include_tests: bool = True

@mcp.tool()
async def analyze_repository(request: AnalysisRequest) -> Dict:
    # Type-safe processing
    pass
```

## Testing

Create comprehensive tests for your MCP server:

```python
import pytest
from your_server import YourMCPServer

@pytest.fixture
async def server():
    return YourMCPServer()

async def test_tool_execution(server):
    result = await server.execute_tool("hello", {"name": "World"})
    assert result["success"] is True
```
"""
    
    def _get_best_practices_guide(self) -> str:
        return """# MCP Best Practices

Guidelines for building production-ready MCP servers.

## Performance

### Async Operations
- Use async/await for I/O operations
- Avoid blocking operations in tool handlers
- Implement proper connection pooling

### Caching
- Cache expensive computations
- Use TTL for time-sensitive data
- Implement cache invalidation strategies

## Security

### Input Validation
- Validate all user inputs
- Sanitize file paths and URLs
- Implement rate limiting

### Resource Protection
- Limit resource access scope
- Implement proper authentication
- Use sandboxing for code execution

## Documentation

### Tool Documentation
- Provide clear descriptions
- Document all parameters
- Include usage examples

### Error Messages
- Use descriptive error messages
- Provide actionable guidance
- Include error codes for categorization

## Deployment

### Containerization
- Use Docker for isolation
- Implement health checks
- Configure resource limits

### Monitoring
- Log important events
- Monitor performance metrics
- Implement alerting

## Scalability

- Design for horizontal scaling
- Use connection pooling
- Implement proper cleanup
"""
    
    def _get_fastmcp_quickstart(self) -> str:
        return """# FastMCP Quickstart

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
    \"\"\"Greet someone by name\"\"\"
    return f"Hello, {name}!"

# Define a resource
@mcp.resource("config://app/{key}")
async def get_config(key: str) -> Dict:
    \"\"\"Get configuration value\"\"\"
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
"""
    
    def _get_fastmcp_decorators(self) -> str:
        return """# FastMCP Decorators

FastMCP provides decorators to easily define tools, resources, and prompts.

## @mcp.tool()

Define executable tools:

```python
@mcp.tool()
async def analyze_code(file_path: str, language: str = "python") -> Dict:
    \"\"\"Analyze code file for complexity\"\"\"
    # Implementation
    return {"complexity": 5, "lines": 100}

# With custom name and description
@mcp.tool(name="custom_name", description="Custom description")
async def my_tool() -> str:
    return "result"
```

## @mcp.resource()

Define retrievable resources:

```python
@mcp.resource("docs://{category}/{topic}")
async def get_documentation(category: str, topic: str) -> Dict:
    \"\"\"Get documentation content\"\"\"
    return {
        "uri": f"docs://{category}/{topic}",
        "mimeType": "text/markdown",
        "text": "# Documentation content"
    }
```

## @mcp.prompt()

Define prompt templates:

```python
@mcp.prompt("code_review")
async def code_review_prompt() -> Dict:
    \"\"\"Generate code review prompt\"\"\"
    return {
        "name": "code_review",
        "description": "Review code for quality",
        "arguments": [
            {"name": "code", "description": "Code to review"}
        ]
    }
```

## Parameter Types

FastMCP supports rich type annotations:

```python
from typing import Optional, List, Dict
from enum import Enum

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"

@mcp.tool()
async def create_task(
    title: str,
    description: Optional[str] = None,
    priority: Priority = Priority.MEDIUM,
    tags: List[str] = [],
    metadata: Dict[str, Any] = {}
) -> Dict:
    \"\"\"Create a new task with rich parameters\"\"\"
    return {"id": "task-123", "title": title}
```
"""
    
    def _get_fastmcp_resources(self) -> str:
        return """# FastMCP Resources

Resources in FastMCP provide access to static or semi-static content through URI patterns.

## Resource Definition

```python
@mcp.resource("docs://{category}/{topic}")
async def get_docs(category: str, topic: str) -> Dict:
    \"\"\"Get documentation by category and topic\"\"\"
    content = load_documentation(category, topic)
    
    return {
        "uri": f"docs://{category}/{topic}",
        "name": f"{category.title()}: {topic.title()}",
        "description": f"Documentation for {topic} in {category}",
        "mimeType": "text/markdown",
        "text": content
    }
```

## URI Patterns

Resources use URI patterns with parameters:

- `{param}` - Required parameter
- `{param?}` - Optional parameter
- `**` - Wildcard matching

Examples:
- `docs://{section}/{page}` - Matches `docs://api/authentication`
- `files://{path**}` - Matches `files://src/main/app.py`
- `config://{key?}` - Matches `config://` or `config://database`

## Return Format

Resources should return a dictionary with:

```python
{
    "uri": "resource URI",
    "name": "Human-readable name",
    "description": "Resource description",
    "mimeType": "content type",
    "text": "text content"  # or "blob": bytes for binary
}
```

## Common MIME Types

- `text/plain` - Plain text
- `text/markdown` - Markdown content
- `application/json` - JSON data
- `application/xml` - XML content
- `text/html` - HTML content

## Caching

Resources can be cached for performance:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def load_documentation(category: str, topic: str) -> str:
    # Expensive loading operation
    return content

@mcp.resource("docs://{category}/{topic}")
async def get_docs(category: str, topic: str) -> Dict:
    content = load_documentation(category, topic)
    # Return resource dict
```
"""
    
    def _get_fastmcp_tools(self) -> str:
        return """# FastMCP Tools

Tools in FastMCP are executable functions that perform actions and return results.

## Tool Definition

```python
@mcp.tool()
async def search_files(
    pattern: str,
    directory: str = ".",
    recursive: bool = True,
    max_results: int = 100
) -> List[Dict]:
    \"\"\"Search for files matching a pattern\"\"\"
    results = []
    # Search implementation
    for file_path in search_filesystem(pattern, directory, recursive):
        if len(results) >= max_results:
            break
        results.append({
            "path": str(file_path),
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime
        })
    return results
```

## Error Handling

Handle errors gracefully in tools:

```python
@mcp.tool()
async def read_file(file_path: str) -> Dict:
    \"\"\"Read file contents safely\"\"\"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "success": True,
            "content": content,
            "encoding": "utf-8"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading file: {str(e)}"
        }
```

## Async Operations

Use async for I/O operations:

```python
import aiohttp
import aiofiles

@mcp.tool()
async def fetch_url_content(url: str) -> Dict:
    \"\"\"Fetch content from a URL\"\"\"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.text()
                return {
                    "success": True,
                    "content": content,
                    "status": response.status,
                    "content_type": response.content_type
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def write_file_async(file_path: str, content: str) -> Dict:
    \"\"\"Write content to file asynchronously\"\"\"
    try:
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(content)
        return {"success": True, "path": file_path}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Validation

Validate inputs and provide helpful errors:

```python
from pathlib import Path

@mcp.tool()
async def analyze_directory(directory_path: str) -> Dict:
    \"\"\"Analyze directory structure\"\"\"
    # Validate path
    path = Path(directory_path)
    if not path.exists():
        return {"error": f"Directory does not exist: {directory_path}"}
    
    if not path.is_dir():
        return {"error": f"Path is not a directory: {directory_path}"}
    
    # Analyze directory
    files = list(path.glob("**/*"))
    return {
        "total_files": len([f for f in files if f.is_file()]),
        "total_dirs": len([f for f in files if f.is_dir()]),
        "total_size": sum(f.stat().st_size for f in files if f.is_file())
    }
```
"""
    
    def _get_fastmcp_deployment(self) -> str:
        return """# FastMCP Deployment

Deploy FastMCP servers in production environments with Docker and proper configuration.

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy server code
COPY . .

# Run server
CMD ["python", "server.py"]
```

### requirements.txt

```
fastmcp>=2.0.0
aiofiles>=0.8.0
aiohttp>=3.8.0
pydantic>=1.10.0
```

### Build and Run

```bash
# Build image
docker build -t my-mcp-server .

# Run container
docker run -i --rm my-mcp-server
```

## Gateway Integration

Add your server to the MCP gateway:

### servers.yaml

```yaml
my-server:
  image: "my-mcp-server"
  command: ["python", "server.py"]
  description: "My custom MCP server"
  environment:
    LOG_LEVEL: "INFO"
  idle_timeout: 300
  tools:
    - name: "my_tool"
      description: "Description of my tool"
  resources:
    - pattern: "my://**"
      description: "My resource pattern"
```

## Environment Configuration

Use environment variables for configuration:

```python
import os
from fastmcp import FastMCP

mcp = FastMCP(
    name=os.getenv("SERVER_NAME", "default-server"),
    version=os.getenv("SERVER_VERSION", "1.0.0")
)

# Configure based on environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
```

## Health Checks

Implement health check endpoints:

```python
@mcp.tool()
async def health_check() -> Dict:
    \"\"\"Check server health status\"\"\"
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": time.time() - start_time
    }
```

## Monitoring

Add logging and metrics:

```python
import logging
import time

logger = logging.getLogger(__name__)

@mcp.tool()
async def timed_operation(data: str) -> Dict:
    \"\"\"Operation with timing and logging\"\"\"
    start = time.time()
    try:
        logger.info(f"Starting operation with {len(data)} bytes")
        result = await process_data(data)
        duration = time.time() - start
        logger.info(f"Operation completed in {duration:.3f}s")
        return {"success": True, "result": result, "duration": duration}
    except Exception as e:
        duration = time.time() - start
        logger.error(f"Operation failed after {duration:.3f}s: {e}")
        return {"success": False, "error": str(e)}
```

## Security Considerations

- Run containers with non-root users
- Implement input validation
- Limit resource access
- Use secrets management for sensitive data
- Enable audit logging
"""
    
    def _get_analyzer_overview(self) -> str:
        return """# Repository Analyzer Overview

The Repository Analyzer scans codebases to identify functions suitable for MCP tool conversion.

## Purpose

The analyzer helps convert existing code repositories into MCP servers by:
- Analyzing function signatures and documentation
- Scoring functions for MCP suitability (0-10 scale)
- Identifying security risks and patterns
- Generating conversion recommendations

## Supported Languages

- **Python**: Full AST analysis with docstring parsing
- **JavaScript**: Function detection and parameter analysis
- **Go**: Basic function identification (planned)
- **Rust**: Future support planned

## Analysis Process

1. **Discovery**: Scan repository for code files
2. **Parsing**: Extract function definitions and metadata
3. **Scoring**: Rate each function for MCP conversion potential
4. **Security**: Identify potentially dangerous patterns
5. **Reporting**: Generate detailed analysis results

## Usage

### Command Line

```bash
# Analyze current directory
python analyze_repo.py .

# Analyze specific repository
python analyze_repo.py /path/to/repo

# Filter by score threshold
python analyze_repo.py /path/to/repo --min-score 7.0

# Show security warnings
python analyze_repo.py /path/to/repo --show-security
```

### Programmatic

```python
from analyzer.repository_analyzer import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
result = analyzer.analyze_repository("/path/to/repo")

print(f"Found {len(result.candidates)} candidates")
for candidate in result.candidates:
    if candidate.mcp_score >= 7.0:
        print(f"- {candidate.function.function_name}: {candidate.mcp_score}")
```

## Output Formats

- **Table**: Human-readable console output
- **JSON**: Machine-readable structured data
- **Summary**: High-level statistics only

## Integration

The analyzer integrates with:
- **Dockerfile Generator**: Automatic server generation
- **Approval Flow**: Interactive conversion approval
- **Gateway**: Server registration and management
"""
    
    def _get_analyzer_scoring(self) -> str:
        return """# Repository Analyzer Scoring Algorithm

The scoring algorithm rates functions on their suitability for MCP tool conversion using a 0-10 scale.

## Scoring Factors

### Documentation Quality (0-3 points)
- **3 points**: Comprehensive docstring with parameter descriptions
- **2 points**: Basic docstring with function description
- **1 point**: Minimal docstring or comments
- **0 points**: No documentation

### Parameter Complexity (0-2 points)
- **2 points**: Simple, well-typed parameters
- **1 point**: Moderate complexity
- **0 points**: Complex or poorly defined parameters

### Function Purpose (0-3 points)
- **3 points**: Clear utility/tool-like function
- **2 points**: Processing or analysis function
- **1 point**: Helper or internal function
- **0 points**: Constructor or boilerplate

### Return Value (0-2 points)
- **2 points**: Structured, informative return
- **1 point**: Simple return value
- **0 points**: No return or void

## Bonus Factors

### Async Support (+0.5 points)
Functions that are already async or easily convertible

### Type Hints (+0.5 points)
Well-typed function signatures

### Error Handling (+0.5 points)
Proper exception handling and validation

## Penalty Factors

### Security Risks (-1 to -3 points)
- File system manipulation
- Network operations
- System command execution
- Dangerous module imports

### Complexity (-0.5 to -1 points)
- Excessive parameter count
- Complex nested structures
- Hard-to-understand logic

## Example Scoring

### High Score Function (8.5/10)

```python
async def analyze_repository(repo_path: str, min_score: float = 5.0) -> Dict[str, Any]:
    \"\"\"
    Analyze a Git repository for code quality metrics.
    
    Args:
        repo_path: Path to the repository directory
        min_score: Minimum quality score threshold (0-10)
        
    Returns:
        Dictionary containing analysis results with metrics,
        file counts, and quality scores.
        
    Raises:
        ValueError: If repo_path doesn't exist
        PermissionError: If repo_path isn't readable
    \"\"\"
    # Implementation
    return {"metrics": {}, "score": 8.5}
```

**Score Breakdown:**
- Documentation: 3/3 (comprehensive docstring)
- Parameters: 2/2 (well-typed, reasonable)
- Purpose: 3/3 (clear analysis tool)
- Return: 2/2 (structured dict)
- Async: +0.5 (async function)
- **Total: 10.5/10 → 10/10 (capped)**

### Low Score Function (2.0/10)

```python
def _internal_helper(data):
    # TODO: implement this
    pass
```

**Score Breakdown:**
- Documentation: 0/3 (no docstring)
- Parameters: 0/2 (untyped)
- Purpose: 0/3 (internal helper)
- Return: 0/2 (no return)
- **Total: 2.0/10**

## Threshold Guidelines

- **9-10**: Excellent MCP tool candidates
- **7-8**: Good candidates, minor improvements needed
- **5-6**: Acceptable with modifications
- **3-4**: Significant work required
- **0-2**: Not suitable for MCP conversion

## Customization

The scoring algorithm can be customized:

```python
from analyzer.repository_analyzer import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
analyzer.scoring_weights = {
    "documentation": 0.4,  # 40% weight
    "parameters": 0.2,     # 20% weight
    "purpose": 0.3,        # 30% weight
    "return_value": 0.1    # 10% weight
}

result = analyzer.analyze_repository("/path/to/repo")
```
"""
    
    def _get_analyzer_security(self) -> str:
        return """# Repository Analyzer Security Scanning

The security scanner identifies potentially dangerous patterns in code that could pose risks when converted to MCP tools.

## Risk Categories

### High Risk Patterns

#### System Commands
- `os.system()`, `subprocess.*`
- `shell=True` parameter usage
- `exec()`, `eval()` function calls

```python
# HIGH RISK
os.system("rm -rf " + user_input)  # Command injection risk
subprocess.run(user_command, shell=True)  # Shell injection
```

#### File System Access
- Absolute path operations (`/etc/`, `/home/`)
- Directory traversal patterns (`../`)
- Destructive operations (`os.remove`, `shutil.rmtree`)

```python
# HIGH RISK  
open("/etc/passwd", "r")  # System file access
open("../" + filename)    # Directory traversal
os.remove(user_path)      # Destructive operation
```

#### Network Operations
- HTTP requests without validation
- Socket operations
- External service calls

```python
# HIGH RISK
requests.get(user_url)           # Unvalidated HTTP requests
socket.connect((host, port))     # Raw socket access
```

### Medium Risk Patterns

#### Database Operations
- Raw SQL execution
- Destructive database commands
- Unparameterized queries

```python
# MEDIUM RISK
cursor.execute("DROP TABLE " + table_name)  # SQL injection risk
db.execute(f"DELETE FROM {table}")          # Dynamic SQL
```

#### Code Generation
- Dynamic code compilation
- String formatting in code contexts

```python
# MEDIUM RISK
compile(user_code, "<string>", "exec")  # Code injection
eval(f"function_{user_input}()")        # Dynamic execution
```

## Risk Scoring

### Calculation Method
- **High Risk**: 3.0 points per pattern
- **Medium Risk**: 1.5 points per pattern
- **Maximum**: 10.0 points (very dangerous)

### Risk Thresholds
- **0.0-2.0**: Safe for MCP conversion
- **2.0-5.0**: Caution required, review needed
- **5.0+**: High risk, not recommended

## Security Report Example

```python
from analyzer.security.pattern_scanner import SecurityScanner
from analyzer.models import FunctionCandidate

scanner = SecurityScanner()
warnings = scanner.scan_function(function_candidate)

for warning in warnings:
    print(warning)
# Output:
# HIGH RISK (system_commands): Found potentially dangerous pattern: subprocess\.
# MEDIUM RISK (database_operations): Pattern needs review: \.execute\s*\(
```

## Mitigation Strategies

### Input Validation
```python
# Before: Dangerous
def delete_file(filename):
    os.remove(filename)

# After: Safe
def delete_file(filename):
    # Validate filename
    if not filename or '..' in filename:
        raise ValueError("Invalid filename")
    
    # Restrict to safe directory
    safe_path = Path("./uploads") / filename
    if not safe_path.is_relative_to("./uploads"):
        raise ValueError("Path outside allowed directory")
    
    safe_path.unlink()
```

### Sandboxing
```python
# Use restricted environments
import subprocess

def safe_command(cmd_args):
    # Only allow specific commands
    allowed_commands = ["git", "ls", "cat"]
    if cmd_args[0] not in allowed_commands:
        raise ValueError("Command not allowed")
    
    # Run with restricted permissions
    result = subprocess.run(
        cmd_args,
        capture_output=True,
        timeout=30,
        cwd="/safe/directory"
    )
    return result.stdout.decode()
```

### Resource Limits
```python
# Implement timeouts and limits
async def limited_operation(data):
    # Size limits
    if len(data) > 1024 * 1024:  # 1MB
        raise ValueError("Data too large")
    
    # Time limits
    try:
        result = await asyncio.wait_for(
            process_data(data),
            timeout=30.0
        )
        return result
    except asyncio.TimeoutError:
        raise ValueError("Operation timed out")
```

## Configuration

Customize security scanning:

```python
from analyzer.security.pattern_scanner import SecurityScanner

scanner = SecurityScanner()

# Add custom patterns
scanner.DANGEROUS_PATTERNS['custom_risk'] = [
    r'dangerous_function\s*\(',
    r'unsafe_operation\s*\('
]

# Adjust risk thresholds
scanner.RISK_THRESHOLD = 3.0  # More strict
```

## Best Practices

1. **Review All High-Risk Functions**: Manual review required
2. **Implement Input Validation**: Validate all external inputs
3. **Use Sandboxing**: Restrict file and network access
4. **Add Monitoring**: Log security-relevant operations
5. **Regular Updates**: Keep security patterns current
"""
    
    def _get_analyzer_conversion(self) -> str:
        return """# Repository Analyzer Conversion Guide

Convert repository analysis results into working MCP servers using the analyzer output.

## Conversion Workflow

### 1. Repository Analysis
```bash
# Generate analysis report
python analyze_repo.py /path/to/repo --min-score 6.0 --show-security
```

### 2. Review Results
- Examine high-scoring functions (7.0+)
- Review security warnings
- Identify conversion candidates

### 3. Interactive Approval
```bash
# Use interactive approval workflow
python generate_docker_server.py /path/to/repo my-server --interactive
```

### 4. Generate MCP Server
```bash
# Generate complete MCP server
python generate_docker_server.py /path/to/repo my-server --build
```

## Conversion Strategies

### High-Score Functions (8-10)
**Strategy**: Direct conversion with minimal changes

```python
# Original function (score: 9.2)
async def analyze_code_quality(file_path: str, metrics: List[str] = None) -> Dict:
    \"\"\"Analyze code quality metrics for a file\"\"\"
    # Implementation
    return {"score": 8.5, "metrics": {}}

# Converted MCP tool (minimal changes)
@mcp.tool()
async def analyze_code_quality(file_path: str, metrics: List[str] = None) -> Dict:
    \"\"\"Analyze code quality metrics for a file\"\"\"
    # Same implementation
    return {"score": 8.5, "metrics": {}}
```

### Medium-Score Functions (6-7)
**Strategy**: Enhance documentation and error handling

```python
# Original function (score: 6.5)
def process_data(data):
    # Basic processing
    return result

# Enhanced for MCP (score: 8.0+)
@mcp.tool()
async def process_data(data: str, format_type: str = "json") -> Dict:
    \"\"\"
    Process input data with specified format.
    
    Args:
        data: Input data to process
        format_type: Output format (json, csv, xml)
    
    Returns:
        Processed data in specified format
        
    Raises:
        ValueError: If data is invalid or format unsupported
    \"\"\"
    try:
        # Add validation
        if not data:
            raise ValueError("Data cannot be empty")
        
        if format_type not in ["json", "csv", "xml"]:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Enhanced processing
        result = enhanced_processing(data, format_type)
        return {"success": True, "result": result, "format": format_type}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Low-Score Functions (3-5)
**Strategy**: Significant refactoring required

```python
# Original function (score: 3.2)
def helper(x, y, z=None):
    if z:
        return x + y + z
    return x + y

# Refactored for MCP (score: 7.5+)
@mcp.tool()
async def calculate_sum(
    first_number: float, 
    second_number: float, 
    third_number: Optional[float] = None
) -> Dict[str, Any]:
    \"\"\"
    Calculate sum of two or three numbers.
    
    Args:
        first_number: First number to add
        second_number: Second number to add  
        third_number: Optional third number to include in sum
        
    Returns:
        Dictionary with calculation result and metadata
    \"\"\"
    try:
        numbers = [first_number, second_number]
        if third_number is not None:
            numbers.append(third_number)
        
        total = sum(numbers)
        
        return {
            "sum": total,
            "count": len(numbers),
            "numbers": numbers,
            "success": True
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "numbers": []
        }
```

## Security Conversion

### Handle High-Risk Functions

```python
# Original (HIGH RISK - score penalty: -3.0)
def read_any_file(path):
    return open(path).read()

# Secured conversion
@mcp.tool()
async def read_safe_file(filename: str) -> Dict:
    \"\"\"
    Read file contents from allowed directory.
    
    Args:
        filename: Name of file to read (no paths allowed)
        
    Returns:
        File contents or error message
    \"\"\"
    try:
        # Security: Restrict to safe directory
        if '/' in filename or '..' in filename:
            return {"success": False, "error": "Invalid filename"}
        
        safe_path = Path("./data") / filename
        if not safe_path.exists():
            return {"success": False, "error": "File not found"}
            
        # Security: Size limit
        if safe_path.stat().st_size > 1024 * 1024:  # 1MB
            return {"success": False, "error": "File too large"}
            
        content = safe_path.read_text(encoding='utf-8')
        
        return {
            "success": True,
            "content": content,
            "filename": filename,
            "size": len(content)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Testing Conversions

### Unit Tests
```python
import pytest
from your_mcp_server import YourMCPServer

@pytest.fixture
async def server():
    return YourMCPServer()

async def test_converted_function(server):
    # Test successful case
    result = await server.calculate_sum(5.0, 3.0, 2.0)
    assert result["success"] is True
    assert result["sum"] == 10.0
    assert result["count"] == 3

async def test_error_handling(server):
    # Test error case
    result = await server.read_safe_file("../etc/passwd")
    assert result["success"] is False
    assert "Invalid filename" in result["error"]
```

### Integration Tests
```python
async def test_mcp_integration():
    # Test with actual MCP client
    client = MCPClient()
    await client.connect_to_server("your-server")
    
    tools = await client.list_tools()
    assert "calculate_sum" in [tool.name for tool in tools]
    
    result = await client.call_tool("calculate_sum", {
        "first_number": 10.0,
        "second_number": 20.0
    })
    assert result["sum"] == 30.0
```

## Best Practices

1. **Start with High Scores**: Convert functions with scores 7.0+ first
2. **Address Security**: Fix security issues before deployment  
3. **Enhance Documentation**: Improve docstrings and type hints
4. **Add Error Handling**: Implement comprehensive error handling
5. **Test Thoroughly**: Create unit and integration tests
6. **Monitor Performance**: Track converted tool performance
"""
    
    def _get_concept_content(self, concept: str) -> str:
        """Get content for search indexing"""
        methods = {
            "tools": self._get_tools_concept,
            "resources": self._get_resources_concept,
            "prompts": self._get_prompts_concept,
            "protocol": self._get_protocol_concept,
        }
        return methods.get(concept, lambda: "")()
    
    def _get_fastmcp_content(self, section: str) -> str:
        """Get FastMCP content for search indexing"""
        methods = {
            "quickstart": self._get_fastmcp_quickstart,
            "decorators": self._get_fastmcp_decorators,
            "resources": self._get_fastmcp_resources,
            "tools": self._get_fastmcp_tools,
            "deployment": self._get_fastmcp_deployment,
        }
        return methods.get(section, lambda: "")()
    
    def _get_analyzer_content(self, topic: str) -> str:
        """Get analyzer content for search indexing"""
        methods = {
            "overview": self._get_analyzer_overview,
            "scoring": self._get_analyzer_scoring,
            "security": self._get_analyzer_security,
            "conversion": self._get_analyzer_conversion,
        }
        return methods.get(topic, lambda: "")()

    def run(self):
        """Run the MCP documentation server"""
        logger.info("Starting MCP Documentation Server...")
        self.mcp.run()

if __name__ == "__main__":
    server = MCPDocumentationServer()
    server.run()