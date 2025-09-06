"""
Dependency resolution system for MCP server generation
"""

import re
import ast
from typing import List, Set, Dict, Optional
from pathlib import Path

# Import from analyzer
import sys
sys.path.append(str(Path(__file__).parent.parent))
from analyzer.models import MCPToolCandidate


class DependencyResolver:
    """Resolves dependencies for different programming languages"""
    
    # Python standard library modules (partial list of common ones)
    PYTHON_STDLIB = {
        'os', 'sys', 'json', 'csv', 'xml', 'html', 'http', 'urllib',
        'datetime', 'time', 'calendar', 'collections', 'itertools',
        'functools', 'operator', 'pathlib', 'glob', 'shutil', 'tempfile',
        'io', 'string', 'textwrap', 're', 'math', 'random', 'statistics',
        'hashlib', 'hmac', 'secrets', 'uuid', 'logging', 'traceback',
        'warnings', 'inspect', 'types', 'copy', 'pickle', 'sqlite3',
        'threading', 'multiprocessing', 'concurrent', 'asyncio', 'socket',
        'subprocess', 'argparse', 'configparser', 'getpass', 'platform'
    }
    
    # Known package mappings for common imports
    PYTHON_PACKAGE_MAPPINGS = {
        'cv2': 'opencv-python',
        'pil': 'Pillow',
        'PIL': 'Pillow',
        'sklearn': 'scikit-learn',
        'yaml': 'PyYAML',
        'bs4': 'beautifulsoup4',
        'dateutil': 'python-dateutil',
        'jwt': 'PyJWT',
        'crypto': 'pycryptodome',
        'psutil': 'psutil',
        'lxml': 'lxml',
        'openpyxl': 'openpyxl',
        'xlrd': 'xlrd',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'plotly': 'plotly'
    }
    
    # Node.js built-in modules
    NODEJS_BUILTIN = {
        'assert', 'buffer', 'child_process', 'cluster', 'console', 'constants',
        'crypto', 'dgram', 'dns', 'domain', 'events', 'fs', 'http', 'https',
        'module', 'net', 'os', 'path', 'punycode', 'querystring', 'readline',
        'repl', 'stream', 'string_decoder', 'sys', 'timers', 'tls', 'tty',
        'url', 'util', 'vm', 'zlib'
    }
    
    def resolve_dependencies(self, candidates: List[MCPToolCandidate], language: str) -> List[str]:
        """
        Resolve dependencies for a list of MCP tool candidates
        
        Args:
            candidates: List of MCP tool candidates
            language: Programming language ('python', 'javascript', 'go')
            
        Returns:
            List of dependency specifications
        """
        if language == 'python':
            return self._resolve_python_dependencies(candidates)
        elif language == 'javascript':
            return self._resolve_nodejs_dependencies(candidates)
        elif language == 'go':
            return self._resolve_go_dependencies(candidates)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _resolve_python_dependencies(self, candidates: List[MCPToolCandidate]) -> List[str]:
        """Resolve Python dependencies"""
        dependencies = set()
        
        # Always include MCP SDK
        dependencies.add("mcp>=1.0.0")
        
        for candidate in candidates:
            func = candidate.function
            
            # Extract imports from function source
            imports = self._extract_python_imports(func.source_code)
            
            # Add discovered dependencies  
            for imp in imports:
                if imp not in self.PYTHON_STDLIB:
                    # Check for known package mappings
                    package_name = self.PYTHON_PACKAGE_MAPPINGS.get(imp, imp)
                    dependencies.add(package_name)
            
            # Add dependencies from analyzer's docker_requirements
            dependencies.update(candidate.docker_requirements)
            
            # Infer additional dependencies from function patterns
            source_lower = func.source_code.lower()
            
            if 'requests.' in source_lower or 'import requests' in source_lower:
                dependencies.add("requests")
            if 'pandas.' in source_lower or 'import pandas' in source_lower:
                dependencies.add("pandas")
            if 'numpy.' in source_lower or 'import numpy' in source_lower:
                dependencies.add("numpy")
            if 'flask' in source_lower:
                dependencies.add("flask")
            if 'fastapi' in source_lower:
                dependencies.add("fastapi")
            if 'sqlalchemy' in source_lower:
                dependencies.add("sqlalchemy")
        
        # Convert to sorted list and add version constraints where appropriate
        return sorted(self._add_version_constraints(list(dependencies), 'python'))
    
    def _resolve_nodejs_dependencies(self, candidates: List[MCPToolCandidate]) -> List[str]:
        """Resolve Node.js dependencies"""
        dependencies = set()
        
        # Always include MCP SDK
        dependencies.add("@modelcontextprotocol/sdk")
        
        for candidate in candidates:
            func = candidate.function
            
            # Extract requires/imports from function source
            imports = self._extract_nodejs_imports(func.source_code)
            
            # Add discovered dependencies
            for imp in imports:
                if imp not in self.NODEJS_BUILTIN and not imp.startswith('./') and not imp.startswith('../'):
                    dependencies.add(imp)
            
            # Add dependencies from analyzer's docker_requirements  
            dependencies.update(candidate.docker_requirements)
            
            # Infer additional dependencies from function patterns
            source_lower = func.source_code.lower()
            
            if 'axios' in source_lower:
                dependencies.add("axios")
            if 'express' in source_lower:
                dependencies.add("express")
            if 'lodash' in source_lower:
                dependencies.add("lodash")
            if 'moment' in source_lower:
                dependencies.add("moment")
            if 'cheerio' in source_lower:
                dependencies.add("cheerio")
        
        return sorted(list(dependencies))
    
    def _resolve_go_dependencies(self, candidates: List[MCPToolCandidate]) -> List[str]:
        """Resolve Go dependencies (basic implementation)"""
        dependencies = set()
        
        for candidate in candidates:
            func = candidate.function
            
            # Extract imports from function source
            imports = self._extract_go_imports(func.source_code)
            
            # Add non-standard library dependencies
            for imp in imports:
                if '.' in imp and not imp.startswith('golang.org/x/'):
                    # Third-party package
                    dependencies.add(imp)
        
        return sorted(list(dependencies))
    
    def _extract_python_imports(self, source_code: str) -> Set[str]:
        """Extract Python imports from source code"""
        imports = set()
        
        try:
            tree = ast.parse(source_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        
        except SyntaxError:
            # Fallback to regex-based extraction
            imports.update(self._extract_imports_regex(source_code, 'python'))
        
        return imports
    
    def _extract_nodejs_imports(self, source_code: str) -> Set[str]:
        """Extract Node.js imports/requires from source code"""
        imports = set()
        
        # Regex patterns for different import styles
        patterns = [
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',  # require('module')
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',  # import ... from 'module'
            r'import\s+[\'"]([^\'"]+)[\'"]',  # import 'module'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, source_code)
            imports.update(matches)
        
        return imports
    
    def _extract_go_imports(self, source_code: str) -> Set[str]:
        """Extract Go imports from source code"""
        imports = set()
        
        # Regex pattern for Go imports
        patterns = [
            r'import\s+"([^"]+)"',  # import "package"
            r'import\s+\(\s*([^)]+)\s*\)',  # import ( ... )
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, source_code, re.MULTILINE | re.DOTALL)
            for match in matches:
                if '\n' in match:  # Multi-line import block
                    for line in match.split('\n'):
                        line = line.strip().strip('"')
                        if line and not line.startswith('//'):
                            imports.add(line)
                else:
                    imports.add(match.strip('"'))
        
        return imports
    
    def _extract_imports_regex(self, source_code: str, language: str) -> Set[str]:
        """Fallback regex-based import extraction"""
        imports = set()
        
        if language == 'python':
            patterns = [
                r'import\s+(\w+)',
                r'from\s+(\w+)\s+import',
            ]
        else:
            return imports
        
        for pattern in patterns:
            matches = re.findall(pattern, source_code)
            imports.update(matches)
        
        return imports
    
    def _add_version_constraints(self, dependencies: List[str], language: str) -> List[str]:
        """Add version constraints to dependencies"""
        constrained_deps = []
        
        # Known stable versions for common packages
        if language == 'python':
            version_constraints = {
                'requests': '>=2.25.0,<3.0.0',
                'pandas': '>=1.3.0,<3.0.0', 
                'numpy': '>=1.20.0,<2.0.0',
                'flask': '>=2.0.0,<3.0.0',
                'fastapi': '>=0.68.0,<1.0.0',
                'sqlalchemy': '>=1.4.0,<3.0.0',
                'pyyaml': '>=5.4.0,<7.0.0',
                'pillow': '>=8.0.0,<11.0.0'
            }
            
            for dep in dependencies:
                if dep in version_constraints:
                    constrained_deps.append(f"{dep}{version_constraints[dep]}")
                elif '>' not in dep and '<' not in dep and '=' not in dep:
                    constrained_deps.append(dep)  # Keep as-is if no version specified
                else:
                    constrained_deps.append(dep)
        else:
            constrained_deps = dependencies
        
        return constrained_deps