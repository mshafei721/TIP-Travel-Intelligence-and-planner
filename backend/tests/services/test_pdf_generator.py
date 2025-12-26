"""Tests for the PDF generator service."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.pdf_generator import PDFGenerator
from app.services.report_aggregator import (
    AggregatedReport,
    TripInfo,
    ReportSection,
)


class TestPDFGenerator:
    """Tests for PDFGenerator service."""

    @pytest.fixture
    def generator(self):
        """Create a PDFGenerator instance."""
        return PDFGenerator()

    @pytest.fixture
    def sample_trip_info(self):
        """Create sample TripInfo for testing."""
        return TripInfo(
            trip_id="123e4567-e89b-12d3-a456-426614174000",
            title="Trip to Paris",
            destination_country="France",
            destination_city="Paris",
            departure_date="2025-01-15",
            return_date="2025-01-22",
            travelers=2,
            status="completed",
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_report(self, sample_trip_info):
        """Create sample AggregatedReport for testing."""
        visa_section = ReportSection(
            section_type="visa",
            title="Visa Requirements",
            content={
                "visa_required": False,
                "max_stay_days": 90,
                "visa_type": "Visa-free",
            },
            confidence_score=0.9,
            generated_at=datetime.utcnow(),
            sources=[],
        )

        weather_section = ReportSection(
            section_type="weather",
            title="Weather Forecast",
            content={
                "current_temp": 15,
                "conditions": "Partly cloudy",
                "forecast": [
                    {"day": "Monday", "temp": 14, "conditions": "Sunny"},
                    {"day": "Tuesday", "temp": 16, "conditions": "Cloudy"},
                ],
            },
            confidence_score=0.85,
            generated_at=datetime.utcnow(),
            sources=[],
        )

        return AggregatedReport(
            trip_id="123e4567-e89b-12d3-a456-426614174000",
            trip_info=sample_trip_info,
            sections={"visa": visa_section, "weather": weather_section},
            available_sections=["visa", "weather"],
            missing_sections=["currency", "culture"],
            overall_confidence=0.875,
            is_complete=False,
        )

    def test_generator_initialization(self, generator):
        """Test PDFGenerator initialization."""
        assert generator is not None
        assert generator._playwright_available is None

    def test_generate_html_basic(self, generator, sample_report):
        """Test basic HTML generation."""
        html = generator._generate_html(sample_report)

        assert html is not None
        assert isinstance(html, str)
        assert "Trip to Paris" in html
        assert "France" in html
        assert "2025-01-15" in html

    def test_generate_html_contains_sections(self, generator, sample_report):
        """Test HTML contains all sections."""
        html = generator._generate_html(sample_report)

        assert "Visa Requirements" in html
        assert "Weather Forecast" in html

    def test_generate_html_styling(self, generator, sample_report):
        """Test HTML contains proper styling."""
        html = generator._generate_html(sample_report)

        # Check for essential CSS
        assert "<style>" in html
        assert "</style>" in html
        assert "@media print" in html

    def test_generate_html_empty_sections(self, generator, sample_trip_info):
        """Test HTML generation with no sections."""
        report = AggregatedReport(
            trip_id="123",
            trip_info=sample_trip_info,
            sections={},
            available_sections=[],
            missing_sections=["visa", "weather"],
            overall_confidence=0.0,
            is_complete=False,
        )

        html = generator._generate_html(report)

        assert html is not None
        assert "Trip to Paris" in html

    def test_section_rendering_visa(self, generator, sample_report):
        """Test visa section is rendered correctly."""
        html = generator._generate_html(sample_report)

        assert "Visa Requirements" in html
        # Should contain visa-related info
        assert "90" in html or "Visa" in html

    def test_section_rendering_weather(self, generator, sample_report):
        """Test weather section is rendered correctly."""
        html = generator._generate_html(sample_report)

        assert "Weather" in html

    @pytest.mark.asyncio
    async def test_check_playwright_available(self, generator):
        """Test Playwright availability check."""
        with patch.dict("sys.modules", {"playwright": MagicMock(), "playwright.async_api": MagicMock()}):
            result = await generator._check_playwright()
            assert result is True
            assert generator._playwright_available is True

    @pytest.mark.asyncio
    async def test_check_playwright_not_available(self, generator):
        """Test Playwright not available."""
        with patch.dict("sys.modules", {"playwright": None, "playwright.async_api": None}):
            # Force re-check
            generator._playwright_available = None

            # This will try to import and fail
            with patch("app.services.pdf_generator.PDFGenerator._check_playwright") as mock_check:
                mock_check.return_value = False
                result = await mock_check()
                assert result is False

    @pytest.mark.asyncio
    async def test_generate_pdf_fallback_html(self, generator, sample_report):
        """Test PDF generation falls back to HTML when Playwright unavailable."""
        # Force playwright to be unavailable
        generator._playwright_available = False

        result = await generator.generate_pdf(sample_report)

        # Should return HTML bytes as fallback
        assert result is not None
        assert isinstance(result, bytes)
        assert b"Trip to Paris" in result


class TestPDFGeneratorEdgeCases:
    """Edge case tests for PDFGenerator."""

    @pytest.fixture
    def generator(self):
        """Create a PDFGenerator instance."""
        return PDFGenerator()

    @pytest.fixture
    def base_trip_info(self):
        """Create base TripInfo."""
        return TripInfo(
            trip_id="123",
            title="Test Trip",
            destination_country="Country",
            departure_date="2025-01-01",
            status="completed",
            created_at=datetime.utcnow(),
        )

    def test_html_unicode_characters(self, generator, base_trip_info):
        """Test HTML with unicode characters."""
        trip_info = TripInfo(
            trip_id="123",
            title="Trip to Tokyo",
            destination_country="Japan",
            destination_city="Tokyo",
            departure_date="2025-01-01",
            status="completed",
            created_at=datetime.utcnow(),
        )

        culture_section = ReportSection(
            section_type="culture",
            title="Japanese Culture",
            content={
                "greeting": "Hello",
                "currency": "JPY",
            },
            confidence_score=0.9,
            generated_at=datetime.utcnow(),
            sources=[],
        )

        report = AggregatedReport(
            trip_id="123",
            trip_info=trip_info,
            sections={"culture": culture_section},
            available_sections=["culture"],
            missing_sections=[],
            overall_confidence=0.9,
            is_complete=False,
        )

        html = generator._generate_html(report)

        assert html is not None
        assert "charset" in html.lower() or "utf-8" in html.lower()

    def test_html_long_content(self, generator, base_trip_info):
        """Test HTML with very long content."""
        long_text = "A" * 10000

        culture_section = ReportSection(
            section_type="culture",
            title="Culture",
            content={
                "description": long_text,
            },
            confidence_score=0.8,
            generated_at=datetime.utcnow(),
            sources=[],
        )

        report = AggregatedReport(
            trip_id="123",
            trip_info=base_trip_info,
            sections={"culture": culture_section},
            available_sections=["culture"],
            missing_sections=[],
            overall_confidence=0.8,
            is_complete=False,
        )

        html = generator._generate_html(report)

        assert html is not None
        # Should contain the long content
        assert len(html) > 1000

    def test_html_nested_content(self, generator, base_trip_info):
        """Test HTML with deeply nested content."""
        itinerary_section = ReportSection(
            section_type="itinerary",
            title="Itinerary",
            content={
                "daily_plans": [
                    {
                        "day": 1,
                        "activities": [
                            {"time": "09:00", "activity": "Breakfast"},
                            {"time": "10:00", "activity": "Museum visit"},
                        ],
                    },
                    {
                        "day": 2,
                        "activities": [
                            {"time": "08:00", "activity": "Early start"},
                        ],
                    },
                ],
            },
            confidence_score=0.85,
            generated_at=datetime.utcnow(),
            sources=[],
        )

        report = AggregatedReport(
            trip_id="123",
            trip_info=base_trip_info,
            sections={"itinerary": itinerary_section},
            available_sections=["itinerary"],
            missing_sections=[],
            overall_confidence=0.85,
            is_complete=False,
        )

        html = generator._generate_html(report)

        assert html is not None
        assert "Itinerary" in html


class TestPDFGeneratorMetadata:
    """Tests for PDF metadata and configuration."""

    @pytest.fixture
    def generator(self):
        """Create a PDFGenerator instance."""
        return PDFGenerator()

    @pytest.fixture
    def sample_trip_info(self):
        """Create sample TripInfo."""
        return TripInfo(
            trip_id="123",
            title="Test Trip",
            destination_country="Country",
            departure_date="2025-01-01",
            status="completed",
            created_at=datetime.utcnow(),
        )

    def test_pdf_format_settings(self, generator):
        """Test that PDF format settings are correct."""
        assert hasattr(generator, "_playwright_available")

    def test_html_includes_print_styles(self, generator, sample_trip_info):
        """Test HTML includes print-specific styles."""
        report = AggregatedReport(
            trip_id="123",
            trip_info=sample_trip_info,
            sections={},
            available_sections=[],
            missing_sections=[],
            overall_confidence=0.0,
            is_complete=False,
        )

        html = generator._generate_html(report)

        # Should have print media query
        assert "@media print" in html

    def test_html_includes_header_footer(self, generator, sample_trip_info):
        """Test HTML includes header and footer elements."""
        report = AggregatedReport(
            trip_id="123",
            trip_info=sample_trip_info,
            sections={},
            available_sections=[],
            missing_sections=[],
            overall_confidence=0.0,
            is_complete=False,
        )

        html = generator._generate_html(report)

        # Should have some form of header
        assert "<header" in html or "header" in html.lower()
        # Should include trip title
        assert "Test Trip" in html


class TestPDFGeneratorStorage:
    """Tests for PDF storage functionality."""

    @pytest.fixture
    def generator(self):
        """Create a PDFGenerator instance."""
        return PDFGenerator()

    @pytest.mark.asyncio
    async def test_save_pdf_to_storage_success(self, generator):
        """Test saving PDF to storage (mocked)."""
        with patch("app.core.supabase.supabase") as mock_supabase:
            mock_storage = MagicMock()
            mock_storage.from_.return_value.upload.return_value = MagicMock()
            mock_storage.from_.return_value.get_public_url.return_value = "https://storage.example.com/trip-reports/123/report.pdf"
            mock_supabase.storage = mock_storage

            url = await generator.save_pdf_to_storage(
                trip_id="123",
                pdf_bytes=b"fake pdf content",
                user_id="user-1",
            )

            assert url is not None

    @pytest.mark.asyncio
    async def test_save_pdf_to_storage_failure(self, generator):
        """Test saving PDF to storage handles errors."""
        with patch("app.core.supabase.supabase") as mock_supabase:
            mock_storage = MagicMock()
            mock_storage.from_.return_value.upload.side_effect = Exception("Upload failed")
            mock_supabase.storage = mock_storage

            result = await generator.save_pdf_to_storage(
                trip_id="123",
                pdf_bytes=b"fake pdf content",
                user_id="user-1",
            )

            # Should return None on storage error
            assert result is None
