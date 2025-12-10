# WebDocx MCP - Agents Documentation

This document describes how AI agents and LLMs should interact with WebDocx MCP tools.

---

## Tool Usage Guidelines

### search_web

**Purpose**: Discover relevant sources for a topic.

**When to use**:
- Starting research on a new topic
- Finding documentation URLs
- Looking for tutorials or articles

**Best practices**:
- Use specific, targeted queries
- Limit results to avoid information overload (default: 5)
- Follow up with `scrape_url` for detailed content

**Example**:
```json
{
  "tool": "search_web",
  "args": {
    "query": "fastapi authentication middleware",
    "limit": 5
  }
}
```

---

### scrape_url

**Purpose**: Extract content from a single webpage.

**When to use**:
- Reading documentation pages
- Extracting article content
- Getting detailed information from a known URL

**Best practices**:
- Verify the URL is accessible before scraping
- Use for authoritative sources (official docs, reputable sites)
- Always attribute the source in your response

**Example**:
```json
{
  "tool": "scrape_url",
  "args": {
    "url": "https://docs.python.org/3/library/asyncio.html"
  }
}
```

---

### deep_dive

**Purpose**: Comprehensive research on a topic.

**When to use**:
- User asks for thorough research
- Need to synthesize multiple sources
- Building documentation or guides

**Best practices**:
- Set appropriate depth (1-3 for quick research, 4-5 for comprehensive)
- Review all sources for accuracy
- Synthesize, don't just concatenate

**Example**:
```json
{
  "tool": "deep_dive",
  "args": {
    "topic": "Python type hints best practices",
    "depth": 3
  }
}
```

---

### crawl_docs

**Purpose**: Ingest multi-page documentation.

**When to use**:
- Learning a new framework or library
- Building a local knowledge base
- Comprehensive documentation review

**Best practices**:
- Start with the documentation root URL
- Limit pages to avoid excessive crawling
- Use for same-domain content only

**Example**:
```json
{
  "tool": "crawl_docs",
  "args": {
    "root_url": "https://fastapi.tiangolo.com/",
    "max_pages": 10
  }
}
```

---

### summarize_page

**Purpose**: Quick overview without full content.

**When to use**:
- Triaging multiple pages
- Deciding if full scrape is needed
- Getting page structure quickly

**Best practices**:
- Use before `scrape_url` to check relevance
- Good for long articles or documentation
- Follow up with full scrape if content is relevant

**Example**:
```json
{
  "tool": "summarize_page",
  "args": {
    "url": "https://blog.example.com/long-article"
  }
}
```

---

## Workflow Patterns

### Research Workflow
1. `search_web` — Find relevant sources
2. `summarize_page` — Triage results
3. `scrape_url` — Get full content from relevant pages
4. Synthesize and respond with attribution

### Documentation Learning Workflow
1. `crawl_docs` — Ingest documentation
2. Parse and understand structure
3. Answer questions from gathered context

### Quick Answer Workflow
1. `search_web` — Find top result
2. `scrape_url` — Get content
3. Extract answer with source citation

---

## Response Guidelines

### Always Include
- Source URLs for all cited information
- Clear attribution when quoting
- Structured Markdown formatting

### Avoid
- Presenting scraped content as your own knowledge
- Making claims without source backing
- Overloading context with unnecessary content

---

## Error Handling

| Error | Recommended Action |
|-------|-------------------|
| URL not accessible | Try alternative sources via `search_web` |
| Timeout | Retry once, then report to user |
| No results | Broaden search query or suggest alternatives |
| Rate limited | Wait and retry, or use cached content |
