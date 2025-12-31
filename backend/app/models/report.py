"""Report API response models"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        serialize_by_alias=True,
    )

    url: str = ""
    # source_type/type - accepts both, outputs as 'type'
    source_type: str = Field(
        default="third-party",
        alias="type",
    )
    # title/name - accepts both, outputs as 'name'
    title: str | None = Field(
        default=None,
        alias="name",
    )
    reliability: str | None = None
    accessed_at: datetime | None = Field(default=None, alias="accessedAt")
    # verified_at/lastVerified - accepts both, outputs as 'lastVerified'
    verified_at: datetime | None = Field(
        default=None,
        alias="lastVerified",
    )


class VisaRequirementResponse(BaseModel):
    """Visa requirement details"""

    model_config = ConfigDict(extra="ignore", populate_by_name=True, serialize_by_alias=True)

    visa_required: bool = Field(default=True, alias="visaRequired")
    visa_type: str | None = Field(default=None, alias="visaType")
    visa_category: str | None = Field(default=None, alias="visaCategory")  # Added from agent
    max_stay_days: int | None = Field(default=None, alias="maxStayDays")
    validity_period: str | None = Field(default=None, alias="validityPeriod")
    multiple_entry: bool | None = Field(default=None, alias="multipleEntry")  # Added from agent
    urgency_level: str | None = Field(default=None, alias="urgencyLevel")  # Added from agent


class ApplicationProcessResponse(BaseModel):
    """Visa application process details"""

    model_config = ConfigDict(extra="ignore", populate_by_name=True, serialize_by_alias=True)

    application_method: str | None = Field(default=None, alias="applicationMethod")
    processing_time: str | None = Field(default=None, alias="processingTime")
    cost_usd: float | None = Field(default=None, alias="costUsd")
    cost_local: str | None = Field(default=None, alias="costLocal")
    required_documents: list[str] = Field(default_factory=list, alias="requiredDocuments")
    application_url: str | None = Field(default=None, alias="applicationUrl")


class EntryRequirementResponse(BaseModel):
    """Entry requirements beyond visa"""

    model_config = ConfigDict(extra="ignore", populate_by_name=True, serialize_by_alias=True)

    passport_validity: str | None = Field(default=None, alias="passportValidity")
    blank_pages_required: int | None = Field(default=None, alias="blankPagesRequired")
    vaccinations: list[str] = Field(default_factory=list)
    health_declaration: bool = Field(default=False, alias="healthDeclaration")
    travel_insurance: bool = Field(default=False, alias="travelInsurance")
    proof_of_funds: bool = Field(default=False, alias="proofOfFunds")
    return_ticket: bool = Field(default=False, alias="returnTicket")


class VisaReportResponse(BaseModel):
    """
    Complete visa report response

    This is the API response format for GET /trips/{id}/report/visa
    """

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    report_id: str = Field(..., alias="reportId")
    trip_id: str = Field(..., alias="tripId")
    generated_at: datetime = Field(..., alias="generatedAt")
    confidence_score: float = Field(..., alias="confidenceScore")  # 0.0 - 1.0
    confidence_level: str | None = Field(default=None, alias="confidenceLevel")

    # Trip context (from trip data)
    user_nationality: str | None = Field(default=None, alias="userNationality")
    destination_country: str | None = Field(default=None, alias="destinationCountry")
    destination_city: str | None = Field(default=None, alias="destinationCity")
    trip_purpose: str | None = Field(default=None, alias="tripPurpose")
    duration_days: int | None = Field(default=None, alias="durationDays")

    # Core visa information
    visa_requirement: VisaRequirementResponse = Field(..., alias="visaRequirement")
    application_process: ApplicationProcessResponse = Field(..., alias="applicationProcess")
    entry_requirements: EntryRequirementResponse = Field(..., alias="entryRequirements")

    # Additional intelligence
    tips: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    # Data provenance
    sources: list[SourceReferenceResponse] = Field(default_factory=list)
    last_verified: datetime | None = Field(default=None, alias="lastVerified")
    is_partial_data: bool = Field(default=False, alias="isPartialData")


class ReportNotFoundError(BaseModel):
    """Error response when report is not found"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    detail: str = "Visa report not found for this trip"
    code: str = "REPORT_NOT_FOUND"
    suggestion: str = "Generate the trip report first using POST /trips/{id}/generate"


class ReportUnauthorizedError(BaseModel):
    """Error response when user doesn't own the trip"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    detail: str = "You do not have permission to access this report"
    code: str = "UNAUTHORIZED"


# Country/Destination Report Models


class EmergencyContactResponse(BaseModel):
    """Emergency contact information"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    service: str
    number: str
    notes: str | None = None


class PowerOutletResponse(BaseModel):
    """Power outlet information"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    plug_types: list[str] = Field(..., alias="plugTypes")
    voltage: str
    frequency: str


class TravelAdvisoryResponse(BaseModel):
    """Travel advisory information"""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    level: str
    title: str
    summary: str
    updated_at: str | None = Field(default=None, alias="updatedAt")
    source: str


class CountryReportResponse(BaseModel):
    """
    Complete country/destination intelligence report response

    This is the API response format for GET /trips/{id}/report/destination
    """

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    report_id: str = Field(..., alias="reportId")
    trip_id: str = Field(..., alias="tripId")
    generated_at: datetime = Field(..., alias="generatedAt")
    confidence_score: float = Field(..., alias="confidenceScore")  # 0.0 - 1.0

    # Basic Information
    country_name: str = Field(..., alias="countryName")
    country_code: str = Field(..., alias="countryCode")
    capital: str
    region: str
    subregion: str | None = None

    # Demographics
    population: int
    area_km2: float | None = Field(default=None, alias="areaKm2")
    population_density: float | None = Field(default=None, alias="populationDensity")

    # Languages and Communication
    official_languages: list[str] = Field(..., alias="officialLanguages")
    common_languages: list[str] | None = Field(default=None, alias="commonLanguages")

    # Time and Geography
    time_zones: list[str] = Field(..., alias="timeZones")
    coordinates: dict | None = None
    borders: list[str] | None = None

    # Practical Information
    emergency_numbers: list[EmergencyContactResponse] = Field(..., alias="emergencyNumbers")
    power_outlet: PowerOutletResponse = Field(..., alias="powerOutlet")
    driving_side: str = Field(..., alias="drivingSide")

    # Currency
    currencies: list[str]
    currency_codes: list[str] = Field(..., alias="currencyCodes")

    # Safety and Advisories
    safety_rating: float = Field(..., alias="safetyRating")  # 0.0 - 5.0
    travel_advisories: list[TravelAdvisoryResponse] = Field(
        default_factory=list, alias="travelAdvisories"
    )

    # Additional Information
    notable_facts: list[str] = Field(default_factory=list, alias="notableFacts")
    best_time_to_visit: str | None = Field(default=None, alias="bestTimeToVisit")

    # Metadata
    sources: list[SourceReferenceResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# Itinerary Report Models


class ItineraryReportResponse(BaseModel):
    """
    Complete itinerary report response

    This is the API response format for GET /trips/{id}/report/itinerary
    Returns the full itinerary content as generated by the ItineraryAgent
    """

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    report_id: str = Field(..., alias="reportId")
    trip_id: str = Field(..., alias="tripId")
    generated_at: datetime = Field(..., alias="generatedAt")
    confidence_score: float = Field(..., alias="confidenceScore")  # 0.0 - 1.0

    # Itinerary content (structured as per ItineraryAgentOutput)
    content: dict  # Full itinerary data including daily_plans, accommodations, etc.

    # Metadata
    sources: list[SourceReferenceResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# Flight Report Models


class FlightReportResponse(BaseModel):
    """
    Complete flight report response

    This is the API response format for GET /trips/{id}/report/flight
    Returns the full flight recommendations as generated by the FlightAgent
    """

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    report_id: str = Field(..., alias="reportId")
    trip_id: str = Field(..., alias="tripId")
    generated_at: datetime = Field(..., alias="generatedAt")
    confidence_score: float = Field(..., alias="confidenceScore")  # 0.0 - 1.0

    # Flight content (structured as per FlightAgentOutput)
    content: dict  # Full flight data including recommended_flights, pricing, airport info, etc.

    # Metadata
    sources: list[SourceReferenceResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# Full Report Models (Aggregated)


class TripInfoResponse(BaseModel):
    """Basic trip information for the report header."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    title: str
    destination_country: str = Field(..., alias="destinationCountry")
    destination_city: str | None = Field(default=None, alias="destinationCity")
    departure_date: str = Field(..., alias="departureDate")
    return_date: str | None = Field(default=None, alias="returnDate")
    travelers: int = 1
    status: str
    created_at: datetime = Field(..., alias="createdAt")


class ReportSectionResponse(BaseModel):
    """Individual report section in aggregated report."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    section_type: str = Field(..., alias="sectionType")
    title: str
    content: dict
    confidence_score: float = Field(..., alias="confidenceScore")
    generated_at: datetime = Field(..., alias="generatedAt")
    sources: list[dict] = Field(default_factory=list)


class FullReportResponse(BaseModel):
    """
    Complete aggregated report response

    This is the API response format for GET /trips/{id}/report
    Returns all report sections combined into a single response.
    """

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    trip_id: str = Field(..., alias="tripId")
    trip_info: TripInfoResponse = Field(..., alias="tripInfo")
    sections: dict[str, ReportSectionResponse] = Field(default_factory=dict)
    available_sections: list[str] = Field(default_factory=list, alias="availableSections")
    missing_sections: list[str] = Field(default_factory=list, alias="missingSections")
    overall_confidence: float = Field(default=0.0, alias="overallConfidence")
    generated_at: datetime = Field(..., alias="generatedAt")
    is_complete: bool = Field(default=False, alias="isComplete")


class PDFExportResponse(BaseModel):
    """Response for PDF export endpoint."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    success: bool
    pdf_url: str | None = Field(default=None, alias="pdfUrl")
    message: str | None = None


class PDFExportError(BaseModel):
    """Error response for PDF export."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    detail: str = "PDF generation failed"
    code: str = "PDF_GENERATION_ERROR"
