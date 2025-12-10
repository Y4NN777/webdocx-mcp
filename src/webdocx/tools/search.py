"""Search tool implementation."""

from webdocx.adapters.duckduckgo import DDGAdapter

# Shared adapter instance
_adapter = DDGAdapter()


async def search_web(query: str, limit: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string.
        limit: Maximum number of results (1-20).

    Returns:
        List of search results with title, url, and snippet.
    """
    results = await _adapter.search(query, limit=min(max(limit, 1), 20))
    return [r.model_dump() for r in results]
