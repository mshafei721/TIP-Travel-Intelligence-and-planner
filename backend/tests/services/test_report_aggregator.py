"""Tests for the report aggregator service."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.services.report_aggregator import (
    ReportAggregator,
    ReportSection,
    TripInfo,
    AggregatedReport,
    EXPECTED_SECTIONS,
)


class TestReportSection:
    """Tests for ReportSection model."""

    def test_report_section_creation(self):
        """Test creating a ReportSection."""
        section = ReportSection(
            section_type="visa",
            title="Visa Requirements",
            content={"visa_required": True},
            confidence_score=0.85,
            generated_at=datetime.utcnow(),
            sources=[{"url": "https://example.com", "type": "official"}],
        )

        assert section.section_type == "visa"
        assert section.title == "Visa Requirements"
        assert section.content["visa_required"] is True
        assert section.confidence_score == 0.85
        assert len(section.sources) == 1

    def test_report_section_defaults(self):
        """Test ReportSection default values."""
        section = ReportSection(
            section_type="country",
            title="Country Info",
            content={},
            confidence_score=0.5,
            generated_at=datetime.utcnow(),
        )

        assert section.sources == []


class TestTripInfo:
    """Tests for TripInfo model."""

    def test_trip_info_creation(self):
        """Test creating a TripInfo."""
        trip_info = TripInfo(
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

        assert trip_info.trip_id == "123e4567-e89b-12d3-a456-426614174000"
        assert trip_info.title == "Trip to Paris"
        assert trip_info.destination_country == "France"
        assert trip_info.destination_city == "Paris"
        assert trip_info.travelers == 2

    def test_trip_info_defaults(self):
        """Test TripInfo default values."""
        trip_info = TripInfo(
            trip_id="123e4567-e89b-12d3-a456-426614174000",
            title="Trip to Tokyo",
            destination_country="Japan",
            departure_date="2025-02-01",
            status="draft",
            created_at=datetime.utcnow(),
        )

        assert trip_info.destination_city is None
        assert trip_info.return_date is None
        assert trip_info.travelers == 1


class TestAggregatedReport:
    """Tests for AggregatedReport model."""

    def test_aggregated_report_creation(self):
        """Test creating an AggregatedReport."""
        trip_info = TripInfo(
            trip_id="123e4567-e89b-12d3-a456-426614174000",
            title="Trip to Paris",
            destination_country="France",
            departure_date="2025-01-15",
            status="completed",
            created_at=datetime.utcnow(),
        )

        report = AggregatedReport(
            trip_id="123e4567-e89b-12d3-a456-426614174000",
            trip_info=trip_info,
            sections={},
            available_sections=["visa", "country"],
            missing_sections=["weather", "currency"],
            overall_confidence=0.75,
            is_complete=False,
        )

        assert report.trip_id == "123e4567-e89b-12d3-a456-426614174000"
        assert report.overall_confidence == 0.75
        assert report.is_complete is False
        assert len(report.available_sections) == 2
        assert len(report.missing_sections) == 2

    def test_aggregated_report_defaults(self):
        """Test AggregatedReport default values."""
        trip_info = TripInfo(
            trip_id="123",
            title="Trip",
            destination_country="Country",
            departure_date="2025-01-01",
            status="draft",
            created_at=datetime.utcnow(),
        )

        report = AggregatedReport(
            trip_id="123",
            trip_info=trip_info,
        )

        assert report.sections == {}
        assert report.available_sections == []
        assert report.missing_sections == []
        assert report.overall_confidence == 0.0
        assert report.is_complete is False


class TestExpectedSections:
    """Tests for expected sections constant."""

    def test_expected_sections_list(self):
        """Test that expected sections list is complete."""
        expected = [
            "visa",
            "country",
            "weather",
            "currency",
            "culture",
            "food",
            "attractions",
            "itinerary",
            "flight",
        ]

        assert EXPECTED_SECTIONS == expected
        assert len(EXPECTED_SECTIONS) == 9


class TestReportAggregator:
    """Tests for ReportAggregator service."""

    @pytest.fixture
    def aggregator(self):
        """Create a ReportAggregator instance."""
        return ReportAggregator()

    @pytest.fixture
    def mock_supabase(self):
        """Create a mock Supabase client."""
        with patch("app.services.report_aggregator.supabase") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_get_trip_info_found(self, aggregator, mock_supabase):
        """Test getting trip info when trip exists."""
        mock_response = MagicMock()
        mock_response.data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "destination_country": "France",
            "destination_city": "Paris",
            "departure_date": "2025-01-15",
            "return_date": "2025-01-22",
            "travelers": 2,
            "status": "completed",
            "created_at": "2025-01-01T00:00:00Z",
        }

        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        aggregator.supabase = mock_supabase

        trip_info = await aggregator.get_trip_info("123e4567-e89b-12d3-a456-426614174000")

        assert trip_info is not None
        assert trip_info.trip_id == "123e4567-e89b-12d3-a456-426614174000"
        assert trip_info.destination_country == "France"
        assert trip_info.destination_city == "Paris"
        assert trip_info.title == "Trip to Paris"

    @pytest.mark.asyncio
    async def test_get_trip_info_not_found(self, aggregator, mock_supabase):
        """Test getting trip info when trip doesn't exist."""
        mock_response = MagicMock()
        mock_response.data = None

        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        aggregator.supabase = mock_supabase

        trip_info = await aggregator.get_trip_info("nonexistent-id")

        assert trip_info is None

    @pytest.mark.asyncio
    async def test_get_all_sections_found(self, aggregator, mock_supabase):
        """Test getting all sections when sections exist."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "section_type": "visa",
                "title": "Visa Requirements",
                "content": {"visa_required": True},
                "confidence_score": 85,
                "generated_at": "2025-01-01T00:00:00Z",
                "sources": [],
            },
            {
                "section_type": "country",
                "title": "Country Information",
                "content": {"country_name": "France"},
                "confidence_score": 90,
                "generated_at": "2025-01-01T00:00:00Z",
                "sources": [],
            },
        ]

        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        aggregator.supabase = mock_supabase

        sections = await aggregator.get_all_sections("123")

        assert len(sections) == 2
        assert sections[0].section_type == "visa"
        assert sections[0].confidence_score == 0.85
        assert sections[1].section_type == "country"
        assert sections[1].confidence_score == 0.90

    @pytest.mark.asyncio
    async def test_get_all_sections_empty(self, aggregator, mock_supabase):
        """Test getting all sections when none exist."""
        mock_response = MagicMock()
        mock_response.data = []

        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        aggregator.supabase = mock_supabase

        sections = await aggregator.get_all_sections("123")

        assert sections == []

    @pytest.mark.asyncio
    async def test_aggregate_report_partial(self, aggregator, mock_supabase):
        """Test aggregating a partial report."""
        # Mock trip info
        trip_mock = MagicMock()
        trip_mock.data = {
            "id": "123",
            "destination_country": "France",
            "destination_city": "Paris",
            "departure_date": "2025-01-15",
            "status": "processing",
            "created_at": "2025-01-01T00:00:00Z",
        }

        # Mock sections
        sections_mock = MagicMock()
        sections_mock.data = [
            {
                "section_type": "visa",
                "title": "Visa Requirements",
                "content": {"visa_required": False},
                "confidence_score": 90,
                "generated_at": "2025-01-01T00:00:00Z",
                "sources": [],
            },
        ]

        # Set up mock chain
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = trip_mock
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = sections_mock
        aggregator.supabase = mock_supabase

        report = await aggregator.aggregate_report("123")

        assert report is not None
        assert report.trip_id == "123"
        assert report.is_complete is False
        assert "visa" in report.available_sections
        assert len(report.missing_sections) == 8  # 9 expected - 1 available
        assert report.overall_confidence == 0.90

    @pytest.mark.asyncio
    async def test_aggregate_report_trip_not_found(self, aggregator, mock_supabase):
        """Test aggregating report when trip doesn't exist."""
        mock_response = MagicMock()
        mock_response.data = None

        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        aggregator.supabase = mock_supabase

        report = await aggregator.aggregate_report("nonexistent")

        assert report is None

    @pytest.mark.asyncio
    async def test_get_section_found(self, aggregator, mock_supabase):
        """Test getting a specific section when it exists."""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "section_type": "visa",
                "title": "Visa Requirements",
                "content": {"visa_required": True},
                "confidence_score": 85,
                "generated_at": "2025-01-01T00:00:00Z",
                "sources": [{"url": "https://example.com", "type": "official"}],
            }
        ]

        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        aggregator.supabase = mock_supabase

        section = await aggregator.get_section("123", "visa")

        assert section is not None
        assert section.section_type == "visa"
        assert section.confidence_score == 0.85
        assert len(section.sources) == 1

    @pytest.mark.asyncio
    async def test_get_section_not_found(self, aggregator, mock_supabase):
        """Test getting a specific section when it doesn't exist."""
        mock_response = MagicMock()
        mock_response.data = []

        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        aggregator.supabase = mock_supabase

        section = await aggregator.get_section("123", "visa")

        assert section is None


class TestConfidenceScoreConversion:
    """Tests for confidence score conversion (integer to float)."""

    @pytest.fixture
    def aggregator(self):
        """Create a ReportAggregator instance."""
        return ReportAggregator()

    @pytest.mark.asyncio
    async def test_confidence_conversion_high(self, aggregator):
        """Test confidence conversion for high values."""
        with patch("app.services.report_aggregator.supabase") as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [
                {
                    "section_type": "visa",
                    "title": "Visa",
                    "content": {},
                    "confidence_score": 100,
                    "generated_at": "2025-01-01T00:00:00Z",
                    "sources": [],
                }
            ]

            mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
            aggregator.supabase = mock_supabase

            sections = await aggregator.get_all_sections("123")

            assert sections[0].confidence_score == 1.0

    @pytest.mark.asyncio
    async def test_confidence_conversion_zero(self, aggregator):
        """Test confidence conversion for zero."""
        with patch("app.services.report_aggregator.supabase") as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [
                {
                    "section_type": "visa",
                    "title": "Visa",
                    "content": {},
                    "confidence_score": 0,
                    "generated_at": "2025-01-01T00:00:00Z",
                    "sources": [],
                }
            ]

            mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
            aggregator.supabase = mock_supabase

            sections = await aggregator.get_all_sections("123")

            assert sections[0].confidence_score == 0.0

    @pytest.mark.asyncio
    async def test_confidence_conversion_missing(self, aggregator):
        """Test confidence conversion when missing."""
        with patch("app.services.report_aggregator.supabase") as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [
                {
                    "section_type": "visa",
                    "title": "Visa",
                    "content": {},
                    # No confidence_score field
                    "generated_at": "2025-01-01T00:00:00Z",
                    "sources": [],
                }
            ]

            mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
            aggregator.supabase = mock_supabase

            sections = await aggregator.get_all_sections("123")

            assert sections[0].confidence_score == 0.0
