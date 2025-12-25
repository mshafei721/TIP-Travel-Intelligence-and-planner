"""
Data models for Itinerary Agent

Defines input/output structures for trip itinerary generation including
daily plans, activities, meals, transportation, and accommodation.
"""

from datetime import datetime
from datetime import date as date_type
from datetime import time as datetime_time
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from ..interfaces import AgentResult


class ItineraryAgentInput(BaseModel):
    """
    Input model for Itinerary Agent

    Synthesizes data from all other agents to create a comprehensive
    day-by-day itinerary optimized for traveler preferences.
    """

    # Trip identification
    trip_id: str = Field(..., description="Unique trip identifier")

    # Destination
    destination_country: str = Field(..., min_length=1, description="Destination country")
    destination_city: Optional[str] = Field(None, description="Destination city")

    # Dates
    departure_date: date_type = Field(..., description="Trip start date")
    return_date: date_type = Field(..., description="Trip end date")

    # Traveler profile
    traveler_nationality: Optional[str] = Field(None, description="Traveler nationality")
    group_size: int = Field(1, ge=1, le=20, description="Number of travelers")
    traveler_ages: Optional[list[int]] = Field(None, description="Ages of travelers")

    # Preferences
    budget_level: str = Field(
        "mid-range",
        description="Budget level: budget, mid-range, luxury",
    )
    pace: str = Field(
        "moderate",
        description="Trip pace: relaxed, moderate, packed",
    )
    interests: Optional[list[str]] = Field(
        None,
        description="Interests: history, art, culture, nature, food, adventure, relaxation",
    )

    # Constraints
    mobility_constraints: Optional[list[str]] = Field(
        None, description="Mobility limitations or accessibility needs"
    )
    dietary_restrictions: Optional[list[str]] = Field(
        None, description="Dietary restrictions"
    )

    # Optional agent data to incorporate
    visa_info: Optional[dict] = Field(None, description="Visa requirements from VisaAgent")
    country_info: Optional[dict] = Field(None, description="Country data from CountryAgent")
    weather_info: Optional[dict] = Field(None, description="Weather forecast from WeatherAgent")
    attractions_info: Optional[dict] = Field(
        None, description="Attractions from AttractionsAgent"
    )

    @field_validator("destination_country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Validate destination country is not empty."""
        if not v or v.strip() == "":
            raise ValueError("Destination country cannot be empty")
        return v.strip()

    @field_validator("return_date")
    @classmethod
    def validate_dates(cls, v: date_type, info) -> date_type:
        """Validate return date is after departure date."""
        if "departure_date" in info.data and v <= info.data["departure_date"]:
            raise ValueError("Return date must be after departure date")
        return v

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v: str) -> str:
        """Validate budget level."""
        valid_budgets = ["budget", "mid-range", "luxury"]
        if v not in valid_budgets:
            raise ValueError(f"Budget level must be one of: {valid_budgets}")
        return v

    @field_validator("pace")
    @classmethod
    def validate_pace(cls, v: str) -> str:
        """Validate trip pace."""
        valid_paces = ["relaxed", "moderate", "packed"]
        if v not in valid_paces:
            raise ValueError(f"Pace must be one of: {valid_paces}")
        return v


class Activity(BaseModel):
    """Single activity in the itinerary"""

    name: str = Field(..., description="Activity name")
    category: str = Field(
        ...,
        description="Category: sightseeing, museum, nature, food, shopping, relaxation, adventure",
    )
    location: str = Field(..., description="Activity location")
    start_time: Optional[datetime_time] = Field(None, description="Suggested start time")
    duration_minutes: int = Field(..., ge=15, le=480, description="Duration in minutes")
    cost_estimate: Optional[str] = Field(None, description="Estimated cost")
    booking_required: bool = Field(False, description="Whether advance booking needed")
    booking_url: Optional[str] = Field(None, description="Booking URL if available")
    description: Optional[str] = Field(None, description="Activity description")
    tips: Optional[list[str]] = Field(None, description="Helpful tips")
    priority: str = Field(
        "recommended",
        description="Priority: must-see, recommended, optional",
    )


class Meal(BaseModel):
    """Meal suggestion in the itinerary"""

    meal_type: str = Field(..., description="Type: breakfast, lunch, dinner, snack")
    time: Optional[datetime_time] = Field(None, description="Suggested time")
    restaurant_name: Optional[str] = Field(None, description="Restaurant suggestion")
    cuisine: Optional[str] = Field(None, description="Cuisine type")
    location: str = Field(..., description="Location/neighborhood")
    cost_estimate: str = Field(..., description="Price range: $, $$, $$$, $$$$")
    description: Optional[str] = Field(None, description="Why recommended")


class Transportation(BaseModel):
    """Transportation between locations"""

    from_location: str = Field(..., description="Starting location")
    to_location: str = Field(..., description="Destination location")
    mode: str = Field(
        ..., description="Mode: walk, taxi, metro, bus, train, car, bike"
    )
    duration_minutes: int = Field(..., ge=1, description="Travel time in minutes")
    cost_estimate: Optional[str] = Field(None, description="Estimated cost")
    notes: Optional[str] = Field(None, description="Additional notes")


class DayPlan(BaseModel):
    """Complete plan for one day"""

    day_number: int = Field(..., ge=1, description="Day number in trip")
    date: date_type = Field(..., description="Date of this day")
    theme: Optional[str] = Field(None, description="Theme for the day")
    morning_activities: list[Activity] = Field(
        default_factory=list, description="Morning activities"
    )
    afternoon_activities: list[Activity] = Field(
        default_factory=list, description="Afternoon activities"
    )
    evening_activities: list[Activity] = Field(
        default_factory=list, description="Evening activities"
    )
    meals: list[Meal] = Field(default_factory=list, description="Meal suggestions")
    transportation: list[Transportation] = Field(
        default_factory=list, description="Transportation between locations"
    )
    daily_cost_estimate: Optional[str] = Field(None, description="Total daily cost range")
    notes: Optional[list[str]] = Field(None, description="Important notes for the day")


class Accommodation(BaseModel):
    """Accommodation suggestion"""

    name: str = Field(..., description="Hotel/accommodation name")
    type: str = Field(
        ..., description="Type: hotel, hostel, apartment, guesthouse, resort"
    )
    neighborhood: str = Field(..., description="Neighborhood/area")
    price_range: str = Field(..., description="Price range per night")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Rating out of 5")
    amenities: Optional[list[str]] = Field(None, description="Key amenities")
    booking_url: Optional[str] = Field(None, description="Booking URL")
    why_recommended: Optional[str] = Field(
        None, description="Why this accommodation is recommended"
    )


class ItineraryAgentOutput(AgentResult):
    """
    Output model for Itinerary Agent

    Comprehensive day-by-day itinerary with activities, meals, transportation,
    accommodation suggestions, and cost estimates.
    """

    # Daily plans (core output)
    daily_plans: list[DayPlan] = Field(
        ..., description="Day-by-day itinerary plans"
    )

    # Cost estimates
    total_estimated_cost: Optional[str] = Field(
        None, description="Total trip cost estimate range"
    )
    cost_breakdown: Optional[dict[str, str]] = Field(
        None,
        description="Cost breakdown: activities, meals, transportation, accommodation",
    )

    # Transportation planning
    transportation_plan: Optional[str] = Field(
        None, description="Overall transportation strategy"
    )
    getting_around_tips: Optional[list[str]] = Field(
        None, description="Tips for getting around the destination"
    )

    # Accommodation
    accommodation_suggestions: list[Accommodation] = Field(
        default_factory=list, description="Recommended accommodations"
    )

    # Optimization and tips
    optimization_notes: Optional[list[str]] = Field(
        None, description="How the itinerary was optimized"
    )
    packing_checklist: Optional[list[str]] = Field(
        None, description="What to pack for this itinerary"
    )
    pro_tips: Optional[list[str]] = Field(
        None, description="Pro tips for this destination"
    )

    # Alternative suggestions
    flexible_alternatives: Optional[dict[str, list[str]]] = Field(
        None,
        description="Alternative activities if plans change (by day)",
    )
