#!/usr/bin/env python3
"""
Standalone STDIO MCP Gateway for Claude Code Integration
This version runs directly in STDIO mode, bypassing HTTP complications
"""

import asyncio
import json
import subprocess
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServerProcess:
    process: subprocess.Popen
    server_id: str
    started_at: datetime
    last_used: float

class DockerBridge:
    """Manages STDIO communication with Docker containers running MCP servers"""
    
    def __init__(self):
        self.active_processes: Dict[str, ServerProcess] = {}
        
    def spawn_container(self, server_id: str, config: dict) -> ServerProcess:
        """Spawn a Docker container for an MCP server"""
        image = config.get("image")
        command = config.get("command", [])
        env_vars = config.get("environment", {})
        
        docker_cmd = ["docker", "run", "-i", "--rm"]
        
        # Add environment variables
        for key, value in env_vars.items():
            docker_cmd.extend(["-e", f"{key}={value}"])
        
        docker_cmd.append(image)
        docker_cmd.extend(command)
        
        logger.info(f"Starting container for {server_id}: {' '.join(docker_cmd)}")
        
        try:
            process = subprocess.Popen(
                docker_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            server_proc = ServerProcess(
                process=process,
                server_id=server_id,
                started_at=datetime.now(),
                last_used=datetime.now().timestamp()
            )
            
            self.active_processes[server_id] = server_proc
            return server_proc
            
        except Exception as e:
            logger.error(f"Failed to spawn container for {server_id}: {e}")
            raise

    def get_or_spawn(self, server_id: str, config: dict) -> ServerProcess:
        """Get existing container or spawn new one"""
        if server_id in self.active_processes:
            server_proc = self.active_processes[server_id]
            server_proc.last_used = datetime.now().timestamp()
            return server_proc
        else:
            return self.spawn_container(server_id, config)

    def send_message(self, server_proc: ServerProcess, message: dict) -> dict:
        """Send message to container and get response"""
        try:
            json_message = json.dumps(message)
            server_proc.process.stdin.write(json_message + "\n")
            server_proc.process.stdin.flush()
            
            # Read response
            response_line = server_proc.process.stdout.readline().strip()
            if response_line:
                return json.loads(response_line)
            else:
                return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32603, "message": "No response from container"}}
                
        except Exception as e:
            logger.error(f"Error communicating with container {server_proc.server_id}: {e}")
            return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32603, "message": str(e)}}

class STDIOMCPGateway:
    """Simplified MCP Gateway for STDIO communication with Claude Code"""
    
    def __init__(self, registry_path: str = "servers.yaml"):
        self.mcp = FastMCP("MCP Gateway")
        self.bridge = DockerBridge()
        self.registry_path = Path(registry_path)
        self.server_registry = {}
        self._request_counter = 0
        
        self._load_registry()
        self._register_tools()

    def _load_registry(self):
        """Load server registry from YAML file"""
        try:
            with open(self.registry_path, 'r') as f:
                self.server_registry = yaml.safe_load(f) or {}
            logger.info(f"Loaded {len(self.server_registry)} servers from registry")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            self.server_registry = {}

    def _register_tools(self):
        """Register gateway tools with FastMCP"""
        
        @self.mcp.tool
        async def list_available_tools() -> list:
            """List all available tools from all registered MCP servers"""
            tools = []
            for server_id, config in self.server_registry.items():
                server_tools = config.get("tools", [])
                for tool in server_tools:
                    tools.append({
                        "server": server_id,
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "when_to_use": tool.get("when_to_use", ""),
                        "parameters": tool.get("parameters", {})
                    })
            return tools
        
        @self.mcp.tool
        async def execute_tool(server_id: str, tool_name: str, arguments: Optional[Any] = None) -> Any:
            """Execute a tool on a specific MCP server"""
            
            if server_id not in self.server_registry:
                raise ValueError(f"Server {server_id} not found in registry")
            
            config = self.server_registry[server_id]
            
            # Handle arguments - could be dict, string, or None
            if arguments is not None:
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        raise ValueError(f"Invalid JSON in arguments: {arguments}")
                elif not isinstance(arguments, dict):
                    raise ValueError(f"Arguments must be dict or JSON string, got {type(arguments)}")
            
            # Get or spawn container
            server_proc = self.bridge.get_or_spawn(server_id, config)
            
            # Create tool call request
            self._request_counter += 1
            request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments or {}
                },
                "id": self._request_counter
            }
            
            # Send request and get response
            response = self.bridge.send_message(server_proc, request)
            
            if "error" in response:
                raise Exception(f"Tool execution error: {response['error']}")
            
            return response.get("result", {})

        @self.mcp.tool
        async def list_active_servers() -> list:
            """List currently active (running) MCP servers"""
            active = []
            for server_id, server_proc in self.bridge.active_processes.items():
                config = self.server_registry.get(server_id, {})
                active.append({
                    "server_id": server_id,
                    "started_at": server_proc.started_at.isoformat(),
                    "last_used": datetime.fromtimestamp(server_proc.last_used).isoformat(),
                    "idle_timeout": config.get("idle_timeout", 300)
                })
            return active

    def start(self):
        """Start the MCP Gateway in STDIO mode"""
        logger.info("Starting STDIO MCP Gateway for Claude Code integration")
        # Run FastMCP server on STDIO for direct Claude Code integration
        self.mcp.run(transport="stdio")

def main():
    gateway = STDIOMCPGateway()
    
    try:
        gateway.start()
    except KeyboardInterrupt:
        logger.info("Shutting down STDIO gateway")
    except Exception as e:
        logger.error(f"Gateway error: {e}")

if __name__ == "__main__":
    main()