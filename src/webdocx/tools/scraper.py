"""Scraper tool implementations."""

import asyncio

from webdocx.adapters.scraper import ScraperAdapter
from webdocx.models.errors import CrawlError

# Shared adapter instance
_adapter = ScraperAdapter()


async def scrape_url(url: str) -> str:
    """Scrape content from a URL and return as Markdown.

    Args:
        url: The URL to scrape.

    Returns:
        Markdown content with source attribution.
    """
    doc = await _adapter.fetch(url)
    return doc.content


async def crawl_docs(root_url: str, max_pages: int = 5) -> str:
    """Crawl documentation starting from a root URL.

    Follows same-domain links to build a combined document with
    table of contents.

    Args:
        root_url: Starting URL for crawl.
        max_pages: Maximum pages to crawl (1-20).

    Returns:
        Combined Markdown with table of contents.
    """
    max_pages = min(max(max_pages, 1), 20)
    visited: set[str] = set()
    to_visit: list[str] = [root_url]
    pages: list[tuple[str, str, str]] = []  # (url, title, content)

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        try:
            doc = await _adapter.fetch(url)
            visited.add(url)
            pages.append((url, doc.title, doc.content))

            # Find more links
            async with asyncio.timeout(10):
                import httpx
                async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                    resp = await client.get(url)
                    links = _adapter.get_same_domain_links(resp.text, url)

                    for link in links:
                        if link not in visited and link not in to_visit:
                            to_visit.append(link)

        except Exception:
            # Skip failed pages, continue crawling
            continue

    if not pages:
        raise CrawlError(root_url, "No pages could be crawled")

    # Build combined document
    toc_lines = ["# Documentation\n", f"> Crawled from: {root_url}\n", "## Table of Contents\n"]
    content_lines: list[str] = []

    for i, (url, title, content) in enumerate(pages, 1):
        toc_lines.append(f"{i}. [{title or url}](#{i})")
        content_lines.append(f"\n---\n\n## {i}. {title or url}\n\n> Source: {url}\n\n")
        # Strip the header from content since we added our own
        lines = content.split("\n")
        # Skip first few lines (title and source)
        start = 0
        for j, line in enumerate(lines):
            if line.startswith("> Source:"):
                start = j + 1
                break
        content_lines.append("\n".join(lines[start:]))

    return "\n".join(toc_lines) + "\n" + "\n".join(content_lines)
