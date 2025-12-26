"""Pydantic models for user profile management"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TravelStyle(str, Enum):
    """Travel style preferences"""

    BUDGET = "budget"
    BALANCED = "balanced"
    LUXURY = "luxury"


class Units(str, Enum):
    """Measurement units"""

    METRIC = "metric"
    IMPERIAL = "imperial"


class UserProfileUpdate(BaseModel):
    """Model for updating user profile (user_profiles table)"""

    display_name: str | None = Field(None, min_length=1, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            raise ValueError("Display name cannot be empty")
        return v.strip() if v else None

    class Config:
        json_schema_extra = {
            "example": {
                "display_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
            }
        }


class TravelerProfileCreate(BaseModel):
    """Model for creating traveler profile"""

    nationality: str = Field(
        ..., min_length=2, max_length=2, description="ISO Alpha-2 country code"
    )
    residency_country: str = Field(
        ..., min_length=2, max_length=2, description="ISO Alpha-2 country code"
    )
    residency_status: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date | None = None
    travel_style: TravelStyle = TravelStyle.BALANCED
    dietary_restrictions: list[str] = Field(default_factory=list)
    accessibility_needs: str | None = Field(None, max_length=500)

    @field_validator("nationality", "residency_country")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate ISO Alpha-2 country code format"""
        if not v.isupper():
            raise ValueError("Country code must be uppercase")
        if len(v) != 2:
            raise ValueError("Country code must be 2 characters (ISO Alpha-2)")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: date | None) -> date | None:
        """Validate date of birth is in the past"""
        if v is not None and v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nationality": "US",
                "residency_country": "US",
                "residency_status": "citizen",
                "date_of_birth": "1990-01-01",
                "travel_style": "balanced",
                "dietary_restrictions": ["vegetarian", "gluten-free"],
                "accessibility_needs": "Wheelchair accessible",
            }
        }


class TravelerProfileUpdate(BaseModel):
    """Model for updating traveler profile (all fields optional)"""

    nationality: str | None = Field(None, min_length=2, max_length=2)
    residency_country: str | None = Field(None, min_length=2, max_length=2)
    residency_status: str | None = Field(None, min_length=1, max_length=50)
    date_of_birth: date | None = None
    travel_style: TravelStyle | None = None
    dietary_restrictions: list[str] | None = None
    accessibility_needs: str | None = Field(None, max_length=500)

    @field_validator("nationality", "residency_country")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        """Validate ISO Alpha-2 country code format"""
        if v is not None:
            if not v.isupper():
                raise ValueError("Country code must be uppercase")
            if len(v) != 2:
                raise ValueError("Country code must be 2 characters (ISO Alpha-2)")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: date | None) -> date | None:
        """Validate date of birth is in the past"""
        if v is not None and v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nationality": "US",
                "travel_style": "luxury",
                "dietary_restrictions": ["vegan"],
            }
        }


class UserPreferences(BaseModel):
    """User preferences stored in user_profiles.preferences JSONB field"""

    email_notifications: bool = True
    push_notifications: bool = False
    marketing_emails: bool = False
    language: str = Field(default="en", min_length=2, max_length=5)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    units: Units = Units.METRIC

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code format (ISO 639-1)"""
        if len(v) < 2:
            raise ValueError("Language code must be at least 2 characters")
        return v.lower()

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code format (ISO 4217)"""
        if not v.isupper():
            raise ValueError("Currency code must be uppercase")
        if len(v) != 3:
            raise ValueError("Currency code must be 3 characters (ISO 4217)")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email_notifications": True,
                "push_notifications": False,
                "marketing_emails": False,
                "language": "en",
                "currency": "USD",
                "units": "metric",
            }
        }


class AccountDeletionRequest(BaseModel):
    """Model for account deletion confirmation"""

    confirmation: str = Field(..., min_length=1)

    @field_validator("confirmation")
    @classmethod
    def validate_confirmation(cls, v: str) -> str:
        """Validate confirmation text matches expected value"""
        expected = "DELETE MY ACCOUNT"
        if v != expected:
            raise ValueError(f"Confirmation must be exactly: {expected}")
        return v

    class Config:
        json_schema_extra = {"example": {"confirmation": "DELETE MY ACCOUNT"}}


class ConsentUpdate(BaseModel):
    """Model for updating user consent preferences (GDPR compliance)"""

    consent_type: str = Field(
        ...,
        description=(
            "Type of consent: terms_of_service, privacy_policy, "
            "marketing_emails, data_processing, third_party_sharing, analytics"
        ),
    )
    granted: bool = Field(..., description="Whether consent is granted or revoked")
    version: str = Field(default="1.0", description="Version of terms/policy")

    @field_validator("consent_type")
    @classmethod
    def validate_consent_type(cls, v: str) -> str:
        """Validate consent type is valid"""
        valid_types = [
            "terms_of_service",
            "privacy_policy",
            "marketing_emails",
            "data_processing",
            "third_party_sharing",
            "analytics",
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid consent type. Must be one of: {valid_types}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "consent_type": "marketing_emails",
                "granted": True,
                "version": "1.0",
            }
        }


# Response models
class UserProfileResponse(BaseModel):
    """Response model for user profile"""

    id: str
    display_name: str | None
    avatar_url: str | None
    preferences: dict
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TravelerProfileResponse(BaseModel):
    """Response model for traveler profile"""

    id: str
    user_id: str
    nationality: str
    residency_country: str
    residency_status: str
    date_of_birth: str | None
    travel_style: str
    dietary_restrictions: list[str]
    accessibility_needs: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
