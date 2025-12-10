"""Research tool implementations."""

from webdocx.adapters.duckduckgo import DDGAdapter
from webdocx.adapters.scraper import ScraperAdapter

# Shared adapter instances
_ddg = DDGAdapter()
_scraper = ScraperAdapter()


async def deep_dive(topic: str, depth: int = 3) -> str:
    """Research a topic by searching and scraping multiple sources.

    Args:
        topic: Topic to research.
        depth: Number of sources to scrape (1-10).

    Returns:
        Aggregated research report with sources.
    """
    depth = min(max(depth, 1), 10)

    # Search for sources
    results = await _ddg.search(topic, limit=depth)

    if not results:
        return f"# Research: {topic}\n\nNo results found for this topic."

    # Build report header
    report_lines = [
        f"# Research: {topic}\n",
        "## Sources\n",
    ]

    # Add sources list
    for i, r in enumerate(results, 1):
        report_lines.append(f"{i}. [{r.title}]({r.url})")

    report_lines.append("\n## Content\n")

    # Scrape each source
    for i, r in enumerate(results, 1):
        report_lines.append(f"### From Source {i}: {r.title}\n")
        report_lines.append(f"> {r.url}\n")

        try:
            doc = await _scraper.fetch(r.url)
            # Extract just the content, skip the title/source we already have
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
            report_lines.append(content)
        except Exception as e:
            report_lines.append(f"*Failed to fetch: {e}*")

        report_lines.append("\n")

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
