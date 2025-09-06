#!/usr/bin/env python3
"""
MCP Protocol Compliance Tests

Tests that validate MCP server compliance with the Model Context Protocol specification.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mcp_test_framework import MCPServerTester, TestRunner, TestCase, TestSuite, TestResult


# Protocol Compliance Test Functions

async def test_server_initialization(tester: MCPServerTester) -> tuple:
    """Test MCP server initialization sequence"""
    try:
        success, message, response = await tester.initialize_server()
        
        if not success:
            return False, f"Initialization failed: {message}"
        
        # Check protocol version
        result = response.get("result", {})
        protocol_version = result.get("protocolVersion")
        
        if not protocol_version:
            return False, "Missing protocolVersion in response"
        
        # Check capabilities
        capabilities = result.get("capabilities", {})
        if not isinstance(capabilities, dict):
            return False, "Capabilities must be a dictionary"
        
        details = {
            "protocol_version": protocol_version,
            "capabilities": capabilities,
            "server_info": result.get("serverInfo", {})
        }
        
        return True, f"Server initialized with protocol {protocol_version}", details
        
    except Exception as e:
        return False, f"Initialization error: {str(e)}"


async def test_tools_discovery(tester: MCPServerTester) -> tuple:
    """Test tools discovery via tools/list"""
    try:
        success, message, tools = await tester.discover_tools()
        
        if not success:
            return False, f"Tools discovery failed: {message}"
        
        # Validate tool structure
        for i, tool in enumerate(tools):
            required_fields = ["name", "description", "inputSchema"]
            for field in required_fields:
                if field not in tool:
                    return False, f"Tool {i} missing required field: {field}"
            
            # Validate inputSchema structure
            schema = tool["inputSchema"]
            if not isinstance(schema, dict):
                return False, f"Tool {i} inputSchema must be a dictionary"
            
            if schema.get("type") != "object":
                return False, f"Tool {i} inputSchema type must be 'object'"
        
        details = {
            "tool_count": len(tools),
            "tools": [{"name": t["name"], "description": t["description"][:100]} for t in tools]
        }
        
        return True, f"Discovered {len(tools)} valid tools", details
        
    except Exception as e:
        return False, f"Tools discovery error: {str(e)}"


async def test_resources_discovery(tester: MCPServerTester) -> tuple:
    """Test resources discovery via resources/list"""
    try:
        success, message, resources = await tester.discover_resources()
        
        if not success:
            # Resources are optional, so not finding any is not a failure
            if "0 resources" in message:
                return True, "No resources available (optional feature)", {"resource_count": 0}
            return False, f"Resources discovery failed: {message}"
        
        # Validate resource structure
        for i, resource in enumerate(resources):
            if "uri" not in resource:
                return False, f"Resource {i} missing required field: uri"
            
            if "name" not in resource:
                return False, f"Resource {i} missing required field: name"
        
        details = {
            "resource_count": len(resources),
            "resources": [{"uri": r["uri"], "name": r["name"]} for r in resources[:5]]  # First 5
        }
        
        return True, f"Discovered {len(resources)} valid resources", details
        
    except Exception as e:
        return False, f"Resources discovery error: {str(e)}"


async def test_prompts_discovery(tester: MCPServerTester) -> tuple:
    """Test prompts discovery via prompts/list"""
    try:
        success, message, prompts = await tester.discover_prompts()
        
        if not success:
            # Prompts are optional, so not finding any is not a failure
            if "0 prompts" in message:
                return True, "No prompts available (optional feature)", {"prompt_count": 0}
            return False, f"Prompts discovery failed: {message}"
        
        # Validate prompt structure
        for i, prompt in enumerate(prompts):
            required_fields = ["name", "description"]
            for field in required_fields:
                if field not in prompt:
                    return False, f"Prompt {i} missing required field: {field}"
        
        details = {
            "prompt_count": len(prompts),
            "prompts": [{"name": p["name"], "description": p["description"][:100]} for p in prompts]
        }
        
        return True, f"Discovered {len(prompts)} valid prompts", details
        
    except Exception as e:
        return False, f"Prompts discovery error: {str(e)}"


async def test_invalid_method_handling(tester: MCPServerTester) -> tuple:
    """Test server handles invalid methods gracefully"""
    try:
        response = await tester.send_request("invalid/method", {})
        
        # Should return an error response
        if "error" not in response:
            return False, "Server should return error for invalid method"
        
        error = response["error"]
        if not isinstance(error, dict):
            return False, "Error must be a dictionary"
        
        if "code" not in error or "message" not in error:
            return False, "Error must have code and message fields"
        
        # Common error codes: -32601 (Method not found), -32600 (Invalid Request)
        error_code = error["code"]
        if error_code not in [-32601, -32600]:
            return False, f"Unexpected error code: {error_code}"
        
        details = {
            "error_code": error_code,
            "error_message": error["message"]
        }
        
        return True, "Server properly handles invalid methods", details
        
    except Exception as e:
        return False, f"Invalid method test error: {str(e)}"


async def test_malformed_json_handling(tester: MCPServerTester) -> tuple:
    """Test server handles malformed JSON gracefully"""
    try:
        # Send malformed JSON
        if tester.process:
            malformed_json = '{"jsonrpc": "2.0", "method": "test", "id": 1,}\n'  # Extra comma
            tester.process.stdin.write(malformed_json)
            tester.process.stdin.flush()
            
            # Try to read response with timeout
            import time
            start_time = time.time()
            response_received = False
            
            while time.time() - start_time < 5:  # 5 second timeout
                if tester.process.stdout.readable():
                    try:
                        response_line = tester.process.stdout.readline()
                        if response_line:
                            import json
                            response = json.loads(response_line.strip())
                            response_received = True
                            break
                    except json.JSONDecodeError:
                        # Server might send error response
                        pass
                await asyncio.sleep(0.1)
            
            # Server should either send error response or continue operating
            # The key is that it shouldn't crash
            if tester.process.poll() is not None:
                return False, "Server crashed on malformed JSON"
            
            details = {
                "server_stable": True,
                "response_received": response_received
            }
            
            return True, "Server handles malformed JSON without crashing", details
    
    except Exception as e:
        return False, f"Malformed JSON test error: {str(e)}"


# Test Suite Setup/Teardown

async def protocol_test_setup(tester: MCPServerTester):
    """Setup for protocol tests"""
    started = await tester.start_server()
    if not started:
        raise Exception("Failed to start server for protocol tests")


async def protocol_test_teardown(tester: MCPServerTester):
    """Teardown for protocol tests"""
    await tester.stop_server()


# Define Protocol Test Suite

def create_protocol_test_suite() -> TestSuite:
    """Create the protocol compliance test suite"""
    
    test_cases = [
        TestCase(
            name="server_initialization",
            description="Test MCP server initialization handshake",
            test_function=test_server_initialization,
            tags=["protocol", "initialization", "required"],
            timeout=15,
            required=True
        ),
        TestCase(
            name="tools_discovery",
            description="Test tools discovery via tools/list",
            test_function=test_tools_discovery,
            tags=["protocol", "tools", "discovery", "required"],
            timeout=10,
            required=True
        ),
        TestCase(
            name="resources_discovery",
            description="Test resources discovery via resources/list",
            test_function=test_resources_discovery,
            tags=["protocol", "resources", "discovery", "optional"],
            timeout=10,
            required=False
        ),
        TestCase(
            name="prompts_discovery",
            description="Test prompts discovery via prompts/list",
            test_function=test_prompts_discovery,
            tags=["protocol", "prompts", "discovery", "optional"],
            timeout=10,
            required=False
        ),
        TestCase(
            name="invalid_method_handling",
            description="Test server handles invalid methods gracefully",
            test_function=test_invalid_method_handling,
            tags=["protocol", "error_handling", "required"],
            timeout=10,
            required=True
        ),
        TestCase(
            name="malformed_json_handling",
            description="Test server handles malformed JSON without crashing",
            test_function=test_malformed_json_handling,
            tags=["protocol", "error_handling", "stability"],
            timeout=10,
            required=False
        )
    ]
    
    return TestSuite(
        name="Protocol Compliance Tests",
        description="Tests for MCP protocol compliance and basic functionality",
        test_cases=test_cases,
        setup=protocol_test_setup,
        teardown=protocol_test_teardown
    )


# Main test runner

async def run_protocol_tests(server_config: dict, output_file: str = None):
    """Run protocol compliance tests on a server"""
    print("=" * 60)
    print("MCP Protocol Compliance Tests")
    print("=" * 60)
    
    # Create tester and runner
    tester = MCPServerTester(server_config)
    runner = TestRunner()
    
    # Create and run test suite
    test_suite = create_protocol_test_suite()
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
        print("Usage: python test_mcp_protocol.py <server_name> [output_file]")
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
        success, report = asyncio.run(run_protocol_tests(server_config, output_file))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test execution failed: {e}")
        sys.exit(1)