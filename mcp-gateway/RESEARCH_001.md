# RESEARCH REPORT: Repository Analyzer Implementation
**Task ID**: Task-001  
**Agent**: Context Manager  
**Date**: 2025-09-06  
**Priority**: HIGH

## Executive Summary

Research for implementing a multi-language repository analyzer that can scan Python, JavaScript, and Go codebases to identify functions suitable for MCP tool conversion. The analyzer should extract function signatures, docstrings, and determine MCP tool suitability.

## Key Technologies and Approaches

### 1. Python Code Analysis

#### Primary Tool: `ast` module (Built-in)
- **Capability**: Parse Python source code into Abstract Syntax Trees
- **Use Case**: Extract function definitions, docstrings, parameters, return types
- **Implementation**: 
  ```python
  import ast
  class FunctionVisitor(ast.NodeVisitor):
      def visit_FunctionDef(self, node):
          # Extract function metadata
  ```

#### Alternative: `libcst` (Concrete Syntax Tree)
- **Advantage**: Preserves exact formatting and comments
- **Use Case**: When code modification is needed
- **Better for**: Documentation extraction and code transformation

### 2. JavaScript Code Analysis

#### Primary Tool: `@babel/parser` + `@babel/traverse`
- **Capability**: Industry standard JS/TS AST parsing
- **Implementation**: Node.js based parser
- **Use Case**: Extract functions, classes, JSDoc comments

#### Alternative: `tree-sitter-javascript`
- **Advantage**: Language-agnostic parser
- **Performance**: Fast, incremental parsing
- **Multi-language**: Single parser for multiple languages

### 3. Go Code Analysis

#### Primary Tool: `go/ast` + `go/parser` (Go standard library)
- **Implementation**: Go-based analysis tool
- **Capability**: Parse Go source, extract functions, comments
- **Integration**: Requires Go runtime or subprocess calls

#### Alternative: `tree-sitter-go`
- **Advantage**: Consistent with tree-sitter approach
- **Integration**: Python bindings available

### 4. Multi-Language Unified Approach

#### Recommended: Tree-sitter Framework
- **Languages Supported**: Python, JavaScript, Go, Rust, C++, etc.
- **Python Package**: `tree-sitter`
- **Benefits**:
  - Single parsing framework
  - Consistent query syntax
  - High performance
  - Incremental parsing

## Implementation Strategy

### Phase 1: Core Repository Analyzer

```python
class RepositoryAnalyzer:
    def __init__(self):
        self.parsers = {
            'python': PythonAnalyzer(),
            'javascript': JavaScriptAnalyzer(), 
            'go': GoAnalyzer()
        }
    
    def analyze_repository(self, repo_path):
        # 1. Detect language files
        # 2. Parse and extract functions
        # 3. Analyze MCP suitability
        # 4. Generate conversion report
```

### Phase 2: MCP Suitability Detection

#### Function Classification Criteria:
1. **Pure Functions**: No side effects, good for MCP tools
2. **I/O Operations**: File reading, API calls - suitable for MCP
3. **Utility Functions**: Data processing, transformation
4. **Avoid**: GUI code, system modifications, authentication

#### Scoring Algorithm:
- **High Score (8-10)**: Well-documented, clear I/O, no dependencies
- **Medium Score (5-7)**: Some documentation, manageable dependencies
- **Low Score (1-4)**: Complex dependencies, poor documentation

### Phase 3: Documentation Analysis

#### Documentation Sources:
1. **Docstrings/Comments**: Primary source of tool descriptions
2. **README.md**: Project overview and usage examples
3. **API Documentation**: Endpoint descriptions
4. **Test Files**: Usage examples and expected behavior

#### Extraction Strategy:
```python
def extract_documentation(function_node):
    docstring = get_docstring(function_node)
    parameters = extract_parameter_docs(docstring)
    return {
        'description': extract_description(docstring),
        'parameters': parameters,
        'examples': find_usage_examples(function_node)
    }
```

## Security Considerations

### Dangerous Pattern Detection

#### High-Risk Patterns:
- File system modifications outside working directory
- Network requests without validation
- System command execution
- Database operations without constraints
- Authentication/credential handling

#### Implementation:
```python
class SecurityScanner:
    DANGEROUS_PATTERNS = [
        r'os\.system\(',
        r'subprocess\.',
        r'eval\(',
        r'exec\(',
        r'__import__\(',
        r'open\([\'"].*/.*[\'"]',  # Absolute paths
    ]
    
    def scan_function(self, source_code):
        warnings = []
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, source_code):
                warnings.append(f"Potentially dangerous: {pattern}")
        return warnings
```

## Tool Architecture

### Directory Structure:
```
analyzer/
├── __init__.py
├── repository_analyzer.py     # Main orchestrator
├── language_parsers/
│   ├── python_analyzer.py
│   ├── javascript_analyzer.py
│   └── go_analyzer.py
├── security/
│   └── pattern_scanner.py
├── documentation/
│   └── doc_extractor.py
└── mcp_generator/
    └── tool_generator.py
```

### Key Classes:

1. **RepositoryAnalyzer**: Main orchestrator
2. **LanguageAnalyzer**: Base class for language-specific parsing
3. **FunctionCandidate**: Data class for extracted functions
4. **MCPToolCandidate**: Analyzed function with MCP metadata
5. **SecurityScanner**: Pattern detection for dangerous code
6. **DocumentationExtractor**: Extracts and parses documentation

## Dependencies Required

### Python Packages:
```
tree-sitter==0.20.4
tree-sitter-python==0.20.4
tree-sitter-javascript==0.20.3  
tree-sitter-go==0.20.0
gitpython==3.1.40
pyyaml==6.0.1
```

### Optional Enhancements:
- `libcst`: Advanced Python analysis
- `@babel/parser`: If using Node.js for JS analysis
- `pygit2`: Advanced Git integration

## Expected Output Format

### Function Analysis Result:
```json
{
  "repository": "github.com/user/repo",
  "analyzed_files": 45,
  "languages": ["python", "javascript"],
  "candidates": [
    {
      "function_name": "process_data",
      "file_path": "src/utils.py",
      "language": "python",
      "mcp_score": 8.5,
      "description": "Process CSV data and return cleaned results",
      "parameters": {
        "csv_path": {"type": "str", "description": "Path to CSV file"},
        "clean_nulls": {"type": "bool", "default": true}
      },
      "security_warnings": [],
      "suggested_tool_name": "process_csv_data",
      "docker_requirements": ["pandas", "numpy"]
    }
  ],
  "security_summary": {
    "high_risk_functions": 2,
    "warnings_total": 5
  }
}
```

## Integration Points

### 1. Docker Generator Integration:
- Function candidates → Dockerfile templates
- Dependency analysis → Requirements files
- Entry point generation

### 2. MCP Tool Generator:
- Function metadata → MCP tool schemas
- Documentation → Tool descriptions
- Parameters → MCP parameter definitions

### 3. User Approval Workflow:
- Present analysis results
- Allow function selection/deselection
- Enable custom modifications

## Implementation Priorities

### Must-Have (Phase 1):
1. Multi-language function extraction
2. Basic MCP suitability scoring
3. Security pattern detection
4. JSON output format

### Nice-to-Have (Phase 2):
1. Advanced documentation analysis
2. Test file integration
3. Dependency graph analysis
4. Interactive CLI for repository analysis

### Future Enhancements (Phase 3):
1. ML-based function classification
2. Automatic documentation generation
3. Performance analysis integration
4. Code quality metrics

## Conclusion

The Repository Analyzer should be built using tree-sitter for consistent multi-language parsing, with a focus on security-first analysis and comprehensive documentation extraction. The modular architecture will allow for easy extension to additional languages and analysis techniques.

**Estimated Development Time**: 3-5 days for Phase 1 implementation
**Key Success Metrics**: 
- Successfully analyze 95%+ of target functions
- Zero false-positive security warnings
- Generate usable MCP tool candidates from analysis

---

**Next Agent**: CODER
**Next Task**: Implement the RepositoryAnalyzer core system with tree-sitter integration