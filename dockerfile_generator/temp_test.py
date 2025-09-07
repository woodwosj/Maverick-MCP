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
        prompts.append(self._generate_architecture_prompt(server_name))
        
        # Tool-specific prompts
        for candidate in candidates:
            prompts.append(self._generate_tool_prompt(candidate))
        
        # Troubleshooting prompt
        prompts.append(self._generate_troubleshooting_prompt(server_name))
        
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
        
        tools_section = "\n".join(tool_list)
        
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
        content = f\"\"\"# {server_name} MCP Server Usage Guide

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
AI Client ↔ MCP Protocol ↔ STDIO ↔ {server_name} Server ↔ Original Functions
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
\"\"\"
        
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
\"\"\"
    
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

