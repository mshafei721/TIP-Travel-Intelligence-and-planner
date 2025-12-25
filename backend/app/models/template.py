"""Pydantic models for trip template management"""

from pydantic import BaseModel, Field, field_validator


class TripTemplateCreate(BaseModel):
    """Model for creating a trip template"""

    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str | None = Field(None, max_length=500, description="Template description")
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
    traveler_details: dict | None = None
    destinations: list[dict] | None = None
    preferences: dict | None = None

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
    traveler_details: dict | None
    destinations: list[dict]
    preferences: dict | None
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
                "destinations": [{"country": "France", "city": "Paris"}],
                "traveler_details": {"nationality": "US", "residency_country": "US"},
                "preferences": {
                    "travel_style": "balanced",
                    "dietary_restrictions": ["vegetarian"],
                },
                "created_at": "2025-12-25T10:00:00Z",
                "updated_at": "2025-12-25T10:00:00Z",
            }
        }
