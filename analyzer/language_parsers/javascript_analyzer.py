"""
JavaScript/TypeScript code analyzer using Esprima AST parsing
"""

import re
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

try:
    import esprima
    from esprima import nodes
    HAS_ESPRIMA = True
except ImportError:
    print("Warning: esprima package not available. Using fallback regex-based parser.")
    HAS_ESPRIMA = False
    esprima = None
    nodes = None

from ..models import FunctionCandidate, FunctionParameter


class JavaScriptAnalyzer:
    """Analyzes JavaScript/TypeScript source code to extract function information"""
    
    def __init__(self):
        self.current_file = None
        self.current_source = None
    
    def analyze_file(self, file_path: str) -> List[FunctionCandidate]:
        """
        Analyze a JavaScript/TypeScript file and extract function candidates
        
        Args:
            file_path: Path to the JS/TS file
            
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
        Analyze JavaScript/TypeScript source code and extract function candidates
        
        Args:
            source: JavaScript/TypeScript source code
            file_path: Optional file path for reference
            
        Returns:
            List of function candidates
        """
        self.current_file = file_path
        self.current_source = source
        
        try:
            if HAS_ESPRIMA:
                # Try parsing as ES6 module first
                try:
                    ast = esprima.parseModule(source, 
                                            tolerant=True,
                                            attachComments=True,
                                            range=True)
                except:
                    # Fallback to script parsing for non-module code
                    ast = esprima.parseScript(source, 
                                            tolerant=True,
                                            attachComments=True,
                                            range=True)
                
                visitor = JavaScriptFunctionVisitor(source, file_path)
                return visitor.extract_functions(ast)
            else:
                # Use regex fallback parser
                fallback_parser = JavaScriptRegexParser(source, file_path)
                return fallback_parser.extract_functions()
        
        except Exception as e:
            print(f"Error parsing JavaScript/TypeScript {file_path}: {e}")
            return []


class JavaScriptFunctionVisitor:
    """Extracts function information from JavaScript/TypeScript AST"""
    
    def __init__(self, source: str, file_path: str):
        self.source = source
        self.file_path = file_path
        self.source_lines = source.split('\n')
        self.functions = []
        self.class_stack = []  # Track nested classes
    
    def extract_functions(self, ast) -> List[FunctionCandidate]:
        """Extract functions from the AST"""
        self.functions = []
        self._visit_node(ast)
        return self.functions
    
    def _visit_node(self, node):
        """Visit AST node and extract function information"""
        if not hasattr(node, 'type'):
            return
        
        # Handle different node types
        if node.type == 'Program':
            for child in getattr(node, 'body', []):
                self._visit_node(child)
                
        elif node.type == 'ClassDeclaration':
            self._visit_class(node)
            
        elif node.type == 'FunctionDeclaration':
            self._process_function_declaration(node)
            
        elif node.type == 'VariableDeclaration':
            self._visit_variable_declaration(node)
            
        elif node.type == 'ExpressionStatement':
            self._visit_expression_statement(node)
            
        elif node.type == 'ExportNamedDeclaration' or node.type == 'ExportDefaultDeclaration':
            self._visit_export_declaration(node)
            
        # Recursively visit child nodes
        for key, value in vars(node).items():
            if isinstance(value, list):
                for child in value:
                    if hasattr(child, 'type'):
                        self._visit_node(child)
            elif hasattr(value, 'type'):
                self._visit_node(value)
    
    def _visit_class(self, node):
        """Visit class declaration"""
        class_name = getattr(node, 'id', {}).get('name', 'AnonymousClass')
        self.class_stack.append(class_name)
        
        # Visit class body for methods
        class_body = getattr(node, 'body', {})
        for method in getattr(class_body, 'body', []):
            if method.type == 'MethodDefinition':
                self._process_method(method, class_name)
        
        self.class_stack.pop()
    
    def _visit_variable_declaration(self, node):
        """Visit variable declarations to find arrow functions"""
        for declarator in getattr(node, 'declarations', []):
            if hasattr(declarator, 'init') and declarator.init:
                if declarator.init.type == 'ArrowFunctionExpression':
                    func_name = getattr(declarator, 'id', {}).get('name', 'anonymous')
                    self._process_arrow_function(declarator.init, func_name)
    
    def _visit_expression_statement(self, node):
        """Visit expression statements to find function expressions"""
        expr = getattr(node, 'expression', {})
        if expr.type == 'AssignmentExpression':
            left = getattr(expr, 'left', {})
            right = getattr(expr, 'right', {})
            
            if right.type in ('FunctionExpression', 'ArrowFunctionExpression'):
                func_name = self._extract_assignment_name(left)
                if right.type == 'ArrowFunctionExpression':
                    self._process_arrow_function(right, func_name)
                else:
                    self._process_function_expression(right, func_name)
    
    def _visit_export_declaration(self, node):
        """Visit export declarations"""
        declaration = getattr(node, 'declaration', None)
        if declaration:
            if declaration.type == 'FunctionDeclaration':
                self._process_function_declaration(declaration, is_export=True)
            elif declaration.type == 'VariableDeclaration':
                # Handle export const myFunc = () => {}
                for declarator in getattr(declaration, 'declarations', []):
                    if hasattr(declarator, 'init') and declarator.init:
                        if declarator.init.type == 'ArrowFunctionExpression':
                            func_name = getattr(declarator, 'id', {}).get('name', 'anonymous')
                            self._process_arrow_function(declarator.init, func_name, is_export=True)
    
    def _process_function_declaration(self, node, is_export=False):
        """Process function declaration"""
        func_name = getattr(node, 'id', {}).get('name', 'anonymous')
        
        # Skip if private function (starting with _) and no substantial docs
        if func_name.startswith('_') and not self._has_substantial_jsdoc(node):
            return
        
        self._create_function_candidate(node, func_name, is_export=is_export)
    
    def _process_method(self, node, class_name):
        """Process class method"""
        method_key = getattr(node, 'key', {})
        method_name = getattr(method_key, 'name', 'anonymous')
        func_node = getattr(node, 'value', {})
        
        # Skip private methods unless they have good docs
        if method_name.startswith('_') and not self._has_substantial_jsdoc(func_node):
            return
        
        self._create_function_candidate(func_node, method_name, class_name=class_name)
    
    def _process_arrow_function(self, node, func_name, is_export=False):
        """Process arrow function"""
        if func_name.startswith('_') and not self._has_substantial_jsdoc(node):
            return
        
        self._create_function_candidate(node, func_name, is_arrow=True, is_export=is_export)
    
    def _process_function_expression(self, node, func_name):
        """Process function expression"""
        if func_name.startswith('_') and not self._has_substantial_jsdoc(node):
            return
        
        self._create_function_candidate(node, func_name)
    
    def _create_function_candidate(self, node, func_name, class_name=None, is_arrow=False, is_export=False):
        """Create a FunctionCandidate from the AST node"""
        
        # Extract function source code
        source_code = self._extract_function_source(node)
        
        # Extract JSDoc comment
        docstring = self._extract_jsdoc(node)
        
        # Extract parameters
        parameters = self._extract_parameters(node)
        
        # Extract return type (TypeScript)
        return_type = self._extract_return_type(node)
        
        # Determine if async
        is_async = getattr(node, 'async', False)
        
        # Get line number
        line_number = getattr(node, 'loc', {}).get('start', {}).get('line', 1)
        
        # Create function candidate
        function = FunctionCandidate(
            function_name=func_name,
            file_path=self.file_path,
            language='javascript',
            line_number=line_number,
            source_code=source_code,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type,
            class_name=class_name,
            module_name=self._extract_module_name()
        )
        
        self.functions.append(function)
    
    def _extract_function_source(self, node) -> str:
        """Extract the complete source code for a function"""
        try:
            # Get the range from the AST node
            node_range = getattr(node, 'range', None)
            if node_range:
                start_idx, end_idx = node_range
                return self.source[start_idx:end_idx]
            
            # Fallback: try to extract based on line numbers
            loc = getattr(node, 'loc', {})
            start_line = loc.get('start', {}).get('line', 1)
            end_line = loc.get('end', {}).get('line', start_line)
            
            if start_line and end_line:
                # Convert to 0-based indexing
                start_idx = start_line - 1
                end_idx = end_line
                
                function_lines = self.source_lines[start_idx:end_idx]
                return '\n'.join(function_lines)
                
        except Exception:
            pass
        
        # Final fallback
        return f"function {getattr(node, 'id', {}).get('name', 'anonymous')}() {{ /* source extraction failed */ }}"
    
    def _extract_jsdoc(self, node) -> Optional[str]:
        """Extract JSDoc comment from function"""
        # Try to find leading comments
        comments = getattr(node, 'leadingComments', [])
        for comment in comments:
            comment_value = getattr(comment, 'value', '')
            if comment_value.startswith('*'):
                # This is likely a JSDoc comment
                return self._clean_jsdoc(comment_value)
        
        return None
    
    def _clean_jsdoc(self, jsdoc_raw: str) -> str:
        """Clean JSDoc comment for better readability"""
        lines = jsdoc_raw.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove leading * and whitespace
            clean_line = re.sub(r'^\s*\*\s?', '', line.strip())
            if clean_line:
                cleaned_lines.append(clean_line)
        
        return '\n'.join(cleaned_lines)
    
    def _has_substantial_jsdoc(self, node) -> bool:
        """Check if function has substantial JSDoc documentation"""
        docstring = self._extract_jsdoc(node)
        if not docstring:
            return False
        
        # Consider it substantial if it mentions parameters, returns, or has multiple lines
        return (len(docstring.split('\n')) > 1 or 
                any(keyword in docstring.lower() for keyword in ['@param', '@return', '@arg', 'param:', 'return:']))
    
    def _extract_parameters(self, node) -> List[FunctionParameter]:
        """Extract function parameters with type information"""
        parameters = []
        
        params = getattr(node, 'params', [])
        
        for param in params:
            param_info = self._parse_parameter(param)
            if param_info:
                parameters.append(param_info)
        
        return parameters
    
    def _parse_parameter(self, param) -> Optional[FunctionParameter]:
        """Parse individual parameter"""
        param_type = getattr(param, 'type', '')
        
        if param_type == 'Identifier':
            # Simple parameter: function(param)
            param_name = getattr(param, 'name', 'unknown')
            return FunctionParameter(
                name=param_name,
                type_hint=None,
                required=True
            )
        
        elif param_type == 'AssignmentPattern':
            # Parameter with default value: function(param = default)
            left = getattr(param, 'left', {})
            right = getattr(param, 'right', {})
            
            param_name = getattr(left, 'name', 'unknown')
            default_value = self._extract_default_value(right)
            
            return FunctionParameter(
                name=param_name,
                type_hint=None,
                default_value=default_value,
                required=False
            )
        
        elif param_type == 'RestElement':
            # Rest parameter: function(...args)
            argument = getattr(param, 'argument', {})
            param_name = getattr(argument, 'name', 'unknown')
            return FunctionParameter(
                name=f"...{param_name}",
                type_hint='Array',
                required=False
            )
        
        elif param_type == 'ObjectPattern':
            # Destructured object parameter: function({a, b})
            return FunctionParameter(
                name="destructured_object",
                type_hint='Object',
                required=True
            )
        
        elif param_type == 'ArrayPattern':
            # Destructured array parameter: function([a, b])
            return FunctionParameter(
                name="destructured_array",
                type_hint='Array',
                required=True
            )
        
        return None
    
    def _extract_default_value(self, default_node) -> str:
        """Extract default value as string"""
        if not default_node:
            return "undefined"
        
        node_type = getattr(default_node, 'type', '')
        
        if node_type == 'Literal':
            value = getattr(default_node, 'value', None)
            if isinstance(value, str):
                return f'"{value}"'
            return str(value)
        
        elif node_type == 'Identifier':
            return getattr(default_node, 'name', 'undefined')
        
        elif node_type == 'ArrayExpression':
            return "[]"
        
        elif node_type == 'ObjectExpression':
            return "{}"
        
        return "undefined"
    
    def _extract_return_type(self, node) -> Optional[str]:
        """Extract return type hint (TypeScript)"""
        # TypeScript return type annotation
        return_type = getattr(node, 'returnType', None)
        if return_type:
            # This would be a TypeScript type annotation
            return str(return_type)
        
        return None
    
    def _extract_assignment_name(self, left_node) -> str:
        """Extract function name from assignment expression"""
        if getattr(left_node, 'type', '') == 'Identifier':
            return getattr(left_node, 'name', 'anonymous')
        
        elif getattr(left_node, 'type', '') == 'MemberExpression':
            # Handle cases like module.exports.funcName or obj.method
            property_node = getattr(left_node, 'property', {})
            return getattr(property_node, 'name', 'anonymous')
        
        return 'anonymous'
    
    def _extract_module_name(self) -> Optional[str]:
        """Extract module name from file path"""
        if not self.file_path:
            return None
        
        path = Path(self.file_path)
        return path.stem


class JavaScriptRegexParser:
    """Fallback regex-based JavaScript parser when esprima is not available"""
    
    def __init__(self, source: str, file_path: str):
        self.source = source
        self.file_path = file_path
        self.source_lines = source.split('\n')
        
    def extract_functions(self) -> List[FunctionCandidate]:
        """Extract functions using regex patterns"""
        functions = []
        
        # Function declaration patterns
        patterns = [
            # Regular function declarations: function name(params) { }
            (r'function\s+(\w+)\s*\(([^)]*)\)\s*\{', 'function'),
            # Arrow functions assigned to variables: const name = (params) => { }
            (r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=])\s*=>', 'arrow'),
            # Export function declarations: export function name(params) { }
            (r'export\s+function\s+(\w+)\s*\(([^)]*)\)\s*\{', 'export_function'),
            # Export arrow functions: export const name = (params) => { }
            (r'export\s+(?:const|let)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=])\s*=>', 'export_arrow'),
        ]
        
        for pattern, func_type in patterns:
            matches = re.finditer(pattern, self.source, re.MULTILINE)
            
            for match in matches:
                func_name = match.group(1)
                
                # Skip private functions
                if func_name.startswith('_'):
                    continue
                
                # Try to extract parameters
                params_str = match.group(2) if match.lastindex >= 2 else ""
                parameters = self._parse_parameters_regex(params_str)
                
                # Find line number
                line_num = self.source[:match.start()].count('\n') + 1
                
                # Extract function source (basic approximation)
                source_code = self._extract_function_source_regex(match, func_type)
                
                # Extract JSDoc comment if present
                docstring = self._extract_jsdoc_regex(match.start())
                
                function = FunctionCandidate(
                    function_name=func_name,
                    file_path=self.file_path,
                    language='javascript',
                    line_number=line_num,
                    source_code=source_code,
                    docstring=docstring,
                    parameters=parameters,
                    return_type=None,  # Hard to detect with regex
                    class_name=None,   # Hard to detect with regex
                    module_name=Path(self.file_path).stem if self.file_path else None
                )
                
                functions.append(function)
        
        # Deduplicate functions by name and file_path
        unique_functions = []
        seen = set()
        
        for func in functions:
            key = (func.function_name, func.file_path)
            if key not in seen:
                seen.add(key)
                unique_functions.append(func)
        
        return unique_functions
    
    def _parse_parameters_regex(self, params_str: str) -> List[FunctionParameter]:
        """Parse parameter string using regex"""
        if not params_str.strip():
            return []
        
        parameters = []
        # Simple parameter parsing - split by comma
        param_parts = [p.strip() for p in params_str.split(',') if p.strip()]
        
        for param_part in param_parts:
            # Handle default values: param = default
            if '=' in param_part:
                param_name = param_part.split('=')[0].strip()
                default_val = param_part.split('=', 1)[1].strip()
                parameters.append(FunctionParameter(
                    name=param_name,
                    type_hint=None,
                    default_value=default_val,
                    required=False
                ))
            else:
                # Handle destructuring and rest parameters
                if param_part.startswith('...'):
                    param_name = param_part[3:].strip()
                    parameters.append(FunctionParameter(
                        name=f"...{param_name}",
                        type_hint='Array',
                        required=False
                    ))
                elif param_part.startswith('{') or param_part.startswith('['):
                    # Destructured parameters
                    parameters.append(FunctionParameter(
                        name="destructured_param",
                        type_hint='Object' if param_part.startswith('{') else 'Array',
                        required=True
                    ))
                else:
                    parameters.append(FunctionParameter(
                        name=param_part,
                        type_hint=None,
                        required=True
                    ))
        
        return parameters
    
    def _extract_function_source_regex(self, match, func_type: str) -> str:
        """Extract function source code using basic heuristics"""
        start_pos = match.start()
        
        # Find the opening brace
        open_brace = self.source.find('{', start_pos)
        if open_brace == -1:
            # Might be an arrow function without braces
            line_end = self.source.find('\n', start_pos)
            if line_end == -1:
                return self.source[start_pos:]
            return self.source[start_pos:line_end]
        
        # Find matching closing brace
        brace_count = 0
        pos = open_brace
        
        while pos < len(self.source):
            if self.source[pos] == '{':
                brace_count += 1
            elif self.source[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return self.source[start_pos:pos + 1]
            pos += 1
        
        # Fallback: return until end of file or reasonable limit
        end_pos = min(start_pos + 1000, len(self.source))
        return self.source[start_pos:end_pos]
    
    def _extract_jsdoc_regex(self, func_start_pos: int) -> Optional[str]:
        """Extract JSDoc comment before function using regex"""
        # Look backward for JSDoc comment
        before_func = self.source[:func_start_pos]
        
        # Find the last JSDoc comment before this position
        jsdoc_pattern = r'/\*\*.*?\*/'
        matches = list(re.finditer(jsdoc_pattern, before_func, re.DOTALL))
        
        if matches:
            last_match = matches[-1]
            # Check if it's close to the function (within a few lines)
            lines_between = before_func[last_match.end():].count('\n')
            if lines_between <= 3:  # Allow up to 3 lines between comment and function
                comment_text = last_match.group(0)
                # Clean up the comment
                return self._clean_jsdoc_regex(comment_text)
        
        return None
    
    def _clean_jsdoc_regex(self, jsdoc_raw: str) -> str:
        """Clean JSDoc comment for better readability"""
        # Remove /** and */ wrapper
        content = jsdoc_raw[3:-2] if jsdoc_raw.startswith('/**') else jsdoc_raw[2:-2]
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove leading * and whitespace
            clean_line = re.sub(r'^\s*\*\s?', '', line.strip())
            if clean_line:
                cleaned_lines.append(clean_line)
        
        return '\n'.join(cleaned_lines)