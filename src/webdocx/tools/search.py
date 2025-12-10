"""Search tool implementation."""

import re
from functools import lru_cache
from webdocx.adapters.duckduckgo import DDGAdapter
from webdocx.models.errors import SearchError

# Shared adapter instance
_adapter = DDGAdapter()


@lru_cache(maxsize=100)
def _normalize_query(query: str) -> str:
    """Normalize search query for better results."""
    # Remove excessive whitespace
    query = re.sub(r"\s+", " ", query.strip())
    return query


async def search_web(
    query: str,
    limit: int = 5,
    *,
    region: str | None = None,
    safe_search: bool = True,
) -> list[dict]:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string. Supports operators like:
            - site:domain.com to search specific domain
            - "exact phrase" for exact matches
            - -word to exclude terms
        limit: Maximum number of results (1-20).
        region: Optional region code (e.g., 'us-en', 'uk-en').
        safe_search: Enable safe search filtering.

    Returns:
        List of search results with title, url, and snippet.

    Raises:
        SearchError: If search fails or query is invalid.

    Example:
        >>> results = await search_web("Python asyncio tutorial", limit=5)
        >>> results = await search_web('site:docs.python.org async', limit=3)
    """
    if not query or not query.strip():
        raise SearchError(query, "Query cannot be empty")

    # Normalize query
    normalized = _normalize_query(query)

    # Clamp limit
    limit = min(max(limit, 1), 20)

    try:
        results = await _adapter.search(
            normalized,
            limit=limit,
            region=region,
            safe_search=safe_search,
        )

        # Filter out low-quality results
        filtered = [r for r in results if r.title and r.url and len(r.snippet) > 20]

        return [r.model_dump() for r in filtered]

    except SearchError:
        raise
    except Exception as e:
        raise SearchError(query, f"Unexpected error: {e}") from e
