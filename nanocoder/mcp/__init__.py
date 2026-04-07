"""MCP (Model Context Protocol) integration for NanoCoder.

This module allows NanoCoder to connect to MCP servers and use their tools.
"""

from .client import MCPClient
from .tool_adapter import MCPTool, MCPToolManager

__all__ = ["MCPClient", "MCPTool", "MCPToolManager"]