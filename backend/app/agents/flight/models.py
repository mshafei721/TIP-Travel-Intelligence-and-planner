"""
Flight Agent - Pydantic Models

Data models for flight agent input and output.
"""

from datetime import date as DateType
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CabinClass(str, Enum):
    """Flight cabin class options."""

    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class FlightAgentInput(BaseModel):
    """Input model for Flight Agent."""

    trip_id: str = Field(..., description="Unique trip identifier")
    origin_city: str = Field(..., description="Departure city")
    destination_city: str = Field(..., description="Arrival city")
    departure_date: DateType = Field(..., description="Departure date")
    return_date: Optional[DateType] = Field(None, description="Return date (None for one-way)")
    passengers: int = Field(default=1, ge=1, le=9, description="Number of passengers")
    cabin_class: CabinClass = Field(default=CabinClass.ECONOMY, description="Preferred cabin class")
    budget_usd: Optional[float] = Field(None, ge=0, description="Maximum budget per person in USD")
    direct_flights_only: bool = Field(
        default=False, description="Whether to search only direct flights"
    )
    flexible_dates: bool = Field(default=True, description="Whether to consider nearby dates")

    @field_validator("return_date")
    @classmethod
    def validate_return_date(cls, v: Optional[DateType], info) -> Optional[DateType]:
        """Validate return date is after departure date."""
        if v is not None and "departure_date" in info.data:
            if v <= info.data["departure_date"]:
                raise ValueError("Return date must be after departure date")
        return v


class Airport(BaseModel):
    """Airport information."""

    code: str = Field(..., description="IATA airport code (e.g., 'JFK')")
    name: str = Field(..., description="Full airport name")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name")
    timezone: Optional[str] = Field(None, description="Airport timezone")


class FlightSegment(BaseModel):
    """Individual flight segment (for connecting flights)."""

    departure_airport: Airport
    arrival_airport: Airport
    departure_time: datetime
    arrival_time: datetime
    airline: str = Field(..., description="Airline name")
    airline_code: str = Field(..., description="IATA airline code")
    flight_number: str = Field(..., description="Flight number")
    aircraft_type: Optional[str] = Field(None, description="Aircraft model")
    duration_minutes: int = Field(..., ge=0, description="Flight duration in minutes")


class Flight(BaseModel):
    """Complete flight option (outbound or return)."""

    segments: list[FlightSegment] = Field(..., min_length=1, description="Flight segments")
    total_duration_minutes: int = Field(..., ge=0, description="Total travel duration")
    departure_time: datetime = Field(..., description="First segment departure")
    arrival_time: datetime = Field(..., description="Last segment arrival")
    is_direct: bool = Field(..., description="Whether it's a direct flight")
    layover_airports: list[str] = Field(
        default_factory=list, description="List of layover airport codes"
    )
    layover_durations_minutes: list[int] = Field(
        default_factory=list, description="Layover durations in minutes"
    )


class FlightOption(BaseModel):
    """Complete flight booking option (round-trip or one-way)."""

    outbound_flight: Flight = Field(..., description="Outbound flight")
    return_flight: Optional[Flight] = Field(None, description="Return flight (if round-trip)")
    price_usd: float = Field(..., ge=0, description="Total price in USD")
    cabin_class: CabinClass = Field(..., description="Cabin class")
    booking_url: Optional[str] = Field(None, description="Direct booking link")
    provider: str = Field(..., description="Flight provider/OTA")
    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="Price last updated"
    )
    seats_available: Optional[int] = Field(None, description="Available seats")
    refundable: bool = Field(default=False, description="Whether ticket is refundable")
    changeable: bool = Field(default=False, description="Whether ticket is changeable")


class AirportInfo(BaseModel):
    """Airport and transportation information."""

    departure_airport: Airport
    arrival_airport: Airport
    transportation_options: list[str] = Field(
        default_factory=list, description="Ways to reach city center"
    )
    avg_transfer_time_minutes: Optional[int] = Field(
        None, description="Average transfer time to city"
    )
    facilities: list[str] = Field(
        default_factory=list, description="Airport facilities (lounges, wifi, etc.)"
    )
    tips: list[str] = Field(default_factory=list, description="Airport-specific tips")


class FlightAgentOutput(BaseModel):
    """Output model for Flight Agent."""

    trip_id: str = Field(..., description="Trip identifier")
    recommended_flights: list[FlightOption] = Field(
        ..., max_length=5, description="Top 5 recommended flight options"
    )
    price_range: dict[str, float] = Field(
        ...,
        description="Price range (min, max, average) in USD",
        example={"min": 450.0, "max": 1200.0, "average": 750.0},
    )
    best_time_to_book: Optional[str] = Field(
        None, description="Optimal booking timing recommendation"
    )
    booking_tips: list[str] = Field(default_factory=list, description="General flight booking tips")
    airport_info: AirportInfo = Field(..., description="Airport and transport info")
    layover_suggestions: Optional[list[str]] = Field(
        None, description="Tips for layover airports if applicable"
    )
    alternative_routes: Optional[list[str]] = Field(
        None, description="Alternative routing suggestions"
    )
    seasonal_notes: Optional[list[str]] = Field(
        None, description="Seasonal flight availability notes"
    )
    baggage_tips: list[str] = Field(default_factory=list, description="Baggage allowance and tips")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Generation timestamp"
    )
    confidence_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Agent confidence (0-1)"
    )
    sources: list[str] = Field(
        default_factory=list, description="Data sources for flight information"
    )
    warnings: list[str] = Field(default_factory=list, description="Important warnings or notices")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                "recommended_flights": [],
                "price_range": {"min": 450.0, "max": 1200.0, "average": 750.0},
                "best_time_to_book": "Book 2-3 months in advance for best prices",
                "booking_tips": [
                    "Consider booking Tuesday or Wednesday for lower fares",
                    "Enable price alerts to track fare changes",
                ],
                "generated_at": "2024-12-26T12:00:00Z",
                "confidence_score": 0.85,
                "sources": ["Flight search engine data", "Historical pricing trends"],
            }
        }
