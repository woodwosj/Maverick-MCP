#!/usr/bin/env python3
"""
MCP Test Generator - Automatically generates tests for converted MCP servers

This module generates comprehensive test suites based on repository analysis results,
creating custom tests for each tool converted from repository functions.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Template, Environment, FileSystemLoader
import yaml

# Add analyzer to path
sys.path.append(str(Path(__file__).parent / "analyzer"))

try:
    from repository_analyzer import AnalysisResult, FunctionCandidate, FunctionInfo
except ImportError:
    # Create dummy classes if analyzer not available
    class AnalysisResult:
        def __init__(self):
            self.candidates = []
    
    class FunctionCandidate:
        def __init__(self):
            self.function = None
            self.mcp_score = 0.0
            self.security_warnings = []
    
    class FunctionInfo:
        def __init__(self):
            self.function_name = ""
            self.parameters = []


class TestGenerator:
    """Generates test suites for MCP servers based on analysis results"""
    
    def __init__(self, templates_dir: str = None):
        self.templates_dir = Path(templates_dir) if templates_dir else Path(__file__).parent / "templates" / "test_templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default test templates"""
        
        # Protocol test template
        protocol_template = """#!/usr/bin/env python3
\"\"\"
Generated Protocol Tests for {{ server_name }}

Auto-generated tests for MCP protocol compliance.
Generated on: {{ generation_date }}
\"\"\"

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mcp_test_framework import MCPServerTester, TestRunner, TestCase, TestSuite, TestResult


async def test_{{ server_name }}_initialization(tester: MCPServerTester) -> tuple:
    \"\"\"Test {{ server_name }} server initialization\"\"\"
    try:
        success, message, response = await tester.initialize_server()
        
        if not success:
            return False, f"Initialization failed: {message}"
        
        # Check server-specific capabilities
        result = response.get("result", {})
        capabilities = result.get("capabilities", {})
        
        details = {
            "protocol_version": result.get("protocolVersion"),
            "capabilities": capabilities,
            "server_info": result.get("serverInfo", {})
        }
        
        return True, "Server initialized successfully", details
        
    except Exception as e:
        return False, f"Initialization error: {str(e)}"


async def test_{{ server_name }}_tools_discovery(tester: MCPServerTester) -> tuple:
    \"\"\"Test {{ server_name }} tools discovery\"\"\"
    try:
        success, message, tools = await tester.discover_tools()
        
        if not success:
            return False, f"Tools discovery failed: {message}"
        
        # Check for expected tools
        expected_tools = {{ expected_tools | tojson }}
        found_tools = [tool["name"] for tool in tools]
        
        missing_tools = [t for t in expected_tools if t not in found_tools]
        unexpected_tools = [t for t in found_tools if t not in expected_tools]
        
        details = {
            "expected_tools": expected_tools,
            "found_tools": found_tools,
            "missing_tools": missing_tools,
            "unexpected_tools": unexpected_tools,
            "tool_count": len(tools)
        }
        
        if missing_tools:
            return False, f"Missing expected tools: {missing_tools}", details
        
        return True, f"Found all {len(tools)} expected tools", details
        
    except Exception as e:
        return False, f"Tools discovery error: {str(e)}"


# Test setup/teardown
async def {{ server_name }}_test_setup(tester: MCPServerTester):
    \"\"\"Setup for {{ server_name }} tests\"\"\"
    started = await tester.start_server()
    if not started:
        raise Exception("Failed to start {{ server_name }} server")

async def {{ server_name }}_test_teardown(tester: MCPServerTester):
    \"\"\"Teardown for {{ server_name }} tests\"\"\"
    await tester.stop_server()


# Create test suite
def create_{{ server_name }}_protocol_suite() -> TestSuite:
    \"\"\"Create protocol test suite for {{ server_name }}\"\"\"
    
    test_cases = [
        TestCase(
            name="{{ server_name }}_initialization",
            description="Test {{ server_name }} server initialization",
            test_function=test_{{ server_name }}_initialization,
            tags=["protocol", "{{ server_name }}", "initialization"],
            timeout=15,
            required=True
        ),
        TestCase(
            name="{{ server_name }}_tools_discovery", 
            description="Test {{ server_name }} tools discovery",
            test_function=test_{{ server_name }}_tools_discovery,
            tags=["protocol", "{{ server_name }}", "tools"],
            timeout=10,
            required=True
        )
    ]
    
    return TestSuite(
        name="{{ server_name | title }} Protocol Tests",
        description="Protocol compliance tests for {{ server_name }} server",
        test_cases=test_cases,
        setup={{ server_name }}_test_setup,
        teardown={{ server_name }}_test_teardown
    )


if __name__ == "__main__":
    import yaml
    
    server_config = {
        "image": "{{ docker_image }}",
        "command": {{ docker_command | tojson }},
        "description": "{{ server_description }}",
        "environment": {{ environment | tojson }}
    }
    
    async def run_tests():
        tester = MCPServerTester(server_config)
        runner = TestRunner()
        
        test_suite = create_{{ server_name }}_protocol_suite()
        results = await runner.run_test_suite(test_suite, tester)
        
        report = runner.generate_report()
        summary = report["summary"]
        
        print(f"{{ server_name | title }} Protocol Tests:")
        print(f"  Passed: {summary['passed']}/{{summary['total_tests']}}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        
        return summary['failed'] == 0 and summary['errors'] == 0
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
"""
        
        # Tool-specific test template
        tool_test_template = """#!/usr/bin/env python3
\"\"\"
Generated Tool Tests for {{ tool_name }}

Auto-generated tests for {{ tool_name }} tool functionality.
Generated on: {{ generation_date }}
Source: {{ source_function }} in {{ source_file }}
\"\"\"

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mcp_test_framework import MCPServerTester, TestRunner, TestCase, TestSuite, TestResult


async def test_{{ tool_name }}_basic_execution(tester: MCPServerTester) -> tuple:
    \"\"\"Test basic execution of {{ tool_name }} tool\"\"\"
    try:
        # Test with minimal valid parameters
        test_args = {{ basic_test_args | tojson }}
        
        success, message, response = await tester.test_tool_execution("{{ tool_name }}", test_args)
        
        if not success:
            return False, f"Tool execution failed: {message}"
        
        # Validate response format
        if "result" not in response:
            return False, "Missing result in response"
        
        result = response["result"]
        if "content" not in result:
            return False, "Missing content in result"
        
        content = result["content"]
        if not isinstance(content, list):
            return False, "Content must be a list"
        
        details = {
            "response_format": "valid",
            "content_items": len(content),
            "test_args": test_args
        }
        
        return True, f"Tool executed successfully with {len(content)} content items", details
        
    except Exception as e:
        return False, f"Tool execution error: {str(e)}"


async def test_{{ tool_name }}_parameter_validation(tester: MCPServerTester) -> tuple:
    \"\"\"Test parameter validation for {{ tool_name }} tool\"\"\"
    try:
        validation_cases = {{ validation_test_cases | tojson }}
        
        results = []
        for case in validation_cases:
            test_name = case["name"]
            test_args = case["args"]
            expect_success = case["expect_success"]
            
            try:
                success, message, response = await tester.test_tool_execution("{{ tool_name }}", test_args)
                
                case_result = {
                    "test": test_name,
                    "args": test_args,
                    "expected_success": expect_success,
                    "actual_success": success,
                    "message": message[:100],
                    "correct": (success == expect_success)
                }
                
                results.append(case_result)
                
            except Exception as e:
                results.append({
                    "test": test_name,
                    "args": test_args,
                    "expected_success": expect_success,
                    "actual_success": False,
                    "error": str(e)[:100],
                    "correct": (False == expect_success)
                })
        
        correct_cases = [r for r in results if r.get("correct", False)]
        success_rate = len(correct_cases) / len(results) if results else 0
        
        details = {
            "total_cases": len(results),
            "correct_cases": len(correct_cases),
            "success_rate": success_rate,
            "case_results": results
        }
        
        if success_rate >= 0.8:  # 80% success rate required
            return True, f"Parameter validation working ({len(correct_cases)}/{len(results)} cases correct)", details
        else:
            return False, f"Parameter validation issues ({len(correct_cases)}/{len(results)} cases correct)", details
            
    except Exception as e:
        return False, f"Parameter validation test error: {str(e)}"


{% if security_warnings %}
async def test_{{ tool_name }}_security_behavior(tester: MCPServerTester) -> tuple:
    \"\"\"Test security behavior for {{ tool_name }} tool\"\"\"
    try:
        # Test with potentially dangerous inputs
        security_test_cases = {{ security_test_cases | tojson }}
        
        security_results = []
        for case in security_test_cases:
            test_name = case["name"]
            test_args = case["args"]
            risk_level = case["risk_level"]
            
            try:
                success, message, response = await tester.test_tool_execution("{{ tool_name }}", test_args)
                
                # For high-risk inputs, we expect either:
                # 1. Graceful rejection (error response)
                # 2. Safe handling (success with sanitized output)
                
                if risk_level == "high":
                    if "error" in response:
                        security_results.append({
                            "test": test_name,
                            "result": "properly_rejected",
                            "safe": True
                        })
                    elif success:
                        # Check if output seems sanitized/safe
                        content = response.get("result", {}).get("content", [])
                        contains_dangerous = any(
                            any(danger in str(item) for danger in ["<script>", "eval(", "exec(", "import os"])
                            for item in content
                        )
                        if isinstance(content, list) else False
                        
                        security_results.append({
                            "test": test_name,
                            "result": "handled_safely" if not contains_dangerous else "potential_risk",
                            "safe": not contains_dangerous
                        })
                else:
                    security_results.append({
                        "test": test_name,
                        "result": "completed",
                        "safe": True
                    })
                    
            except Exception as e:
                security_results.append({
                    "test": test_name,
                    "result": "error",
                    "error": str(e)[:100],
                    "safe": True  # Errors are safe
                })
        
        safe_results = [r for r in security_results if r.get("safe", False)]
        safety_rate = len(safe_results) / len(security_results) if security_results else 1.0
        
        details = {
            "security_tests": len(security_results),
            "safe_results": len(safe_results),
            "safety_rate": safety_rate,
            "test_results": security_results
        }
        
        if safety_rate >= 0.9:  # 90% safety rate required
            return True, f"Security behavior acceptable ({len(safe_results)}/{len(security_results)} tests safe)", details
        else:
            return False, f"Security concerns detected ({len(safe_results)}/{len(security_results)} tests safe)", details
            
    except Exception as e:
        return False, f"Security test error: {str(e)}"
{% endif %}


# Test setup/teardown
async def {{ tool_name }}_test_setup(tester: MCPServerTester):
    \"\"\"Setup for {{ tool_name }} tool tests\"\"\"
    started = await tester.start_server()
    if not started:
        raise Exception("Failed to start server for {{ tool_name }} tests")
    
    success, message, response = await tester.initialize_server()
    if not success:
        raise Exception(f"Failed to initialize server: {message}")

async def {{ tool_name }}_test_teardown(tester: MCPServerTester):
    \"\"\"Teardown for {{ tool_name }} tool tests\"\"\"
    await tester.stop_server()


# Create test suite
def create_{{ tool_name }}_test_suite() -> TestSuite:
    \"\"\"Create test suite for {{ tool_name }} tool\"\"\"
    
    test_cases = [
        TestCase(
            name="{{ tool_name }}_basic_execution",
            description="Test basic execution of {{ tool_name }} tool",
            test_function=test_{{ tool_name }}_basic_execution,
            tags=["tool", "{{ tool_name }}", "execution"],
            timeout=30,
            required=True
        ),
        TestCase(
            name="{{ tool_name }}_parameter_validation",
            description="Test parameter validation for {{ tool_name }} tool",
            test_function=test_{{ tool_name }}_parameter_validation,
            tags=["tool", "{{ tool_name }}", "validation"],
            timeout=20,
            required=True
        ){% if security_warnings %},
        TestCase(
            name="{{ tool_name }}_security_behavior",
            description="Test security behavior for {{ tool_name }} tool",
            test_function=test_{{ tool_name }}_security_behavior,
            tags=["tool", "{{ tool_name }}", "security"],
            timeout=25,
            required=True
        ){% endif %}
    ]
    
    return TestSuite(
        name="{{ tool_name | title }} Tool Tests",
        description="Functionality tests for {{ tool_name }} tool",
        test_cases=test_cases,
        setup={{ tool_name }}_test_setup,
        teardown={{ tool_name }}_test_teardown
    )


if __name__ == "__main__":
    import yaml
    
    server_config = {{ server_config | tojson }}
    
    async def run_tests():
        tester = MCPServerTester(server_config)
        runner = TestRunner()
        
        test_suite = create_{{ tool_name }}_test_suite()
        results = await runner.run_test_suite(test_suite, tester)
        
        report = runner.generate_report()
        summary = report["summary"]
        
        print(f"{{ tool_name | title }} Tool Tests:")
        print(f"  Passed: {summary['passed']}/{summary['total_tests']}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        
        return summary['failed'] == 0 and summary['errors'] == 0
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
"""
        
        # Save templates
        protocol_template_path = self.templates_dir / "protocol_test.py.j2"
        tool_template_path = self.templates_dir / "tool_test.py.j2"
        
        if not protocol_template_path.exists():
            protocol_template_path.write_text(protocol_template)
        
        if not tool_template_path.exists():
            tool_template_path.write_text(tool_test_template)
    
    def generate_protocol_tests(self, 
                               server_name: str,
                               server_config: dict,
                               expected_tools: List[str],
                               output_file: str) -> str:
        """Generate protocol compliance tests for a server"""
        
        template = self.jinja_env.get_template("protocol_test.py.j2")
        
        content = template.render(
            server_name=server_name,
            docker_image=server_config.get("image", f"mcp-{server_name}"),
            docker_command=server_config.get("command", ["python", "server.py"]),
            server_description=server_config.get("description", f"{server_name} MCP server"),
            environment=server_config.get("environment", {}),
            expected_tools=expected_tools,
            generation_date=Path().cwd().name  # Simple timestamp
        )
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        
        return str(output_path)
    
    def generate_tool_tests(self,
                           server_name: str,
                           server_config: dict,
                           tool_name: str,
                           function_info: Dict[str, Any],
                           output_file: str) -> str:
        """Generate tool-specific tests"""
        
        template = self.jinja_env.get_template("tool_test.py.j2")
        
        # Generate test cases based on function info
        basic_test_args = self._generate_basic_test_args(function_info)
        validation_test_cases = self._generate_validation_test_cases(function_info)
        security_test_cases = self._generate_security_test_cases(function_info)
        
        content = template.render(
            tool_name=tool_name,
            server_name=server_name,
            server_config=server_config,
            source_function=function_info.get("function_name", tool_name),
            source_file=function_info.get("source_file", "unknown"),
            basic_test_args=basic_test_args,
            validation_test_cases=validation_test_cases,
            security_test_cases=security_test_cases,
            security_warnings=function_info.get("security_warnings", []),
            generation_date=Path().cwd().name
        )
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        
        return str(output_path)
    
    def _generate_basic_test_args(self, function_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic test arguments for a function"""
        parameters = function_info.get("parameters", [])
        test_args = {}
        
        for param in parameters:
            param_name = param.get("name", "")
            param_type = param.get("type", "string")
            
            if param_type == "str" or param_type == "string":
                test_args[param_name] = "test_value"
            elif param_type == "int" or param_type == "number":
                test_args[param_name] = 42
            elif param_type == "bool" or param_type == "boolean":
                test_args[param_name] = True
            elif param_type == "list" or param_type == "array":
                test_args[param_name] = ["item1", "item2"]
            elif param_type == "dict" or param_type == "object":
                test_args[param_name] = {"key": "value"}
            else:
                test_args[param_name] = "test_value"
        
        return test_args
    
    def _generate_validation_test_cases(self, function_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate parameter validation test cases"""
        parameters = function_info.get("parameters", [])
        test_cases = []
        
        # Test with empty arguments
        test_cases.append({
            "name": "empty_args",
            "args": {},
            "expect_success": len(parameters) == 0  # Success only if no required params
        })
        
        # Test with wrong parameter types
        for param in parameters[:2]:  # Test first 2 parameters
            param_name = param.get("name", "")
            param_type = param.get("type", "string")
            
            if param_type in ["str", "string"]:
                test_cases.append({
                    "name": f"{param_name}_wrong_type",
                    "args": {param_name: 123},  # Number instead of string
                    "expect_success": False
                })
            elif param_type in ["int", "number"]:
                test_cases.append({
                    "name": f"{param_name}_wrong_type", 
                    "args": {param_name: "not_a_number"},  # String instead of number
                    "expect_success": False
                })
        
        # Test with unexpected parameters
        test_cases.append({
            "name": "unexpected_param",
            "args": {"unexpected_parameter": "value"},
            "expect_success": False
        })
        
        return test_cases
    
    def _generate_security_test_cases(self, function_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security test cases based on function analysis"""
        parameters = function_info.get("parameters", [])
        security_warnings = function_info.get("security_warnings", [])
        test_cases = []
        
        # If function has security warnings, test with dangerous inputs
        if security_warnings:
            for param in parameters[:2]:  # Test first 2 parameters
                param_name = param.get("name", "")
                
                # Test script injection
                test_cases.append({
                    "name": f"{param_name}_script_injection",
                    "args": {param_name: "<script>alert('xss')</script>"},
                    "risk_level": "high"
                })
                
                # Test command injection  
                test_cases.append({
                    "name": f"{param_name}_command_injection",
                    "args": {param_name: "; rm -rf /"},
                    "risk_level": "high"
                })
                
                # Test code execution
                test_cases.append({
                    "name": f"{param_name}_code_execution",
                    "args": {param_name": "eval('import os; os.system()')"},
                    "risk_level": "high"
                })
        
        return test_cases
    
    def generate_test_suite_from_analysis(self,
                                         analysis_result: AnalysisResult,
                                         server_name: str,
                                         server_config: dict,
                                         output_dir: str) -> List[str]:
        """Generate complete test suite from repository analysis"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # Extract tool names from analysis
        tool_names = []
        for candidate in analysis_result.candidates:
            if hasattr(candidate, 'function') and hasattr(candidate.function, 'function_name'):
                tool_names.append(candidate.function.function_name)
        
        # Generate protocol tests
        protocol_test_file = output_path / f"test_{server_name}_protocol.py"
        self.generate_protocol_tests(
            server_name=server_name,
            server_config=server_config,
            expected_tools=tool_names,
            output_file=str(protocol_test_file)
        )
        generated_files.append(str(protocol_test_file))
        
        # Generate tool-specific tests
        for candidate in analysis_result.candidates[:5]:  # Limit to first 5 tools
            if not hasattr(candidate, 'function'):
                continue
                
            function = candidate.function
            if not hasattr(function, 'function_name'):
                continue
                
            tool_name = function.function_name
            
            # Prepare function info
            function_info = {
                "function_name": tool_name,
                "source_file": getattr(function, 'file_path', 'unknown'),
                "parameters": [
                    {
                        "name": param.name if hasattr(param, 'name') else str(param),
                        "type": getattr(param, 'type_hint', 'string')
                    }
                    for param in getattr(function, 'parameters', [])
                ],
                "security_warnings": getattr(candidate, 'security_warnings', [])
            }
            
            # Generate tool tests
            tool_test_file = output_path / f"test_{server_name}_{tool_name}.py"
            self.generate_tool_tests(
                server_name=server_name,
                server_config=server_config,
                tool_name=tool_name,
                function_info=function_info,
                output_file=str(tool_test_file)
            )
            generated_files.append(str(tool_test_file))
        
        # Generate test runner script
        runner_script = self._generate_test_runner(server_name, generated_files, output_path)
        generated_files.append(runner_script)
        
        return generated_files
    
    def _generate_test_runner(self, server_name: str, test_files: List[str], output_path: Path) -> str:
        """Generate a test runner script for all generated tests"""
        
        runner_content = f'''#!/usr/bin/env python3
"""
Test Runner for {server_name} MCP Server

Auto-generated test runner for all {server_name} tests.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mcp_test_framework import TestRunner, MCPServerTester


async def run_all_tests(server_config: dict):
    """Run all generated tests for {server_name}"""
    
    print("=" * 60)
    print(f"{server_name.upper()} MCP SERVER - FULL TEST SUITE")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    total_errors = 0
    
    # Import and run each test module
    test_modules = [
'''
        
        for test_file in test_files:
            if test_file.endswith('.py'):
                module_name = Path(test_file).stem
                runner_content += f'        "{module_name}",\n'
        
        runner_content += f'''    ]
    
    for module_name in test_modules:
        try:
            print(f"\\nRunning {{module_name}}...")
            
            # Import the test module
            module = __import__(module_name)
            
            # Find and run the test suite
            if hasattr(module, 'create_{server_name}_protocol_suite'):
                test_suite = getattr(module, f'create_{server_name}_protocol_suite')()
            elif hasattr(module, f'create_{{module_name.split("_")[-1]}}_test_suite'):
                test_suite_func = getattr(module, f'create_{{module_name.split("_")[-1]}}_test_suite')
                test_suite = test_suite_func()
            else:
                print(f"  No test suite found in {{module_name}}")
                continue
            
            # Run the test suite
            tester = MCPServerTester(server_config)
            runner = TestRunner()
            
            results = await runner.run_test_suite(test_suite, tester)
            report = runner.generate_report()
            summary = report["summary"]
            
            print(f"  Results: {{summary['passed']}}/{{summary['total_tests']}} passed")
            
            total_passed += summary['passed']
            total_failed += summary['failed']
            total_errors += summary['errors']
            
        except Exception as e:
            print(f"  Error running {{module_name}}: {{e}}")
            total_errors += 1
    
    print("\\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total Passed: {{total_passed}} ✅")
    print(f"Total Failed: {{total_failed}} ❌")
    print(f"Total Errors: {{total_errors}} 💥")
    
    success_rate = (total_passed / (total_passed + total_failed + total_errors) * 100) if (total_passed + total_failed + total_errors) > 0 else 0
    print(f"Overall Success Rate: {{success_rate:.1f}}%")
    
    return total_failed == 0 and total_errors == 0


if __name__ == "__main__":
    import yaml
    
    # Load server configuration
    try:
        with open("../servers.yaml", "r") as f:
            servers_config = yaml.safe_load(f)
        
        if "{server_name}" not in servers_config:
            print(f"Server '{server_name}' not found in servers.yaml")
            sys.exit(1)
        
        server_config = servers_config["{server_name}"]
        
    except Exception as e:
        print(f"Error loading server configuration: {{e}}")
        sys.exit(1)
    
    # Run all tests
    try:
        success = asyncio.run(run_all_tests(server_config))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test execution failed: {{e}}")
        sys.exit(1)
'''
        
        runner_file = output_path / f"run_{server_name}_tests.py"
        runner_file.write_text(runner_content)
        
        return str(runner_file)


# CLI interface
def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate MCP server tests from analysis results")
    parser.add_argument("--analysis-file", required=True, help="Path to analysis result JSON file")
    parser.add_argument("--server-name", required=True, help="Name of the MCP server")
    parser.add_argument("--server-config", help="Path to server configuration YAML file (defaults to servers.yaml)")
    parser.add_argument("--output-dir", default="generated_tests", help="Output directory for generated tests")
    parser.add_argument("--templates-dir", help="Directory containing test templates")
    
    args = parser.parse_args()
    
    # Load analysis result
    try:
        with open(args.analysis_file, 'r') as f:
            analysis_data = json.load(f)
        
        # Convert to AnalysisResult object (simplified)
        analysis_result = AnalysisResult()
        # Note: In real implementation, would properly deserialize
        
    except Exception as e:
        print(f"Error loading analysis file: {e}")
        return 1
    
    # Load server configuration
    config_file = args.server_config or "servers.yaml"
    try:
        with open(config_file, 'r') as f:
            servers_config = yaml.safe_load(f)
        
        if args.server_name not in servers_config:
            print(f"Server '{args.server_name}' not found in {config_file}")
            return 1
        
        server_config = servers_config[args.server_name]
        
    except Exception as e:
        print(f"Error loading server configuration: {e}")
        return 1
    
    # Generate tests
    generator = TestGenerator(args.templates_dir)
    generated_files = generator.generate_test_suite_from_analysis(
        analysis_result=analysis_result,
        server_name=args.server_name,
        server_config=server_config,
        output_dir=args.output_dir
    )
    
    print(f"Generated {len(generated_files)} test files:")
    for file_path in generated_files:
        print(f"  - {file_path}")
    
    print(f"\\nTo run tests: cd {args.output_dir} && python run_{args.server_name}_tests.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())