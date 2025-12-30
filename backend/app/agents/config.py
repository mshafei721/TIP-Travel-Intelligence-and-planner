"""
Agent Configuration

Configuration schema for AI agents using Pydantic for validation.
Supports multiple agent types including visa, country, weather, culture, and food agents.

LLM Fallback Strategy:
- Primary: Anthropic (Claude)
- Fallback 1: Google (Gemini)
- Fallback 2: OpenAI (GPT-4)
"""

import logging
import os

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# LLM Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
LLM_FALLBACK_ENABLED = os.getenv("LLM_FALLBACK_ENABLED", "true").lower() == "true"

# Default models for each provider
DEFAULT_ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
DEFAULT_GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Use the appropriate default based on provider
DEFAULT_LLM_MODEL = DEFAULT_ANTHROPIC_MODEL


def _create_anthropic_llm(temperature: float = 0.1):
    """Create Anthropic (Claude) LLM instance."""
    from langchain_anthropic import ChatAnthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    return ChatAnthropic(
        model=DEFAULT_ANTHROPIC_MODEL,
        temperature=temperature,
        timeout=60.0,
        anthropic_api_key=api_key,
    )


def _create_google_llm(temperature: float = 0.1):
    """Create Google (Gemini) LLM instance."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    return ChatGoogleGenerativeAI(
        model=DEFAULT_GOOGLE_MODEL,
        temperature=temperature,
        google_api_key=api_key,
    )


def _create_openai_llm(temperature: float = 0.1):
    """Create OpenAI (GPT) LLM instance."""
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    return ChatOpenAI(
        model=DEFAULT_OPENAI_MODEL,
        temperature=temperature,
        api_key=api_key,
    )


def get_llm(temperature: float = 0.1):
    """
    Get LLM instance with automatic fallback support.

    Fallback chain: Anthropic -> Gemini -> OpenAI

    Args:
        temperature: LLM temperature (default 0.1 for factual responses)

    Returns:
        Configured LLM instance

    Raises:
        RuntimeError: If all LLM providers fail
    """
    # Define provider chain based on primary provider
    if LLM_PROVIDER == "google":
        providers = [
            ("google", _create_google_llm),
            ("anthropic", _create_anthropic_llm),
            ("openai", _create_openai_llm),
        ]
    elif LLM_PROVIDER == "openai":
        providers = [
            ("openai", _create_openai_llm),
            ("anthropic", _create_anthropic_llm),
            ("google", _create_google_llm),
        ]
    else:  # Default: anthropic first
        providers = [
            ("anthropic", _create_anthropic_llm),
            ("google", _create_google_llm),
            ("openai", _create_openai_llm),
        ]

    errors = []

    for name, create_fn in providers:
        try:
            llm = create_fn(temperature)
            logger.info(f"LLM initialized successfully with provider: {name}")
            return llm
        except Exception as e:
            error_msg = str(e)
            errors.append((name, error_msg))
            logger.warning(f"LLM provider '{name}' failed: {error_msg}")

            # If fallback is disabled, raise immediately
            if not LLM_FALLBACK_ENABLED:
                raise RuntimeError(f"LLM provider '{name}' failed and fallback is disabled: {error_msg}")

            continue

    # All providers failed
    error_details = "; ".join([f"{name}: {err}" for name, err in errors])
    raise RuntimeError(f"All LLM providers failed: {error_details}")


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
