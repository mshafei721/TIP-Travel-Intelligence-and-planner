"""Pydantic models for analytics endpoints"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DateRange(str, Enum):
    """Date range options for analytics queries"""

    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


class DestinationCount(BaseModel):
    """Popular destination with visit count"""

    country: str
    country_code: str | None = None
    city: str | None = None
    count: int
    percentage: float = Field(..., ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "country": "Japan",
                "country_code": "JP",
                "city": "Tokyo",
                "count": 5,
                "percentage": 25.0,
            }
        }


class BudgetRange(BaseModel):
    """Budget range distribution"""

    range_label: str = Field(..., description="e.g., '$0-500', '$500-1000'")
    min_value: float
    max_value: float | None = None  # None for "unlimited" ranges
    count: int
    percentage: float = Field(..., ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "range_label": "$500-1000",
                "min_value": 500,
                "max_value": 1000,
                "count": 8,
                "percentage": 40.0,
            }
        }


class SeasonalCount(BaseModel):
    """Seasonal trip distribution"""

    season: str = Field(..., description="spring, summer, fall, winter")
    count: int
    percentage: float = Field(..., ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "season": "summer",
                "count": 12,
                "percentage": 35.0,
            }
        }


class PurposeCount(BaseModel):
    """Trip purpose distribution"""

    purpose: str = Field(..., description="leisure, business, family, adventure, etc.")
    count: int
    percentage: float = Field(..., ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "purpose": "leisure",
                "count": 15,
                "percentage": 60.0,
            }
        }


class AgentUsageStats(BaseModel):
    """Per-agent usage statistics"""

    agent_type: str
    invocations: int
    avg_duration_seconds: float | None = None
    success_rate: float = Field(..., ge=0, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "visa",
                "invocations": 25,
                "avg_duration_seconds": 12.5,
                "success_rate": 96.0,
            }
        }


class UsageStats(BaseModel):
    """User usage statistics summary"""

    period: DateRange
    period_start: datetime | None = None
    period_end: datetime | None = None

    # Trip metrics
    total_trips: int = 0
    trips_created: int = 0
    trips_completed: int = 0
    trips_in_progress: int = 0
    trips_draft: int = 0

    # Report metrics
    reports_generated: int = 0
    reports_exported_pdf: int = 0

    # Agent metrics
    agents_invoked: dict[str, int] = Field(default_factory=dict)
    agent_stats: list[AgentUsageStats] = Field(default_factory=list)
    avg_generation_time_seconds: float | None = None

    # Engagement metrics
    destinations_explored: int = 0
    countries_planned: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "period": "month",
                "period_start": "2025-11-01T00:00:00Z",
                "period_end": "2025-11-30T23:59:59Z",
                "total_trips": 10,
                "trips_created": 3,
                "trips_completed": 5,
                "trips_in_progress": 2,
                "trips_draft": 0,
                "reports_generated": 5,
                "reports_exported_pdf": 2,
                "agents_invoked": {
                    "visa": 5,
                    "weather": 5,
                    "country": 5,
                    "itinerary": 4,
                },
                "avg_generation_time_seconds": 45.3,
                "destinations_explored": 8,
                "countries_planned": 4,
            }
        }


class UsageTrend(BaseModel):
    """Usage trend data point for charts"""

    date: str = Field(..., description="ISO date string")
    trips_created: int = 0
    reports_generated: int = 0
    countries_visited: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-12-01",
                "trips_created": 2,
                "reports_generated": 2,
                "countries_visited": 3,
            }
        }


class TripAnalytics(BaseModel):
    """Comprehensive trip analytics"""

    period: DateRange
    period_start: datetime | None = None
    period_end: datetime | None = None

    # Destination analytics
    top_destinations: list[DestinationCount] = Field(default_factory=list)
    unique_countries: int = 0
    unique_cities: int = 0

    # Budget analytics
    budget_ranges: list[BudgetRange] = Field(default_factory=list)
    avg_budget: float | None = None
    total_planned_budget: float = 0

    # Duration analytics
    avg_trip_duration_days: float | None = None
    shortest_trip_days: int | None = None
    longest_trip_days: int | None = None

    # Seasonal preferences
    seasonal_distribution: list[SeasonalCount] = Field(default_factory=list)

    # Purpose distribution
    purpose_distribution: list[PurposeCount] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "period": "year",
                "top_destinations": [
                    {
                        "country": "Japan",
                        "country_code": "JP",
                        "city": "Tokyo",
                        "count": 5,
                        "percentage": 25.0,
                    }
                ],
                "unique_countries": 8,
                "unique_cities": 15,
                "budget_ranges": [
                    {
                        "range_label": "$1000-2000",
                        "min_value": 1000,
                        "max_value": 2000,
                        "count": 6,
                        "percentage": 30.0,
                    }
                ],
                "avg_budget": 1500.0,
                "total_planned_budget": 30000.0,
                "avg_trip_duration_days": 7.5,
                "shortest_trip_days": 3,
                "longest_trip_days": 14,
                "seasonal_distribution": [
                    {"season": "summer", "count": 8, "percentage": 40.0}
                ],
                "purpose_distribution": [
                    {"purpose": "leisure", "count": 12, "percentage": 60.0}
                ],
            }
        }


# Request/Response models
class UsageStatsRequest(BaseModel):
    """Request model for usage statistics"""

    period: DateRange = DateRange.MONTH

    class Config:
        json_schema_extra = {"example": {"period": "month"}}


class TripAnalyticsRequest(BaseModel):
    """Request model for trip analytics"""

    period: DateRange = DateRange.YEAR
    limit_destinations: int = Field(default=10, ge=1, le=50)

    class Config:
        json_schema_extra = {"example": {"period": "year", "limit_destinations": 10}}


class UsageStatsResponse(BaseModel):
    """Response model for usage statistics endpoint"""

    success: bool = True
    data: UsageStats

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "period": "month",
                    "total_trips": 10,
                    "trips_created": 3,
                    "trips_completed": 5,
                },
            }
        }


class UsageTrendsResponse(BaseModel):
    """Response model for usage trends endpoint"""

    success: bool = True
    period: DateRange
    data: list[UsageTrend]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "period": "month",
                "data": [
                    {
                        "date": "2025-12-01",
                        "trips_created": 2,
                        "reports_generated": 2,
                        "countries_visited": 3,
                    }
                ],
            }
        }


class TripAnalyticsResponse(BaseModel):
    """Response model for trip analytics endpoint"""

    success: bool = True
    data: TripAnalytics

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "period": "year",
                    "unique_countries": 8,
                    "avg_budget": 1500.0,
                },
            }
        }


class AgentUsageResponse(BaseModel):
    """Response model for agent usage statistics"""

    success: bool = True
    period: DateRange
    data: list[AgentUsageStats]
    total_invocations: int

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "period": "month",
                "data": [
                    {
                        "agent_type": "visa",
                        "invocations": 25,
                        "avg_duration_seconds": 12.5,
                        "success_rate": 96.0,
                    }
                ],
                "total_invocations": 150,
            }
        }
