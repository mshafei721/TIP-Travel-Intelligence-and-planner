"""
Tests for Attractions Agent

Comprehensive test suite for AttractionsAgent implementation.
"""

from datetime import date, datetime

import pytest

from app.agents.attractions import (
    Attraction,
    AttractionsAgent,
    AttractionsAgentInput,
    AttractionsAgentOutput,
    DayTrip,
    HiddenGem,
)


# ============================================================================
# Input Validation Tests
# ============================================================================


def test_attractions_agent_input_valid():
    """Test valid AttractionsAgentInput creation."""
    input_data = AttractionsAgentInput(
        trip_id="test-123",
        destination_country="France",
        destination_city="Paris",
        departure_date=date(2025, 7, 1),
        return_date=date(2025, 7, 10),
        traveler_nationality="USA",
        interests=["history", "art", "culture"],
    )

    assert input_data.trip_id == "test-123"
    assert input_data.destination_country == "France"
    assert input_data.destination_city == "Paris"
    assert input_data.interests == ["history", "art", "culture"]


def test_attractions_agent_input_empty_country_rejected():
    """Test that empty country name is rejected."""
    with pytest.raises(ValueError, match="Destination country cannot be empty"):
        AttractionsAgentInput(
            trip_id="test-123",
            destination_country="",
            departure_date=date(2025, 7, 1),
            return_date=date(2025, 7, 10),
        )


def test_attractions_agent_input_invalid_dates_rejected():
    """Test that return date before departure date is rejected."""
    with pytest.raises(ValueError, match="Return date must be after departure date"):
        AttractionsAgentInput(
            trip_id="test-123",
            destination_country="Japan",
            departure_date=date(2025, 7, 10),
            return_date=date(2025, 7, 1),
        )


def test_attractions_agent_input_minimal_required_fields():
    """Test AttractionsAgentInput with minimal required fields."""
    input_data = AttractionsAgentInput(
        trip_id="test-123",
        destination_country="Italy",
        departure_date=date(2025, 7, 1),
        return_date=date(2025, 7, 10),
    )

    assert input_data.trip_id == "test-123"
    assert input_data.destination_city is None
    assert input_data.interests is None


# ============================================================================
# Model Validation Tests
# ============================================================================


def test_attraction_model_valid():
    """Test valid Attraction model creation."""
    attraction = Attraction(
        name="Eiffel Tower",
        category="architecture",
        description="Iconic iron lattice tower on the Champ de Mars",
        location="Champ de Mars, 7th arrondissement",
        coordinates={"lat": 48.8584, "lon": 2.2945},
        opening_hours="9:30 AM - 11:45 PM",
        entrance_fee="€28 (adults), €14 (12-24 years), free (under 4)",
        estimated_duration="2-3 hours",
        best_time_to_visit="Early morning or sunset",
        booking_required=True,
        accessibility="Limited wheelchair access (first two floors only)",
        tips=["Book tickets online", "Visit at sunset for best photos"],
        popularity_score=10,
    )

    assert attraction.name == "Eiffel Tower"
    assert attraction.category == "architecture"
    assert attraction.popularity_score == 10


def test_attraction_model_invalid_popularity_rejected():
    """Test that invalid popularity score is rejected."""
    with pytest.raises(ValueError):
        Attraction(
            name="Test Attraction",
            category="museum",
            description="Test description",
            popularity_score=11,  # Invalid: must be 1-10
        )


def test_hidden_gem_model_valid():
    """Test valid HiddenGem model creation."""
    gem = HiddenGem(
        name="Promenade Plantée",
        category="park",
        description="Elevated park built on abandoned railway viaduct",
        location="12th arrondissement",
        why_hidden="Not well-known to tourists",
        best_for=["photographers", "nature lovers", "couples"],
    )

    assert gem.name == "Promenade Plantée"
    assert "photographers" in gem.best_for


def test_day_trip_model_valid():
    """Test valid DayTrip model creation."""
    trip = DayTrip(
        destination="Versailles",
        distance_km=20.0,
        transportation="RER C train (45 minutes) or car (30 minutes)",
        duration="6-8 hours (full day)",
        highlights=["Palace of Versailles", "Gardens", "Marie Antoinette's Estate"],
        estimated_cost="€40-€60 per person",
        best_season="Spring and early fall",
        difficulty_level="easy",
    )

    assert trip.destination == "Versailles"
    assert trip.distance_km == 20.0
    assert len(trip.highlights) == 3


# ============================================================================
# Agent Integration Tests
# ============================================================================


@pytest.mark.integration
def test_attractions_agent_initialization():
    """Test AttractionsAgent initialization."""
    agent = AttractionsAgent()

    assert agent.agent_type == "attractions"
    assert agent.config.name == "Attractions Agent"
    assert agent.config.agent_type == "attractions"
    assert agent.config.version == "1.0.0"
    assert agent.agent is not None


@pytest.mark.integration
@pytest.mark.slow
def test_attractions_agent_run_paris():
    """Test AttractionsAgent execution for Paris."""
    agent = AttractionsAgent()

    input_data = AttractionsAgentInput(
        trip_id="test-paris-001",
        destination_country="France",
        destination_city="Paris",
        departure_date=date(2025, 7, 1),
        return_date=date(2025, 7, 10),
        traveler_nationality="USA",
        interests=["history", "art", "culture"],
    )

    result = agent.run(input_data)

    # Validate output structure
    assert isinstance(result, AttractionsAgentOutput)
    assert result.trip_id == "test-paris-001"
    assert result.agent_type == "attractions"
    assert isinstance(result.generated_at, datetime)
    assert 0.0 <= result.confidence_score <= 1.0

    # Validate attractions data
    assert len(result.top_attractions) >= 1
    assert len(result.estimated_costs) > 0
    assert len(result.booking_tips) >= 1

    # Validate first attraction
    if result.top_attractions:
        first_attraction = result.top_attractions[0]
        assert first_attraction.name
        assert first_attraction.category
        assert first_attraction.description


@pytest.mark.integration
@pytest.mark.slow
def test_attractions_agent_run_tokyo():
    """Test AttractionsAgent execution for Tokyo."""
    agent = AttractionsAgent()

    input_data = AttractionsAgentInput(
        trip_id="test-tokyo-001",
        destination_country="Japan",
        destination_city="Tokyo",
        departure_date=date(2025, 8, 1),
        return_date=date(2025, 8, 14),
        interests=["culture", "nature", "food"],
    )

    result = agent.run(input_data)

    assert isinstance(result, AttractionsAgentOutput)
    assert result.trip_id == "test-tokyo-001"
    assert result.confidence_score > 0.0
    assert len(result.top_attractions) >= 1


@pytest.mark.integration
def test_attractions_agent_run_minimal_input():
    """Test AttractionsAgent with minimal input."""
    agent = AttractionsAgent()

    input_data = AttractionsAgentInput(
        trip_id="test-minimal-001",
        destination_country="Spain",
        departure_date=date(2025, 9, 1),
        return_date=date(2025, 9, 7),
    )

    result = agent.run(input_data)

    assert isinstance(result, AttractionsAgentOutput)
    assert result.trip_id == "test-minimal-001"
    assert len(result.top_attractions) >= 1


# ============================================================================
# Confidence Score Tests
# ============================================================================


@pytest.mark.integration
def test_attractions_agent_confidence_calculation():
    """Test confidence score calculation."""
    agent = AttractionsAgent()

    # Test high confidence result
    high_confidence_result = {
        "top_attractions": [
            {
                "name": f"Attraction {i}",
                "category": "museum",
                "description": "Test description",
            }
            for i in range(10)
        ],
        "hidden_gems": [
            {"name": f"Gem {i}", "category": "park", "description": "Hidden spot"}
            for i in range(3)
        ],
        "day_trips": [
            {
                "destination": f"Trip {i}",
                "transportation": "Train",
                "duration": "Full day",
                "highlights": ["A", "B"],
            }
            for i in range(2)
        ],
        "museums_and_galleries": ["Museum 1", "Museum 2"],
        "historical_sites": ["Site 1", "Site 2"],
        "natural_attractions": ["Park 1"],
        "estimated_costs": {"museums": "$20"},
        "booking_tips": ["Tip 1", "Tip 2"],
    }

    confidence = agent._calculate_confidence(high_confidence_result)
    assert confidence >= 0.8

    # Test low confidence result
    low_confidence_result = {
        "top_attractions": [
            {"name": "One attraction", "category": "museum", "description": "Test"}
        ],
        "estimated_costs": {},
        "booking_tips": [],
    }

    confidence = agent._calculate_confidence(low_confidence_result)
    assert confidence < 0.5


# ============================================================================
# Fallback Tests
# ============================================================================


@pytest.mark.integration
def test_attractions_agent_fallback_result():
    """Test fallback result creation."""
    agent = AttractionsAgent()

    input_data = AttractionsAgentInput(
        trip_id="test-fallback-001",
        destination_country="Iceland",
        destination_city="Reykjavik",
        departure_date=date(2025, 10, 1),
        return_date=date(2025, 10, 7),
    )

    fallback = agent._create_fallback_result(input_data)

    assert isinstance(fallback, dict)
    assert "top_attractions" in fallback
    assert "estimated_costs" in fallback
    assert "booking_tips" in fallback
    assert len(fallback["top_attractions"]) >= 2


# ============================================================================
# JSON Extraction Tests
# ============================================================================


@pytest.mark.integration
def test_attractions_agent_extract_json_from_markdown():
    """Test JSON extraction from markdown code blocks."""
    agent = AttractionsAgent()

    markdown_text = """
    Here is the result:
    ```json
    {
        "top_attractions": [
            {"name": "Test", "category": "museum", "description": "Test attraction"}
        ],
        "estimated_costs": {"museums": "$20"}
    }
    ```
    """

    result = agent._extract_json_from_text(markdown_text)

    assert result is not None
    assert "top_attractions" in result
    assert len(result["top_attractions"]) == 1


@pytest.mark.integration
def test_attractions_agent_extract_json_plain():
    """Test JSON extraction from plain text."""
    agent = AttractionsAgent()

    json_text = '{"top_attractions": [], "estimated_costs": {}}'

    result = agent._extract_json_from_text(json_text)

    assert result is not None
    assert "top_attractions" in result


# ============================================================================
# Output Model Tests
# ============================================================================


def test_attractions_agent_output_model_valid():
    """Test valid AttractionsAgentOutput creation."""
    output = AttractionsAgentOutput(
        trip_id="test-123",
        agent_type="attractions",
        generated_at=datetime.utcnow(),
        confidence_score=0.95,
        sources=[],
        warnings=[],
        top_attractions=[
            Attraction(
                name="Louvre Museum",
                category="museum",
                description="World's largest art museum",
                popularity_score=10,
            )
        ],
        hidden_gems=[],
        day_trips=[],
        museums_and_galleries=["Louvre", "Musée d'Orsay"],
        historical_sites=["Notre-Dame", "Arc de Triomphe"],
        natural_attractions=[],
        religious_sites=[],
        viewpoints_and_landmarks=["Eiffel Tower"],
        estimated_costs={
            "museums": "$15-$25",
            "historical": "$10-$20",
            "tours": "$40-$100",
        },
        booking_tips=["Book major museums in advance"],
        crowd_avoidance_tips=["Visit on weekday mornings"],
        photography_tips=["Golden hour for outdoor monuments"],
        accessibility_notes=["Most museums wheelchair accessible"],
    )

    assert output.trip_id == "test-123"
    assert output.agent_type == "attractions"
    assert len(output.top_attractions) == 1
    assert output.top_attractions[0].name == "Louvre Museum"


def test_attractions_agent_output_model_minimal():
    """Test AttractionsAgentOutput with minimal fields."""
    output = AttractionsAgentOutput(
        trip_id="test-456",
        agent_type="attractions",
        generated_at=datetime.utcnow(),
        confidence_score=0.5,
        sources=[],
        warnings=[],
        top_attractions=[],
        estimated_costs={},
        booking_tips=[],
    )

    assert output.trip_id == "test-456"
    assert len(output.top_attractions) == 0
    assert len(output.hidden_gems) == 0


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.integration
def test_attractions_agent_handles_invalid_input():
    """Test that agent handles invalid input gracefully."""
    agent = AttractionsAgent()

    # This should raise ValueError due to invalid dates
    with pytest.raises(ValueError):
        input_data = AttractionsAgentInput(
            trip_id="test-error-001",
            destination_country="Germany",
            departure_date=date(2025, 12, 31),
            return_date=date(2025, 12, 1),  # Invalid: before departure
        )
