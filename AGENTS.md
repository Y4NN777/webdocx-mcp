# WebDocx MCP - Agent Guidelines

Rules and conventions for AI agents working on this project.

---

## Project Overview

WebDocx is an MCP server providing web search and scraping capabilities for LLMs.

| Aspect | Choice |
|--------|--------|
| Framework | `fastmcp` |
| Runtime | Python 3.12+ |
| Package Manager | `uv` |
| Type Checking | `mypy` (strict) |
| Formatting | `ruff format` |
| Linting | `ruff check` |

---

## Architecture

### Layered Design

```
┌─────────────────────────────────────────┐
│              MCP Interface              │  ← JSON-RPC, tool registration
├─────────────────────────────────────────┤
│                 Tools                   │  ← Public API (search, scrape, etc.)
├─────────────────────────────────────────┤
│               Services                  │  ← Business logic, orchestration
├─────────────────────────────────────────┤
│               Adapters                  │  ← External APIs (DDG, crawl4ai)
├─────────────────────────────────────────┤
│                Models                   │  ← Pydantic schemas, types
└─────────────────────────────────────────┘
```

### Dependency Flow

- **Tools** depend on **Services**
- **Services** depend on **Adapters** and **Models**
- **Adapters** are isolated and replaceable
- **Models** have no dependencies

---

## Module Structure

```
src/webdocx/
├── __init__.py         # Package exports
├── server.py           # MCP server entry point
├── config.py           # Configuration and env vars
│
├── tools/              # MCP tool implementations
│   ├── __init__.py     # Tool registration
│   ├── search.py       # search_web tool
│   ├── scraper.py      # scrape_url, crawl_docs tools
│   └── research.py     # deep_dive, summarize_page tools
│
├── services/           # Business logic layer
│   ├── __init__.py
│   ├── search_service.py
│   ├── scraper_service.py
│   └── aggregator.py   # Combines multiple sources
│
├── adapters/           # External integrations
│   ├── __init__.py
│   ├── duckduckgo.py   # DDG search adapter
│   ├── crawl4ai.py     # Crawl4AI adapter
│   └── httpx_client.py # HTTP client wrapper
│
├── models/             # Data structures
│   ├── __init__.py
│   ├── search.py       # SearchResult, SearchQuery
│   ├── document.py     # Document, Page, Content
│   └── errors.py       # Custom exceptions
│
└── utils/              # Shared utilities
    ├── __init__.py
    ├── markdown.py     # Markdown processing
    └── url.py          # URL validation/parsing
```

### Module Guidelines

| Module | Purpose | Allowed Imports |
|--------|---------|-----------------|
| `tools/` | MCP interface | services, models |
| `services/` | Business logic | adapters, models, utils |
| `adapters/` | External APIs | models, utils |
| `models/` | Data types | stdlib only |
| `utils/` | Helpers | stdlib, models |

---

## Code Style

### Type Hints

```python
# Required on all functions
async def search_web(
    query: str,
    limit: int = 5,
    *,
    timeout: float | None = None,
) -> list[SearchResult]:
    ...
```

### Docstrings (Google Style)

```python
async def scrape_url(url: str) -> Document:
    """Scrape content from a URL and return as Markdown.

    Fetches the page, extracts main content, and converts to
    clean Markdown with source attribution.

    Args:
        url: The URL to scrape. Must be a valid HTTP(S) URL.

    Returns:
        Document containing Markdown content and metadata.

    Raises:
        ScrapingError: If the page cannot be fetched or parsed.
        ValidationError: If the URL is invalid.

    Example:
        >>> doc = await scrape_url("https://example.com")
        >>> print(doc.content[:100])
    """
```

### Comments

```python
# GOOD: Explain WHY, not WHAT
# Rate limit to avoid DDG blocking (max 1 req/sec)
await asyncio.sleep(1.0)

# GOOD: Document non-obvious behavior
# Returns empty list on timeout instead of raising
# to allow partial results in deep_dive

# BAD: Obvious comments
# Loop through results  ← Don't do this
for result in results:

# TODO format (include issue/context)
# TODO(#42): Add retry logic for transient failures

# FIXME format
# FIXME: This breaks on URLs with unicode paths
```

### Error Handling

```python
# Use custom exceptions from models/errors.py
class WebDocxError(Exception):
    """Base exception for all WebDocx errors."""

class ScrapingError(WebDocxError):
    """Failed to scrape a URL."""
    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to scrape {url}: {reason}")

# Always catch specific exceptions
try:
    result = await adapter.fetch(url)
except httpx.TimeoutException:
    raise ScrapingError(url, "Request timed out")
except httpx.HTTPStatusError as e:
    raise ScrapingError(url, f"HTTP {e.response.status_code}")
```

---

## Commit Conventions

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(tools): add summarize_page tool` |
| `fix` | Bug fix | `fix(scraper): handle timeout on large pages` |
| `refactor` | Code restructure | `refactor(services): extract URL validation` |
| `docs` | Documentation | `docs: update AGENTS.md with module structure` |
| `test` | Tests only | `test(search): add edge case for empty query` |
| `chore` | Maintenance | `chore: update dependencies` |
| `perf` | Performance | `perf(crawl): parallelize page fetching` |

### Scopes

Use module names: `tools`, `services`, `adapters`, `models`, `utils`, `config`

### Subject Rules

- Imperative mood: "add" not "added" or "adds"
- Lowercase first letter
- No period at end
- Max 50 characters

### Body (When Needed)

- Wrap at 72 characters
- Explain WHAT and WHY, not HOW
- Reference issues: `Fixes #123`

### Examples

```
feat(tools): add deep_dive research tool

Implements multi-source research by chaining search and scrape.
Aggregates results with source attribution.

Closes #15
```

```
fix(adapters): handle DDG rate limiting

- Add exponential backoff (1s, 2s, 4s)
- Return partial results on final timeout
- Log warning when rate limited

Fixes #28
```

---

## Testing

### File Naming

```
tests/
├── unit/
│   ├── test_search_service.py
│   └── test_url_utils.py
├── integration/
│   └── test_scraper_e2e.py
└── conftest.py
```

### Test Structure

```python
class TestSearchService:
    """Tests for SearchService."""

    async def test_search_returns_results(self):
        """Should return list of SearchResult for valid query."""
        # Arrange
        service = SearchService(adapter=MockDDGAdapter())
        
        # Act
        results = await service.search("python mcp")
        
        # Assert
        assert len(results) == 5
        assert all(isinstance(r, SearchResult) for r in results)

    async def test_search_empty_query_raises(self):
        """Should raise ValidationError for empty query."""
        service = SearchService(adapter=MockDDGAdapter())
        
        with pytest.raises(ValidationError):
            await service.search("")
```

---

## Dependency Rules

### Adding Dependencies

1. Check if existing dependency can solve the problem
2. Prefer well-maintained, typed packages
3. Add to `pyproject.toml` with version constraint
4. Document why in commit message

### Core Dependencies (Do Not Replace)

| Package | Purpose |
|---------|---------|
| `fastmcp` | MCP protocol |
| `crawl4ai` | JS-capable scraping |
| `duckduckgo-search` | Web search |
| `pydantic` | Validation |
| `httpx` | HTTP client |

---

## Prohibited Practices

- Synchronous I/O in async functions
- Bare `except:` clauses
- Mutable default arguments
- Global state outside `config.py`
- Hardcoded URLs or API keys
- Removing source attribution from outputs
- Breaking existing tool signatures
