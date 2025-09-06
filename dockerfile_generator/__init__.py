"""
Dockerfile Generator for MCP Server Conversion

A template-based system that generates Docker containers and MCP server wrappers
for functions identified by the Repository Analyzer.
"""

from .dockerfile_generator import DockerfileGenerator
from .dependency_resolver import DependencyResolver
from .server_wrapper_generator import ServerWrapperGenerator

__all__ = [
    'DockerfileGenerator',
    'DependencyResolver', 
    'ServerWrapperGenerator'
]

__version__ = '1.0.0'