"""
Python code analyzer using AST parsing
"""

import ast
import inspect
from typing import List, Optional, Dict, Any
from pathlib import Path
import re

from ..models import FunctionCandidate, FunctionParameter


class PythonAnalyzer:
    """Analyzes Python source code to extract function information"""
    
    def __init__(self):
        self.current_file = None
        self.current_source = None
    
    def analyze_file(self, file_path: str) -> List[FunctionCandidate]:
        """
        Analyze a Python file and extract function candidates
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List of function candidates found in the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            return self.analyze_source(source, file_path)
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []
    
    def analyze_source(self, source: str, file_path: str = "") -> List[FunctionCandidate]:
        """
        Analyze Python source code and extract function candidates
        
        Args:
            source: Python source code
            file_path: Optional file path for reference
            
        Returns:
            List of function candidates
        """
        self.current_file = file_path
        self.current_source = source
        
        try:
            tree = ast.parse(source)
            visitor = PythonFunctionVisitor(source, file_path)
            visitor.visit(tree)
            return visitor.functions
        
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []


class PythonFunctionVisitor(ast.NodeVisitor):
    """AST visitor to extract function information"""
    
    def __init__(self, source: str, file_path: str):
        self.source = source
        self.file_path = file_path
        self.source_lines = source.split('\n')
        self.functions = []
        self.class_stack = []  # Track nested classes
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Track class context for methods"""
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Extract function definition information"""
        self._process_function(node)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Extract async function definition information"""
        self._process_function(node, is_async=True)
        self.generic_visit(node)
    
    def _process_function(self, node: ast.FunctionDef, is_async: bool = False):
        """Process a function or method definition"""
        
        # Skip private functions (starting with _) unless they have good docstrings
        if node.name.startswith('_') and not self._has_substantial_docstring(node):
            return
        
        # Extract function source code
        source_code = self._extract_function_source(node)
        
        # Extract docstring
        docstring = self._extract_docstring(node)
        
        # Extract parameters
        parameters = self._extract_parameters(node)
        
        # Extract return type hint
        return_type = self._extract_return_type(node)
        
        # Determine class context
        class_name = self.class_stack[-1] if self.class_stack else None
        
        # Create function candidate
        function = FunctionCandidate(
            function_name=node.name,
            file_path=self.file_path,
            language='python',
            line_number=node.lineno,
            source_code=source_code,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type,
            class_name=class_name,
            module_name=self._extract_module_name()
        )
        
        self.functions.append(function)
    
    def _extract_function_source(self, node: ast.FunctionDef) -> str:
        """Extract the complete source code for a function"""
        try:
            # Calculate the end line by finding the next function/class or end of file
            end_line = len(self.source_lines)
            
            # Find the next top-level definition after this function
            for other_node in ast.walk(ast.parse(self.source)):
                if (isinstance(other_node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and
                    other_node != node and 
                    other_node.lineno > node.lineno):
                    end_line = min(end_line, other_node.lineno - 1)
            
            # Extract the function source
            start_line = node.lineno - 1  # Convert to 0-based indexing
            function_lines = self.source_lines[start_line:end_line]
            
            # Remove trailing empty lines
            while function_lines and not function_lines[-1].strip():
                function_lines.pop()
            
            return '\n'.join(function_lines)
        
        except Exception:
            # Fallback: return just the function signature
            return f"def {node.name}(...):"
    
    def _extract_docstring(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract docstring from function definition"""
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value.strip()
        return None
    
    def _has_substantial_docstring(self, node: ast.FunctionDef) -> bool:
        """Check if function has a substantial docstring (more than just a title)"""
        docstring = self._extract_docstring(node)
        if not docstring:
            return False
        
        # Consider it substantial if it has multiple lines or mentions parameters/returns
        return (len(docstring.split('\n')) > 1 or 
                any(keyword in docstring.lower() for keyword in ['param', 'arg', 'return', 'yield']))
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[FunctionParameter]:
        """Extract function parameters with type hints and defaults"""
        parameters = []
        
        args = node.args
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            # Skip 'self' and 'cls' parameters
            if arg.arg in ('self', 'cls'):
                continue
                
            param = FunctionParameter(
                name=arg.arg,
                type_hint=self._extract_type_hint(arg.annotation),
                required=True
            )
            
            # Check if this parameter has a default value
            default_offset = len(args.args) - len(args.defaults)
            if i >= default_offset:
                default_index = i - default_offset
                default_value = self._extract_default_value(args.defaults[default_index])
                param.default_value = default_value
                param.required = False
            
            parameters.append(param)
        
        # Keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            param = FunctionParameter(
                name=arg.arg,
                type_hint=self._extract_type_hint(arg.annotation),
                required=True
            )
            
            # Check for default value in kw_defaults
            if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
                default_value = self._extract_default_value(args.kw_defaults[i])
                param.default_value = default_value
                param.required = False
            
            parameters.append(param)
        
        return parameters
    
    def _extract_type_hint(self, annotation) -> Optional[str]:
        """Extract type hint as string"""
        if annotation is None:
            return None
        
        try:
            return ast.unparse(annotation)
        except AttributeError:
            # Fallback for older Python versions
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Constant):
                return str(annotation.value)
            else:
                return str(annotation)
    
    def _extract_default_value(self, default_node) -> str:
        """Extract default value as string"""
        try:
            return ast.unparse(default_node)
        except AttributeError:
            # Fallback for older Python versions
            if isinstance(default_node, ast.Constant):
                return repr(default_node.value)
            elif isinstance(default_node, ast.Name):
                return default_node.id
            else:
                return str(default_node)
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type hint"""
        if node.returns:
            return self._extract_type_hint(node.returns)
        return None
    
    def _extract_module_name(self) -> Optional[str]:
        """Extract module name from file path"""
        if not self.file_path:
            return None
        
        path = Path(self.file_path)
        if path.name == '__init__.py':
            return path.parent.name
        else:
            return path.stem