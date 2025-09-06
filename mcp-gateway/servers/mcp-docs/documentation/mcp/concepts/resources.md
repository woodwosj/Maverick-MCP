# MCP Resources

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
    """Get MCP protocol concept documentation"""
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
- Database query results