"""Research tool implementations."""

from webdocx.adapters.duckduckgo import DDGAdapter
from webdocx.adapters.scraper import ScraperAdapter

# Shared adapter instances
_ddg = DDGAdapter()
_scraper = ScraperAdapter()


async def deep_dive(topic: str, depth: int = 3, *, parallel: bool = True) -> str:
    """Research a topic by searching and scraping multiple sources.

    Args:
        topic: Topic to research.
        depth: Number of sources to scrape (1-10).
        parallel: Whether to scrape sources in parallel (faster).

    Returns:
        Aggregated research report with sources.

    Example:
        >>> report = await deep_dive("Python async/await tutorial", depth=5)
    """
    import asyncio

    depth = min(max(depth, 1), 10)

    # Search for sources
    results = await _ddg.search(topic, limit=depth * 2)  # Get more to filter

    # Filter to unique domains for diversity
    from urllib.parse import urlparse

    seen_domains = set()
    filtered_results = []
    for r in results:
        domain = urlparse(r.url).netloc
        if domain not in seen_domains and len(filtered_results) < depth:
            seen_domains.add(domain)
            filtered_results.append(r)

    results = filtered_results

    if not results:
        return f"# Research: {topic}\n\nNo results found for this topic."

    # Build report header
    report_lines = [
        f"# Research: {topic}\n",
        f"*Analyzed {len(results)} sources*\n",
        "## Sources\n",
    ]

    # Add sources list
    for i, r in enumerate(results, 1):
        report_lines.append(f"{i}. [{r.title}]({r.url})")

    report_lines.append("\n## Content\n")

    # Scrape sources (parallel or sequential)
    async def fetch_source(i: int, r) -> tuple[int, str, str, str | None]:
        """Fetch a single source."""
        try:
            doc = await _scraper.fetch(r.url)
            # Extract content without header
            lines = doc.content.split("\n")
            start = 0
            for j, line in enumerate(lines):
                if line.startswith("> Source:"):
                    start = j + 1
                    break
            content = "\n".join(lines[start:]).strip()
            # Truncate if too long
            if len(content) > 3000:
                content = content[:3000] + "\n\n*[Content truncated...]*"
            return (i, r.title, r.url, content)
        except Exception:
            return (i, r.title, r.url, None)

    if parallel:
        # Fetch all sources concurrently
        tasks = [fetch_source(i, r) for i, r in enumerate(results, 1)]
        fetched = await asyncio.gather(*tasks, return_exceptions=False)
    else:
        # Fetch sequentially
        fetched = []
        for i, r in enumerate(results, 1):
            result = await fetch_source(i, r)
            fetched.append(result)

    # Build content sections
    successful = 0
    for i, title, url, content in fetched:
        report_lines.append(f"### Source {i}: {title}\n")
        report_lines.append(f"> {url}\n")

        if content:
            report_lines.append(content)
            successful += 1
        else:
            report_lines.append("*Failed to fetch content*")

        report_lines.append("\n")

    # Add summary footer
    report_lines.append(
        f"---\n\n*Successfully retrieved {successful}/{len(results)} sources*"
    )

    return "\n".join(report_lines)


async def summarize_page(url: str) -> str:
    """Get a structural summary of a page.

    Args:
        url: URL to summarize.

    Returns:
        Page summary with sections.
    """
    summary = await _scraper.summarize(url)

    lines = [
        f"# Summary: {summary.title}\n",
        f"> Source: {url}\n",
        "## Key Sections\n",
    ]

    if not summary.sections:
        lines.append("*No sections found*")
    else:
        for section in summary.sections:
            if section.summary:
                lines.append(f"- **{section.heading}**: {section.summary}")
            else:
                lines.append(f"- **{section.heading}**")

    return "\n".join(lines)
