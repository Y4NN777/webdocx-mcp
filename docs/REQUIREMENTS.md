# WebDocx MCP - Requirements

## Goal
An MCP server that gives LLMs real-time web access for gathering documentation or aricle without leaving your workspace: search, scrape, crawl documentation, and synthesize content with source attribution.

## Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `search_web` | Discover sources | query, limit | List of {title, url, snippet} |
| `scrape_url` | Read single page | url | Markdown with source header |
| `crawl_docs` | Ingest multi-page docs | root_url, max_pages | Combined Markdown with ToC |
| `deep_dive` | Research a topic | topic, depth | Aggregated report with sources |
| `summarize_page` | Quick overview | url | Headers + key points outline |

## Output Contract
- Every response includes source URL(s)
- Content returned as clean Markdown
- Errors return structured messages, not crashes

## Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **Protocol** | `mcp` (official SDK) | Standard compliance |
| **Server Framework** | `fastmcp` | Pythonic, handles JSON-RPC boilerplate |
| **Search** | `duckduckgo-search` | Free, no API key |
| **Scraping** | `crawl4ai` | AI-optimized, handles JS, outputs Markdown |
| **Fallback Scraping** | `httpx` + `beautifulsoup4` + `readability-lxml` | For simple static pages |
| **Async** | `asyncio` | Concurrent fetching |
| **Validation** | `pydantic` | Strict input/output schemas |

## V1 Scope
1. `search_web` - working
2. `scrape_url` - working
3. `deep_dive` - working (chains 1 + 2)
4. `crawl_docs` - basic (follow same-domain links)
5. `summarize_page` - extract headers

## Out of Scope (V2)
- PDF parsing
- Authentication/login pages
- Proxy rotation
