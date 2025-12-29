"""
Agent Configuration

Configuration schema for AI agents using Pydantic for validation.
Supports multiple agent types including visa, country, weather, culture, and food agents.
"""

import os

from pydantic import BaseModel, Field

# Default model - can be overridden via ANTHROPIC_MODEL environment variable
# Options: claude-sonnet-4-20250514, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022
DEFAULT_LLM_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")


class AgentConfig(BaseModel):
    """
    Configuration for AI agents

    Attributes:
        agent_type: Type identifier for the agent (visa, country, weather, etc.)
        name: Human-readable agent name
        description: Agent purpose and capabilities
        version: Agent version for tracking
        llm_model: Claude model to use (default from ANTHROPIC_MODEL env or claude-sonnet-4-20250514)
        temperature: LLM temperature for randomness (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in LLM response
        verbose: Enable verbose logging for debugging
        timeout_seconds: Maximum execution time before timeout
    """

    agent_type: str = Field(
        ..., description="Agent type identifier (visa, country, weather, culture, food, etc.)"
    )

    name: str | None = Field(None, description="Human-readable agent name")

    description: str | None = Field(None, description="Agent purpose and capabilities")

    version: str | None = Field(None, description="Agent version")

    llm_model: str = Field(
        default=DEFAULT_LLM_MODEL,
        description="Claude model ID to use for agent execution",
    )

    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="LLM temperature (0.0 = factual, 1.0 = creative)",
    )

    max_tokens: int = Field(
        default=4000, ge=100, le=200000, description="Maximum tokens in LLM response"
    )

    verbose: bool = Field(default=True, description="Enable verbose logging and debugging output")

    timeout_seconds: int | None = Field(
        default=300,
        ge=10,
        le=1800,
        description="Maximum execution time in seconds (default: 5 minutes)",
    )

    class Config:
        """Pydantic config"""

        frozen = False  # Allow modification after creation
        validate_assignment = True  # Validate on field assignment
