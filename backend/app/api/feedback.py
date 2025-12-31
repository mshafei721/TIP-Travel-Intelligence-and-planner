"""Feedback API endpoints for bug reports and feature requests"""

import logging
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from app.core.auth import optional_jwt_token
from app.core.errors import log_and_raise_http_error
from app.core.supabase import supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackType(str, Enum):
    """Types of feedback"""

    BUG = "bug"
    FEATURE = "feature"


class FeedbackCreate(BaseModel):
    """Schema for creating feedback"""

    type: FeedbackType = Field(description="Type of feedback: bug or feature")
    title: str = Field(..., min_length=1, max_length=200, description="Brief title")
    description: str = Field(
        ..., min_length=10, max_length=5000, description="Detailed description"
    )
    email: Optional[EmailStr] = Field(
        None, description="Email for follow-up (optional)"
    )
    route: Optional[str] = Field(None, description="Current route when submitted")
    app_release: Optional[str] = Field(None, description="Application version/release")
    browser: Optional[str] = Field(None, description="Browser user agent")
    posthog_id: Optional[str] = Field(None, description="PostHog distinct ID")
    sentry_event_id: Optional[str] = Field(
        None, description="Sentry event ID if error-related"
    )

    model_config = {"json_schema_extra": {"example": {"type": "bug", "title": "Trip creation fails on step 2", "description": "After selecting dates, the Next button spins forever.", "route": "/trip/create", "app_release": "1.0.0"}}}


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""

    id: str
    type: FeedbackType
    title: str
    description: str
    email: Optional[str] = None
    route: Optional[str] = None
    app_release: Optional[str] = None
    status: str = "new"
    created_at: datetime
    user_id: Optional[str] = None


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: FeedbackCreate,
    request: Request,
    token_payload: Optional[dict] = Depends(optional_jwt_token),
):
    """
    Submit user feedback (bug report or feature request)

    This endpoint accepts feedback from authenticated and anonymous users.
    Rate-limited to prevent spam.

    Args:
        feedback: FeedbackCreate with type, title, description, and optional context

    Returns:
        Created feedback record
    """
    try:
        # Get user ID if authenticated
        user_id = token_payload.get("user_id") if token_payload else None

        # Get client IP for spam prevention
        client_ip = request.client.host if request.client else None

        # Prepare data for insertion
        feedback_data = {
            "type": feedback.type.value,
            "title": feedback.title,
            "description": feedback.description,
            "email": feedback.email,
            "route": feedback.route,
            "app_release": feedback.app_release,
            "browser": (
                feedback.browser[:500] if feedback.browser else None
            ),  # Truncate UA
            "posthog_id": feedback.posthog_id,
            "sentry_event_id": feedback.sentry_event_id,
            "user_id": user_id,
            "ip_address": client_ip,
            "status": "new",
        }

        # Insert into database
        response = supabase.table("user_feedback").insert(feedback_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit feedback",
            )

        feedback_record = response.data[0]

        logger.info(
            "Feedback submitted",
            extra={
                "feedback_id": feedback_record["id"],
                "type": feedback.type.value,
                "user_id": user_id,
                "has_sentry_id": bool(feedback.sentry_event_id),
            },
        )

        return FeedbackResponse(
            id=feedback_record["id"],
            type=FeedbackType(feedback_record["type"]),
            title=feedback_record["title"],
            description=feedback_record["description"],
            email=feedback_record.get("email"),
            route=feedback_record.get("route"),
            app_release=feedback_record.get("app_release"),
            status=feedback_record["status"],
            created_at=feedback_record["created_at"],
            user_id=feedback_record.get("user_id"),
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error(
            "submit feedback", e, "Failed to submit feedback. Please try again."
        )


@router.get("")
async def list_feedback(
    status_filter: Optional[str] = None,
    type_filter: Optional[FeedbackType] = None,
    limit: int = 50,
    offset: int = 0,
    token_payload: dict = Depends(optional_jwt_token),
):
    """
    List feedback submissions (admin only in production)

    For now, allows listing feedback for debugging purposes.
    Should be restricted to admin users in production.

    Args:
        status_filter: Filter by status (new, in_progress, resolved, closed)
        type_filter: Filter by type (bug, feature)
        limit: Number of records to return (max 100)
        offset: Pagination offset

    Returns:
        List of feedback records
    """
    try:
        # Clamp limit
        limit = min(limit, 100)

        # Build query
        query = supabase.table("user_feedback").select("*")

        if status_filter:
            query = query.eq("status", status_filter)

        if type_filter:
            query = query.eq("type", type_filter.value)

        # Order by newest first and paginate
        response = (
            query.order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return {"feedback": response.data if response.data else [], "count": len(response.data) if response.data else 0, "offset": offset, "limit": limit}

    except Exception as e:
        log_and_raise_http_error(
            "list feedback", e, "Failed to list feedback. Please try again."
        )


@router.get("/{feedback_id}")
async def get_feedback(
    feedback_id: str,
    token_payload: Optional[dict] = Depends(optional_jwt_token),
):
    """
    Get a specific feedback record

    Args:
        feedback_id: UUID of the feedback record

    Returns:
        Feedback record if found
    """
    try:
        response = (
            supabase.table("user_feedback")
            .select("*")
            .eq("id", feedback_id)
            .maybe_single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found",
            )

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error(
            "get feedback", e, "Failed to get feedback. Please try again."
        )


@router.patch("/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: str,
    new_status: str,
    token_payload: dict = Depends(optional_jwt_token),
):
    """
    Update feedback status (admin only in production)

    Args:
        feedback_id: UUID of the feedback record
        new_status: New status (new, in_progress, resolved, closed)

    Returns:
        Updated feedback record
    """
    valid_statuses = {"new", "in_progress", "resolved", "closed"}

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    try:
        response = (
            supabase.table("user_feedback")
            .update({"status": new_status})
            .eq("id", feedback_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error(
            "update feedback status", e, "Failed to update feedback. Please try again."
        )
