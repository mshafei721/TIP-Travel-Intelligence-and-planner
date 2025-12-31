"""Pydantic models for user settings management"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    theme: Theme = Theme.SYSTEM
    language: str = Field(default="en", min_length=2, max_length=5)
    timezone: str = Field(default="UTC", max_length=50)
    date_format: DateFormat = Field(default=DateFormat.MDY, alias="dateFormat")
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


# =============================================================================
# Notification Settings
# =============================================================================


class NotificationSettings(BaseModel):
    """Email and push notification preferences"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    # Email notifications
    email_notifications: bool = Field(default=True, alias="emailNotifications")
    email_trip_updates: bool = Field(default=True, alias="emailTripUpdates")
    email_report_completion: bool = Field(default=True, alias="emailReportCompletion")
    email_recommendations: bool = Field(default=False, alias="emailRecommendations")
    email_marketing: bool = Field(default=False, alias="emailMarketing")
    email_weekly_digest: bool = Field(default=False, alias="emailWeeklyDigest")

    # Push notifications (for future mobile app)
    push_notifications: bool = Field(default=False, alias="pushNotifications")
    push_trip_reminders: bool = Field(default=False, alias="pushTripReminders")
    push_travel_alerts: bool = Field(default=False, alias="pushTravelAlerts")


# =============================================================================
# Privacy Settings
# =============================================================================


class PrivacySettings(BaseModel):
    """Privacy and data sharing settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    profile_visibility: ProfileVisibility = Field(
        default=ProfileVisibility.PRIVATE, alias="profileVisibility"
    )
    show_travel_history: bool = Field(default=False, alias="showTravelHistory")
    allow_template_sharing: bool = Field(default=True, alias="allowTemplateSharing")
    personalization_opt_in: bool = Field(default=True, alias="personalizationOptIn")
    share_usage_data: bool = Field(default=False, alias="shareUsageData")


# =============================================================================
# AI Settings
# =============================================================================


class AIPreferences(BaseModel):
    """AI behavior and generation preferences"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    ai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Creativity level (0.0 = precise, 1.0 = creative)",
        alias="aiTemperature",
    )
    preferred_detail_level: DetailLevel = Field(
        default=DetailLevel.BALANCED, alias="preferredDetailLevel"
    )
    include_budget_estimates: bool = Field(default=True, alias="includeBudgetEstimates")
    include_local_tips: bool = Field(default=True, alias="includeLocalTips")
    include_safety_warnings: bool = Field(default=True, alias="includeSafetyWarnings")
    preferred_pace: str = Field(
        default="balanced",
        description="Trip pacing preference: relaxed, balanced, packed",
        alias="preferredPace",
    )

    @field_validator("preferred_pace")
    @classmethod
    def validate_pace(cls, v: str) -> str:
        """Validate pace preference"""
        valid_paces = ["relaxed", "balanced", "packed"]
        if v.lower() not in valid_paces:
            raise ValueError(f"Pace must be one of: {valid_paces}")
        return v.lower()


# =============================================================================
# Complete User Settings
# =============================================================================


class UserSettings(BaseModel):
    """Complete user settings model"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    # Appearance
    appearance: AppearanceSettings = Field(default_factory=AppearanceSettings)

    # Notifications
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)

    # Privacy
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)

    # AI preferences
    ai_preferences: AIPreferences = Field(default_factory=AIPreferences, alias="aiPreferences")


# =============================================================================
# Update Models (partial updates)
# =============================================================================


class AppearanceSettingsUpdate(BaseModel):
    """Partial update for appearance settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    theme: Theme | None = None
    language: str | None = Field(None, min_length=2, max_length=5)
    timezone: str | None = Field(None, max_length=50)
    date_format: DateFormat | None = Field(None, alias="dateFormat")
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


class NotificationSettingsUpdate(BaseModel):
    """Partial update for notification settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    email_notifications: bool | None = Field(None, alias="emailNotifications")
    email_trip_updates: bool | None = Field(None, alias="emailTripUpdates")
    email_report_completion: bool | None = Field(None, alias="emailReportCompletion")
    email_recommendations: bool | None = Field(None, alias="emailRecommendations")
    email_marketing: bool | None = Field(None, alias="emailMarketing")
    email_weekly_digest: bool | None = Field(None, alias="emailWeeklyDigest")
    push_notifications: bool | None = Field(None, alias="pushNotifications")
    push_trip_reminders: bool | None = Field(None, alias="pushTripReminders")
    push_travel_alerts: bool | None = Field(None, alias="pushTravelAlerts")


class PrivacySettingsUpdate(BaseModel):
    """Partial update for privacy settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    profile_visibility: ProfileVisibility | None = Field(None, alias="profileVisibility")
    show_travel_history: bool | None = Field(None, alias="showTravelHistory")
    allow_template_sharing: bool | None = Field(None, alias="allowTemplateSharing")
    personalization_opt_in: bool | None = Field(None, alias="personalizationOptIn")
    share_usage_data: bool | None = Field(None, alias="shareUsageData")


class AIPreferencesUpdate(BaseModel):
    """Partial update for AI preferences"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    ai_temperature: float | None = Field(None, ge=0.0, le=1.0, alias="aiTemperature")
    preferred_detail_level: DetailLevel | None = Field(None, alias="preferredDetailLevel")
    include_budget_estimates: bool | None = Field(None, alias="includeBudgetEstimates")
    include_local_tips: bool | None = Field(None, alias="includeLocalTips")
    include_safety_warnings: bool | None = Field(None, alias="includeSafetyWarnings")
    preferred_pace: str | None = Field(None, alias="preferredPace")

    @field_validator("preferred_pace")
    @classmethod
    def validate_pace(cls, v: str | None) -> str | None:
        if v is not None:
            valid_paces = ["relaxed", "balanced", "packed"]
            if v.lower() not in valid_paces:
                raise ValueError(f"Pace must be one of: {valid_paces}")
            return v.lower()
        return v


class UserSettingsUpdate(BaseModel):
    """Partial update for complete settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    appearance: AppearanceSettingsUpdate | None = None
    notifications: NotificationSettingsUpdate | None = None
    privacy: PrivacySettingsUpdate | None = None
    ai_preferences: AIPreferencesUpdate | None = Field(None, alias="aiPreferences")


# =============================================================================
# Response Models
# =============================================================================


class UserSettingsResponse(BaseModel):
    """Response model for user settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    success: bool = True
    data: UserSettings


class AppearanceSettingsResponse(BaseModel):
    """Response model for appearance settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    success: bool = True
    data: AppearanceSettings


class NotificationSettingsResponse(BaseModel):
    """Response model for notification settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    success: bool = True
    data: NotificationSettings


class PrivacySettingsResponse(BaseModel):
    """Response model for privacy settings"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    success: bool = True
    data: PrivacySettings


class AIPreferencesResponse(BaseModel):
    """Response model for AI preferences"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    success: bool = True
    data: AIPreferences


# =============================================================================
# Data Export Models
# =============================================================================


class DataExportRequest(BaseModel):
    """Request model for data export"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    format: str = Field(default="json", description="Export format: json, csv")
    include_trips: bool = Field(default=True, alias="includeTrips")
    include_reports: bool = Field(default=True, alias="includeReports")
    include_templates: bool = Field(default=True, alias="includeTemplates")
    include_settings: bool = Field(default=True, alias="includeSettings")

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate export format"""
        valid_formats = ["json", "csv"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Format must be one of: {valid_formats}")
        return v.lower()


class DataExportStatus(str, Enum):
    """Data export job status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class DataExportResponse(BaseModel):
    """Response model for data export request"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    success: bool = True
    export_id: str = Field(..., alias="exportId")
    status: DataExportStatus
    download_url: str | None = Field(None, alias="downloadUrl")
    expires_at: str | None = Field(None, alias="expiresAt")
    message: str | None = None
