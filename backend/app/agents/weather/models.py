"""Data models for Weather Agent."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from ..interfaces import AgentInput, AgentResult


class DailyForecast(BaseModel):
    """Daily weather forecast model."""

    date: date = Field(description="Date of the forecast")
    temp_max: float = Field(description="Maximum temperature (Celsius)")
    temp_min: float = Field(description="Minimum temperature (Celsius)")
    temp_avg: float | None = Field(None, description="Average temperature (Celsius)")
    conditions: str = Field(description="Weather conditions description")
    icon: str | None = Field(None, description="Weather icon identifier")
    precipitation_prob: float = Field(description="Probability of precipitation (0-100%)")
    precipitation_amount: float | None = Field(None, description="Precipitation amount (mm)")
    humidity: float | None = Field(None, description="Humidity percentage (0-100%)")
    wind_speed: float | None = Field(None, description="Wind speed (km/h)")
    wind_direction: str | None = Field(None, description="Wind direction (N/S/E/W)")
    uv_index: int | None = Field(None, description="UV index (0-11+)")
    sunrise: str | None = Field(None, description="Sunrise time (HH:MM)")
    sunset: str | None = Field(None, description="Sunset time (HH:MM)")
    description: str | None = Field(None, description="Additional weather description")


class PackingSuggestion(BaseModel):
    """Packing suggestion based on weather."""

    item: str = Field(description="Item to pack")
    reason: str = Field(description="Reason for packing this item")
    priority: Literal["essential", "recommended", "optional"] = Field(description="Priority level")


class ClimateInfo(BaseModel):
    """Climate information for the destination."""

    climate_type: str = Field(description="Climate classification (e.g., Tropical, Temperate)")
    best_time_to_visit: str = Field(description="Recommended time period to visit")
    worst_time_to_visit: str | None = Field(None, description="Time period to avoid")
    seasonal_notes: list[str] = Field(default_factory=list, description="Seasonal considerations")


class WeatherAgentInput(AgentInput):
    """Input model for Weather Agent."""

    trip_id: str = Field(description="Unique trip identifier")
    user_nationality: str = Field(description="User's nationality (ISO 3166-1 alpha-2)")
    destination_country: str = Field(description="Destination country name")
    destination_city: str = Field(description="Destination city name")
    departure_date: date = Field(description="Trip departure date")
    return_date: date = Field(description="Trip return date")
    latitude: float | None = Field(None, description="Destination latitude for precise location")
    longitude: float | None = Field(None, description="Destination longitude for precise location")


class WeatherAgentOutput(AgentResult):
    """Output model for Weather Agent."""

    trip_id: str = Field(description="Unique trip identifier")
    agent_type: Literal["weather"] = Field(default="weather", description="Agent type identifier")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Generation timestamp"
    )

    # Location
    location: str = Field(description="Location queried")
    latitude: float | None = Field(None, description="Location latitude")
    longitude: float | None = Field(None, description="Location longitude")
    timezone: str | None = Field(None, description="Location timezone")

    # Weather forecast
    forecast: list[DailyForecast] = Field(
        default_factory=list, description="Daily weather forecasts"
    )

    # Aggregated metrics
    average_temp: float = Field(description="Average temperature for trip (Celsius)")
    temp_range_min: float = Field(description="Lowest expected temperature (Celsius)")
    temp_range_max: float = Field(description="Highest expected temperature (Celsius)")
    precipitation_chance: float = Field(description="Overall precipitation probability (0-100%)")
    total_precipitation: float | None = Field(None, description="Total expected precipitation (mm)")

    # Recommendations
    packing_suggestions: list[PackingSuggestion] = Field(
        default_factory=list, description="Packing recommendations based on weather"
    )
    climate_info: ClimateInfo | None = Field(
        None, description="Climate information for the destination"
    )
    weather_alerts: list[str] = Field(
        default_factory=list, description="Active weather alerts or warnings"
    )
    travel_tips: list[str] = Field(
        default_factory=list,
        description="Weather-related travel tips and recommendations",
    )

    # Metadata
    confidence_score: float = Field(description="Confidence in forecast accuracy (0.0-1.0)")
    sources: list[str] = Field(
        default_factory=list, description="Data sources for weather information"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Warnings or caveats about the forecast"
    )

    # Best time assessment
    is_good_time_to_visit: bool | None = Field(
        None, description="Whether the trip dates are a good time weather-wise"
    )
    seasonal_recommendation: str | None = Field(
        None, description="Seasonal recommendation for the destination"
    )
