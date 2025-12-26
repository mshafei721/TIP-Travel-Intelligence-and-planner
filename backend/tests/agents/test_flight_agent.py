"""
Tests for Flight Agent

Comprehensive test suite for FlightAgent implementation.
"""

from datetime import date, datetime

import pytest

from app.agents.flight import (
    FlightAgent,
    FlightAgentInput,
    FlightAgentOutput,
)
from app.agents.flight.models import (
    Airport,
    AirportInfo,
    CabinClass,
    Flight,
    FlightOption,
    FlightSegment,
)


# ============================================================================
# Input Validation Tests
# ============================================================================


def test_flight_agent_input_valid():
    """Test valid FlightAgentInput creation."""
    input_data = FlightAgentInput(
        trip_id="test-123",
        origin_city="New York",
        destination_city="London",
        departure_date=date(2025, 7, 1),
        return_date=date(2025, 7, 10),
        passengers=2,
        cabin_class=CabinClass.ECONOMY,
    )

    assert input_data.trip_id == "test-123"
    assert input_data.origin_city == "New York"
    assert input_data.destination_city == "London"
    assert input_data.passengers == 2
    assert input_data.cabin_class == CabinClass.ECONOMY


def test_flight_agent_input_one_way():
    """Test one-way flight input (no return date)."""
    input_data = FlightAgentInput(
        trip_id="test-123",
        origin_city="Paris",
        destination_city="Tokyo",
        departure_date=date(2025, 8, 15),
        return_date=None,
    )

    assert input_data.return_date is None


def test_flight_agent_input_invalid_return_date_rejected():
    """Test that return date before departure date is rejected."""
    with pytest.raises(ValueError, match="Return date must be after departure date"):
        FlightAgentInput(
            trip_id="test-123",
            origin_city="London",
            destination_city="New York",
            departure_date=date(2025, 7, 10),
            return_date=date(2025, 7, 5),
        )


def test_flight_agent_input_invalid_passengers_rejected():
    """Test that invalid passenger count is rejected."""
    with pytest.raises(ValueError):
        FlightAgentInput(
            trip_id="test-123",
            origin_city="Berlin",
            destination_city="Rome",
            departure_date=date(2025, 7, 1),
            passengers=0,  # Must be at least 1
        )

    with pytest.raises(ValueError):
        FlightAgentInput(
            trip_id="test-123",
            origin_city="Berlin",
            destination_city="Rome",
            departure_date=date(2025, 7, 1),
            passengers=10,  # Max is 9
        )


def test_flight_agent_input_all_cabin_classes():
    """Test all cabin class options."""
    for cabin_class in CabinClass:
        input_data = FlightAgentInput(
            trip_id="test-123",
            origin_city="Miami",
            destination_city="Cancun",
            departure_date=date(2025, 7, 1),
            cabin_class=cabin_class,
        )
        assert input_data.cabin_class == cabin_class


def test_flight_agent_input_with_budget():
    """Test input with budget constraint."""
    input_data = FlightAgentInput(
        trip_id="test-123",
        origin_city="Chicago",
        destination_city="Los Angeles",
        departure_date=date(2025, 7, 1),
        budget_usd=500.0,
    )

    assert input_data.budget_usd == 500.0


def test_flight_agent_input_direct_flights_only():
    """Test direct flights only flag."""
    input_data = FlightAgentInput(
        trip_id="test-123",
        origin_city="Seattle",
        destination_city="San Francisco",
        departure_date=date(2025, 7, 1),
        direct_flights_only=True,
    )

    assert input_data.direct_flights_only is True


def test_flight_agent_input_minimal_required_fields():
    """Test FlightAgentInput with minimal required fields."""
    input_data = FlightAgentInput(
        trip_id="test-123",
        origin_city="Boston",
        destination_city="Denver",
        departure_date=date(2025, 7, 1),
    )

    assert input_data.trip_id == "test-123"
    assert input_data.return_date is None
    assert input_data.passengers == 1  # Default
    assert input_data.cabin_class == CabinClass.ECONOMY  # Default
    assert input_data.budget_usd is None
    assert input_data.direct_flights_only is False  # Default
    assert input_data.flexible_dates is True  # Default


# ============================================================================
# Output Model Tests
# ============================================================================


def test_flight_agent_output_valid():
    """Test valid FlightAgentOutput creation."""
    output = FlightAgentOutput(
        trip_id="test-123",
        recommended_flights=[],
        price_range={"min": 400.0, "max": 1200.0, "average": 750.0},
        airport_info=AirportInfo(
            departure_airport=Airport(
                code="JFK", name="John F Kennedy International", city="New York", country="USA"
            ),
            arrival_airport=Airport(
                code="LHR", name="London Heathrow", city="London", country="UK"
            ),
        ),
        booking_tips=["Book 2-3 months in advance"],
        confidence_score=0.85,
    )

    assert output.trip_id == "test-123"
    assert output.price_range["min"] == 400.0
    assert output.confidence_score == 0.85


def test_airport_model():
    """Test Airport model."""
    airport = Airport(
        code="LAX",
        name="Los Angeles International Airport",
        city="Los Angeles",
        country="USA",
        timezone="America/Los_Angeles",
    )

    assert airport.code == "LAX"
    assert airport.timezone == "America/Los_Angeles"


def test_flight_segment_model():
    """Test FlightSegment model."""
    segment = FlightSegment(
        departure_airport=Airport(
            code="JFK", name="JFK Airport", city="New York", country="USA"
        ),
        arrival_airport=Airport(
            code="LHR", name="Heathrow", city="London", country="UK"
        ),
        departure_time=datetime(2025, 7, 1, 14, 0),
        arrival_time=datetime(2025, 7, 2, 2, 0),
        airline="British Airways",
        airline_code="BA",
        flight_number="BA178",
        duration_minutes=420,
    )

    assert segment.airline == "British Airways"
    assert segment.duration_minutes == 420


def test_flight_option_model():
    """Test FlightOption model."""
    segment = FlightSegment(
        departure_airport=Airport(code="JFK", name="JFK", city="NYC", country="USA"),
        arrival_airport=Airport(code="CDG", name="CDG", city="Paris", country="France"),
        departure_time=datetime(2025, 7, 1, 10, 0),
        arrival_time=datetime(2025, 7, 1, 22, 0),
        airline="Air France",
        airline_code="AF",
        flight_number="AF001",
        duration_minutes=450,
    )

    flight = Flight(
        segments=[segment],
        total_duration_minutes=450,
        departure_time=datetime(2025, 7, 1, 10, 0),
        arrival_time=datetime(2025, 7, 1, 22, 0),
        is_direct=True,
        layover_airports=[],
        layover_durations_minutes=[],
    )

    option = FlightOption(
        outbound_flight=flight,
        price_usd=850.0,
        cabin_class=CabinClass.ECONOMY,
        provider="Expedia",
    )

    assert option.price_usd == 850.0
    assert option.outbound_flight.is_direct is True


# ============================================================================
# Agent Initialization Tests
# ============================================================================


def test_flight_agent_initialization():
    """Test FlightAgent can be initialized."""
    agent = FlightAgent()
    assert agent is not None
    assert agent.agent_type == "flight"


def test_flight_agent_with_custom_config():
    """Test FlightAgent with custom configuration."""
    from app.agents.config import AgentConfig

    config = AgentConfig(
        name="Custom Flight Agent",
        agent_type="flight",
        description="Custom description",
        version="2.0.0",
    )

    agent = FlightAgent(config=config)
    assert agent.config.name == "Custom Flight Agent"
    assert agent.config.version == "2.0.0"


def test_flight_agent_has_tools():
    """Test FlightAgent has required tools configured."""
    agent = FlightAgent()
    # Check that the agent was created (tools are passed to CrewAI agent)
    assert agent.agent is not None


# ============================================================================
# Integration Tests (Skip if no API key)
# ============================================================================


@pytest.mark.skipif(
    True,  # Skip by default - requires actual API
    reason="Integration test requires live API",
)
def test_flight_agent_run_integration():
    """Integration test - run flight agent with real data."""
    agent = FlightAgent()

    input_data = FlightAgentInput(
        trip_id="integration-test",
        origin_city="New York",
        destination_city="London",
        departure_date=date(2025, 8, 1),
        return_date=date(2025, 8, 10),
        passengers=1,
        cabin_class=CabinClass.ECONOMY,
    )

    result = agent.run(input_data)

    assert result is not None
    assert result.trip_id == "integration-test"
    assert result.agent_type == "flight"
    assert 0.0 <= result.confidence_score <= 1.0
