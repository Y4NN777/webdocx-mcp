"""WebDocx models package."""

from webdocx.models.search import SearchResult, SearchQuery
from webdocx.models.document import Document, PageSummary, Section
from webdocx.models.errors import WebDocxError, SearchError, ScrapingError, CrawlError

__all__ = [
    "SearchResult",
    "SearchQuery",
    "Document",
    "PageSummary",
    "Section",
    "WebDocxError",
    "SearchError",
    "ScrapingError",
    "CrawlError",
]
