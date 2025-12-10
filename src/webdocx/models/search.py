"""Search-related models."""

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Input for web search."""

    query: str = Field(..., description="Search query string")
    limit: int = Field(default=5, ge=1, le=20, description="Max results to return")


class SearchResult(BaseModel):
    """A single search result."""

    title: str = Field(..., description="Page title")
    url: str = Field(..., description="Page URL")
    snippet: str = Field(default="", description="Text snippet from the page")
