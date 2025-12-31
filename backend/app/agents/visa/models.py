"""
Visa Agent Pydantic Models

Input/Output schemas for the Visa Agent following the roadmap specification.
Includes enhanced visa classification and confidence scoring.
"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class VisaCategory(str, Enum):
    """
    Visa requirement categories for classification.

    Categories are ordered from least to most restrictive.
    """

    # No visa required
    VISA_FREE = "visa_free"  # No visa needed, just passport
    FREEDOM_OF_MOVEMENT = "freedom_of_movement"  # EU/Schengen-style free movement

    # Visa on arrival or electronic
    VISA_ON_ARRIVAL = "visa_on_arrival"  # Get visa at airport
    EVISA = "evisa"  # Electronic visa (apply online before travel)
    ETA = "eta"  # Electronic Travel Authorization (e.g., Canada, Australia)

    # Pre-travel visa required
    TOURIST_VISA = "tourist_visa"  # Standard tourist visa at embassy
    BUSINESS_VISA = "business_visa"  # Business purpose visa
    TRANSIT_VISA = "transit_visa"  # For transit through country
    WORK_VISA = "work_visa"  # Employment visa
    STUDENT_VISA = "student_visa"  # Study visa

    # Special categories
    RESTRICTED = "restricted"  # Travel heavily restricted
    NOT_ALLOWED = "not_allowed"  # No entry permitted
    UNKNOWN = "unknown"  # Unable to determine


class SourceType(str, Enum):
    """Type of data source for attribution."""

    GOVERNMENT = "government"  # Official government source
    EMBASSY = "embassy"  # Embassy or consulate
    API = "api"  # Travel data API (Sherpa, IATA, etc.)
    THIRD_PARTY = "third_party"  # Third-party aggregator
    AI_INFERENCE = "ai_inference"  # AI-derived information
    USER_REPORT = "user_report"  # User-contributed data


class ConfidenceLevel(str, Enum):
    """Human-readable confidence levels."""

    VERIFIED = "verified"  # >0.9 - Official source confirmed
    HIGH = "high"  # 0.75-0.9 - Multiple sources agree
    MEDIUM = "medium"  # 0.5-0.75 - Some uncertainty
    LOW = "low"  # 0.25-0.5 - Limited information
    UNCERTAIN = "uncertain"  # <0.25 - Significant uncertainty


def calculate_confidence_score(
    source_types: list[SourceType],
    sources_count: int,
    data_freshness_days: int,
    has_official_source: bool,
    data_completeness: float,
) -> tuple[float, ConfidenceLevel]:
    """
    Calculate confidence score based on multiple factors.

    Args:
        source_types: Types of sources used
        sources_count: Number of sources consulted
        data_freshness_days: Days since data was last verified
        has_official_source: Whether an official government source was used
        data_completeness: Fraction of expected fields that are populated (0-1)

    Returns:
        Tuple of (confidence_score, confidence_level)
    """
    score = 0.0

    # Base score from source types (max 0.4)
    source_weights = {
        SourceType.GOVERNMENT: 0.4,
        SourceType.EMBASSY: 0.35,
        SourceType.API: 0.3,
        SourceType.THIRD_PARTY: 0.2,
        SourceType.AI_INFERENCE: 0.15,
        SourceType.USER_REPORT: 0.1,
    }
    if source_types:
        best_source_score = max(source_weights.get(st, 0.1) for st in source_types)
        score += best_source_score

    # Bonus for multiple sources (max 0.15)
    if sources_count >= 3:
        score += 0.15
    elif sources_count == 2:
        score += 0.1
    elif sources_count == 1:
        score += 0.05

    # Freshness penalty (max 0.2, decays over time)
    if data_freshness_days <= 7:
        score += 0.2
    elif data_freshness_days <= 30:
        score += 0.15
    elif data_freshness_days <= 90:
        score += 0.1
    elif data_freshness_days <= 180:
        score += 0.05
    # Older than 180 days: no freshness bonus

    # Official source bonus (0.1)
    if has_official_source:
        score += 0.1

    # Data completeness (max 0.15)
    score += data_completeness * 0.15

    # Clamp to [0, 1]
    score = max(0.0, min(1.0, score))

    # Determine level
    if score >= 0.9:
        level = ConfidenceLevel.VERIFIED
    elif score >= 0.75:
        level = ConfidenceLevel.HIGH
    elif score >= 0.5:
        level = ConfidenceLevel.MEDIUM
    elif score >= 0.25:
        level = ConfidenceLevel.LOW
    else:
        level = ConfidenceLevel.UNCERTAIN

    return score, level


def classify_visa_type(category_string: str) -> VisaCategory:
    """
    Classify a visa type string into a VisaCategory.

    Args:
        category_string: Raw visa type string from API or user input

    Returns:
        VisaCategory enum value
    """
    if not category_string:
        return VisaCategory.UNKNOWN

    category_lower = category_string.lower().strip()

    # Visa-free categories
    if any(
        term in category_lower
        for term in ["visa-free", "visa_free", "visa free", "no visa", "exempt", "waiver"]
    ):
        return VisaCategory.VISA_FREE

    if any(
        term in category_lower for term in ["freedom", "schengen", "eu citizen", "free movement"]
    ):
        return VisaCategory.FREEDOM_OF_MOVEMENT

    # On arrival / Electronic
    if any(term in category_lower for term in ["on arrival", "on-arrival", "voa", "at airport"]):
        return VisaCategory.VISA_ON_ARRIVAL

    if any(
        term in category_lower for term in ["evisa", "e-visa", "electronic visa", "online visa"]
    ):
        return VisaCategory.EVISA

    if any(term in category_lower for term in ["eta", "electronic travel", "esta", "etas"]):
        return VisaCategory.ETA

    # Standard visas
    if any(term in category_lower for term in ["tourist", "tourism", "vacation", "holiday"]):
        return VisaCategory.TOURIST_VISA

    if any(term in category_lower for term in ["business", "commercial", "meeting"]):
        return VisaCategory.BUSINESS_VISA

    if any(term in category_lower for term in ["transit", "passing through", "layover"]):
        return VisaCategory.TRANSIT_VISA

    if any(term in category_lower for term in ["work", "employment", "job"]):
        return VisaCategory.WORK_VISA

    if any(term in category_lower for term in ["student", "study", "education"]):
        return VisaCategory.STUDENT_VISA

    # Restricted
    if any(term in category_lower for term in ["restricted", "limited", "special permit"]):
        return VisaCategory.RESTRICTED

    if any(term in category_lower for term in ["not allowed", "banned", "prohibited", "no entry"]):
        return VisaCategory.NOT_ALLOWED

    # Default
    if "visa" in category_lower and "required" in category_lower:
        return VisaCategory.TOURIST_VISA  # Assume tourist visa if just "visa required"

    return VisaCategory.UNKNOWN


class VisaAgentInput(BaseModel):
    """
    Input for Visa Agent

    Attributes:
        trip_id: Unique trip identifier
        user_nationality: ISO 3166-1 alpha-2 code (e.g., "US", "GB", "IN")
        destination_country: ISO 3166-1 alpha-2 code (e.g., "FR", "JP", "TH")
        destination_city: Destination city name
        trip_purpose: Purpose of trip (tourism, business, transit)
        duration_days: Trip duration in days
        departure_date: Trip departure date
        traveler_count: Number of travelers (default: 1)
    """

    trip_id: str
    user_nationality: str = Field(..., min_length=2, max_length=2, description="ISO Alpha-2 code")
    destination_country: str = Field(
        ..., min_length=2, max_length=2, description="ISO Alpha-2 code"
    )
    destination_city: str
    trip_purpose: str = Field(default="tourism", description="tourism, business, or transit")
    duration_days: int = Field(..., gt=0, description="Trip duration in days")
    departure_date: date
    traveler_count: int = Field(default=1, gt=0)

    @field_validator("user_nationality", "destination_country")
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Validate ISO Alpha-2 country code"""
        if not v.isalpha() or len(v) != 2:
            raise ValueError(f"Invalid country code: {v}. Must be ISO Alpha-2 (2 letters)")
        return v.upper()

    @field_validator("trip_purpose")
    @classmethod
    def validate_trip_purpose(cls, v: str) -> str:
        """Validate trip purpose"""
        valid_purposes = ["tourism", "business", "transit"]
        if v.lower() not in valid_purposes:
            raise ValueError(f"Invalid trip purpose: {v}. Must be one of {valid_purposes}")
        return v.lower()


class VisaRequirement(BaseModel):
    """
    Visa requirement information

    Attributes:
        visa_required: Whether a visa is required
        visa_type: Type of visa (tourist, business, e-visa, visa-free, etc.)
        visa_category: Standardized visa category enum
        max_stay_days: Maximum allowed stay in days
        validity_period: Visa validity period (e.g., "90 days", "6 months")
        multiple_entry: Whether multiple entries are allowed
        urgency_level: How urgent is it to apply (low, medium, high)
    """

    visa_required: bool
    visa_type: str | None = None
    visa_category: VisaCategory = VisaCategory.UNKNOWN
    max_stay_days: int | None = None
    validity_period: str | None = None
    multiple_entry: bool | None = None
    urgency_level: str | None = None  # low, medium, high

    @classmethod
    def from_api_response(cls, api_data: dict) -> "VisaRequirement":
        """
        Create VisaRequirement from API response with auto-classification.

        Args:
            api_data: Raw API response data

        Returns:
            VisaRequirement with classified visa category
        """
        visa_type = api_data.get("visa_type") or api_data.get("category", "")
        visa_category = classify_visa_type(visa_type)

        # Determine if visa is required based on category
        visa_free_categories = {
            VisaCategory.VISA_FREE,
            VisaCategory.FREEDOM_OF_MOVEMENT,
        }
        visa_required = visa_category not in visa_free_categories

        return cls(
            visa_required=visa_required,
            visa_type=visa_type,
            visa_category=visa_category,
            max_stay_days=api_data.get("max_stay_days"),
            validity_period=api_data.get("validity_period"),
            multiple_entry=api_data.get("multiple_entry"),
            urgency_level=api_data.get("urgency_level"),
        )


class ApplicationProcess(BaseModel):
    """
    Visa application process information

    Attributes:
        application_method: How to apply (online, embassy, on-arrival)
        processing_time: Estimated processing time
        cost_usd: Cost in USD
        cost_local: Cost in local currency (with currency code)
        required_documents: List of required documents
        application_url: URL to application portal
    """

    application_method: str | None = None
    processing_time: str | None = None
    cost_usd: float | None = None
    cost_local: str | None = None
    required_documents: list[str] = Field(default_factory=list)
    application_url: str | None = None


class EntryRequirement(BaseModel):
    """
    Entry requirements beyond visa

    Attributes:
        passport_validity: Required passport validity (e.g., "6 months beyond stay")
        blank_pages_required: Number of blank passport pages required
        vaccinations: Required vaccinations
        health_declaration: Whether health declaration is required
        travel_insurance: Whether travel insurance is required
        proof_of_funds: Whether proof of funds is required
        return_ticket: Whether return ticket is required
    """

    passport_validity: str | None = None
    blank_pages_required: int | None = None
    vaccinations: list[str] = Field(default_factory=list)
    health_declaration: bool = False
    travel_insurance: bool = False
    proof_of_funds: bool = False
    return_ticket: bool = False


class EnhancedSourceReference(BaseModel):
    """
    Enhanced source reference with type classification.

    Provides detailed source attribution for data provenance tracking.
    """

    source_type: SourceType = SourceType.API
    url: str = ""
    description: str = ""
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    is_official: bool = False


class VisaAgentOutput(BaseModel):
    """
    Complete output from Visa Agent

    Attributes:
        trip_id: Trip identifier (from input)
        generated_at: Timestamp when report was generated
        confidence_score: Confidence in the data (0.0 - 1.0)
        confidence_level: Human-readable confidence level
        visa_requirement: Core visa information
        application_process: How to apply for visa
        entry_requirements: Entry requirements beyond visa
        tips: Helpful tips for travelers
        warnings: Important warnings
        sources: Data source references
        last_verified: When data was last verified
    """

    trip_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM

    # Core visa information
    visa_requirement: VisaRequirement
    application_process: ApplicationProcess
    entry_requirements: EntryRequirement

    # Additional intelligence
    tips: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    # Data provenance
    sources: list["SourceReference"] = Field(default_factory=list)
    enhanced_sources: list[EnhancedSourceReference] = Field(default_factory=list)
    last_verified: datetime = Field(default_factory=datetime.utcnow)

    def recalculate_confidence(self) -> None:
        """
        Recalculate confidence score based on sources and data completeness.

        Updates both confidence_score and confidence_level fields.
        """
        # Get source types from enhanced sources
        source_types = [s.source_type for s in self.enhanced_sources]
        sources_count = len(self.enhanced_sources)

        # Check for official sources
        has_official = any(s.is_official for s in self.enhanced_sources)

        # Calculate data freshness (days since last verified)
        freshness_days = (datetime.utcnow() - self.last_verified).days

        # Calculate data completeness
        completeness_fields = [
            self.visa_requirement.visa_type is not None,
            self.visa_requirement.max_stay_days is not None,
            self.application_process.application_method is not None,
            self.application_process.processing_time is not None,
            self.entry_requirements.passport_validity is not None,
            len(self.tips) > 0,
        ]
        data_completeness = sum(completeness_fields) / len(completeness_fields)

        # Calculate new score
        self.confidence_score, self.confidence_level = calculate_confidence_score(
            source_types=source_types,
            sources_count=sources_count,
            data_freshness_days=freshness_days,
            has_official_source=has_official,
            data_completeness=data_completeness,
        )


# Import SourceReference from interfaces
from app.agents.interfaces import SourceReference

# Update forward references
VisaAgentOutput.model_rebuild()
