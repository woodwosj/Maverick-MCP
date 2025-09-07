"""
Main repository analyzer orchestrator
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set, Optional
import json

from .models import (
    FunctionCandidate, MCPToolCandidate, AnalysisResult, 
    FunctionParameter
)
from .language_parsers.python_analyzer import PythonAnalyzer
from .language_parsers.javascript_analyzer import JavaScriptAnalyzer
from .security.pattern_scanner import SecurityScanner


class RepositoryAnalyzer:
    """
    Main orchestrator for repository analysis and MCP tool candidate identification
    """
    
    # File patterns for different languages
    LANGUAGE_PATTERNS = {
        'python': [r'\.py$'],
        'javascript': [r'\.js$', r'\.jsx$', r'\.ts$', r'\.tsx$'],
        'go': [r'\.go$']
    }
    
    # Common directories to skip
    SKIP_DIRECTORIES = {
        '.git', '.svn', '.hg',
        '__pycache__', '.pytest_cache',
        'node_modules', 'dist', 'build',
        '.venv', 'venv', 'env',
        '.idea', '.vscode',
        'tests', 'test'  # Skip test directories for now
    }
    
    # Files to skip
    SKIP_FILES = {
        '__init__.py',  # Usually just imports
        'setup.py', 'conftest.py',
        'manage.py'  # Django management
    }
    
    def __init__(self):
        self.analyzers = {
            'python': PythonAnalyzer(),
            'javascript': JavaScriptAnalyzer()
        }
        self.security_scanner = SecurityScanner()
    
    def analyze_repository(self, repo_path: str) -> AnalysisResult:
        """
        Analyze a complete repository for MCP tool candidates
        
        Args:
            repo_path: Path to the repository root
            
        Returns:
            Complete analysis result with MCP tool candidates
        """
        repo_path = Path(repo_path).resolve()
        
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        print(f"Analyzing repository: {repo_path}")
        
        # Discover all relevant files
        files_by_language = self._discover_files(repo_path)
        
        # Analyze files by language
        all_functions = []
        for language, files in files_by_language.items():
            print(f"Analyzing {len(files)} {language} files...")
            
            if language in self.analyzers:
                analyzer = self.analyzers[language]
                for file_path in files:
                    try:
                        functions = analyzer.analyze_file(str(file_path))
                        all_functions.extend(functions)
                    except Exception as e:
                        print(f"Error analyzing {file_path}: {e}")
        
        print(f"Found {len(all_functions)} functions across all files")
        
        # Convert functions to MCP tool candidates
        mcp_candidates = self._evaluate_mcp_candidates(all_functions)
        
        # Generate security summary
        security_summary = self.security_scanner.get_security_summary(all_functions)
        
        # Create final result
        result = AnalysisResult(
            repository=str(repo_path),
            analyzed_files=sum(len(files) for files in files_by_language.values()),
            languages=list(files_by_language.keys()),
            candidates=mcp_candidates,
            security_summary=security_summary
        )
        
        print(f"Analysis complete: {len(mcp_candidates)} MCP tool candidates identified")
        
        return result
    
    def _discover_files(self, repo_path: Path) -> Dict[str, List[Path]]:
        """
        Discover all relevant source files in the repository
        
        Args:
            repo_path: Repository root path
            
        Returns:
            Dictionary mapping language to list of file paths
        """
        files_by_language = {}
        
        for language, patterns in self.LANGUAGE_PATTERNS.items():
            files_by_language[language] = []
            compiled_patterns = [re.compile(pattern) for pattern in patterns]
            
            for root, dirs, files in os.walk(repo_path):
                # Skip unwanted directories
                dirs[:] = [d for d in dirs if d not in self.SKIP_DIRECTORIES]
                
                root_path = Path(root)
                
                for file_name in files:
                    # Skip unwanted files
                    if file_name in self.SKIP_FILES:
                        continue
                    
                    # Check if file matches language patterns
                    if any(pattern.search(file_name) for pattern in compiled_patterns):
                        file_path = root_path / file_name
                        
                        # Additional filtering for empty or very small files
                        try:
                            if file_path.stat().st_size < 50:  # Skip very small files
                                continue
                        except OSError:
                            continue
                        
                        files_by_language[language].append(file_path)
        
        # Remove languages with no files found
        files_by_language = {k: v for k, v in files_by_language.items() if v}
        
        return files_by_language
    
    def _evaluate_mcp_candidates(self, functions: List[FunctionCandidate]) -> List[MCPToolCandidate]:
        """
        Evaluate functions and convert suitable ones to MCP tool candidates
        
        Args:
            functions: List of all discovered functions
            
        Returns:
            List of MCP tool candidates with scores and metadata
        """
        candidates = []
        
        for function in functions:
            # Calculate MCP suitability score
            mcp_score = self._calculate_mcp_score(function)
            
            # Skip functions with very low scores
            if mcp_score < 3.0:
                continue
            
            # Run security analysis
            security_warnings = self.security_scanner.scan_function(function)
            
            # Skip functions with high security risks (unless they have amazing documentation)
            risk_score = self.security_scanner.calculate_risk_score(security_warnings)
            if risk_score > 5.0 and mcp_score < 8.0:
                continue
            
            # Generate tool description
            description = self._generate_tool_description(function)
            
            # Generate MCP parameter schema
            mcp_parameters = self._generate_mcp_parameters(function)
            
            # Determine Docker requirements (basic inference)
            docker_requirements = self._infer_docker_requirements(function)
            
            # Create MCP tool candidate
            candidate = MCPToolCandidate(
                function=function,
                mcp_score=mcp_score,
                description=description,
                security_warnings=security_warnings,
                docker_requirements=docker_requirements,
                mcp_parameters=mcp_parameters
            )
            
            candidates.append(candidate)
        
        # Sort by MCP score (highest first)
        candidates.sort(key=lambda c: c.mcp_score, reverse=True)
        
        return candidates
    
    def _calculate_mcp_score(self, function: FunctionCandidate) -> float:
        """
        Calculate how suitable a function is for MCP tool conversion
        
        Args:
            function: Function to evaluate
            
        Returns:
            Score from 0.0 to 10.0 (higher is better for MCP conversion)
        """
        score = 5.0  # Base score
        
        # Boost for good documentation
        if function.docstring:
            docstring_quality = len(function.docstring.split())
            if docstring_quality > 10:
                score += 2.0
            elif docstring_quality > 5:
                score += 1.0
            
            # Extra boost for parameter documentation
            if 'param' in function.docstring.lower() or 'arg' in function.docstring.lower():
                score += 1.0
            
            # Extra boost for return documentation  
            if 'return' in function.docstring.lower() or 'yield' in function.docstring.lower():
                score += 0.5
        else:
            score -= 2.0  # Penalty for no docstring
        
        # Boost for reasonable parameter count (2-6 parameters ideal for MCP tools)
        param_count = len(function.parameters)
        if 2 <= param_count <= 6:
            score += 1.0
        elif param_count > 10:
            score -= 1.0
        
        # Boost for type hints
        typed_params = sum(1 for p in function.parameters if p.type_hint)
        type_coverage = typed_params / max(len(function.parameters), 1)
        score += type_coverage * 1.0
        
        # Boost for return type hint
        if function.return_type:
            score += 0.5
        
        # Penalty for overly complex functions (heuristic based on source length)
        if len(function.source_code) > 1000:
            score -= 1.0
        elif len(function.source_code) < 50:
            score -= 0.5  # Too trivial
        
        # Boost for functions that look like utilities or data processors
        name_lower = function.function_name.lower()
        utility_keywords = ['process', 'parse', 'convert', 'transform', 'validate', 'format', 'generate', 'calculate']
        if any(keyword in name_lower for keyword in utility_keywords):
            score += 1.0
        
        # Penalty for overly generic names
        generic_names = ['main', 'run', 'execute', 'handler', 'callback']
        if any(name in name_lower for name in generic_names):
            score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _generate_tool_description(self, function: FunctionCandidate) -> str:
        """Generate a description for the MCP tool based on the function"""
        
        # Use docstring if available
        if function.docstring:
            # Clean up the docstring - take the first paragraph
            lines = function.docstring.strip().split('\n')
            description = lines[0].strip()
            
            # If it's too short, try to add more context
            if len(description) < 20 and len(lines) > 1:
                description += " " + lines[1].strip()
            
            return description
        
        # Generate description from function name and signature
        name_words = re.sub(r'[_-]', ' ', function.function_name)
        name_words = re.sub(r'([a-z])([A-Z])', r'\1 \2', name_words)
        
        if function.parameters:
            param_names = [p.name for p in function.parameters[:3]]  # First 3 params
            param_str = ', '.join(param_names)
            if len(function.parameters) > 3:
                param_str += ", ..."
            description = f"Function to {name_words.lower()} with parameters: {param_str}"
        else:
            description = f"Function to {name_words.lower()}"
        
        return description
    
    def _generate_mcp_parameters(self, function: FunctionCandidate) -> Dict[str, any]:
        """Generate MCP parameter schema from function parameters"""
        
        if not function.parameters:
            return {}
        
        properties = {}
        required = []
        
        for param in function.parameters:
            param_schema = {
                "type": self._python_type_to_json_schema(param.type_hint),
                "description": param.description or f"Parameter {param.name}"
            }
            
            if param.default_value:
                param_schema["default"] = param.default_value
            
            properties[param.name] = param_schema
            
            if param.required:
                required.append(param.name)
        
        schema = {
            "type": "object",
            "properties": properties
        }
        
        if required:
            schema["required"] = required
        
        return schema
    
    def _python_type_to_json_schema(self, type_hint: Optional[str]) -> str:
        """Convert type hint to JSON schema type (supports Python and JavaScript types)"""
        if not type_hint:
            return "string"  # Default fallback
        
        type_hint = type_hint.lower()
        
        # Python types
        if 'str' in type_hint or 'string' in type_hint:
            return "string"
        elif 'int' in type_hint or 'integer' in type_hint:
            return "integer"
        elif 'float' in type_hint or 'number' in type_hint:
            return "number"
        elif 'bool' in type_hint or 'boolean' in type_hint:
            return "boolean"
        elif 'list' in type_hint or 'sequence' in type_hint or 'array' in type_hint:
            return "array"
        elif 'dict' in type_hint or 'object' in type_hint:
            return "object"
        else:
            return "string"  # Safe fallback
    
    def _infer_docker_requirements(self, function: FunctionCandidate) -> List[str]:
        """Infer basic Docker/Python package requirements from function source"""
        requirements = set()
        source = function.source_code.lower()
        
        # Common patterns for package usage
        package_patterns = {
            'requests': r'\brequests\.',
            'pandas': r'\bpd\.|pandas\.',
            'numpy': r'\bnp\.|numpy\.',
            'json': r'\bjson\.',
            'yaml': r'yaml\.',
            'sqlite3': r'sqlite3\.',
            'csv': r'\bcsv\.',
            'xml': r'\bxml\.',
            'datetime': r'datetime\.',
            'pathlib': r'pathlib\.|Path\(',
        }
        
        for package, pattern in package_patterns.items():
            if re.search(pattern, source):
                requirements.add(package)
        
        return sorted(list(requirements))
    
    def save_result(self, result: AnalysisResult, output_path: str):
        """Save analysis result to JSON file"""
        with open(output_path, 'w') as f:
            f.write(result.to_json())
        
        print(f"Analysis result saved to: {output_path}")


def main():
    """CLI entry point for testing"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python repository_analyzer.py <repository_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    analyzer = RepositoryAnalyzer()
    
    try:
        result = analyzer.analyze_repository(repo_path)
        
        # Print summary
        print(f"\nAnalysis Summary:")
        print(f"Repository: {result.repository}")
        print(f"Files analyzed: {result.analyzed_files}")
        print(f"Languages: {', '.join(result.languages)}")
        print(f"MCP tool candidates: {len(result.candidates)}")
        print(f"Security summary: {result.security_summary}")
        
        # Save result
        output_file = f"analysis_result_{Path(repo_path).name}.json"
        analyzer.save_result(result, output_file)
        
    except Exception as e:
        print(f"Error analyzing repository: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()