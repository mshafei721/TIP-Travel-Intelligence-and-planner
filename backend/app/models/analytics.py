"""Pydantic models for analytics endpoints"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DateRange(str, Enum):
    """Date range options for analytics queries"""

    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


class DestinationCount(BaseModel):
    """Popular destination with visit count"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    country: str
    country_code: str | None = Field(default=None, alias="countryCode")
    city: str | None = None
    count: int
    percentage: float = Field(..., ge=0, le=100)


class BudgetRange(BaseModel):
    """Budget range distribution"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    range_label: str = Field(..., description="e.g., '$0-500', '$500-1000'", alias="rangeLabel")
    min_value: float = Field(..., alias="minValue")
    max_value: float | None = Field(default=None, alias="maxValue")  # None for "unlimited" ranges
    count: int
    percentage: float = Field(..., ge=0, le=100)


class SeasonalCount(BaseModel):
    """Seasonal trip distribution"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    season: str = Field(..., description="spring, summer, fall, winter")
    count: int
    percentage: float = Field(..., ge=0, le=100)


class PurposeCount(BaseModel):
    """Trip purpose distribution"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    purpose: str = Field(..., description="leisure, business, family, adventure, etc.")
    count: int
    percentage: float = Field(..., ge=0, le=100)


class AgentUsageStats(BaseModel):
    """Per-agent usage statistics"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    agent_type: str = Field(..., alias="agentType")
    invocations: int
    avg_duration_seconds: float | None = Field(default=None, alias="avgDurationSeconds")
    success_rate: float = Field(..., ge=0, le=100, alias="successRate")


class UsageStats(BaseModel):
    """User usage statistics summary"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    period: DateRange
    period_start: datetime | None = Field(default=None, alias="periodStart")
    period_end: datetime | None = Field(default=None, alias="periodEnd")

    # Trip metrics
    total_trips: int = Field(default=0, alias="totalTrips")
    trips_created: int = Field(default=0, alias="tripsCreated")
    trips_completed: int = Field(default=0, alias="tripsCompleted")
    trips_in_progress: int = Field(default=0, alias="tripsInProgress")
    trips_draft: int = Field(default=0, alias="tripsDraft")

    # Report metrics
    reports_generated: int = Field(default=0, alias="reportsGenerated")
    reports_exported_pdf: int = Field(default=0, alias="reportsExportedPdf")

    # Agent metrics
    agents_invoked: dict[str, int] = Field(default_factory=dict, alias="agentsInvoked")
    agent_stats: list[AgentUsageStats] = Field(default_factory=list, alias="agentStats")
    avg_generation_time_seconds: float | None = Field(default=None, alias="avgGenerationTimeSeconds")

    # Engagement metrics
    destinations_explored: int = Field(default=0, alias="destinationsExplored")
    countries_planned: int = Field(default=0, alias="countriesPlanned")


class UsageTrend(BaseModel):
    """Usage trend data point for charts"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    date: str = Field(..., description="ISO date string")
    trips_created: int = Field(default=0, alias="tripsCreated")
    reports_generated: int = Field(default=0, alias="reportsGenerated")
    countries_visited: int = Field(default=0, alias="countriesVisited")


class TripAnalytics(BaseModel):
    """Comprehensive trip analytics"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    period: DateRange
    period_start: datetime | None = Field(default=None, alias="periodStart")
    period_end: datetime | None = Field(default=None, alias="periodEnd")

    # Destination analytics
    top_destinations: list[DestinationCount] = Field(default_factory=list, alias="topDestinations")
    unique_countries: int = Field(default=0, alias="uniqueCountries")
    unique_cities: int = Field(default=0, alias="uniqueCities")

    # Budget analytics
    budget_ranges: list[BudgetRange] = Field(default_factory=list, alias="budgetRanges")
    avg_budget: float | None = Field(default=None, alias="avgBudget")
    total_planned_budget: float = Field(default=0, alias="totalPlannedBudget")

    # Duration analytics
    avg_trip_duration_days: float | None = Field(default=None, alias="avgTripDurationDays")
    shortest_trip_days: int | None = Field(default=None, alias="shortestTripDays")
    longest_trip_days: int | None = Field(default=None, alias="longestTripDays")

    # Seasonal preferences
    seasonal_distribution: list[SeasonalCount] = Field(
        default_factory=list, alias="seasonalDistribution"
    )

    # Purpose distribution
    purpose_distribution: list[PurposeCount] = Field(
        default_factory=list, alias="purposeDistribution"
    )


# Request/Response models
class UsageStatsRequest(BaseModel):
    """Request model for usage statistics"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    period: DateRange = DateRange.MONTH


class TripAnalyticsRequest(BaseModel):
    """Request model for trip analytics"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    period: DateRange = DateRange.YEAR
    limit_destinations: int = Field(default=10, ge=1, le=50, alias="limitDestinations")


class UsageStatsResponse(BaseModel):
    """Response model for usage statistics endpoint"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    success: bool = True
    data: UsageStats


class UsageTrendsResponse(BaseModel):
    """Response model for usage trends endpoint"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    success: bool = True
    period: DateRange
    data: list[UsageTrend]


class TripAnalyticsResponse(BaseModel):
    """Response model for trip analytics endpoint"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    success: bool = True
    data: TripAnalytics


class AgentUsageResponse(BaseModel):
    """Response model for agent usage statistics"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    success: bool = True
    period: DateRange
    data: list[AgentUsageStats]
    total_invocations: int = Field(..., alias="totalInvocations")
