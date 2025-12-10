# WebDocx MCP

MCP server for web access—search, scrape, crawl. Nine tools to gather and analyze web content from any MCP client.

## Why

Your AI assistant can't browse the web. WebDocx fixes that through MCP protocol. Works with Claude Desktop, VS Code Copilot, or any MCP-compatible client.

## Tools

### Core Research
**search_web** — DuckDuckGo search with region/filter support  
**scrape_url** — Extract page content as Markdown (optional metadata)  
**crawl_docs** — Multi-page documentation crawling (smart filtering)  
**deep_dive** — Multi-source research with parallel fetching  
**summarize_page** — Quick page structure overview  

### Analysis
**compare_sources** — Analyze multiple sources for consensus/differences  
**find_related** — Discover related pages via content analysis  
**extract_links** — Categorize internal/external links  
**monitor_changes** — Track page updates via content hashing

### Smart Orchestration
**suggest_workflow** — Auto-recommend optimal research workflow  
**classify_research_intent** — Detect research goal with confidence scores

## Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Y4NN777/webdocx-mcp.git
cd webdocx-mcp

# Install dependencies
uv sync

# Run the server (STDIO mode)
uv run python -m webdocx.server

# Test locally
uv run python test_benchmark.py
```

### MCP Client Configuration

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` or `~/.config/claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "webdocx": {
      "command": "uv",
      "args": ["run", "python", "-m", "webdocx.server"],
      "cwd": "/path/to/webdocx-mcp"
    }
  }
}
```

**VS Code Copilot** (`.vscode/mcp.json` in workspace):
```json
{
  "servers": {
    "webdocx": {
      "command": "/path/to/webdocx-mcp/launch_mcp.sh"
    }
  }
}
```

**Other MCP Clients**: Use STDIO transport with `uv run python -m webdocx.server`

## Library Stack

- `fastmcp` — MCP server framework
- `crawl4ai` — Web scraping with JavaScript support
- `ddgs` — Search (DuckDuckGo)
- `httpx` — HTTP client with fallback
- `pydantic` — Validation

## Features

**Enhanced Scraping**
- Metadata extraction (+41% information density)
- Exponential backoff retry (handles flaky networks)
- Multi-source comparison analysis
- Region-specific search results
- Parallel content fetching (3x faster)
- Content change detection

**Smart Orchestration**
- Intent classification (7 research patterns)
- Dynamic workflow generation
- Context-aware parameter optimization
- Fallback strategies & parallel execution
- Resource cost estimation (fast/medium/slow)

## Docs

- [Requirements](docs/REQUIREMENTS.md) — Scope and tech stack
- [Architecture](docs/ARCHITECTURE.md) — How it works
- [Tools Reference](docs/TOOLS.md) — Detailed tool usage

