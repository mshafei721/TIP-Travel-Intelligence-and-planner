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
            - environment: Current environment (development/production)
            - version: API version
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME,
    }


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
