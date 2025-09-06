# RESEARCH REPORT: Dockerfile Generator Implementation
**Task ID**: Task-002  
**Agent**: Context Manager  
**Date**: 2025-09-06  
**Priority**: HIGH

## Executive Summary

Research for implementing a template-based Dockerfile generator that works with the Repository Analyzer to automatically create appropriate Docker containers for MCP servers. The generator should support multiple programming languages and create optimized containers based on detected dependencies and function requirements.

## Key Requirements Analysis

### Integration with Repository Analyzer
- **Input**: MCPToolCandidate objects from Task-001 analyzer
- **Output**: Complete Dockerfile + MCP server wrapper code
- **Dependency Detection**: Use docker_requirements from analyzer
- **Language Support**: Python, JavaScript/Node.js, Go (extensible)

### Current MCP Server Patterns (from existing servers)

#### Context7 Server (Node.js Pattern):
```dockerfile
FROM node:18-alpine
WORKDIR /app
RUN npm init -y && npm pkg set type="module" && npm install @modelcontextprotocol/sdk axios cheerio
COPY server.js .
ENV NODE_ENV=production
CMD ["node", "server.js"]
```

#### Gateway Server (Python Pattern):
```dockerfile  
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY gateway.py .
EXPOSE 8000
CMD ["python", "gateway.py"]
```

## Dockerfile Generation Strategy

### Template-Based Approach

#### 1. Language-Specific Base Templates

**Python Template Structure:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY {source_files} .
ENV PYTHONPATH=/app
CMD ["python", "mcp_server.py"]
```

**Node.js Template Structure:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
RUN npm init -y && npm pkg set type="module"
RUN npm install {npm_packages}
COPY {source_files} .
ENV NODE_ENV=production
CMD ["node", "mcp_server.js"]
```

**Go Template Structure:**
```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY {source_files} .
RUN go build -o mcp_server

FROM alpine:latest
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/mcp_server .
CMD ["./mcp_server"]
```

### 2. Dynamic Template Variables

#### Required Variables:
- `{base_image}`: Language-specific base image
- `{source_files}`: Generated MCP server files
- `{dependencies}`: Package requirements/dependencies  
- `{environment_vars}`: Runtime environment variables
- `{exposed_ports}`: Container ports (usually none for MCP servers)
- `{startup_command}`: Container startup command

#### Conditional Sections:
- Database connections (if detected)
- Network requirements (if API calls detected)
- File system access (if file operations detected)
- Security contexts (for privileged operations)

## MCP Server Wrapper Generation

### Server Wrapper Templates

#### Python MCP Server Wrapper:
```python
#!/usr/bin/env python3
"""
Auto-generated MCP Server
Created from repository: {repo_name}
Generated on: {generation_date}
"""

import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from typing import Any, Sequence
import mcp.types as types

# Import the original functions
{function_imports}

app = Server("mcp-{server_name}")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        {tool_definitions}
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    {tool_handlers}
    
if __name__ == "__main__":
    import mcp.server.stdio
    mcp.server.stdio.run_server(app)
```

#### Node.js MCP Server Wrapper:
```javascript
#!/usr/bin/env node
/**
 * Auto-generated MCP Server
 * Created from repository: {repo_name}
 * Generated on: {generation_date}
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { 
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Import the original functions  
{function_imports}

const server = new Server(
    {{ name: "mcp-{server_name}", version: "1.0.0" }},
    {{ capabilities: {{ tools: {{}} }} }}
);

server.setRequestHandler(ListToolsRequestSchema, async () => {{
    return {{
        tools: [
            {tool_definitions}
        ]
    }};
}});

server.setRequestHandler(CallToolRequestSchema, async (request) => {{
    {tool_handlers}
}});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Dependency Management System

### 1. Dependency Detection and Resolution

#### Python Dependency Analysis:
```python
class PythonDependencyResolver:
    STANDARD_LIBRARY = {...}  # Python stdlib modules
    
    def resolve_dependencies(self, functions: List[FunctionCandidate]) -> Dict[str, str]:
        requirements = set()
        
        for func in functions:
            # Analyze import statements
            imports = self.extract_imports(func.source_code)
            
            # Add MCP SDK
            requirements.add("mcp>=1.0.0")
            
            # Add detected packages
            for imp in imports:
                if imp not in self.STANDARD_LIBRARY:
                    version = self.get_package_version(imp)
                    requirements.add(f"{imp}{version}")
        
        return sorted(requirements)
```

#### Node.js Dependency Analysis:
```javascript
class NodeDependencyResolver {
    async resolveDependencies(functions) {
        const dependencies = new Set([
            "@modelcontextprotocol/sdk"  // Always required
        ]);
        
        for (const func of functions) {
            const imports = this.extractRequires(func.source_code);
            dependencies.add(...imports);
        }
        
        return Array.from(dependencies);
    }
}
```

### 2. Package Version Management
- Use latest stable versions by default
- Support for pinned versions from package files
- Security vulnerability scanning for known bad versions
- Compatibility matrix for MCP SDK versions

## Security Considerations

### Container Security Best Practices

#### 1. Base Image Selection:
- Use official slim/alpine images when possible
- Avoid `latest` tags, pin specific versions
- Scan base images for vulnerabilities

#### 2. User Permissions:
```dockerfile
# Create non-root user for Python containers
RUN adduser --disabled-password --gecos '' mcpuser
USER mcpuser
```

#### 3. File System Security:
```dockerfile  
# Read-only root filesystem for enhanced security
CMD ["python", "mcp_server.py"]
USER 1000:1000
```

#### 4. Network Security:
- No exposed ports by default (MCP uses STDIO)
- Restricted network access if not needed
- Environment variable validation

### Security Integration with Pattern Scanner
```python
def generate_secure_dockerfile(candidates: List[MCPToolCandidate]) -> str:
    # Check security warnings from analyzer
    high_risk_functions = [c for c in candidates if any("HIGH RISK" in w for w in c.security_warnings)]
    
    if high_risk_functions:
        # Add additional security layers
        template = SECURE_DOCKERFILE_TEMPLATE
        template += """
# Additional security for high-risk functions
RUN adduser --disabled-password mcpuser
USER mcpuser
"""
    return template
```

## Template System Architecture

### 1. Template Engine Selection
- **Jinja2**: Powerful templating with conditionals, loops, filters
- **String Templates**: Simple variable substitution
- **Custom Engine**: Specialized for Dockerfile generation

#### Jinja2 Implementation:
```python
from jinja2 import Environment, FileSystemLoader

class DockerfileGenerator:
    def __init__(self, template_dir: str = "templates/"):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate(self, language: str, context: dict) -> str:
        template = self.env.get_template(f"{language}.dockerfile.j2")
        return template.render(**context)
```

### 2. Template Directory Structure:
```
dockerfile_generator/
├── templates/
│   ├── python.dockerfile.j2
│   ├── nodejs.dockerfile.j2
│   ├── go.dockerfile.j2
│   └── common/
│       ├── security.j2
│       └── cleanup.j2
├── server_wrappers/
│   ├── python_server.py.j2
│   ├── nodejs_server.js.j2
│   └── go_server.go.j2
└── requirements/
    ├── python_base.txt
    ├── nodejs_base.json
    └── go_base.mod
```

### 3. Context Generation:
```python
def build_dockerfile_context(
    candidates: List[MCPToolCandidate],
    language: str,
    repo_info: Dict[str, Any]
) -> Dict[str, Any]:
    
    return {
        "language": language,
        "base_image": get_base_image(language),
        "dependencies": resolve_dependencies(candidates, language),
        "functions": candidates,
        "repo_name": repo_info.get("name"),
        "security_level": calculate_security_level(candidates),
        "environment_vars": extract_env_vars(candidates),
        "generation_date": datetime.now().isoformat(),
        "mcp_tools": generate_tool_definitions(candidates)
    }
```

## Integration with Repository Analyzer

### Workflow Integration:
1. **Repository Analyzer** identifies function candidates
2. **Dockerfile Generator** creates containers for candidates
3. **Security Scanner** validates generated containers
4. **User Approval** reviews complete package
5. **Container Builder** builds and registers images

### Data Flow:
```python
# From Repository Analyzer (Task-001)
analysis_result: AnalysisResult = analyzer.analyze_repository(repo_path)

# To Dockerfile Generator (Task-002)  
docker_generator = DockerfileGenerator()
for language in analysis_result.languages:
    language_candidates = [c for c in analysis_result.candidates if c.function.language == language]
    
    dockerfile = docker_generator.generate_dockerfile(language, language_candidates)
    server_code = docker_generator.generate_server_wrapper(language, language_candidates)
    
    # Output: Complete MCP server package ready for building
```

## Expected Output Format

### Generated Package Structure:
```
generated_servers/{server_name}/
├── Dockerfile
├── requirements.txt (or package.json, go.mod)
├── mcp_server.py (or .js, .go)
├── original_functions.py (extracted from repo)
├── .dockerignore
├── README.md (auto-generated documentation)
└── test_server.py (basic functionality tests)
```

### Server Registration Entry:
```yaml
# Auto-generated servers.yaml entry
{server_name}:
  image: "mcp-{server_name}"
  command: ["{runtime}", "mcp_server.{ext}"]
  description: "Auto-generated from {repo_name}"
  environment:
    {env_vars}
  idle_timeout: 300
  tools: {tool_definitions}
```

## Implementation Priorities

### Phase 1: Core Generation Engine
1. Template system with Jinja2
2. Python Dockerfile generation
3. Python MCP server wrapper generation
4. Basic dependency resolution
5. Integration with Repository Analyzer output

### Phase 2: Multi-Language Support  
1. Node.js Dockerfile templates
2. Go Dockerfile templates
3. Language-specific dependency resolvers
4. Cross-language dependency conflict resolution

### Phase 3: Advanced Features
1. Security-hardened container generation
2. Multi-stage builds for optimized images
3. Custom base image selection
4. Performance optimization templates
5. Caching layer optimization

### Phase 4: Integration Features
1. Direct integration with Docker daemon
2. Automatic image building and tagging
3. Registry push/pull capabilities
4. Health check generation
5. Monitoring and metrics integration

## Error Handling and Edge Cases

### 1. Dependency Conflicts:
- Version pinning strategies
- Alternative package suggestions
- Manual override capabilities

### 2. Security Violations:
- Reject high-risk functions automatically
- Provide secure alternatives
- User warning and confirmation flows

### 3. Template Failures:
- Fallback to minimal working templates
- Error reporting with suggested fixes
- Template validation before generation

### 4. Build Failures:
- Dependency resolution retry logic
- Alternative base image fallbacks
- Comprehensive error logging

## Testing Strategy

### 1. Unit Tests:
- Template rendering correctness
- Dependency resolution accuracy
- Security validation logic

### 2. Integration Tests:
- End-to-end dockerfile generation
- Container build and run tests
- MCP protocol compliance validation

### 3. Security Tests:
- Container vulnerability scanning
- Permission and access validation
- Network isolation verification

## Performance Considerations

### 1. Template Caching:
- Pre-compiled Jinja2 templates
- Dependency resolution caching
- Base image layer reuse

### 2. Build Optimization:
- Multi-stage Docker builds
- Layer ordering for cache efficiency
- Minimal base images

### 3. Generation Speed:
- Parallel dockerfile generation
- Async template processing
- Incremental builds for updates

## Conclusion

The Dockerfile Generator should be implemented as a template-based system that seamlessly integrates with the Repository Analyzer. Priority should be on Python support first, with a clean architecture that easily extends to other languages. Security must be built-in from the start, with automatic scanning and hardening of generated containers.

**Estimated Development Time**: 4-6 days for Phase 1 implementation  
**Key Success Metrics**:
- Generate working Dockerfiles for 95%+ of analyzed Python repositories
- All generated containers pass security baseline scans
- Complete integration with Repository Analyzer workflow
- Template system extensible to new languages within 1 day

---

**Next Agent**: CODER  
**Next Task**: Implement Dockerfile Generator with template system and Python support