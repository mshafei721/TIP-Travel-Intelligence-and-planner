"""Report API response models"""

from datetime import datetime

from pydantic import BaseModel, Field


class SourceReferenceResponse(BaseModel):
    """
    Source reference in API response

    Field aliases ensure frontend compatibility:
    - 'title' -> serialized as 'name' for frontend
    - 'source_type' -> serialized as 'type' for frontend
    - 'verified_at' -> serialized as 'lastVerified' for frontend

    Accepts both original field names and frontend aliases during input.
    Outputs using frontend-compatible aliases.
    """

    url: str = ""
    # source_type/type - accepts both, outputs as 'type'
    source_type: str = Field(
        default="third-party",
        validation_alias="type",  # Accept 'type' during input
        serialization_alias="type",  # Output as 'type'
    )
    # title/name - accepts both, outputs as 'name'
    title: str | None = Field(
        default=None,
        validation_alias="name",  # Accept 'name' during input
        serialization_alias="name",  # Output as 'name'
    )
    reliability: str | None = None
    accessed_at: datetime | None = None
    # verified_at/lastVerified - accepts both, outputs as 'lastVerified'
    verified_at: datetime | None = Field(
        default=None,
        validation_alias="lastVerified",  # Accept 'lastVerified' during input
        serialization_alias="lastVerified",  # Output as 'lastVerified'
    )

    model_config = {
        "extra": "ignore",  # Ignore extra fields from agent output
        "populate_by_name": True,  # Accept both original and alias names for input
        "by_alias": True,  # Use alias names when serializing (for FastAPI responses)
    }


class VisaRequirementResponse(BaseModel):
    """Visa requirement details"""

    visa_required: bool = True
    visa_type: str | None = None
    visa_category: str | None = None  # Added from agent
    max_stay_days: int | None = None
    validity_period: str | None = None
    multiple_entry: bool | None = None  # Added from agent
    urgency_level: str | None = None  # Added from agent

    class Config:
        extra = "ignore"


class ApplicationProcessResponse(BaseModel):
    """Visa application process details"""

    application_method: str | None = None
    processing_time: str | None = None
    cost_usd: float | None = None
    cost_local: str | None = None
    required_documents: list[str] = Field(default_factory=list)
    application_url: str | None = None

    class Config:
        extra = "ignore"


class EntryRequirementResponse(BaseModel):
    """Entry requirements beyond visa"""

    passport_validity: str | None = None
    blank_pages_required: int | None = None
    vaccinations: list[str] = Field(default_factory=list)
    health_declaration: bool = False
    travel_insurance: bool = False
    proof_of_funds: bool = False
    return_ticket: bool = False

    class Config:
        extra = "ignore"


class VisaReportResponse(BaseModel):
    """
    Complete visa report response

    This is the API response format for GET /trips/{id}/report/visa
    """

    report_id: str
    trip_id: str
    generated_at: datetime
    confidence_score: float  # 0.0 - 1.0
    confidence_level: str | None = None  # Added: human-readable confidence

    # Trip context (from trip data)
    user_nationality: str | None = None
    destination_country: str | None = None
    destination_city: str | None = None
    trip_purpose: str | None = None
    duration_days: int | None = None

    # Core visa information
    visa_requirement: VisaRequirementResponse
    application_process: ApplicationProcessResponse
    entry_requirements: EntryRequirementResponse

    # Additional intelligence
    tips: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    # Data provenance
    sources: list[SourceReferenceResponse] = Field(default_factory=list)
    last_verified: datetime | None = None
    is_partial_data: bool = False

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
    notes: str | None = None


class PowerOutletResponse(BaseModel):
    """Power outlet information"""

    plug_types: list[str]
    voltage: str
    frequency: str


class TravelAdvisoryResponse(BaseModel):
    """Travel advisory information"""

    level: str
    title: str
    summary: str
    updated_at: str | None = None
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
    subregion: str | None = None

    # Demographics
    population: int
    area_km2: float | None = None
    population_density: float | None = None

    # Languages and Communication
    official_languages: list[str]
    common_languages: list[str] | None = None

    # Time and Geography
    time_zones: list[str]
    coordinates: dict | None = None
    borders: list[str] | None = None

    # Practical Information
    emergency_numbers: list[EmergencyContactResponse]
    power_outlet: PowerOutletResponse
    driving_side: str

    # Currency
    currencies: list[str]
    currency_codes: list[str]

    # Safety and Advisories
    safety_rating: float  # 0.0 - 5.0
    travel_advisories: list[TravelAdvisoryResponse] = Field(default_factory=list)

    # Additional Information
    notable_facts: list[str] = Field(default_factory=list)
    best_time_to_visit: str | None = None

    # Metadata
    sources: list[SourceReferenceResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Itinerary Report Models


class ItineraryReportResponse(BaseModel):
    """
    Complete itinerary report response

    This is the API response format for GET /trips/{id}/report/itinerary
    Returns the full itinerary content as generated by the ItineraryAgent
    """

    report_id: str
    trip_id: str
    generated_at: datetime
    confidence_score: float  # 0.0 - 1.0

    # Itinerary content (structured as per ItineraryAgentOutput)
    content: dict  # Full itinerary data including daily_plans, accommodations, etc.

    # Metadata
    sources: list[SourceReferenceResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Flight Report Models


class FlightReportResponse(BaseModel):
    """
    Complete flight report response

    This is the API response format for GET /trips/{id}/report/flight
    Returns the full flight recommendations as generated by the FlightAgent
    """

    report_id: str
    trip_id: str
    generated_at: datetime
    confidence_score: float  # 0.0 - 1.0

    # Flight content (structured as per FlightAgentOutput)
    content: dict  # Full flight data including recommended_flights, pricing, airport info, etc.

    # Metadata
    sources: list[SourceReferenceResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Full Report Models (Aggregated)


class TripInfoResponse(BaseModel):
    """Basic trip information for the report header."""

    trip_id: str
    title: str
    destination_country: str
    destination_city: str | None = None
    departure_date: str
    return_date: str | None = None
    travelers: int = 1
    status: str
    created_at: datetime


class ReportSectionResponse(BaseModel):
    """Individual report section in aggregated report."""

    section_type: str
    title: str
    content: dict
    confidence_score: float
    generated_at: datetime
    sources: list[dict] = Field(default_factory=list)


class FullReportResponse(BaseModel):
    """
    Complete aggregated report response

    This is the API response format for GET /trips/{id}/report
    Returns all report sections combined into a single response.
    """

    trip_id: str
    trip_info: TripInfoResponse
    sections: dict[str, ReportSectionResponse] = Field(default_factory=dict)
    available_sections: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    overall_confidence: float = 0.0
    generated_at: datetime
    is_complete: bool = False

    class Config:
        from_attributes = True


class PDFExportResponse(BaseModel):
    """Response for PDF export endpoint."""

    success: bool
    pdf_url: str | None = None
    message: str | None = None

    class Config:
        from_attributes = True


class PDFExportError(BaseModel):
    """Error response for PDF export."""

    detail: str = "PDF generation failed"
    code: str = "PDF_GENERATION_ERROR"
