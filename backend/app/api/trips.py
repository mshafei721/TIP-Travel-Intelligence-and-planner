"""Trips API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from datetime import datetime, date
from app.core.supabase import supabase
from app.core.auth import verify_jwt_token
from app.core.config import settings

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("")
async def list_trips(
    status_filter: Optional[str] = Query(None, description="Filter by trip status"),
    limit: int = Query(20, ge=1, le=100, description="Number of trips to return"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    List trips for the authenticated user

    Query Parameters:
    - status: Filter by trip status (draft, pending, processing, completed, failed)
    - limit: Number of trips to return (1-100, default 20)
    - cursor: Pagination cursor for next page

    Returns:
    - items: List of trip summaries
    - nextCursor: Cursor for next page (if more results exist)
    """
    user_id = token_payload["user_id"]

    try:
        # Build query
        query = supabase.table("trips").select(
            "id, created_at, updated_at, status, trip_details, destinations"
        ).eq("user_id", user_id).order("created_at", desc=True).limit(limit)

        # Apply status filter if provided
        if status_filter:
            query = query.eq("status", status_filter)

        # Execute query
        response = query.execute()

        if not response.data:
            return {"items": [], "nextCursor": None}

        # Transform to TripListItem format
        items = []
        for trip in response.data:
            # Extract destination from first destination in array
            destination_name = "Unknown"
            if trip.get("destinations") and len(trip["destinations"]) > 0:
                first_dest = trip["destinations"][0]
                destination_name = f"{first_dest.get('city', '')}, {first_dest.get('country', '')}".strip(", ")

            # Extract dates from trip_details
            trip_details = trip.get("trip_details", {})
            start_date = trip_details.get("departureDate", "")
            end_date = trip_details.get("returnDate", "")

            # Determine display status
            if trip["status"] == "completed":
                display_status = "completed"
            elif trip["status"] in ["draft", "pending", "processing"]:
                # Check if trip is in future or past
                if start_date:
                    try:
                        departure = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                        if departure.date() > date.today():
                            display_status = "upcoming"
                        elif end_date:
                            return_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                            if return_date.date() >= date.today():
                                display_status = "in-progress"
                            else:
                                display_status = "completed"
                        else:
                            display_status = "in-progress"
                    except (ValueError, AttributeError):
                        display_status = "upcoming"
                else:
                    display_status = "upcoming"
            else:
                display_status = "completed"

            items.append({
                "id": trip["id"],
                "destination": destination_name,
                "startDate": start_date,
                "endDate": end_date,
                "status": display_status,
                "createdAt": trip["created_at"],
                "deletionDate": trip.get("auto_delete_at", "")
            })

        # Determine if there are more results (simple pagination)
        next_cursor = None
        if len(items) == limit:
            # There might be more results
            next_cursor = items[-1]["createdAt"]

        return {
            "items": items,
            "nextCursor": next_cursor
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trips: {str(e)}"
        )


@router.get("/{trip_id}")
async def get_trip(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get detailed trip information

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - Complete trip object with all fields
    """
    user_id = token_payload["user_id"]

    try:
        response = supabase.table("trips").select("*").eq(
            "id", trip_id
        ).eq("user_id", user_id).single().execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trip: {str(e)}"
        )
