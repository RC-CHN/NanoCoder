# NanoCoder Configuration Reference / NanoCoder 配置参考

This document lists all configurable parameters in NanoCoder, including environment variables and hardcoded values that may be exposed as configurable options in future versions.

本文档列出 NanoCoder 中所有可配置参数，包括环境变量和未来版本可能开放的硬编码值。

---

## Environment Variables / 环境变量

These are currently supported via environment variables or `.env` file.

这些目前通过环境变量或 `.env` 文件支持。

### API Configuration / API 配置

| Variable | Default | Description |
|----------|---------|-------------|
| `NANOCODER_API_KEY` | - | API key (primary) / API 密钥（优先） |
| `OPENAI_API_KEY` | - | API key (fallback) / API 密钥（备选） |
| `DEEPSEEK_API_KEY` | - | API key (fallback) / API 密钥（备选） |
| `NANOCODER_MODEL` | `gpt-4o` | Model name / 模型名称 |
| `OPENAI_BASE_URL` | - | API base URL (primary) / API 地址（优先） |
| `NANOCODER_BASE_URL` | - | API base URL (fallback) / API 地址（备选） |

### Generation Parameters / 生成参数

| Variable | Default | Description |
|----------|---------|-------------|
| `NANOCODER_MAX_TOKENS` | `4096` | Max output tokens / 最大输出 token |
| `NANOCODER_TEMPERATURE` | `0` | Temperature / 温度参数 |
| `NANOCODER_MAX_CONTEXT` | `128000` | Max context window / 最大上下文窗口 |

### MCP Configuration / MCP 配置

| Variable | Default | Description |
|----------|---------|-------------|
| `NANOCODER_MCP_SERVERS` | - | JSON config for MCP servers / MCP 服务器 JSON 配置 |

MCP servers can also be configured via `nanocoder.json` config file (see below).

MCP 服务器也可以通过 `nanocoder.json` 配置文件配置（见下文）。

---

## Hardcoded Values / 硬编码值

These values are currently hardcoded but may be exposed as configurable options in future versions.

这些值目前是硬编码的，未来版本可能开放为可配置选项。

### Agent Configuration / Agent 配置

**File:** `nanocoder/agent.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `max_context_tokens` | 128,000 | Line 26 | Main agent context window / 主 Agent 上下文窗口 |
| `max_rounds` | 50 | Line 27 | Main agent max loop rounds / 主 Agent 最大循环轮次 |

### Sub-Agent Configuration / 子 Agent 配置

**File:** `nanocoder/tools/agent.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `max_context_tokens` | inherited | Line 47 | Sub-agent context (inherits from parent) / 子 Agent 上下文（继承父 Agent） |
| `max_rounds` | 20 | Line 48 | Sub-agent max rounds / 子 Agent 最大轮次 |
| `result_truncate` | 5,000 | Line 54 | Max result length / 结果最大长度 |
| `result_keep` | 4,500 | Line 55 | Characters kept after truncate / 截断后保留字符 |

### Context Compression / 上下文压缩

**File:** `nanocoder/context.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `max_tokens` | 128,000 | Line 38 | Context manager max / 上下文管理器最大值 |
| `_snip_at` | 50% | Line 41 | Layer 1 trigger threshold / Layer 1 触发阈值 |
| `_summarize_at` | 70% | Line 42 | Layer 2 trigger threshold / Layer 2 触发阈值 |
| `_collapse_at` | 90% | Line 43 | Layer 3 trigger threshold / Layer 3 触发阈值 |
| `tool_output_snip` | 1,500 | Line 81 | Tool output truncate threshold / 工具输出截断阈值 |
| `snip_keep_lines` | 3+3 | Line 86-90 | Lines kept after snip / 截断后保留行数 |
| `keep_recent` | 8 | Line 58 | Messages kept in Layer 2 / Layer 2 保留消息数 |
| `collapse_keep` | 4 | Line 121 | Messages kept in Layer 3 / Layer 3 保留消息数 |
| `summary_input_max` | 15,000 | Line 153 | Summary input truncate / 摘要输入截断 |
| `flatten_truncate` | 400 | Line 170 | Per-message truncate / 每条消息截断 |
| `error_line_truncate` | 150 | Line 189 | Error line truncate / 错误行截断 |
| `file_list_max` | 20 | Line 193 | Max files in extraction / 文件列表上限 |

### Bash Tool / Bash 工具

**File:** `nanocoder/tools/bash.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `timeout` | 120 | Line 53 | Command timeout (seconds) / 命令超时（秒） |
| `output_truncate` | 15,000 | Line 82 | Output truncate threshold / 输出截断阈值 |
| `output_keep_head` | 6,000 | Line 84 | Head characters kept / 保留头部字符 |
| `output_keep_tail` | 3,000 | Line 86 | Tail characters kept / 保留尾部字符 |

### Read Tool / Read 工具

**File:** `nanocoder/tools/read.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `limit` | 2,000 | Line 32 | Default max lines to read / 默认读取行数上限 |

### Glob Tool / Glob 工具

**File:** `nanocoder/tools/glob_tool.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `result_max` | 100 | Line 39 | Max matched files / 匹配结果上限 |

### Grep Tool / Grep 工具

**File:** `nanocoder/tools/grep.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `per_file_max` | 200 | Line 60 | Max matches per file / 单文件匹配上限 |
| `total_max` | 5,000 | Line 76 | Total results max / 总结果上限 |

### Edit Tool / Edit 工具

**File:** `nanocoder/tools/edit.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `preview_truncate` | 500 | Line 51 | Preview truncate when not found / 未找到时预览截断 |
| `diff_truncate` | 3,000 | Line 83 | Diff result truncate / diff 结果截断 |
| `diff_keep` | 2,500 | Line 84 | Characters kept after truncate / 截断后保留 |

### Session / 会话

**File:** `nanocoder/session.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `preview_truncate` | 80 | Line 57 | Session preview truncate / 会话预览截断 |
| `list_max` | 20 | Line 68 | Max sessions in list / 会话列表上限 |

### LLM Client / LLM 客户端

**File:** `nanocoder/llm.py`

| Parameter | Value | Location | Description |
|-----------|-------|----------|-------------|
| `retry_backoff` | 2^attempt | Line 154 | Retry wait time (exponential) / 重试等待（指数退避） |

---

## Future Configuration Options / 未来配置选项

The following environment variables are planned for future releases:

以下环境变量计划在未来版本中支持：

### Layered Model Configuration / 分层模型配置

| Variable | Description |
|----------|-------------|
| `NANOCODER_SUBAGENT_MODEL` | Model for sub-agents (cheaper model for cost savings) / 子 Agent 模型（便宜模型节省成本） |
| `NANOCODER_COMPACT_MODEL` | Model for context compression (cheaper model for summaries) / 上下文压缩模型（便宜模型做摘要） |

### Fine-tuning Options / 微调选项

| Variable | Description |
|----------|-------------|
| `NANOCODER_MAX_ROUNDS` | Main agent max rounds / 主 Agent 最大轮次 |
| `NANOCODER_SUBAGENT_MAX_ROUNDS` | Sub-agent max rounds / 子 Agent 最大轮次 |
| `NANOCODER_SUBAGENT_MAX_RESULT` | Sub-agent result truncate / 子 Agent 结果截断 |
| `NANOCODER_BASH_TIMEOUT` | Bash command timeout / Bash 命令超时 |
| `NANOCODER_READ_LIMIT` | Read tool default limit / Read 工具默认上限 |
| `NANOCODER_COMPACT_SNIP_AT` | Layer 1 trigger % / Layer 1 触发百分比 |
| `NANOCODER_COMPACT_SUMMARIZE_AT` | Layer 2 trigger % / Layer 2 触发百分比 |
| `NANOCODER_COMPACT_COLLAPSE_AT` | Layer 3 trigger % / Layer 3 触发百分比 |

---

## Priority for Configuration / 配置优先级

**High Priority (Cost Optimization) / 高优先级（成本优化）：**
1. `NANOCODER_SUBAGENT_MODEL` - Use cheaper models for sub-tasks
2. `NANOCODER_COMPACT_MODEL` - Use cheaper models for compression

**Medium Priority (Behavior Tuning) / 中优先级（行为调优）：**
3. `NANOCODER_MAX_ROUNDS` - Control main agent depth
4. `NANOCODER_SUBAGENT_MAX_ROUNDS` - Control sub-agent depth
5. `NANOCODER_BASH_TIMEOUT` - Adjust command timeout

**Low Priority (Advanced Tuning) / 低优先级（高级调优）：**
6. Compression thresholds, tool truncate sizes, etc.

---

## MCP (Model Context Protocol) Integration / MCP 集成

NanoCoder can connect to MCP servers and use their tools alongside built-in tools.

NanoCoder 可以连接 MCP 服务器，并使用其工具与内置工具一起工作。

### Configuration Methods / 配置方式

**Method 1: Config File (Recommended) / 方式 1：配置文件（推荐）**

Create `nanocoder.json` in your project directory or `~/.nanocoder.json` for global config:

在项目目录创建 `nanocoder.json` 或 `~/.nanocoder.json` 作为全局配置：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allow"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

**Method 2: Environment Variable / 方式 2：环境变量**

```bash
export NANOCODER_MCP_SERVERS='{"filesystem":{"command":"npx","args":["-y","@modelcontextprotocol/server-filesystem","/home/user"]}}'
```

### Server Configuration Fields / 服务器配置字段

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes | Executable to run (e.g., `npx`, `uvx`, `python`) |
| `args` | No | Command arguments |
| `env` | No | Environment variables for the server |
| `cwd` | No | Working directory |

### Popular MCP Servers / 常用 MCP 服务器

| Server | Command | Description |
|--------|---------|-------------|
| `@modelcontextprotocol/server-filesystem` | `npx -y @modelcontextprotocol/server-filesystem /path` | File system access |
| `@modelcontextprotocol/server-github` | `npx -y @modelcontextprotocol/server-github` | GitHub API |
| `@modelcontextprotocol/server-postgres` | `uvx mcp-server-postgres` | PostgreSQL database |
| `@modelcontextprotocol/server-slack` | `npx -y @modelcontextprotocol/server-slack` | Slack integration |

### Example: Filesystem Server / 示例：文件系统服务器

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
    }
  }
}
```

This gives NanoCoder access to MCP filesystem tools like `read_file`, `write_file`, `list_directory`, etc.

这使 NanoCoder 可以访问 MCP 文件系统工具，如 `read_file`、`write_file`、`list_directory` 等。

### Notes / 注意事项

- MCP servers are started as subprocesses and communicate via stdio
- MCP servers 作为子进程启动，通过 stdio 通信
- Tools from MCP servers are automatically merged with NanoCoder's built-in tools
- MCP 服务器的工具会自动与 NanoCoder 内置工具合并
- If a tool name conflicts, both tools will be available (MCP tool may override)
- 如果工具名称冲突，两个工具都可用（MCP 工具可能覆盖）