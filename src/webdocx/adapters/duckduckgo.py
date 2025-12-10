"""DuckDuckGo search adapter."""

import asyncio
from duckduckgo_search import DDGS

from webdocx.models.search import SearchResult
from webdocx.models.errors import SearchError


class DDGAdapter:
    """Adapter for DuckDuckGo search."""

    def __init__(self, rate_limit_delay: float = 1.0):
        """Initialize DDG adapter.

        Args:
            rate_limit_delay: Delay between requests to avoid rate limiting.
        """
        self._rate_limit_delay = rate_limit_delay
        self._last_request_time: float = 0

    async def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Search DuckDuckGo for the given query.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of SearchResult objects.

        Raises:
            SearchError: If search fails.
        """
        if not query.strip():
            raise SearchError(query, "Query cannot be empty")

        try:
            # Rate limiting
            await asyncio.sleep(self._rate_limit_delay)

            # Run sync DDG search in executor
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: list(DDGS().text(query, max_results=limit))
            )

            return [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                )
                for r in results
            ]

        except Exception as e:
            raise SearchError(query, str(e)) from e
