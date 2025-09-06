#!/usr/bin/env python3
"""
Integration test for MCP Documentation Server

Tests that the documentation server integrates properly with the MCP Gateway.
"""

import yaml
from pathlib import Path


def test_servers_yaml_integration():
    """Test that mcp-docs server is properly configured in servers.yaml"""
    print("=== Testing servers.yaml Integration ===")
    
    servers_file = Path("servers.yaml")
    if not servers_file.exists():
        print("❌ servers.yaml not found")
        return False
    
    with open(servers_file, 'r') as f:
        servers_config = yaml.safe_load(f)
    
    if "mcp-docs" not in servers_config:
        print("❌ mcp-docs server not found in servers.yaml")
        return False
    
    mcp_docs_config = servers_config["mcp-docs"]
    
    # Check required fields
    required_fields = ["image", "command", "description", "tools", "resources"]
    for field in required_fields:
        if field not in mcp_docs_config:
            print(f"❌ Missing required field: {field}")
            return False
    
    print("✅ mcp-docs server properly configured in servers.yaml")
    
    # Check tools configuration
    tools = mcp_docs_config["tools"]
    expected_tools = ["search_documentation", "list_documentation_topics", "get_documentation_index"]
    
    for tool in expected_tools:
        found = any(t["name"] == tool for t in tools)
        if not found:
            print(f"❌ Missing tool: {tool}")
            return False
        print(f"✅ Tool configured: {tool}")
    
    # Check resources configuration  
    resources = mcp_docs_config["resources"]
    expected_patterns = [
        "docs://mcp/concepts/**",
        "docs://mcp/guides/**",
        "docs://fastmcp/**", 
        "docs://analyzer/**"
    ]
    
    for pattern in expected_patterns:
        found = any(r["pattern"] == pattern for r in resources)
        if not found:
            print(f"❌ Missing resource pattern: {pattern}")
            return False
        print(f"✅ Resource pattern configured: {pattern}")
    
    return True


def test_documentation_server_files():
    """Test that documentation server files are present and valid"""
    print("\n=== Testing Documentation Server Files ===")
    
    server_dir = Path("servers/mcp-docs")
    if not server_dir.exists():
        print("❌ Documentation server directory not found")
        return False
    
    required_files = [
        "mcp_docs_server.py",
        "Dockerfile",
        "requirements.txt",
        "test_mcp_docs_server.py"
    ]
    
    for file in required_files:
        file_path = server_dir / file
        if not file_path.exists():
            print(f"❌ Missing file: {file}")
            return False
        print(f"✅ File present: {file}")
    
    # Check documentation structure
    doc_dir = server_dir / "documentation"
    if not doc_dir.exists():
        print("❌ Documentation directory not found")
        return False
    
    expected_docs = [
        "mcp/concepts/tools.md",
        "mcp/concepts/resources.md", 
        "fastmcp/quickstart.md"
    ]
    
    for doc in expected_docs:
        doc_path = doc_dir / doc
        if not doc_path.exists():
            print(f"❌ Missing documentation: {doc}")
            return False
        
        # Check content length
        content = doc_path.read_text()
        if len(content) < 100:
            print(f"❌ Documentation too short: {doc}")
            return False
            
        print(f"✅ Documentation present: {doc}")
    
    return True


def test_docker_image_exists():
    """Test that Docker image was built successfully"""
    print("\n=== Testing Docker Image ===")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ["docker", "images", "mcp-docs-server", "--format", "table"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Failed to check Docker images")
            return False
        
        if "mcp-docs-server" not in result.stdout:
            print("❌ mcp-docs-server Docker image not found")
            print("Run: cd servers/mcp-docs && docker build -t mcp-docs-server .")
            return False
        
        print("✅ mcp-docs-server Docker image exists")
        return True
        
    except FileNotFoundError:
        print("⚠️  Docker not available for testing")
        return True  # Don't fail if Docker isn't available


def main():
    """Run all integration tests"""
    print("MCP Documentation Server Integration Tests")
    print("=" * 60)
    
    tests = [
        test_servers_yaml_integration,
        test_documentation_server_files,
        test_docker_image_exists
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"❌ Test error in {test.__name__}: {e}")
    
    print(f"\n" + "=" * 60)
    if passed == total:
        print(f"🎉 All {total} integration tests passed!")
        print("\nNext steps:")
        print("1. Start the gateway: docker-compose up -d")
        print("2. The mcp-docs server will be available via the gateway")
        print("3. Test with: curl http://localhost:8000/mcp")
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())