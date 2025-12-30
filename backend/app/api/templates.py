"""Trip templates API endpoints"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import verify_jwt_token
from app.core.errors import log_and_raise_http_error
from app.core.supabase import supabase

logger = logging.getLogger(__name__)
from app.models.template import (
    CreateTripFromTemplateRequest,
    PublicTemplateResponse,
    TemplatesListResponse,
    TripTemplateCreate,
    TripTemplateResponse,
    TripTemplateUpdate,
)

router = APIRouter(prefix="/templates", tags=["templates"])


# ============================================
# Public Templates Endpoints
# ============================================


@router.get("/public", response_model=list[PublicTemplateResponse])
async def list_public_templates(
    tag: str | None = Query(None, description="Filter by tag"),
    destination: str | None = Query(None, description="Filter by destination country"),
    limit: int = Query(20, ge=1, le=100, description="Results limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """
    Browse public templates (no authentication required)

    Args:
    - tag: Filter by specific tag
    - destination: Filter by destination country
    - limit: Max results (default 20)
    - offset: Pagination offset

    Returns:
    - List of public templates ordered by use_count
    """
    try:
        query = (
            supabase.table("trip_templates")
            .select("*")
            .eq("is_public", True)
            .order("use_count", desc=True)
            .range(offset, offset + limit - 1)
        )

        response = query.execute()

        if not response.data:
            return []

        # Filter by tag if specified
        results = response.data
        if tag:
            results = [
                t for t in results if tag.lower() in [x.lower() for x in (t.get("tags") or [])]
            ]

        # Filter by destination if specified
        if destination:
            results = [
                t
                for t in results
                if any(
                    destination.lower() in (d.get("country", "").lower())
                    for d in (t.get("destinations") or [])
                )
            ]

        return results

    except Exception as e:
        log_and_raise_http_error("fetch public templates", e, "Failed to fetch public templates. Please try again.")


@router.get("/public/featured", response_model=list[PublicTemplateResponse])
async def get_featured_templates(
    limit: int = Query(6, ge=1, le=20, description="Number of featured templates"),
):
    """
    Get featured public templates (highest use_count)

    Returns:
    - Top templates sorted by use_count
    """
    try:
        response = (
            supabase.table("trip_templates")
            .select("*")
            .eq("is_public", True)
            .order("use_count", desc=True)
            .limit(limit)
            .execute()
        )

        return response.data if response.data else []

    except Exception as e:
        log_and_raise_http_error("fetch featured templates", e, "Failed to fetch featured templates. Please try again.")


@router.post("/{template_id}/clone", response_model=TripTemplateResponse)
async def clone_template(
    template_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Clone a public template to user's library

    Args:
    - template_id: UUID of the public template to clone

    Returns:
    - Cloned template (owned by user)
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch the template (must be public or owned by user)
        existing = (
            supabase.table("trip_templates")
            .select("*")
            .eq("id", template_id)
            .execute()
        )

        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        template = existing.data[0]

        # Check if user can access this template
        if not template.get("is_public") and template.get("user_id") != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Create clone with new ownership
        clone_data = {
            "user_id": user_id,
            "name": f"{template['name']} (Copy)",
            "description": template.get("description"),
            "cover_image": template.get("cover_image"),
            "is_public": False,  # Clones are private by default
            "tags": template.get("tags", []),
            "traveler_details": template.get("traveler_details"),
            "destinations": template.get("destinations"),
            "preferences": template.get("preferences"),
            "typical_duration": template.get("typical_duration"),
            "estimated_budget": template.get("estimated_budget"),
            "currency": template.get("currency", "USD"),
        }

        response = supabase.table("trip_templates").insert(clone_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clone template",
            )

        # Increment use_count on original template
        if template.get("is_public"):
            supabase.table("trip_templates").update(
                {"use_count": (template.get("use_count") or 0) + 1}
            ).eq("id", template_id).execute()

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("clone template", e, "Failed to clone template. Please try again.")


@router.get("", response_model=TemplatesListResponse)
async def list_templates(token_payload: dict = Depends(verify_jwt_token)):
    """
    List all trip templates for the authenticated user

    Returns:
    - Object with templates array for frontend compatibility
    """
    user_id = token_payload["user_id"]

    try:
        response = (
            supabase.table("trip_templates")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return {"templates": response.data if response.data else []}

    except Exception as e:
        log_and_raise_http_error("fetch templates", e, "Failed to fetch templates. Please try again.")


@router.get("/{template_id}", response_model=TripTemplateResponse)
async def get_template(template_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get a specific trip template by ID

    Args:
    - template_id: UUID of the template

    Returns:
    - Trip template details
    """
    user_id = token_payload["user_id"]

    try:
        response = (
            supabase.table("trip_templates")
            .select("*")
            .eq("id", template_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("fetch template", e, "Failed to fetch template. Please try again.")


@router.post("", response_model=TripTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: TripTemplateCreate, token_payload: dict = Depends(verify_jwt_token)
):
    """
    Create a new trip template

    Args:
    - template: TripTemplateCreate with required fields

    Returns:
    - Created trip template
    """
    user_id = token_payload["user_id"]

    try:
        # Prepare data for insertion with all new fields
        template_data = {
            "user_id": user_id,
            "name": template.name,
            "description": template.description,
            "cover_image": template.cover_image,
            "is_public": template.is_public,
            "tags": template.tags,
            "traveler_details": template.traveler_details,
            "destinations": template.destinations,
            "preferences": template.preferences,
            "typical_duration": template.typical_duration,
            "estimated_budget": float(template.estimated_budget) if template.estimated_budget else None,
            "currency": template.currency,
        }

        response = supabase.table("trip_templates").insert(template_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create template",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("create template", e, "Failed to create template. Please try again.")


@router.put("/{template_id}", response_model=TripTemplateResponse)
async def update_template(
    template_id: str,
    template: TripTemplateUpdate,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Update an existing trip template

    Args:
    - template_id: UUID of the template to update
    - template: TripTemplateUpdate with fields to update

    Returns:
    - Updated trip template
    """
    user_id = token_payload["user_id"]

    try:
        # Check template exists and belongs to user
        existing = (
            supabase.table("trip_templates")
            .select("*")
            .eq("id", template_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        # Build update dict with only provided fields
        update_data = {}
        if template.name is not None:
            update_data["name"] = template.name
        if template.description is not None:
            update_data["description"] = template.description
        if template.cover_image is not None:
            update_data["cover_image"] = template.cover_image
        if template.is_public is not None:
            update_data["is_public"] = template.is_public
        if template.tags is not None:
            update_data["tags"] = template.tags
        if template.traveler_details is not None:
            update_data["traveler_details"] = template.traveler_details
        if template.destinations is not None:
            update_data["destinations"] = template.destinations
        if template.preferences is not None:
            update_data["preferences"] = template.preferences
        if template.typical_duration is not None:
            update_data["typical_duration"] = template.typical_duration
        if template.estimated_budget is not None:
            update_data["estimated_budget"] = float(template.estimated_budget)
        if template.currency is not None:
            update_data["currency"] = template.currency

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        response = (
            supabase.table("trip_templates")
            .update(update_data)
            .eq("id", template_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update template",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("update template", e, "Failed to update template. Please try again.")


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Delete a trip template

    Args:
    - template_id: UUID of the template to delete

    Returns:
    - 204 No Content on success
    """
    user_id = token_payload["user_id"]

    try:
        # Check template exists and belongs to user
        existing = (
            supabase.table("trip_templates")
            .select("id")
            .eq("id", template_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        response = (
            supabase.table("trip_templates")
            .delete()
            .eq("id", template_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete template",
            )

        return

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("delete template", e, "Failed to delete template. Please try again.")
