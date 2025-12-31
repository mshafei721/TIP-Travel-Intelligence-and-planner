"""Pydantic models for user profile management"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    display_name: str | None = Field(None, min_length=1, max_length=100, alias="displayName")
    avatar_url: str | None = Field(None, max_length=500, alias="avatarUrl")

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            raise ValueError("Display name cannot be empty")
        return v.strip() if v else None


class TravelerProfileCreate(BaseModel):
    """Model for creating traveler profile"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    nationality: str = Field(
        ..., min_length=2, max_length=2, description="ISO Alpha-2 country code"
    )
    residency_country: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="ISO Alpha-2 country code",
        alias="residencyCountry",
    )
    residency_status: str = Field(..., min_length=1, max_length=50, alias="residencyStatus")
    date_of_birth: date | None = Field(None, alias="dateOfBirth")
    travel_style: TravelStyle = Field(default=TravelStyle.BALANCED, alias="travelStyle")
    dietary_restrictions: list[str] = Field(default_factory=list, alias="dietaryRestrictions")
    accessibility_needs: str | None = Field(None, max_length=500, alias="accessibilityNeeds")

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


class TravelerProfileUpdate(BaseModel):
    """Model for updating traveler profile (all fields optional)"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    nationality: str | None = Field(None, min_length=2, max_length=2)
    residency_country: str | None = Field(
        None, min_length=2, max_length=2, alias="residencyCountry"
    )
    residency_status: str | None = Field(None, min_length=1, max_length=50, alias="residencyStatus")
    date_of_birth: date | None = Field(None, alias="dateOfBirth")
    travel_style: TravelStyle | None = Field(None, alias="travelStyle")
    dietary_restrictions: list[str] | None = Field(None, alias="dietaryRestrictions")
    accessibility_needs: str | None = Field(None, max_length=500, alias="accessibilityNeeds")

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


class UserPreferences(BaseModel):
    """User preferences stored in user_profiles.preferences JSONB field"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    email_notifications: bool = Field(default=True, alias="emailNotifications")
    push_notifications: bool = Field(default=False, alias="pushNotifications")
    marketing_emails: bool = Field(default=False, alias="marketingEmails")
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


class AccountDeletionRequest(BaseModel):
    """Model for account deletion confirmation"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    confirmation: str = Field(..., min_length=1)

    @field_validator("confirmation")
    @classmethod
    def validate_confirmation(cls, v: str) -> str:
        """Validate confirmation text matches expected value"""
        expected = "DELETE MY ACCOUNT"
        if v != expected:
            raise ValueError(f"Confirmation must be exactly: {expected}")
        return v


class ConsentUpdate(BaseModel):
    """Model for updating user consent preferences (GDPR compliance)"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    consent_type: str = Field(
        ...,
        description=(
            "Type of consent: terms_of_service, privacy_policy, "
            "marketing_emails, data_processing, third_party_sharing, analytics"
        ),
        alias="consentType",
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


# Response models
class UserProfileResponse(BaseModel):
    """Response model for user profile"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    id: str
    display_name: str | None = Field(None, alias="displayName")
    avatar_url: str | None = Field(None, alias="avatarUrl")
    preferences: dict
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")


class TravelerProfileResponse(BaseModel):
    """Response model for traveler profile"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    id: str
    user_id: str = Field(..., alias="userId")
    nationality: str
    residency_country: str = Field(..., alias="residencyCountry")
    residency_status: str = Field(..., alias="residencyStatus")
    date_of_birth: str | None = Field(None, alias="dateOfBirth")
    travel_style: str = Field(..., alias="travelStyle")
    dietary_restrictions: list[str] = Field(..., alias="dietaryRestrictions")
    accessibility_needs: str | None = Field(None, alias="accessibilityNeeds")
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
