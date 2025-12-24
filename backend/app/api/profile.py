"""Profile and statistics API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.supabase import supabase
from app.core.auth import verify_jwt_token
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
