# WebDocx MCP

> **Give your LLM superpowers to search and read the web.**

WebDocx is an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that bridges the gap between LLMs and the internet. It enables AI assistants like Claude to search the web, scrape content, crawl documentation sites, and synthesize information—all with proper source attribution.

---

## Features

| Tool | Description |
|------|-------------|
| **`search_web`** | Search the web using DuckDuckGo and get structured results |
| **`scrape_url`** | Extract clean Markdown content from any webpage |
| **`crawl_docs`** | Crawl multi-page documentation sites with automatic ToC generation |
| **`deep_dive`** | Research a topic by chaining search + scrape for comprehensive reports |
| **`summarize_page`** | Get a quick structural overview of a page (headers + key points) |

### Key Principles

- **Source Attribution** — Every response includes the original URL(s)
- **Clean Markdown** — Content is returned as LLM-friendly Markdown
- **Async & Fast** — Concurrent fetching for speed
- **Error Handling** — Structured error messages, no crashes

---

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/webdocx-mcp.git
cd webdocx-mcp

# Install dependencies
uv sync
```

### Running the Server

```bash
# Start the MCP server (stdio mode)
uv run python -m webdocx.server
```

### Claude Desktop Integration

Add to your `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "webdocx": {
      "command": "uv",
      "args": ["run", "python", "-m", "webdocx.server"],
      "cwd": "/absolute/path/to/webdocx-mcp"
    }
  }
}
```

Restart Claude Desktop, and you'll have access to all WebDocx tools!

---

## Usage Examples

### Search the Web
```
"Search for Python MCP tutorials"
→ Returns top results with titles, URLs, and snippets
```

### Scrape a Page
```
"Read the content from https://docs.python.org/3/"
→ Returns clean Markdown with source attribution
```

### Deep Dive Research
```
"Do a deep dive on 'async programming in Python'"
→ Searches, scrapes multiple sources, returns aggregated report
```

### Crawl Documentation
```
"Crawl the FastAPI documentation starting from https://fastapi.tiangolo.com/"
→ Returns combined docs with table of contents
```

---

## Architecture

```
You (Human)
    │
    │ "Research topic X"
    ▼
┌─────────────┐
│   Claude    │  ← LLM (no native internet access)
└─────────────┘
    │
    │ Calls: search_web("topic X")
    ▼
┌──────────────────────┐
│   WebDocx Server     │  ← THIS PROJECT
│   (MCP Protocol)     │
└──────────────────────┘
    │
    │ HTTP requests
    ▼
┌──────────────────────┐
│   The Internet       │
│   (DuckDuckGo, etc.) │
└──────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed technical documentation.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Protocol | `mcp` (official SDK) | MCP standard compliance |
| Server | `fastmcp` | Pythonic JSON-RPC handling |
| Search | `duckduckgo-search` | Free web search, no API key needed |
| Scraping | `crawl4ai` | AI-optimized, handles JS, outputs Markdown |
| Fallback | `httpx` + `beautifulsoup4` + `readability-lxml` | Static page fallback |
| Validation | `pydantic` | Input/output schemas |

---

## Project Structure

```
webdocx-mcp/
├── src/webdocx/
│   ├── server.py       # Entry point, tool registration
│   ├── tools/
│   │   ├── search.py   # search_web()
│   │   ├── scraper.py  # scrape_url(), crawl_docs()
│   │   └── research.py # deep_dive(), summarize_page()
│   └── models.py       # Pydantic types
├── docs/
│   ├── ARCHITECTURE.md # Technical architecture docs
│   └── REQUIREMENTS.md # Project requirements
├── pyproject.toml
└── README.md
```

---

## Roadmap

### V1 (Current)
- [x] `search_web` — Web search via DuckDuckGo
- [x] `scrape_url` — Single page scraping
- [x] `deep_dive` — Chained research (search + scrape)
- [ ] `crawl_docs` — Multi-page documentation crawling
- [ ] `summarize_page` — Header extraction

### V2 (Planned)
- [ ] PDF parsing
- [ ] Authentication support for login-protected pages
- [ ] Proxy rotation

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  Made with care for the MCP ecosystem
</p>

