# WebDocx MCP - Architecture

## What is this?

WebDocx is an **MCP Server** - a program that sits between an LLM (like Claude) and the internet. It gives the LLM "superpowers" to search and read the web.

```
You (Human)
    |
    | "Research topic X"
    v
+-------------+
|   Claude    |  <-- LLM has no internet access
+-------------+
    |
    | Calls tool: search_web("topic X")
    v
+----------------------+
|  WebDocx Server      |  <-- THIS is what we're building
|  (MCP Protocol)      |
+----------------------+
    |
    | HTTP requests
    v
+------------------+
|  The Internet    |
|  (DDG, websites) |
+------------------+
    |
    | Results flow back up
    v
Claude receives data, answers your question with sources
```

## How the Server Works

The server exposes **Tools** that the LLM can call. Each tool is just a Python function.

```
+------------------------------------------------------------------+
|                      WebDocx MCP Server                          |
|                                                                  |
|  +--------------------+  +--------------------+                  |
|  |   MCP Interface    |  |   Tool Registry    |                  |
|  |   (fastmcp)        |  |                    |                  |
|  |                    |  |  - search_web      |                  |
|  |  Handles:          |  |  - scrape_url      |                  |
|  |  - JSON-RPC msgs   |  |  - deep_dive       |                  |
|  |  - Tool routing    |  |  - crawl_docs      |                  |
|  |  - Error handling  |  |  - summarize_page  |                  |
|  +--------------------+  +--------------------+                  |
|            |                      |                              |
|            v                      v                              |
|  +----------------------------------------------------------+   |
|  |                    Shared Services                        |   |
|  |                                                           |   |
|  |  +---------------+  +---------------+  +---------------+  |   |
|  |  | Web Fetcher   |  | HTML Cleaner  |  | Aggregator    |  |   |
|  |  | (crawl4ai)    |  | (readability) |  | (combines     |  |   |
|  |  |               |  |               |  |  sources)     |  |   |
|  |  +---------------+  +---------------+  +---------------+  |   |
|  +----------------------------------------------------------+   |
+------------------------------------------------------------------+
```

## Tool Details

### 1. search_web
```
Input:  query="python MCP tutorial", limit=5
Output: [
  { title: "...", url: "https://...", snippet: "..." },
  ...
]
```
Uses DuckDuckGo. Fast, no setup.

### 2. scrape_url
```
Input:  url="https://docs.python.org/3/"
Output: 
  # Python Documentation
  > Source: https://docs.python.org/3/
  
  (clean markdown content...)
```
Uses crawl4ai. Handles JavaScript pages. Strips ads/nav.

### 3. deep_dive
```
Input:  topic="MCP architecture", depth=3
Output:
  # Research: MCP architecture
  
  ## Sources
  1. [Article A](url)
  2. [Article B](url)
  3. [Article C](url)
  
  ## Content
  ### From Source 1
  (content...)
  
  ### From Source 2
  (content...)
```
Chains search + scrape. One call = full research.

### 4. crawl_docs
```
Input:  root_url="https://fastapi.tiangolo.com/", max_pages=5
Output:
  # FastAPI Documentation
  
  ## Table of Contents
  1. Introduction
  2. Installation
  3. First Steps
  
  ## 1. Introduction
  (content from page 1...)
  
  ## 2. Installation
  (content from page 2...)
```
Follows links within the same domain. Builds a complete context.

### 5. summarize_page
```
Input:  url="https://long-article.com/post"
Output:
  # Summary: Article Title
  > Source: https://long-article.com/post
  
  ## Key Sections
  - Introduction: Brief overview of...
  - Main Point 1: ...
  - Main Point 2: ...
  - Conclusion: ...
```
Extracts structure without full content. Good for triage.

## File Structure

```
webdocx/
├── src/webdocx/
│   ├── server.py       # Entry point, registers tools with fastmcp
│   ├── tools/
│   │   ├── search.py   # search_web()
│   │   ├── scraper.py  # scrape_url(), crawl_docs()
│   │   └── research.py # deep_dive(), summarize_page()
│   └── models.py       # Pydantic types (SearchResult, Document, etc.)
├── pyproject.toml
└── README.md
```

## How to Run

```bash
# Install
uv sync

# Run server (stdio mode for Claude Desktop)
uv run python -m webdocx.server
```

Then add to Claude Desktop's `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "webdocx": {
      "command": "uv",
      "args": ["run", "python", "-m", "webdocx.server"],
      "cwd": "/path/to/webdocx"
    }
  }
}
```
