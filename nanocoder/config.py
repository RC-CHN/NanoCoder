"""Configuration - env vars and defaults."""

import os
from dataclasses import dataclass
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
class Config:
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.0
    max_context_tokens: int = 128_000

    @classmethod
    def from_env(cls) -> "Config":
        # pick up common env vars automatically
        api_key = (
            os.getenv("NANOCODER_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("DEEPSEEK_API_KEY")
            or ""
        )
        return cls(
            model=os.getenv("NANOCODER_MODEL", "gpt-4o"),
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("NANOCODER_BASE_URL"),
            max_tokens=int(os.getenv("NANOCODER_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("NANOCODER_TEMPERATURE", "0")),
            max_context_tokens=int(os.getenv("NANOCODER_MAX_CONTEXT", "128000")),
        )
