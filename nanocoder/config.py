"""Configuration - env vars and defaults."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

# Load .env file if exists
try:
    from dotenv import load_dotenv
    # Load from current directory and parent directories
    load_dotenv()
    # Also try to load from project root if in subdirectory
    project_root = Path.cwd()
    for _ in range(3):  # Search up to 3 levels
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            break
        if project_root.parent == project_root:
            break
        project_root = project_root.parent
except ImportError:
    pass  # python-dotenv not installed, skip


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    cwd: str | None = None
    
    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "cwd": self.cwd,
        }
    
    @classmethod
    def from_dict(cls, name: str, d: dict) -> "MCPServerConfig":
        return cls(
            name=name,
            command=d.get("command", ""),
            args=d.get("args", []),
            env=d.get("env", {}),
            cwd=d.get("cwd"),
        )


@dataclass
class Config:
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.0
    max_context_tokens: int = 128_000
    mcp_servers: list[MCPServerConfig] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "Config":
        # pick up common env vars automatically
        api_key = (
            os.getenv("NANOCODER_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("DEEPSEEK_API_KEY")
            or ""
        )
        
        # Load MCP server configs from environment or config file
        mcp_servers = cls._load_mcp_config()
        
        return cls(
            model=os.getenv("NANOCODER_MODEL", "gpt-4o"),
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("NANOCODER_BASE_URL"),
            max_tokens=int(os.getenv("NANOCODER_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("NANOCODER_TEMPERATURE", "0")),
            max_context_tokens=int(os.getenv("NANOCODER_MAX_CONTEXT", "128000")),
            mcp_servers=mcp_servers,
        )
    
    @classmethod
    def _load_mcp_config(cls) -> list[MCPServerConfig]:
        """Load MCP server configurations from nanocoder.json or NANOCODER_MCP_SERVERS env var."""
        servers = []
        
        # Method 1: From environment variable (JSON format)
        env_config = os.getenv("NANOCODER_MCP_SERVERS")
        if env_config:
            try:
                config_data = json.loads(env_config)
                for name, server_config in config_data.items():
                    servers.append(MCPServerConfig.from_dict(name, server_config))
            except json.JSONDecodeError as e:
                print(f"[MCP] Warning: Failed to parse NANOCODER_MCP_SERVERS: {e}")
        
        # Method 2: From config file (nanocoder.json)
        config_paths = [
            Path.cwd() / "nanocoder.json",
            Path.home() / ".nanocoder.json",
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config_data = json.load(f)
                    
                    mcp_config = config_data.get("mcpServers", {})
                    for name, server_config in mcp_config.items():
                        # Avoid duplicates
                        if not any(s.name == name for s in servers):
                            servers.append(MCPServerConfig.from_dict(name, server_config))
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[MCP] Warning: Failed to load {config_path}: {e}")
        
        return servers
