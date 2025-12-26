"""
Itinerary data models for the Visual Itinerary Builder.

These models define the structure for user-editable itineraries,
distinct from the AI-generated itinerary reports.
"""

from datetime import date, datetime, time
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


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

    name: str = Field(..., description="Location/venue name")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    lng: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    neighborhood: Optional[str] = Field(None, description="Neighborhood/area")
    google_place_id: Optional[str] = Field(None, description="Google Places ID for linking")


# ============================================================================
# Activity Models
# ============================================================================


class ActivityBase(BaseModel):
    """Base model for activity data."""

    name: str = Field(..., min_length=1, max_length=200, description="Activity name")
    type: ActivityType = Field(default=ActivityType.ACTIVITY, description="Activity category")
    location: Location = Field(..., description="Activity location")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    duration_minutes: int = Field(..., ge=1, le=1440, description="Duration in minutes")
    cost_estimate: Optional[float] = Field(None, ge=0, description="Estimated cost")
    currency: str = Field(default="USD", description="Currency code")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    booking_url: Optional[str] = Field(None, description="Booking/reservation URL")
    booking_status: BookingStatus = Field(
        default=BookingStatus.NONE, description="Booking status"
    )
    booking_reference: Optional[str] = Field(None, description="Booking confirmation number")
    priority: ActivityPriority = Field(
        default=ActivityPriority.RECOMMENDED, description="Activity priority"
    )
    accessibility_notes: Optional[str] = Field(None, description="Accessibility information")
    transport_to_next: Optional[str] = Field(
        None, description="Transport method to next activity"
    )
    transport_duration_minutes: Optional[int] = Field(
        None, ge=0, description="Travel time to next activity"
    )


class Activity(ActivityBase):
    """Complete activity model with ID."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique activity ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Visit Tokyo Tower",
                "type": "attraction",
                "location": {
                    "name": "Tokyo Tower",
                    "address": "4-2-8 Shiba-koen, Minato-ku",
                    "city": "Tokyo",
                    "country": "Japan",
                    "lat": 35.6586,
                    "lng": 139.7454,
                },
                "start_time": "10:00",
                "end_time": "12:00",
                "duration_minutes": 120,
                "cost_estimate": 23.50,
                "currency": "USD",
                "priority": "must-see",
            }
        }


class ActivityCreate(ActivityBase):
    """Model for creating a new activity."""

    pass


class ActivityUpdate(BaseModel):
    """Model for updating an activity (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[ActivityType] = None
    location: Optional[Location] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    cost_estimate: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)
    booking_url: Optional[str] = None
    booking_status: Optional[BookingStatus] = None
    booking_reference: Optional[str] = None
    priority: Optional[ActivityPriority] = None
    accessibility_notes: Optional[str] = None
    transport_to_next: Optional[str] = None
    transport_duration_minutes: Optional[int] = Field(None, ge=0)


# ============================================================================
# Day Plan Models
# ============================================================================


class DayPlanBase(BaseModel):
    """Base model for a day plan."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    day_number: int = Field(..., ge=1, description="Day number in the trip")
    title: Optional[str] = Field(None, max_length=100, description="Day title/theme")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes for the day")


class DayPlan(DayPlanBase):
    """Complete day plan model with activities."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique day ID")
    activities: list[Activity] = Field(default_factory=list, description="Activities for the day")
    total_cost: float = Field(default=0.0, ge=0, description="Total cost for the day")

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

    date: Optional[str] = None
    day_number: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


# ============================================================================
# Itinerary Models
# ============================================================================


class ItineraryBase(BaseModel):
    """Base model for an itinerary."""

    pass


class Itinerary(ItineraryBase):
    """Complete itinerary model."""

    trip_id: str = Field(..., description="Associated trip ID")
    days: list[DayPlan] = Field(default_factory=list, description="Day plans")
    total_cost: float = Field(default=0.0, ge=0, description="Total trip cost")
    currency: str = Field(default="USD", description="Primary currency")
    last_modified: datetime = Field(
        default_factory=datetime.utcnow, description="Last modification time"
    )

    def calculate_total_cost(self) -> float:
        """Calculate total cost from all days."""
        return sum(day.calculate_total_cost() for day in self.days)


class ItineraryUpdate(BaseModel):
    """Model for updating the full itinerary."""

    days: list[DayPlan] = Field(..., description="Complete list of day plans")
    currency: Optional[str] = None


# ============================================================================
# Reorder Models
# ============================================================================


class ReorderItem(BaseModel):
    """Single item in a reorder operation."""

    activity_id: str = Field(..., description="Activity ID to move")
    target_day_id: str = Field(..., description="Target day ID")
    position: int = Field(..., ge=0, description="New position (0-indexed)")


class ReorderRequest(BaseModel):
    """Request to reorder activities."""

    operations: list[ReorderItem] = Field(..., description="List of reorder operations")


# ============================================================================
# Place Search Models
# ============================================================================


class PlaceSearchResult(BaseModel):
    """Result from a place search."""

    place_id: str = Field(..., description="Unique place identifier")
    name: str = Field(..., description="Place name")
    address: str = Field(..., description="Formatted address")
    city: Optional[str] = None
    country: Optional[str] = None
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    category: Optional[str] = Field(None, description="Place category")
    rating: Optional[float] = Field(None, ge=0, le=5)
    price_level: Optional[int] = Field(None, ge=0, le=4)
    photo_url: Optional[str] = None
    opening_hours: Optional[list[str]] = None


class PlaceSearchRequest(BaseModel):
    """Request for searching places."""

    query: str = Field(..., min_length=1, max_length=200, description="Search query")
    location: Optional[str] = Field(None, description="City/country to search in")
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Center latitude")
    lng: Optional[float] = Field(None, ge=-180, le=180, description="Center longitude")
    radius_km: float = Field(default=10, ge=1, le=50, description="Search radius in km")
    type: Optional[str] = Field(
        None, description="Place type filter (restaurant, attraction, etc.)"
    )
    limit: int = Field(default=20, ge=1, le=50, description="Maximum results")


class PlaceSearchResponse(BaseModel):
    """Response from place search."""

    results: list[PlaceSearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., ge=0, description="Total matching places")


# ============================================================================
# Response Models
# ============================================================================


class ItineraryResponse(BaseModel):
    """API response for itinerary retrieval."""

    trip_id: str
    itinerary: Itinerary
    has_ai_generated: bool = Field(
        False, description="Whether an AI-generated itinerary exists"
    )
    last_synced_at: Optional[datetime] = Field(
        None, description="Last sync with AI-generated itinerary"
    )


class DayPlanResponse(BaseModel):
    """API response for day plan operations."""

    success: bool
    day: DayPlan
    message: Optional[str] = None


class ActivityResponse(BaseModel):
    """API response for activity operations."""

    success: bool
    activity: Activity
    message: Optional[str] = None


class ReorderResponse(BaseModel):
    """API response for reorder operations."""

    success: bool
    updated_days: list[DayPlan]
    message: Optional[str] = None
