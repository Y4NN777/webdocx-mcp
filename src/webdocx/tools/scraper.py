"""Scraper tool implementations."""

import asyncio

from webdocx.adapters.scraper import ScraperAdapter
from webdocx.models.errors import CrawlError

# Shared adapter instance
_adapter = ScraperAdapter()


async def scrape_url(url: str, *, include_metadata: bool = False) -> str:
    """Scrape content from a URL and return as Markdown.

    Args:
        url: The URL to scrape.
        include_metadata: Include page metadata (fetch time, word count, etc.).

    Returns:
        Markdown content with source attribution.

    Example:
        >>> content = await scrape_url("https://example.com")
        >>> content = await scrape_url("https://example.com", include_metadata=True)
    """
    doc = await _adapter.fetch(url)

    if not include_metadata:
        return doc.content

    # Add metadata section
    import re

    words = len(re.findall(r"\w+", doc.content))
    lines = len(doc.content.split("\n"))

    metadata = [
        doc.content,
        "\n---\n",
        "## Metadata\n",
        f"- **Fetched**: {doc.fetched_at.strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"- **Word Count**: ~{words:,}\n",
        f"- **Lines**: {lines:,}\n",
    ]

    return "".join(metadata)


async def crawl_docs(
    root_url: str, max_pages: int = 5, *, follow_external: bool = False
) -> str:
    """Crawl documentation starting from a root URL.

    Follows same-domain links to build a combined document with
    table of contents.

    Args:
        root_url: Starting URL for crawl.
        max_pages: Maximum pages to crawl (1-20).
        follow_external: Allow following external links (not recommended).

    Returns:
        Combined Markdown with table of contents.

    Example:
        >>> docs = await crawl_docs("https://docs.python.org/3/library/asyncio.html")
    """
    from urllib.parse import urlparse

    max_pages = min(max(max_pages, 1), 20)
    visited: set[str] = set()
    to_visit: list[str] = [root_url]
    pages: list[tuple[str, str, str]] = []  # (url, title, content)
    root_domain = urlparse(root_url).netloc

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        # Skip non-documentation URLs
        if any(
            skip in url.lower()
            for skip in ["login", "signup", "download", "print", ".pdf", ".zip"]
        ):
            continue

        try:
            doc = await _adapter.fetch(url, retry=1)  # Less retries for crawling
            visited.add(url)
            pages.append((url, doc.title, doc.content))

            # Find more links
            async with asyncio.timeout(10):
                import httpx

                async with httpx.AsyncClient(
                    timeout=10, follow_redirects=True
                ) as client:
                    resp = await client.get(url)
                    links = _adapter.get_same_domain_links(resp.text, url)

                    # Filter links
                    for link in links:
                        if link in visited or link in to_visit:
                            continue

                        # Check domain restriction
                        if not follow_external:
                            link_domain = urlparse(link).netloc
                            if link_domain != root_domain:
                                continue

                        # Prioritize docs-like URLs
                        if any(
                            doc_hint in link.lower()
                            for doc_hint in ["doc", "guide", "tutorial", "reference"]
                        ):
                            to_visit.insert(0, link)  # Add to front
                        else:
                            to_visit.append(link)

        except Exception:
            # Skip failed pages, continue crawling
            continue

    if not pages:
        raise CrawlError(root_url, "No pages could be crawled")

    # Build combined document
    toc_lines = [
        "# Documentation\n",
        f"> Crawled from: {root_url}\n",
        f"> Pages: {len(pages)}/{max_pages}\n",
        "## Table of Contents\n",
    ]
    content_lines: list[str] = []

    for i, (url, title, content) in enumerate(pages, 1):
        # Create anchor-friendly title
        anchor = title.lower().replace(" ", "-").replace("/", "-")[:50]
        toc_lines.append(f"{i}. [{title or url}](#{anchor})")
        content_lines.append(f"\n---\n\n## {i}. {title or url}\n\n> Source: {url}\n\n")

        # Strip the header from content since we added our own
        lines = content.split("\n")
        start = 0
        for j, line in enumerate(lines):
            if line.startswith("> Source:"):
                start = j + 1
                break
        content_lines.append("\n".join(lines[start:]))

    return "\n".join(toc_lines) + "\n" + "\n".join(content_lines)
