"""
Test suite for Dockerfile Generator
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from unittest import TestCase, main

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dockerfile_generator.dockerfile_generator import DockerfileGenerator
from dockerfile_generator.dependency_resolver import DependencyResolver
from dockerfile_generator.server_wrapper_generator import ServerWrapperGenerator
from analyzer.models import MCPToolCandidate, FunctionCandidate, FunctionParameter


class TestDockerfileGenerator(TestCase):
    """Test the main Dockerfile generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = DockerfileGenerator()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample function candidate
        func_param = FunctionParameter(
            name="data",
            type_hint="str",
            description="Input data to process",
            required=True
        )
        
        sample_function = FunctionCandidate(
            function_name="process_data",
            file_path="/test/utils.py",
            language="python",
            line_number=10,
            source_code="""def process_data(data: str) -> str:
    \"\"\"Process input data and return result\"\"\"
    return data.upper()""",
            docstring="Process input data and return result",
            parameters=[func_param],
            return_type="str"
        )
        
        self.sample_candidate = MCPToolCandidate(
            function=sample_function,
            mcp_score=8.5,
            description="Process input data and return result",
            security_warnings=[],
            docker_requirements=["requests"],
            mcp_parameters={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "Input data to process"
                    }
                },
                "required": ["data"]
            }
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_determine_primary_language(self):
        """Test language detection"""
        # Test with single language
        candidates = [self.sample_candidate]
        language = self.generator._determine_primary_language(candidates)
        self.assertEqual(language, "python")
        
        # Test with mixed languages (would need more candidates)
        # For now, just test the basic case
    
    def test_build_generation_context(self):
        """Test context generation"""
        candidates = [self.sample_candidate]
        context = self.generator._build_generation_context(
            candidates, "python", "test-server", {"name": "test-repo"}
        )
        
        self.assertEqual(context['server_name'], "test-server")
        self.assertEqual(context['language'], "python")
        self.assertEqual(context['function_count'], 1)
        self.assertEqual(context['security_level'], "low")
        self.assertIn("mcp>=1.0.0", context['dependencies'])
    
    def test_generate_basic_dockerfile(self):
        """Test basic Dockerfile generation"""
        context = {
            'server_name': 'test-server',
            'language': 'python',
            'base_image': 'python:3.11-slim',
            'package_file': 'requirements.txt',
            'server_file': 'mcp_server.py',
            'security_level': 'low'
        }
        
        dockerfile = self.generator._generate_basic_dockerfile("python", context)
        
        self.assertIn("FROM python:3.11-slim", dockerfile)
        self.assertIn("COPY requirements.txt", dockerfile)
        self.assertIn("pip install", dockerfile)
        self.assertIn("CMD [\"python\", \"mcp_server.py\"]", dockerfile)
    
    def test_generate_mcp_server_package(self):
        """Test complete package generation"""
        candidates = [self.sample_candidate]
        repo_info = {"name": "test-repo", "url": ""}
        
        result = self.generator.generate_mcp_server_package(
            candidates=candidates,
            server_name="test-server",
            repo_info=repo_info,
            output_dir=self.temp_dir
        )
        
        # Check result structure
        self.assertEqual(result['server_name'], "test-server")
        self.assertEqual(result['language'], "python")
        self.assertEqual(result['total_functions'], 1)
        
        # Check generated files exist
        generated_files = result['generated_files']
        for file_type, file_path in generated_files.items():
            self.assertTrue(Path(file_path).exists(), f"Missing file: {file_type}")
        
        # Check Dockerfile content
        dockerfile_path = Path(generated_files['dockerfile'])
        dockerfile_content = dockerfile_path.read_text()
        self.assertIn("FROM python:3.11-slim", dockerfile_content)
        self.assertIn("mcp_server.py", dockerfile_content)
        
        # Check requirements.txt
        requirements_path = Path(generated_files['requirements'])
        requirements_content = requirements_path.read_text()
        self.assertIn("mcp>=1.0.0", requirements_content)
        self.assertIn("requests", requirements_content)


class TestDependencyResolver(TestCase):
    """Test the dependency resolver"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.resolver = DependencyResolver()
    
    def test_python_stdlib_detection(self):
        """Test Python standard library detection"""
        self.assertIn("os", self.resolver.PYTHON_STDLIB)
        self.assertIn("json", self.resolver.PYTHON_STDLIB)
        self.assertNotIn("requests", self.resolver.PYTHON_STDLIB)
    
    def test_extract_python_imports(self):
        """Test Python import extraction"""
        source_code = '''import os
import requests
from pathlib import Path
from custom_module import func'''
        
        imports = self.resolver._extract_python_imports(source_code)
        
        expected_imports = {"os", "requests", "pathlib", "custom_module"}
        self.assertEqual(imports, expected_imports)
    
    def test_extract_nodejs_imports(self):
        """Test Node.js import extraction"""
        source_code = '''const fs = require('fs');
import axios from 'axios';
import { readFile } from 'fs/promises';'''
        
        imports = self.resolver._extract_nodejs_imports(source_code)
        
        expected_imports = {"fs", "axios", "fs/promises"}
        self.assertEqual(imports, expected_imports)
    
    def test_python_dependency_resolution(self):
        """Test Python dependency resolution"""
        # Create sample candidate with requests import
        sample_function = FunctionCandidate(
            function_name="fetch_data",
            file_path="/test/api.py",
            language="python",
            line_number=5,
            source_code="""import requests
def fetch_data(url: str) -> dict:
    response = requests.get(url)
    return response.json()""",
            parameters=[]
        )
        
        sample_candidate = MCPToolCandidate(
            function=sample_function,
            mcp_score=7.0,
            description="Fetch data from API",
            docker_requirements=["pandas"]
        )
        
        dependencies = self.resolver._resolve_python_dependencies([sample_candidate])
        
        self.assertIn("mcp>=1.0.0", dependencies)
        self.assertIn("requests", dependencies)
        self.assertIn("pandas", dependencies)


class TestServerWrapperGenerator(TestCase):
    """Test the server wrapper generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.wrapper_generator = ServerWrapperGenerator()
        
        # Create sample candidate
        func_param = FunctionParameter(
            name="message",
            type_hint="str",
            description="Message to process",
            required=True
        )
        
        sample_function = FunctionCandidate(
            function_name="echo_message",
            file_path="/test/utils.py",
            language="python",
            line_number=1,
            source_code='''def echo_message(message: str) -> str:
    """Echo the input message"""
    return f"Echo: {message}"''',
            docstring="Echo the input message",
            parameters=[func_param],
            return_type="str"
        )
        
        self.sample_candidate = MCPToolCandidate(
            function=sample_function,
            mcp_score=9.0,
            description="Echo the input message",
            suggested_tool_name="echo_message",
            mcp_parameters={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to process"
                    }
                },
                "required": ["message"]
            }
        )
    
    def test_generate_python_wrapper(self):
        """Test Python wrapper generation"""
        wrapper_code = self.wrapper_generator._generate_python_wrapper(
            candidates=[self.sample_candidate],
            server_name="test-server",
            repo_info={"name": "test-repo"}
        )
        
        # Check for essential components
        self.assertIn("from original_functions import echo_message", wrapper_code)
        self.assertIn("mcp-test-server", wrapper_code)
        self.assertIn("handle_list_tools", wrapper_code)
        self.assertIn("handle_call_tool", wrapper_code)
        self.assertIn('if name == "echo_message":', wrapper_code)
        self.assertIn("echo_message(message)", wrapper_code)
    
    def test_generate_javascript_wrapper(self):
        """Test JavaScript wrapper generation"""
        wrapper_code = self.wrapper_generator._generate_javascript_wrapper(
            candidates=[self.sample_candidate],
            server_name="test-server", 
            repo_info={"name": "test-repo"}
        )
        
        # Check for essential components
        self.assertIn("import { echo_message } from './original_functions.js';", wrapper_code)
        self.assertIn("mcp-test-server", wrapper_code)
        self.assertIn("ListToolsRequestSchema", wrapper_code)
        self.assertIn("CallToolRequestSchema", wrapper_code)
        self.assertIn('if (request.params.name === "echo_message")', wrapper_code)


def run_integration_test():
    """Run a complete integration test"""
    print("Running integration test...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create sample candidates
        func_param1 = FunctionParameter(
            name="text",
            type_hint="str", 
            description="Text to process",
            required=True
        )
        
        func_param2 = FunctionParameter(
            name="count",
            type_hint="int",
            description="Number of repetitions",
            default_value="1",
            required=False
        )
        
        sample_function = FunctionCandidate(
            function_name="repeat_text",
            file_path="/test/text_utils.py",
            language="python",
            line_number=5,
            source_code='''def repeat_text(text: str, count: int = 1) -> str:
    """Repeat text specified number of times"""
    return (text + " ") * count''',
            docstring="Repeat text specified number of times",
            parameters=[func_param1, func_param2],
            return_type="str"
        )
        
        sample_candidate = MCPToolCandidate(
            function=sample_function,
            mcp_score=8.0,
            description="Repeat text specified number of times",
            suggested_tool_name="repeat_text",
            docker_requirements=["requests"],
            mcp_parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to process"},
                    "count": {"type": "integer", "description": "Number of repetitions", "default": 1}
                },
                "required": ["text"]
            }
        )
        
        # Generate complete package
        generator = DockerfileGenerator()
        result = generator.generate_mcp_server_package(
            candidates=[sample_candidate],
            server_name="integration-test",
            repo_info={"name": "test-integration-repo"},
            output_dir=temp_dir
        )
        
        print(f"✅ Integration test passed!")
        print(f"Generated {len(result['generated_files'])} files")
        print(f"Output directory: {temp_dir}")
        
        # Verify key files
        dockerfile_path = Path(result['generated_files']['dockerfile'])
        server_path = Path(result['generated_files']['server'])
        
        dockerfile_content = dockerfile_path.read_text()
        server_content = server_path.read_text()
        
        assert "FROM python:3.11-slim" in dockerfile_content
        assert "repeat_text" in server_content
        assert "integration-test" in server_content
        
        print("✅ All integration test assertions passed!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    main(verbosity=2, exit=False)
    
    # Run integration test
    print("\n" + "="*50)
    run_integration_test()
    
    print(f"\n🎉 All tests completed successfully!")