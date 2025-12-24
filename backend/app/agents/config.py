"""
Agent Configuration

Configuration schema for AI agents using Pydantic for validation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AgentConfig(BaseModel):
    """
    Configuration for AI agents

    Attributes:
        llm_model: Claude model to use (default: claude-3-5-sonnet-20241022)
        temperature: LLM temperature for randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in LLM response
        verbose: Enable verbose logging for debugging
        timeout_seconds: Maximum execution time before timeout
    """

    llm_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Claude model ID to use for agent execution"
    )

    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="LLM temperature (0.0 = factual, 1.0 = creative)"
    )

    max_tokens: int = Field(
        default=4000,
        ge=100,
        le=200000,
        description="Maximum tokens in LLM response"
    )

    verbose: bool = Field(
        default=True,
        description="Enable verbose logging and debugging output"
    )

    timeout_seconds: Optional[int] = Field(
        default=300,
        ge=10,
        le=1800,
        description="Maximum execution time in seconds (default: 5 minutes)"
    )

    class Config:
        """Pydantic config"""
        frozen = False  # Allow modification after creation
        validate_assignment = True  # Validate on field assignment
