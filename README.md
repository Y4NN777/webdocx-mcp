# **DevLens MCP**

**The MCP Server I Built to Kill Alt-Tab. Clean, fast web context, right in your IDE.**

Like most developers, I was sick of context-switching between VS Code and the browser for documentation. That was my core frustration. So, I built DevLens: an **open-source** MCP server because I was curious and wanted a **custom solution** that was more efficient than existing tools.

The goal is simple: give your workspace AI (Copilot, Claude, etc.) web access that is **structured** and **token-efficient**. DevLens delivers twelve specialized tools via a three-layered architecture built for power and easy deployment.

## **What is MCP and DevLens's Role?**

The **MCP (Model Context Protocol)** is the standard that lets your AI assistant call external tools (web search, scraping) to act beyond its training data. It gives the AI real-world power.

**DevLens's Role** is to be the most efficient implementation for web research. DevLens handles the intelligence (Smart Orchestration) and formats the results into clean Markdown. This ensures your workspace AI receives the precise context it needs without the clutter or high token cost of raw HTML.

## **Why DevLens (Solving the Flow Problem)**

DevLens is built on two principles to solve context loss: **Technical Composability** and **Token Efficiency**.

### **Built for the Developer Workflow**

* **The Problem Solved:** No more useless switching between browser and editor. Your coding flow stays intact.  
* **The Technical Edge:** Our layered architecture uses simple primitives that combine powerfully. This means more precise and less costly workflows than existing "monolithic" solutions.  
* **LLM Context Optimal:** Our clean, token-optimized Markdown output is about **70% smaller** than raw HTML. This is the secret for fast, accurate AI results in your chat.  
* **Seamless IDE Integration:** Designed to pair perfectly with **VS Code Copilot and GitHub Copilot**. Web research is injected directly into your editor.  
* **Deployment Ready:** Use it locally for your own work, or deploy it on a server to share with others.  
* **Smart Orchestration** — The system chooses the best tool sequence, automatically.  
* **Zero Configuration** — Install, run. Done.

### **Developer Personas & Use Cases**

| Persona | Problem Solved (The Pain) | DevLens Solution (The Win) |
| :---- | :---- | :---- |
| **Nina, the Frontend Developer** | Needs a quick fix (e.g., that one CORS config snippet) but hates opening 5 Stack Overflow tabs. | Uses suggest\_workflow or search\_web \+ summarize\_page to get the validated code snippet instantly in chat. Flow maintained. |
| **Kenji, the Staff Engineer** | Must compare three serverless vendors for an architecture decision. Needs a single, definitive data dump. | Uses deep\_dive to fetch, aggregate, and analyze complex data concurrently. The LLM receives the full, pre-processed report. |
| **Sarah, the DevOps Specialist** | Has to manually check third-party deployment guides every week for silent, breaking changes. | Uses monitor\_changes to passively track content hashes on critical docs, sending an alert only when something actually changes. |

## **Tools**

DevLens gives you **12 specialized tools**—think of it like a camera bag of lenses. Pick one, or let the smart system auto-select:

| Layer | Metaphor | Focus | Tools |
| :---- | :---- | :---- | :---- |
| **Primitives** | *Basic Lenses* | Precision & Reliability | search\_web, scrape\_url, crawl\_docs, summarize\_page, extract\_links |
| **Composed** | *Multi-Lens Systems* | Convenience & Aggregation | deep\_dive, compare\_sources, find\_related, monitor\_changes |
| **Meta** | *Auto-Focus Intelligence* | Guidance & Optimization | suggest\_workflow, classify\_research\_intent, get\_server\_docs |

## **Quick Start (Seriously, It's Fast)**

### **Prerequisites**

* Python 3.12 or newer  
* uv package manager

### **Installation**

```bash
# Clone the repository
git clone https://github.com/Y4NN777/devlens-mcp.git
cd devlens-mcp

# Install dependencies
uv sync

# Run the server (STDIO mode)
uv run python -m devlens.server
```

### **Configuration du client MCP**

#### **Claude Desktop**

Add this to `claude_desktop_config.json`:

* macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
* Linux: `~/.config/claude/claude_desktop_config.json`
* Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Option 1: Using launch script (Recommended - Cross-Platform)**
```json
{
  "mcpServers": {
    "devlens": {
      "command": "/absolute/path/to/devlens-mcp/launch_mcp.sh",
      "args": []
    }
  }
}
```

**Option 2: Direct uv command**
```json
{
  "mcpServers": {
    "devlens": {
      "command": "uv",
      "args": ["run", "python", "-m", "devlens.server"],
      "cwd": "/absolute/path/to/devlens-mcp"
    }
  }
}
```

#### **VS Code Copilot (Recommended - Cross-Platform)**

Create `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "devlens": {
      "command": "/absolute/path/to/devlens-mcp/launch_mcp.sh",
      "args": []
    }
  }
}
```

**Note:** The `launch_mcp.sh` script is **cross-platform** and automatically:
- Detects your OS (Linux/macOS/Windows)
- Locates `uv` installation (checks `~/.local/bin/uv`, `~/.cargo/bin/uv`, or system PATH)
- Uses the correct Python from `.venv` (`.venv/bin/python` on Unix, `.venv/Scripts/python.exe` on Windows)
- No manual configuration needed!

#### **Other MCP Clients**

Use STDIO transport:

```bash
uv run python -m devlens.server
```

### **Verify Installation**

Test the server is working:

```bash
# Test basic functionality
uv run python -c "from devlens.server import mcp; print('DevLens server loaded successfully')"
```

## **Usage Examples**

### **Manual Tool Usage**

```python
# Simple search
search_web("FastAPI tutorial", limit=5)

# Scrape with metadata
scrape_url("https://docs.python.org", include_metadata=True)

# Multi-source research
deep_dive("Python async best practices", depth=5, parallel=True)

# Compare perspectives
compare_sources("FastAPI vs Flask", ["url1", "url2"])
```

### **Smart Orchestration**

```python
# Let DevLens recommend the workflow
suggest_workflow("How to integrate payment API in Burkina Faso?")

# Returns:
# - Primary intent: quick_answer (50% confidence)
# - Workflow: [search_web(limit=3), scrape_url]
# - Suggested parameters optimized for intent
# - Fallback strategies if tools fail
```

### **With Context**

```python
# Provide known URLs to skip search
context = ResearchContext(known_urls=["https://docs.stripe.com"])
suggest_workflow("Stripe payment integration guide", context)

# DevLens adapts:
# - Skips search (URLs already known)
# - Goes straight to crawl_docs or scrape_url
# - Optimizes parameters based on intent
```

## **Architecture**

DevLens uses a simple, effective layered architecture—the smart bits guide the reliable bits.

* **Meta Layer** (Intelligence) \-\> suggests workflows  
* **Composed Layer** (Convenience) \-\> combines primitives  
* **Primitive Layer** (Reliability) \-\> uses adapters  
* **External Services** (The Actual Internet)

**Key Design Principles:**

* **Composability** — Tiny tools that handle huge tasks.  
* **Intelligence at the Edges** — Smart brain decides, reliable primitives execute.  
* **Token Optimization** — Maximum context, minimum token cost.  
* **Fail Explicitly** — No silent failures. We tell you exactly what broke.  
* **Developer Velocity First** — If it doesn't make you faster, we don't build it.

See ARCHITECTURE.md for the deep dive.

### **Library Stack (The Ingredients)**

| Layer | Library | Purpose | Framework |
| :---- | :---- | :---- | :---- |
| MCP | fastmcp | MCP protocol implementation |  |
| Scraping | crawl4ai | JavaScript-enabled web scraping |  |
| Search | ddgs | DuckDuckGo search (no API key) |  |
| HTTP | httpx | Fallback HTTP client |  |
| Validation | pydantic | Input/output schemas |  |

## **Features**

### **Intelligent Scraping**

* Exponential backoff retry (because the internet is flaky)  
* Metadata extraction (+41% information density)  
* Smart filtering (skips all the login/signup/spam garbage)  
* Markdown conversion (clean text for the AI)  
* Content change detection via hashing

### **Multi-Source Research**

* Parallel content fetching (3x faster)  
* Domain diversity filtering  
* Comparative analysis across sources  
* Progress tracking with success/failure reporting

### **Smart Orchestration**

* 7 research intent patterns (e.g., quick\_answer, deep\_research, comparison)  
* Dynamic workflow generation based on context  
* Parameter optimization (limits/depths automatically set for intent)  
* Fallback strategies when tools fail  
* LRU cache for insane speed (200 entries)

### **Context Awareness**

* Tracks known URLs (no redundant searches)  
* Records failed tools (so the AI doesn't try the same thing twice)  
* Adapts workflows based on research state

## **Performance (Proof We Aren't Lying)**

| Tool | Duration | Cost | Notes |
| :---- | :---- | :---- | :---- |
| search\_web | 1-2s | Low | DuckDuckGo API |
| scrape\_url | 2-5s | Low | Single page fetch |
| crawl\_docs | 10-60s | High | Multi-page crawling (big tasks take big time) |
| deep\_dive | 5-15s | Medium | Parallel scraping |
| suggest\_workflow | \<50ms | Minimal | LRU cached |

## **Documentation**

* REQUIREMENTS.md — Project scope and technical requirements  
* ARCHITECTURE.md — Software architecture and design philosophy  
* TOOLS.md — Comprehensive tool reference with examples

## **Philosophy**

The DevLens Philosophy: Make the hard stuff simple and fast.

* **Composability** — Build with small, focused primitives that combine  
* **Intelligence at the Edges** — Smart brain, reliable hands  
* **Developer Velocity** — If setup takes more than 5 minutes, it's too much.  
* **Token Economy** — Efficiency is currency.  
* **Fail Explicitly** — We tell you when something breaks.  
* **Context-Aware** — It remembers what happened.

Read the full philosophy in ARCHITECTURE.md.

## **Examples (In Action)**

### **Quick Answer**

Query: "What is FastAPI?"  
\-\> suggest\_workflow thinks: quick\_answer (50%)  
\-\> Workflow: search\_web(limit=3) \-\> scrape\_url  
\-\> Result: Fast answer from the top source. Done.

### **Deep Research**

Query: "Comprehensive guide to mobile payments in Africa"  
\-\> suggest\_workflow thinks: deep\_research (75%)  
\-\> Workflow: search\_web(limit=10) \-\> deep\_dive(depth=10, parallel=true)  
\-\> Result: Multi-source aggregated report, ready for planning.

### **Documentation Learning**

Query: "FastAPI documentation" \+ known\_url  
\-\> suggest\_workflow thinks: documentation (80%)  
\-\> Workflow: crawl\_docs(max\_pages=25) (skips search, goes straight to the docs)  
\-\> Result: Complete documentation with TOC.

### **Comparison Research**

Query: "Compare FastAPI vs Flask"  
\-\> suggest\_workflow thinks: comparison (65%)  
\-\> Workflow: search\_web \-\> scrape\_url (parallel) \-\> compare\_sources  
\-\> Result: Side-by-side analysis ready for your pull request.

## **Contributing**

Contributions welcome\! Keep it simple:

* **Add, don't modify** — New tools over changing existing ones  
* **Document why** — Explain your design choices  
* **Test everything** — All tools must have validation tests  
* **Keep it simple** — Clarity over cleverness

## **License**

MIT License \- See LICENSE for details.

  
Name origin: DevLens \= A developer's lens for viewing the web. Different tools are different lenses (wide-angle, macro, zoom), with smart auto-focus (orchestration) that picks the right lens automatically.