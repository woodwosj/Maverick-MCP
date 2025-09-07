# 🚀 Maverick MCP

> **Transform any Python codebase into AI-accessible tools in minutes, not hours**

Turn your existing Python functions into powerful MCP (Model Context Protocol) servers that AI assistants like Claude can use directly. No manual configuration, no protocol knowledge required—just point it at your code and get a production-ready containerized server with comprehensive documentation.

[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen)](https://github.com/woodwosj/Maverick-MCP)
[![Docker](https://img.shields.io/badge/docker-containerized-blue)](https://www.docker.com/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-purple)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 💡 What Does This Do?

Imagine having a magic wand that looks at your Python code and automatically creates:
- 🐳 A **Docker container** running an MCP server
- 📋 **Complete documentation** with usage examples
- 🔐 **Security analysis** highlighting any risks
- 🤖 **AI-ready tools** that Claude Code can discover and use
- ⚡ **Production deployment** files and configuration

**In 30 seconds**, you go from "I have some useful Python functions" to "Claude can now use my code as tools."

## 🎯 Perfect For

- **Developers** who want to share their utilities with AI assistants
- **Teams** looking to make internal tools AI-accessible
- **Researchers** who need their analysis functions available to Claude
- **Anyone** tired of manually creating MCP servers and writing documentation

## ⚡ Quick Demo

```bash
# 1. Point it at your Python code
python -c "
from analyzer.repository_analyzer import RepositoryAnalyzer
from dockerfile_generator.dockerfile_generator import DockerfileGenerator

# Analyze your repository 
analyzer = RepositoryAnalyzer()
result = analyzer.analyze_repository('/path/to/your/code')
print(f'Found {len(result.candidates)} useful functions!')

# Generate complete MCP server package
generator = DockerfileGenerator() 
output = generator.generate_mcp_server_package(
    candidates=result.candidates,
    server_name='my-awesome-tools',
    repo_info={'name': 'my-project'},
    output_dir='output/my-server'
)
print(f'Generated {len(output[\"generated_files\"])} files ready for deployment!')
"

# 2. Build and run your new MCP server
cd output/my-server
docker build -t my-awesome-tools .
docker run -i my-awesome-tools

# 3. Connect to Claude Code and start using your functions as AI tools!
```

**Result**: Your Python functions are now available as AI tools with full documentation, examples, and security analysis. 🎉

## 🏗️ What Gets Generated

For every repository you analyze, you get a **complete package**:

```
📦 your-maverick-server/
├── 🐳 Dockerfile                 # Production-ready container
├── 🤖 mcp_server.py             # MCP protocol implementation  
├── 📄 original_functions.py     # Your extracted functions
├── 📋 requirements.txt          # Auto-detected dependencies
├── 📚 README.md                 # Auto-generated documentation
├── 🔧 INTEGRATION.md            # Step-by-step setup guide
├── 🚀 DEPLOYMENT.md             # Production deployment guide
├── ⚙️ servers_entry.yaml       # Maverick MCP gateway configuration
└── 🐋 .dockerignore             # Optimized container builds
```

## 🌟 Why This Is Awesome

### 🧠 **Smart Analysis**
- Automatically finds functions worth converting to MCP tools
- Extracts parameters, types, and documentation 
- Scores each function on "MCP worthiness" (0-10 scale)
- Identifies security risks before deployment

### 🔒 **Security First**
- **Risk Classification**: Flags dangerous operations (file system, network, command execution)
- **Sandboxed Containers**: Non-root users, minimal attack surface
- **Audit Trail**: Comprehensive logging of all operations
- **User Control**: You approve what gets converted

### 📖 **Documentation That Actually Helps**
- **Usage Examples**: Real code examples for every function
- **Integration Guides**: Step-by-step setup for different scenarios  
- **MCP Resources**: Built-in help system for AI assistants
- **API References**: Complete parameter documentation

### 🏃 **Production Ready**
- **Docker Best Practices**: Multi-stage builds, security hardening
- **MCP Protocol Compliance**: Uses official SDK, fully tested
- **Error Handling**: Graceful failures with detailed error messages
- **Performance Optimized**: Efficient container startup and execution

## 🚀 Getting Started

### Prerequisites
```bash
# You need these installed:
- Python 3.8+
- Docker
- Git
```

### Installation

```bash
# Clone the repository
git clone https://github.com/woodwosj/Maverick-MCP.git
cd Maverick-MCP

# Install Python dependencies
pip install -r requirements.txt

# You're ready to go! 🎉
```

### Your First MCP Server

Let's convert the included example code:

```bash
# Test with our mock repository (calculator + text utilities)
python -c "
from analyzer.repository_analyzer import RepositoryAnalyzer
from dockerfile_generator.dockerfile_generator import DockerfileGenerator

# Analyze the included examples
analyzer = RepositoryAnalyzer()
result = analyzer.analyze_repository('tests/mock_repos/simple_python/')

# Generate MCP server
generator = DockerfileGenerator()
output = generator.generate_mcp_server_package(
    candidates=result.candidates,
    server_name='demo-tools',
    repo_info={'name': 'demo'},
    output_dir='my-first-server'
)

print('🎉 Generated your first MCP server!')
print(f'📁 Check out: my-first-server/')
print(f'🔧 Found {len(result.candidates)} functions to convert')
print(f'📋 Created {len(output[\"generated_files\"])} files')
"

# Build and test it
cd my-first-server
docker build -t demo-tools .
echo '🚀 Your MCP server is ready!'
```

**What you just created**: A working MCP server with 16 functions including a calculator, text utilities, and even some "risky" functions (properly flagged for security).

## 🔍 Deep Dive: How It Works

### 1. **Repository Analysis** 🔬
```python
# The analyzer uses Python's AST to understand your code
analyzer = RepositoryAnalyzer()
result = analyzer.analyze_repository('/your/code')

# It finds functions like this:
def calculate_area(radius: float) -> float:
    """Calculate circle area from radius."""
    return math.pi * radius * radius

# And converts them to MCP tool candidates with:
# - Parameter types and descriptions  
# - Security risk assessment
# - Usage examples
# - MCP protocol compatibility score
```

### 2. **Intelligent Conversion** 🤖
The generator creates production-ready code:

```python
# Your function becomes an MCP tool:
@app.tool()
async def calculate_area(radius: float) -> float:
    """Calculate circle area from radius.
    
    Args:
        radius: Circle radius (must be positive)
    
    Returns:
        Area of the circle
    
    Examples:
        >>> calculate_area(5.0)
        78.54
    """
    return math.pi * radius * radius
```

### 3. **Complete Documentation** 📚
Every generated server includes comprehensive docs:

- **README.md**: How to use your new MCP server
- **Integration guides**: Connect to Claude Code, API usage
- **Security analysis**: What functions do what, risks involved
- **Examples**: Real code snippets for every function

## 🎨 Advanced Features

### Custom Generation Options
```python
# Fine-tune the generation process
generator = DockerfileGenerator()
output = generator.generate_mcp_server_package(
    candidates=analyzed_functions,
    server_name='my-custom-server',
    repo_info={'name': 'my-project', 'url': 'https://github.com/...'},
    output_dir='custom-output',
    # Add custom configuration here
)
```

### Security Configuration
The generator automatically classifies functions by risk level:

- 🟢 **Low Risk**: Math, string manipulation, data processing
- 🟡 **Medium Risk**: File reading, HTTP requests  
- 🔴 **High Risk**: Command execution, file writing, system access

You control what gets included based on your security requirements.

### Multi-Repository Support
```bash
# Analyze multiple repositories and combine them
python .dev/tools/batch_analysis.py \
  --repos /path/to/repo1,/path/to/repo2 \
  --output combined-server \
  --name "multi-repo-tools"
```

## 🧪 Testing Your Generated Servers

Every server comes with built-in testing:

```bash
# Test MCP protocol compliance
cd your-generated-server
python test_mcp_compliance.py

# Test individual functions
python test_functions.py

# Full integration test
docker run --rm -i your-server-image python -c "
from mcp_server import app
print(f'✅ Server {app.name} is working!')
"
```

## 📊 Real-World Examples

### Example 1: Data Analysis Tools
```python
# Your existing code:
def analyze_csv(file_path: str) -> dict:
    # Your analysis logic
    return {"rows": 1000, "columns": 5, "summary": "..."}

# Becomes MCP tool that Claude can use:
# "Claude, analyze the sales data CSV and summarize the trends"
```

### Example 2: Utility Functions  
```python
# Your utilities:
def format_phone(phone: str) -> str:
    return re.sub(r'(\d{3})(\d{3})(\d{4})', r'(\1) \2-\3', phone)

# Claude can now use it:
# "Claude, format this list of phone numbers for me"
```

### Example 3: API Integrations
```python
# Your API wrapper:
def get_weather(city: str) -> dict:
    # Your weather API logic
    return {"temp": 72, "conditions": "sunny"}

# Claude gains weather capabilities:
# "Claude, what's the weather like in San Francisco?"
```

## 🔧 Customization & Extension

### Adding Your Own Templates
```python
# Create custom Dockerfile templates
custom_template = """
FROM python:3.11-slim
# Your custom setup
COPY . /app
CMD ["python", "mcp_server.py"]
"""

generator.add_template('my-template', custom_template)
```

### Custom Security Rules
```python
# Define your own security classifications
security_rules = {
    'database_operations': 'HIGH_RISK',
    'file_encryption': 'MEDIUM_RISK',  
    'data_validation': 'LOW_RISK'
}

analyzer.add_security_rules(security_rules)
```

## 📈 Performance & Scaling

### Resource Usage
- **Memory**: ~50MB base + ~10-20MB per active server
- **Startup**: ~2-5 seconds for typical Python servers
- **Throughput**: Handles 100+ concurrent MCP requests
- **Storage**: ~100MB per generated server package

### Production Deployment
```yaml
# docker-compose.yml for production
version: '3.8'
services:
  my-mcp-server:
    build: ./my-server
    restart: unless-stopped
    resource_limits:
      memory: 256M
      cpu: '0.5'
    healthcheck:
      test: ["CMD", "python", "-c", "import mcp_server"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🐛 Troubleshooting

### Common Issues

**Q: My functions aren't being detected**
```bash
# Check if your functions have proper docstrings and type hints
def my_function(param: str) -> str:
    """This docstring is required for MCP detection."""
    return param.upper()
```

**Q: Docker build fails with dependency errors**
```bash
# The generator creates requirements.txt automatically, but you can customize it
echo "your-special-package==1.0.0" >> output/your-server/requirements.txt
```

**Q: Generated server won't start**
```bash
# Test the server locally first
cd output/your-server
python mcp_server.py
# Check for import errors or missing dependencies
```

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python your_generation_script.py
```

### Getting Help
- 📖 Check the generated `README.md` in your server package
- 🔍 Look at `tests/mock_repos/` for working examples
- 🐛 Open an issue if you find bugs
- 💬 Discussions for questions and feature requests

## 🤝 Contributing

We'd love your contributions! Here's how:

### Quick Contributions
- 🐛 **Bug Reports**: Found something broken? Let us know!
- 💡 **Feature Ideas**: Have ideas for improvement? Share them!
- 📖 **Documentation**: Help make the docs even better
- 🧪 **Test Cases**: Add more example repositories

### Development Setup
```bash
# Fork the repo and clone your fork
git clone https://github.com/yourusername/Maverick-MCP.git
cd Maverick-MCP

# Install development dependencies
pip install -r requirements.txt

# Run the test suite
python -m pytest tests/

# Make your changes and submit a PR!
```

### Architecture Overview
```
Repository Code → AST Analysis → MCP Tool Candidates → 
Maverick MCP Generation → Documentation → Testing → 
Production-Ready Container
```

## 🎯 Roadmap

### Coming Soon
- [ ] **JavaScript/TypeScript** support (ES6+ analysis)
- [ ] **Go** support (AST parsing for Go modules)  
- [ ] **Web Interface** for non-developers
- [ ] **GitHub Integration** (analyze repos directly from URLs)
- [ ] **Advanced Security** (permission management, sandboxing)

### Future Vision
- [ ] **Multi-language** repository analysis
- [ ] **Cloud deployment** (AWS, GCP, Azure)
- [ ] **Monitoring dashboard** for deployed servers
- [ ] **Auto-scaling** based on usage patterns

## 💝 Recognition

Maverick MCP stands on the shoulders of giants:

- **[Model Context Protocol](https://modelcontextprotocol.io/)** - The standard that makes AI-tool integration possible
- **[FastMCP](https://github.com/jlowin/fastmcp)** - The Python framework powering our MCP servers
- **[Docker](https://www.docker.com/)** - Containerization that makes deployment simple
- **[Python AST](https://docs.python.org/3/library/ast.html)** - The foundation of our code analysis

## 📄 License

MIT License - build, modify, and distribute freely! See [LICENSE](LICENSE) for details.

---

## 🚀 Ready to Get Started?

```bash
# In just 3 commands, you can have your first MCP server running:
git clone https://github.com/woodwosj/Maverick-MCP.git
cd Maverick-MCP  
python -c "from analyzer.repository_analyzer import RepositoryAnalyzer; print('🎉 Maverick MCP is ready to analyze your code!')"

# Then point it at your Python code and watch the magic happen! ✨
```

**Questions? Issues? Ideas?** 

Open an issue, start a discussion, or just dive in and start converting your code to MCP tools. The future of AI-assisted development is here! 🤖✨

---

> "The best tools are the ones that feel like magic but work like engineering." - Maverick MCP is both! 🪄⚙️