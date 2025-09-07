"""
MCP Server Wrapper Generator

Generates MCP server wrapper code that exposes repository functions as MCP tools.
Enhanced with comprehensive prompts and resources for better documentation.
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# Import from analyzer
import sys
sys.path.append(str(Path(__file__).parent.parent))
from analyzer.models import MCPToolCandidate

# Import prompt and resource generator
from .prompt_generator import PromptResourceGenerator


class ServerWrapperGenerator:
    """Generates MCP server wrapper code for different languages"""
    
    def __init__(self):
        self.prompt_generator = PromptResourceGenerator()
    
    def generate_wrapper(
        self,
        language: str,
        candidates: List[MCPToolCandidate],
        server_name: str,
        repo_info: Dict[str, Any]
    ) -> str:
        """
        Generate MCP server wrapper code
        
        Args:
            language: Programming language
            candidates: List of MCP tool candidates
            server_name: Name of the server
            repo_info: Repository information
            
        Returns:
            Generated server wrapper code
        """
        if language == 'python':
            return self._generate_python_wrapper(candidates, server_name, repo_info)
        elif language == 'javascript':
            return self._generate_javascript_wrapper(candidates, server_name, repo_info)
        elif language == 'go':
            return self._generate_go_wrapper(candidates, server_name, repo_info)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _generate_python_wrapper(
        self,
        candidates: List[MCPToolCandidate],
        server_name: str,
        repo_info: Dict[str, Any]
    ) -> str:
        """Generate Python MCP server wrapper"""
        
        # Generate imports for original functions
        function_imports = []
        function_names = []
        
        for candidate in candidates:
            func_name = candidate.function.function_name
            function_names.append(func_name)
            # Import from the original functions file
            function_imports.append(f"from original_functions import {func_name}")
        
        imports_section = '\\n'.join(function_imports)
        
        # Generate tool definitions
        tool_definitions = []
        for candidate in candidates:
            tool_def = f'''types.Tool(
            name="{candidate.suggested_tool_name}",
            description="{candidate.description}",
            inputSchema={json.dumps(candidate.mcp_parameters, indent=12)}
        )'''
            tool_definitions.append(tool_def)
        
        tools_section = ',\\n        '.join(tool_definitions)
        
        # Generate tool handlers
        tool_handlers = []
        for candidate in candidates:
            func_name = candidate.function.function_name
            tool_name = candidate.suggested_tool_name
            
            # Generate parameter extraction
            param_extractions = []
            for param in candidate.function.parameters:
                if param.required:
                    param_extractions.append(
                        f'{param.name} = arguments.get("{param.name}")'
                    )
                else:
                    default_val = param.default_value or 'None'
                    param_extractions.append(
                        f'{param.name} = arguments.get("{param.name}", {default_val})'
                    )
            
            param_section = '\\n        '.join(param_extractions)
            param_names = [p.name for p in candidate.function.parameters]
            param_call = ', '.join(param_names)
            
            handler = f'''if name == "{tool_name}":
        # Extract parameters
        {param_section}
        
        try:
            # Call the original function
            result = {func_name}({param_call})
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {{str(e)}}")]'''
            
            tool_handlers.append(handler)
        
        handlers_section = '\\n    el'.join(tool_handlers)
        
        # Generate prompts and resources
        prompts_section = self.prompt_generator.generate_prompts(candidates, server_name, repo_info)
        resources_section = self.prompt_generator.generate_resources(candidates, server_name, repo_info)
        
        return f'''#!/usr/bin/env python3
"""
Auto-generated MCP Server: {server_name}
Created from repository: {repo_info.get('name', 'unknown')}
Generated on: {datetime.now().isoformat()}

This server exposes {len(candidates)} functions as MCP tools.
"""

import asyncio
import sys
from typing import Any, Sequence

# MCP SDK imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as types
from mcp.server.stdio import stdio_server

# Import original functions
{imports_section}

# Create MCP server
app = Server("mcp-{server_name}")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        {tools_section}
    ]

@app.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests"""
    
    if arguments is None:
        arguments = {{}}
    
    {handlers_section}
    else:
        return [types.TextContent(
            type="text", 
            text=f"Unknown tool: {{name}}"
        )]

# Prompts and Resources for enhanced documentation
{prompts_section}

{resources_section}

async def main():
    """Main entry point"""
    # Run the MCP server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-{server_name}",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={{}}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def _generate_javascript_wrapper(
        self,
        candidates: List[MCPToolCandidate],
        server_name: str,
        repo_info: Dict[str, Any]
    ) -> str:
        """Generate JavaScript MCP server wrapper"""
        
        # Generate imports for original functions
        function_imports = []
        for candidate in candidates:
            func_name = candidate.function.function_name
            function_imports.append(f"import {{ {func_name} }} from './original_functions.js';")
        
        imports_section = '\\n'.join(function_imports)
        
        # Generate tool definitions
        tool_definitions = []
        for candidate in candidates:
            tool_def = f'''{{
            name: "{candidate.suggested_tool_name}",
            description: "{candidate.description}",
            inputSchema: {json.dumps(candidate.mcp_parameters, indent=12)}
        }}'''
            tool_definitions.append(tool_def)
        
        tools_section = ',\\n            '.join(tool_definitions)
        
        # Generate tool handlers
        tool_handlers = []
        for candidate in candidates:
            func_name = candidate.function.function_name
            tool_name = candidate.suggested_tool_name
            
            # Generate parameter extraction
            param_extractions = []
            for param in candidate.function.parameters:
                if param.required:
                    param_extractions.append(
                        f'const {param.name} = request.params.arguments?.{param.name};'
                    )
                else:
                    default_val = param.default_value or 'undefined'
                    param_extractions.append(
                        f'const {param.name} = request.params.arguments?.{param.name} ?? {default_val};'
                    )
            
            param_section = '\\n        '.join(param_extractions)
            param_names = [p.name for p in candidate.function.parameters]
            param_call = ', '.join(param_names)
            
            handler = f'''if (request.params.name === "{tool_name}") {{
        // Extract parameters
        {param_section}
        
        try {{
            // Call the original function
            const result = await {func_name}({param_call});
            
            // Return result
            return {{
                content: [{{
                    type: "text",
                    text: String(result)
                }}]
            }};
        }} catch (error) {{
            return {{
                content: [{{
                    type: "text", 
                    text: `Error: ${{error.message}}`
                }}]
            }};
        }}
    }}'''
            
            tool_handlers.append(handler)
        
        handlers_section = '\\n    else '.join(tool_handlers)
        
        return f'''#!/usr/bin/env node
/**
 * Auto-generated MCP Server: {server_name}
 * Created from repository: {repo_info.get('name', 'unknown')}
 * Generated on: {datetime.now().isoformat()}
 * 
 * This server exposes {len(candidates)} functions as MCP tools.
 */

import {{ Server }} from "@modelcontextprotocol/sdk/server/index.js";
import {{ StdioServerTransport }} from "@modelcontextprotocol/sdk/server/stdio.js";
import {{ 
    CallToolRequestSchema,
    ListToolsRequestSchema,
}} from "@modelcontextprotocol/sdk/types.js";

// Import original functions
{imports_section}

// Create MCP server
const server = new Server(
    {{ 
        name: "mcp-{server_name}", 
        version: "1.0.0" 
    }},
    {{ 
        capabilities: {{ 
            tools: {{}} 
        }} 
    }}
);

// List tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => {{
    return {{
        tools: [
            {tools_section}
        ]
    }};
}});

// Call tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {{
    {handlers_section}
    else {{
        return {{
            content: [{{
                type: "text",
                text: `Unknown tool: ${{request.params.name}}`
            }}]
        }};
    }}
}});

// Start server
async function main() {{
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("MCP server {server_name} running on stdio");
}}

main().catch(console.error);
'''
    
    def _generate_go_wrapper(
        self,
        candidates: List[MCPToolCandidate],
        server_name: str,
        repo_info: Dict[str, Any]
    ) -> str:
        """Generate Go MCP server wrapper (basic implementation)"""
        
        return f'''package main

/*
Auto-generated MCP Server: {server_name}
Created from repository: {repo_info.get('name', 'unknown')}
Generated on: {datetime.now().isoformat()}

This server exposes {len(candidates)} functions as MCP tools.
*/

import (
    "encoding/json"
    "fmt"
    "log"
    "os"
)

func main() {{
    // Basic Go MCP server implementation
    // TODO: Implement full MCP protocol support
    fmt.Println("Go MCP server not fully implemented yet")
    log.Println("Server {server_name} would expose {len(candidates)} tools")
    os.Exit(1)
}}
'''