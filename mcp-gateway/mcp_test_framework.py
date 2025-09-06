#!/usr/bin/env python3
"""
MCP Test Framework - Automated testing for MCP servers

This framework provides comprehensive testing capabilities for MCP (Model Context Protocol) servers,
including protocol compliance, tool execution, container lifecycle, and gateway integration validation.
"""

import asyncio
import json
import subprocess
import time
import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestResult(Enum):
    """Test result status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestCase:
    """Individual test case"""
    name: str
    description: str
    test_function: callable
    tags: List[str] = None
    timeout: int = 30
    required: bool = True


@dataclass
class TestSuite:
    """Collection of test cases"""
    name: str
    description: str
    test_cases: List[TestCase]
    setup: callable = None
    teardown: callable = None


@dataclass
class TestExecution:
    """Test execution result"""
    test_case: TestCase
    result: TestResult
    message: str = ""
    duration: float = 0.0
    details: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}


class ProtocolValidator:
    """Validates MCP protocol compliance"""
    
    def __init__(self):
        self.protocol_version = "2024-11-05"
        self.required_methods = [
            "initialize",
            "tools/list",
            "tools/call",
            "resources/list",
            "resources/read",
            "prompts/list",
            "prompts/get"
        ]
    
    def validate_json_rpc(self, message: dict) -> Tuple[bool, str]:
        """Validate JSON-RPC 2.0 format"""
        if not isinstance(message, dict):
            return False, "Message must be a dictionary"
        
        if message.get("jsonrpc") != "2.0":
            return False, "Missing or invalid jsonrpc version"
        
        if "id" not in message and "method" not in message:
            return False, "Message must have either id or method"
        
        if "method" in message:
            # Request message
            if not isinstance(message.get("method"), str):
                return False, "Method must be a string"
        else:
            # Response message
            if "result" not in message and "error" not in message:
                return False, "Response must have either result or error"
        
        return True, "Valid JSON-RPC 2.0 message"
    
    def validate_initialize_response(self, response: dict) -> Tuple[bool, str]:
        """Validate initialization response"""
        is_valid, msg = self.validate_json_rpc(response)
        if not is_valid:
            return False, f"JSON-RPC validation failed: {msg}"
        
        if "error" in response:
            return False, f"Initialization error: {response['error']}"
        
        result = response.get("result", {})
        if "protocolVersion" not in result:
            return False, "Missing protocolVersion in response"
        
        if "capabilities" not in result:
            return False, "Missing capabilities in response"
        
        return True, "Valid initialization response"
    
    def validate_tools_list_response(self, response: dict) -> Tuple[bool, str]:
        """Validate tools/list response"""
        is_valid, msg = self.validate_json_rpc(response)
        if not is_valid:
            return False, f"JSON-RPC validation failed: {msg}"
        
        if "error" in response:
            return False, f"Tools list error: {response['error']}"
        
        result = response.get("result", {})
        tools = result.get("tools", [])
        
        if not isinstance(tools, list):
            return False, "Tools must be a list"
        
        for i, tool in enumerate(tools):
            if not isinstance(tool, dict):
                return False, f"Tool {i} must be a dictionary"
            
            if "name" not in tool:
                return False, f"Tool {i} missing name"
            
            if "description" not in tool:
                return False, f"Tool {i} missing description"
            
            if "inputSchema" not in tool:
                return False, f"Tool {i} missing inputSchema"
        
        return True, f"Valid tools list with {len(tools)} tools"
    
    def validate_tool_call_response(self, response: dict) -> Tuple[bool, str]:
        """Validate tools/call response"""
        is_valid, msg = self.validate_json_rpc(response)
        if not is_valid:
            return False, f"JSON-RPC validation failed: {msg}"
        
        if "error" in response:
            # Error responses are valid if properly formatted
            error = response["error"]
            if not isinstance(error, dict):
                return False, "Error must be a dictionary"
            
            if "code" not in error or "message" not in error:
                return False, "Error must have code and message"
            
            return True, f"Valid error response: {error['message']}"
        
        result = response.get("result", {})
        if "content" not in result:
            return False, "Tool call result missing content"
        
        content = result["content"]
        if not isinstance(content, list):
            return False, "Content must be a list"
        
        for i, item in enumerate(content):
            if not isinstance(item, dict):
                return False, f"Content item {i} must be a dictionary"
            
            if "type" not in item:
                return False, f"Content item {i} missing type"
            
            if item["type"] not in ["text", "image", "resource"]:
                return False, f"Content item {i} has invalid type: {item['type']}"
        
        return True, "Valid tool call response"


class MCPServerTester:
    """Main MCP server testing framework"""
    
    def __init__(self, server_config: dict, working_dir: str = None):
        self.server_config = server_config
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.process = None
        self.validator = ProtocolValidator()
        self.request_counter = 0
        self.test_results = []
        self.server_capabilities = {}
        self.available_tools = []
        self.available_resources = []
        self.available_prompts = []
    
    async def start_server(self) -> bool:
        """Start the MCP server process"""
        try:
            image = self.server_config.get("image")
            command = self.server_config.get("command", [])
            env_vars = self.server_config.get("environment", {})
            
            docker_cmd = ["docker", "run", "-i", "--rm"]
            
            # Add environment variables
            for key, value in env_vars.items():
                docker_cmd.extend(["-e", f"{key}={value}"])
            
            docker_cmd.append(image)
            docker_cmd.extend(command)
            
            logger.info(f"Starting server: {' '.join(docker_cmd)}")
            
            self.process = subprocess.Popen(
                docker_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait a moment for the server to start
            await asyncio.sleep(2)
            
            # Check if process is still running
            if self.process.poll() is not None:
                stderr = self.process.stderr.read()
                raise Exception(f"Server failed to start: {stderr}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    async def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
    
    async def send_request(self, method: str, params: dict = None, timeout: int = 10) -> dict:
        """Send JSON-RPC request to server"""
        if not self.process:
            raise Exception("Server not started")
        
        self.request_counter += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_counter
        }
        
        # Send request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        # Read response with timeout
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.process.stdout.readable():
                    response_line = self.process.stdout.readline()
                    if response_line:
                        response = json.loads(response_line.strip())
                        return response
                await asyncio.sleep(0.1)
            
            raise TimeoutError(f"No response within {timeout} seconds")
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
    
    async def initialize_server(self) -> Tuple[bool, str, dict]:
        """Initialize the MCP server"""
        try:
            init_params = {
                "protocolVersion": self.validator.protocol_version,
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-test-framework",
                    "version": "1.0.0"
                }
            }
            
            response = await self.send_request("initialize", init_params)
            is_valid, msg = self.validator.validate_initialize_response(response)
            
            if is_valid:
                self.server_capabilities = response.get("result", {}).get("capabilities", {})
                
                # Send initialized notification
                await self.send_notification("notifications/initialized")
            
            return is_valid, msg, response
            
        except Exception as e:
            return False, f"Initialization failed: {e}", {}
    
    async def send_notification(self, method: str, params: dict = None):
        """Send JSON-RPC notification (no response expected)"""
        if not self.process:
            raise Exception("Server not started")
        
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        notification_str = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_str)
        self.process.stdin.flush()
    
    async def discover_tools(self) -> Tuple[bool, str, List[dict]]:
        """Discover available tools"""
        try:
            response = await self.send_request("tools/list")
            is_valid, msg = self.validator.validate_tools_list_response(response)
            
            if is_valid:
                tools = response.get("result", {}).get("tools", [])
                self.available_tools = tools
                return True, f"Discovered {len(tools)} tools", tools
            
            return False, msg, []
            
        except Exception as e:
            return False, f"Tool discovery failed: {e}", []
    
    async def test_tool_execution(self, tool_name: str, arguments: dict = None) -> Tuple[bool, str, dict]:
        """Test tool execution"""
        try:
            params = {
                "name": tool_name,
                "arguments": arguments or {}
            }
            
            response = await self.send_request("tools/call", params)
            is_valid, msg = self.validator.validate_tool_call_response(response)
            
            return is_valid, msg, response
            
        except Exception as e:
            return False, f"Tool execution failed: {e}", {}
    
    async def discover_resources(self) -> Tuple[bool, str, List[dict]]:
        """Discover available resources"""
        try:
            response = await self.send_request("resources/list")
            
            if "error" in response:
                return False, f"Resource discovery error: {response['error']}", []
            
            resources = response.get("result", {}).get("resources", [])
            self.available_resources = resources
            return True, f"Discovered {len(resources)} resources", resources
            
        except Exception as e:
            return False, f"Resource discovery failed: {e}", []
    
    async def discover_prompts(self) -> Tuple[bool, str, List[dict]]:
        """Discover available prompts"""
        try:
            response = await self.send_request("prompts/list")
            
            if "error" in response:
                return False, f"Prompt discovery error: {response['error']}", []
            
            prompts = response.get("result", {}).get("prompts", [])
            self.available_prompts = prompts
            return True, f"Discovered {len(prompts)} prompts", prompts
            
        except Exception as e:
            return False, f"Prompt discovery failed: {e}", []


class TestRunner:
    """Runs test suites and manages results"""
    
    def __init__(self, working_dir: str = None):
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    async def run_test_suite(self, test_suite: TestSuite, tester: MCPServerTester) -> List[TestExecution]:
        """Run a complete test suite"""
        logger.info(f"Running test suite: {test_suite.name}")
        suite_results = []
        
        # Setup
        if test_suite.setup:
            try:
                await test_suite.setup(tester)
            except Exception as e:
                logger.error(f"Setup failed: {e}")
                return suite_results
        
        # Run test cases
        for test_case in test_suite.test_cases:
            result = await self.run_test_case(test_case, tester)
            suite_results.append(result)
            self.test_results.append(result)
        
        # Teardown
        if test_suite.teardown:
            try:
                await test_suite.teardown(tester)
            except Exception as e:
                logger.error(f"Teardown failed: {e}")
        
        return suite_results
    
    async def run_test_case(self, test_case: TestCase, tester: MCPServerTester) -> TestExecution:
        """Run a single test case"""
        logger.info(f"Running test: {test_case.name}")
        start_time = time.time()
        
        try:
            # Run test with timeout
            result = await asyncio.wait_for(
                test_case.test_function(tester),
                timeout=test_case.timeout
            )
            
            if result is True:
                execution = TestExecution(
                    test_case=test_case,
                    result=TestResult.PASSED,
                    message="Test passed",
                    duration=time.time() - start_time
                )
            elif result is False:
                execution = TestExecution(
                    test_case=test_case,
                    result=TestResult.FAILED,
                    message="Test failed",
                    duration=time.time() - start_time
                )
            elif isinstance(result, tuple):
                # (success, message, details)
                success, message = result[:2]
                details = result[2] if len(result) > 2 else {}
                
                execution = TestExecution(
                    test_case=test_case,
                    result=TestResult.PASSED if success else TestResult.FAILED,
                    message=message,
                    duration=time.time() - start_time,
                    details=details
                )
            else:
                execution = TestExecution(
                    test_case=test_case,
                    result=TestResult.ERROR,
                    message=f"Invalid test result type: {type(result)}",
                    duration=time.time() - start_time
                )
                
        except asyncio.TimeoutError:
            execution = TestExecution(
                test_case=test_case,
                result=TestResult.ERROR,
                message=f"Test timed out after {test_case.timeout} seconds",
                duration=time.time() - start_time
            )
        except Exception as e:
            execution = TestExecution(
                test_case=test_case,
                result=TestResult.ERROR,
                message=f"Test error: {str(e)}",
                duration=time.time() - start_time
            )
        
        # Log result
        status_emoji = {
            TestResult.PASSED: "✅",
            TestResult.FAILED: "❌",
            TestResult.ERROR: "💥",
            TestResult.SKIPPED: "⏭️"
        }
        
        logger.info(f"{status_emoji[execution.result]} {test_case.name}: {execution.message}")
        
        return execution
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        if not self.test_results:
            return {"error": "No test results available"}
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r.result == TestResult.PASSED])
        failed = len([r for r in self.test_results if r.result == TestResult.FAILED])
        errors = len([r for r in self.test_results if r.result == TestResult.ERROR])
        skipped = len([r for r in self.test_results if r.result == TestResult.SKIPPED])
        
        total_duration = sum(r.duration for r in self.test_results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration
            },
            "test_results": []
        }
        
        for execution in self.test_results:
            test_result = {
                "name": execution.test_case.name,
                "description": execution.test_case.description,
                "result": execution.result.value,
                "message": execution.message,
                "duration": execution.duration,
                "timestamp": execution.timestamp.isoformat(),
                "tags": execution.test_case.tags or [],
                "required": execution.test_case.required
            }
            
            if execution.details:
                test_result["details"] = execution.details
            
            report["test_results"].append(test_result)
        
        return report
    
    def save_report(self, report: Dict[str, Any], file_path: str):
        """Save test report to file"""
        output_path = Path(file_path)
        
        if output_path.suffix.lower() == '.json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif output_path.suffix.lower() == '.yaml':
            with open(output_path, 'w') as f:
                yaml.dump(report, f, default_flow_style=False)
        else:
            # Text format
            with open(output_path, 'w') as f:
                self._write_text_report(report, f)
        
        logger.info(f"Test report saved to: {output_path}")
    
    def _write_text_report(self, report: Dict[str, Any], file):
        """Write text format report"""
        summary = report["summary"]
        
        file.write("MCP Server Test Report\n")
        file.write("=" * 50 + "\n\n")
        
        file.write("Summary:\n")
        file.write(f"  Total Tests: {summary['total_tests']}\n")
        file.write(f"  Passed: {summary['passed']}\n")
        file.write(f"  Failed: {summary['failed']}\n")
        file.write(f"  Errors: {summary['errors']}\n")
        file.write(f"  Skipped: {summary['skipped']}\n")
        file.write(f"  Success Rate: {summary['success_rate']:.1f}%\n")
        file.write(f"  Total Duration: {summary['total_duration']:.2f}s\n\n")
        
        file.write("Test Results:\n")
        file.write("-" * 30 + "\n")
        
        for result in report["test_results"]:
            status = {"passed": "✅", "failed": "❌", "error": "💥", "skipped": "⏭️"}
            file.write(f"{status[result['result']]} {result['name']}\n")
            file.write(f"   {result['message']}\n")
            file.write(f"   Duration: {result['duration']:.2f}s\n")
            if result.get('details'):
                file.write(f"   Details: {result['details']}\n")
            file.write("\n")


# Export main classes
__all__ = [
    'MCPServerTester',
    'ProtocolValidator', 
    'TestRunner',
    'TestCase',
    'TestSuite',
    'TestExecution',
    'TestResult'
]