"""WebDocx tools package."""

from webdocx.tools.search import search_web
from webdocx.tools.scraper import scrape_url, crawl_docs
from webdocx.tools.research import deep_dive, summarize_page

__all__ = [
    "search_web",
    "scrape_url",
    "crawl_docs",
    "deep_dive",
    "summarize_page",
]
