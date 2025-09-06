"""
Data models for repository analysis
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json


@dataclass
class FunctionParameter:
    """Represents a function parameter"""
    name: str
    type_hint: Optional[str] = None
    description: Optional[str] = None
    default_value: Optional[str] = None
    required: bool = True


@dataclass
class FunctionCandidate:
    """Represents a function found during repository analysis"""
    function_name: str
    file_path: str
    language: str
    line_number: int
    source_code: str
    docstring: Optional[str] = None
    parameters: List[FunctionParameter] = field(default_factory=list)
    return_type: Optional[str] = None
    class_name: Optional[str] = None
    module_name: Optional[str] = None


@dataclass 
class MCPToolCandidate:
    """Analyzed function with MCP conversion metadata"""
    function: FunctionCandidate
    mcp_score: float
    description: str
    security_warnings: List[str] = field(default_factory=list)
    suggested_tool_name: str = ""
    docker_requirements: List[str] = field(default_factory=list)
    mcp_parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.suggested_tool_name:
            self.suggested_tool_name = self.function.function_name


@dataclass
class AnalysisResult:
    """Complete repository analysis result"""
    repository: str
    analyzed_files: int
    languages: List[str]
    candidates: List[MCPToolCandidate]
    security_summary: Dict[str, int] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON format"""
        data = {
            "repository": self.repository,
            "analyzed_files": self.analyzed_files,
            "languages": self.languages,
            "candidates": [
                {
                    "function_name": c.function.function_name,
                    "file_path": c.function.file_path,
                    "language": c.function.language,
                    "mcp_score": c.mcp_score,
                    "description": c.description,
                    "parameters": {
                        p.name: {
                            "type": p.type_hint,
                            "description": p.description,
                            "default": p.default_value,
                            "required": p.required
                        } for p in c.function.parameters
                    },
                    "security_warnings": c.security_warnings,
                    "suggested_tool_name": c.suggested_tool_name,
                    "docker_requirements": c.docker_requirements
                } for c in self.candidates
            ],
            "security_summary": self.security_summary
        }
        return json.dumps(data, indent=2)