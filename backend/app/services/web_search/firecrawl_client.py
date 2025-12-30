"""
Firecrawl API Client

Provides web search and scraping capabilities for agents
that need real-time information from the web.
"""

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

FIRECRAWL_API_URL = "https://api.firecrawl.dev/v1"


class FirecrawlClient:
    """Client for Firecrawl web search and scraping API."""

    def __init__(self, api_key: str | None = None):
        """
        Initialize Firecrawl client.

        Args:
            api_key: Firecrawl API key (defaults to settings)
        """
        self.api_key = api_key or settings.FIRECRAWL_API_KEY
        self.base_url = FIRECRAWL_API_URL
        self._client = httpx.Client(timeout=30.0)

    def _headers(self) -> dict[str, str]:
        """Get request headers with auth."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def search(
        self,
        query: str,
        limit: int = 5,
        scrape_content: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Search the web using Firecrawl.

        Args:
            query: Search query string
            limit: Maximum number of results (default: 5)
            scrape_content: Whether to scrape page content (default: True)

        Returns:
            List of search results with title, url, and content
        """
        if not self.api_key:
            logger.warning("Firecrawl API key not configured")
            return []

        try:
            payload = {
                "query": query,
                "limit": limit,
            }

            if scrape_content:
                payload["scrapeOptions"] = {
                    "formats": ["markdown"],
                }

            response = self._client.post(
                f"{self.base_url}/search",
                headers=self._headers(),
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("data", [])
                logger.info(f"Firecrawl search returned {len(results)} results for: {query}")
                return results
            else:
                logger.error(f"Firecrawl search failed: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.error(f"Firecrawl search error: {e}")
            return []

    def scrape(self, url: str) -> dict[str, Any] | None:
        """
        Scrape a specific URL.

        Args:
            url: URL to scrape

        Returns:
            Scraped content with markdown and metadata
        """
        if not self.api_key:
            logger.warning("Firecrawl API key not configured")
            return None

        try:
            response = self._client.post(
                f"{self.base_url}/scrape",
                headers=self._headers(),
                json={
                    "url": url,
                    "formats": ["markdown"],
                },
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data")
            else:
                logger.error(f"Firecrawl scrape failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Firecrawl scrape error: {e}")
            return None

    def close(self):
        """Close the HTTP client."""
        self._client.close()


# Convenience function for quick searches
def search_web(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Quick web search using Firecrawl.

    Args:
        query: Search query
        limit: Max results

    Returns:
        List of search results
    """
    client = FirecrawlClient()
    try:
        return client.search(query, limit=limit)
    finally:
        client.close()
