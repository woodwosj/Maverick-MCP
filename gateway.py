#!/usr/bin/env python3
"""
MCP Gateway Server - Unified API endpoint for Docker-hosted MCP servers
"""

import asyncio
import json
import subprocess
import time
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
        
        process = subprocess.Popen(
            docker_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        server_proc = ServerProcess(
            process=process,
            server_id=server_id,
            started_at=datetime.now(),
            last_used=time.time()
        )
        
        self.active_processes[server_id] = server_proc
        
        # Wait for initialization
        self._initialize_connection(server_proc)
        
        return server_proc
    
    def _initialize_connection(self, server_proc: ServerProcess):
        """Send initialization message to MCP server"""
        init_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-gateway",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        response = self.send_message(server_proc, init_message)
        logger.info(f"Server {server_proc.server_id} initialized: {response}")
        
        # Send initialized notification
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        server_proc.process.stdin.write(json.dumps(initialized_msg) + "\n")
        server_proc.process.stdin.flush()
    
    def send_message(self, server_proc: ServerProcess, message: dict) -> dict:
        """Send JSON-RPC message to server and get response"""
        server_proc.last_used = time.time()
        
        # Send message
        msg_str = json.dumps(message)
        logger.debug(f"Sending to {server_proc.server_id}: {msg_str}")
        server_proc.process.stdin.write(msg_str + "\n")
        server_proc.process.stdin.flush()
        
        # Read response
        response_line = server_proc.process.stdout.readline()
        if not response_line:
            raise Exception(f"No response from server {server_proc.server_id}")
        
        response = json.loads(response_line)
        logger.debug(f"Received from {server_proc.server_id}: {response}")
        
        return response
    
    def terminate_container(self, server_id: str):
        """Terminate a Docker container"""
        if server_id in self.active_processes:
            server_proc = self.active_processes[server_id]
            logger.info(f"Terminating container for {server_id}")
            server_proc.process.terminate()
            server_proc.process.wait(timeout=5)
            del self.active_processes[server_id]
    
    def get_or_spawn(self, server_id: str, config: dict) -> ServerProcess:
        """Get existing process or spawn new one"""
        if server_id not in self.active_processes:
            return self.spawn_container(server_id, config)
        return self.active_processes[server_id]

class MCPGateway:
    """Main gateway server that routes requests to Docker-hosted MCP servers"""
    
    def __init__(self, registry_path: str = "servers.yaml"):
        self.mcp = FastMCP("MCP Gateway")
        self.bridge = DockerBridge()
        self.registry_path = Path(registry_path)
        self.server_registry = self._load_registry()
        self.idle_monitor_task = None
        self._request_counter = 1000
        
        # Register gateway tools
        self._register_tools()
    
    def _load_registry(self) -> dict:
        """Load server configurations from YAML file"""
        if not self.registry_path.exists():
            logger.warning(f"Registry file {self.registry_path} not found, using empty registry")
            return {}
        
        with open(self.registry_path) as f:
            return yaml.safe_load(f) or {}
    
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
        
        @self.mcp.tool
        async def stop_server(server_id: str) -> dict:
            """Manually stop a running MCP server"""
            if server_id in self.bridge.active_processes:
                self.bridge.terminate_container(server_id)
                return {"status": "stopped", "server_id": server_id}
            return {"status": "not_running", "server_id": server_id}
    
    async def idle_monitor(self):
        """Background task to shutdown idle containers"""
        while True:
            try:
                current_time = time.time()
                servers_to_stop = []
                
                for server_id, server_proc in self.bridge.active_processes.items():
                    config = self.server_registry.get(server_id, {})
                    idle_timeout = config.get("idle_timeout", 300)  # Default 5 minutes
                    
                    if current_time - server_proc.last_used > idle_timeout:
                        servers_to_stop.append(server_id)
                
                for server_id in servers_to_stop:
                    logger.info(f"Shutting down idle server: {server_id}")
                    self.bridge.terminate_container(server_id)
                
            except Exception as e:
                logger.error(f"Error in idle monitor: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    def start(self):
        """Start the gateway server"""
        # Start idle monitor in background
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.idle_monitor_task = loop.create_task(self.idle_monitor())
        
        # Run FastMCP server (this blocks)
        logger.info("Starting MCP Gateway on port 8000")
        self.mcp.run(transport="http", port=8000, host="0.0.0.0")
    
    def cleanup(self):
        """Cleanup all running containers"""
        logger.info("Cleaning up all containers")
        for server_id in list(self.bridge.active_processes.keys()):
            self.bridge.terminate_container(server_id)
        
        if self.idle_monitor_task:
            self.idle_monitor_task.cancel()

def main():
    gateway = MCPGateway()
    
    try:
        gateway.start()
    except KeyboardInterrupt:
        logger.info("Shutting down gateway")
    finally:
        gateway.cleanup()

if __name__ == "__main__":
    main()