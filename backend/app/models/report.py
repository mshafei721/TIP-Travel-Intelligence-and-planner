"""Report API response models"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SourceReferenceResponse(BaseModel):
    """Source reference in API response"""
    url: str
    source_type: str
    title: Optional[str] = None
    reliability: Optional[str] = None
    accessed_at: Optional[datetime] = None


class VisaRequirementResponse(BaseModel):
    """Visa requirement details"""
    visa_required: bool
    visa_type: Optional[str] = None
    max_stay_days: Optional[int] = None
    validity_period: Optional[str] = None


class ApplicationProcessResponse(BaseModel):
    """Visa application process details"""
    application_method: Optional[str] = None
    processing_time: Optional[str] = None
    cost_usd: Optional[float] = None
    cost_local: Optional[str] = None
    required_documents: List[str] = Field(default_factory=list)
    application_url: Optional[str] = None


class EntryRequirementResponse(BaseModel):
    """Entry requirements beyond visa"""
    passport_validity: Optional[str] = None
    blank_pages_required: Optional[int] = None
    vaccinations: List[str] = Field(default_factory=list)
    health_declaration: bool = False
    travel_insurance: bool = False
    proof_of_funds: bool = False
    return_ticket: bool = False


class VisaReportResponse(BaseModel):
    """
    Complete visa report response

    This is the API response format for GET /trips/{id}/report/visa
    """
    report_id: str
    trip_id: str
    generated_at: datetime
    confidence_score: float  # 0.0 - 1.0

    # Core visa information
    visa_requirement: VisaRequirementResponse
    application_process: ApplicationProcessResponse
    entry_requirements: EntryRequirementResponse

    # Additional intelligence
    tips: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Data provenance
    sources: List[SourceReferenceResponse] = Field(default_factory=list)
    last_verified: datetime

    class Config:
        from_attributes = True


class ReportNotFoundError(BaseModel):
    """Error response when report is not found"""
    detail: str = "Visa report not found for this trip"
    code: str = "REPORT_NOT_FOUND"
    suggestion: str = "Generate the trip report first using POST /trips/{id}/generate"


class ReportUnauthorizedError(BaseModel):
    """Error response when user doesn't own the trip"""
    detail: str = "You do not have permission to access this report"
    code: str = "UNAUTHORIZED"


# Country/Destination Report Models

class EmergencyContactResponse(BaseModel):
    """Emergency contact information"""
    service: str
    number: str
    notes: Optional[str] = None


class PowerOutletResponse(BaseModel):
    """Power outlet information"""
    plug_types: List[str]
    voltage: str
    frequency: str


class TravelAdvisoryResponse(BaseModel):
    """Travel advisory information"""
    level: str
    title: str
    summary: str
    updated_at: Optional[str] = None
    source: str


class CountryReportResponse(BaseModel):
    """
    Complete country/destination intelligence report response

    This is the API response format for GET /trips/{id}/report/destination
    """
    report_id: str
    trip_id: str
    generated_at: datetime
    confidence_score: float  # 0.0 - 1.0

    # Basic Information
    country_name: str
    country_code: str
    capital: str
    region: str
    subregion: Optional[str] = None

    # Demographics
    population: int
    area_km2: Optional[float] = None
    population_density: Optional[float] = None

    # Languages and Communication
    official_languages: List[str]
    common_languages: Optional[List[str]] = None

    # Time and Geography
    time_zones: List[str]
    coordinates: Optional[dict] = None
    borders: Optional[List[str]] = None

    # Practical Information
    emergency_numbers: List[EmergencyContactResponse]
    power_outlet: PowerOutletResponse
    driving_side: str

    # Currency
    currencies: List[str]
    currency_codes: List[str]

    # Safety and Advisories
    safety_rating: float  # 0.0 - 5.0
    travel_advisories: List[TravelAdvisoryResponse] = Field(default_factory=list)

    # Additional Information
    notable_facts: List[str] = Field(default_factory=list)
    best_time_to_visit: Optional[str] = None

    # Metadata
    sources: List[SourceReferenceResponse] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
