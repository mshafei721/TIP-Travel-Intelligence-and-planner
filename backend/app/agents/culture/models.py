"""
Culture Agent Pydantic Models

Defines input and output data structures for the Culture Agent.
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator

from ..interfaces import AgentResult


class CultureAgentInput(BaseModel):
    """Input model for Culture Agent."""

    trip_id: str = Field(..., description="Unique trip identifier")
    destination_country: str = Field(..., description="Country name or ISO code")
    destination_city: str | None = Field(None, description="Primary destination city")
    departure_date: date = Field(..., description="Trip departure date")
    return_date: date = Field(..., description="Trip return date")
    traveler_nationality: str | None = Field(None, description="Traveler's nationality")

    @field_validator("destination_country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Ensure country name is not empty."""
        if not v or not v.strip():
            raise ValueError("Destination country cannot be empty")
        return v.strip()

    @field_validator("return_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Ensure return date is after departure date."""
        if "departure_date" in info.data and v < info.data["departure_date"]:
            raise ValueError("Return date must be after departure date")
        return v


class CommonPhrase(BaseModel):
    """A common phrase with translation."""

    english: str = Field(..., description="English phrase")
    local: str = Field(..., description="Local language phrase")
    pronunciation: str | None = Field(None, description="Pronunciation guide")
    context: str | None = Field(None, description="When to use this phrase")


class DressCodeInfo(BaseModel):
    """Dress code information for different contexts."""

    casual: str = Field(..., description="Casual dress guidelines")
    formal: str | None = Field(None, description="Formal dress guidelines")
    religious_sites: str | None = Field(None, description="Dress code for religious sites")
    beaches: str | None = Field(None, description="Beach/swimwear guidelines")
    general_notes: str | None = Field(None, description="General dress code notes")


class ReligiousConsideration(BaseModel):
    """Religious consideration or guideline."""

    topic: str = Field(..., description="Topic area (e.g., 'Prayer times', 'Alcohol')")
    guideline: str = Field(..., description="What travelers should know")
    severity: str = Field(..., description="Importance level (info/advisory/critical)")


class CulturalTaboo(BaseModel):
    """Cultural taboo or sensitive topic."""

    behavior: str = Field(..., description="The behavior or topic")
    explanation: str = Field(..., description="Why it's taboo")
    alternative: str | None = Field(None, description="What to do instead")
    severity: str = Field(..., description="Severity level (minor/moderate/major)")


class EtiquetteRule(BaseModel):
    """Cultural etiquette rule."""

    category: str = Field(
        ..., description="Category (e.g., 'Greetings', 'Dining', 'Communication')"
    )
    rule: str = Field(..., description="The etiquette rule")
    do: list[str] = Field(default_factory=list, description="Things to do")
    dont: list[str] = Field(default_factory=list, description="Things to avoid")


class CultureAgentOutput(AgentResult):
    """Output model for Culture Agent."""

    # AgentResult requires data field - we provide it as empty since we use specific fields
    data: dict = Field(default_factory=dict, description="Legacy field for compatibility")

    # Greetings & Communication
    greeting_customs: list[str] = Field(..., description="How people greet each other")
    communication_style: str = Field(
        ..., description="Communication norms (direct/indirect, formal/informal)"
    )
    body_language_notes: list[str] = Field(
        default_factory=list, description="Important body language considerations"
    )

    # Dress Code
    dress_code: DressCodeInfo = Field(..., description="Dress code information")

    # Religious Considerations
    primary_religion: str | None = Field(None, description="Primary religion(s)")
    religious_considerations: list[ReligiousConsideration] = Field(
        default_factory=list, description="Religious guidelines for travelers"
    )

    # Cultural Taboos
    taboos: list[CulturalTaboo] = Field(
        default_factory=list, description="Cultural taboos and sensitivities"
    )

    # Etiquette
    dining_etiquette: list[EtiquetteRule] = Field(
        default_factory=list, description="Dining etiquette rules"
    )
    social_etiquette: list[EtiquetteRule] = Field(
        default_factory=list, description="Social etiquette rules"
    )
    business_etiquette: list[EtiquetteRule] | None = Field(
        None, description="Business etiquette rules"
    )

    # Language & Phrases
    official_languages: list[str] = Field(..., description="Official language(s)")
    common_phrases: list[CommonPhrase] = Field(..., description="Essential phrases for travelers")
    language_tips: list[str] = Field(
        default_factory=list, description="Tips for communicating with locals"
    )

    # Gift Giving
    gift_giving_customs: list[str] | None = Field(None, description="Gift giving etiquette")

    # Photography & Privacy
    photography_etiquette: list[str] = Field(
        default_factory=list, description="Photography guidelines and restrictions"
    )

    # Time & Punctuality
    time_culture: str | None = Field(None, description="Attitudes toward time and punctuality")

    # Additional Tips
    cultural_sensitivity_tips: list[str] = Field(
        ..., description="General cultural sensitivity advice"
    )
    respect_local_customs_summary: str = Field(
        ..., description="Overall summary of respecting local customs"
    )
