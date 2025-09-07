"""
Main Dockerfile generator with template system
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Optional Jinja2 import
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

# Import from analyzer
import sys
sys.path.append(str(Path(__file__).parent.parent))
from analyzer.models import MCPToolCandidate, AnalysisResult

from .dependency_resolver import DependencyResolver
from .server_wrapper_generator import ServerWrapperGenerator
from .documentation_generator import DocumentationGenerator


class DockerfileGenerator:
    """
    Template-based Dockerfile generator for MCP servers
    """
    
    SUPPORTED_LANGUAGES = {
        'python': {
            'base_image': 'python:3.11-slim',
            'package_manager': 'pip',
            'package_file': 'requirements.txt',
            'server_file': 'mcp_server.py'
        },
        'javascript': {
            'base_image': 'node:18-alpine',
            'package_manager': 'npm',
            'package_file': 'package.json',
            'server_file': 'mcp_server.js'
        },
        'go': {
            'base_image': 'golang:1.21-alpine',
            'package_manager': 'go',
            'package_file': 'go.mod',
            'server_file': 'mcp_server.go'
        }
    }
    
    def __init__(self, template_dir: Optional[str] = None):
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        
        self.template_dir = Path(template_dir)
        self.dependency_resolver = DependencyResolver()
        self.server_wrapper_generator = ServerWrapperGenerator()
        self.documentation_generator = DocumentationGenerator()
        
        # Initialize Jinja2 environment if available
        if HAS_JINJA2:
            self.env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # Add custom filters
            self.env.filters['sanitize_name'] = self._sanitize_name
            self.env.filters['quote_list'] = self._quote_list
        else:
            self.env = None
    
    def generate_mcp_server_package(
        self,
        candidates: List[MCPToolCandidate],
        server_name: str,
        repo_info: Dict[str, Any],
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Generate complete MCP server package with Dockerfile and server wrapper
        
        Args:
            candidates: List of MCP tool candidates
            server_name: Name for the generated server
            repo_info: Repository information
            output_dir: Directory to save generated files
            
        Returns:
            Dictionary with generation results and file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Determine primary language
        language = self._determine_primary_language(candidates)
        
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        # Build generation context
        context = self._build_generation_context(
            candidates, language, server_name, repo_info
        )
        
        generated_files = {}
        
        # Generate Dockerfile
        dockerfile_content = self._generate_dockerfile(language, context)
        dockerfile_path = output_path / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)
        generated_files['dockerfile'] = str(dockerfile_path)
        
        # Generate package requirements file
        requirements_content = self._generate_requirements_file(language, context)
        requirements_file = self.SUPPORTED_LANGUAGES[language]['package_file']
        requirements_path = output_path / requirements_file
        requirements_path.write_text(requirements_content)
        generated_files['requirements'] = str(requirements_path)
        
        # Generate MCP server wrapper
        server_content = self.server_wrapper_generator.generate_wrapper(
            language, candidates, server_name, repo_info
        )
        server_file = self.SUPPORTED_LANGUAGES[language]['server_file']
        server_path = output_path / server_file
        server_path.write_text(server_content)
        generated_files['server'] = str(server_path)
        
        # Generate original functions file
        functions_content = self._extract_original_functions(candidates, language)
        functions_file = f"original_functions.{self._get_file_extension(language)}"
        functions_path = output_path / functions_file
        functions_path.write_text(functions_content)
        generated_files['functions'] = str(functions_path)
        
        # Generate .dockerignore
        dockerignore_content = self._generate_dockerignore(language)
        dockerignore_path = output_path / ".dockerignore"
        dockerignore_path.write_text(dockerignore_content)
        generated_files['dockerignore'] = str(dockerignore_path)
        
        # Generate comprehensive README
        readme_content = self.documentation_generator.generate_readme(
            candidates, server_name, repo_info, language
        )
        readme_path = output_path / "README.md"
        readme_path.write_text(readme_content)
        generated_files['readme'] = str(readme_path)
        
        # Generate integration guide
        integration_content = self.documentation_generator.generate_integration_guide(
            server_name, repo_info, candidates
        )
        integration_path = output_path / "INTEGRATION.md"
        integration_path.write_text(integration_content)
        generated_files['integration'] = str(integration_path)
        
        # Generate deployment guide
        deployment_content = self.documentation_generator.generate_deployment_guide(
            server_name, candidates
        )
        deployment_path = output_path / "DEPLOYMENT.md"
        deployment_path.write_text(deployment_content)
        generated_files['deployment'] = str(deployment_path)
        
        # Generate enhanced servers.yaml entry
        servers_entry = self.documentation_generator.generate_servers_yaml_entry(
            server_name, repo_info, candidates
        )
        servers_path = output_path / "servers_entry.yaml"
        servers_path.write_text(servers_entry)
        generated_files['servers_entry'] = str(servers_path)
        
        return {
            'server_name': server_name,
            'language': language,
            'generated_files': generated_files,
            'context': context,
            'total_functions': len(candidates),
            'generation_time': datetime.now().isoformat()
        }
    
    def _determine_primary_language(self, candidates: List[MCPToolCandidate]) -> str:
        """Determine the primary language from candidates"""
        language_counts = {}
        for candidate in candidates:
            lang = candidate.function.language
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        # Return the most common language
        return max(language_counts.items(), key=lambda x: x[1])[0]
    
    def _build_generation_context(
        self,
        candidates: List[MCPToolCandidate],
        language: str,
        server_name: str,
        repo_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context dictionary for template rendering"""
        
        lang_config = self.SUPPORTED_LANGUAGES[language]
        dependencies = self.dependency_resolver.resolve_dependencies(candidates, language)
        
        # Calculate security level
        security_warnings = sum(len(c.security_warnings) for c in candidates)
        high_risk_count = sum(1 for c in candidates if any("HIGH RISK" in w for w in c.security_warnings))
        security_level = "high" if high_risk_count > 0 else ("medium" if security_warnings > 0 else "low")
        
        context = {
            # Basic info
            'server_name': server_name,
            'language': language,
            'base_image': lang_config['base_image'],
            'package_manager': lang_config['package_manager'],
            'package_file': lang_config['package_file'],
            'server_file': lang_config['server_file'],
            
            # Repository info
            'repo_name': repo_info.get('name', 'unknown'),
            'repo_url': repo_info.get('url', ''),
            'generation_date': datetime.now().isoformat(),
            
            # Functions and dependencies
            'candidates': candidates,
            'dependencies': dependencies,
            'function_count': len(candidates),
            
            # Security
            'security_level': security_level,
            'security_warnings': security_warnings,
            'high_risk_functions': high_risk_count,
            
            # MCP tools
            'mcp_tools': self._generate_mcp_tool_definitions(candidates),
            
            # Environment variables
            'environment_vars': self._extract_environment_vars(candidates),
            
            # File extensions
            'file_extension': self._get_file_extension(language)
        }
        
        return context
    
    def _generate_dockerfile(self, language: str, context: Dict[str, Any]) -> str:
        """Generate Dockerfile using templates"""
        if HAS_JINJA2 and self.env:
            template_name = f"{language}.dockerfile.j2"
            
            try:
                template = self.env.get_template(template_name)
                return template.render(**context)
            except Exception as e:
                # Fallback to basic template
                return self._generate_basic_dockerfile(language, context)
        else:
            # Use basic template when Jinja2 is not available
            return self._generate_basic_dockerfile(language, context)
    
    def _generate_basic_dockerfile(self, language: str, context: Dict[str, Any]) -> str:
        """Generate basic Dockerfile as fallback"""
        lang_config = self.SUPPORTED_LANGUAGES[language]
        
        if language == 'python':
            return f"""FROM {lang_config['base_image']}

WORKDIR /app

# Install Python dependencies
COPY {lang_config['package_file']} .
RUN pip install --no-cache-dir -r {lang_config['package_file']}

# Copy application files
COPY {lang_config['server_file']} .
COPY original_functions.py .

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user for security
RUN adduser --disabled-password --gecos '' mcpuser
USER mcpuser

# Run the MCP server
CMD ["python", "{lang_config['server_file']}"]
"""
        elif language == 'javascript':
            return f"""FROM {lang_config['base_image']}

WORKDIR /app

# Initialize npm and install dependencies
RUN npm init -y && npm pkg set type="module"
COPY {lang_config['package_file']} .
RUN npm install

# Copy application files
COPY {lang_config['server_file']} .
COPY original_functions.js .

# Set environment
ENV NODE_ENV=production

# Create non-root user for security
RUN adduser -D mcpuser
USER mcpuser

# Run the MCP server
CMD ["node", "{lang_config['server_file']}"]
"""
        else:
            raise ValueError(f"No basic template for language: {language}")
    
    def _generate_requirements_file(self, language: str, context: Dict[str, Any]) -> str:
        """Generate requirements/package file"""
        dependencies = context['dependencies']
        
        if language == 'python':
            return '\n'.join(dependencies) + '\n'
        elif language == 'javascript':
            deps_dict = {dep.split('==')[0] if '==' in dep else dep: "latest" for dep in dependencies}
            package_json = {
                "name": f"mcp-{context['server_name']}",
                "version": "1.0.0",
                "type": "module",
                "dependencies": deps_dict,
                "scripts": {
                    "start": f"node {context['server_file']}"
                }
            }
            return json.dumps(package_json, indent=2)
        else:
            return "# Dependencies for " + language
    
    def _extract_original_functions(self, candidates: List[MCPToolCandidate], language: str) -> str:
        """Extract original function source code"""
        if language == 'python':
            header = '"""\\nOriginal functions extracted from repository\\n"""\\n\\n'
        else:
            header = '// Original functions extracted from repository\\n\\n'
        
        functions_code = header
        
        for candidate in candidates:
            func = candidate.function
            functions_code += f"# Function: {func.function_name}\\n"
            functions_code += f"# File: {func.file_path}\\n"
            functions_code += f"# Line: {func.line_number}\\n\\n"
            functions_code += func.source_code + "\\n\\n"
        
        return functions_code
    
    def _generate_mcp_tool_definitions(self, candidates: List[MCPToolCandidate]) -> List[Dict[str, Any]]:
        """Generate MCP tool definitions for server registration"""
        tools = []
        
        for candidate in candidates:
            func = candidate.function
            tool_def = {
                'name': candidate.suggested_tool_name,
                'description': candidate.description,
                'parameters': candidate.mcp_parameters
            }
            tools.append(tool_def)
        
        return tools
    
    def _extract_environment_vars(self, candidates: List[MCPToolCandidate]) -> Dict[str, str]:
        """Extract environment variables needed by functions"""
        env_vars = {}
        
        for candidate in candidates:
            source = candidate.function.source_code.lower()
            
            # Look for common environment variable patterns
            if 'api_key' in source:
                env_vars['API_KEY'] = '${API_KEY}'
            if 'database_url' in source or 'db_url' in source:
                env_vars['DATABASE_URL'] = '${DATABASE_URL}'
            if 'secret' in source and 'key' in source:
                env_vars['SECRET_KEY'] = '${SECRET_KEY}'
        
        return env_vars
    
    def _generate_dockerignore(self, language: str) -> str:
        """Generate .dockerignore file"""
        common_ignores = [
            ".git",
            ".gitignore", 
            "README.md",
            "*.md",
            ".env*",
            "tests/",
            "test/",
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
            "node_modules/",
            ".npm/",
            "coverage/",
            ".coverage"
        ]
        
        return '\\n'.join(common_ignores)
    
    def _generate_readme(self, context: Dict[str, Any]) -> str:
        """Generate README for the MCP server"""
        return f"""# MCP Server: {context['server_name']}

Auto-generated MCP server from repository analysis.

## Overview
- **Language**: {context['language']}
- **Functions**: {context['function_count']}
- **Generated**: {context['generation_date']}
- **Security Level**: {context['security_level']}

## Available Tools
{chr(10).join(f"- **{tool['name']}**: {tool['description']}" for tool in context['mcp_tools'])}

## Build and Run

```bash
# Build the Docker image
docker build -t mcp-{context['server_name']} .

# Run the container (for testing - MCP servers typically run via gateway)
docker run -i mcp-{context['server_name']}
```

## Integration with MCP Gateway

Add this server to your `servers.yaml`:

```yaml
{context['server_name']}:
  image: "mcp-{context['server_name']}"
  command: ["{context['package_manager']}", "{context['server_file']}"]
  description: "Auto-generated from {context['repo_name']}"
  idle_timeout: 300
```

## Security Notes
- Security level: {context['security_level']}
- Functions with warnings: {context['security_warnings']}
- High-risk functions: {context['high_risk_functions']}

Generated by MCP Gateway Repository Analyzer
"""
    
    def _generate_servers_yaml_entry(self, context: Dict[str, Any]) -> str:
        """Generate servers.yaml entry"""
        env_vars = context.get('environment_vars', {})
        env_section = ""
        if env_vars:
            env_section = "\\n  environment:"
            for key, value in env_vars.items():
                env_section += f"\\n    {key}: \"{value}\""
        
        tools_section = "\\n  tools:"
        for tool in context['mcp_tools']:
            tools_section += f"""
    - name: "{tool['name']}"
      description: "{tool['description']}"
      parameters: {json.dumps(tool['parameters'], indent=6)}"""
        
        return f"""{context['server_name']}:
  image: "mcp-{context['server_name']}"
  command: ["{context.get('runtime', 'python')}", "{context['server_file']}"]
  description: "Auto-generated from {context['repo_name']}"
  idle_timeout: 300{env_section}{tools_section}
"""
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'go': 'go'
        }
        return extensions.get(language, 'txt')
    
    def _sanitize_name(self, name: str) -> str:
        """Jinja2 filter to sanitize names"""
        import re
        return re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())
    
    def _quote_list(self, items: List[str]) -> str:
        """Jinja2 filter to quote list items"""
        return ', '.join(f'"{item}"' for item in items)