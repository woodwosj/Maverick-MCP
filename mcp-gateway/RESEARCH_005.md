# Research Report for Task-005
Date: 2025-09-06
Task: MCP Documentation Server - FastMCP and Protocol reference hub

## Requirements

Task-005 focuses on creating an MCP Documentation Server that provides:

1. FastMCP framework documentation as MCP resources
2. MCP Protocol reference documentation
3. Repository analysis documentation and guides
4. Integration with the existing gateway architecture
5. Access patterns like `docs://mcp/concepts/{topic}` and `docs://fastmcp/{section}`

## Documentation Found

### MCP Protocol Overview

**Model Context Protocol (MCP)**:
- Standard protocol for AI model context management
- Uses JSON-RPC over STDIO for communication
- Defines Tools, Resources, and Prompts as core concepts
- Tools: Executable functions exposed to AI models
- Resources: Data/content that can be retrieved
- Prompts: Pre-defined interaction templates

**FastMCP Framework**:
- Python framework for building MCP servers
- Uses decorators for tool definition
- Provides async support and context management
- Currently used in gateway.py with version >=2.0.0

### Existing Documentation Infrastructure

**Current Documentation Assets**:
1. README.md - Basic gateway setup and usage
2. RESEARCH_*.md files - Task-specific research reports
3. servers/context7 - Example MCP server implementation
4. Tool descriptions in servers.yaml configuration

**Documentation Access Patterns**:
- Context7 server already provides `get_documentation` tool for library docs
- Gateway exposes tool descriptions without implementation details
- Need to differentiate between Tools (executable) and Resources (retrievable content)

## Code Examples

### MCP Resource Server Pattern (Python with FastMCP)

```python
from fastmcp import FastMCP, Resource
from typing import List, Dict, Optional
import json
from pathlib import Path

class DocumentationServer:
    """MCP server providing documentation as resources"""
    
    def __init__(self):
        self.mcp = FastMCP("mcp-docs-server")
        self.docs_path = Path("./documentation")
        self.setup_resources()
    
    def setup_resources(self):
        """Register documentation resources"""
        
        @self.mcp.resource("docs://mcp/concepts/{topic}")
        async def get_mcp_concept(topic: str) -> Dict:
            """Get MCP protocol concept documentation"""
            concepts = {
                "tools": "Tools are executable functions exposed by MCP servers...",
                "resources": "Resources are data/content that can be retrieved...",
                "prompts": "Prompts are pre-defined interaction templates...",
                "protocol": "MCP uses JSON-RPC 2.0 over STDIO...",
            }
            
            if topic not in concepts:
                return {"error": f"Unknown concept: {topic}"}
            
            return {
                "uri": f"docs://mcp/concepts/{topic}",
                "mimeType": "text/markdown",
                "content": concepts[topic]
            }
        
        @self.mcp.resource("docs://fastmcp/{section}")
        async def get_fastmcp_docs(section: str) -> Dict:
            """Get FastMCP framework documentation"""
            sections = {
                "quickstart": "# FastMCP Quick Start\n\n```python\nfrom fastmcp import FastMCP...",
                "decorators": "# FastMCP Decorators\n\n@mcp.tool() - Define a tool...",
                "context": "# Context Management\n\nFastMCP provides context...",
                "deployment": "# Deployment Guide\n\nDeploy with Docker..."
            }
            
            if section not in sections:
                return {"error": f"Unknown section: {section}"}
            
            return {
                "uri": f"docs://fastmcp/{section}",
                "mimeType": "text/markdown", 
                "content": sections[section]
            }
        
        @self.mcp.tool()
        async def search_documentation(query: str, category: Optional[str] = None) -> List[Dict]:
            """Search across all documentation"""
            results = []
            # Search implementation
            return results
```

### Documentation Content Structure

```markdown
documentation/
├── mcp/
│   ├── concepts/
│   │   ├── tools.md
│   │   ├── resources.md
│   │   ├── prompts.md
│   │   └── protocol.md
│   ├── guides/
│   │   ├── getting-started.md
│   │   ├── building-servers.md
│   │   └── best-practices.md
│   └── reference/
│       ├── json-rpc.md
│       └── message-types.md
├── fastmcp/
│   ├── quickstart.md
│   ├── decorators.md
│   ├── context.md
│   ├── deployment.md
│   └── api-reference.md
└── analyzer/
    ├── repository-analysis.md
    ├── scoring-algorithm.md
    └── conversion-guide.md
```

## Important Notes

### Resource vs Tool Distinction

**Resources** (for documentation):
- Static or semi-static content retrieval
- Use URI patterns like `docs://protocol/topic`
- Return content with MIME types
- Ideal for documentation, reference materials
- Can be cached and indexed

**Tools** (for actions):
- Execute functions and return results
- Take parameters and perform operations
- Used for search, analysis, generation
- Current gateway already handles tool routing

### Integration with Gateway Architecture

**Current Gateway Flow**:
1. Gateway receives requests at `http://localhost:8000`
2. Routes to appropriate Docker container via STDIO
3. Manages container lifecycle (spawn/cleanup)
4. Returns results to client

**Documentation Server Integration**:
- Deploy as another Docker container like context7
- Register in servers.yaml with documentation tools/resources
- Gateway handles routing automatically
- Can run alongside existing MCP servers

### Content Management Considerations

**Static Documentation**:
- Store as Markdown files in container
- Version control with git
- Update via container rebuilds

**Dynamic Documentation**:
- Generate from code analysis
- Pull from external sources
- Cache with TTL for performance

**Search and Discovery**:
- Implement full-text search tool
- Provide category browsing
- Cross-reference related topics

## Suggested Approach

### Phase 1: Core Documentation Server (Immediate)

1. **Create mcp_docs_server.py**
   - FastMCP server with resource handlers
   - Load documentation from markdown files
   - Implement URI routing for docs://mcp and docs://fastmcp

2. **Documentation Content Creation**
   - Write core MCP protocol documentation
   - Create FastMCP usage guides
   - Document repository analyzer usage

3. **Docker Container Setup**
   - Create Dockerfile for documentation server
   - Add to servers.yaml configuration
   - Test with gateway integration

### Phase 2: Enhanced Features (Follow-up)

4. **Search and Discovery**
   - Full-text search across all documentation
   - Category-based browsing
   - Related content suggestions

5. **Dynamic Content Generation**
   - Auto-generate API references from code
   - Create interactive examples
   - Version-specific documentation

### Phase 3: Integration Tools (Future)

6. **Repository Analysis Documentation**
   - `analyze_repo_for_mcp()` tool implementation
   - Generate custom guides based on repo analysis
   - Conversion best practices

## Technical Architecture

### Documentation Server Components

```
MCP Documentation Server
├── mcp_docs_server.py      # FastMCP server implementation
├── documentation/           # Markdown documentation files
│   ├── mcp/                # MCP protocol docs
│   ├── fastmcp/            # FastMCP framework docs
│   └── analyzer/           # Repository analyzer docs
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── servers_entry.yaml      # Gateway registration
```

### Resource URI Patterns

```
docs://mcp/concepts/tools           # MCP tool concept
docs://mcp/guides/getting-started   # Getting started guide
docs://fastmcp/decorators          # FastMCP decorator reference
docs://fastmcp/api/tool            # API reference for @tool
docs://analyzer/scoring            # Scoring algorithm docs
```

### Gateway Registration

```yaml
# servers.yaml entry
mcp-docs:
  image: "mcp-docs-server"
  command: ["python", "mcp_docs_server.py"]
  description: "MCP and FastMCP documentation server"
  idle_timeout: 600  # Keep alive longer for documentation
  resources:
    - pattern: "docs://mcp/**"
      description: "MCP protocol documentation"
    - pattern: "docs://fastmcp/**"
      description: "FastMCP framework documentation"
  tools:
    - name: "search_documentation"
      description: "Search across all documentation"
    - name: "list_documentation_topics"
      description: "List available documentation topics"
```

### Implementation Priority

1. **High Priority**:
   - Basic resource server with markdown loading
   - Core MCP and FastMCP documentation
   - Gateway integration

2. **Medium Priority**:
   - Search functionality
   - Repository analyzer documentation
   - Interactive examples

3. **Low Priority**:
   - Auto-generated API docs
   - Version management
   - External source integration

This approach provides a comprehensive documentation server that integrates seamlessly with the existing MCP gateway architecture while maintaining clear separation between documentation resources and executable tools.