"""Profile and statistics API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.supabase import supabase
from app.core.auth import verify_jwt_token
from app.models.profile import (
    UserProfileUpdate,
    TravelerProfileCreate,
    TravelerProfileUpdate,
    UserPreferences,
    AccountDeletionRequest
)
from datetime import date

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/statistics")
async def get_statistics(
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get user travel statistics

    Aggregates data from trips to calculate:
    - Total trips created
    - Unique countries visited (from completed trips)
    - Unique destinations explored (from completed trips)
    - Active trips (draft, pending, processing statuses)

    Returns:
    - statistics: Object with totalTrips, countriesVisited, destinationsExplored, activeTrips
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch all trips for user
        response = supabase.table("trips").select(
            "id, status, destinations"
        ).eq("user_id", user_id).execute()

        trips = response.data if response.data else []

        # Calculate statistics
        total_trips = len(trips)
        active_trips = len([t for t in trips if t["status"] in ["draft", "pending", "processing"]])

        # Count unique countries and destinations from completed trips
        completed_trips = [t for t in trips if t["status"] == "completed"]
        countries = set()
        destinations = set()

        for trip in completed_trips:
            if trip.get("destinations"):
                for dest in trip["destinations"]:
                    country = dest.get("country")
                    city = dest.get("city")
                    if country:
                        countries.add(country)
                    if city and country:
                        destinations.add(f"{city}, {country}")

        statistics = {
            "totalTrips": total_trips,
            "countriesVisited": len(countries),
            "destinationsExplored": len(destinations),
            "activeTrips": active_trips
        }

        return {"statistics": statistics}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate statistics: {str(e)}"
        )


@router.get("")
async def get_profile(
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get complete user profile

    Returns:
    - user: User profile from user_profiles table
    - travelerProfile: Traveler preferences from traveler_profiles table (if exists)
    - notificationSettings: Notification preferences (placeholder for now)
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch user profile
        user_response = supabase.table("user_profiles").select("*").eq(
            "id", user_id
        ).single().execute()

        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        user_profile = user_response.data

        # Fetch traveler profile (optional)
        traveler_response = supabase.table("traveler_profiles").select("*").eq(
            "user_id", user_id
        ).maybe_single().execute()

        traveler_profile = traveler_response.data if traveler_response.data else None

        # Notification settings (placeholder - will be implemented in user settings section)
        notification_settings = {
            "deletionReminders": True,
            "reportCompletion": True,
            "productUpdates": False
        }

        return {
            "user": user_profile,
            "travelerProfile": traveler_profile,
            "notificationSettings": notification_settings
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )


@router.put("")
async def update_profile(
    profile_update: UserProfileUpdate,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Update user profile

    Updates display_name and/or avatar_url in user_profiles table

    Args:
    - profile_update: UserProfileUpdate with optional display_name and avatar_url

    Returns:
    - Updated user profile
    """
    user_id = token_payload["user_id"]

    # Build update dict with only provided fields
    update_data = {}
    if profile_update.display_name is not None:
        update_data["display_name"] = profile_update.display_name
    if profile_update.avatar_url is not None:
        update_data["avatar_url"] = profile_update.avatar_url

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    try:
        response = supabase.table("user_profiles").update(update_data).eq(
            "id", user_id
        ).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/traveler")
async def get_traveler_profile(
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get traveler profile

    Returns traveler profile from traveler_profiles table if it exists

    Returns:
    - Traveler profile or null if not yet created
    """
    user_id = token_payload["user_id"]

    try:
        response = supabase.table("traveler_profiles").select("*").eq(
            "user_id", user_id
        ).maybe_single().execute()

        return response.data if response.data else None

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch traveler profile: {str(e)}"
        )


@router.put("/traveler")
async def update_traveler_profile(
    traveler_update: TravelerProfileUpdate,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Create or update traveler profile

    Creates a new traveler profile if one doesn't exist, otherwise updates existing

    Args:
    - traveler_update: TravelerProfileUpdate with optional fields

    Returns:
    - Created or updated traveler profile
    """
    user_id = token_payload["user_id"]

    try:
        # Check if traveler profile exists
        existing = supabase.table("traveler_profiles").select("*").eq(
            "user_id", user_id
        ).maybe_single().execute()

        # Build update dict with only provided fields
        update_data = {}
        if traveler_update.nationality is not None:
            update_data["nationality"] = traveler_update.nationality
        if traveler_update.residency_country is not None:
            update_data["residency_country"] = traveler_update.residency_country
        if traveler_update.residency_status is not None:
            update_data["residency_status"] = traveler_update.residency_status
        if traveler_update.date_of_birth is not None:
            update_data["date_of_birth"] = traveler_update.date_of_birth.isoformat()
        if traveler_update.travel_style is not None:
            update_data["travel_style"] = traveler_update.travel_style.value
        if traveler_update.dietary_restrictions is not None:
            update_data["dietary_restrictions"] = traveler_update.dietary_restrictions
        if traveler_update.accessibility_needs is not None:
            update_data["accessibility_needs"] = traveler_update.accessibility_needs

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        if existing.data:
            # Update existing profile
            response = supabase.table("traveler_profiles").update(update_data).eq(
                "user_id", user_id
            ).execute()
        else:
            # Create new profile - need all required fields
            if not all(key in update_data for key in ["nationality", "residency_country", "residency_status"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Creating traveler profile requires nationality, residency_country, and residency_status"
                )

            update_data["user_id"] = user_id
            if "travel_style" not in update_data:
                update_data["travel_style"] = "balanced"
            if "dietary_restrictions" not in update_data:
                update_data["dietary_restrictions"] = []

            response = supabase.table("traveler_profiles").insert(update_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or update traveler profile"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update traveler profile: {str(e)}"
        )


@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Update user preferences

    Updates preferences stored in user_profiles.preferences JSONB field

    Args:
    - preferences: UserPreferences with notification, language, currency, and unit settings

    Returns:
    - Updated user profile with new preferences
    """
    user_id = token_payload["user_id"]

    try:
        # Convert Pydantic model to dict for JSONB storage
        preferences_dict = preferences.model_dump()

        response = supabase.table("user_profiles").update({
            "preferences": preferences_dict
        }).eq("id", user_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.delete("")
async def delete_account(
    deletion_request: AccountDeletionRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Delete user account

    Permanently deletes the user's account and all associated data.
    Requires confirmation text "DELETE MY ACCOUNT" to proceed.

    Due to CASCADE delete constraints, this will automatically delete:
    - user_profiles
    - traveler_profiles
    - trips
    - agent_jobs
    - report_sections
    - notifications
    - deletion_schedule entries

    Args:
    - deletion_request: AccountDeletionRequest with confirmation text

    Returns:
    - Success message
    """
    user_id = token_payload["user_id"]

    try:
        # Delete from user_profiles table
        # This will CASCADE delete all related data due to foreign key constraints
        response = supabase.table("user_profiles").delete().eq(
            "id", user_id
        ).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        return {
            "message": "Account deleted successfully",
            "user_id": user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
