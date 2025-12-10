# WebDocx MCP

A simple MCP server built to give my LLMs and AI agents real-time web access. Search, scrape, crawl docs—all without leaving my workspace.

## Why?

I got tired of copy-pasting URLs and manually feeding web content to Claude or leaving my editor to read docs and understand docs ( favorite pain points ). This server lets the LLM fetch what it needs directly.

## Tools

| Tool | What it does |
|------|-------------|
| `search_web` | Search with DuckDuckGo |
| `scrape_url` | Grab content from a URL as Markdown |
| `crawl_docs` | Crawl multi-page docs |
| `deep_dive` | Research a topic (search + scrape combined) |
| `summarize_page` | Quick page overview |

## Setup

```bash
# Install
uv sync

# Run
uv run python -m webdocx.server
```

Add to Claude Desktop config:

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

## Stack

- `fastmcp` — MCP server
- `crawl4ai` — Web scraping (handles JS)
- `duckduckgo-search` — Search
- `pydantic` — Validation

## Docs

- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Tools Reference](docs/TOOLS.md)

