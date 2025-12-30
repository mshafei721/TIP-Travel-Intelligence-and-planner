"""
Scraping module with multi-layer fallback strategy.

Provides a unified interface for web scraping with automatic fallback:
1. API first (fastest, most reliable)
2. Playwright for JS-heavy sites (self-hosted, free)
3. Firecrawl (paid service, reliable fallback)
4. BeautifulSoup for simple HTML (last resort)
"""

from app.scrapers.base import (
    ScrapingStrategy,
    ScrapeResult,
    ScrapingError,
    AllScrapersFailedError,
)

__all__ = [
    "ScrapingStrategy",
    "ScrapeResult",
    "ScrapingError",
    "AllScrapersFailedError",
]
