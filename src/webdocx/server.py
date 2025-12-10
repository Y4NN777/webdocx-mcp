"""WebDocx MCP Server.

An MCP server for web search, scraping, and documentation gathering.
"""

from fastmcp import FastMCP

from webdocx.tools.search import search_web
from webdocx.tools.scraper import scrape_url, crawl_docs
from webdocx.tools.research import deep_dive, summarize_page
from webdocx.tools.advanced import (
    compare_sources,
    find_related,
    extract_links,
    monitor_changes,
)
from webdocx.utils.orchestrator import (
    suggest_tools,
    classify_intent,
    ResearchContext,
)

# Create MCP server
mcp = FastMCP(
    name="webdocx",
    instructions="""Web search, scraping, and documentation gathering for LLMs.
    
Provides comprehensive web research capabilities including:
- Search: DuckDuckGo web search with filters
- Scraping: Extract clean Markdown from any URL
- Research: Multi-source topic research with aggregation
- Crawling: Follow links to build documentation collections
- Analysis: Compare sources, find related content, extract links
- Monitoring: Track page changes over time
""",
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


@mcp.tool()
async def tool_compare_sources(topic: str, sources: list[str]) -> str:
    """Compare information across multiple sources.

    Analyzes differences and similarities between sources.

    Args:
        topic: Topic being compared.
        sources: List of URLs (2-5) to compare.

    Returns:
        Comparison report with common topics and differences.
    """
    return await compare_sources(topic, sources)


@mcp.tool()
async def tool_find_related(url: str, limit: int = 5) -> str:
    """Find pages related to a given URL.

    Uses the page content to discover similar resources.

    Args:
        url: Base URL to find related content for.
        limit: Max related pages (1-10, default 5).

    Returns:
        List of related pages with descriptions.
    """
    return await find_related(url, limit)


@mcp.tool()
async def tool_extract_links(url: str, filter_external: bool = True) -> str:
    """Extract all links from a page.

    Useful for discovering navigation structure and resources.

    Args:
        url: URL to extract links from.
        filter_external: Only return same-domain links (default True).

    Returns:
        Organized list of internal and external links.
    """
    return await extract_links(url, filter_external=filter_external)


@mcp.tool()
async def tool_monitor_changes(url: str, previous_hash: str | None = None) -> str:
    """Check if a page has changed.

    Tracks content modifications over time.

    Args:
        url: URL to monitor.
        previous_hash: Previous content hash to compare against.

    Returns:
        Change detection report with content hash.
    """
    return await monitor_changes(url, previous_hash)


@mcp.tool()
def tool_suggest_workflow(query: str, known_urls: list[str] = None) -> dict:
    """Suggest optimal research workflow for a query.
    
    Analyzes the query and recommends the best tools and workflow to answer it.
    Uses smart intent classification and dynamic workflow generation.

    Args:
        query: Research question or task description.
        known_urls: Optional list of already known URLs (default None).

    Returns:
        Dictionary with intent, workflow steps, and suggested parameters.
    """
    # Build context from known URLs
    context = ResearchContext()
    if known_urls:
        context.known_urls = known_urls
    
    # Get workflow suggestions
    result = suggest_tools(query, context)
    
    return result


@mcp.tool()
def tool_classify_research_intent(query: str) -> dict:
    """Classify the research intent of a query.
    
    Analyzes a query to determine the user's research goal (quick answer,
    deep research, documentation, comparison, discovery, or monitoring).
    Returns confidence scores for each detected intent.

    Args:
        query: Research question or task description.

    Returns:
        Dictionary with primary and secondary intents with confidence scores.
    """
    intent_scores = classify_intent(query)
    
    return {
        "primary_intent": {
            "type": intent_scores[0].intent.value,
            "confidence": intent_scores[0].confidence,
            "reasons": intent_scores[0].reasons,
            "keywords": intent_scores[0].keywords_matched,
        },
        "secondary_intents": [
            {
                "type": score.intent.value,
                "confidence": score.confidence,
                "reasons": score.reasons,
                "keywords": score.keywords_matched,
            }
            for score in intent_scores[1:3]
        ] if len(intent_scores) > 1 else []
    }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
