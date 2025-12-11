"""
Smart tool orchestration for devlens MCP server.
Automatically selects the right tools based on user intent and research workflow.
Handles dynamic workflows, error recovery, and parameter optimization.
"""

from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from typing import List, Optional, Dict, Any, Callable


class ResearchIntent(Enum):
    """User's research intention."""

    QUICK_ANSWER = "quick_answer"  # Find one answer fast
    DEEP_RESEARCH = "deep_research"  # Comprehensive multi-source
    DOCUMENTATION = "documentation"  # Read full docs
    COMPARISON = "comparison"  # Compare multiple sources
    DISCOVERY = "discovery"  # Find related resources
    MONITORING = "monitoring"  # Track changes
    VALIDATION = "validation"  # Verify URL accessibility


@dataclass
class ToolPurpose:
    """Tool metadata with purpose and use cases."""

    name: str
    purpose: str
    use_cases: List[str]
    inputs: List[str]
    best_for: List[str]
    avoid_when: List[str]
    estimated_duration: str  # "fast", "medium", "slow"
    resource_cost: str  # "low", "medium", "high"


@dataclass
class IntentScore:
    """Scored research intent with reasoning."""

    intent: ResearchIntent
    confidence: float
    reasons: List[str]
    keywords_matched: List[str]


@dataclass
class ResearchContext:
    """Tracks research state and history."""

    known_urls: List[str] = field(default_factory=list)
    failed_tools: List[str] = field(default_factory=list)
    failure_reasons: Dict[str, str] = field(default_factory=dict)
    found_sources: List[Dict[str, Any]] = field(default_factory=list)
    previous_results: Dict[str, Any] = field(default_factory=dict)
    user_constraints: Dict[str, Any] = field(default_factory=dict)
    search_attempts: int = 0

    def add_result(self, tool: str, result: Any) -> None:
        """Record successful tool execution."""
        self.previous_results[tool] = result

    def mark_failed(self, tool: str, reason: str = "Unknown error") -> None:
        """Mark tool as failed for this session with reason."""
        if tool not in self.failed_tools:
            self.failed_tools.append(tool)
        self.failure_reasons[tool] = reason

    def has_urls(self) -> bool:
        """Check if we have any known URLs."""
        return len(self.known_urls) > 0

    def get_failure_reason(self, tool: str) -> Optional[str]:
        """Get the reason why a tool failed."""
        return self.failure_reasons.get(tool)


@dataclass
class WorkflowStep:
    """Individual workflow step with error handling."""

    tool: str
    purpose: str
    required_inputs: Dict[str, Any]
    success_criteria: Optional[Callable[[Any], bool]] = None
    fallback_step: Optional["WorkflowStep"] = None
    parallel_group: Optional[int] = None  # For parallel execution
    skip_if: Optional[Callable[[ResearchContext], bool]] = None

    def validate_inputs(self, actual_inputs: Dict[str, Any]) -> bool:
        """Check if all required inputs are provided."""
        return all(
            key in actual_inputs and actual_inputs[key] is not None
            for key in self.required_inputs.keys()
            if key != ""  # Skip placeholder keys
        )


# Tool registry with detailed metadata
TOOL_REGISTRY = {
    "search_web": ToolPurpose(
        name="search_web",
        purpose="Find relevant sources via DuckDuckGo search",
        use_cases=[
            "Starting research on new topic",
            "Finding documentation URLs",
            "Locating specific resources",
            "Getting region-specific results",
        ],
        inputs=["query", "limit", "region", "safe_search"],
        best_for=[
            "Broad topic exploration",
            "Finding authoritative sources",
            "Quick source discovery",
        ],
        avoid_when=[
            "You already have specific URLs",
            "Need deep content analysis",
            "Require full documentation",
        ],
        estimated_duration="fast",
        resource_cost="low",
    ),
    "scrape_url": ToolPurpose(
        name="scrape_url",
        purpose="Extract content from a single URL as Markdown",
        use_cases=[
            "Reading specific documentation page",
            "Extracting article content",
            "Getting detailed information from known URL",
        ],
        inputs=["url", "include_metadata"],
        best_for=[
            "Single page analysis",
            "Authoritative source content",
            "Specific documentation pages",
        ],
        avoid_when=[
            "URL is unknown",
            "Need multiple pages",
            "Require site-wide crawling",
        ],
        estimated_duration="fast",
        resource_cost="low",
    ),
    "crawl_docs": ToolPurpose(
        name="crawl_docs",
        purpose="Crawl multi-page documentation with smart filtering",
        use_cases=[
            "Learning new framework/library",
            "Building local knowledge base",
            "Comprehensive documentation review",
        ],
        inputs=["root_url", "max_pages", "follow_external"],
        best_for=[
            "Complete documentation ingestion",
            "Framework/library learning",
            "Building comprehensive context",
        ],
        avoid_when=[
            "Need quick single answer",
            "Unclear starting point",
            "Rate limiting concerns",
        ],
        estimated_duration="slow",
        resource_cost="high",
    ),
    "deep_dive": ToolPurpose(
        name="deep_dive",
        purpose="Multi-source research with parallel fetching",
        use_cases=[
            "Thorough topic research",
            "Synthesizing multiple perspectives",
            "Building comprehensive reports",
        ],
        inputs=["topic", "depth", "parallel"],
        best_for=[
            "Complex topics needing multiple sources",
            "Comparative analysis needs",
            "Building thorough understanding",
        ],
        avoid_when=[
            "Need single authoritative source",
            "Very specific question",
            "Time-sensitive quick lookup",
        ],
        estimated_duration="medium",
        resource_cost="medium",
    ),
    "summarize_page": ToolPurpose(
        name="summarize_page",
        purpose="Quick page structure overview without full content",
        use_cases=[
            "Triaging multiple pages",
            "Deciding if full scrape needed",
            "Getting quick page structure",
        ],
        inputs=["url"],
        best_for=[
            "Quick relevance checks",
            "Page structure understanding",
            "Pre-scraping triage",
        ],
        avoid_when=[
            "Need full content",
            "Detailed analysis required",
            "Already know page is relevant",
        ],
        estimated_duration="fast",
        resource_cost="low",
    ),
    "compare_sources": ToolPurpose(
        name="compare_sources",
        purpose="Analyze multiple sources for consensus/differences",
        use_cases=[
            "Comparing different perspectives",
            "Finding consensus points",
            "Analyzing implementations",
        ],
        inputs=["topic", "sources"],
        best_for=[
            "Multiple known sources to compare",
            "Finding common ground",
            "Analyzing disagreements",
        ],
        avoid_when=[
            "Don't have specific sources yet",
            "Need single perspective",
            "Sources unrelated to each other",
        ],
        estimated_duration="medium",
        resource_cost="medium",
    ),
    "find_related": ToolPurpose(
        name="find_related",
        purpose="Discover related pages via content analysis",
        use_cases=[
            "Finding similar resources",
            "Exploring topic broadly",
            "Discovering alternatives",
        ],
        inputs=["url", "limit"],
        best_for=[
            "Have good initial resource",
            "Want broader coverage",
            "Discovering alternatives",
        ],
        avoid_when=[
            "Starting from scratch",
            "Need comprehensive coverage",
            "Unclear initial source",
        ],
        estimated_duration="medium",
        resource_cost="medium",
    ),
    "extract_links": ToolPurpose(
        name="extract_links",
        purpose="Categorize all internal/external links",
        use_cases=[
            "Understanding site structure",
            "Finding navigation patterns",
            "Building sitemap",
        ],
        inputs=["url", "filter_external"],
        best_for=["Site exploration", "Navigation discovery", "Pre-crawl planning"],
        avoid_when=["Need actual content", "Links not important", "Single page focus"],
        estimated_duration="fast",
        resource_cost="low",
    ),
    "monitor_changes": ToolPurpose(
        name="monitor_changes",
        purpose="Track content changes via hashing",
        use_cases=[
            "Monitoring documentation updates",
            "Tracking blog/news changes",
            "Detecting modifications",
        ],
        inputs=["url", "previous_hash"],
        best_for=["Periodic update checks", "Change detection", "Version tracking"],
        avoid_when=[
            "First time checking",
            "Don't need change tracking",
            "Real-time monitoring",
        ],
        estimated_duration="fast",
        resource_cost="low",
    ),
    "validate_url": ToolPurpose(
        name="validate_url",
        purpose="Check if URL is accessible before processing",
        use_cases=[
            "Pre-flight URL validation",
            "Avoiding 404 errors",
            "Checking redirects",
        ],
        inputs=["url"],
        best_for=[
            "Before expensive operations",
            "Batch URL validation",
            "Error prevention",
        ],
        avoid_when=[
            "URL from trusted source",
            "Time critical operations",
            "Already validated",
        ],
        estimated_duration="fast",
        resource_cost="low",
    ),
}


# Intent classification patterns with priorities
INTENT_PATTERNS = {
    ResearchIntent.DOCUMENTATION: {
        "keywords": [
            "documentation",
            "docs",
            "api reference",
            "guide",
            "tutorial",
            "manual",
            "handbook",
            "specification",
        ],
        "priority": 8,
        "conflicts_with": [],
    },
    ResearchIntent.COMPARISON: {
        "keywords": [
            "compare",
            "difference",
            "versus",
            "vs",
            "better than",
            "advantages",
            "pros cons",
            "which",
            "between",
        ],
        "priority": 7,
        "conflicts_with": [],
    },
    ResearchIntent.DEEP_RESEARCH: {
        "keywords": [
            "research",
            "comprehensive",
            "everything about",
            "deep dive",
            "thorough",
            "complete",
            "exhaustive",
            "in-depth",
        ],
        "priority": 6,
        "conflicts_with": [ResearchIntent.QUICK_ANSWER],
    },
    ResearchIntent.DISCOVERY: {
        "keywords": [
            "related",
            "similar",
            "alternatives",
            "also",
            "other",
            "like",
            "find more",
            "explore",
        ],
        "priority": 5,
        "conflicts_with": [],
    },
    ResearchIntent.MONITORING: {
        "keywords": [
            "changed",
            "updated",
            "new version",
            "check",
            "monitor",
            "track",
            "latest",
            "recent changes",
        ],
        "priority": 9,
        "conflicts_with": [],
    },
    ResearchIntent.VALIDATION: {
        "keywords": [
            "check if",
            "verify",
            "validate",
            "exists",
            "accessible",
            "working",
            "available",
        ],
        "priority": 7,
        "conflicts_with": [],
    },
    ResearchIntent.QUICK_ANSWER: {
        "keywords": ["what is", "how to", "quick", "simple", "just", "only"],
        "priority": 3,
        "conflicts_with": [ResearchIntent.DEEP_RESEARCH],
    },
}


@lru_cache(maxsize=200)
def _classify_intent_cached(
    query_lower: str, has_urls: bool, search_attempts: int
) -> tuple:
    """Cached intent classification for identical queries.

    Args:
        query_lower: Lowercase query string
        has_urls: Whether context has URLs
        search_attempts: Number of search attempts

    Returns:
        Tuple of (intent_type, confidence, keywords, reasons) for caching
    """
    scores = []

    # Check each intent pattern
    for intent, pattern in INTENT_PATTERNS.items():
        matched_keywords = [kw for kw in pattern["keywords"] if kw in query_lower]

        if matched_keywords:
            # Base confidence on number of matches and priority
            base_confidence = len(matched_keywords) * 0.15
            priority_boost = pattern["priority"] * 0.05
            confidence = min(0.95, base_confidence + priority_boost)

            # Adjust based on context
            if intent == ResearchIntent.QUICK_ANSWER and search_attempts > 2:
                confidence *= 0.5  # Probably need deeper research
            elif intent == ResearchIntent.DEEP_RESEARCH and has_urls:
                confidence *= 1.2  # We have starting points

            reasons = [
                f"Matched keywords: {', '.join(matched_keywords)}",
                f"Priority level: {pattern['priority']}/10",
            ]

            scores.append(
                (intent.value, confidence, tuple(matched_keywords), tuple(reasons))
            )

    # Add default if nothing matched
    if not scores:
        scores.append(
            (
                ResearchIntent.QUICK_ANSWER.value,
                0.5,
                tuple(),
                ("Default fallback - no specific intent detected",),
            )
        )

    return tuple(scores)


def classify_intent(
    query: str, context: Optional[ResearchContext] = None
) -> List[IntentScore]:
    """
    Classify user's research intent from query with confidence scores.

    Args:
        query: User's research query
        context: Optional research context for additional signals

    Returns:
        List of IntentScore objects ranked by confidence
    """
    query_lower = query.lower()
    has_urls = context.has_urls() if context else False
    search_attempts = context.search_attempts if context else 0

    # Use cached classification
    cached_scores = _classify_intent_cached(query_lower, has_urls, search_attempts)

    # Convert back to IntentScore objects
    scores = [
        IntentScore(
            intent=ResearchIntent(intent_value),
            confidence=confidence,
            reasons=list(reasons),
            keywords_matched=list(keywords),
        )
        for intent_value, confidence, keywords, reasons in cached_scores
    ]

    # Filter out conflicting intents (keep highest confidence)
    filtered_scores = []
    intents_added = set()

    for score in sorted(scores, key=lambda x: x.confidence, reverse=True):
        conflicts = INTENT_PATTERNS[score.intent]["conflicts_with"]
        if not any(conflict in intents_added for conflict in conflicts):
            filtered_scores.append(score)
            intents_added.add(score.intent)

    return sorted(filtered_scores, key=lambda x: x.confidence, reverse=True)


def suggest_parameters(
    tool_name: str, intent: ResearchIntent, context: ResearchContext
) -> Dict[str, Any]:
    """
    Suggest optimal parameters for a tool based on intent and context.

    Args:
        tool_name: Name of the tool
        intent: Primary research intent
        context: Current research context

    Returns:
        Dictionary of suggested parameters
    """
    params = {}

    if tool_name == "crawl_docs":
        if intent == ResearchIntent.QUICK_ANSWER:
            params["max_pages"] = 5
            params["follow_external"] = False
        elif intent == ResearchIntent.DEEP_RESEARCH:
            params["max_pages"] = 100
            params["follow_external"] = True
        else:
            params["max_pages"] = 25
            params["follow_external"] = False

    elif tool_name == "search_web":
        if intent == ResearchIntent.QUICK_ANSWER:
            params["limit"] = 3
        elif intent == ResearchIntent.DEEP_RESEARCH:
            params["limit"] = 10
        else:
            params["limit"] = 5

        # Increase limit if previous searches failed
        if context.search_attempts > 1:
            params["limit"] = min(15, params["limit"] * 2)

    elif tool_name == "deep_dive":
        if intent == ResearchIntent.DEEP_RESEARCH:
            params["depth"] = 10
            params["parallel"] = True
        elif intent == ResearchIntent.QUICK_ANSWER:
            params["depth"] = 3
            params["parallel"] = False
        else:
            params["depth"] = 5
            params["parallel"] = True

    elif tool_name == "find_related":
        if intent == ResearchIntent.DISCOVERY:
            params["limit"] = 10
        else:
            params["limit"] = 5

    return params


def build_dynamic_workflow(
    primary_intent: IntentScore,
    context: ResearchContext,
    secondary_intents: List[IntentScore] = None,
) -> List[WorkflowStep]:
    """
    Build a dynamic workflow based on intent and context.

    Args:
        primary_intent: Primary research intent with score
        context: Current research context
        secondary_intents: Additional intents to consider

    Returns:
        List of workflow steps with fallbacks
    """
    intent = primary_intent.intent
    workflow = []

    # QUICK_ANSWER workflow
    if intent == ResearchIntent.QUICK_ANSWER:
        if context.has_urls():
            # Skip search if we already have URLs
            workflow.append(
                WorkflowStep(
                    tool="scrape_url",
                    purpose="Extract content from known URL",
                    required_inputs={"url": context.known_urls[0]},
                    skip_if=lambda ctx: not ctx.has_urls(),
                )
            )
        else:
            workflow.append(
                WorkflowStep(
                    tool="search_web",
                    purpose="Find top result",
                    required_inputs={"query": "", "limit": 3},
                    success_criteria=lambda result: result and len(result) > 0,
                    fallback_step=WorkflowStep(
                        tool="search_web",
                        purpose="Retry with broader query",
                        required_inputs={"query": "", "limit": 5},
                    ),
                )
            )
            workflow.append(
                WorkflowStep(
                    tool="scrape_url",
                    purpose="Get content from best result",
                    required_inputs={"url": ""},
                    fallback_step=WorkflowStep(
                        tool="deep_dive",
                        purpose="Multi-source fallback",
                        required_inputs={"topic": "", "depth": 3},
                    ),
                )
            )

    # DEEP_RESEARCH workflow
    elif intent == ResearchIntent.DEEP_RESEARCH:
        if not context.has_urls():
            workflow.append(
                WorkflowStep(
                    tool="search_web",
                    purpose="Find authoritative sources",
                    required_inputs={"query": "", "limit": 10},
                )
            )

        workflow.append(
            WorkflowStep(
                tool="deep_dive",
                purpose="Comprehensive multi-source research",
                required_inputs={"topic": "", "depth": 10, "parallel": True},
            )
        )

    # DOCUMENTATION workflow
    elif intent == ResearchIntent.DOCUMENTATION:
        if context.has_urls():
            workflow.append(
                WorkflowStep(
                    tool="validate_url",
                    purpose="Check documentation URL",
                    required_inputs={"url": context.known_urls[0]},
                )
            )
            workflow.append(
                WorkflowStep(
                    tool="crawl_docs",
                    purpose="Ingest documentation",
                    required_inputs={
                        "root_url": context.known_urls[0],
                        "max_pages": 25,
                    },
                )
            )
        else:
            workflow.append(
                WorkflowStep(
                    tool="search_web",
                    purpose="Find official documentation",
                    required_inputs={"query": "", "limit": 5},
                )
            )
            workflow.append(
                WorkflowStep(
                    tool="crawl_docs",
                    purpose="Ingest found documentation",
                    required_inputs={"root_url": "", "max_pages": 25},
                )
            )

    # COMPARISON workflow
    elif intent == ResearchIntent.COMPARISON:
        if len(context.known_urls) >= 2:
            # Parallel scraping of known sources
            workflow.append(
                WorkflowStep(
                    tool="scrape_url",
                    purpose="Get first source",
                    required_inputs={"url": context.known_urls[0]},
                    parallel_group=1,
                )
            )
            workflow.append(
                WorkflowStep(
                    tool="scrape_url",
                    purpose="Get second source",
                    required_inputs={"url": context.known_urls[1]},
                    parallel_group=1,
                )
            )
        else:
            workflow.append(
                WorkflowStep(
                    tool="search_web",
                    purpose="Find sources to compare",
                    required_inputs={"query": "", "limit": 5},
                )
            )

        workflow.append(
            WorkflowStep(
                tool="compare_sources",
                purpose="Analyze differences and consensus",
                required_inputs={"topic": "", "sources": []},
            )
        )

    # DISCOVERY workflow
    elif intent == ResearchIntent.DISCOVERY:
        if context.has_urls():
            workflow.append(
                WorkflowStep(
                    tool="find_related",
                    purpose="Discover related resources",
                    required_inputs={"url": context.known_urls[0], "limit": 10},
                )
            )
        else:
            workflow.append(
                WorkflowStep(
                    tool="search_web",
                    purpose="Find initial resource",
                    required_inputs={"query": "", "limit": 5},
                )
            )
            workflow.append(
                WorkflowStep(
                    tool="find_related",
                    purpose="Discover related pages",
                    required_inputs={"url": "", "limit": 10},
                )
            )

    # MONITORING workflow
    elif intent == ResearchIntent.MONITORING:
        workflow.append(
            WorkflowStep(
                tool="monitor_changes",
                purpose="Check for content updates",
                required_inputs={"url": "", "previous_hash": None},
            )
        )

    # VALIDATION workflow
    elif intent == ResearchIntent.VALIDATION:
        workflow.append(
            WorkflowStep(
                tool="validate_url",
                purpose="Check URL accessibility",
                required_inputs={"url": ""},
            )
        )

    return workflow


def get_tool_info(tool_name: str) -> Optional[ToolPurpose]:
    """
    Get detailed info about a tool.

    Args:
        tool_name: Name of the tool

    Returns:
        ToolPurpose object or None if not found
    """
    return TOOL_REGISTRY.get(tool_name)


def suggest_tools(
    query: str, context: Optional[ResearchContext] = None
) -> Dict[str, Any]:
    """
    Suggest optimal tools and workflow for user query.

    Args:
        query: User's research question
        context: Optional research context

    Returns:
        Dictionary with intents, workflow, and tool details
    """
    if context is None:
        context = ResearchContext()

    # Classify intent with confidence scores
    intent_scores = classify_intent(query, context)
    primary_intent = intent_scores[0]
    secondary_intents = intent_scores[1:3] if len(intent_scores) > 1 else []

    # Build dynamic workflow
    workflow = build_dynamic_workflow(primary_intent, context, secondary_intents)

    # Suggest parameters for each step
    workflow_with_params = []
    for i, step in enumerate(workflow):
        suggested_params = suggest_parameters(step.tool, primary_intent.intent, context)

        tool_info = get_tool_info(step.tool)

        workflow_with_params.append(
            {
                "step": i + 1,
                "tool": step.tool,
                "purpose": step.purpose,
                "suggested_parameters": suggested_params,
                "required_inputs": step.required_inputs,
                "has_fallback": step.fallback_step is not None,
                "parallel_group": step.parallel_group,
                "tool_details": tool_info.__dict__ if tool_info else None,
            }
        )

    return {
        "primary_intent": {
            "type": primary_intent.intent.value,
            "confidence": primary_intent.confidence,
            "reasons": primary_intent.reasons,
            "keywords": primary_intent.keywords_matched,
        },
        "secondary_intents": [
            {
                "type": score.intent.value,
                "confidence": score.confidence,
                "reasons": score.reasons,
            }
            for score in secondary_intents
        ],
        "workflow": workflow_with_params,
        "context_notes": {
            "has_known_urls": context.has_urls(),
            "failed_tools": context.failed_tools,
            "failure_reasons": context.failure_reasons,
            "search_attempts": context.search_attempts,
        },
        "explanation": (
            f"Detected {primary_intent.intent.value} intent with "
            f"{primary_intent.confidence:.0%} confidence. "
            f"Recommended {len(workflow)}-step workflow"
            + (
                f" with {len(secondary_intents)} secondary intents."
                if secondary_intents
                else "."
            )
        ),
    }


def update_context_from_result(
    context: ResearchContext,
    tool: str,
    result: Any,
    success: bool,
    error_message: str = "",
) -> ResearchContext:
    """
    Update research context based on tool execution result.

    Args:
        context: Current research context
        tool: Tool that was executed
        result: Result from tool execution
        success: Whether execution was successful
        error_message: Error message if execution failed

    Returns:
        Updated research context
    """
    if success:
        context.add_result(tool, result)

        # Extract URLs from search results
        if tool == "search_web" and isinstance(result, list):
            for item in result:
                if isinstance(item, dict) and "url" in item:
                    if item["url"] not in context.known_urls:
                        context.known_urls.append(item["url"])
            context.search_attempts += 1
    else:
        context.mark_failed(tool, error_message or "Unknown error")

    return context


# Example usage
if __name__ == "__main__":
    # Example 1: Quick answer
    result = suggest_tools("What is FastAPI?")
    print("Quick Answer Query:", result["explanation"])
    print()

    # Example 2: Deep research with context
    ctx = ResearchContext(known_urls=["https://fastapi.tiangolo.com"])
    result = suggest_tools("comprehensive guide to FastAPI", context=ctx)
    print("Deep Research with Context:", result["explanation"])
    print()

    # Example 3: Comparison
    result = suggest_tools("compare FastAPI vs Flask performance")
    print("Comparison Query:", result["explanation"])
    for step in result["workflow"]:
        print(f"  Step {step['step']}: {step['tool']} - {step['purpose']}")
    print()

    # Example 4: Context with failures
    ctx = ResearchContext()
    ctx = update_context_from_result(ctx, "search_web", [], False, "Network timeout")
    result = suggest_tools("Python tutorials", context=ctx)
    print("With Failed Tool:", result["context_notes"])
