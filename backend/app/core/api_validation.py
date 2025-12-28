"""
API Key Validation and Health Check Module.

Validates external API key configuration at startup and provides
health status for deployed services.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class ApiStatus(str, Enum):
    """API configuration status."""

    CONFIGURED = "configured"
    MISSING = "missing"
    DEGRADED = "degraded"  # Using fallback


@dataclass
class ApiKeyStatus:
    """Status of a single API key."""

    name: str
    status: ApiStatus
    required: bool
    fallback_available: bool
    message: str


def validate_api_keys() -> dict:
    """
    Validate all API keys and return status report.

    Returns:
        dict with overall status and per-API details
    """
    results: list[ApiKeyStatus] = []
    critical_missing = False

    # ANTHROPIC_API_KEY - CRITICAL (no fallback)
    if settings.ANTHROPIC_API_KEY:
        results.append(
            ApiKeyStatus(
                name="ANTHROPIC_API_KEY",
                status=ApiStatus.CONFIGURED,
                required=True,
                fallback_available=False,
                message="Claude AI ready for agent reasoning",
            )
        )
    else:
        critical_missing = True
        results.append(
            ApiKeyStatus(
                name="ANTHROPIC_API_KEY",
                status=ApiStatus.MISSING,
                required=True,
                fallback_available=False,
                message="CRITICAL: All AI agents will fail without this key",
            )
        )
        logger.critical(
            "ANTHROPIC_API_KEY not configured - AI agents will fail!"
        )

    # Weather APIs (either one works)
    weather_configured = bool(
        settings.WEATHERAPI_KEY or settings.VISUAL_CROSSING_API_KEY
    )
    if weather_configured:
        results.append(
            ApiKeyStatus(
                name="WEATHER_APIS",
                status=ApiStatus.CONFIGURED,
                required=False,
                fallback_available=True,
                message="Weather data available from external API",
            )
        )
    else:
        results.append(
            ApiKeyStatus(
                name="WEATHER_APIS",
                status=ApiStatus.DEGRADED,
                required=False,
                fallback_available=True,
                message="Using AI knowledge base for weather estimates",
            )
        )
        logger.warning(
            "No weather API keys configured - using AI fallback"
        )

    # Amadeus Flight API (optional, has AI fallback)
    if settings.AMADEUS_API_KEY and settings.AMADEUS_API_SECRET:
        results.append(
            ApiKeyStatus(
                name="AMADEUS_FLIGHT_API",
                status=ApiStatus.CONFIGURED,
                required=False,
                fallback_available=True,
                message="Real-time flight data available",
            )
        )
    else:
        results.append(
            ApiKeyStatus(
                name="AMADEUS_FLIGHT_API",
                status=ApiStatus.DEGRADED,
                required=False,
                fallback_available=True,
                message="Using AI knowledge base for flight estimates",
            )
        )
        logger.info(
            "Amadeus API not configured - using AI flight estimates"
        )

    # Currency API (free, no key needed)
    results.append(
        ApiKeyStatus(
            name="CURRENCY_API",
            status=ApiStatus.CONFIGURED,
            required=False,
            fallback_available=True,
            message="Free exchange rate API (no key required)",
        )
    )

    # Mapbox (optional)
    if settings.MAPBOX_ACCESS_TOKEN:
        results.append(
            ApiKeyStatus(
                name="MAPBOX_API",
                status=ApiStatus.CONFIGURED,
                required=False,
                fallback_available=False,
                message="Map visualizations available",
            )
        )
    else:
        results.append(
            ApiKeyStatus(
                name="MAPBOX_API",
                status=ApiStatus.MISSING,
                required=False,
                fallback_available=False,
                message="Map features disabled",
            )
        )

    # RapidAPI (used for various services)
    if settings.RAPIDAPI_KEY:
        results.append(
            ApiKeyStatus(
                name="RAPIDAPI_KEY",
                status=ApiStatus.CONFIGURED,
                required=False,
                fallback_available=True,
                message="RapidAPI services available",
            )
        )

    return {
        "healthy": not critical_missing,
        "critical_missing": critical_missing,
        "apis": [
            {
                "name": r.name,
                "status": r.status.value,
                "required": r.required,
                "fallback_available": r.fallback_available,
                "message": r.message,
            }
            for r in results
        ],
    }


def get_api_health_summary() -> dict:
    """
    Get a simplified health summary for the /health endpoint.

    Returns:
        dict with status counts
    """
    status = validate_api_keys()

    configured = sum(
        1 for api in status["apis"] if api["status"] == "configured"
    )
    degraded = sum(
        1 for api in status["apis"] if api["status"] == "degraded"
    )
    missing = sum(
        1 for api in status["apis"] if api["status"] == "missing"
    )

    return {
        "apis_healthy": status["healthy"],
        "configured": configured,
        "degraded": degraded,
        "missing": missing,
        "message": (
            "All critical APIs configured"
            if status["healthy"]
            else "Critical API keys missing"
        ),
    }


def startup_api_check() -> None:
    """
    Run API validation at startup and log results.

    Called from FastAPI lifespan event.
    """
    logger.info("Validating external API configuration...")

    status = validate_api_keys()

    # Log summary
    configured = sum(
        1 for api in status["apis"] if api["status"] == "configured"
    )
    degraded = sum(
        1 for api in status["apis"] if api["status"] == "degraded"
    )
    missing = sum(
        1 for api in status["apis"] if api["status"] == "missing"
    )

    logger.info(
        f"API Status: {configured} configured, {degraded} degraded, {missing} missing"
    )

    if status["critical_missing"]:
        logger.critical(
            "=" * 60 + "\n"
            "CRITICAL: Required API keys are missing!\n"
            "AI agents will fail without ANTHROPIC_API_KEY.\n"
            "Please set this environment variable.\n"
            + "=" * 60
        )
        # In production, you might want to prevent startup
        if settings.ENVIRONMENT == "production":
            logger.error(
                "Continuing with missing keys in production - "
                "agent functionality will be unavailable"
            )

    for api in status["apis"]:
        if api["status"] == "missing" and api["required"]:
            logger.error(f"  {api['name']}: {api['message']}")
        elif api["status"] == "degraded":
            logger.warning(f"  {api['name']}: {api['message']}")
        else:
            logger.debug(f"  {api['name']}: {api['message']}")
