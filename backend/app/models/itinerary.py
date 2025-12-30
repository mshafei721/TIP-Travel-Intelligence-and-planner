"""
Itinerary data models for the Visual Itinerary Builder.

These models define the structure for user-editable itineraries,
distinct from the AI-generated itinerary reports.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ActivityType(str, Enum):
    """Types of activities in an itinerary."""

    ATTRACTION = "attraction"
    RESTAURANT = "restaurant"
    TRANSPORT = "transport"
    ACCOMMODATION = "accommodation"
    ACTIVITY = "activity"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    RELAXATION = "relaxation"
    PHOTOGRAPHY = "photography"
    CUSTOM = "custom"


class BookingStatus(str, Enum):
    """Booking status for an activity."""

    NONE = "none"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ActivityPriority(str, Enum):
    """Priority level for activities."""

    MUST_SEE = "must-see"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class Location(BaseModel):
    """Geographic location for an activity."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str = Field(..., description="Location/venue name")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    neighborhood: Optional[str] = Field(None, description="Neighborhood/area")
    google_place_id: Optional[str] = Field(
        None, description="Google Places ID for linking", alias="googlePlaceId"
    )


# ============================================================================
# Activity Models
# ============================================================================


class ActivityBase(BaseModel):
    """Base model for activity data."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str = Field(..., min_length=1, max_length=200, description="Activity name")
    type: ActivityType = Field(default=ActivityType.ACTIVITY, description="Activity category")
    location: Location = Field(..., description="Activity location")
    start_time: str = Field(..., description="Start time in HH:MM format", alias="startTime")
    end_time: str = Field(..., description="End time in HH:MM format", alias="endTime")
    duration_minutes: int = Field(
        ..., ge=1, le=1440, description="Duration in minutes", alias="durationMinutes"
    )
    cost_estimate: Optional[float] = Field(
        None, ge=0, description="Estimated cost", alias="costEstimate"
    )
    currency: str = Field(default="USD", description="Currency code")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    booking_url: Optional[str] = Field(
        None, description="Booking/reservation URL", alias="bookingUrl"
    )
    booking_status: BookingStatus = Field(
        default=BookingStatus.NONE, description="Booking status", alias="bookingStatus"
    )
    booking_reference: Optional[str] = Field(
        None, description="Booking confirmation number", alias="bookingReference"
    )
    priority: ActivityPriority = Field(
        default=ActivityPriority.RECOMMENDED, description="Activity priority"
    )
    accessibility_notes: Optional[str] = Field(
        None, description="Accessibility information", alias="accessibilityNotes"
    )
    transport_to_next: Optional[str] = Field(
        None, description="Transport method to next activity", alias="transportToNext"
    )
    transport_duration_minutes: Optional[int] = Field(
        None, ge=0, description="Travel time to next activity", alias="transportDurationMinutes"
    )


class Activity(ActivityBase):
    """Complete activity model with ID."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique activity ID")


class ActivityCreate(ActivityBase):
    """Model for creating a new activity."""

    pass


class ActivityUpdate(BaseModel):
    """Model for updating an activity (all fields optional)."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[ActivityType] = None
    location: Optional[Location] = None
    start_time: Optional[str] = Field(None, alias="startTime")
    end_time: Optional[str] = Field(None, alias="endTime")
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440, alias="durationMinutes")
    cost_estimate: Optional[float] = Field(None, ge=0, alias="costEstimate")
    currency: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)
    booking_url: Optional[str] = Field(None, alias="bookingUrl")
    booking_status: Optional[BookingStatus] = Field(None, alias="bookingStatus")
    booking_reference: Optional[str] = Field(None, alias="bookingReference")
    priority: Optional[ActivityPriority] = None
    accessibility_notes: Optional[str] = Field(None, alias="accessibilityNotes")
    transport_to_next: Optional[str] = Field(None, alias="transportToNext")
    transport_duration_minutes: Optional[int] = Field(None, ge=0, alias="transportDurationMinutes")


# ============================================================================
# Day Plan Models
# ============================================================================


class DayPlanBase(BaseModel):
    """Base model for a day plan."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    day_number: int = Field(..., ge=1, description="Day number in the trip", alias="dayNumber")
    title: Optional[str] = Field(None, max_length=100, description="Day title/theme")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes for the day")


class DayPlan(DayPlanBase):
    """Complete day plan model with activities."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique day ID")
    activities: list[Activity] = Field(default_factory=list, description="Activities for the day")
    total_cost: float = Field(default=0.0, ge=0, description="Total cost for the day", alias="totalCost")

    def calculate_total_cost(self) -> float:
        """Calculate total cost from activities."""
        return sum(a.cost_estimate or 0 for a in self.activities)


class DayPlanCreate(DayPlanBase):
    """Model for creating a new day plan."""

    activities: list[ActivityCreate] = Field(
        default_factory=list, description="Initial activities"
    )


class DayPlanUpdate(BaseModel):
    """Model for updating a day plan (all fields optional)."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    date: Optional[str] = None
    day_number: Optional[int] = Field(None, ge=1, alias="dayNumber")
    title: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


# ============================================================================
# Itinerary Models
# ============================================================================


class ItineraryBase(BaseModel):
    """Base model for an itinerary."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class Itinerary(ItineraryBase):
    """Complete itinerary model."""

    trip_id: str = Field(..., description="Associated trip ID", alias="tripId")
    days: list[DayPlan] = Field(default_factory=list, description="Day plans")
    total_cost: float = Field(default=0.0, ge=0, description="Total trip cost", alias="totalCost")
    currency: str = Field(default="USD", description="Primary currency")
    last_modified: datetime = Field(
        default_factory=datetime.utcnow, description="Last modification time", alias="lastModified"
    )

    def calculate_total_cost(self) -> float:
        """Calculate total cost from all days."""
        return sum(day.calculate_total_cost() for day in self.days)


class ItineraryUpdate(BaseModel):
    """Model for updating the full itinerary."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    days: list[DayPlan] = Field(..., description="Complete list of day plans")
    currency: Optional[str] = None


# ============================================================================
# Reorder Models
# ============================================================================


class ReorderItem(BaseModel):
    """Single item in a reorder operation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    activity_id: str = Field(..., description="Activity ID to move", alias="activityId")
    target_day_id: str = Field(..., description="Target day ID", alias="targetDayId")
    position: int = Field(..., ge=0, description="New position (0-indexed)")


class ReorderRequest(BaseModel):
    """Request to reorder activities."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    operations: list[ReorderItem] = Field(..., description="List of reorder operations")


# ============================================================================
# Place Search Models
# ============================================================================


class PlaceSearchResult(BaseModel):
    """Result from a place search."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    place_id: str = Field(..., description="Unique place identifier", alias="placeId")
    name: str = Field(..., description="Place name")
    address: str = Field(..., description="Formatted address")
    city: Optional[str] = None
    country: Optional[str] = None
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    category: Optional[str] = Field(None, description="Place category")
    rating: Optional[float] = Field(None, ge=0, le=5)
    price_level: Optional[int] = Field(None, ge=0, le=4, alias="priceLevel")
    photo_url: Optional[str] = Field(None, alias="photoUrl")
    opening_hours: Optional[list[str]] = Field(None, alias="openingHours")


class PlaceSearchRequest(BaseModel):
    """Request for searching places."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    location: Optional[str] = Field(None, description="City/country to search in")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Center latitude")
    lng: Optional[float] = Field(None, ge=-180, le=180, description="Center longitude")
    radius_km: float = Field(
        default=10, ge=1, le=50, description="Search radius in km", alias="radiusKm"
    )
    type: Optional[str] = Field(
        None, description="Place type filter (restaurant, attraction, etc.)"
    )
    limit: int = Field(default=20, ge=1, le=50, description="Maximum results")


class PlaceSearchResponse(BaseModel):
    """Response from place search."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    results: list[PlaceSearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., ge=0, description="Total matching places", alias="totalCount")


# ============================================================================
# Response Models
# ============================================================================


class ItineraryResponse(BaseModel):
    """API response for itinerary retrieval."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    itinerary: Itinerary
    has_ai_generated: bool = Field(
        False, description="Whether an AI-generated itinerary exists", alias="hasAiGenerated"
    )
    last_synced_at: Optional[datetime] = Field(
        None, description="Last sync with AI-generated itinerary", alias="lastSyncedAt"
    )


class DayPlanResponse(BaseModel):
    """API response for day plan operations."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    success: bool
    day: DayPlan
    message: Optional[str] = None


class ActivityResponse(BaseModel):
    """API response for activity operations."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    success: bool
    activity: Activity
    message: Optional[str] = None


class ReorderResponse(BaseModel):
    """API response for reorder operations."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    success: bool
    updated_days: list[DayPlan] = Field(..., alias="updatedDays")
    message: Optional[str] = None
