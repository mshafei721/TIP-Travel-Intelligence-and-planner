"""
Country Agent Pydantic Models

Defines input and output data structures for the Country Agent.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from ..interfaces import AgentResult


class CountryAgentInput(BaseModel):
    """Input model for Country Agent."""

    trip_id: str = Field(..., description="Unique trip identifier")
    destination_country: str = Field(..., description="Country name or ISO code")
    destination_city: Optional[str] = Field(None, description="Primary destination city")
    departure_date: date = Field(..., description="Trip departure date")
    return_date: date = Field(..., description="Trip return date")
    traveler_nationality: Optional[str] = Field(None, description="Traveler's nationality")

    @field_validator("destination_country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Ensure country name is not empty."""
        if not v or not v.strip():
            raise ValueError("Destination country cannot be empty")
        return v.strip()

    @field_validator("return_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Ensure return date is after departure date."""
        if "departure_date" in info.data and v < info.data["departure_date"]:
            raise ValueError("Return date must be after departure date")
        return v


class EmergencyContact(BaseModel):
    """Emergency contact information."""

    service: str = Field(..., description="Service name (e.g., Police, Ambulance, Fire)")
    number: str = Field(..., description="Phone number")
    notes: Optional[str] = Field(None, description="Additional information")


class PowerOutletInfo(BaseModel):
    """Power outlet and voltage information."""

    plug_types: list[str] = Field(..., description="Plug types used (e.g., A, B, C)")
    voltage: str = Field(..., description="Standard voltage (e.g., 230V)")
    frequency: str = Field(..., description="Frequency (e.g., 50Hz)")


class TravelAdvisory(BaseModel):
    """Travel advisory information."""

    level: str = Field(..., description="Advisory level (e.g., Level 1, Level 2)")
    title: str = Field(..., description="Advisory title")
    summary: str = Field(..., description="Brief summary")
    updated_at: Optional[str] = Field(None, description="Last updated date")
    source: str = Field(..., description="Source of the advisory")


class CountryAgentOutput(AgentResult):
    """Output model for Country Agent."""

    # Basic Information
    country_name: str = Field(..., description="Official country name")
    country_code: str = Field(..., description="ISO 3166-1 alpha-2 code")
    capital: str = Field(..., description="Capital city")
    region: str = Field(..., description="Geographic region")
    subregion: Optional[str] = Field(None, description="Geographic subregion")

    # Demographics
    population: int = Field(..., description="Total population")
    area_km2: Optional[float] = Field(None, description="Total area in km²")
    population_density: Optional[float] = Field(None, description="Population per km²")

    # Languages and Communication
    official_languages: list[str] = Field(..., description="Official languages")
    common_languages: Optional[list[str]] = Field(None, description="Commonly spoken languages")

    # Time and Geography
    time_zones: list[str] = Field(..., description="Time zones (e.g., UTC+01:00)")
    coordinates: Optional[dict[str, float]] = Field(None, description="Latitude and longitude")
    borders: Optional[list[str]] = Field(None, description="Bordering countries")

    # Practical Information
    emergency_numbers: list[EmergencyContact] = Field(
        ..., description="Emergency contact numbers"
    )
    power_outlet: PowerOutletInfo = Field(..., description="Power outlet information")
    driving_side: str = Field(..., description="Driving side: 'left' or 'right'")

    # Currency
    currencies: list[str] = Field(..., description="Official currencies")
    currency_codes: list[str] = Field(..., description="Currency ISO codes")

    # Safety and Advisories
    safety_rating: float = Field(
        ..., ge=0.0, le=5.0, description="Safety rating (0-5)"
    )
    travel_advisories: list[TravelAdvisory] = Field(
        default_factory=list, description="Current travel advisories"
    )

    # Additional Information
    notable_facts: list[str] = Field(
        default_factory=list, description="Interesting facts about the country"
    )
    best_time_to_visit: Optional[str] = Field(
        None, description="Recommended time to visit"
    )

    # Metadata (inherited from AgentResult)
    # trip_id: str
    # agent_type: str = "country"
    # generated_at: datetime
    # confidence_score: float
    # sources: list[SourceReference]
    # warnings: list[str]

    model_config = {"json_schema_extra": {
        "example": {
            "trip_id": "550e8400-e29b-41d4-a716-446655440000",
            "agent_type": "country",
            "generated_at": "2025-12-25T10:00:00Z",
            "confidence_score": 0.95,
            "country_name": "France",
            "country_code": "FR",
            "capital": "Paris",
            "region": "Europe",
            "subregion": "Western Europe",
            "population": 67391582,
            "area_km2": 643801.0,
            "population_density": 104.7,
            "official_languages": ["French"],
            "time_zones": ["UTC+01:00"],
            "emergency_numbers": [
                {
                    "service": "Emergency (All Services)",
                    "number": "112",
                    "notes": "EU standard emergency number"
                },
                {
                    "service": "Police",
                    "number": "17",
                    "notes": "National police"
                }
            ],
            "power_outlet": {
                "plug_types": ["C", "E"],
                "voltage": "230V",
                "frequency": "50Hz"
            },
            "driving_side": "right",
            "currencies": ["Euro"],
            "currency_codes": ["EUR"],
            "safety_rating": 4.5,
            "travel_advisories": [],
            "sources": [
                {
                    "name": "REST Countries API",
                    "url": "https://restcountries.com/v3.1/name/france",
                    "accessed_at": "2025-12-25T10:00:00Z",
                    "reliability": "official"
                }
            ],
            "warnings": []
        }
    }}
