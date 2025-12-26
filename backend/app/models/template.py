"""Pydantic models for trip template management"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TemplateDestination(BaseModel):
    """Destination within a template"""

    country: str = Field(..., description="Country name")
    city: str | None = Field(None, description="City name")
    suggested_days: int | None = Field(None, ge=1, description="Suggested days to spend")
    highlights: list[str] = Field(default_factory=list, description="Key highlights")


class TripTemplateCreate(BaseModel):
    """Model for creating a trip template"""

    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str | None = Field(None, max_length=500, description="Template description")
    cover_image: str | None = Field(None, description="Cover image URL")
    is_public: bool = Field(False, description="Make template publicly visible")
    tags: list[str] = Field(default_factory=list, description="Template tags for filtering")
    traveler_details: dict | None = Field(
        None, description="Default traveler details (nationality, residency, etc.)"
    )
    destinations: list[dict] = Field(
        default_factory=list,
        description="List of destination objects with country and city",
    )
    preferences: dict | None = Field(
        None, description="Travel preferences (style, dietary restrictions, etc.)"
    )
    typical_duration: int | None = Field(None, ge=1, description="Typical trip duration in days")
    estimated_budget: float | None = Field(None, ge=0, description="Estimated budget")
    currency: str = Field("USD", max_length=3, description="Currency code")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Template name cannot be empty")
        return v.strip()

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v: list[dict]) -> list[dict]:
        if not v:
            raise ValueError("At least one destination is required")

        for dest in v:
            if not isinstance(dest, dict):
                raise ValueError("Each destination must be an object")
            if "country" not in dest:
                raise ValueError("Each destination must have a 'country' field")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Weekend Getaway",
                "description": "Quick 3-day city break template",
                "destinations": [{"country": "France", "city": "Paris"}],
                "traveler_details": {
                    "nationality": "US",
                    "residency_country": "US",
                    "residency_status": "citizen",
                },
                "preferences": {
                    "travel_style": "balanced",
                    "dietary_restrictions": ["vegetarian"],
                    "budget": "moderate",
                },
            }
        }


class TripTemplateUpdate(BaseModel):
    """Model for updating a trip template (all fields optional)"""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    cover_image: str | None = None
    is_public: bool | None = None
    tags: list[str] | None = None
    traveler_details: dict | None = None
    destinations: list[dict] | None = None
    preferences: dict | None = None
    typical_duration: int | None = None
    estimated_budget: float | None = None
    currency: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            raise ValueError("Template name cannot be empty")
        return v.strip() if v else None

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v: list[dict] | None) -> list[dict] | None:
        if v is not None:
            if not v:
                raise ValueError("At least one destination is required")

            for dest in v:
                if not isinstance(dest, dict):
                    raise ValueError("Each destination must be an object")
                if "country" not in dest:
                    raise ValueError("Each destination must have a 'country' field")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Weekend Getaway",
                "destinations": [
                    {"country": "France", "city": "Paris"},
                    {"country": "France", "city": "Lyon"},
                ],
            }
        }


class TripTemplateResponse(BaseModel):
    """Response model for trip template"""

    id: str
    user_id: str
    name: str
    description: str | None
    cover_image: str | None = None
    is_public: bool = False
    tags: list[str] = []
    traveler_details: dict | None
    destinations: list[dict]
    preferences: dict | None
    typical_duration: int | None = None
    estimated_budget: float | None = None
    currency: str = "USD"
    use_count: int = 0
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e4567-e89b-12d3-a456-426614174000",
                "name": "Weekend Getaway",
                "description": "Quick 3-day city break template",
                "cover_image": "https://example.com/paris.jpg",
                "is_public": False,
                "tags": ["weekend", "city-break", "europe"],
                "destinations": [
                    {"country": "France", "city": "Paris", "suggested_days": 3}
                ],
                "traveler_details": {"nationality": "US", "residency_country": "US"},
                "preferences": {
                    "travel_style": "balanced",
                    "dietary_restrictions": ["vegetarian"],
                },
                "typical_duration": 3,
                "estimated_budget": 1500.00,
                "currency": "USD",
                "use_count": 0,
                "created_at": "2025-12-25T10:00:00Z",
                "updated_at": "2025-12-25T10:00:00Z",
            }
        }


class PublicTemplateResponse(BaseModel):
    """Response model for public template (excludes user_id for privacy)"""

    id: str
    name: str
    description: str | None
    cover_image: str | None = None
    tags: list[str] = []
    destinations: list[dict]
    typical_duration: int | None = None
    estimated_budget: float | None = None
    currency: str = "USD"
    use_count: int = 0
    created_at: str

    class Config:
        from_attributes = True


class CreateTripFromTemplateRequest(BaseModel):
    """Request to create a trip from a template"""

    title: str | None = Field(None, description="Custom trip title (optional)")
    start_date: str | None = Field(None, description="Trip start date (ISO format)")
    end_date: str | None = Field(None, description="Trip end date (ISO format)")
    override_traveler_details: dict | None = Field(
        None, description="Override template traveler details"
    )
    override_preferences: dict | None = Field(
        None, description="Override template preferences"
    )
