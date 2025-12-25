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
