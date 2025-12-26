"""Health check endpoints"""

from datetime import UTC, datetime

from fastapi import APIRouter, status

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
