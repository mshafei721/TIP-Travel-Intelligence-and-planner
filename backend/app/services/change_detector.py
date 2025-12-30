"""
Change Detector Service for Trip Updates

Detects changes between old and new trip data, and determines which agents
need to be re-run for selective recalculation.
"""

from datetime import date
from typing import Any

from pydantic import BaseModel

from app.models.trips import (
    Destination,
    TravelerDetails,
    TripDetails,
    TripPreferences,
)


class ChangeResult(BaseModel):
    """Result of change detection."""

    has_changes: bool
    changes: dict[str, dict[str, Any]]
    affected_agents: list[str]
    estimated_recalc_time: int  # seconds


class ChangeDetector:
    """
    Detects changes between old and new trip data and determines
    which AI agents need recalculation.

    Usage:
        detector = ChangeDetector()
        result = detector.detect_changes(old_trip_data, new_trip_data)

        if result.has_changes:
            print(f"Changes detected in: {list(result.changes.keys())}")
            print(f"Affected agents: {result.affected_agents}")
            print(f"Estimated recalc time: {result.estimated_recalc_time}s")
    """

    # Agent dependencies - which fields affect which agents
    AGENT_DEPENDENCIES: dict[str, list[str]] = {
        "visa": ["nationality", "destination", "trip_purposes"],
        "weather": ["destination", "departure_date", "return_date"],
        "currency": ["destination", "budget", "currency"],
        "culture": ["destination"],
        "food": ["destination", "dietary_restrictions"],
        "attractions": ["destination", "interests", "budget"],
        "itinerary": [
            "destination",
            "departure_date",
            "return_date",
            "interests",
            "budget",
            "travel_style",
            "accommodation_type",
            "transportation_preference",
        ],
        "country": ["destination"],
        "flight": ["origin_city", "destination", "departure_date", "return_date"],
    }

    # Average time per agent in seconds
    AGENT_TIMES: dict[str, int] = {
        "visa": 15,
        "weather": 10,
        "currency": 10,
        "culture": 15,
        "food": 15,
        "attractions": 20,
        "itinerary": 25,
        "country": 10,
        "flight": 15,
    }

    def detect_changes(
        self,
        old_trip: dict[str, Any],
        new_trip: dict[str, Any],
    ) -> ChangeResult:
        """
        Detect changes between old and new trip data.

        Args:
            old_trip: Previous trip data (dict with traveler_details, destinations, trip_details, preferences)
            new_trip: New trip data (same structure)

        Returns:
            ChangeResult with changes dict and affected agents list
        """
        changes: dict[str, dict[str, Any]] = {}

        # Compare traveler details
        changes.update(self._compare_traveler_details(old_trip, new_trip))

        # Compare destinations
        changes.update(self._compare_destinations(old_trip, new_trip))

        # Compare trip details
        changes.update(self._compare_trip_details(old_trip, new_trip))

        # Compare preferences
        changes.update(self._compare_preferences(old_trip, new_trip))

        # Get affected agents based on changes
        affected_agents = self.get_affected_agents(changes) if changes else []

        # Calculate estimated time
        estimated_time = self.estimate_recalc_time(affected_agents) if affected_agents else 0

        return ChangeResult(
            has_changes=len(changes) > 0,
            changes=changes,
            affected_agents=affected_agents,
            estimated_recalc_time=estimated_time,
        )

    def _compare_traveler_details(
        self,
        old_trip: dict[str, Any],
        new_trip: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Compare traveler details and detect changes."""
        changes: dict[str, dict[str, Any]] = {}

        old_td = old_trip.get("traveler_details")
        new_td = new_trip.get("traveler_details")

        if old_td is None or new_td is None:
            return changes

        # Handle both dict and TravelerDetails objects
        # Use by_alias=False to get snake_case keys for comparison
        old_dict = old_td.model_dump(by_alias=False) if isinstance(old_td, TravelerDetails) else old_td
        new_dict = new_td.model_dump(by_alias=False) if isinstance(new_td, TravelerDetails) else new_td

        # Check nationality
        if old_dict.get("nationality") != new_dict.get("nationality"):
            changes["nationality"] = {
                "old": old_dict.get("nationality"),
                "new": new_dict.get("nationality"),
            }

        # Check origin city
        if old_dict.get("origin_city") != new_dict.get("origin_city"):
            changes["origin_city"] = {
                "old": old_dict.get("origin_city"),
                "new": new_dict.get("origin_city"),
            }

        # Check residence country
        if old_dict.get("residence_country") != new_dict.get("residence_country"):
            changes["residence_country"] = {
                "old": old_dict.get("residence_country"),
                "new": new_dict.get("residence_country"),
            }

        return changes

    def _compare_destinations(
        self,
        old_trip: dict[str, Any],
        new_trip: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Compare destinations and detect changes."""
        changes: dict[str, dict[str, Any]] = {}

        old_dests = old_trip.get("destinations", [])
        new_dests = new_trip.get("destinations", [])

        # Convert to comparable format
        # Use by_alias=False to get snake_case keys for comparison
        def dest_to_dict(d: Destination | dict) -> dict:
            if isinstance(d, Destination):
                return d.model_dump(by_alias=False)
            return d

        old_list = [dest_to_dict(d) for d in old_dests]
        new_list = [dest_to_dict(d) for d in new_dests]

        # Compare destination lists
        if old_list != new_list:
            # Determine what changed
            old_countries = [d.get("country") for d in old_list]
            new_countries = [d.get("country") for d in new_list]
            old_cities = [d.get("city") for d in old_list]
            new_cities = [d.get("city") for d in new_list]

            if old_countries != new_countries or old_cities != new_cities:
                changes["destination"] = {
                    "old": old_list,
                    "new": new_list,
                }

        return changes

    def _compare_trip_details(
        self,
        old_trip: dict[str, Any],
        new_trip: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Compare trip details and detect changes."""
        changes: dict[str, dict[str, Any]] = {}

        old_td = old_trip.get("trip_details")
        new_td = new_trip.get("trip_details")

        if old_td is None or new_td is None:
            return changes

        # Handle both dict and TripDetails objects
        # Use by_alias=False to get snake_case keys for comparison
        old_dict = old_td.model_dump(by_alias=False) if isinstance(old_td, TripDetails) else old_td
        new_dict = new_td.model_dump(by_alias=False) if isinstance(new_td, TripDetails) else new_td

        # Convert dates to comparable format
        def to_date_str(d: date | str | None) -> str | None:
            if d is None:
                return None
            if isinstance(d, date):
                return d.isoformat()
            return d

        # Check departure date
        old_dep = to_date_str(old_dict.get("departure_date"))
        new_dep = to_date_str(new_dict.get("departure_date"))
        if old_dep != new_dep:
            changes["departure_date"] = {"old": old_dep, "new": new_dep}

        # Check return date
        old_ret = to_date_str(old_dict.get("return_date"))
        new_ret = to_date_str(new_dict.get("return_date"))
        if old_ret != new_ret:
            changes["return_date"] = {"old": old_ret, "new": new_ret}

        # Check budget
        if old_dict.get("budget") != new_dict.get("budget"):
            changes["budget"] = {
                "old": old_dict.get("budget"),
                "new": new_dict.get("budget"),
            }

        # Check currency
        if old_dict.get("currency") != new_dict.get("currency"):
            changes["currency"] = {
                "old": old_dict.get("currency"),
                "new": new_dict.get("currency"),
            }

        # Check trip purposes (list)
        old_purposes = sorted(old_dict.get("trip_purposes", []))
        new_purposes = sorted(new_dict.get("trip_purposes", []))
        if old_purposes != new_purposes:
            changes["trip_purposes"] = {"old": old_purposes, "new": new_purposes}

        return changes

    def _compare_preferences(
        self,
        old_trip: dict[str, Any],
        new_trip: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Compare preferences and detect changes."""
        changes: dict[str, dict[str, Any]] = {}

        old_prefs = old_trip.get("preferences")
        new_prefs = new_trip.get("preferences")

        if old_prefs is None or new_prefs is None:
            return changes

        # Handle both dict and TripPreferences objects
        # Use by_alias=False to get snake_case keys for comparison
        old_dict = old_prefs.model_dump(by_alias=False) if isinstance(old_prefs, TripPreferences) else old_prefs
        new_dict = new_prefs.model_dump(by_alias=False) if isinstance(new_prefs, TripPreferences) else new_prefs

        # Check travel style
        old_style = old_dict.get("travel_style")
        new_style = new_dict.get("travel_style")
        if hasattr(old_style, "value"):
            old_style = old_style.value
        if hasattr(new_style, "value"):
            new_style = new_style.value
        if old_style != new_style:
            changes["travel_style"] = {"old": old_style, "new": new_style}

        # Check interests
        old_interests = sorted(old_dict.get("interests", []))
        new_interests = sorted(new_dict.get("interests", []))
        if old_interests != new_interests:
            changes["interests"] = {"old": old_interests, "new": new_interests}

        # Check dietary restrictions
        old_dietary = sorted(old_dict.get("dietary_restrictions", []))
        new_dietary = sorted(new_dict.get("dietary_restrictions", []))
        if old_dietary != new_dietary:
            changes["dietary_restrictions"] = {"old": old_dietary, "new": new_dietary}

        # Check accessibility needs
        old_access = sorted(old_dict.get("accessibility_needs", []))
        new_access = sorted(new_dict.get("accessibility_needs", []))
        if old_access != new_access:
            changes["accessibility_needs"] = {"old": old_access, "new": new_access}

        # Check accommodation type
        old_accom = old_dict.get("accommodation_type")
        new_accom = new_dict.get("accommodation_type")
        if hasattr(old_accom, "value"):
            old_accom = old_accom.value
        if hasattr(new_accom, "value"):
            new_accom = new_accom.value
        if old_accom != new_accom:
            changes["accommodation_type"] = {"old": old_accom, "new": new_accom}

        # Check transportation preference
        old_trans = old_dict.get("transportation_preference")
        new_trans = new_dict.get("transportation_preference")
        if hasattr(old_trans, "value"):
            old_trans = old_trans.value
        if hasattr(new_trans, "value"):
            new_trans = new_trans.value
        if old_trans != new_trans:
            changes["transportation_preference"] = {"old": old_trans, "new": new_trans}

        return changes

    def get_affected_agents(self, changes: dict[str, dict[str, Any]]) -> list[str]:
        """
        Determine which agents need recalculation based on detected changes.

        Args:
            changes: Dict of field -> {old, new} value changes

        Returns:
            List of agent names that need recalculation
        """
        affected: set[str] = set()
        changed_fields = set(changes.keys())

        for agent, dependencies in self.AGENT_DEPENDENCIES.items():
            for dep in dependencies:
                if dep in changed_fields:
                    affected.add(agent)
                    break

        return list(affected)

    def estimate_recalc_time(self, agents: list[str]) -> int:
        """
        Estimate recalculation time for a list of agents.

        Args:
            agents: List of agent names to recalculate

        Returns:
            Estimated time in seconds
        """
        total = 0
        for agent in agents:
            total += self.AGENT_TIMES.get(agent, 15)  # Default 15s if unknown
        return total
