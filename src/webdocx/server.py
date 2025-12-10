"""WebDocx MCP Server.

An MCP server for web search, scraping, and documentation gathering.
"""

from fastmcp import FastMCP

from webdocx.tools.search import search_web
from webdocx.tools.scraper import scrape_url, crawl_docs
from webdocx.tools.research import deep_dive, summarize_page

# Create MCP server
mcp = FastMCP(
    name="webdocx",
    instructions="Web search, scraping, and documentation gathering for LLMs",
)


# Register tools
@mcp.tool()
async def tool_search_web(query: str, limit: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string.
        limit: Maximum results (1-20, default 5).

    Returns:
        List of results with title, url, snippet.
    """
    return await search_web(query, limit)


@mcp.tool()
async def tool_scrape_url(url: str) -> str:
    """Scrape content from a URL as Markdown.

    Args:
        url: URL to scrape.

    Returns:
        Markdown content with source attribution.
    """
    return await scrape_url(url)


@mcp.tool()
async def tool_crawl_docs(root_url: str, max_pages: int = 5) -> str:
    """Crawl multi-page documentation.

    Follows same-domain links to build combined docs.

    Args:
        root_url: Starting URL.
        max_pages: Max pages to crawl (1-20, default 5).

    Returns:
        Combined Markdown with table of contents.
    """
    return await crawl_docs(root_url, max_pages)


@mcp.tool()
async def tool_deep_dive(topic: str, depth: int = 3) -> str:
    """Research a topic from multiple sources.

    Searches and scrapes multiple pages to build a report.

    Args:
        topic: Topic to research.
        depth: Number of sources (1-10, default 3).

    Returns:
        Aggregated research report.
    """
    return await deep_dive(topic, depth)


@mcp.tool()
async def tool_summarize_page(url: str) -> str:
    """Get a quick overview of a page.

    Extracts headings and key sections.

    Args:
        url: URL to summarize.

    Returns:
        Page summary with sections.
    """
    return await summarize_page(url)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
