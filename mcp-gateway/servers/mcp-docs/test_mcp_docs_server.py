#!/usr/bin/env python3
"""
Test script for MCP Documentation Server

Tests the documentation server functionality including resources, tools, and content.
"""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the server directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_docs_server import MCPDocumentationServer


class TestMCPDocumentationServer(unittest.TestCase):
    """Test MCPDocumentationServer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.server = MCPDocumentationServer()
    
    def test_server_initialization(self):
        """Test server initializes properly"""
        self.assertIsNotNone(self.server.mcp)
        self.assertEqual(self.server.mcp.name, "mcp-docs-server")
        self.assertEqual(self.server.mcp.version, "1.0.0")
        self.assertTrue(self.server.docs_path.exists())
    
    async def test_mcp_concepts_resource(self):
        """Test MCP concepts resource retrieval"""
        # Test valid concept
        result = await self.server.mcp._resource_handlers["docs://mcp/concepts/{topic}"]("tools")
        
        self.assertIn("uri", result)
        self.assertEqual(result["uri"], "docs://mcp/concepts/tools")
        self.assertIn("mimeType", result)
        self.assertEqual(result["mimeType"], "text/markdown")
        self.assertIn("text", result)
        self.assertIn("Tools are executable functions", result["text"])
    
    async def test_mcp_concepts_invalid(self):
        """Test invalid MCP concept request"""
        result = await self.server.mcp._resource_handlers["docs://mcp/concepts/{topic}"]("invalid")
        
        self.assertIn("error", result)
        self.assertIn("Unknown MCP concept", result["error"])
    
    async def test_fastmcp_resource(self):
        """Test FastMCP documentation resource"""
        result = await self.server.mcp._resource_handlers["docs://fastmcp/{section}"]("quickstart")
        
        self.assertIn("uri", result)
        self.assertEqual(result["uri"], "docs://fastmcp/quickstart")
        self.assertIn("text", result)
        self.assertIn("FastMCP is a Python framework", result["text"])
    
    async def test_analyzer_resource(self):
        """Test analyzer documentation resource"""
        result = await self.server.mcp._resource_handlers["docs://analyzer/{topic}"]("overview")
        
        self.assertIn("uri", result)
        self.assertEqual(result["uri"], "docs://analyzer/overview")
        self.assertIn("text", result)
        self.assertIn("Repository Analyzer", result["text"])
    
    async def test_search_documentation_tool(self):
        """Test documentation search tool"""
        search_tool = None
        for tool_name, tool_handler in self.server.mcp._tool_handlers.items():
            if tool_name == "search_documentation":
                search_tool = tool_handler
                break
        
        self.assertIsNotNone(search_tool)
        
        # Test search for "tools"
        results = await search_tool(query="tools")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check result structure
        for result in results:
            self.assertIn("uri", result)
            self.assertIn("title", result)
            self.assertIn("category", result)
            self.assertIn("relevance", result)
    
    async def test_search_with_category_filter(self):
        """Test documentation search with category filter"""
        search_tool = None
        for tool_name, tool_handler in self.server.mcp._tool_handlers.items():
            if tool_name == "search_documentation":
                search_tool = tool_handler
                break
        
        # Test category filter
        results = await search_tool(query="quickstart", category="fastmcp")
        self.assertIsInstance(results, list)
        
        # Should find fastmcp quickstart
        fastmcp_results = [r for r in results if "fastmcp" in r["category"]]
        self.assertGreater(len(fastmcp_results), 0)
    
    async def test_list_documentation_topics_tool(self):
        """Test list documentation topics tool"""
        list_tool = None
        for tool_name, tool_handler in self.server.mcp._tool_handlers.items():
            if tool_name == "list_documentation_topics":
                list_tool = tool_handler
                break
        
        self.assertIsNotNone(list_tool)
        
        result = await list_tool()
        self.assertIsInstance(result, dict)
        
        # Check structure
        self.assertIn("mcp", result)
        self.assertIn("fastmcp", result)
        self.assertIn("analyzer", result)
        
        # Check MCP concepts
        self.assertIn("concepts", result["mcp"])
        self.assertIn("tools", result["mcp"]["concepts"])
        self.assertIn("resources", result["mcp"]["concepts"])
    
    async def test_get_documentation_index_tool(self):
        """Test get documentation index tool"""
        index_tool = None
        for tool_name, tool_handler in self.server.mcp._tool_handlers.items():
            if tool_name == "get_documentation_index":
                index_tool = tool_handler
                break
        
        self.assertIsNotNone(index_tool)
        
        result = await index_tool()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Check index entry structure
        for entry in result:
            self.assertIn("uri", entry)
            self.assertIn("title", entry)
            self.assertIn("category", entry)
            self.assertIn("description", entry)
    
    def test_content_generation_methods(self):
        """Test internal content generation methods"""
        # Test concept content
        tools_content = self.server._get_tools_concept()
        self.assertIn("Tools are executable functions", tools_content)
        self.assertIn("@mcp.tool()", tools_content)
        
        resources_content = self.server._get_resources_concept()
        self.assertIn("Resources are static", resources_content)
        self.assertIn("@mcp.resource", resources_content)
        
        # Test FastMCP content
        quickstart_content = self.server._get_fastmcp_quickstart()
        self.assertIn("FastMCP is a Python framework", quickstart_content)
        self.assertIn("pip install fastmcp", quickstart_content)
        
        # Test analyzer content
        overview_content = self.server._get_analyzer_overview()
        self.assertIn("Repository Analyzer", overview_content)
        self.assertIn("MCP tool conversion", overview_content)


class TestContentQuality(unittest.TestCase):
    """Test the quality and completeness of documentation content"""
    
    def setUp(self):
        self.server = MCPDocumentationServer()
    
    def test_mcp_concepts_completeness(self):
        """Test that all MCP concepts are properly documented"""
        concepts = ["tools", "resources", "prompts", "protocol"]
        
        for concept in concepts:
            with self.subTest(concept=concept):
                content = self.server._get_concept_content(concept)
                self.assertIsInstance(content, str)
                self.assertGreater(len(content), 100)  # Reasonable content length
                self.assertIn("MCP", content)  # Should mention MCP
    
    def test_fastmcp_sections_completeness(self):
        """Test that all FastMCP sections are documented"""
        sections = ["quickstart", "decorators", "resources", "tools", "deployment"]
        
        for section in sections:
            with self.subTest(section=section):
                content = self.server._get_fastmcp_content(section)
                self.assertIsInstance(content, str)
                self.assertGreater(len(content), 100)
                self.assertIn("FastMCP", content)
    
    def test_analyzer_topics_completeness(self):
        """Test that all analyzer topics are documented"""
        topics = ["overview", "scoring", "security", "conversion"]
        
        for topic in topics:
            with self.subTest(topic=topic):
                content = self.server._get_analyzer_content(topic)
                self.assertIsInstance(content, str)
                self.assertGreater(len(content), 100)
                self.assertIn("analyzer" in content.lower() or "Repository" in content)
    
    def test_code_examples_present(self):
        """Test that documentation includes code examples"""
        # Check tools concept has code examples
        tools_content = self.server._get_tools_concept()
        self.assertIn("```python", tools_content)
        self.assertIn("@mcp.tool()", tools_content)
        
        # Check FastMCP quickstart has examples
        quickstart_content = self.server._get_fastmcp_quickstart()
        self.assertIn("```python", quickstart_content)
        self.assertIn("from fastmcp import FastMCP", quickstart_content)
        
        # Check analyzer sections have examples
        scoring_content = self.server._get_analyzer_scoring()
        self.assertIn("```python", scoring_content)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the documentation server"""
    
    def setUp(self):
        self.server = MCPDocumentationServer()
    
    async def test_invalid_resource_requests(self):
        """Test handling of invalid resource requests"""
        # Test invalid MCP concept
        result = await self.server.mcp._resource_handlers["docs://mcp/concepts/{topic}"]("nonexistent")
        self.assertIn("error", result)
        
        # Test invalid FastMCP section
        result = await self.server.mcp._resource_handlers["docs://fastmcp/{section}"]("nonexistent")
        self.assertIn("error", result)
        
        # Test invalid analyzer topic
        result = await self.server.mcp._resource_handlers["docs://analyzer/{topic}"]("nonexistent")
        self.assertIn("error", result)
    
    async def test_search_with_empty_query(self):
        """Test search tool with empty query"""
        search_tool = None
        for tool_name, tool_handler in self.server.mcp._tool_handlers.items():
            if tool_name == "search_documentation":
                search_tool = tool_handler
                break
        
        # Empty query should still return results (or handle gracefully)
        results = await search_tool(query="")
        self.assertIsInstance(results, list)
    
    @patch('pathlib.Path.read_text')
    async def test_file_read_error_handling(self, mock_read_text):
        """Test handling of file read errors"""
        mock_read_text.side_effect = IOError("File read error")
        
        # Should fall back to built-in content
        result = await self.server.mcp._resource_handlers["docs://mcp/concepts/{topic}"]("tools")
        
        # Should not contain error, should fall back to built-in content
        self.assertIn("text", result)
        self.assertNotIn("error", result)


def run_async_test(test_func):
    """Helper to run async test functions"""
    return asyncio.run(test_func)


class AsyncTestRunner:
    """Helper class to run async tests"""
    
    @staticmethod
    def run_async_tests():
        """Run all async tests"""
        print("Running async tests...")
        
        # Initialize server
        server = MCPDocumentationServer()
        
        async def run_tests():
            test_cases = TestMCPDocumentationServer()
            test_cases.setUp()
            
            try:
                await test_cases.test_mcp_concepts_resource()
                print("✅ MCP concepts resource test passed")
                
                await test_cases.test_mcp_concepts_invalid()
                print("✅ Invalid MCP concept test passed")
                
                await test_cases.test_fastmcp_resource()
                print("✅ FastMCP resource test passed")
                
                await test_cases.test_analyzer_resource()
                print("✅ Analyzer resource test passed")
                
                await test_cases.test_search_documentation_tool()
                print("✅ Search documentation tool test passed")
                
                await test_cases.test_list_documentation_topics_tool()
                print("✅ List topics tool test passed")
                
                await test_cases.test_get_documentation_index_tool()
                print("✅ Documentation index tool test passed")
                
                print("\n🎉 All async tests passed!")
                
            except Exception as e:
                print(f"❌ Async test failed: {e}")
                raise
        
        asyncio.run(run_tests())


def test_documentation_server_basic():
    """Basic functionality test"""
    print("=== Testing MCP Documentation Server ===")
    
    # Test server initialization
    server = MCPDocumentationServer()
    print("✅ Server initialized successfully")
    
    # Test that resource handlers are registered
    resource_handlers = server.mcp._resource_handlers
    expected_patterns = [
        "docs://mcp/concepts/{topic}",
        "docs://mcp/guides/{guide}",
        "docs://fastmcp/{section}",
        "docs://analyzer/{topic}"
    ]
    
    for pattern in expected_patterns:
        assert pattern in resource_handlers, f"Missing resource handler: {pattern}"
    print("✅ All resource handlers registered")
    
    # Test that tool handlers are registered
    tool_handlers = server.mcp._tool_handlers
    expected_tools = [
        "search_documentation",
        "list_documentation_topics", 
        "get_documentation_index"
    ]
    
    for tool in expected_tools:
        assert tool in tool_handlers, f"Missing tool handler: {tool}"
    print("✅ All tool handlers registered")
    
    # Test content generation methods
    tools_content = server._get_tools_concept()
    assert len(tools_content) > 100, "Tools concept content too short"
    assert "MCP" in tools_content, "Tools content missing MCP reference"
    print("✅ Content generation working")
    
    print("=== Basic tests completed successfully! ===")


if __name__ == "__main__":
    print("MCP Documentation Server Tests")
    print("=" * 50)
    
    # Run basic functionality tests
    test_documentation_server_basic()
    
    # Run async tests
    AsyncTestRunner.run_async_tests()
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n🎉 All tests completed!")