"""
Tests for Country Agent

Tests the complete Country Agent implementation including CrewAI integration.

NOTE: These tests require:
- ANTHROPIC_API_KEY environment variable
- Internet connection for REST Countries API
"""

from datetime import date, datetime

import pytest

from app.agents.country.agent import CountryAgent
from app.agents.country.models import CountryAgentInput, CountryAgentOutput


@pytest.fixture()
def sample_input():
    """Create sample Country Agent input."""
    return CountryAgentInput(
        trip_id="test-trip-123",
        destination_country="France",
        destination_city="Paris",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
        traveler_nationality="United States",
    )


@pytest.fixture()
def country_agent():
    """Create Country Agent instance."""
    return CountryAgent()


class TestCountryAgentInput:
    """Test Country Agent input validation."""

    def test_valid_input(self):
        """Test valid input creation."""
        input_data = CountryAgentInput(
            trip_id="trip-001",
            destination_country="Japan",
            departure_date=date(2025, 7, 1),
            return_date=date(2025, 7, 10),
        )

        assert input_data.trip_id == "trip-001"
        assert input_data.destination_country == "Japan"
        assert input_data.departure_date == date(2025, 7, 1)
        assert input_data.return_date == date(2025, 7, 10)

    def test_empty_country_name(self):
        """Test error handling for empty country name."""
        with pytest.raises(ValueError, match="Destination country cannot be empty"):
            CountryAgentInput(
                trip_id="trip-001",
                destination_country="",
                departure_date=date(2025, 7, 1),
                return_date=date(2025, 7, 10),
            )

    def test_whitespace_country_name(self):
        """Test error handling for whitespace country name."""
        with pytest.raises(ValueError, match="Destination country cannot be empty"):
            CountryAgentInput(
                trip_id="trip-001",
                destination_country="   ",
                departure_date=date(2025, 7, 1),
                return_date=date(2025, 7, 10),
            )

    def test_return_before_departure(self):
        """Test error handling for return date before departure."""
        with pytest.raises(ValueError, match="Return date must be after departure date"):
            CountryAgentInput(
                trip_id="trip-001",
                destination_country="Japan",
                departure_date=date(2025, 7, 10),
                return_date=date(2025, 7, 1),
            )


class TestCountryAgentExecution:
    """Test Country Agent execution with real API calls."""

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_france_country_info(self, country_agent, sample_input):
        """Test getting France country information."""
        result = country_agent.run(sample_input)

        assert isinstance(result, CountryAgentOutput)
        assert result.trip_id == "test-trip-123"
        assert result.agent_type == "country"
        assert result.country_name == "France"
        assert result.country_code == "FR"
        assert "Paris" in result.capital
        assert result.region == "Europe"
        assert result.subregion == "Western Europe"
        assert result.population > 60_000_000
        assert "French" in result.official_languages
        assert result.driving_side == "right"
        assert result.confidence_score >= 0.7

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_japan_country_info(self, country_agent):
        """Test getting Japan country information."""
        input_data = CountryAgentInput(
            trip_id="test-trip-japan",
            destination_country="Japan",
            departure_date=date(2025, 8, 1),
            return_date=date(2025, 8, 15),
        )

        result = country_agent.run(input_data)

        assert result.country_name == "Japan"
        assert result.country_code == "JP"
        assert "Tokyo" in result.capital
        assert result.region == "Asia"
        assert result.driving_side == "left"
        assert "Japanese" in result.official_languages
        assert result.confidence_score >= 0.7

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_usa_country_info(self, country_agent):
        """Test getting USA country information."""
        input_data = CountryAgentInput(
            trip_id="test-trip-usa",
            destination_country="United States",
            departure_date=date(2025, 9, 1),
            return_date=date(2025, 9, 15),
        )

        result = country_agent.run(input_data)

        assert result.country_name == "United States"
        assert result.country_code == "US"
        assert "Washington, D.C." in result.capital
        assert result.region == "Americas"
        assert result.driving_side == "right"
        assert "English" in result.official_languages
        assert result.confidence_score >= 0.7


class TestCountryAgentOutputStructure:
    """Test Country Agent output structure and required fields."""

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_output_has_basic_info(self, country_agent, sample_input):
        """Test output contains basic country information."""
        result = country_agent.run(sample_input)

        # Basic Information
        assert result.country_name is not None
        assert result.country_code is not None
        assert result.capital is not None
        assert result.region is not None

        # Demographics
        assert result.population > 0
        assert result.area_km2 is not None

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_output_has_languages(self, country_agent, sample_input):
        """Test output contains language information."""
        result = country_agent.run(sample_input)

        assert len(result.official_languages) > 0
        assert all(isinstance(lang, str) for lang in result.official_languages)

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_output_has_time_zones(self, country_agent, sample_input):
        """Test output contains time zone information."""
        result = country_agent.run(sample_input)

        assert len(result.time_zones) > 0
        assert all(isinstance(tz, str) for tz in result.time_zones)

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_output_has_emergency_numbers(self, country_agent, sample_input):
        """Test output contains emergency contact information."""
        result = country_agent.run(sample_input)

        assert len(result.emergency_numbers) > 0
        for contact in result.emergency_numbers:
            assert contact.service is not None
            assert contact.number is not None

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_output_has_power_outlet_info(self, country_agent, sample_input):
        """Test output contains power outlet information."""
        result = country_agent.run(sample_input)

        assert result.power_outlet is not None
        assert len(result.power_outlet.plug_types) > 0
        assert result.power_outlet.voltage is not None
        assert result.power_outlet.frequency is not None

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_output_has_safety_rating(self, country_agent, sample_input):
        """Test output contains safety rating."""
        result = country_agent.run(sample_input)

        assert result.safety_rating >= 0.0
        assert result.safety_rating <= 5.0

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_output_has_metadata(self, country_agent, sample_input):
        """Test output contains required metadata."""
        result = country_agent.run(sample_input)

        assert result.trip_id == "test-trip-123"
        assert result.agent_type == "country"
        assert isinstance(result.generated_at, datetime)
        assert result.confidence_score >= 0.0
        assert result.confidence_score <= 1.0
        assert len(result.sources) > 0


class TestCountryAgentEdgeCases:
    """Test Country Agent edge cases."""

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_country_with_multiple_capitals(self, country_agent):
        """Test country with multiple capitals (South Africa)."""
        input_data = CountryAgentInput(
            trip_id="test-trip-za",
            destination_country="South Africa",
            departure_date=date(2025, 10, 1),
            return_date=date(2025, 10, 15),
        )

        result = country_agent.run(input_data)

        assert result.country_code == "ZA"
        assert len(result.capital) >= 1  # South Africa has 3 capitals

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_small_island_nation(self, country_agent):
        """Test small island nation (Maldives)."""
        input_data = CountryAgentInput(
            trip_id="test-trip-mv",
            destination_country="Maldives",
            departure_date=date(2025, 11, 1),
            return_date=date(2025, 11, 15),
        )

        result = country_agent.run(input_data)

        assert result.country_code == "MV"
        assert result.region == "Asia"
        assert result.area_km2 is not None
        assert result.area_km2 < 1000  # Very small area

    @pytest.mark.integration()
    @pytest.mark.slow()
    def test_landlocked_country(self, country_agent):
        """Test landlocked country (Switzerland)."""
        input_data = CountryAgentInput(
            trip_id="test-trip-ch",
            destination_country="Switzerland",
            departure_date=date(2025, 12, 1),
            return_date=date(2025, 12, 15),
        )

        result = country_agent.run(input_data)

        assert result.country_code == "CH"
        assert result.borders is not None
        assert len(result.borders) > 0  # Has land borders
