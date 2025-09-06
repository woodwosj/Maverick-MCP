#!/usr/bin/env python3
"""
Auto-generated MCP Server: test-server
Created from repository: test_data
Generated on: 2025-09-06T04:40:54.942081

This server exposes 8 functions as MCP tools.
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
from original_functions import process_csv_data\nfrom original_functions import fetch_user_data\nfrom original_functions import validate_email\nfrom original_functions import calculate_compound_interest\nfrom original_functions import transform_json_data\nfrom original_functions import async_function_example\nfrom original_functions import dangerous_file_operation\nfrom original_functions import function_with_complex_types

# Create MCP server
app = Server("mcp-test-server")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        types.Tool(
            name="process_csv_data",
            description="Process CSV data and return cleaned results",
            inputSchema={
            "type": "object",
            "properties": {
                        "csv_path": {
                                    "type": "string",
                                    "description": "Parameter csv_path"
                        },
                        "clean_nulls": {
                                    "type": "boolean",
                                    "description": "Parameter clean_nulls",
                                    "default": "True"
                        }
            },
            "required": [
                        "csv_path"
            ]
}
        ),\n        types.Tool(
            name="fetch_user_data",
            description="Fetch user data from REST API",
            inputSchema={
            "type": "object",
            "properties": {
                        "api_url": {
                                    "type": "string",
                                    "description": "Parameter api_url"
                        },
                        "user_id": {
                                    "type": "integer",
                                    "description": "Parameter user_id"
                        },
                        "timeout": {
                                    "type": "integer",
                                    "description": "Parameter timeout",
                                    "default": "30"
                        }
            },
            "required": [
                        "api_url",
                        "user_id"
            ]
}
        ),\n        types.Tool(
            name="validate_email",
            description="Validate email address format",
            inputSchema={
            "type": "object",
            "properties": {
                        "email": {
                                    "type": "string",
                                    "description": "Parameter email"
                        }
            },
            "required": [
                        "email"
            ]
}
        ),\n        types.Tool(
            name="calculate_compound_interest",
            description="Calculate compound interest",
            inputSchema={
            "type": "object",
            "properties": {
                        "principal": {
                                    "type": "number",
                                    "description": "Parameter principal"
                        },
                        "rate": {
                                    "type": "number",
                                    "description": "Parameter rate"
                        },
                        "time": {
                                    "type": "number",
                                    "description": "Parameter time"
                        },
                        "n": {
                                    "type": "integer",
                                    "description": "Parameter n",
                                    "default": "1"
                        }
            },
            "required": [
                        "principal",
                        "rate",
                        "time"
            ]
}
        ),\n        types.Tool(
            name="transform_json_data",
            description="Transform JSON data to different formats",
            inputSchema={
            "type": "object",
            "properties": {
                        "json_data": {
                                    "type": "string",
                                    "description": "Parameter json_data"
                        },
                        "format_type": {
                                    "type": "string",
                                    "description": "Parameter format_type",
                                    "default": "'compact'"
                        }
            },
            "required": [
                        "json_data"
            ]
}
        ),\n        types.Tool(
            name="async_function_example",
            description="Async function example for testing async support",
            inputSchema={
            "type": "object",
            "properties": {
                        "url": {
                                    "type": "string",
                                    "description": "Parameter url"
                        }
            },
            "required": [
                        "url"
            ]
}
        ),\n        types.Tool(
            name="dangerous_file_operation",
            description="This function performs dangerous file operations",
            inputSchema={
            "type": "object",
            "properties": {
                        "file_path": {
                                    "type": "string",
                                    "description": "Parameter file_path"
                        }
            },
            "required": [
                        "file_path"
            ]
}
        ),\n        types.Tool(
            name="function_with_complex_types",
            description="Function with complex type hints to test type parsing",
            inputSchema={
            "type": "object",
            "properties": {
                        "data": {
                                    "type": "string",
                                    "description": "Parameter data"
                        }
            },
            "required": [
                        "data"
            ]
}
        )
    ]

@app.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests"""
    
    if arguments is None:
        arguments = {}
    
    if name == "process_csv_data":
        # Extract parameters
        csv_path = arguments.get("csv_path")\n        clean_nulls = arguments.get("clean_nulls", True)
        
        try:
            # Call the original function
            result = process_csv_data(csv_path, clean_nulls)
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]\n    elif name == "fetch_user_data":
        # Extract parameters
        api_url = arguments.get("api_url")\n        user_id = arguments.get("user_id")\n        timeout = arguments.get("timeout", 30)
        
        try:
            # Call the original function
            result = fetch_user_data(api_url, user_id, timeout)
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]\n    elif name == "validate_email":
        # Extract parameters
        email = arguments.get("email")
        
        try:
            # Call the original function
            result = validate_email(email)
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]\n    elif name == "calculate_compound_interest":
        # Extract parameters
        principal = arguments.get("principal")\n        rate = arguments.get("rate")\n        time = arguments.get("time")\n        n = arguments.get("n", 1)
        
        try:
            # Call the original function
            result = calculate_compound_interest(principal, rate, time, n)
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]\n    elif name == "transform_json_data":
        # Extract parameters
        json_data = arguments.get("json_data")\n        format_type = arguments.get("format_type", 'compact')
        
        try:
            # Call the original function
            result = transform_json_data(json_data, format_type)
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]\n    elif name == "async_function_example":
        # Extract parameters
        url = arguments.get("url")
        
        try:
            # Call the original function
            result = async_function_example(url)
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]\n    elif name == "dangerous_file_operation":
        # Extract parameters
        file_path = arguments.get("file_path")
        
        try:
            # Call the original function
            result = dangerous_file_operation(file_path)
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]\n    elif name == "function_with_complex_types":
        # Extract parameters
        data = arguments.get("data")
        
        try:
            # Call the original function
            result = function_with_complex_types(data)
            
            # Return result as TextContent
            return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    else:
        return [types.TextContent(
            type="text", 
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Main entry point"""
    # Run the MCP server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-test-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
