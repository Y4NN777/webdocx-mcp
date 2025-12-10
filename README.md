# WebDocx MCP

A simple MCP server built to give my LLMs and AI agents real-time web access. Search, scrape, crawl docs—all without leaving my workspace.

## Why?

I got tired of copy-pasting URLs and manually feeding web content to Claude or leaving my editor to read docs and understand docs ( favorite pain points ). This server lets the LLM fetch what it needs directly based on given prompts


## Tools

### Core Tools
| Tool | What it does |
|------|-------------|
| `search_web` | 🔍 Search with DuckDuckGo (region/filter support) |
| `scrape_url` | 📄 Grab content from a URL as Markdown (w/ metadata) |
| `crawl_docs` | 📚 Crawl multi-page docs (smart link filtering) |
| `deep_dive` | 🔬 Research a topic (parallel scraping) |
| `summarize_page` | ⚡ Quick page overview |

### Advanced Tools (New!)
| Tool | What it does |
|------|-------------|
| `compare_sources` | ⚖️ Compare info across multiple sources |
| `find_related` | 🔗 Discover related pages |
| `extract_links` | 🕸️ Extract and categorize all links |
| `monitor_changes` | 📊 Track page changes over time |

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

## Features

✨ **v0.2.0 Enhanced** (80% Validated)
- ✅ Metadata extraction (+41% information)
- ✅ Retry mechanism (handles network delays)
- ✅ Source comparison (analytical insights)
- ✅ Region-specific search (localized results)
- ⚡ Parallel research (faster processing)
- 🔗 Link extraction & analysis
- 📊 Change monitoring

[See Benchmark Results →](docs/VALIDATED_IMPROVEMENTS.md)

## Docs

- [Validated Improvements](docs/VALIDATED_IMPROVEMENTS.md) ⭐ **Benchmarked!**
- [Enhanced Features](docs/ENHANCED_FEATURES.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Tools Reference](docs/TOOLS.md)

