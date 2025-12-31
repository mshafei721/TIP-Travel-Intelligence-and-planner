"""
Tests for the scraping fallback layer.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.scrapers.base import (
    ScrapingStrategy,
    ScrapeResult,
    ScrapingError,
    AllScrapersFailedError,
)


class TestScrapeResult:
    """Test ScrapeResult dataclass."""

    def test_scrape_result_basic(self):
        """Test basic ScrapeResult creation."""
        result = ScrapeResult(
            url="https://example.com",
            content="Test content",
            method="test",
        )
        assert result.url == "https://example.com"
        assert result.content == "Test content"
        assert result.method == "test"
        assert result.success is True
        assert result.error is None

    def test_scrape_result_with_metadata(self):
        """Test ScrapeResult with all fields."""
        result = ScrapeResult(
            url="https://example.com",
            content="Test content",
            title="Test Title",
            method="beautifulsoup",
            metadata={"key": "value"},
        )
        assert result.title == "Test Title"
        assert result.metadata == {"key": "value"}


class TestScrapingError:
    """Test ScrapingError exception."""

    def test_scraping_error_message(self):
        """Test error message formatting."""
        error = ScrapingError("Connection timeout", "https://example.com", "playwright")
        assert "playwright failed for https://example.com" in str(error)
        assert "Connection timeout" in str(error)

    def test_scraping_error_attributes(self):
        """Test error attributes."""
        error = ScrapingError("Not found", "https://test.com", "firecrawl")
        assert error.url == "https://test.com"
        assert error.method == "firecrawl"
        assert error.message == "Not found"


class TestAllScrapersFailedError:
    """Test AllScrapersFailedError exception."""

    def test_all_scrapers_failed_message(self):
        """Test error message lists all attempts."""
        error = AllScrapersFailedError(
            "https://example.com",
            ["playwright", "firecrawl", "beautifulsoup"],
        )
        assert "https://example.com" in str(error)
        assert "playwright" in str(error)
        assert "firecrawl" in str(error)
        assert "beautifulsoup" in str(error)


class TestScrapingStrategy:
    """Test ScrapingStrategy class."""

    def test_strategy_initialization_defaults(self):
        """Test default initialization."""
        strategy = ScrapingStrategy()
        assert strategy.use_playwright is True
        assert strategy.use_firecrawl is True
        assert strategy.use_beautifulsoup is True
        assert strategy.timeout == 30

    def test_strategy_initialization_custom(self):
        """Test custom initialization."""
        strategy = ScrapingStrategy(
            use_playwright=False,
            use_firecrawl=False,
            timeout=60,
        )
        assert strategy.use_playwright is False
        assert strategy.use_firecrawl is False
        assert strategy.timeout == 60

    @pytest.mark.asyncio
    async def test_scrape_with_invalid_method(self):
        """Test scraping with invalid method raises error."""
        strategy = ScrapingStrategy()
        with pytest.raises(ValueError, match="Unknown scraping method"):
            await strategy._scrape_with_method("https://example.com", "invalid_method")

    @pytest.mark.asyncio
    async def test_try_api_success(self):
        """Test successful API handler."""
        strategy = ScrapingStrategy()

        def mock_handler(url: str) -> dict:
            return {"data": "test data"}

        result = await strategy._try_api("https://example.com", mock_handler)
        assert result.method == "api"
        assert result.success is True
        assert "test data" in result.content

    @pytest.mark.asyncio
    async def test_try_api_failure(self):
        """Test API handler failure."""
        strategy = ScrapingStrategy()

        def failing_handler(url: str) -> None:
            raise ValueError("API error")

        with pytest.raises(ScrapingError) as exc_info:
            await strategy._try_api("https://example.com", failing_handler)

        assert exc_info.value.method == "api"

    @pytest.mark.asyncio
    async def test_beautifulsoup_without_install(self):
        """Test BeautifulSoup fallback when not installed."""
        strategy = ScrapingStrategy()

        # Mock the BeautifulSoup import to fail
        with patch.dict("sys.modules", {"bs4": None}):
            with pytest.raises(ScrapingError) as exc_info:
                await strategy._try_beautifulsoup("https://example.com")

            assert "not installed" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_firecrawl_without_api_key(self):
        """Test Firecrawl fails without API key."""
        strategy = ScrapingStrategy()

        with patch("app.core.config.settings") as mock_settings:
            mock_settings.FIRECRAWL_API_KEY = None
            with pytest.raises(ScrapingError) as exc_info:
                await strategy._try_firecrawl("https://example.com")

            assert "not configured" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_all_scrapers_failed(self):
        """Test AllScrapersFailedError when all methods fail."""
        strategy = ScrapingStrategy(
            use_playwright=False,  # Disable to avoid real browser
            use_firecrawl=False,   # Disable to avoid API call
            use_beautifulsoup=False,  # Disable all
        )

        with pytest.raises(AllScrapersFailedError):
            await strategy.scrape("https://example.com")

    @pytest.mark.asyncio
    async def test_close_client(self):
        """Test closing HTTP client."""
        strategy = ScrapingStrategy()
        # Create client
        await strategy._get_http_client()
        assert strategy._http_client is not None

        # Close client
        await strategy.close()
        assert strategy._http_client is None


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_scrape_url_creates_and_closes_strategy(self):
        """Test scrape_url properly manages strategy lifecycle."""
        with patch.object(ScrapingStrategy, "scrape") as mock_scrape:
            with patch.object(ScrapingStrategy, "close") as mock_close:
                mock_scrape.return_value = ScrapeResult(
                    url="https://example.com",
                    content="Test",
                    method="test",
                )

                from app.scrapers.base import scrape_url

                result = await scrape_url("https://example.com")
                assert result.content == "Test"
                mock_close.assert_called_once()
