"""Document-related models."""

from datetime import datetime
from pydantic import BaseModel, Field


class Section(BaseModel):
    """A section extracted from a page."""

    heading: str = Field(..., description="Section heading")
    summary: str = Field(default="", description="Brief summary of section content")


class Document(BaseModel):
    """Scraped document content."""

    url: str = Field(..., description="Source URL")
    title: str = Field(default="", description="Page title")
    content: str = Field(..., description="Markdown content")
    fetched_at: datetime = Field(default_factory=datetime.now, description="When fetched")


class PageSummary(BaseModel):
    """Summary of a page without full content."""

    url: str = Field(..., description="Source URL")
    title: str = Field(default="", description="Page title")
    sections: list[Section] = Field(default_factory=list, description="Extracted sections")
