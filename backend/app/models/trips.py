"""Pydantic models for trip management"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator


class TripStatus(str, Enum):
    """Trip status enumeration"""

    DRAFT = "draft"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TripPurpose(str, Enum):
    """Trip purpose enumeration"""

    TOURISM = "tourism"
    BUSINESS = "business"
    ADVENTURE = "adventure"
    EDUCATION = "education"
    FAMILY_VISIT = "family_visit"
    OTHER = "other"


class TravelStyle(str, Enum):
    """Travel style preferences"""

    BUDGET = "budget"
    BALANCED = "balanced"
    LUXURY = "luxury"


class AccommodationType(str, Enum):
    """Accommodation type preferences"""

    HOTEL = "hotel"
    HOSTEL = "hostel"
    AIRBNB = "airbnb"
    RESORT = "resort"
    CAMPING = "camping"
    MIXED = "mixed"


class TransportationPreference(str, Enum):
    """Transportation preference"""

    PUBLIC = "public"
    RENTAL_CAR = "rental_car"
    TAXI_RIDESHARE = "taxi_rideshare"
    WALKING = "walking"
    ANY = "any"


class TravelerDetails(BaseModel):
    """Traveler information for trip creation"""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    nationality: str = Field(
        ..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"
    )
    residence_country: str = Field(
        ..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"
    )
    origin_city: str = Field(..., min_length=1, max_length=100)
    party_size: int = Field(default=1, ge=1, le=20)
    party_ages: list[int] = Field(default_factory=list)

    @field_validator("nationality", "residence_country")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate country code is uppercase"""
        if not v.isupper():
            raise ValueError("Country code must be uppercase (ISO 3166-1 alpha-2)")
        return v

    @field_validator("party_ages")
    @classmethod
    def validate_party_ages(cls, v: list[int], info) -> list[int]:
        """Validate party_ages matches party_size"""
        # Get party_size from the values being validated
        party_size = info.data.get("party_size", 1)

        if len(v) > party_size:
            raise ValueError(
                f"Number of party ages ({len(v)}) cannot exceed party size ({party_size})"
            )

        # Validate all ages are reasonable
        for age in v:
            if age < 0 or age > 120:
                raise ValueError(f"Age {age} is not valid (must be 0-120)")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "nationality": "US",
                "residence_country": "US",
                "origin_city": "New York",
                "party_size": 2,
                "party_ages": [30, 28],
            }
        }


class Destination(BaseModel):
    """Destination information for multi-city trips"""

    country: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    duration_days: int | None = Field(None, ge=1, le=365)

    class Config:
        json_schema_extra = {"example": {"country": "France", "city": "Paris", "duration_days": 5}}


class TripDetails(BaseModel):
    """Trip planning details"""

    departure_date: date
    return_date: date
    budget: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    trip_purpose: TripPurpose = TripPurpose.TOURISM

    @field_validator("return_date")
    @classmethod
    def validate_return_date(cls, v: date, info) -> date:
        """Validate return date is after departure date"""
        departure_date = info.data.get("departure_date")
        if departure_date and v <= departure_date:
            raise ValueError("Return date must be after departure date")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code is uppercase"""
        if not v.isupper():
            raise ValueError("Currency code must be uppercase (ISO 4217)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "departure_date": "2025-06-01",
                "return_date": "2025-06-15",
                "budget": 5000.00,
                "currency": "USD",
                "trip_purpose": "tourism",
            }
        }


class TripPreferences(BaseModel):
    """Trip preferences and special requirements"""

    travel_style: TravelStyle = TravelStyle.BALANCED
    interests: list[str] = Field(default_factory=list)
    dietary_restrictions: list[str] = Field(default_factory=list)
    accessibility_needs: list[str] = Field(default_factory=list)
    accommodation_type: AccommodationType = AccommodationType.HOTEL
    transportation_preference: TransportationPreference = TransportationPreference.ANY

    class Config:
        json_schema_extra = {
            "example": {
                "travel_style": "balanced",
                "interests": ["museums", "food", "nature"],
                "dietary_restrictions": ["vegetarian"],
                "accessibility_needs": [],
                "accommodation_type": "hotel",
                "transportation_preference": "public",
            }
        }


class TripCreateRequest(BaseModel):
    """Request model for creating a new trip"""

    traveler_details: TravelerDetails
    destinations: list[Destination] = Field(..., min_length=1)
    trip_details: TripDetails
    preferences: TripPreferences
    template_id: str | None = None
    cover_image_url: str | None = Field(
        default=None,
        description="URL to the trip cover image in Supabase Storage",
    )

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v: list[Destination]) -> list[Destination]:
        """Validate at least one destination is provided"""
        if len(v) == 0:
            raise ValueError("At least one destination is required")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "traveler_details": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "nationality": "US",
                    "residence_country": "US",
                    "origin_city": "New York",
                    "party_size": 2,
                    "party_ages": [30, 28],
                },
                "destinations": [{"country": "France", "city": "Paris", "duration_days": 7}],
                "trip_details": {
                    "departure_date": "2025-06-01",
                    "return_date": "2025-06-15",
                    "budget": 5000.00,
                    "currency": "USD",
                    "trip_purpose": "tourism",
                },
                "preferences": {
                    "travel_style": "balanced",
                    "interests": ["museums", "food"],
                    "dietary_restrictions": [],
                    "accessibility_needs": [],
                    "accommodation_type": "hotel",
                    "transportation_preference": "public",
                },
                "template_id": None,
            }
        }


class TripUpdateRequest(BaseModel):
    """Request model for updating an existing trip (all fields optional)"""

    traveler_details: TravelerDetails | None = None
    destinations: list[Destination] | None = None
    trip_details: TripDetails | None = None
    preferences: TripPreferences | None = None
    cover_image_url: str | None = None

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v: list[Destination] | None) -> list[Destination] | None:
        """Validate at least one destination if provided"""
        if v is not None and len(v) == 0:
            raise ValueError("At least one destination is required")
        return v


class TripResponse(BaseModel):
    """Response model for trip data"""

    id: str
    user_id: str
    status: TripStatus
    created_at: datetime
    updated_at: datetime
    traveler_details: TravelerDetails
    destinations: list[Destination]
    trip_details: TripDetails
    preferences: TripPreferences
    template_id: str | None = None
    auto_delete_at: datetime | None = None
    cover_image_url: str | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "draft",
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z",
                "traveler_details": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "nationality": "US",
                    "residence_country": "US",
                    "origin_city": "New York",
                    "party_size": 2,
                    "party_ages": [30, 28],
                },
                "destinations": [{"country": "France", "city": "Paris", "duration_days": 7}],
                "trip_details": {
                    "departure_date": "2025-06-01",
                    "return_date": "2025-06-15",
                    "budget": 5000.00,
                    "currency": "USD",
                    "trip_purpose": "tourism",
                },
                "preferences": {
                    "travel_style": "balanced",
                    "interests": ["museums", "food"],
                    "dietary_restrictions": [],
                    "accessibility_needs": [],
                    "accommodation_type": "hotel",
                    "transportation_preference": "public",
                },
                "template_id": None,
                "auto_delete_at": "2025-07-15T00:00:00Z",
            }
        }


# Draft models
class DraftSaveRequest(BaseModel):
    """Request model for saving a draft (partial trip data)"""

    traveler_details: TravelerDetails | None = None
    destinations: list[Destination] | None = None
    trip_details: TripDetails | None = None
    preferences: TripPreferences | None = None


class DraftResponse(BaseModel):
    """Response model for draft data"""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    draft_data: dict

    class Config:
        from_attributes = True


# ============================================================================
# TRIP UPDATES AND RECALCULATION MODELS
# ============================================================================


class ChangePreviewRequest(BaseModel):
    """Request model for previewing changes before applying."""

    traveler_details: TravelerDetails | None = None
    destinations: list[Destination] | None = None
    trip_details: TripDetails | None = None
    preferences: TripPreferences | None = None


class FieldChange(BaseModel):
    """Represents a single field change."""

    field: str
    old_value: str | int | float | list | dict | None
    new_value: str | int | float | list | dict | None


class ChangePreviewResponse(BaseModel):
    """Response model for change preview."""

    has_changes: bool
    changes: list[FieldChange]
    affected_agents: list[str]
    estimated_recalc_time: int  # seconds
    requires_recalculation: bool

    class Config:
        json_schema_extra = {
            "example": {
                "has_changes": True,
                "changes": [
                    {"field": "destination", "old_value": "France", "new_value": "Japan"},
                    {"field": "budget", "old_value": 5000, "new_value": 10000},
                ],
                "affected_agents": ["visa", "weather", "currency", "attractions", "itinerary"],
                "estimated_recalc_time": 75,
                "requires_recalculation": True,
            }
        }


class RecalculationRequest(BaseModel):
    """Request model for manual recalculation."""

    agents: list[str] | None = None  # If None, recalculate all affected agents
    force: bool = False  # Force recalculation even if no changes detected


class RecalculationStatusEnum(str, Enum):
    """Recalculation status enumeration."""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RecalculationResponse(BaseModel):
    """Response model for recalculation request."""

    task_id: str
    status: RecalculationStatusEnum
    affected_agents: list[str]
    estimated_time: int  # seconds
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123",
                "status": "queued",
                "affected_agents": ["visa", "weather", "currency"],
                "estimated_time": 45,
                "message": "Recalculation queued for 3 agents",
            }
        }


class RecalculationStatusResponse(BaseModel):
    """Response model for recalculation status check."""

    task_id: str
    status: RecalculationStatusEnum
    progress: float = 0.0  # 0-100 percentage
    completed_agents: list[str] = []
    pending_agents: list[str] = []
    current_agent: str | None = None
    started_at: datetime | None = None
    estimated_completion: datetime | None = None
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123",
                "status": "in_progress",
                "progress": 45.0,
                "completed_agents": ["visa", "weather"],
                "pending_agents": ["currency", "attractions"],
                "current_agent": "currency",
                "started_at": "2024-01-15T10:30:00Z",
                "estimated_completion": "2024-01-15T10:32:00Z",
                "error": None,
            }
        }


class RecalculationCancelResponse(BaseModel):
    """Response model for recalculation cancellation."""

    task_id: str
    cancelled: bool
    message: str
    completed_agents: list[str] = []  # Agents that completed before cancellation

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123",
                "cancelled": True,
                "message": "Recalculation cancelled successfully",
                "completed_agents": ["visa", "weather"],
            }
        }


class VersionCompareResponse(BaseModel):
    """Response model for version comparison."""

    trip_id: str
    version_a: int
    version_b: int
    changes: list[FieldChange]
    summary: str

    class Config:
        json_schema_extra = {
            "example": {
                "trip_id": "abc123",
                "version_a": 1,
                "version_b": 3,
                "changes": [
                    {"field": "destination", "old_value": "France", "new_value": "Japan"},
                    {"field": "budget", "old_value": 5000, "new_value": 8000},
                ],
                "summary": "2 fields changed between version 1 and version 3",
            }
        }


class TripUpdateWithRecalcRequest(BaseModel):
    """Request model for updating trip with recalculation."""

    traveler_details: TravelerDetails | None = None
    destinations: list[Destination] | None = None
    trip_details: TripDetails | None = None
    preferences: TripPreferences | None = None
    auto_recalculate: bool = True  # Whether to automatically trigger recalculation


class TripUpdateWithRecalcResponse(BaseModel):
    """Response model for trip update with recalculation."""

    trip: TripResponse
    recalculation: RecalculationResponse | None = None
    changes_applied: list[FieldChange]


# ============================================================================
# VERSION HISTORY MODELS
# ============================================================================


class TripVersionSummary(BaseModel):
    """Summary of a trip version."""

    version_number: int
    created_at: datetime
    change_summary: str
    fields_changed: list[str]


class TripVersionDetail(BaseModel):
    """Detailed trip version data."""

    version_number: int
    created_at: datetime
    trip_data: dict
    change_summary: str
    fields_changed: list[str]


class TripVersionListResponse(BaseModel):
    """Response model for listing trip versions."""

    trip_id: str
    current_version: int
    versions: list[TripVersionSummary]


class TripVersionRestoreResponse(BaseModel):
    """Response model for version restore."""

    trip_id: str
    restored_version: int
    new_version: int
    recalculation: RecalculationResponse | None = None


# ============================================================================
# TRAVEL HISTORY MODELS
# ============================================================================


class ArchiveResponse(BaseModel):
    """Response model for archive/unarchive operations."""

    trip_id: str
    is_archived: bool
    archived_at: datetime | None = None
    message: str


class TravelHistoryEntry(BaseModel):
    """Single entry in travel history."""

    trip_id: str
    destination: str
    country: str
    start_date: str
    end_date: str
    status: str  # completed, cancelled
    user_rating: int | None = None  # 1-5
    user_notes: str | None = None
    is_archived: bool = False
    archived_at: datetime | None = None
    cover_image: str | None = None


class TravelStats(BaseModel):
    """Aggregated travel statistics."""

    total_trips: int
    countries_visited: int
    cities_visited: int
    total_days_traveled: int
    favorite_destination: str | None = None
    most_visited_country: str | None = None
    travel_streak: int = 0  # Consecutive months with travel


class CountryVisit(BaseModel):
    """Country visit information for the world map."""

    country_code: str
    country_name: str
    visit_count: int
    last_visited: str | None = None
    cities: list[str] = []


class TravelHistoryResponse(BaseModel):
    """Response model for travel history endpoint."""

    entries: list[TravelHistoryEntry]
    total_count: int


class TravelStatsResponse(BaseModel):
    """Response model for travel statistics endpoint."""

    stats: TravelStats
    countries: list[CountryVisit]


class TravelTimelineEntry(BaseModel):
    """Entry for timeline visualization."""

    trip_id: str
    title: str
    destination: str
    start_date: str
    end_date: str
    duration_days: int
    status: str
    thumbnail: str | None = None


class TravelTimelineResponse(BaseModel):
    """Response model for travel timeline."""

    entries: list[TravelTimelineEntry]
    years: list[int]  # Years with travel for filtering


class TripRatingRequest(BaseModel):
    """Request to rate a completed trip."""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    notes: str | None = Field(None, max_length=1000, description="Optional notes about the trip")
