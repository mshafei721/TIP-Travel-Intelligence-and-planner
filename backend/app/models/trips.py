"""Pydantic models for trip management"""

from datetime import date, datetime
from enum import Enum

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


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
    TRANSIT = "transit"
    WORK = "work"
    STUDY = "study"
    MEDICAL = "medical"
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

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    nationality: str = Field(
        ..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code"
    )
    residence_country: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code",
        validation_alias=AliasChoices("residencyCountry", "residenceCountry", "residence_country"),
        serialization_alias="residencyCountry",
    )
    origin_city: str = Field(..., min_length=1, max_length=100, alias="originCity")
    party_size: int = Field(default=1, ge=1, le=20, alias="partySize")
    party_ages: list[int] = Field(
        default_factory=list,
        validation_alias=AliasChoices("companionAges", "partyAges", "party_ages"),
        serialization_alias="companionAges",
    )

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


class Destination(BaseModel):
    """Destination information for multi-city trips"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    country: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    duration_days: int | None = Field(None, ge=1, le=365, alias="durationDays")


class TripDetails(BaseModel):
    """Trip planning details"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    departure_date: date = Field(..., alias="departureDate")
    return_date: date = Field(..., alias="returnDate")
    budget: float = Field(..., gt=0)
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        validation_alias=AliasChoices("budgetCurrency", "currency"),
        serialization_alias="budgetCurrency",
    )
    # Support both single trip_purpose and array tripPurposes
    trip_purposes: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("tripPurposes", "trip_purposes"),
        serialization_alias="tripPurposes",
    )

    @model_validator(mode="before")
    @classmethod
    def handle_legacy_trip_purpose(cls, data: dict) -> dict:
        """Convert legacy trip_purpose (single string) to trip_purposes (array)"""
        if isinstance(data, dict):
            # Check for legacy single trip_purpose field
            legacy_purpose = data.get("trip_purpose") or data.get("tripPurpose")
            has_purposes = data.get("trip_purposes") or data.get("tripPurposes")

            if legacy_purpose and not has_purposes:
                # Convert single purpose to array
                data["tripPurposes"] = (
                    [legacy_purpose] if isinstance(legacy_purpose, str) else legacy_purpose
                )
        return data

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

    @field_validator("trip_purposes")
    @classmethod
    def validate_trip_purposes(cls, v: list[str]) -> list[str]:
        """Normalize trip purposes to lowercase with underscores"""
        normalized = []
        for purpose in v:
            # Convert "Family Visit" -> "family_visit", etc.
            normalized_purpose = purpose.lower().replace(" ", "_")
            normalized.append(normalized_purpose)
        return normalized


class TripPreferences(BaseModel):
    """Trip preferences and special requirements"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    travel_style: TravelStyle = Field(default=TravelStyle.BALANCED, alias="travelStyle")
    interests: list[str] = Field(default_factory=list)
    dietary_restrictions: list[str] = Field(default_factory=list, alias="dietaryRestrictions")
    accessibility_needs: list[str] = Field(default_factory=list, alias="accessibilityNeeds")
    accommodation_type: AccommodationType = Field(
        default=AccommodationType.HOTEL, alias="accommodationType"
    )
    transportation_preference: TransportationPreference = Field(
        default=TransportationPreference.ANY, alias="transportationPreference"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_preferences(cls, data: dict) -> dict:
        """Normalize frontend values to backend enum values"""
        if isinstance(data, dict):
            # Map frontend travel style values to backend enum
            # Frontend: 'Relaxed', 'Balanced', 'Packed', 'Budget-Focused'
            # Backend: 'budget', 'balanced', 'luxury'
            travel_style_map = {
                "relaxed": "balanced",
                "balanced": "balanced",
                "packed": "luxury",  # Packed = more activities = premium
                "budget-focused": "budget",
                "budget": "budget",
                "luxury": "luxury",
            }
            style = data.get("travelStyle") or data.get("travel_style")
            if style:
                normalized_style = travel_style_map.get(style.lower(), "balanced")
                data["travelStyle"] = normalized_style

            # Handle accessibilityNeeds - convert string to list
            # Check both possible keys explicitly since empty string is falsy
            needs = None
            if "accessibilityNeeds" in data:
                needs = data["accessibilityNeeds"]
            elif "accessibility_needs" in data:
                needs = data["accessibility_needs"]

            if isinstance(needs, str):
                if needs.strip():
                    data["accessibilityNeeds"] = [needs]
                else:
                    data["accessibilityNeeds"] = []
        return data


class TripCreateRequest(BaseModel):
    """Request model for creating a new trip"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    traveler_details: TravelerDetails = Field(..., alias="travelerDetails")
    destinations: list[Destination] = Field(..., min_length=1)
    trip_details: TripDetails = Field(..., alias="tripDetails")
    preferences: TripPreferences
    template_id: str | None = Field(default=None, alias="templateId")
    cover_image_url: str | None = Field(
        default=None,
        description="URL to the trip cover image in Supabase Storage",
        alias="coverImageUrl",
    )

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v: list[Destination]) -> list[Destination]:
        """Validate at least one destination is provided"""
        if len(v) == 0:
            raise ValueError("At least one destination is required")
        return v


class TripUpdateRequest(BaseModel):
    """Request model for updating an existing trip (all fields optional)"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    traveler_details: TravelerDetails | None = Field(default=None, alias="travelerDetails")
    destinations: list[Destination] | None = None
    trip_details: TripDetails | None = Field(default=None, alias="tripDetails")
    preferences: TripPreferences | None = None
    cover_image_url: str | None = Field(default=None, alias="coverImageUrl")

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v: list[Destination] | None) -> list[Destination] | None:
        """Validate at least one destination if provided"""
        if v is not None and len(v) == 0:
            raise ValueError("At least one destination is required")
        return v


class TripResponse(BaseModel):
    """Response model for trip data"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    id: str
    user_id: str = Field(..., alias="userId")
    title: str
    status: TripStatus
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    traveler_details: TravelerDetails = Field(..., alias="travelerDetails")
    destinations: list[Destination]
    trip_details: TripDetails = Field(..., alias="tripDetails")
    preferences: TripPreferences
    template_id: str | None = Field(default=None, alias="templateId")
    auto_delete_at: datetime | None = Field(default=None, alias="autoDeleteAt")
    deleted_at: datetime | None = Field(default=None, alias="deletedAt")
    is_archived: bool = Field(default=False, alias="isArchived")
    archived_at: datetime | None = Field(default=None, alias="archivedAt")
    user_rating: int | None = Field(default=None, alias="userRating")
    user_notes: str | None = Field(default=None, alias="userNotes")
    version: int = 1
    cover_image_url: str | None = Field(default=None, alias="coverImageUrl")


# Draft models
class DraftSaveRequest(BaseModel):
    """Request model for saving a draft (partial trip data)"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    traveler_details: TravelerDetails | None = Field(default=None, alias="travelerDetails")
    destinations: list[Destination] | None = None
    trip_details: TripDetails | None = Field(default=None, alias="tripDetails")
    preferences: TripPreferences | None = None


class DraftResponse(BaseModel):
    """Response model for draft data"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    id: str
    user_id: str = Field(..., alias="userId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    draft_data: dict = Field(..., alias="draftData")


# ============================================================================
# TRIP UPDATES AND RECALCULATION MODELS
# ============================================================================


class ChangePreviewRequest(BaseModel):
    """Request model for previewing changes before applying."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    traveler_details: TravelerDetails | None = Field(default=None, alias="travelerDetails")
    destinations: list[Destination] | None = None
    trip_details: TripDetails | None = Field(default=None, alias="tripDetails")
    preferences: TripPreferences | None = None


class FieldChange(BaseModel):
    """Represents a single field change."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    field: str
    old_value: str | int | float | list | dict | None = Field(..., alias="oldValue")
    new_value: str | int | float | list | dict | None = Field(..., alias="newValue")


class ChangePreviewResponse(BaseModel):
    """Response model for change preview."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    has_changes: bool = Field(..., alias="hasChanges")
    changes: list[FieldChange]
    affected_agents: list[str] = Field(..., alias="affectedAgents")
    estimated_recalc_time: int = Field(..., alias="estimatedRecalcTime")  # seconds
    requires_recalculation: bool = Field(..., alias="requiresRecalculation")


class RecalculationRequest(BaseModel):
    """Request model for manual recalculation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

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

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    task_id: str = Field(..., alias="taskId")
    status: RecalculationStatusEnum
    affected_agents: list[str] = Field(..., alias="affectedAgents")
    estimated_time: int = Field(..., alias="estimatedTime")  # seconds
    message: str


class RecalculationStatusResponse(BaseModel):
    """Response model for recalculation status check."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    task_id: str = Field(..., alias="taskId")
    status: RecalculationStatusEnum
    progress: float = 0.0  # 0-100 percentage
    completed_agents: list[str] = Field(default_factory=list, alias="completedAgents")
    pending_agents: list[str] = Field(default_factory=list, alias="pendingAgents")
    current_agent: str | None = Field(default=None, alias="currentAgent")
    started_at: datetime | None = Field(default=None, alias="startedAt")
    estimated_completion: datetime | None = Field(default=None, alias="estimatedCompletion")
    error: str | None = None


class RecalculationCancelResponse(BaseModel):
    """Response model for recalculation cancellation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    task_id: str = Field(..., alias="taskId")
    cancelled: bool
    message: str
    completed_agents: list[str] = Field(
        default_factory=list, alias="completedAgents"
    )  # Agents that completed before cancellation


class VersionCompareResponse(BaseModel):
    """Response model for version comparison."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    version_a: int = Field(..., alias="versionA")
    version_b: int = Field(..., alias="versionB")
    changes: list[FieldChange]
    summary: str


class TripUpdateWithRecalcRequest(BaseModel):
    """Request model for updating trip with recalculation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    traveler_details: TravelerDetails | None = Field(default=None, alias="travelerDetails")
    destinations: list[Destination] | None = None
    trip_details: TripDetails | None = Field(default=None, alias="tripDetails")
    preferences: TripPreferences | None = None
    auto_recalculate: bool = Field(
        default=True, alias="autoRecalculate"
    )  # Whether to automatically trigger recalculation


class TripUpdateWithRecalcResponse(BaseModel):
    """Response model for trip update with recalculation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip: TripResponse
    recalculation: RecalculationResponse | None = None
    changes_applied: list[FieldChange] = Field(..., alias="changesApplied")


# ============================================================================
# VERSION HISTORY MODELS
# ============================================================================


class TripVersionSummary(BaseModel):
    """Summary of a trip version."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    version_number: int = Field(..., alias="versionNumber")
    created_at: datetime = Field(..., alias="createdAt")
    change_summary: str = Field(..., alias="changeSummary")
    fields_changed: list[str] = Field(..., alias="fieldsChanged")


class TripVersionDetail(BaseModel):
    """Detailed trip version data."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    version_number: int = Field(..., alias="versionNumber")
    created_at: datetime = Field(..., alias="createdAt")
    trip_data: dict = Field(..., alias="tripData")
    change_summary: str = Field(..., alias="changeSummary")
    fields_changed: list[str] = Field(..., alias="fieldsChanged")


class TripVersionListResponse(BaseModel):
    """Response model for listing trip versions."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    current_version: int = Field(..., alias="currentVersion")
    versions: list[TripVersionSummary]


class TripVersionRestoreResponse(BaseModel):
    """Response model for version restore."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    restored_version: int = Field(..., alias="restoredVersion")
    new_version: int = Field(..., alias="newVersion")
    recalculation: RecalculationResponse | None = None


# ============================================================================
# TRAVEL HISTORY MODELS
# ============================================================================


class ArchiveResponse(BaseModel):
    """Response model for archive/unarchive operations."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    is_archived: bool = Field(..., alias="isArchived")
    archived_at: datetime | None = Field(default=None, alias="archivedAt")
    message: str


class TravelHistoryEntry(BaseModel):
    """Single entry in travel history."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    destination: str
    country: str
    start_date: str = Field(..., alias="startDate")
    end_date: str = Field(..., alias="endDate")
    status: str  # completed, cancelled
    user_rating: int | None = Field(default=None, alias="userRating")  # 1-5
    user_notes: str | None = Field(default=None, alias="userNotes")
    is_archived: bool = Field(default=False, alias="isArchived")
    archived_at: datetime | None = Field(default=None, alias="archivedAt")
    cover_image: str | None = Field(default=None, alias="coverImage")


class TravelStats(BaseModel):
    """Aggregated travel statistics."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    total_trips: int = Field(..., alias="totalTrips")
    countries_visited: int = Field(..., alias="countriesVisited")
    cities_visited: int = Field(..., alias="citiesVisited")
    total_days_traveled: int = Field(..., alias="totalDaysTraveled")
    favorite_destination: str | None = Field(default=None, alias="favoriteDestination")
    most_visited_country: str | None = Field(default=None, alias="mostVisitedCountry")
    travel_streak: int = Field(default=0, alias="travelStreak")  # Consecutive months with travel


class CountryVisit(BaseModel):
    """Country visit information for the world map."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    country_code: str = Field(..., alias="countryCode")
    country_name: str = Field(..., alias="countryName")
    visit_count: int = Field(..., alias="visitCount")
    last_visited: str | None = Field(default=None, alias="lastVisited")
    cities: list[str] = Field(default_factory=list)


class TravelHistoryResponse(BaseModel):
    """Response model for travel history endpoint."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    entries: list[TravelHistoryEntry]
    total_count: int = Field(..., alias="totalCount")


class TravelStatsResponse(BaseModel):
    """Response model for travel statistics endpoint."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    stats: TravelStats
    countries: list[CountryVisit]


class TravelTimelineEntry(BaseModel):
    """Entry for timeline visualization."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    title: str
    destination: str
    start_date: str = Field(..., alias="startDate")
    end_date: str = Field(..., alias="endDate")
    duration_days: int = Field(..., alias="durationDays")
    status: str
    thumbnail: str | None = None


class TravelTimelineResponse(BaseModel):
    """Response model for travel timeline."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    entries: list[TravelTimelineEntry]
    years: list[int]  # Years with travel for filtering


class TripRatingRequest(BaseModel):
    """Request to rate a completed trip."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    notes: str | None = Field(None, max_length=1000, description="Optional notes about the trip")


# ============================================================================
# AGENT JOB MODELS
# ============================================================================


class AgentType(str, Enum):
    """Agent type enumeration matching OpenAPI spec"""

    VISA = "visa"
    COUNTRY = "country"
    WEATHER = "weather"
    CURRENCY = "currency"
    CULTURE = "culture"
    FOOD = "food"
    ATTRACTIONS = "attractions"
    ITINERARY = "itinerary"
    FLIGHT = "flight"


class AgentJobStatus(str, Enum):
    """Agent job status enumeration matching OpenAPI spec"""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class AgentJobResponse(BaseModel):
    """Response model for a single agent job"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    trip_id: str = Field(..., alias="tripId")
    agent_type: AgentType = Field(..., alias="agentType")
    status: AgentJobStatus
    started_at: datetime | None = Field(default=None, alias="startedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    retry_count: int = Field(default=0, alias="retryCount")
    error_message: str | None = Field(default=None, alias="errorMessage")


class AgentJobListResponse(BaseModel):
    """Response model for list of agent jobs"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    items: list[AgentJobResponse]
