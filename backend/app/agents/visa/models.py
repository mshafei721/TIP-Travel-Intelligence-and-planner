"""
Visa Agent Pydantic Models

Input/Output schemas for the Visa Agent following the roadmap specification.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


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
    destination_country: str = Field(..., min_length=2, max_length=2, description="ISO Alpha-2 code")
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
        max_stay_days: Maximum allowed stay in days
        validity_period: Visa validity period (e.g., "90 days", "6 months")
    """

    visa_required: bool
    visa_type: Optional[str] = None
    max_stay_days: Optional[int] = None
    validity_period: Optional[str] = None


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

    application_method: Optional[str] = None
    processing_time: Optional[str] = None
    cost_usd: Optional[float] = None
    cost_local: Optional[str] = None
    required_documents: List[str] = Field(default_factory=list)
    application_url: Optional[str] = None


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

    passport_validity: Optional[str] = None
    blank_pages_required: Optional[int] = None
    vaccinations: List[str] = Field(default_factory=list)
    health_declaration: bool = False
    travel_insurance: bool = False
    proof_of_funds: bool = False
    return_ticket: bool = False


class VisaAgentOutput(BaseModel):
    """
    Complete output from Visa Agent

    Attributes:
        trip_id: Trip identifier (from input)
        generated_at: Timestamp when report was generated
        confidence_score: Confidence in the data (0.0 - 1.0)
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

    # Core visa information
    visa_requirement: VisaRequirement
    application_process: ApplicationProcess
    entry_requirements: EntryRequirement

    # Additional intelligence
    tips: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Data provenance
    sources: List["SourceReference"] = Field(default_factory=list)
    last_verified: datetime = Field(default_factory=datetime.utcnow)


# Import SourceReference from interfaces
from app.agents.interfaces import SourceReference

# Update forward references
VisaAgentOutput.model_rebuild()
