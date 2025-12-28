"""Health check endpoints"""

from datetime import UTC, datetime

from fastapi import APIRouter, status

from app.core.api_validation import get_api_health_summary, validate_api_keys
from app.core.config import settings

router = APIRouter(tags=["healthcheck"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns the health status of the API",
)
async def health_check() -> dict[str, str]:
    """
    Health check endpoint to verify API is running.

    Returns:
        dict: Health status information including:
            - status: Overall health status
            - timestamp: Current server timestamp
            - In development: environment, version, service name
    """
    response = {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Only expose detailed info in non-production environments
    if settings.ENVIRONMENT != "production":
        response["environment"] = settings.ENVIRONMENT
        response["version"] = settings.APP_VERSION
        response["service"] = settings.APP_NAME

    return response


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Returns readiness status (for k8s/docker healthchecks)",
)
async def readiness_check() -> dict[str, bool]:
    """
    Readiness check endpoint for container orchestration.

    Returns:
        dict: Simple ready status
    """
    return {"ready": True}


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness Check",
    description="Returns liveness status (for k8s/docker healthchecks)",
)
async def liveness_check() -> dict[str, bool]:
    """
    Liveness check endpoint for container orchestration.

    Returns:
        dict: Simple alive status
    """
    return {"alive": True}


@router.get(
    "/health/apis",
    status_code=status.HTTP_200_OK,
    summary="API Configuration Status",
    description="Returns status of external API integrations",
)
async def api_health_check() -> dict:
    """
    Check external API configuration status.

    Returns detailed information about which APIs are configured,
    which are running in degraded mode (using fallbacks), and
    which are missing.

    Returns:
        dict: API configuration status
    """
    return validate_api_keys()


@router.get(
    "/health/apis/summary",
    status_code=status.HTTP_200_OK,
    summary="API Health Summary",
    description="Returns simplified API health status",
)
async def api_health_summary() -> dict:
    """
    Get a simplified API health summary.

    Returns:
        dict: Summary with counts of configured/degraded/missing APIs
    """
    return get_api_health_summary()
