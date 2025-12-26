"""
Itinerary Builder API endpoints.

CRUD operations for user-editable trip itineraries.
These endpoints manage the user's custom itinerary, which is stored
separately from the AI-generated itinerary report.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import verify_jwt_token
from app.core.supabase import supabase
from app.models.itinerary import (
    Activity,
    ActivityCreate,
    ActivityResponse,
    ActivityUpdate,
    DayPlan,
    DayPlanCreate,
    DayPlanResponse,
    DayPlanUpdate,
    Itinerary,
    ItineraryResponse,
    ItineraryUpdate,
    Location,
    PlaceSearchRequest,
    PlaceSearchResponse,
    PlaceSearchResult,
    ReorderRequest,
    ReorderResponse,
)

router = APIRouter(prefix="/trips", tags=["itinerary"])


# ============================================================================
# Helper Functions
# ============================================================================


def get_trip_itinerary(trip_data: dict) -> Optional[dict]:
    """Extract itinerary from trip data."""
    trip_details = trip_data.get("trip_details", {})
    return trip_details.get("itinerary")


def update_trip_itinerary(trip_id: str, user_id: str, itinerary: dict) -> dict:
    """Update the itinerary in trip_details JSONB field."""
    # Get current trip_details
    response = (
        supabase.table("trips")
        .select("trip_details")
        .eq("id", trip_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    # Update trip_details with new itinerary
    trip_details = response.data.get("trip_details", {}) or {}
    trip_details["itinerary"] = itinerary

    # Save back to database
    update_response = (
        supabase.table("trips")
        .update({"trip_details": trip_details})
        .eq("id", trip_id)
        .eq("user_id", user_id)
        .execute()
    )

    return update_response.data[0] if update_response.data else {}


def calculate_day_cost(day: dict) -> float:
    """Calculate total cost for a day."""
    activities = day.get("activities", [])
    return sum(a.get("cost_estimate", 0) or 0 for a in activities)


def calculate_itinerary_cost(itinerary: dict) -> float:
    """Calculate total cost for entire itinerary."""
    days = itinerary.get("days", [])
    return sum(calculate_day_cost(day) for day in days)


# ============================================================================
# Get Itinerary
# ============================================================================


@router.get(
    "/{trip_id}/itinerary",
    response_model=ItineraryResponse,
    summary="Get trip itinerary",
    description="Retrieve the user-editable itinerary for a trip",
)
async def get_itinerary(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get the user-editable itinerary for a trip.

    Returns the custom itinerary that the user has created/edited,
    or initializes one from the AI-generated report if available.
    """
    user_id = token_payload["user_id"]

    try:
        # Get trip data
        trip_response = (
            supabase.table("trips")
            .select("id, user_id, trip_details, destinations")
            .eq("id", trip_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this itinerary",
            )

        trip_data = trip_response.data
        existing_itinerary = get_trip_itinerary(trip_data)

        # Check if AI-generated itinerary exists
        ai_report_response = (
            supabase.table("report_sections")
            .select("id, generated_at")
            .eq("trip_id", trip_id)
            .eq("section_type", "itinerary")
            .limit(1)
            .execute()
        )

        has_ai_generated = bool(ai_report_response.data and len(ai_report_response.data) > 0)
        last_synced_at = None
        if ai_report_response.data:
            last_synced_at = ai_report_response.data[0].get("generated_at")

        if existing_itinerary:
            # Return existing custom itinerary
            itinerary = Itinerary(
                trip_id=trip_id,
                days=[DayPlan(**day) for day in existing_itinerary.get("days", [])],
                total_cost=existing_itinerary.get("total_cost", 0),
                currency=existing_itinerary.get("currency", "USD"),
                last_modified=datetime.fromisoformat(
                    existing_itinerary["last_modified"].replace("Z", "+00:00")
                )
                if existing_itinerary.get("last_modified")
                else datetime.utcnow(),
            )
        else:
            # Return empty itinerary
            itinerary = Itinerary(
                trip_id=trip_id,
                days=[],
                total_cost=0,
                currency="USD",
                last_modified=datetime.utcnow(),
            )

        return ItineraryResponse(
            trip_id=trip_id,
            itinerary=itinerary,
            has_ai_generated=has_ai_generated,
            last_synced_at=datetime.fromisoformat(last_synced_at.replace("Z", "+00:00"))
            if last_synced_at
            else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve itinerary: {str(e)}",
        )


# ============================================================================
# Update Full Itinerary
# ============================================================================


@router.put(
    "/{trip_id}/itinerary",
    response_model=ItineraryResponse,
    summary="Update full itinerary",
    description="Replace the entire itinerary with new data",
)
async def update_itinerary(
    trip_id: str,
    itinerary_data: ItineraryUpdate,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Update the entire itinerary for a trip.

    Replaces all existing days with the provided data.
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and user owns it
        trip_response = (
            supabase.table("trips")
            .select("id, user_id")
            .eq("id", trip_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this itinerary",
            )

        # Build itinerary object
        itinerary_dict = {
            "days": [day.model_dump(mode="json") for day in itinerary_data.days],
            "currency": itinerary_data.currency or "USD",
            "last_modified": datetime.utcnow().isoformat(),
        }

        # Calculate total cost
        itinerary_dict["total_cost"] = calculate_itinerary_cost(itinerary_dict)

        # Update trip
        update_trip_itinerary(trip_id, user_id, itinerary_dict)

        # Return updated itinerary
        itinerary = Itinerary(
            trip_id=trip_id,
            days=[DayPlan(**day) for day in itinerary_dict["days"]],
            total_cost=itinerary_dict["total_cost"],
            currency=itinerary_dict["currency"],
            last_modified=datetime.fromisoformat(itinerary_dict["last_modified"]),
        )

        return ItineraryResponse(
            trip_id=trip_id,
            itinerary=itinerary,
            has_ai_generated=False,
            last_synced_at=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update itinerary: {str(e)}",
        )


# ============================================================================
# Day Management
# ============================================================================


@router.post(
    "/{trip_id}/itinerary/days",
    response_model=DayPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a day",
    description="Add a new day to the itinerary",
)
async def add_day(
    trip_id: str,
    day_data: DayPlanCreate,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Add a new day to the itinerary.
    """
    user_id = token_payload["user_id"]

    try:
        # Get current itinerary
        trip_response = (
            supabase.table("trips")
            .select("id, user_id, trip_details")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        trip_data = trip_response.data
        existing_itinerary = get_trip_itinerary(trip_data) or {"days": [], "currency": "USD"}

        # Create new day with generated ID
        day_id = str(uuid4())
        new_day = {
            "id": day_id,
            "date": day_data.date,
            "day_number": day_data.day_number,
            "title": day_data.title,
            "notes": day_data.notes,
            "activities": [
                {"id": str(uuid4()), **activity.model_dump(mode="json")}
                for activity in day_data.activities
            ],
            "total_cost": 0,
        }

        # Calculate cost
        new_day["total_cost"] = calculate_day_cost(new_day)

        # Add to itinerary
        existing_itinerary["days"].append(new_day)
        existing_itinerary["last_modified"] = datetime.utcnow().isoformat()
        existing_itinerary["total_cost"] = calculate_itinerary_cost(existing_itinerary)

        # Save
        update_trip_itinerary(trip_id, user_id, existing_itinerary)

        return DayPlanResponse(
            success=True,
            day=DayPlan(**new_day),
            message="Day added successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add day: {str(e)}",
        )


@router.put(
    "/{trip_id}/itinerary/days/{day_id}",
    response_model=DayPlanResponse,
    summary="Update a day",
    description="Update day details (not activities)",
)
async def update_day(
    trip_id: str,
    day_id: str,
    day_data: DayPlanUpdate,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Update a day's details (date, title, notes).
    """
    user_id = token_payload["user_id"]

    try:
        # Get current itinerary
        trip_response = (
            supabase.table("trips")
            .select("id, user_id, trip_details")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        existing_itinerary = get_trip_itinerary(trip_response.data)
        if not existing_itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found"
            )

        # Find and update day
        day_found = False
        for day in existing_itinerary["days"]:
            if day["id"] == day_id:
                day_found = True
                if day_data.date is not None:
                    day["date"] = day_data.date
                if day_data.day_number is not None:
                    day["day_number"] = day_data.day_number
                if day_data.title is not None:
                    day["title"] = day_data.title
                if day_data.notes is not None:
                    day["notes"] = day_data.notes
                break

        if not day_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

        # Update timestamp
        existing_itinerary["last_modified"] = datetime.utcnow().isoformat()

        # Save
        update_trip_itinerary(trip_id, user_id, existing_itinerary)

        # Get updated day
        updated_day = next(d for d in existing_itinerary["days"] if d["id"] == day_id)

        return DayPlanResponse(
            success=True,
            day=DayPlan(**updated_day),
            message="Day updated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update day: {str(e)}",
        )


@router.delete(
    "/{trip_id}/itinerary/days/{day_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a day",
    description="Remove a day and all its activities from the itinerary",
)
async def remove_day(
    trip_id: str,
    day_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Remove a day from the itinerary.
    """
    user_id = token_payload["user_id"]

    try:
        # Get current itinerary
        trip_response = (
            supabase.table("trips")
            .select("id, user_id, trip_details")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        existing_itinerary = get_trip_itinerary(trip_response.data)
        if not existing_itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found"
            )

        # Find and remove day
        original_length = len(existing_itinerary["days"])
        existing_itinerary["days"] = [d for d in existing_itinerary["days"] if d["id"] != day_id]

        if len(existing_itinerary["days"]) == original_length:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

        # Recalculate costs and update timestamp
        existing_itinerary["total_cost"] = calculate_itinerary_cost(existing_itinerary)
        existing_itinerary["last_modified"] = datetime.utcnow().isoformat()

        # Save
        update_trip_itinerary(trip_id, user_id, existing_itinerary)

        return

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove day: {str(e)}",
        )


# ============================================================================
# Activity Management
# ============================================================================


@router.post(
    "/{trip_id}/itinerary/days/{day_id}/activities",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an activity",
    description="Add a new activity to a day",
)
async def add_activity(
    trip_id: str,
    day_id: str,
    activity_data: ActivityCreate,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Add a new activity to a specific day.
    """
    user_id = token_payload["user_id"]

    try:
        # Get current itinerary
        trip_response = (
            supabase.table("trips")
            .select("id, user_id, trip_details")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        existing_itinerary = get_trip_itinerary(trip_response.data)
        if not existing_itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found"
            )

        # Find day
        day = next((d for d in existing_itinerary["days"] if d["id"] == day_id), None)
        if not day:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Day not found")

        # Create new activity
        activity_id = str(uuid4())
        new_activity = {
            "id": activity_id,
            **activity_data.model_dump(mode="json"),
        }

        # Add to day
        if "activities" not in day:
            day["activities"] = []
        day["activities"].append(new_activity)

        # Recalculate costs
        day["total_cost"] = calculate_day_cost(day)
        existing_itinerary["total_cost"] = calculate_itinerary_cost(existing_itinerary)
        existing_itinerary["last_modified"] = datetime.utcnow().isoformat()

        # Save
        update_trip_itinerary(trip_id, user_id, existing_itinerary)

        return ActivityResponse(
            success=True,
            activity=Activity(**new_activity),
            message="Activity added successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add activity: {str(e)}",
        )


@router.put(
    "/{trip_id}/itinerary/activities/{activity_id}",
    response_model=ActivityResponse,
    summary="Update an activity",
    description="Update activity details",
)
async def update_activity(
    trip_id: str,
    activity_id: str,
    activity_data: ActivityUpdate,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Update an activity's details.
    """
    user_id = token_payload["user_id"]

    try:
        # Get current itinerary
        trip_response = (
            supabase.table("trips")
            .select("id, user_id, trip_details")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        existing_itinerary = get_trip_itinerary(trip_response.data)
        if not existing_itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found"
            )

        # Find and update activity across all days
        activity_found = False
        updated_activity = None

        for day in existing_itinerary["days"]:
            for activity in day.get("activities", []):
                if activity["id"] == activity_id:
                    activity_found = True
                    # Update fields
                    update_dict = activity_data.model_dump(exclude_none=True, mode="json")
                    for key, value in update_dict.items():
                        activity[key] = value
                    updated_activity = activity
                    break
            if activity_found:
                day["total_cost"] = calculate_day_cost(day)
                break

        if not activity_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
            )

        # Recalculate total cost and update timestamp
        existing_itinerary["total_cost"] = calculate_itinerary_cost(existing_itinerary)
        existing_itinerary["last_modified"] = datetime.utcnow().isoformat()

        # Save
        update_trip_itinerary(trip_id, user_id, existing_itinerary)

        return ActivityResponse(
            success=True,
            activity=Activity(**updated_activity),
            message="Activity updated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update activity: {str(e)}",
        )


@router.delete(
    "/{trip_id}/itinerary/activities/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an activity",
    description="Remove an activity from the itinerary",
)
async def remove_activity(
    trip_id: str,
    activity_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Remove an activity from the itinerary.
    """
    user_id = token_payload["user_id"]

    try:
        # Get current itinerary
        trip_response = (
            supabase.table("trips")
            .select("id, user_id, trip_details")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        existing_itinerary = get_trip_itinerary(trip_response.data)
        if not existing_itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found"
            )

        # Find and remove activity across all days
        activity_found = False

        for day in existing_itinerary["days"]:
            original_length = len(day.get("activities", []))
            day["activities"] = [
                a for a in day.get("activities", []) if a["id"] != activity_id
            ]
            if len(day["activities"]) < original_length:
                activity_found = True
                day["total_cost"] = calculate_day_cost(day)
                break

        if not activity_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found"
            )

        # Recalculate total cost and update timestamp
        existing_itinerary["total_cost"] = calculate_itinerary_cost(existing_itinerary)
        existing_itinerary["last_modified"] = datetime.utcnow().isoformat()

        # Save
        update_trip_itinerary(trip_id, user_id, existing_itinerary)

        return

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove activity: {str(e)}",
        )


# ============================================================================
# Reorder Activities
# ============================================================================


@router.post(
    "/{trip_id}/itinerary/reorder",
    response_model=ReorderResponse,
    summary="Reorder activities",
    description="Move activities between days or change their order",
)
async def reorder_activities(
    trip_id: str,
    reorder_data: ReorderRequest,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Reorder activities within or between days.

    Supports:
    - Moving activity to a different position in same day
    - Moving activity to a different day
    """
    user_id = token_payload["user_id"]

    try:
        # Get current itinerary
        trip_response = (
            supabase.table("trips")
            .select("id, user_id, trip_details")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        existing_itinerary = get_trip_itinerary(trip_response.data)
        if not existing_itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found"
            )

        days_by_id = {d["id"]: d for d in existing_itinerary["days"]}

        for operation in reorder_data.operations:
            activity_id = operation.activity_id
            target_day_id = operation.target_day_id
            target_position = operation.position

            # Find the activity and its current day
            source_day = None
            activity = None

            for day in existing_itinerary["days"]:
                for i, a in enumerate(day.get("activities", [])):
                    if a["id"] == activity_id:
                        source_day = day
                        activity = a
                        day["activities"].pop(i)
                        break
                if activity:
                    break

            if not activity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Activity {activity_id} not found",
                )

            # Find target day
            if target_day_id not in days_by_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Target day {target_day_id} not found",
                )

            target_day = days_by_id[target_day_id]

            # Insert at target position
            if "activities" not in target_day:
                target_day["activities"] = []

            target_position = min(target_position, len(target_day["activities"]))
            target_day["activities"].insert(target_position, activity)

            # Recalculate costs for affected days
            if source_day:
                source_day["total_cost"] = calculate_day_cost(source_day)
            target_day["total_cost"] = calculate_day_cost(target_day)

        # Update timestamp and total cost
        existing_itinerary["total_cost"] = calculate_itinerary_cost(existing_itinerary)
        existing_itinerary["last_modified"] = datetime.utcnow().isoformat()

        # Save
        update_trip_itinerary(trip_id, user_id, existing_itinerary)

        return ReorderResponse(
            success=True,
            updated_days=[DayPlan(**d) for d in existing_itinerary["days"]],
            message=f"Successfully reordered {len(reorder_data.operations)} activities",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder activities: {str(e)}",
        )


# ============================================================================
# Sync from AI-Generated Itinerary
# ============================================================================


@router.post(
    "/{trip_id}/itinerary/sync-from-ai",
    response_model=ItineraryResponse,
    summary="Sync from AI itinerary",
    description="Copy AI-generated itinerary to editable version",
)
async def sync_from_ai_itinerary(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Sync the user-editable itinerary from the AI-generated version.

    This copies the AI-generated itinerary report into the user's
    editable itinerary, overwriting any existing customizations.
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip ownership
        trip_response = (
            supabase.table("trips")
            .select("id, user_id")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # Get AI-generated itinerary
        ai_report_response = (
            supabase.table("report_sections")
            .select("content, generated_at")
            .eq("trip_id", trip_id)
            .eq("section_type", "itinerary")
            .order("generated_at", desc=True)
            .limit(1)
            .execute()
        )

        if not ai_report_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No AI-generated itinerary found. Generate the trip report first.",
            )

        ai_content = ai_report_response.data[0]["content"]
        generated_at = ai_report_response.data[0]["generated_at"]

        # Transform AI content to editable format
        days = []
        daily_plans = ai_content.get("daily_plans", [])

        for i, ai_day in enumerate(daily_plans):
            activities = []
            for ai_activity in ai_day.get("activities", []):
                activity = {
                    "id": str(uuid4()),
                    "name": ai_activity.get("name", "Unknown Activity"),
                    "type": ai_activity.get("category", "activity"),
                    "location": {
                        "name": ai_activity.get("location", {}).get("name", ""),
                        "address": ai_activity.get("location", {}).get("address"),
                        "city": ai_activity.get("location", {}).get("city"),
                        "country": ai_activity.get("location", {}).get("country"),
                        "lat": ai_activity.get("location", {}).get("lat"),
                        "lng": ai_activity.get("location", {}).get("lng"),
                    },
                    "start_time": ai_activity.get("start_time", "09:00"),
                    "end_time": ai_activity.get("end_time", "10:00"),
                    "duration_minutes": ai_activity.get("duration_minutes", 60),
                    "cost_estimate": ai_activity.get("cost_estimate"),
                    "currency": ai_activity.get("currency", "USD"),
                    "notes": ai_activity.get("notes"),
                    "priority": ai_activity.get("priority", "recommended"),
                    "booking_status": "none",
                }
                activities.append(activity)

            day = {
                "id": str(uuid4()),
                "date": ai_day.get("date", ""),
                "day_number": i + 1,
                "title": ai_day.get("title", f"Day {i + 1}"),
                "notes": ai_day.get("notes"),
                "activities": activities,
                "total_cost": sum(a.get("cost_estimate", 0) or 0 for a in activities),
            }
            days.append(day)

        # Create new itinerary
        itinerary_dict = {
            "days": days,
            "total_cost": sum(d.get("total_cost", 0) for d in days),
            "currency": ai_content.get("currency", "USD"),
            "last_modified": datetime.utcnow().isoformat(),
        }

        # Save
        update_trip_itinerary(trip_id, user_id, itinerary_dict)

        itinerary = Itinerary(
            trip_id=trip_id,
            days=[DayPlan(**d) for d in days],
            total_cost=itinerary_dict["total_cost"],
            currency=itinerary_dict["currency"],
            last_modified=datetime.fromisoformat(itinerary_dict["last_modified"]),
        )

        return ItineraryResponse(
            trip_id=trip_id,
            itinerary=itinerary,
            has_ai_generated=True,
            last_synced_at=datetime.fromisoformat(generated_at.replace("Z", "+00:00")),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync from AI itinerary: {str(e)}",
        )
