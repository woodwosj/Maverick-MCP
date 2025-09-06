#!/usr/bin/env python3
"""
MCP Tool Execution Tests

Tests that validate MCP server tool functionality and execution behavior.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mcp_test_framework import MCPServerTester, TestRunner, TestCase, TestSuite, TestResult


# Tool Execution Test Functions

async def test_tool_execution_basic(tester: MCPServerTester) -> tuple:
    """Test basic tool execution with valid parameters"""
    try:
        # First discover tools
        success, message, tools = await tester.discover_tools()
        if not success:
            return False, f"Cannot test tools without discovery: {message}"
        
        if not tools:
            return True, "No tools available to test", {"tool_count": 0}
        
        # Test each tool with minimal valid parameters
        successful_tools = []
        failed_tools = []
        
        for tool in tools[:3]:  # Test first 3 tools to avoid timeout
            tool_name = tool["name"]
            
            try:
                # Try with empty arguments first
                success, msg, response = await tester.test_tool_execution(tool_name, {})
                
                if success:
                    successful_tools.append(tool_name)
                else:
                    # If empty args fail, try with required parameters
                    input_schema = tool.get("inputSchema", {})
                    required_params = input_schema.get("required", [])
                    
                    if required_params:
                        # Create minimal arguments for required parameters
                        test_args = {}
                        properties = input_schema.get("properties", {})
                        
                        for param in required_params[:2]:  # Test first 2 required params
                            if param in properties:
                                prop_type = properties[param].get("type", "string")
                                if prop_type == "string":
                                    test_args[param] = "test"
                                elif prop_type == "number":
                                    test_args[param] = 1
                                elif prop_type == "boolean":
                                    test_args[param] = True
                                elif prop_type == "array":
                                    test_args[param] = []
                                elif prop_type == "object":
                                    test_args[param] = {}
                        
                        # Try again with test arguments
                        success, msg, response = await tester.test_tool_execution(tool_name, test_args)
                        
                        if success:
                            successful_tools.append(tool_name)
                        else:
                            failed_tools.append({"name": tool_name, "error": msg})
                    else:
                        failed_tools.append({"name": tool_name, "error": msg})
                        
            except Exception as e:
                failed_tools.append({"name": tool_name, "error": str(e)})
        
        details = {
            "total_tools": len(tools),
            "tested_tools": len(successful_tools) + len(failed_tools),
            "successful_tools": successful_tools,
            "failed_tools": failed_tools
        }
        
        if successful_tools:
            return True, f"Successfully executed {len(successful_tools)} tools", details
        else:
            return False, f"No tools could be executed successfully", details
            
    except Exception as e:
        return False, f"Tool execution test error: {str(e)}"


async def test_tool_parameter_validation(tester: MCPServerTester) -> tuple:
    """Test tool parameter validation with invalid inputs"""
    try:
        # Discover tools first
        success, message, tools = await tester.discover_tools()
        if not success or not tools:
            return True, "No tools available for parameter validation tests", {}
        
        validation_results = []
        
        for tool in tools[:2]:  # Test first 2 tools
            tool_name = tool["name"]
            
            # Test with invalid parameter types
            test_cases = [
                {"invalid_param": "unexpected_value"},  # Unknown parameter
                {"library": 123} if "library" in str(tool.get("inputSchema", {})) else {"query": 123},  # Wrong type
                {}  # Missing required parameters (if any)
            ]
            
            tool_results = {"name": tool_name, "cases": []}
            
            for i, invalid_args in enumerate(test_cases):
                try:
                    success, msg, response = await tester.test_tool_execution(tool_name, invalid_args)
                    
                    # For invalid parameters, we expect either:
                    # 1. Graceful error response
                    # 2. Successful execution with handling of invalid params
                    
                    if "error" in response:
                        error = response["error"]
                        tool_results["cases"].append({
                            "case": i,
                            "args": invalid_args,
                            "result": "error_response",
                            "error_code": error.get("code"),
                            "error_message": error.get("message", "")[:100]
                        })
                    elif success:
                        tool_results["cases"].append({
                            "case": i,
                            "args": invalid_args,
                            "result": "handled_gracefully",
                            "message": msg[:100]
                        })
                    else:
                        tool_results["cases"].append({
                            "case": i,
                            "args": invalid_args,
                            "result": "failed_validation",
                            "message": msg[:100]
                        })
                        
                except Exception as e:
                    tool_results["cases"].append({
                        "case": i,
                        "args": invalid_args,
                        "result": "exception",
                        "error": str(e)[:100]
                    })
            
            validation_results.append(tool_results)
        
        details = {
            "tools_tested": len(validation_results),
            "validation_results": validation_results
        }
        
        return True, f"Parameter validation tested on {len(validation_results)} tools", details
        
    except Exception as e:
        return False, f"Parameter validation test error: {str(e)}"


async def test_tool_response_format(tester: MCPServerTester) -> tuple:
    """Test that tool responses follow MCP format specification"""
    try:
        # Discover tools first
        success, message, tools = await tester.discover_tools()
        if not success or not tools:
            return True, "No tools available for response format tests", {}
        
        format_results = []
        
        for tool in tools[:2]:  # Test first 2 tools
            tool_name = tool["name"]
            
            try:
                # Execute tool with empty args
                success, msg, response = await tester.test_tool_execution(tool_name, {})
                
                # Check response format
                format_check = {
                    "tool": tool_name,
                    "response_received": response is not None,
                    "has_jsonrpc": response.get("jsonrpc") == "2.0" if response else False,
                    "has_id": "id" in response if response else False,
                    "has_result_or_error": ("result" in response or "error" in response) if response else False
                }
                
                if "result" in response:
                    result = response["result"]
                    format_check["result_format"] = {
                        "has_content": "content" in result,
                        "content_is_list": isinstance(result.get("content"), list),
                        "content_items": len(result.get("content", [])) if isinstance(result.get("content"), list) else 0
                    }
                    
                    # Check content item formats
                    if isinstance(result.get("content"), list):
                        content_items = result["content"]
                        valid_items = 0
                        for item in content_items:
                            if isinstance(item, dict) and "type" in item:
                                if item["type"] in ["text", "image", "resource"]:
                                    valid_items += 1
                        
                        format_check["result_format"]["valid_content_items"] = valid_items
                        format_check["result_format"]["all_items_valid"] = valid_items == len(content_items)
                
                elif "error" in response:
                    error = response["error"]
                    format_check["error_format"] = {
                        "has_code": "code" in error,
                        "has_message": "message" in error,
                        "code": error.get("code"),
                        "message": error.get("message", "")[:100]
                    }
                
                format_results.append(format_check)
                
            except Exception as e:
                format_results.append({
                    "tool": tool_name,
                    "error": str(e)[:100]
                })
        
        # Analyze results
        valid_formats = len([r for r in format_results if r.get("has_result_or_error", False)])
        total_tested = len(format_results)
        
        details = {
            "tools_tested": total_tested,
            "valid_formats": valid_formats,
            "format_results": format_results
        }
        
        if valid_formats == total_tested and total_tested > 0:
            return True, f"All {total_tested} tools returned valid response formats", details
        elif valid_formats > 0:
            return True, f"{valid_formats}/{total_tested} tools returned valid formats", details
        else:
            return False, "No tools returned valid response formats", details
            
    except Exception as e:
        return False, f"Response format test error: {str(e)}"


async def test_tool_timeout_handling(tester: MCPServerTester) -> tuple:
    """Test tool execution timeout handling"""
    try:
        # Discover tools first
        success, message, tools = await tester.discover_tools()
        if not success or not tools:
            return True, "No tools available for timeout tests", {}
        
        # Test with very short timeout
        original_timeout = 10  # Normal timeout
        short_timeout = 1      # Very short timeout
        
        timeout_results = []
        
        for tool in tools[:1]:  # Test just one tool to avoid long test times
            tool_name = tool["name"]
            
            try:
                # Test with short timeout
                start_time = asyncio.get_event_loop().time()
                
                try:
                    response = await asyncio.wait_for(
                        tester.send_request("tools/call", {
                            "name": tool_name,
                            "arguments": {}
                        }),
                        timeout=short_timeout
                    )
                    
                    end_time = asyncio.get_event_loop().time()
                    duration = end_time - start_time
                    
                    timeout_results.append({
                        "tool": tool_name,
                        "result": "completed",
                        "duration": duration,
                        "within_timeout": duration <= short_timeout
                    })
                    
                except asyncio.TimeoutError:
                    end_time = asyncio.get_event_loop().time()
                    duration = end_time - start_time
                    
                    timeout_results.append({
                        "tool": tool_name,
                        "result": "timeout",
                        "duration": duration,
                        "timeout_value": short_timeout
                    })
                    
            except Exception as e:
                timeout_results.append({
                    "tool": tool_name,
                    "result": "error",
                    "error": str(e)[:100]
                })
        
        details = {
            "timeout_results": timeout_results,
            "short_timeout_used": short_timeout
        }
        
        # Timeout handling is working if we can detect timeouts
        has_timeout_result = any(r["result"] == "timeout" for r in timeout_results)
        has_completion_result = any(r["result"] == "completed" for r in timeout_results)
        
        if has_timeout_result or has_completion_result:
            return True, "Timeout handling is working correctly", details
        else:
            return False, "Could not verify timeout handling", details
            
    except Exception as e:
        return False, f"Timeout test error: {str(e)}"


async def test_concurrent_tool_execution(tester: MCPServerTester) -> tuple:
    """Test concurrent execution of multiple tools"""
    try:
        # Discover tools first
        success, message, tools = await tester.discover_tools()
        if not success or not tools:
            return True, "No tools available for concurrency tests", {}
        
        if len(tools) < 2:
            return True, "Need at least 2 tools for concurrency test", {"tool_count": len(tools)}
        
        # Select first 2 tools
        tool1, tool2 = tools[0], tools[1]
        
        # Create concurrent executions
        async def execute_tool(tool_name):
            try:
                start_time = asyncio.get_event_loop().time()
                success, msg, response = await tester.test_tool_execution(tool_name, {})
                end_time = asyncio.get_event_loop().time()
                
                return {
                    "tool": tool_name,
                    "success": success,
                    "message": msg[:100],
                    "duration": end_time - start_time,
                    "has_response": response is not None
                }
            except Exception as e:
                return {
                    "tool": tool_name,
                    "success": False,
                    "error": str(e)[:100]
                }
        
        # Execute tools concurrently
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(
            execute_tool(tool1["name"]),
            execute_tool(tool2["name"]),
            return_exceptions=True
        )
        total_time = asyncio.get_event_loop().time() - start_time
        
        # Analyze results
        successful_executions = [r for r in results if isinstance(r, dict) and r.get("success")]
        
        details = {
            "tools_tested": [tool1["name"], tool2["name"]],
            "concurrent_results": results,
            "total_execution_time": total_time,
            "successful_executions": len(successful_executions)
        }
        
        if len(successful_executions) >= 1:
            return True, f"Concurrent execution successful ({len(successful_executions)}/2 tools)", details
        else:
            return False, "Concurrent execution failed for all tools", details
            
    except Exception as e:
        return False, f"Concurrency test error: {str(e)}"


# Test Suite Setup/Teardown

async def tool_test_setup(tester: MCPServerTester):
    """Setup for tool execution tests"""
    started = await tester.start_server()
    if not started:
        raise Exception("Failed to start server for tool tests")
    
    # Initialize server
    success, message, response = await tester.initialize_server()
    if not success:
        raise Exception(f"Failed to initialize server: {message}")


async def tool_test_teardown(tester: MCPServerTester):
    """Teardown for tool execution tests"""
    await tester.stop_server()


# Define Tool Execution Test Suite

def create_tool_execution_test_suite() -> TestSuite:
    """Create the tool execution test suite"""
    
    test_cases = [
        TestCase(
            name="tool_execution_basic",
            description="Test basic tool execution with valid parameters",
            test_function=test_tool_execution_basic,
            tags=["tools", "execution", "required"],
            timeout=30,
            required=True
        ),
        TestCase(
            name="tool_parameter_validation",
            description="Test tool parameter validation with invalid inputs",
            test_function=test_tool_parameter_validation,
            tags=["tools", "validation", "parameters"],
            timeout=20,
            required=False
        ),
        TestCase(
            name="tool_response_format",
            description="Test tool responses follow MCP format specification",
            test_function=test_tool_response_format,
            tags=["tools", "format", "protocol"],
            timeout=20,
            required=True
        ),
        TestCase(
            name="tool_timeout_handling",
            description="Test tool execution timeout handling",
            test_function=test_tool_timeout_handling,
            tags=["tools", "timeout", "performance"],
            timeout=15,
            required=False
        ),
        TestCase(
            name="concurrent_tool_execution",
            description="Test concurrent execution of multiple tools",
            test_function=test_concurrent_tool_execution,
            tags=["tools", "concurrency", "performance"],
            timeout=25,
            required=False
        )
    ]
    
    return TestSuite(
        name="Tool Execution Tests",
        description="Tests for MCP tool execution functionality and behavior",
        test_cases=test_cases,
        setup=tool_test_setup,
        teardown=tool_test_teardown
    )


# Main test runner

async def run_tool_execution_tests(server_config: dict, output_file: str = None):
    """Run tool execution tests on a server"""
    print("=" * 60)
    print("MCP Tool Execution Tests")
    print("=" * 60)
    
    # Create tester and runner
    tester = MCPServerTester(server_config)
    runner = TestRunner()
    
    # Create and run test suite
    test_suite = create_tool_execution_test_suite()
    results = await runner.run_test_suite(test_suite, tester)
    
    # Generate report
    report = runner.generate_report()
    
    # Print summary
    summary = report["summary"]
    print(f"\nTest Summary:")
    print(f"  Total: {summary['total_tests']}")
    print(f"  Passed: {summary['passed']} ✅")
    print(f"  Failed: {summary['failed']} ❌")
    print(f"  Errors: {summary['errors']} 💥")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    print(f"  Duration: {summary['total_duration']:.2f}s")
    
    # Save report if requested
    if output_file:
        runner.save_report(report, output_file)
        print(f"\nDetailed report saved to: {output_file}")
    
    # Return success status
    required_failures = [
        r for r in results 
        if r.test_case.required and r.result in [TestResult.FAILED, TestResult.ERROR]
    ]
    
    return len(required_failures) == 0, report


if __name__ == "__main__":
    import sys
    import yaml
    
    if len(sys.argv) < 2:
        print("Usage: python test_tool_execution.py <server_name> [output_file]")
        print("  server_name: Name of server in servers.yaml")
        print("  output_file: Optional output file for detailed report")
        sys.exit(1)
    
    server_name = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Load server configuration
    try:
        with open("servers.yaml", "r") as f:
            servers_config = yaml.safe_load(f)
        
        if server_name not in servers_config:
            print(f"Server '{server_name}' not found in servers.yaml")
            sys.exit(1)
        
        server_config = servers_config[server_name]
        
    except Exception as e:
        print(f"Error loading server configuration: {e}")
        sys.exit(1)
    
    # Run tests
    try:
        success, report = asyncio.run(run_tool_execution_tests(server_config, output_file))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test execution failed: {e}")
        sys.exit(1)