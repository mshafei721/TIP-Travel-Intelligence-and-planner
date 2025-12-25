"""Pydantic models for trip management"""

from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from datetime import date, datetime
from enum import Enum


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
    nationality: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    residence_country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    origin_city: str = Field(..., min_length=1, max_length=100)
    party_size: int = Field(default=1, ge=1, le=20)
    party_ages: list[int] = Field(default_factory=list)

    @field_validator('nationality', 'residence_country')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate country code is uppercase"""
        if not v.isupper():
            raise ValueError("Country code must be uppercase (ISO 3166-1 alpha-2)")
        return v

    @field_validator('party_ages')
    @classmethod
    def validate_party_ages(cls, v: list[int], info) -> list[int]:
        """Validate party_ages matches party_size"""
        # Get party_size from the values being validated
        party_size = info.data.get('party_size', 1)

        if len(v) > party_size:
            raise ValueError(f"Number of party ages ({len(v)}) cannot exceed party size ({party_size})")

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
                "party_ages": [30, 28]
            }
        }


class Destination(BaseModel):
    """Destination information for multi-city trips"""
    country: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    duration_days: Optional[int] = Field(None, ge=1, le=365)

    class Config:
        json_schema_extra = {
            "example": {
                "country": "France",
                "city": "Paris",
                "duration_days": 5
            }
        }


class TripDetails(BaseModel):
    """Trip planning details"""
    departure_date: date
    return_date: date
    budget: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    trip_purpose: TripPurpose = TripPurpose.TOURISM

    @field_validator('return_date')
    @classmethod
    def validate_return_date(cls, v: date, info) -> date:
        """Validate return date is after departure date"""
        departure_date = info.data.get('departure_date')
        if departure_date and v <= departure_date:
            raise ValueError("Return date must be after departure date")
        return v

    @field_validator('currency')
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
                "trip_purpose": "tourism"
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
                "transportation_preference": "public"
            }
        }


class TripCreateRequest(BaseModel):
    """Request model for creating a new trip"""
    traveler_details: TravelerDetails
    destinations: list[Destination] = Field(..., min_length=1)
    trip_details: TripDetails
    preferences: TripPreferences
    template_id: Optional[str] = None

    @field_validator('destinations')
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
                    "party_ages": [30, 28]
                },
                "destinations": [
                    {
                        "country": "France",
                        "city": "Paris",
                        "duration_days": 7
                    }
                ],
                "trip_details": {
                    "departure_date": "2025-06-01",
                    "return_date": "2025-06-15",
                    "budget": 5000.00,
                    "currency": "USD",
                    "trip_purpose": "tourism"
                },
                "preferences": {
                    "travel_style": "balanced",
                    "interests": ["museums", "food"],
                    "dietary_restrictions": [],
                    "accessibility_needs": [],
                    "accommodation_type": "hotel",
                    "transportation_preference": "public"
                },
                "template_id": None
            }
        }


class TripUpdateRequest(BaseModel):
    """Request model for updating an existing trip (all fields optional)"""
    traveler_details: Optional[TravelerDetails] = None
    destinations: Optional[list[Destination]] = None
    trip_details: Optional[TripDetails] = None
    preferences: Optional[TripPreferences] = None

    @field_validator('destinations')
    @classmethod
    def validate_destinations(cls, v: Optional[list[Destination]]) -> Optional[list[Destination]]:
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
    template_id: Optional[str] = None
    auto_delete_at: Optional[datetime] = None

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
                    "party_ages": [30, 28]
                },
                "destinations": [
                    {
                        "country": "France",
                        "city": "Paris",
                        "duration_days": 7
                    }
                ],
                "trip_details": {
                    "departure_date": "2025-06-01",
                    "return_date": "2025-06-15",
                    "budget": 5000.00,
                    "currency": "USD",
                    "trip_purpose": "tourism"
                },
                "preferences": {
                    "travel_style": "balanced",
                    "interests": ["museums", "food"],
                    "dietary_restrictions": [],
                    "accessibility_needs": [],
                    "accommodation_type": "hotel",
                    "transportation_preference": "public"
                },
                "template_id": None,
                "auto_delete_at": "2025-07-15T00:00:00Z"
            }
        }


# Draft models
class DraftSaveRequest(BaseModel):
    """Request model for saving a draft (partial trip data)"""
    traveler_details: Optional[TravelerDetails] = None
    destinations: Optional[list[Destination]] = None
    trip_details: Optional[TripDetails] = None
    preferences: Optional[TripPreferences] = None


class DraftResponse(BaseModel):
    """Response model for draft data"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    draft_data: dict

    class Config:
        from_attributes = True
