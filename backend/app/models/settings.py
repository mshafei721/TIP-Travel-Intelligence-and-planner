"""Pydantic models for user settings management"""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Theme(str, Enum):
    """Application theme options"""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ProfileVisibility(str, Enum):
    """Profile visibility levels"""

    PRIVATE = "private"
    FRIENDS = "friends"
    PUBLIC = "public"


class DetailLevel(str, Enum):
    """AI response detail level preferences"""

    BRIEF = "brief"
    BALANCED = "balanced"
    DETAILED = "detailed"


class DateFormat(str, Enum):
    """Date format options"""

    MDY = "MM/DD/YYYY"
    DMY = "DD/MM/YYYY"
    YMD = "YYYY-MM-DD"
    ISO = "ISO8601"


class Units(str, Enum):
    """Measurement unit systems"""

    METRIC = "metric"
    IMPERIAL = "imperial"


# =============================================================================
# Appearance Settings
# =============================================================================


class AppearanceSettings(BaseModel):
    """Appearance and display settings"""

    theme: Theme = Theme.SYSTEM
    language: str = Field(default="en", min_length=2, max_length=5)
    timezone: str = Field(default="UTC", max_length=50)
    date_format: DateFormat = DateFormat.MDY
    currency: str = Field(default="USD", min_length=3, max_length=3)
    units: Units = Units.METRIC

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code format (ISO 639-1)"""
        return v.lower()

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code format (ISO 4217)"""
        if not v.isupper():
            return v.upper()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "language": "en",
                "timezone": "America/New_York",
                "date_format": "MM/DD/YYYY",
                "currency": "USD",
                "units": "metric",
            }
        }


# =============================================================================
# Notification Settings
# =============================================================================


class NotificationSettings(BaseModel):
    """Email and push notification preferences"""

    # Email notifications
    email_notifications: bool = True
    email_trip_updates: bool = True
    email_report_completion: bool = True
    email_recommendations: bool = False
    email_marketing: bool = False
    email_weekly_digest: bool = False

    # Push notifications (for future mobile app)
    push_notifications: bool = False
    push_trip_reminders: bool = False
    push_travel_alerts: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "email_notifications": True,
                "email_trip_updates": True,
                "email_report_completion": True,
                "email_recommendations": False,
                "email_marketing": False,
                "email_weekly_digest": False,
                "push_notifications": False,
                "push_trip_reminders": False,
                "push_travel_alerts": False,
            }
        }


# =============================================================================
# Privacy Settings
# =============================================================================


class PrivacySettings(BaseModel):
    """Privacy and data sharing settings"""

    profile_visibility: ProfileVisibility = ProfileVisibility.PRIVATE
    show_travel_history: bool = False
    allow_template_sharing: bool = True
    analytics_opt_in: bool = True
    personalization_opt_in: bool = True
    share_usage_data: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "profile_visibility": "private",
                "show_travel_history": False,
                "allow_template_sharing": True,
                "analytics_opt_in": True,
                "personalization_opt_in": True,
                "share_usage_data": False,
            }
        }


# =============================================================================
# AI Settings
# =============================================================================


class AIPreferences(BaseModel):
    """AI behavior and generation preferences"""

    ai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Creativity level (0.0 = precise, 1.0 = creative)",
    )
    preferred_detail_level: DetailLevel = DetailLevel.BALANCED
    include_budget_estimates: bool = True
    include_local_tips: bool = True
    include_safety_warnings: bool = True
    preferred_pace: str = Field(
        default="balanced",
        description="Trip pacing preference: relaxed, balanced, packed",
    )

    @field_validator("preferred_pace")
    @classmethod
    def validate_pace(cls, v: str) -> str:
        """Validate pace preference"""
        valid_paces = ["relaxed", "balanced", "packed"]
        if v.lower() not in valid_paces:
            raise ValueError(f"Pace must be one of: {valid_paces}")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "ai_temperature": 0.7,
                "preferred_detail_level": "balanced",
                "include_budget_estimates": True,
                "include_local_tips": True,
                "include_safety_warnings": True,
                "preferred_pace": "balanced",
            }
        }


# =============================================================================
# Complete User Settings
# =============================================================================


class UserSettings(BaseModel):
    """Complete user settings model"""

    # Appearance
    appearance: AppearanceSettings = Field(default_factory=AppearanceSettings)

    # Notifications
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)

    # Privacy
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)

    # AI preferences
    ai_preferences: AIPreferences = Field(default_factory=AIPreferences)

    class Config:
        json_schema_extra = {
            "example": {
                "appearance": {
                    "theme": "dark",
                    "language": "en",
                    "timezone": "UTC",
                    "date_format": "MM/DD/YYYY",
                    "currency": "USD",
                    "units": "metric",
                },
                "notifications": {
                    "email_notifications": True,
                    "email_trip_updates": True,
                    "push_notifications": False,
                },
                "privacy": {
                    "profile_visibility": "private",
                    "analytics_opt_in": True,
                },
                "ai_preferences": {
                    "ai_temperature": 0.7,
                    "preferred_detail_level": "balanced",
                },
            }
        }


# =============================================================================
# Update Models (partial updates)
# =============================================================================


class AppearanceSettingsUpdate(BaseModel):
    """Partial update for appearance settings"""

    theme: Theme | None = None
    language: str | None = Field(None, min_length=2, max_length=5)
    timezone: str | None = Field(None, max_length=50)
    date_format: DateFormat | None = None
    currency: str | None = Field(None, min_length=3, max_length=3)
    units: Units | None = None

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is not None:
            return v.lower()
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str | None) -> str | None:
        if v is not None:
            return v.upper()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "timezone": "America/New_York",
            }
        }


class NotificationSettingsUpdate(BaseModel):
    """Partial update for notification settings"""

    email_notifications: bool | None = None
    email_trip_updates: bool | None = None
    email_report_completion: bool | None = None
    email_recommendations: bool | None = None
    email_marketing: bool | None = None
    email_weekly_digest: bool | None = None
    push_notifications: bool | None = None
    push_trip_reminders: bool | None = None
    push_travel_alerts: bool | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email_notifications": True,
                "push_notifications": True,
            }
        }


class PrivacySettingsUpdate(BaseModel):
    """Partial update for privacy settings"""

    profile_visibility: ProfileVisibility | None = None
    show_travel_history: bool | None = None
    allow_template_sharing: bool | None = None
    analytics_opt_in: bool | None = None
    personalization_opt_in: bool | None = None
    share_usage_data: bool | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "profile_visibility": "friends",
                "show_travel_history": True,
            }
        }


class AIPreferencesUpdate(BaseModel):
    """Partial update for AI preferences"""

    ai_temperature: float | None = Field(None, ge=0.0, le=1.0)
    preferred_detail_level: DetailLevel | None = None
    include_budget_estimates: bool | None = None
    include_local_tips: bool | None = None
    include_safety_warnings: bool | None = None
    preferred_pace: str | None = None

    @field_validator("preferred_pace")
    @classmethod
    def validate_pace(cls, v: str | None) -> str | None:
        if v is not None:
            valid_paces = ["relaxed", "balanced", "packed"]
            if v.lower() not in valid_paces:
                raise ValueError(f"Pace must be one of: {valid_paces}")
            return v.lower()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "ai_temperature": 0.8,
                "preferred_detail_level": "detailed",
            }
        }


class UserSettingsUpdate(BaseModel):
    """Partial update for complete settings"""

    appearance: AppearanceSettingsUpdate | None = None
    notifications: NotificationSettingsUpdate | None = None
    privacy: PrivacySettingsUpdate | None = None
    ai_preferences: AIPreferencesUpdate | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "appearance": {"theme": "dark"},
                "notifications": {"email_notifications": True},
            }
        }


# =============================================================================
# Response Models
# =============================================================================


class UserSettingsResponse(BaseModel):
    """Response model for user settings"""

    success: bool = True
    data: UserSettings

    class Config:
        from_attributes = True


class AppearanceSettingsResponse(BaseModel):
    """Response model for appearance settings"""

    success: bool = True
    data: AppearanceSettings

    class Config:
        from_attributes = True


class NotificationSettingsResponse(BaseModel):
    """Response model for notification settings"""

    success: bool = True
    data: NotificationSettings

    class Config:
        from_attributes = True


class PrivacySettingsResponse(BaseModel):
    """Response model for privacy settings"""

    success: bool = True
    data: PrivacySettings

    class Config:
        from_attributes = True


class AIPreferencesResponse(BaseModel):
    """Response model for AI preferences"""

    success: bool = True
    data: AIPreferences

    class Config:
        from_attributes = True


# =============================================================================
# Data Export Models
# =============================================================================


class DataExportRequest(BaseModel):
    """Request model for data export"""

    format: str = Field(default="json", description="Export format: json, csv")
    include_trips: bool = True
    include_reports: bool = True
    include_templates: bool = True
    include_settings: bool = True

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate export format"""
        valid_formats = ["json", "csv"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Format must be one of: {valid_formats}")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "format": "json",
                "include_trips": True,
                "include_reports": True,
                "include_templates": True,
                "include_settings": True,
            }
        }


class DataExportStatus(str, Enum):
    """Data export job status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class DataExportResponse(BaseModel):
    """Response model for data export request"""

    success: bool = True
    export_id: str
    status: DataExportStatus
    download_url: str | None = None
    expires_at: str | None = None
    message: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "export_id": "exp_abc123",
                "status": "completed",
                "download_url": "https://storage.example.com/exports/abc123.json",
                "expires_at": "2025-12-27T12:00:00Z",
                "message": "Your data export is ready for download",
            }
        }
