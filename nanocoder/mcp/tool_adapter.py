"""MCP Tool Adapter - wraps MCP tools as NanoCoder Tool instances.

This allows MCP server tools to be used seamlessly alongside built-in tools.
"""

import asyncio
import threading
import concurrent.futures
from typing import Any

from .client import MCPClient, MCPToolInfo
from ..tools.base import Tool


class MCPTool(Tool):
    """Wraps an MCP tool as a NanoCoder Tool.
    
    This adapter bridges the MCP tool protocol to NanoCoder's Tool interface.
    Since MCP uses async communication but NanoCoder's Tool.execute is sync,
    we use the manager's persistent event loop running in a background thread.
    """
    
    def __init__(self, client: MCPClient, tool_info: MCPToolInfo, loop: asyncio.AbstractEventLoop):
        self._client = client
        self._tool_info = tool_info
        self._loop = loop
        self.name = tool_info.name
        self.description = tool_info.description
        self.parameters = tool_info.input_schema
    
    def execute(self, **kwargs) -> str:
        """Execute the MCP tool. Uses the persistent background event loop."""
        if self._loop is None or not self._loop.is_running():
            return "Error: MCP event loop not running"
        
        future = asyncio.run_coroutine_threadsafe(
            self._client.call_tool(self._tool_info.name, kwargs),
            self._loop
        )
        try:
            return future.result(timeout=60.0)
        except concurrent.futures.TimeoutError:
            return "Error: MCP tool call timed out"
        except Exception as e:
            return f"Error: {e}"


class MCPToolManager:
    """Manages connections to multiple MCP servers and aggregates their tools.
    
    Uses a background thread with a persistent event loop to handle MCP async IO.
    """
    
    def __init__(self):
        self._clients: list[MCPClient] = []
        self._tools: list[MCPTool] = []
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._started = False
    
    def start(self):
        """Start the background event loop thread."""
        if self._started:
            return
        
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._started = True
        
        # Wait for loop to be running
        while not self._loop.is_running():
            import time
            time.sleep(0.01)
    
    def _run_loop(self):
        """Run the event loop in background thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
    
    def stop(self):
        """Stop the background event loop."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2.0)
        self._started = False
    
    @property
    def tools(self) -> list[MCPTool]:
        """All tools from all connected MCP servers."""
        return self._tools
    
    def connect_server(self, config) -> bool:
        """Connect to an MCP server and load its tools (sync wrapper).
        
        Args:
            config: MCPServerConfig instance (from nanocoder.config)
            
        Returns:
            True if connection succeeded
        """
        if not self._started:
            self.start()
        
        client = MCPClient(config)
        
        # Run async connect in the background loop
        future = asyncio.run_coroutine_threadsafe(client.connect(), self._loop)
        try:
            success = future.result(timeout=30.0)
        except Exception as e:
            print(f"[MCP] Connection error: {e}")
            return False
        
        if success:
            self._clients.append(client)
            # Create tool adapters for each MCP tool
            for tool_info in client.tools:
                self._tools.append(MCPTool(client, tool_info, self._loop))
        
        return success
    
    def disconnect_all(self):
        """Disconnect from all MCP servers (sync wrapper)."""
        if not self._loop:
            return
        
        async def _disconnect():
            for client in self._clients:
                await client.disconnect()
        
        future = asyncio.run_coroutine_threadsafe(_disconnect(), self._loop)
        try:
            future.result(timeout=5.0)
        except:
            pass
        
        self._clients.clear()
        self._tools.clear()
    
    def get_tool(self, name: str) -> MCPTool | None:
        """Find a tool by name."""
        for tool in self._tools:
            if tool.name == name:
                return tool
        return None