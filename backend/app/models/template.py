"""Pydantic models for trip template management"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TemplateDestination(BaseModel):
    """Destination within a template"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    country: str = Field(..., description="Country name")
    city: str | None = Field(None, description="City name")
    suggested_days: int | None = Field(
        None, ge=1, description="Suggested days to spend", alias="suggestedDays"
    )
    highlights: list[str] = Field(default_factory=list, description="Key highlights")


class TripTemplateCreate(BaseModel):
    """Model for creating a trip template"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str | None = Field(None, max_length=500, description="Template description")
    cover_image: str | None = Field(None, description="Cover image URL", alias="coverImage")
    is_public: bool = Field(False, description="Make template publicly visible", alias="isPublic")
    tags: list[str] = Field(default_factory=list, description="Template tags for filtering")
    traveler_details: dict | None = Field(
        None,
        description="Default traveler details (nationality, residency, etc.)",
        alias="travelerDetails",
    )
    destinations: list[dict] = Field(
        default_factory=list,
        description="List of destination objects with country and city",
    )
    preferences: dict | None = Field(
        None, description="Travel preferences (style, dietary restrictions, etc.)"
    )
    typical_duration: int | None = Field(
        None, ge=1, description="Typical trip duration in days", alias="typicalDuration"
    )
    estimated_budget: float | None = Field(
        None, ge=0, description="Estimated budget", alias="estimatedBudget"
    )
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


class TripTemplateUpdate(BaseModel):
    """Model for updating a trip template (all fields optional)"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    cover_image: str | None = Field(None, alias="coverImage")
    is_public: bool | None = Field(None, alias="isPublic")
    tags: list[str] | None = None
    traveler_details: dict | None = Field(None, alias="travelerDetails")
    destinations: list[dict] | None = None
    preferences: dict | None = None
    typical_duration: int | None = Field(None, alias="typicalDuration")
    estimated_budget: float | None = Field(None, alias="estimatedBudget")
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


class TripTemplateResponse(BaseModel):
    """Response model for trip template"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    id: str
    user_id: str = Field(..., alias="userId")
    name: str
    description: str | None
    cover_image: str | None = Field(None, alias="coverImage")
    is_public: bool = Field(default=False, alias="isPublic")
    tags: list[str] = Field(default_factory=list)
    traveler_details: dict | None = Field(None, alias="travelerDetails")
    destinations: list[dict]
    preferences: dict | None
    typical_duration: int | None = Field(None, alias="typicalDuration")
    estimated_budget: float | None = Field(None, alias="estimatedBudget")
    currency: str = "USD"
    use_count: int = Field(default=0, alias="useCount")
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")


class PublicTemplateResponse(BaseModel):
    """Response model for public template (excludes user_id for privacy)"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    id: str
    name: str
    description: str | None
    cover_image: str | None = Field(None, alias="coverImage")
    tags: list[str] = Field(default_factory=list)
    destinations: list[dict]
    typical_duration: int | None = Field(None, alias="typicalDuration")
    estimated_budget: float | None = Field(None, alias="estimatedBudget")
    currency: str = "USD"
    use_count: int = Field(default=0, alias="useCount")
    created_at: str = Field(..., alias="createdAt")


class TemplatesListResponse(BaseModel):
    """Response model for listing user's templates"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    templates: list[TripTemplateResponse]


class CreateTripFromTemplateRequest(BaseModel):
    """Request to create a trip from a template"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    title: str | None = Field(None, description="Custom trip title (optional)")
    start_date: str | None = Field(
        None, description="Trip start date (ISO format)", alias="startDate"
    )
    end_date: str | None = Field(None, description="Trip end date (ISO format)", alias="endDate")
    override_traveler_details: dict | None = Field(
        None, description="Override template traveler details", alias="overrideTravelerDetails"
    )
    override_preferences: dict | None = Field(
        None, description="Override template preferences", alias="overridePreferences"
    )
