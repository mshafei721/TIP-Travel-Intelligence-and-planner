"""
Multi-layer scraping fallback strategy.

4-Layer fallback:
1. Official API (fastest, most reliable)
2. Playwright self-hosted (free, good for JS-heavy sites)
3. Firecrawl (paid, reliable fallback)
4. BeautifulSoup (simple HTML scraping)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class ScrapingError(Exception):
    """Base exception for scraping errors."""

    def __init__(self, message: str, url: str, method: str):
        self.message = message
        self.url = url
        self.method = method
        super().__init__(f"{method} failed for {url}: {message}")


class AllScrapersFailedError(Exception):
    """Raised when all scraping methods fail."""

    def __init__(self, url: str, attempts: list[str]):
        self.url = url
        self.attempts = attempts
        super().__init__(f"All scrapers failed for {url}. Tried: {', '.join(attempts)}")


@dataclass
class ScrapeResult:
    """Result from a successful scrape operation."""

    url: str
    content: str
    title: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    method: str = "unknown"
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    success: bool = True
    error: str | None = None


class ScrapingStrategy:
    """
    Multi-layer scraping strategy with automatic fallback.

    Usage:
        strategy = ScrapingStrategy()
        result = await strategy.scrape(url)
    """

    def __init__(
        self,
        use_playwright: bool = True,
        use_firecrawl: bool = True,
        use_beautifulsoup: bool = True,
        timeout: int = 30,
    ):
        """
        Initialize scraping strategy.

        Args:
            use_playwright: Enable Playwright for JS-heavy sites
            use_firecrawl: Enable Firecrawl as fallback
            use_beautifulsoup: Enable BeautifulSoup as last resort
            timeout: Request timeout in seconds
        """
        self.use_playwright = use_playwright
        self.use_firecrawl = use_firecrawl
        self.use_beautifulsoup = use_beautifulsoup
        self.timeout = timeout
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def scrape(
        self,
        url: str,
        method: str = "auto",
        api_handler: Callable[[str], Any] | None = None,
    ) -> ScrapeResult:
        """
        Scrape a URL with automatic fallback.

        Args:
            url: URL to scrape
            method: Scraping method ("auto", "api", "playwright", "firecrawl", "beautifulsoup")
            api_handler: Optional custom API handler for the URL

        Returns:
            ScrapeResult with content and metadata

        Raises:
            AllScrapersFailedError: When all methods fail
        """
        if method == "api" and api_handler:
            return await self._try_api(url, api_handler)

        if method != "auto":
            return await self._scrape_with_method(url, method)

        # Auto mode: try each method in order
        attempts = []
        methods = []

        # Build method list based on configuration
        if api_handler:
            methods.append(("api", lambda u: self._try_api(u, api_handler)))

        if self.use_playwright:
            methods.append(("playwright", self._try_playwright))

        if self.use_firecrawl:
            methods.append(("firecrawl", self._try_firecrawl))

        if self.use_beautifulsoup:
            methods.append(("beautifulsoup", self._try_beautifulsoup))

        for method_name, scraper in methods:
            try:
                logger.debug(f"Trying {method_name} for {url}")
                result = await scraper(url)
                if result and result.success:
                    logger.info(f"Successfully scraped {url} using {method_name}")
                    return result
            except ScrapingError as e:
                logger.warning(f"{method_name} failed for {url}: {e.message}")
                attempts.append(method_name)
            except Exception as e:
                logger.warning(f"{method_name} error for {url}: {str(e)}")
                attempts.append(method_name)

        raise AllScrapersFailedError(url, attempts)

    async def _scrape_with_method(self, url: str, method: str) -> ScrapeResult:
        """Scrape using a specific method."""
        scrapers = {
            "playwright": self._try_playwright,
            "firecrawl": self._try_firecrawl,
            "beautifulsoup": self._try_beautifulsoup,
        }

        if method not in scrapers:
            raise ValueError(f"Unknown scraping method: {method}")

        return await scrapers[method](url)

    async def _try_api(
        self, url: str, handler: Callable[[str], Any]
    ) -> ScrapeResult:
        """Try using a custom API handler."""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, handler, url
            )
            return ScrapeResult(
                url=url,
                content=str(result),
                method="api",
                metadata={"raw_result": result} if isinstance(result, dict) else {},
            )
        except Exception as e:
            raise ScrapingError(str(e), url, "api")

    async def _try_playwright(self, url: str) -> ScrapeResult:
        """Scrape using Playwright (for JS-heavy sites)."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ScrapingError(
                "Playwright not installed. Run: pip install playwright && playwright install",
                url,
                "playwright",
            )

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                try:
                    page = await browser.new_page()
                    await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)

                    # Get page content
                    content = await page.content()
                    title = await page.title()

                    # Extract main text content
                    text_content = await page.evaluate("""
                        () => {
                            // Remove scripts and styles
                            const scripts = document.querySelectorAll('script, style, noscript');
                            scripts.forEach(s => s.remove());
                            return document.body.innerText || document.body.textContent || '';
                        }
                    """)

                    return ScrapeResult(
                        url=url,
                        content=text_content,
                        title=title,
                        method="playwright",
                        metadata={"html": content[:10000]},  # First 10k chars of HTML
                    )
                finally:
                    await browser.close()

        except Exception as e:
            raise ScrapingError(str(e), url, "playwright")

    async def _try_firecrawl(self, url: str) -> ScrapeResult:
        """Scrape using Firecrawl API."""
        from app.core.config import settings

        if not settings.FIRECRAWL_API_KEY:
            raise ScrapingError("Firecrawl API key not configured", url, "firecrawl")

        try:
            client = await self._get_http_client()
            response = await client.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}",
                },
                json={"url": url, "formats": ["markdown"]},
            )

            if response.status_code == 200:
                data = response.json()
                scraped = data.get("data", {})
                return ScrapeResult(
                    url=url,
                    content=scraped.get("markdown", ""),
                    title=scraped.get("metadata", {}).get("title"),
                    method="firecrawl",
                    metadata=scraped.get("metadata", {}),
                )
            else:
                raise ScrapingError(
                    f"HTTP {response.status_code}: {response.text}",
                    url,
                    "firecrawl",
                )

        except httpx.RequestError as e:
            raise ScrapingError(str(e), url, "firecrawl")

    async def _try_beautifulsoup(self, url: str) -> ScrapeResult:
        """Scrape using BeautifulSoup (simple HTML)."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ScrapingError(
                "BeautifulSoup not installed. Run: pip install beautifulsoup4",
                url,
                "beautifulsoup",
            )

        try:
            client = await self._get_http_client()
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )

            if response.status_code != 200:
                raise ScrapingError(
                    f"HTTP {response.status_code}",
                    url,
                    "beautifulsoup",
                )

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove scripts and styles
            for script in soup(["script", "style", "noscript"]):
                script.decompose()

            # Get title
            title = soup.title.string if soup.title else None

            # Get main content
            text = soup.get_text(separator="\n", strip=True)

            return ScrapeResult(
                url=url,
                content=text,
                title=title,
                method="beautifulsoup",
                metadata={"domain": urlparse(url).netloc},
            )

        except httpx.RequestError as e:
            raise ScrapingError(str(e), url, "beautifulsoup")


# Convenience functions
async def scrape_url(url: str, method: str = "auto") -> ScrapeResult:
    """
    Quick scrape with automatic fallback.

    Args:
        url: URL to scrape
        method: Scraping method (default: auto)

    Returns:
        ScrapeResult with content
    """
    strategy = ScrapingStrategy()
    try:
        return await strategy.scrape(url, method=method)
    finally:
        await strategy.close()


def scrape_url_sync(url: str, method: str = "auto") -> ScrapeResult:
    """
    Synchronous version of scrape_url.

    Args:
        url: URL to scrape
        method: Scraping method (default: auto)

    Returns:
        ScrapeResult with content
    """
    return asyncio.run(scrape_url(url, method=method))
