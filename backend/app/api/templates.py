"""Trip templates API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import verify_jwt_token
from app.core.supabase import supabase
from app.models.template import (
    TripTemplateCreate,
    TripTemplateResponse,
    TripTemplateUpdate,
)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TripTemplateResponse])
async def list_templates(token_payload: dict = Depends(verify_jwt_token)):
    """
    List all trip templates for the authenticated user

    Returns:
    - List of trip templates ordered by created_at descending
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

        return response.data if response.data else []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch templates: {str(e)}",
        )


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch template: {str(e)}",
        )


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
        # Prepare data for insertion
        template_data = {
            "user_id": user_id,
            "name": template.name,
            "description": template.description,
            "traveler_details": template.traveler_details,
            "destinations": template.destinations,
            "preferences": template.preferences,
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}",
        )


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
        if template.traveler_details is not None:
            update_data["traveler_details"] = template.traveler_details
        if template.destinations is not None:
            update_data["destinations"] = template.destinations
        if template.preferences is not None:
            update_data["preferences"] = template.preferences

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}",
        )


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}",
        )
