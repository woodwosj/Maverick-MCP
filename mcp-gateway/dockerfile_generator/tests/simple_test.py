#!/usr/bin/env python3
"""
Simple test for Dockerfile Generator without external dependencies
"""

import sys
import tempfile
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from analyzer.models import MCPToolCandidate, FunctionCandidate, FunctionParameter


def test_basic_functionality():
    """Test basic functionality without Jinja2"""
    print("Testing basic Dockerfile Generator functionality...")
    
    # Test dependency resolver
    from dockerfile_generator.dependency_resolver import DependencyResolver
    resolver = DependencyResolver()
    
    # Test Python standard library detection
    assert "os" in resolver.PYTHON_STDLIB
    assert "requests" not in resolver.PYTHON_STDLIB
    print("✅ Dependency resolver stdlib detection works")
    
    # Test import extraction
    test_code = """import os
import requests
from pathlib import Path"""
    
    imports = resolver._extract_python_imports(test_code)
    expected = {"os", "requests", "pathlib"}
    assert imports == expected, f"Expected {expected}, got {imports}"
    print("✅ Python import extraction works")
    
    # Test server wrapper generator (basic)
    from dockerfile_generator.server_wrapper_generator import ServerWrapperGenerator
    wrapper_gen = ServerWrapperGenerator()
    
    # Create sample function
    func_param = FunctionParameter(
        name="message",
        type_hint="str", 
        description="Test message",
        required=True
    )
    
    sample_function = FunctionCandidate(
        function_name="test_func",
        file_path="/test/test.py",
        language="python",
        line_number=1,
        source_code='def test_func(message: str) -> str:\n    return message',
        parameters=[func_param]
    )
    
    sample_candidate = MCPToolCandidate(
        function=sample_function,
        mcp_score=8.0,
        description="Test function",
        suggested_tool_name="test_func",
        mcp_parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Test message"}
            },
            "required": ["message"]
        }
    )
    
    # Test wrapper generation
    wrapper_code = wrapper_gen._generate_python_wrapper(
        [sample_candidate], "test-server", {"name": "test"}
    )
    
    assert "test_func" in wrapper_code
    assert "mcp-test-server" in wrapper_code
    print("✅ Server wrapper generation works")
    
    # Test basic template functionality (without Jinja2)
    try:
        from dockerfile_generator.dockerfile_generator import DockerfileGenerator
        generator = DockerfileGenerator()
        
        # Test basic dockerfile generation
        context = {
            'server_name': 'test-server',
            'language': 'python',
            'base_image': 'python:3.11-slim',
            'package_file': 'requirements.txt',
            'server_file': 'mcp_server.py',
            'security_level': 'low'
        }
        
        basic_dockerfile = generator._generate_basic_dockerfile("python", context)
        assert "FROM python:3.11-slim" in basic_dockerfile
        assert "requirements.txt" in basic_dockerfile
        print("✅ Basic Dockerfile generation works")
        
    except ImportError as e:
        print(f"⚠️  Jinja2 not available, skipping template tests: {e}")
    
    print("\n🎉 All basic tests passed!")


def test_integration_with_analyzer():
    """Test integration with existing analyzer"""
    print("\nTesting integration with Repository Analyzer...")
    
    # Use existing test data
    test_data_dir = Path(__file__).parent.parent.parent / "tests" / "test_data"
    
    if test_data_dir.exists():
        from analyzer.repository_analyzer import RepositoryAnalyzer
        
        analyzer = RepositoryAnalyzer()
        result = analyzer.analyze_repository(str(test_data_dir))
        
        print(f"✅ Analyzer found {len(result.candidates)} candidates")
        
        # Test that we can process these candidates
        if result.candidates:
            candidate = result.candidates[0]
            print(f"✅ Sample candidate: {candidate.function.function_name} (score: {candidate.mcp_score})")
            
            # Test dependency resolution
            from dockerfile_generator.dependency_resolver import DependencyResolver
            resolver = DependencyResolver()
            
            deps = resolver._resolve_python_dependencies([candidate])
            print(f"✅ Resolved {len(deps)} dependencies")
    else:
        print("⚠️  Test data directory not found, skipping analyzer integration test")


if __name__ == "__main__":
    test_basic_functionality()
    test_integration_with_analyzer()
    
    print(f"\n✅ Simple tests completed successfully!")
    print("Note: Full functionality requires Jinja2 installation")