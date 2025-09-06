"""
Security pattern scanner for dangerous code detection
"""

import re
from typing import List, Dict, Set
from ..models import FunctionCandidate


class SecurityScanner:
    """Scans code for potentially dangerous patterns"""
    
    # High-risk patterns that could be dangerous in MCP tools
    DANGEROUS_PATTERNS = {
        'system_commands': [
            r'os\.system\s*\(',
            r'subprocess\.',
            r'shell=True',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__\s*\('
        ],
        'file_system_access': [
            r'open\s*\(\s*[\'"][/\\]',  # Absolute paths
            r'\.\./',  # Directory traversal
            r'os\.remove\s*\(',
            r'os\.rmdir\s*\(',
            r'shutil\.rmtree\s*\(',
            r'os\.chmod\s*\(',
        ],
        'network_operations': [
            r'urllib\.request\.',
            r'requests\.',
            r'http\.client\.',
            r'socket\.',
            r'telnetlib\.',
            r'ftplib\.'
        ],
        'dangerous_modules': [
            r'import\s+pickle',
            r'from\s+pickle\s+import',
            r'import\s+marshal',
            r'import\s+ctypes',
        ],
        'credential_handling': [
            r'password\s*=',
            r'api_key\s*=',
            r'secret\s*=',
            r'token\s*=',
            r'\.env',
            r'os\.environ\['
        ]
    }
    
    # Medium-risk patterns that need careful review
    MEDIUM_RISK_PATTERNS = {
        'database_operations': [
            r'\.execute\s*\(',
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'UPDATE\s+.*\s+SET',
            r'CREATE\s+TABLE'
        ],
        'code_generation': [
            r'compile\s*\(',
            r'exec\s*\(',
            r'\.format\s*\(',  # String formatting can be dangerous
        ]
    }
    
    def __init__(self):
        self.pattern_cache = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, Dict[str, List[re.Pattern]]]:
        """Pre-compile regex patterns for better performance"""
        compiled = {}
        
        for risk_level, categories in [
            ('high', self.DANGEROUS_PATTERNS),
            ('medium', self.MEDIUM_RISK_PATTERNS)
        ]:
            compiled[risk_level] = {}
            for category, patterns in categories.items():
                compiled[risk_level][category] = [
                    re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                    for pattern in patterns
                ]
        
        return compiled
    
    def scan_function(self, function: FunctionCandidate) -> List[str]:
        """
        Scan a function for security issues
        
        Args:
            function: Function candidate to scan
            
        Returns:
            List of security warning messages
        """
        warnings = []
        source = function.source_code
        
        # Check high-risk patterns
        for category, patterns in self.pattern_cache['high'].items():
            for pattern in patterns:
                matches = pattern.findall(source)
                if matches:
                    warnings.append(
                        f"HIGH RISK ({category}): Found potentially dangerous pattern: {pattern.pattern}"
                    )
        
        # Check medium-risk patterns  
        for category, patterns in self.pattern_cache['medium'].items():
            for pattern in patterns:
                matches = pattern.findall(source)
                if matches:
                    warnings.append(
                        f"MEDIUM RISK ({category}): Pattern needs review: {pattern.pattern}"
                    )
        
        return warnings
    
    def calculate_risk_score(self, warnings: List[str]) -> float:
        """
        Calculate a risk score based on warnings
        
        Args:
            warnings: List of warning messages
            
        Returns:
            Risk score from 0.0 (safe) to 10.0 (very dangerous)
        """
        if not warnings:
            return 0.0
        
        high_risk_count = sum(1 for w in warnings if 'HIGH RISK' in w)
        medium_risk_count = sum(1 for w in warnings if 'MEDIUM RISK' in w)
        
        # High risk patterns contribute more to the score
        score = (high_risk_count * 3.0) + (medium_risk_count * 1.5)
        
        # Cap at 10.0
        return min(score, 10.0)
    
    def is_safe_for_mcp(self, function: FunctionCandidate, max_risk_score: float = 2.0) -> bool:
        """
        Determine if a function is safe enough for MCP tool conversion
        
        Args:
            function: Function to evaluate
            max_risk_score: Maximum acceptable risk score
            
        Returns:
            True if function appears safe for MCP conversion
        """
        warnings = self.scan_function(function)
        risk_score = self.calculate_risk_score(warnings)
        
        return risk_score <= max_risk_score
    
    def get_security_summary(self, functions: List[FunctionCandidate]) -> Dict[str, int]:
        """
        Generate security summary for a list of functions
        
        Args:
            functions: List of functions to analyze
            
        Returns:
            Dictionary with security statistics
        """
        total_warnings = 0
        high_risk_functions = 0
        medium_risk_functions = 0
        safe_functions = 0
        
        for func in functions:
            warnings = self.scan_function(func)
            total_warnings += len(warnings)
            
            risk_score = self.calculate_risk_score(warnings)
            if risk_score > 5.0:
                high_risk_functions += 1
            elif risk_score > 2.0:
                medium_risk_functions += 1
            else:
                safe_functions += 1
        
        return {
            'total_functions': len(functions),
            'safe_functions': safe_functions,
            'medium_risk_functions': medium_risk_functions,
            'high_risk_functions': high_risk_functions,
            'total_warnings': total_warnings
        }