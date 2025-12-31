"""
Attractions Agent Pydantic Models

Defines input and output data structures for the Attractions Agent.
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator

from ..interfaces import AgentResult


class AttractionsAgentInput(BaseModel):
    """Input model for Attractions Agent."""

    trip_id: str = Field(..., description="Unique trip identifier")
    destination_country: str = Field(..., description="Country name or ISO code")
    destination_city: str | None = Field(None, description="Primary destination city")
    departure_date: date = Field(..., description="Trip departure date")
    return_date: date = Field(..., description="Trip return date")
    traveler_nationality: str | None = Field(None, description="Traveler's nationality")
    interests: list[str] | None = Field(
        None,
        description="Traveler interests (history, art, nature, adventure, culture, food, shopping)",
    )

    @field_validator("destination_country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Ensure country name is not empty."""
        if not v or not v.strip():
            msg = "Destination country cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("return_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Ensure return date is after departure date."""
        if "departure_date" in info.data and v < info.data["departure_date"]:
            msg = "Return date must be after departure date"
            raise ValueError(msg)
        return v


class Attraction(BaseModel):
    """A tourist attraction or point of interest."""

    name: str = Field(..., description="Attraction name")
    category: str = Field(
        ...,
        description="Category (museum, historical-site, natural-wonder, religious-site, architecture, park, viewpoint, other)",
    )
    description: str = Field(..., description="Description of the attraction")
    location: str | None = Field(None, description="Location/neighborhood")
    coordinates: dict[str, float] | None = Field(None, description="GPS coordinates (lat, lon)")
    opening_hours: str | None = Field(None, description="Opening hours")
    entrance_fee: str | None = Field(None, description="Entrance fee information")
    estimated_duration: str | None = Field(
        None, description="Estimated visit duration (e.g., 1-2 hours, half-day)"
    )
    best_time_to_visit: str | None = Field(
        None, description="Best time to visit (morning, afternoon, evening, weekday, weekend)"
    )
    booking_required: bool = Field(default=False, description="Whether advance booking is required")
    accessibility: str | None = Field(
        None, description="Accessibility information for mobility-impaired visitors"
    )
    tips: list[str] = Field(default_factory=list, description="Visitor tips")
    popularity_score: int | None = Field(None, description="Popularity score (1-10)", ge=1, le=10)


class HiddenGem(BaseModel):
    """A lesser-known attraction or hidden gem."""

    name: str = Field(..., description="Attraction name")
    category: str = Field(..., description="Category")
    description: str = Field(..., description="What makes it special")
    location: str | None = Field(None, description="Location/neighborhood")
    why_hidden: str = Field(..., description="Why it's considered a hidden gem")
    best_for: list[str] = Field(
        default_factory=list, description="Best for (photographers, couples, families, solo)"
    )


class DayTrip(BaseModel):
    """A recommended day trip from the destination city."""

    destination: str = Field(..., description="Day trip destination name")
    distance_km: float | None = Field(None, description="Distance in kilometers")
    transportation: str = Field(..., description="How to get there")
    duration: str = Field(..., description="Total trip duration (e.g., 8-10 hours)")
    highlights: list[str] = Field(..., description="Main highlights")
    estimated_cost: str | None = Field(None, description="Estimated cost per person")
    best_season: str | None = Field(None, description="Best season to visit")
    difficulty_level: str | None = Field(
        None, description="Difficulty level (easy, moderate, challenging)"
    )


class AttractionsAgentOutput(AgentResult):
    """Output model for Attractions Agent."""

    # AgentResult requires data field - we provide it as empty since we use specific fields
    data: dict = Field(default_factory=dict, description="Legacy field for compatibility")

    # Top Attractions
    top_attractions: list[Attraction] = Field(..., description="Must-see attractions and landmarks")

    # Hidden Gems
    hidden_gems: list[HiddenGem] = Field(
        default_factory=list, description="Lesser-known attractions off the beaten path"
    )

    # Day Trips
    day_trips: list[DayTrip] = Field(
        default_factory=list, description="Recommended day trips from the main destination"
    )

    # Categorized Attractions
    museums_and_galleries: list[str] = Field(
        default_factory=list, description="Museums and art galleries"
    )
    historical_sites: list[str] = Field(
        default_factory=list, description="Historical landmarks and sites"
    )
    natural_attractions: list[str] = Field(
        default_factory=list, description="Natural wonders and outdoor spaces"
    )
    religious_sites: list[str] = Field(
        default_factory=list, description="Religious and spiritual sites"
    )
    viewpoints_and_landmarks: list[str] = Field(
        default_factory=list, description="Scenic viewpoints and iconic landmarks"
    )

    # Estimated Costs
    estimated_costs: dict[str, str] = Field(
        ...,
        description="Estimated costs for different attraction types (museums/historical/tours)",
    )

    # Booking & Practical Tips
    booking_tips: list[str] = Field(..., description="Booking and ticket purchasing tips")
    crowd_avoidance_tips: list[str] = Field(
        default_factory=list, description="Tips for avoiding crowds"
    )
    photography_tips: list[str] = Field(
        default_factory=list, description="Photography tips and restrictions"
    )

    # Accessibility
    accessibility_notes: list[str] = Field(
        default_factory=list, description="General accessibility information"
    )
