"""Travel history API endpoints"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import verify_jwt_token
from app.core.errors import log_and_raise_http_error
from app.core.supabase import supabase

logger = logging.getLogger(__name__)
from app.models.trips import (
    ArchiveResponse,
    CountryVisit,
    TravelHistoryEntry,
    TravelHistoryResponse,
    TravelStats,
    TravelStatsResponse,
    TravelTimelineEntry,
    TravelTimelineResponse,
    TripRatingRequest,
)

router = APIRouter(prefix="/history", tags=["history"])


# Country code mapping for world map visualization
COUNTRY_CODE_MAP = {
    "United States": "US",
    "United Kingdom": "GB",
    "France": "FR",
    "Germany": "DE",
    "Japan": "JP",
    "China": "CN",
    "Australia": "AU",
    "Canada": "CA",
    "Italy": "IT",
    "Spain": "ES",
    "Brazil": "BR",
    "India": "IN",
    "Mexico": "MX",
    "Netherlands": "NL",
    "Switzerland": "CH",
    "Thailand": "TH",
    "Singapore": "SG",
    "South Korea": "KR",
    "Portugal": "PT",
    "Greece": "GR",
    # Add more as needed
}


def get_country_code(country_name: str) -> str:
    """Get ISO 3166-1 alpha-2 code for a country name."""
    return COUNTRY_CODE_MAP.get(country_name, country_name[:2].upper())


@router.get("", response_model=TravelHistoryResponse)
async def get_travel_history(
    include_archived: bool = Query(False, description="Include archived trips"),
    limit: int = Query(50, ge=1, le=100, description="Results limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get travel history for the authenticated user.

    Returns completed trips with destination info, dates, and user ratings.

    Query Parameters:
    - include_archived: Include archived trips (default: false)
    - limit: Max results (default 50)
    - offset: Pagination offset

    Returns:
    - List of travel history entries
    - Total count for pagination
    """
    user_id = token_payload["user_id"]

    try:
        # Build query for completed trips
        query = (
            supabase.table("trips")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )

        # Filter archived trips if not included
        if not include_archived:
            query = query.or_("is_archived.is.null,is_archived.eq.false")

        response = query.execute()

        if not response.data:
            return TravelHistoryResponse(entries=[], total_count=0)

        # Transform to TravelHistoryEntry format
        entries = []
        for trip in response.data:
            destinations = trip.get("destinations", [])
            first_dest = destinations[0] if destinations else {}
            trip_details = trip.get("trip_details", {})

            entries.append(
                TravelHistoryEntry(
                    trip_id=trip["id"],
                    destination=f"{first_dest.get('city', '')}, {first_dest.get('country', '')}".strip(", "),
                    country=first_dest.get("country", "Unknown"),
                    start_date=trip_details.get("departureDate", ""),
                    end_date=trip_details.get("returnDate", ""),
                    status=trip["status"],
                    user_rating=trip.get("user_rating"),
                    user_notes=trip.get("user_notes"),
                    is_archived=trip.get("is_archived", False),
                    archived_at=trip.get("archived_at"),
                    cover_image=trip.get("cover_image_url"),
                )
            )

        # Get total count
        count_query = (
            supabase.table("trips")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("status", "completed")
        )
        if not include_archived:
            count_query = count_query.or_("is_archived.is.null,is_archived.eq.false")

        count_response = count_query.execute()
        total_count = count_response.count if count_response.count else len(entries)

        return TravelHistoryResponse(entries=entries, total_count=total_count)

    except Exception as e:
        log_and_raise_http_error("fetch travel history", e, "Failed to fetch travel history. Please try again.")


@router.get("/stats", response_model=TravelStatsResponse)
async def get_travel_stats(token_payload: dict = Depends(verify_jwt_token)):
    """
    Get aggregated travel statistics for the authenticated user.

    Returns:
    - Total trips count
    - Countries and cities visited
    - Total days traveled
    - Favorite destination
    - Most visited country
    - Country list for world map
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch all completed trips
        response = (
            supabase.table("trips")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .execute()
        )

        trips = response.data if response.data else []

        if not trips:
            return TravelStatsResponse(
                stats=TravelStats(
                    total_trips=0,
                    countries_visited=0,
                    cities_visited=0,
                    total_days_traveled=0,
                ),
                countries=[],
            )

        # Calculate statistics
        countries: dict[str, dict] = {}
        cities_set: set = set()
        total_days = 0

        for trip in trips:
            destinations = trip.get("destinations", [])
            trip_details = trip.get("trip_details", {})

            # Calculate trip duration
            start_date_str = trip_details.get("departureDate")
            end_date_str = trip_details.get("returnDate")
            if start_date_str and end_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                    end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                    trip_duration = (end_date - start_date).days
                    total_days += max(trip_duration, 1)
                except (ValueError, TypeError):
                    pass

            # Track countries and cities
            for dest in destinations:
                country = dest.get("country", "Unknown")
                city = dest.get("city", "")

                if city:
                    cities_set.add(f"{city}, {country}")

                if country not in countries:
                    countries[country] = {
                        "visit_count": 0,
                        "cities": set(),
                        "last_visited": None,
                    }

                countries[country]["visit_count"] += 1
                if city:
                    countries[country]["cities"].add(city)

                if end_date_str:
                    if (
                        countries[country]["last_visited"] is None
                        or end_date_str > countries[country]["last_visited"]
                    ):
                        countries[country]["last_visited"] = end_date_str

        # Find most visited and favorite
        most_visited_country = max(countries.keys(), key=lambda c: countries[c]["visit_count"]) if countries else None
        favorite_destination = most_visited_country  # Could be enhanced with user ratings

        # Calculate travel streak (consecutive months with travel)
        travel_streak = 0
        if trips:
            # Collect all trip months
            trip_months: set[tuple[int, int]] = set()
            for trip in trips:
                trip_details = trip.get("trip_details", {})
                start_date_str = trip_details.get("departureDate")
                if start_date_str:
                    try:
                        start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                        trip_months.add((start_date.year, start_date.month))
                    except (ValueError, TypeError):
                        pass

            # Count consecutive months from current month going back
            if trip_months:
                now = datetime.utcnow()
                current_year, current_month = now.year, now.month

                while (current_year, current_month) in trip_months:
                    travel_streak += 1
                    # Go to previous month
                    current_month -= 1
                    if current_month == 0:
                        current_month = 12
                        current_year -= 1

        # Build country visit list for world map
        country_visits = [
            CountryVisit(
                country_code=get_country_code(country),
                country_name=country,
                visit_count=data["visit_count"],
                last_visited=data["last_visited"],
                cities=list(data["cities"]),
            )
            for country, data in countries.items()
        ]

        return TravelStatsResponse(
            stats=TravelStats(
                total_trips=len(trips),
                countries_visited=len(countries),
                cities_visited=len(cities_set),
                total_days_traveled=total_days,
                favorite_destination=favorite_destination,
                most_visited_country=most_visited_country,
                travel_streak=travel_streak,
            ),
            countries=country_visits,
        )

    except Exception as e:
        log_and_raise_http_error("fetch travel stats", e, "Failed to fetch travel stats. Please try again.")


@router.get("/countries", response_model=list[CountryVisit])
async def get_countries_visited(token_payload: dict = Depends(verify_jwt_token)):
    """
    Get list of countries visited for world map visualization.

    Returns:
    - List of countries with visit count and ISO codes
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch all completed trips
        response = (
            supabase.table("trips")
            .select("destinations, trip_details")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .execute()
        )

        trips = response.data if response.data else []
        countries: dict[str, dict] = {}

        for trip in trips:
            destinations = trip.get("destinations", [])
            trip_details = trip.get("trip_details", {})
            end_date_str = trip_details.get("returnDate")

            for dest in destinations:
                country = dest.get("country", "Unknown")
                city = dest.get("city", "")

                if country not in countries:
                    countries[country] = {
                        "visit_count": 0,
                        "cities": set(),
                        "last_visited": None,
                    }

                countries[country]["visit_count"] += 1
                if city:
                    countries[country]["cities"].add(city)

                if end_date_str:
                    if (
                        countries[country]["last_visited"] is None
                        or end_date_str > countries[country]["last_visited"]
                    ):
                        countries[country]["last_visited"] = end_date_str

        return [
            CountryVisit(
                country_code=get_country_code(country),
                country_name=country,
                visit_count=data["visit_count"],
                last_visited=data["last_visited"],
                cities=list(data["cities"]),
            )
            for country, data in countries.items()
        ]

    except Exception as e:
        log_and_raise_http_error("fetch countries visited", e, "Failed to fetch countries visited. Please try again.")


@router.get("/timeline", response_model=TravelTimelineResponse)
async def get_travel_timeline(
    year: int | None = Query(None, description="Filter by year"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get travel timeline for visualization.

    Query Parameters:
    - year: Filter by specific year (optional)

    Returns:
    - Timeline entries with trip info
    - List of years with travel for filtering
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch all completed trips
        response = (
            supabase.table("trips")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .order("created_at", desc=True)
            .execute()
        )

        trips = response.data if response.data else []
        entries = []
        years_set = set()

        for trip in trips:
            destinations = trip.get("destinations", [])
            first_dest = destinations[0] if destinations else {}
            trip_details = trip.get("trip_details", {})

            start_date_str = trip_details.get("departureDate", "")
            end_date_str = trip_details.get("returnDate", "")

            # Extract year for filtering
            if start_date_str:
                try:
                    trip_year = int(start_date_str[:4])
                    years_set.add(trip_year)

                    # Filter by year if specified
                    if year and trip_year != year:
                        continue
                except (ValueError, IndexError):
                    pass

            # Calculate duration
            duration_days = 0
            if start_date_str and end_date_str:
                try:
                    start = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                    end = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                    duration_days = max((end - start).days, 1)
                except (ValueError, TypeError):
                    duration_days = 1

            destination = f"{first_dest.get('city', '')}, {first_dest.get('country', '')}".strip(", ")

            entries.append(
                TravelTimelineEntry(
                    trip_id=trip["id"],
                    title=trip.get("title", f"Trip to {destination}"),
                    destination=destination,
                    start_date=start_date_str,
                    end_date=end_date_str,
                    duration_days=duration_days,
                    status=trip["status"],
                    thumbnail=None,  # TODO: Add thumbnail support
                )
            )

        return TravelTimelineResponse(
            entries=entries,
            years=sorted(years_set, reverse=True),
        )

    except Exception as e:
        log_and_raise_http_error("fetch travel timeline", e, "Failed to fetch travel timeline. Please try again.")


# ============================================
# Archive/Unarchive Endpoints (using trips router prefix)
# ============================================


@router.post("/trips/{trip_id}/archive", response_model=ArchiveResponse)
async def archive_trip(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Archive a completed trip.

    Archived trips are hidden from the main travel history but can be restored.

    Path Parameters:
    - trip_id: UUID of the trip to archive

    Returns:
    - Archive confirmation with timestamp
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        existing_response = (
            supabase.table("trips")
            .select("id, status, is_archived")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not existing_response.data or len(existing_response.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        trip = existing_response.data[0]

        # Only completed trips can be archived
        if trip.get("status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only completed trips can be archived",
            )

        if trip.get("is_archived"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip is already archived",
            )

        # Archive the trip
        archived_at = datetime.utcnow().isoformat()
        supabase.table("trips").update({
            "is_archived": True,
            "archived_at": archived_at,
        }).eq("id", trip_id).execute()

        return ArchiveResponse(
            trip_id=trip_id,
            is_archived=True,
            archived_at=datetime.fromisoformat(archived_at),
            message="Trip archived successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("archive trip", e, "Failed to archive trip. Please try again.")


@router.post("/trips/{trip_id}/unarchive", response_model=ArchiveResponse)
async def unarchive_trip(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Restore an archived trip.

    Path Parameters:
    - trip_id: UUID of the trip to unarchive

    Returns:
    - Unarchive confirmation
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        existing_response = (
            supabase.table("trips")
            .select("id, is_archived")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not existing_response.data or len(existing_response.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        trip = existing_response.data[0]

        if not trip.get("is_archived"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip is not archived",
            )

        # Unarchive the trip
        supabase.table("trips").update({
            "is_archived": False,
            "archived_at": None,
        }).eq("id", trip_id).execute()

        return ArchiveResponse(
            trip_id=trip_id,
            is_archived=False,
            archived_at=None,
            message="Trip restored from archive successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("unarchive trip", e, "Failed to unarchive trip. Please try again.")


@router.post("/trips/{trip_id}/rate")
async def rate_trip(
    trip_id: str,
    rating_data: TripRatingRequest,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Rate a completed trip.

    Path Parameters:
    - trip_id: UUID of the trip to rate

    Request Body:
    - rating: 1-5 star rating
    - notes: Optional notes about the trip

    Returns:
    - Updated trip rating
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        existing_response = (
            supabase.table("trips")
            .select("id, status")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not existing_response.data or len(existing_response.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        trip = existing_response.data[0]

        if trip.get("status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only completed trips can be rated",
            )

        # Update rating
        update_data = {"user_rating": rating_data.rating}
        if rating_data.notes is not None:
            update_data["user_notes"] = rating_data.notes

        supabase.table("trips").update(update_data).eq("id", trip_id).execute()

        return {
            "trip_id": trip_id,
            "rating": rating_data.rating,
            "notes": rating_data.notes,
            "message": "Trip rated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("rate trip", e, "Failed to rate trip. Please try again.")
