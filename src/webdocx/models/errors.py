"""Custom exceptions for WebDocx."""


class WebDocxError(Exception):
    """Base exception for all WebDocx errors."""

    pass


class SearchError(WebDocxError):
    """Failed to perform web search."""

    def __init__(self, query: str, reason: str):
        self.query = query
        self.reason = reason
        super().__init__(f"Search failed for '{query}': {reason}")


class ScrapingError(WebDocxError):
    """Failed to scrape a URL."""

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to scrape {url}: {reason}")


class CrawlError(WebDocxError):
    """Failed to crawl documentation."""

    def __init__(self, root_url: str, reason: str):
        self.root_url = root_url
        self.reason = reason
        super().__init__(f"Failed to crawl {root_url}: {reason}")
