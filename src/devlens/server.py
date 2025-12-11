"""WebDocx MCP Server.

An MCP server for web search, scraping, and documentation gathering.
"""

from fastmcp import FastMCP

from devlens.tools.search import search_web
from devlens.tools.scraper import scrape_url, crawl_docs
from devlens.tools.research import deep_dive, summarize_page
from devlens.tools.advanced import (
    compare_sources,
    find_related,
    extract_links,
    monitor_changes,
)
from devlens.utils.orchestrator import (
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
        ]
        if len(intent_scores) > 1
        else [],
    }


@mcp.tool()
def get_server_docs(topic: str = "overview") -> str:
    """Get documentation about the WebDocx MCP server.

    Provides guidance on server capabilities, tool usage, workflows, and best practices.

    Args:
        topic: Documentation topic - 'overview', 'tools', 'workflows', 'orchestration', or 'examples'

    Returns:
        Formatted documentation for the requested topic.
    """
    docs = {
        "overview": """
# WebDocx MCP Server

MCP server for intelligent web research. 12 tools in 3 layers.

## Tools
Primitives: search_web, scrape_url, crawl_docs, summarize_page, extract_links
Composed: deep_dive, compare_sources, find_related, monitor_changes
Meta: suggest_workflow, classify_research_intent, get_server_docs

## Design
- Composable: small tools combine powerfully
- Smart: auto-orchestration via suggest_workflow
- Efficient: Markdown output, token-optimized
- Context-aware: workflows adapt to research state

## Usage
search_web → scrape_url (simple)
suggest_workflow (auto-recommends)
deep_dive (multi-source aggregation)

## Topics
tools, philosophy, workflows, orchestration, examples
""",
        "tools": """
# Tools

## Primitives (fast, focused)
search_web(query, limit=5) - DuckDuckGo search, returns [{title,url,snippet}]
scrape_url(url) - Extract clean Markdown with metadata
summarize_page(url) - Headings only, triage before full scrape
extract_links(url, filter_external=True) - Categorize internal/external links
crawl_docs(root_url, max_pages=5) - Follow links, aggregate docs with TOC

## Composed (workflows)
deep_dive(topic, depth=3) - Search + parallel scraping + aggregation
compare_sources(topic, sources) - Analyze consensus/differences across 2-5 URLs
find_related(url, limit=5) - Discover similar resources via content analysis
monitor_changes(url, previous_hash) - Track content changes via hashing

## Meta (intelligence)
suggest_workflow(query, known_urls=[]) - Auto-recommend optimal tool sequence
classify_research_intent(query) - Detect research goal (7 patterns)
get_server_docs(topic) - This documentation

## Guidelines
- Simple: search_web → scrape_url
- Complex: suggest_workflow → follow steps
- Multi-source: deep_dive
- Provide known_urls to skip search
- summarize_page before expensive scrape
""",
        "workflows": """
# Workflows

Quick: search_web → scrape_url
Deep: search_web(limit=10) → deep_dive(depth=5)
Docs: search_web → crawl_docs(max_pages=25)
Compare: search_web → scrape_url(parallel) → compare_sources
Discover: search_web → find_related → extract_links
Monitor: monitor_changes(url, prev_hash)
Smart: suggest_workflow → follow steps
""",
        "orchestration": """
# Orchestration

7 Intents: quick_answer, deep_research, documentation, comparison, discovery, monitoring, validation

Adapts to:
- Intent confidence
- Known URLs (skips search)
- Failed tools (fallbacks)
- Search history (adjusts limits)

Parameter optimization:
- Quick: limit=3, max_pages=5
- Deep: limit=10, depth=comprehensive, max_pages=100
- Docs: max_pages=25, filter_external=False

Context tracks: known_urls, failed_tools, search_attempts, previous_results

Example:
suggest_workflow("integrate API?") → quick_answer, [search_web(3), scrape_url]
suggest_workflow("API docs", ["url"]) → documentation, [crawl_docs(25)] [skips search]
""",
        "examples": """
# Examples

API Integration: search_web("LidgiCash API") → scrape_url → deep_dive(depth=3)
Framework Compare: search_web("FastAPI vs Flask") → scrape_url(parallel) → compare_sources
Learn Docs: search_web("FastAPI docs") → crawl_docs(max_pages=50)
Find Alternatives: search_web("Stripe alternatives") → find_related(limit=10) → summarize_page
Smart Research: suggest_workflow("mobile payments Africa") → follow steps

Best:
- suggest_workflow when uncertain
- Provide known_urls to skip search
- summarize_page before full scrape
- compare_sources for 2-5 sources
""",
        "philosophy": """
# Design Philosophy & Developer Mindset

## Core Principles

### 1. Composability Over Complexity
Build small, focused tools that combine powerfully rather than monolithic solutions.

**Why it matters:**
- Easier to test, debug, maintain
- Users compose workflows, not forced into rigid patterns
- New capabilities emerge from combinations

**Example:**
```python
# Bad: One giant tool
research_everything(query, mode="deep", compare=True, monitor=True)

# Good: Composable primitives
search_web(query) → scrape_url(top_result) → find_related(url)
```

### 2. Intelligence at the Edges
Put smarts in orchestration layer, keep primitives simple and predictable.

**Why it matters:**
- Primitives remain reliable, testable, fast
- Intelligence adapts without breaking core tools
- Users choose: manual control or auto-orchestration

**Architecture:**
```
Meta Layer (suggest_workflow) ← Smart decisions here
     ↓
Composed Tools (deep_dive) ← Convenience combinations
     ↓
Primitives (search, scrape) ← Dumb, fast, reliable
```

### 3. Optimize for LLM Token Economy
Markdown output is not just formatting—it's an optimization strategy.

**Why it matters:**
- 50-70% smaller than HTML
- Preserves semantic structure (headings, lists, links)
- Directly consumable by LLMs without parsing

**Design choices:**
- Strip boilerplate (nav, footer, ads)
- Preserve code blocks with syntax hints
- Keep attribution (source URLs)
- Nested lists → flat hierarchy where possible

### 4. Fail Fast, Fail Clearly
Errors are data. Surface them immediately with actionable context.

**Why it matters:**
- Silent failures waste time and tokens
- Clear errors enable self-correction
- Partial success > complete failure

**Error handling:**
```python
# Bad: Silent degradation
results = [scrape(url) for url in urls]  # Some might be None

# Good: Explicit failure reporting
results = []
for url in urls:
    try:
        results.append(scrape(url))
    except ScraperError as e:
        results.append({"error": str(e), "url": url})
```

### 5. Developer Velocity First
Ship fast, iterate based on real usage, avoid premature optimization.

**Decisions made:**
- DuckDuckGo (no API keys) over Google (auth complexity)
- Sync + threadpool over async (simpler, good enough)
- Content hashing over diff algorithms (fast, 80% solution)
- Python stdlib where possible (fewer deps)

**When to optimize:**
- After measuring actual bottlenecks
- When users hit real limits (not theoretical)
- If it doesn't add complexity tax

### 6. Context is King
Track research state, adapt workflows, avoid redundant work.

**Why it matters:**
- User provides URL → skip search
- Previous tool failed → use fallback
- Multiple searches → increase limit

**ResearchContext tracks:**
- known_urls: Don't search for what you have
- failed_tools: Don't retry what doesn't work
- search_attempts: Escalate if not finding results
- previous_results: Learn from success patterns

### 7. Batteries Included, Escape Hatches Available
Work out-of-box for 80% case, allow customization for power users.

**Defaults are opinionated:**
- limit=5 (fast, usually enough)
- depth=3 (balance speed vs thoroughness)
- filter_external=True (stay on topic)
- region="wt-wt" (global results)

**But everything is tunable:**
```python
# Beginner: Just works
search_web("FastAPI")

# Power user: Full control
search_web("FastAPI", limit=20, region="us-en", safesearch="off")
```

## Anti-Patterns Avoided

### ❌ Feature Bloat
Every tool must justify its existence. If two tools overlap 70%+, merge or remove one.

### ❌ Magic Configuration
No config files, environment variables, or setup scripts. Works immediately after install.

### ❌ Abstract Interfaces
No "Strategy Pattern" with 5 implementations. Concrete tools with clear purpose.

### ❌ Premature Generalization
Solve the problem at hand. Don't build for "future requirements" that may never exist.

### ❌ Hidden State
Tools are stateless. ResearchContext is explicit parameter, not global variable.

## Performance Philosophy

**"Fast enough" beats "theoretically optimal"**
- 2s scrape is fine, 200ms not worth complexity
- Parallelization when trivial (threadpool), not when hard (async rewrite)
- Cache when obvious (content hashing), not by default

**Measure before optimizing:**
- Actual bottleneck: network I/O (not our code)
- User tolerance: 30s for deep_dive is acceptable
- Token cost > compute cost in LLM context

## Success Metrics

Good design enables:
1. **New users productive in <5 minutes** (suggest_workflow)
2. **Power users not frustrated** (full parameter control)
3. **Composable for automation** (stateless, predictable)
4. **Maintainable codebase** (small tools, clear boundaries)
5. **Extensible without forking** (add tools, don't modify existing)

## When to Break Rules

Rules are guidelines, not laws. Break them when:
- User data at risk (add complexity for security)
- Silent failure would corrupt results (add validation)
- Performance blocks real usage (optimize hot paths)
- Alternative is genuinely simpler (challenge assumptions)

**But document why:**
```python
# Breaking "no config" rule here because:
# - 100+ page crawls OOM on default limits
# - Too expensive to make dynamic
# - Power user feature, not beginner concern
MAX_CRAWL_PAGES = int(os.getenv("WEBDOCX_MAX_PAGES", "100"))
```

## Evolution Strategy

**Add, don't modify:**
- New tool > changing existing tool behavior
- New parameter > changing default
- New workflow pattern > forcing migration

**Deprecate gracefully:**
- Warning for 2 versions before removal
- Provide migration path
- Document why (not just "use X instead")

**Learn from usage:**
- Which tools are never used? (remove)
- Which combinations repeat? (compose)
- Which errors are common? (improve messages)

This isn't academic computer science—it's pragmatic engineering for real problems.
""",
    }

    topic_lower = topic.lower()
    if topic_lower in docs:
        return docs[topic_lower]
    else:
        available = ", ".join(sorted(docs.keys()))
        return f"Unknown topic '{topic}'. Available topics: {available}\n\nRecommended reading order:\n1. overview - Start here for capabilities\n2. philosophy - Understand the design mindset\n3. tools - Deep dive into each tool\n4. workflows - Common usage patterns\n5. orchestration - Smart automation\n6. examples - Real-world scenarios"


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
