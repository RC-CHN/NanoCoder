"""MCP Client - connects to MCP servers and calls their tools.

MCP uses JSON-RPC 2.0 over stdio (for local servers) or SSE (for remote).
This implementation supports stdio transport, which is the most common for
local MCP servers like filesystem, github, etc.
"""

import asyncio
import json
import os
import shutil
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MCPToolInfo:
    """Tool metadata from an MCP server."""
    name: str
    description: str
    input_schema: dict  # JSON Schema for parameters


class MCPClient:
    """Async client for communicating with an MCP server via stdio."""
    
    def __init__(self, config):
        """Initialize MCP client with a server configuration.
        
        Args:
            config: MCPServerConfig instance (from nanocoder.config)
        """
        self.config = config
        self._process: asyncio.subprocess.Process | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._request_id = 0
        self._tools: list[MCPToolInfo] = []
        self._initialized = False
        self._pending_requests: dict[int, asyncio.Future] = {}
        self._receive_task: asyncio.Task | None = None
    
    @property
    def tools(self) -> list[MCPToolInfo]:
        """List of tools available from this server."""
        return self._tools
    
    async def connect(self) -> bool:
        """Start the MCP server process and initialize connection."""
        # Find the command
        cmd = shutil.which(self.config.command)
        if not cmd:
            # Try common locations
            for prefix in ["/usr/local/bin", "/usr/bin", os.path.expanduser("~/.local/bin")]:
                candidate = os.path.join(prefix, self.config.command)
                if os.path.exists(candidate):
                    cmd = candidate
                    break
        
        if not cmd:
            print(f"[MCP] Cannot find command: {self.config.command}")
            return False
        
        # Build environment
        env = os.environ.copy()
        env.update(self.config.env)
        
        # Start the process
        try:
            self._process = await asyncio.create_subprocess_exec(
                cmd,
                *self.config.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=self.config.cwd,
            )
            self._reader = self._process.stdout
            self._writer = self._process.stdin
        except Exception as e:
            print(f"[MCP] Failed to start server '{self.config.name}': {e}")
            return False
        
        # Start background receiver task
        self._receive_task = asyncio.create_task(self._receive_loop())
        
        # Initialize MCP protocol
        try:
            # 1. Send initialize request
            result = await self._request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "nanocoder", "version": "0.1.0"},
            })
            
            if not result:
                print(f"[MCP] Failed to initialize server '{self.config.name}'")
                return False
            
            # 2. Send initialized notification
            await self._notify("notifications/initialized", {})
            
            # 3. List available tools
            tools_result = await self._request("tools/list", {})
            if tools_result and "tools" in tools_result:
                for t in tools_result["tools"]:
                    self._tools.append(MCPToolInfo(
                        name=t["name"],
                        description=t.get("description", ""),
                        input_schema=t.get("inputSchema", {"type": "object", "properties": {}}),
                    ))
            
            self._initialized = True
            print(f"[MCP] Connected to '{self.config.name}' with {len(self._tools)} tools")
            return True
            
        except Exception as e:
            print(f"[MCP] Initialization error: {e}")
            return False
    
    async def disconnect(self):
        """Close the connection."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self._process:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=2.0)
            except:
                try:
                    self._process.kill()
                except:
                    pass
        
        self._process = None
        self._reader = None
        self._writer = None
        self._initialized = False
    
    async def call_tool(self, name: str, arguments: dict) -> str:
        """Call a tool on the MCP server and return the result as a string."""
        if not self._initialized:
            return "Error: MCP client not connected"
        
        try:
            result = await self._request("tools/call", {
                "name": name,
                "arguments": arguments,
            })
            
            if not result:
                return "Error: No response from MCP server"
            
            # MCP returns content as a list of content items
            # Each item has a type (text, image, resource) and corresponding data
            content = result.get("content", [])
            if not content:
                return "(no output)"
            
            # Combine all text content
            text_parts = []
            for item in content:
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif item.get("type") == "resource":
                    # Resource reference
                    resource = item.get("resource", {})
                    text_parts.append(f"[Resource: {resource.get('uri', 'unknown')}]")
            
            result_text = "\n".join(text_parts)
            
            # Check for errors
            if result.get("isError"):
                return f"Error: {result_text}"
            
            return result_text or "(no output)"
            
        except Exception as e:
            return f"Error calling MCP tool: {e}"
    
    async def _request(self, method: str, params: dict) -> dict | None:
        """Send a JSON-RPC request and wait for response."""
        if not self._writer or not self._reader:
            return None
        
        self._request_id += 1
        request_id = self._request_id
        
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        
        # Create future for response
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self._pending_requests[request_id] = future
        
        # Send request
        try:
            line = json.dumps(message) + "\n"
            self._writer.write(line.encode())
            await self._writer.drain()
        except Exception as e:
            self._pending_requests.pop(request_id, None)
            print(f"[MCP] Send error: {e}")
            return None
        
        # Wait for response with timeout
        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:
            self._pending_requests.pop(request_id, None)
            print(f"[MCP] Request timeout: {method}")
            return None
    
    async def _notify(self, method: str, params: dict):
        """Send a JSON-RPC notification (no response expected)."""
        if not self._writer:
            return
        
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        
        try:
            line = json.dumps(message) + "\n"
            self._writer.write(line.encode())
            await self._writer.drain()
        except Exception as e:
            print(f"[MCP] Notify error: {e}")
    
    async def _receive_loop(self):
        """Background task to receive and route responses."""
        if not self._reader:
            return
        
        buffer = b""
        try:
            while True:
                chunk = await self._reader.read(4096)
                if not chunk:
                    break
                buffer += chunk
                
                # Process complete lines
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    
                    try:
                        message = json.loads(line.decode())
                    except json.JSONDecodeError:
                        continue
                    
                    # Route response to waiting future
                    if "id" in message and message["id"] in self._pending_requests:
                        future = self._pending_requests.pop(message["id"])
                        if not future.done():
                            if "error" in message:
                                future.set_result(None)
                            else:
                                future.set_result(message.get("result"))
                    
                    # Handle logging notifications
                    if message.get("method") == "notifications/message":
                        params = message.get("params", {})
                        level = params.get("level", "info")
                        data = params.get("data", "")
                        if level in ("error", "warning"):
                            print(f"[MCP/{self.config.name}] {level}: {data}")
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[MCP] Receive error: {e}")