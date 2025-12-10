"""Advanced web research tools."""

import asyncio
from collections import Counter
from urllib.parse import urlparse

from webdocx.adapters.duckduckgo import DDGAdapter
from webdocx.adapters.scraper import ScraperAdapter
from webdocx.models.errors import SearchError, ScrapingError

# Shared adapter instances
_ddg = DDGAdapter()
_scraper = ScraperAdapter()


async def compare_sources(topic: str, sources: list[str]) -> str:
    """Compare information across multiple sources.

    Args:
        topic: Topic being compared.
        sources: List of URLs to compare.

    Returns:
        Comparison report showing differences and similarities.

    Example:
        >>> report = await compare_sources(
        ...     "Python async",
        ...     ["https://realpython.com/async", "https://docs.python.org/3/library/asyncio.html"]
        ... )
    """
    if len(sources) < 2:
        return "Error: Need at least 2 sources to compare"

    if len(sources) > 5:
        sources = sources[:5]  # Limit to 5 sources

    # Fetch all sources in parallel
    async def fetch_with_title(url: str) -> tuple[str, str, str | None]:
        """Fetch source and return (url, title, content)."""
        try:
            doc = await _scraper.fetch(url, retry=1)
            return (url, doc.title, doc.content)
        except Exception:
            return (url, "Failed", None)

    results = await asyncio.gather(*[fetch_with_title(url) for url in sources])

    # Build comparison report
    report_lines = [
        f"# Source Comparison: {topic}\n",
        "## Sources\n",
    ]

    for i, (url, title, _) in enumerate(results, 1):
        status = "✓" if results[i - 1][2] else "✗"
        report_lines.append(f"{i}. {status} [{title}]({url})")

    report_lines.append("\n## Content Analysis\n")

    # Extract key terms from each source
    import re

    all_words: list[list[str]] = []
    for _, _, content in results:
        if content:
            # Extract meaningful words (lowercase, alphanumeric)
            words = re.findall(r"\b[a-z]{4,}\b", content.lower())
            all_words.append(words)

    if all_words:
        # Find common terms
        common_terms = set(all_words[0])
        for words in all_words[1:]:
            common_terms &= set(words)

        # Top common terms
        if common_terms:
            report_lines.append("### Common Topics\n")
            # Count frequencies
            freq = Counter()
            for words in all_words:
                freq.update(w for w in words if w in common_terms)

            top_common = freq.most_common(10)
            for term, count in top_common:
                report_lines.append(
                    f"- **{term}**: mentioned {count} times across sources"
                )

        report_lines.append("\n### Source-Specific Content\n")

    # Show excerpts from each source
    for i, (url, title, content) in enumerate(results, 1):
        report_lines.append(f"\n#### Source {i}: {title}\n")
        if content:
            # Get first 500 chars
            excerpt = content[:500].strip()
            report_lines.append(f"{excerpt}...\n")
        else:
            report_lines.append("*Failed to fetch*\n")

    return "\n".join(report_lines)


async def find_related(url: str, limit: int = 5) -> str:
    """Find related pages to a given URL.

    Args:
        url: Base URL to find related content for.
        limit: Maximum related pages (1-10).

    Returns:
        List of related pages with descriptions.

    Example:
        >>> related = await find_related("https://docs.python.org/3/library/asyncio.html")
    """
    limit = min(max(limit, 1), 10)

    # Extract topic from URL
    try:
        doc = await _scraper.fetch(url, retry=1)
        # Use title as search query
        search_query = f"{doc.title} related documentation"
    except Exception:
        # Fallback to URL-based query
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        search_query = " ".join(path_parts[-2:] if len(path_parts) > 1 else path_parts)

    # Search for related content
    try:
        results = await _ddg.search(search_query, limit=limit + 5)
    except SearchError:
        return f"# Related Pages\n\nFailed to find related content for: {url}"

    # Filter out the original URL
    related = [r for r in results if r.url != url][:limit]

    if not related:
        return f"# Related Pages\n\nNo related pages found for: {url}"

    # Build report
    report_lines = [
        "# Related Pages\n",
        f"> Based on: {url}\n",
        "## Recommendations\n",
    ]

    for i, r in enumerate(related, 1):
        report_lines.append(f"\n### {i}. {r.title}\n")
        report_lines.append(f"**URL**: {r.url}\n")
        report_lines.append(f"{r.snippet}\n")

    return "\n".join(report_lines)


async def extract_links(url: str, *, filter_external: bool = True) -> str:
    """Extract all links from a page.

    Args:
        url: URL to extract links from.
        filter_external: Only return same-domain links.

    Returns:
        Markdown list of links organized by type.

    Example:
        >>> links = await extract_links("https://example.com")
    """
    try:
        import httpx
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(url).netloc

        # Categorize links
        from urllib.parse import urljoin

        internal_links: list[tuple[str, str]] = []  # (url, text)
        external_links: list[tuple[str, str]] = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True) or href
            absolute_url = urljoin(url, href)
            parsed = urlparse(absolute_url)

            if parsed.scheme in ("http", "https"):
                if parsed.netloc == base_domain:
                    internal_links.append((absolute_url, text))
                else:
                    external_links.append((absolute_url, text))

        # Build report
        report_lines = [
            f"# Links from {url}\n",
            f"## Internal Links ({len(internal_links)})\n",
        ]

        # Deduplicate and sort
        internal_links = sorted(set(internal_links), key=lambda x: x[1].lower())
        external_links = sorted(set(external_links), key=lambda x: x[1].lower())

        for link_url, text in internal_links[:50]:  # Limit to 50
            report_lines.append(f"- [{text}]({link_url})")

        if not filter_external and external_links:
            report_lines.append(f"\n## External Links ({len(external_links)})\n")
            for link_url, text in external_links[:30]:  # Limit to 30
                report_lines.append(f"- [{text}]({link_url})")

        return "\n".join(report_lines)

    except Exception as e:
        raise ScrapingError(url, f"Failed to extract links: {e}") from e


async def monitor_changes(url: str, previous_content: str | None = None) -> str:
    """Check if a page has changed since last check.

    Args:
        url: URL to monitor.
        previous_content: Previous content hash or snippet to compare.

    Returns:
        Change detection report.

    Example:
        >>> changes = await monitor_changes("https://example.com", previous_hash)
    """
    try:
        doc = await _scraper.fetch(url, retry=1)
        current_content = doc.content

        # Generate content hash
        import hashlib

        current_hash = hashlib.sha256(current_content.encode()).hexdigest()[:16]

        report_lines = [
            f"# Change Monitor: {doc.title}\n",
            f"> URL: {url}\n",
            f"> Checked: {doc.fetched_at.strftime('%Y-%m-%d %H:%M:%S')}\n",
            "\n## Status\n",
        ]

        if previous_content:
            if previous_content == current_hash:
                report_lines.append("✓ **No changes detected**\n")
            else:
                report_lines.append("⚠️ **Content has changed**\n")
                report_lines.append(f"\n- Previous hash: `{previous_content}`\n")
                report_lines.append(f"- Current hash: `{current_hash}`\n")
        else:
            report_lines.append("ℹ️ **First check - baseline established**\n")
            report_lines.append(f"\n- Content hash: `{current_hash}`\n")

        # Add content preview
        report_lines.append("\n## Current Content Preview\n")
        preview = current_content[:500].strip()
        report_lines.append(f"{preview}...\n")

        return "\n".join(report_lines)

    except Exception as e:
        raise ScrapingError(url, f"Failed to monitor changes: {e}") from e
