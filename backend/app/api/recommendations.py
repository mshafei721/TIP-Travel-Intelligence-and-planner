"""Recommendations API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.core.auth import verify_jwt_token
from app.core.config import settings
from app.services.recommendations import get_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
async def list_recommendations(
    limit: int = Query(3, ge=1, le=10, description="Number of recommendations"),
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get personalized destination recommendations

    Query Parameters:
    - limit: Number of recommendations to return (1-10, default 3)

    Returns:
    - recommendations: List of recommended destinations with reasons
    """
    # Check feature flag
    if not settings.FEATURE_RECOMMENDATIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendations feature is currently disabled"
        )

    user_id = token_payload["user_id"]

    try:
        recommendations = get_recommendations(user_id, limit)

        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
