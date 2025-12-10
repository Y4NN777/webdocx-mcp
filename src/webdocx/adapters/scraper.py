"""Web scraping adapter."""

import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from readability import Document as ReadabilityDocument

from webdocx.models.document import Document, PageSummary, Section
from webdocx.models.errors import ScrapingError


class ScraperAdapter:
    """Adapter for web scraping."""

    def __init__(self, timeout: float = 30.0):
        """Initialize scraper adapter.

        Args:
            timeout: Request timeout in seconds.
        """
        self._timeout = timeout
        self._headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WebDocx/1.0; +https://github.com/Y4NN777/webdocx-mcp)"
        }

    async def fetch(self, url: str) -> Document:
        """Fetch and parse a URL into a Document.

        Args:
            url: URL to fetch.

        Returns:
            Document with markdown content.

        Raises:
            ScrapingError: If fetching or parsing fails.
        """
        if not url.strip():
            raise ScrapingError(url, "URL cannot be empty")

        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self._headers)
                response.raise_for_status()
                html = response.text

            # Use readability to extract main content
            doc = ReadabilityDocument(html)
            title = doc.title()
            content_html = doc.summary()

            # Convert to markdown-ish format
            content = self._html_to_markdown(content_html)

            # Add source attribution
            markdown = f"# {title}\n\n> Source: {url}\n\n{content}"

            return Document(
                url=url,
                title=title,
                content=markdown,
                fetched_at=datetime.now(),
            )

        except httpx.TimeoutException:
            raise ScrapingError(url, "Request timed out")
        except httpx.HTTPStatusError as e:
            raise ScrapingError(url, f"HTTP {e.response.status_code}")
        except Exception as e:
            raise ScrapingError(url, str(e)) from e

    async def summarize(self, url: str) -> PageSummary:
        """Extract page structure without full content.

        Args:
            url: URL to summarize.

        Returns:
            PageSummary with sections.

        Raises:
            ScrapingError: If fetching or parsing fails.
        """
        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self._headers)
                response.raise_for_status()
                html = response.text

            soup = BeautifulSoup(html, "html.parser")

            # Extract title
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            # Extract headings as sections
            sections: list[Section] = []
            for heading in soup.find_all(["h1", "h2", "h3"]):
                text = heading.get_text(strip=True)
                if text:
                    # Get next sibling paragraph as summary if exists
                    summary = ""
                    next_elem = heading.find_next_sibling(["p", "div"])
                    if next_elem:
                        summary = next_elem.get_text(strip=True)[:200]
                    sections.append(Section(heading=text, summary=summary))

            return PageSummary(url=url, title=title, sections=sections)

        except httpx.TimeoutException:
            raise ScrapingError(url, "Request timed out")
        except httpx.HTTPStatusError as e:
            raise ScrapingError(url, f"HTTP {e.response.status_code}")
        except Exception as e:
            raise ScrapingError(url, str(e)) from e

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to basic markdown.

        Args:
            html: HTML content.

        Returns:
            Markdown-formatted text.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for elem in soup(["script", "style", "nav", "footer", "header"]):
            elem.decompose()

        # Convert headings
        for i, tag in enumerate(["h1", "h2", "h3", "h4", "h5", "h6"]):
            for heading in soup.find_all(tag):
                prefix = "#" * (i + 1)
                heading.replace_with(f"\n\n{prefix} {heading.get_text(strip=True)}\n\n")

        # Convert links
        for link in soup.find_all("a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if href and text:
                link.replace_with(f"[{text}]({href})")

        # Convert bold/strong
        for tag in soup.find_all(["strong", "b"]):
            tag.replace_with(f"**{tag.get_text(strip=True)}**")

        # Convert italic/em
        for tag in soup.find_all(["em", "i"]):
            tag.replace_with(f"*{tag.get_text(strip=True)}*")

        # Convert code
        for tag in soup.find_all("code"):
            tag.replace_with(f"`{tag.get_text(strip=True)}`")

        # Convert lists
        for ul in soup.find_all("ul"):
            items = ul.find_all("li")
            md_list = "\n".join(f"- {li.get_text(strip=True)}" for li in items)
            ul.replace_with(f"\n{md_list}\n")

        for ol in soup.find_all("ol"):
            items = ol.find_all("li")
            md_list = "\n".join(f"{i+1}. {li.get_text(strip=True)}" for i, li in enumerate(items))
            ol.replace_with(f"\n{md_list}\n")

        # Get text and clean up
        text = soup.get_text()

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        return text.strip()

    def get_same_domain_links(self, html: str, base_url: str) -> list[str]:
        """Extract same-domain links from HTML.

        Args:
            html: HTML content.
            base_url: Base URL for resolving relative links.

        Returns:
            List of absolute URLs on the same domain.
        """
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(base_url).netloc

        links: list[str] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)

            # Same domain, http(s), no fragments/anchors only
            if (
                parsed.netloc == base_domain
                and parsed.scheme in ("http", "https")
                and parsed.path  # Has a path
            ):
                # Remove fragment
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean_url not in links:
                    links.append(clean_url)

        return links
