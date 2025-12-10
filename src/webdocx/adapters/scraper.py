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
    """Adapter for web scraping using crawl4ai with httpx fallback."""

    def __init__(self, timeout: float = 30.0):
        """Initialize scraper adapter.

        Args:
            timeout: Request timeout in seconds.
        """
        self._timeout = timeout
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self._crawl4ai_available = True

    async def fetch(self, url: str, *, retry: int = 2) -> Document:
        """Fetch and parse a URL into a Document.

        Uses crawl4ai for JS-heavy pages, falls back to httpx+readability.

        Args:
            url: URL to fetch.
            retry: Number of retry attempts on failure.

        Returns:
            Document with markdown content.

        Raises:
            ScrapingError: If fetching or parsing fails after all retries.
        """
        if not url.strip():
            raise ScrapingError(url, "URL cannot be empty")

        # Validate URL format
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ScrapingError(url, "Invalid URL format")

        last_error = None
        for attempt in range(retry + 1):
            try:
                # Try crawl4ai first for better JS support
                if self._crawl4ai_available:
                    try:
                        return await self._fetch_with_crawl4ai(url)
                    except Exception as e:
                        last_error = e
                        # Fall back to httpx if crawl4ai fails
                        pass

                # Fallback to httpx + readability
                return await self._fetch_with_httpx(url)

            except ScrapingError as e:
                if attempt == retry:
                    raise
                last_error = e
                # Wait before retry (exponential backoff)
                import asyncio

                await asyncio.sleep(2**attempt)
            except Exception as e:
                last_error = e
                if attempt == retry:
                    raise ScrapingError(
                        url, f"Failed after {retry + 1} attempts: {e}"
                    ) from e
                await asyncio.sleep(2**attempt)

        raise ScrapingError(url, f"Failed after all retries: {last_error}")

    async def _fetch_with_crawl4ai(self, url: str) -> Document:
        """Fetch using crawl4ai (handles JavaScript).

        Args:
            url: URL to fetch.

        Returns:
            Document with markdown content.
        """
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

        browser_config = BrowserConfig(
            headless=True,
            verbose=False,
        )

        run_config = CrawlerRunConfig(
            wait_until="domcontentloaded",
            page_timeout=int(self._timeout * 1000),
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)

            if not result.success:
                raise ScrapingError(url, result.error_message or "Crawl failed")

            title = result.metadata.get("title", "") if result.metadata else ""
            content = result.markdown or ""

            # Add source attribution
            markdown = f"# {title}\n\n> Source: {url}\n\n{content}"

            return Document(
                url=url,
                title=title,
                content=markdown,
                fetched_at=datetime.now(),
            )

    async def _fetch_with_httpx(self, url: str) -> Document:
        """Fetch using httpx + readability (fallback for static pages).

        Args:
            url: URL to fetch.

        Returns:
            Document with markdown content.
        """
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, follow_redirects=True
            ) as client:
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
        # Use crawl4ai for better JS support
        if self._crawl4ai_available:
            try:
                return await self._summarize_with_crawl4ai(url)
            except Exception:
                pass

        # Fallback
        return await self._summarize_with_httpx(url)

    async def _summarize_with_crawl4ai(self, url: str) -> PageSummary:
        """Summarize using crawl4ai."""
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

        browser_config = BrowserConfig(headless=True, verbose=False)
        run_config = CrawlerRunConfig(
            wait_until="domcontentloaded",
            page_timeout=int(self._timeout * 1000),
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)

            if not result.success:
                raise ScrapingError(url, result.error_message or "Crawl failed")

            title = result.metadata.get("title", "") if result.metadata else ""
            html = result.html or ""

            soup = BeautifulSoup(html, "html.parser")
            sections: list[Section] = []

            for heading in soup.find_all(["h1", "h2", "h3"]):
                text = heading.get_text(strip=True)
                if text:
                    summary = ""
                    next_elem = heading.find_next_sibling(["p", "div"])
                    if next_elem:
                        summary = next_elem.get_text(strip=True)[:200]
                    sections.append(Section(heading=text, summary=summary))

            return PageSummary(url=url, title=title, sections=sections)

    async def _summarize_with_httpx(self, url: str) -> PageSummary:
        """Summarize using httpx (fallback)."""
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, follow_redirects=True
            ) as client:
                response = await client.get(url, headers=self._headers)
                response.raise_for_status()
                html = response.text

            soup = BeautifulSoup(html, "html.parser")

            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            sections: list[Section] = []
            for heading in soup.find_all(["h1", "h2", "h3"]):
                text = heading.get_text(strip=True)
                if text:
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
        """Convert HTML to basic markdown."""
        soup = BeautifulSoup(html, "html.parser")

        for elem in soup(["script", "style", "nav", "footer", "header"]):
            elem.decompose()

        for i, tag in enumerate(["h1", "h2", "h3", "h4", "h5", "h6"]):
            for heading in soup.find_all(tag):
                prefix = "#" * (i + 1)
                heading.replace_with(f"\n\n{prefix} {heading.get_text(strip=True)}\n\n")

        for link in soup.find_all("a"):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if href and text:
                link.replace_with(f"[{text}]({href})")

        for tag in soup.find_all(["strong", "b"]):
            tag.replace_with(f"**{tag.get_text(strip=True)}**")

        for tag in soup.find_all(["em", "i"]):
            tag.replace_with(f"*{tag.get_text(strip=True)}*")

        for tag in soup.find_all("code"):
            tag.replace_with(f"`{tag.get_text(strip=True)}`")

        for ul in soup.find_all("ul"):
            items = ul.find_all("li")
            md_list = "\n".join(f"- {li.get_text(strip=True)}" for li in items)
            ul.replace_with(f"\n{md_list}\n")

        for ol in soup.find_all("ol"):
            items = ol.find_all("li")
            md_list = "\n".join(
                f"{i + 1}. {li.get_text(strip=True)}" for i, li in enumerate(items)
            )
            ol.replace_with(f"\n{md_list}\n")

        text = soup.get_text()
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        return text.strip()

    def get_same_domain_links(self, html: str, base_url: str) -> list[str]:
        """Extract same-domain links from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        base_domain = urlparse(base_url).netloc

        links: list[str] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)

            if (
                parsed.netloc == base_domain
                and parsed.scheme in ("http", "https")
                and parsed.path
            ):
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean_url not in links:
                    links.append(clean_url)

        return links
