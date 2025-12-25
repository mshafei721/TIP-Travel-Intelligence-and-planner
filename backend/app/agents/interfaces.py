"""
Agent Interfaces

Pydantic models for agent input/output to ensure type safety and validation.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SourceReference(BaseModel):
    """
    Reference to external data source

    Used for source attribution and data provenance tracking.
    Ensures transparency and allows users to verify information.
    """

    url: str = Field(description="URL of the source (API endpoint, website, document)")

    title: str = Field(description="Human-readable title of the source")

    verified_at: datetime = Field(description="Timestamp when this source was last verified")

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "url": "https://www.travel.state.gov/content/travel/en/international-travel/International-Travel-Country-Information-Pages.html",
                "title": "U.S. Department of State - International Travel",
                "verified_at": "2025-12-24T10:30:00Z",
            }
        }


class AgentResult(BaseModel):
    """
    Standard result format for all agents

    This ensures consistent output structure across all agents,
    making it easy to aggregate results and display in the frontend.

    Attributes:
        agent_type: Type of agent that generated this result (visa, weather, etc.)
        trip_id: Associated trip ID
        generated_at: When this result was generated
        confidence_score: Confidence in result accuracy (0.0 = low, 1.0 = high)
        data: Agent-specific result data (structure varies by agent type)
        sources: List of sources used to generate this result
        error: Error message if agent failed (None if successful)
    """

    agent_type: str = Field(description="Type of agent (visa, country, weather, etc.)")

    trip_id: str = Field(description="Trip ID this result is associated with")

    generated_at: datetime = Field(description="Timestamp when this result was generated")

    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence score between 0.0 (low) and 1.0 (high)"
    )

    data: dict[str, Any] = Field(
        description="Agent-specific result data (structure varies by agent)"
    )

    sources: list[SourceReference] = Field(
        default_factory=list, description="List of sources used to generate this result"
    )

    error: str | None = Field(
        default=None, description="Error message if agent failed, None if successful"
    )

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        """Ensure confidence score is between 0.0 and 1.0"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {v}")
        return v

    @field_validator("agent_type")
    @classmethod
    def validate_agent_type(cls, v: str) -> str:
        """Ensure agent_type is not empty"""
        if not v or v.strip() == "":
            raise ValueError("agent_type cannot be empty")
        return v.strip().lower()

    @field_validator("trip_id")
    @classmethod
    def validate_trip_id(cls, v: str) -> str:
        """Ensure trip_id is not empty"""
        if not v or v.strip() == "":
            raise ValueError("trip_id cannot be empty")
        return v.strip()

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "agent_type": "visa",
                "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                "generated_at": "2025-12-24T10:30:00Z",
                "confidence_score": 0.95,
                "data": {
                    "visa_required": False,
                    "visa_type": "visa-free",
                    "max_stay_days": 90,
                },
                "sources": [
                    {
                        "url": "https://www.joinsherpa.com/visa-requirements",
                        "title": "Sherpa API - Visa Requirements",
                        "verified_at": "2025-12-24T10:29:00Z",
                    }
                ],
                "error": None,
            }
        }
