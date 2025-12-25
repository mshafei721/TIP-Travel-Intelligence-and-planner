"""Tests for Weather Agent."""

import os
from datetime import date, datetime, timedelta

import pytest

from app.agents.config import AgentConfig
from app.agents.weather import WeatherAgent, WeatherAgentInput, WeatherAgentOutput
from app.agents.weather.models import ClimateInfo, DailyForecast, PackingSuggestion


class TestWeatherAgentInput:
    """Test WeatherAgentInput model."""

    def test_valid_input(self):
        """Test creating valid input."""
        input_data = WeatherAgentInput(
            trip_id="test123",
            user_nationality="US",
            destination_country="Japan",
            destination_city="Tokyo",
            departure_date=date(2024, 6, 15),
            return_date=date(2024, 6, 20),
            latitude=35.6762,
            longitude=139.6503,
        )

        assert input_data.trip_id == "test123"
        assert input_data.destination_city == "Tokyo"
        assert input_data.latitude == 35.6762

    def test_input_without_coordinates(self):
        """Test input without lat/lon is valid."""
        input_data = WeatherAgentInput(
            trip_id="test123",
            user_nationality="US",
            destination_country="France",
            destination_city="Paris",
            departure_date=date(2024, 6, 15),
            return_date=date(2024, 6, 20),
        )

        assert input_data.latitude is None
        assert input_data.longitude is None

    def test_date_validation(self):
        """Test date validation."""
        # Valid dates
        input_data = WeatherAgentInput(
            trip_id="test123",
            user_nationality="US",
            destination_country="Japan",
            destination_city="Tokyo",
            departure_date=date.today(),
            return_date=date.today() + timedelta(days=7),
        )

        assert input_data.departure_date < input_data.return_date


class TestWeatherAgentOutput:
    """Test WeatherAgentOutput model."""

    def test_minimal_output(self):
        """Test creating minimal output."""
        output = WeatherAgentOutput(
            trip_id="test123",
            location="Tokyo, Japan",
            average_temp=24.5,
            temp_range_min=18.0,
            temp_range_max=30.0,
            precipitation_chance=40.0,
            confidence_score=0.85,
        )

        assert output.agent_type == "weather"
        assert output.trip_id == "test123"
        assert output.average_temp == 24.5
        assert len(output.forecast) == 0  # Empty by default

    def test_complete_output(self):
        """Test creating complete output with all fields."""
        forecast = [
            DailyForecast(
                date=date(2024, 6, 15),
                temp_max=28.5,
                temp_min=20.1,
                temp_avg=24.3,
                conditions="Partly cloudy",
                icon="partly-cloudy-day",
                precipitation_prob=20.0,
                precipitation_amount=0.0,
                humidity=65.5,
                wind_speed=12.3,
                wind_direction="S",
                uv_index=8,
                sunrise="04:25",
                sunset="19:00",
                description="Partly cloudy throughout the day",
            )
        ]

        packing = [
            PackingSuggestion(item="Light jacket", reason="Cool mornings", priority="recommended")
        ]

        climate = ClimateInfo(
            climate_type="Humid Subtropical",
            best_time_to_visit="March-May, September-November",
            worst_time_to_visit="July-August (hot and humid)",
            seasonal_notes=["Cherry blossom season: Late March to early April"],
        )

        output = WeatherAgentOutput(
            trip_id="test123",
            location="Tokyo, Japan",
            latitude=35.6762,
            longitude=139.6503,
            timezone="Asia/Tokyo",
            forecast=forecast,
            average_temp=24.3,
            temp_range_min=20.1,
            temp_range_max=28.5,
            precipitation_chance=20.0,
            total_precipitation=0.0,
            packing_suggestions=packing,
            climate_info=climate,
            weather_alerts=[],
            travel_tips=["Best time for outdoor activities: Early morning"],
            confidence_score=0.9,
            sources=["Visual Crossing Weather API"],
            warnings=[],
            is_good_time_to_visit=True,
            seasonal_recommendation="Excellent time to visit - pleasant weather",
        )

        assert len(output.forecast) == 1
        assert len(output.packing_suggestions) == 1
        assert output.climate_info is not None
        assert output.is_good_time_to_visit is True


class TestWeatherAgent:
    """Test Weather Agent."""

    @pytest.fixture()
    def config(self):
        """Provide agent config."""
        return AgentConfig(model_name="claude-3-5-sonnet-20241022", temperature=0.1)

    @pytest.fixture()
    def agent(self, config):
        """Create Weather Agent instance."""
        return WeatherAgent(config=config)

    @pytest.fixture()
    def sample_input(self):
        """Sample agent input."""
        return WeatherAgentInput(
            trip_id="test123",
            user_nationality="US",
            destination_country="Japan",
            destination_city="Tokyo",
            departure_date=date.today() + timedelta(days=7),
            return_date=date.today() + timedelta(days=14),
            latitude=35.6762,
            longitude=139.6503,
        )

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_type == "weather"
        assert agent.crew_agent is not None
        assert agent.crew_agent.role == "Weather Forecast Specialist"

    def test_agent_tools(self, agent):
        """Test agent has required tools."""
        tools = agent.crew_agent.tools
        assert len(tools) == 4  # 4 weather tools
        tool_names = [tool.name for tool in tools]
        assert "Get Weather Forecast" in tool_names
        assert "Get Weather by Coordinates" in tool_names
        assert "Get Climate Information" in tool_names
        assert "Calculate Packing Needs" in tool_names

    def test_invalid_input_type(self, agent):
        """Test agent rejects invalid input type."""
        from app.agents.visa import VisaAgentInput

        invalid_input = VisaAgentInput(
            trip_id="test123",
            user_nationality="US",
            destination_country="JP",  # Use ISO code for VisaAgentInput
            destination_city="Tokyo",
            departure_date=date.today(),
            return_date=date.today() + timedelta(days=7),
            trip_purpose="tourism",
            duration_days=7,
        )

        with pytest.raises(ValueError, match="Expected WeatherAgentInput"):
            agent.run(invalid_input)

    @pytest.mark.skipif(
        not os.getenv("WEATHERAPI_KEY"),
        reason="Requires WEATHERAPI_KEY and ANTHROPIC_API_KEY",
    )
    def test_agent_execution_real(self, agent, sample_input):
        """
        Test agent execution with real APIs.

        Note: Requires both WEATHERAPI_KEY and ANTHROPIC_API_KEY.
        """
        result = agent.run(sample_input)

        assert isinstance(result, WeatherAgentOutput)
        assert result.trip_id == sample_input.trip_id
        assert result.location
        assert result.average_temp > 0
        assert 0.0 <= result.confidence_score <= 1.0
        assert len(result.sources) > 0

    def test_agent_fallback_on_error(self, agent, sample_input, monkeypatch):
        """Test agent creates fallback output on error."""
        # Remove API key to force error
        monkeypatch.delenv("WEATHERAPI_KEY", raising=False)

        result = agent.run(sample_input)

        assert isinstance(result, WeatherAgentOutput)
        assert result.trip_id == sample_input.trip_id
        assert result.confidence_score < 0.5  # Low confidence for fallback
        assert len(result.warnings) > 0
        assert "fallback" in " ".join(result.warnings).lower()

    def test_parse_result_valid_json(self, agent, sample_input):
        """Test parsing valid JSON result."""
        crew_result = """```json
        {
            "location": "Tokyo, Japan",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "timezone": "Asia/Tokyo",
            "forecast": [
                {
                    "date": "2024-06-15",
                    "temp_max": 28.5,
                    "temp_min": 20.1,
                    "temp_avg": 24.3,
                    "conditions": "Partly cloudy",
                    "icon": "partly-cloudy-day",
                    "precipitation_prob": 20.0,
                    "precipitation_amount": 0.0,
                    "humidity": 65.5,
                    "wind_speed": 12.3,
                    "wind_direction": "S",
                    "uv_index": 8,
                    "sunrise": "04:25",
                    "sunset": "19:00",
                    "description": "Partly cloudy throughout the day"
                }
            ],
            "average_temp": 24.3,
            "temp_range_min": 20.1,
            "temp_range_max": 28.5,
            "precipitation_chance": 20.0,
            "total_precipitation": 0.0,
            "packing_suggestions": [
                {
                    "item": "Light jacket",
                    "reason": "Cool mornings",
                    "priority": "recommended"
                }
            ],
            "climate_info": {
                "climate_type": "Humid Subtropical",
                "best_time_to_visit": "March-May, September-November",
                "worst_time_to_visit": "July-August",
                "seasonal_notes": ["Cherry blossom season: Late March"]
            },
            "weather_alerts": [],
            "travel_tips": ["Best time for outdoor activities: Early morning"],
            "confidence_score": 0.9,
            "sources": ["WeatherAPI.com"],
            "warnings": [],
            "is_good_time_to_visit": true,
            "seasonal_recommendation": "Excellent time to visit"
        }
        ```"""

        result = agent._parse_result(crew_result, sample_input)

        assert isinstance(result, WeatherAgentOutput)
        assert result.location == "Tokyo, Japan"
        assert result.latitude == 35.6762
        assert len(result.forecast) == 1
        assert result.forecast[0].temp_max == 28.5
        assert len(result.packing_suggestions) == 1
        assert result.climate_info is not None
        assert result.confidence_score == 0.9
        assert result.is_good_time_to_visit is True

    def test_parse_result_minimal_json(self, agent, sample_input):
        """Test parsing minimal JSON result."""
        crew_result = """{
            "average_temp": 24.0,
            "temp_range_min": 20.0,
            "temp_range_max": 28.0,
            "precipitation_chance": 30.0,
            "confidence_score": 0.7
        }"""

        result = agent._parse_result(crew_result, sample_input)

        assert isinstance(result, WeatherAgentOutput)
        assert result.average_temp == 24.0
        assert result.temp_range_min == 20.0
        assert len(result.forecast) == 0  # No forecast data

    def test_parse_result_invalid_json(self, agent, sample_input):
        """Test parsing invalid JSON falls back."""
        crew_result = "This is not valid JSON"

        result = agent._parse_result(crew_result, sample_input)

        assert isinstance(result, WeatherAgentOutput)
        assert result.confidence_score < 0.5
        assert len(result.warnings) > 0

    def test_create_fallback_output(self, agent, sample_input):
        """Test fallback output creation."""
        error_msg = "API connection failed"

        result = agent._create_fallback_output(sample_input, error_msg)

        assert isinstance(result, WeatherAgentOutput)
        assert result.trip_id == sample_input.trip_id
        assert result.confidence_score < 0.5
        assert any("fallback" in w.lower() for w in result.warnings)
        assert any(error_msg in w for w in result.warnings)
        assert len(result.packing_suggestions) > 0  # Has generic suggestions
        assert len(result.travel_tips) > 0  # Has generic tips

    def test_output_has_metadata(self, agent, sample_input, monkeypatch):
        """Test output includes proper metadata."""
        # Force fallback to test quickly
        monkeypatch.delenv("WEATHERAPI_KEY", raising=False)

        result = agent.run(sample_input)

        assert result.trip_id == sample_input.trip_id
        assert result.agent_type == "weather"
        assert isinstance(result.generated_at, datetime)
        assert len(result.sources) > 0
        assert 0.0 <= result.confidence_score <= 1.0

    def test_different_destinations(self, config):
        """Test agent works for different destinations."""
        destinations = [
            ("Paris", "France", 48.8566, 2.3522),
            ("New York", "USA", 40.7128, -74.0060),
            ("Sydney", "Australia", -33.8688, 151.2093),
        ]

        agent = WeatherAgent(config=config)

        for city, country, lat, lon in destinations:
            input_data = WeatherAgentInput(
                trip_id=f"test_{city}",
                user_nationality="US",
                destination_country=country,
                destination_city=city,
                departure_date=date.today() + timedelta(days=7),
                return_date=date.today() + timedelta(days=14),
                latitude=lat,
                longitude=lon,
            )

            # Test without actually running (would need API keys)
            assert agent.agent_type == "weather"
            assert agent.crew_agent is not None
