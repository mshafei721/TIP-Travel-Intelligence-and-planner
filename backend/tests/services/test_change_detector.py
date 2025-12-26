"""
Tests for ChangeDetector service (TDD - Write tests FIRST)

Tests for detecting trip changes and determining affected agents for selective recalculation.
"""

from datetime import date

import pytest

from app.models.trips import (
    AccommodationType,
    Destination,
    TransportationPreference,
    TravelerDetails,
    TravelStyle,
    TripDetails,
    TripPreferences,
    TripPurpose,
    TripResponse,
)
from app.services.change_detector import ChangeDetector, ChangeResult


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def change_detector():
    """Create a ChangeDetector instance."""
    return ChangeDetector()


@pytest.fixture
def base_trip_data():
    """Base trip data for testing."""
    return {
        "traveler_details": TravelerDetails(
            name="John Doe",
            email="john@example.com",
            nationality="US",
            residence_country="US",
            origin_city="New York",
            party_size=2,
            party_ages=[30, 28],
        ),
        "destinations": [
            Destination(country="France", city="Paris", duration_days=7),
        ],
        "trip_details": TripDetails(
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 15),
            budget=5000.00,
            currency="USD",
            trip_purpose=TripPurpose.TOURISM,
        ),
        "preferences": TripPreferences(
            travel_style=TravelStyle.BALANCED,
            interests=["museums", "food"],
            dietary_restrictions=[],
            accessibility_needs=[],
            accommodation_type=AccommodationType.HOTEL,
            transportation_preference=TransportationPreference.PUBLIC,
        ),
    }


# ============================================================================
# CHANGE DETECTION TESTS
# ============================================================================


class TestDetectChanges:
    """Test change detection between old and new trip data."""

    def test_no_changes_detected(self, change_detector, base_trip_data):
        """When trip data is identical, no changes should be detected."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()

        result = change_detector.detect_changes(old_trip, new_trip)

        assert isinstance(result, ChangeResult)
        assert result.has_changes is False
        assert len(result.changes) == 0
        assert len(result.affected_agents) == 0

    def test_destination_country_change(self, change_detector, base_trip_data):
        """Changing destination country should affect multiple agents."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["destinations"] = [
            Destination(country="Japan", city="Tokyo", duration_days=7),
        ]

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "destination" in result.changes
        # Destination change affects: visa, weather, currency, culture, food, attractions, itinerary, country
        expected_agents = {"visa", "weather", "currency", "culture", "food", "attractions", "itinerary", "country"}
        assert expected_agents.issubset(set(result.affected_agents))

    def test_destination_city_change(self, change_detector, base_trip_data):
        """Changing destination city (same country) should affect some agents."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["destinations"] = [
            Destination(country="France", city="Lyon", duration_days=7),  # Same country, different city
        ]

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "destination" in result.changes
        # City change affects: weather, attractions, itinerary, food
        assert "weather" in result.affected_agents
        assert "attractions" in result.affected_agents
        assert "itinerary" in result.affected_agents

    def test_departure_date_change(self, change_detector, base_trip_data):
        """Changing departure date should affect weather and itinerary."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["trip_details"] = TripDetails(
            departure_date=date(2025, 7, 1),  # Different date
            return_date=date(2025, 7, 15),
            budget=5000.00,
            currency="USD",
            trip_purpose=TripPurpose.TOURISM,
        )

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "departure_date" in result.changes or "trip_details" in result.changes
        assert "weather" in result.affected_agents
        assert "itinerary" in result.affected_agents
        # Visa should NOT be affected by date change
        assert "visa" not in result.affected_agents

    def test_nationality_change(self, change_detector, base_trip_data):
        """Changing nationality should affect visa agent."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["traveler_details"] = TravelerDetails(
            name="John Doe",
            email="john@example.com",
            nationality="GB",  # Changed from US to GB
            residence_country="US",
            origin_city="New York",
            party_size=2,
            party_ages=[30, 28],
        )

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "nationality" in result.changes or "traveler_details" in result.changes
        assert "visa" in result.affected_agents

    def test_budget_change(self, change_detector, base_trip_data):
        """Changing budget should affect itinerary and attractions."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["trip_details"] = TripDetails(
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 15),
            budget=10000.00,  # Doubled budget
            currency="USD",
            trip_purpose=TripPurpose.TOURISM,
        )

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "budget" in result.changes or "trip_details" in result.changes
        assert "itinerary" in result.affected_agents
        assert "currency" in result.affected_agents

    def test_interests_change(self, change_detector, base_trip_data):
        """Changing interests should affect itinerary and attractions."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["preferences"] = TripPreferences(
            travel_style=TravelStyle.BALANCED,
            interests=["hiking", "nature", "photography"],  # Different interests
            dietary_restrictions=[],
            accessibility_needs=[],
            accommodation_type=AccommodationType.HOTEL,
            transportation_preference=TransportationPreference.PUBLIC,
        )

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "preferences" in result.changes or "interests" in result.changes
        assert "attractions" in result.affected_agents
        assert "itinerary" in result.affected_agents

    def test_dietary_restrictions_change(self, change_detector, base_trip_data):
        """Changing dietary restrictions should affect food agent."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["preferences"] = TripPreferences(
            travel_style=TravelStyle.BALANCED,
            interests=["museums", "food"],
            dietary_restrictions=["vegetarian", "gluten-free"],  # Added restrictions
            accessibility_needs=[],
            accommodation_type=AccommodationType.HOTEL,
            transportation_preference=TransportationPreference.PUBLIC,
        )

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "food" in result.affected_agents

    def test_currency_change(self, change_detector, base_trip_data):
        """Changing currency should affect currency agent."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["trip_details"] = TripDetails(
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 15),
            budget=4500.00,
            currency="EUR",  # Changed currency
            trip_purpose=TripPurpose.TOURISM,
        )

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "currency" in result.affected_agents

    def test_trip_purpose_change(self, change_detector, base_trip_data):
        """Changing trip purpose should affect visa agent."""
        old_trip = base_trip_data.copy()
        new_trip = base_trip_data.copy()
        new_trip["trip_details"] = TripDetails(
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 15),
            budget=5000.00,
            currency="USD",
            trip_purpose=TripPurpose.BUSINESS,  # Changed from TOURISM
        )

        result = change_detector.detect_changes(old_trip, new_trip)

        assert result.has_changes is True
        assert "visa" in result.affected_agents


# ============================================================================
# AFFECTED AGENTS TESTS
# ============================================================================


class TestGetAffectedAgents:
    """Test which agents are affected by specific field changes."""

    def test_destination_affects_all_major_agents(self, change_detector):
        """Destination changes should affect visa, weather, currency, culture, food, attractions, itinerary, country."""
        changes = {"destination": {"old": "France", "new": "Japan"}}

        affected = change_detector.get_affected_agents(changes)

        expected = {"visa", "weather", "currency", "culture", "food", "attractions", "itinerary", "country"}
        assert expected.issubset(set(affected))

    def test_date_changes_affect_weather_and_itinerary(self, change_detector):
        """Date changes should affect weather and itinerary only."""
        changes = {"departure_date": {"old": "2025-06-01", "new": "2025-07-01"}}

        affected = change_detector.get_affected_agents(changes)

        assert "weather" in affected
        assert "itinerary" in affected
        assert "visa" not in affected  # Dates don't affect visa

    def test_nationality_affects_visa(self, change_detector):
        """Nationality changes should affect visa agent."""
        changes = {"nationality": {"old": "US", "new": "GB"}}

        affected = change_detector.get_affected_agents(changes)

        assert "visa" in affected

    def test_multiple_changes_combine_agents(self, change_detector):
        """Multiple changes should combine all affected agents."""
        changes = {
            "nationality": {"old": "US", "new": "GB"},
            "budget": {"old": 5000, "new": 10000},
        }

        affected = change_detector.get_affected_agents(changes)

        assert "visa" in affected  # From nationality
        assert "currency" in affected  # From budget
        assert "itinerary" in affected  # From budget


# ============================================================================
# CHANGE RESULT MODEL TESTS
# ============================================================================


class TestChangeResult:
    """Test ChangeResult model."""

    def test_change_result_creation(self):
        """ChangeResult should be created correctly."""
        result = ChangeResult(
            has_changes=True,
            changes={"destination": {"old": "France", "new": "Japan"}},
            affected_agents=["visa", "weather"],
            estimated_recalc_time=30,
        )

        assert result.has_changes is True
        assert len(result.changes) == 1
        assert len(result.affected_agents) == 2
        assert result.estimated_recalc_time == 30

    def test_empty_change_result(self):
        """Empty ChangeResult should have no changes."""
        result = ChangeResult(
            has_changes=False,
            changes={},
            affected_agents=[],
            estimated_recalc_time=0,
        )

        assert result.has_changes is False
        assert len(result.changes) == 0
        assert len(result.affected_agents) == 0


# ============================================================================
# AGENT DEPENDENCIES TESTS
# ============================================================================


class TestAgentDependencies:
    """Test agent dependency mappings."""

    def test_visa_dependencies(self, change_detector):
        """Visa agent should depend on nationality, destination, and trip_purpose."""
        deps = change_detector.AGENT_DEPENDENCIES.get("visa", [])

        assert "nationality" in deps
        assert "destination" in deps
        assert "trip_purpose" in deps

    def test_weather_dependencies(self, change_detector):
        """Weather agent should depend on destination and dates."""
        deps = change_detector.AGENT_DEPENDENCIES.get("weather", [])

        assert "destination" in deps
        assert "departure_date" in deps
        assert "return_date" in deps

    def test_currency_dependencies(self, change_detector):
        """Currency agent should depend on destination, budget, and currency."""
        deps = change_detector.AGENT_DEPENDENCIES.get("currency", [])

        assert "destination" in deps
        assert "budget" in deps
        assert "currency" in deps

    def test_food_dependencies(self, change_detector):
        """Food agent should depend on destination and dietary_restrictions."""
        deps = change_detector.AGENT_DEPENDENCIES.get("food", [])

        assert "destination" in deps
        assert "dietary_restrictions" in deps

    def test_attractions_dependencies(self, change_detector):
        """Attractions agent should depend on destination, interests, and budget."""
        deps = change_detector.AGENT_DEPENDENCIES.get("attractions", [])

        assert "destination" in deps
        assert "interests" in deps
        assert "budget" in deps

    def test_itinerary_dependencies(self, change_detector):
        """Itinerary agent should depend on most fields."""
        deps = change_detector.AGENT_DEPENDENCIES.get("itinerary", [])

        assert "destination" in deps
        assert "departure_date" in deps
        assert "return_date" in deps
        assert "interests" in deps


# ============================================================================
# ESTIMATED TIME CALCULATION TESTS
# ============================================================================


class TestEstimatedTime:
    """Test recalculation time estimation."""

    def test_single_agent_time(self, change_detector):
        """Single agent recalc should take ~15 seconds."""
        agents = ["weather"]

        time = change_detector.estimate_recalc_time(agents)

        assert 10 <= time <= 30  # Approximate range

    def test_multiple_agents_time(self, change_detector):
        """Multiple agents should take proportionally longer."""
        agents = ["visa", "weather", "currency", "itinerary"]

        time = change_detector.estimate_recalc_time(agents)

        assert time >= 40  # At least 10s per agent
        assert time <= 120  # Not unreasonably long

    def test_full_recalc_time(self, change_detector):
        """Full recalc of all agents should give reasonable estimate."""
        agents = ["visa", "country", "weather", "currency", "culture", "food", "attractions", "itinerary"]

        time = change_detector.estimate_recalc_time(agents)

        assert time >= 80  # At least 10s per agent
        assert time <= 240  # Not unreasonably long
