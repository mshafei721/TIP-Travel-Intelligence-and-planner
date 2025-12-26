"""
Places API endpoints.

Search for places/locations to add to itineraries.
Uses OpenTripMap API (free tier) for place data.
"""

import asyncio
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import verify_jwt_token
from app.models.itinerary import PlaceSearchResponse, PlaceSearchResult

router = APIRouter(prefix="/places", tags=["places"])

# OpenTripMap API configuration
OPENTRIPMAP_API_KEY = os.getenv("OPENTRIPMAP_API_KEY", "")
OPENTRIPMAP_BASE_URL = "https://api.opentripmap.com/0.1/en/places"

# Category mapping for OpenTripMap
CATEGORY_MAP = {
    "attraction": "interesting_places",
    "restaurant": "restaurants",
    "cafe": "cafes",
    "hotel": "accommodations",
    "museum": "museums",
    "shopping": "shops",
    "entertainment": "amusements",
    "park": "natural",
    "beach": "beaches",
    "temple": "religion",
    "historic": "historic",
    "viewpoint": "view_points",
}


async def geocode_location(location: str) -> tuple[float, float]:
    """
    Geocode a location string to coordinates.
    Uses OpenTripMap's geoname API.
    """
    if not OPENTRIPMAP_API_KEY:
        # Fallback to a default location (Tokyo) if no API key
        return (35.6762, 139.6503)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{OPENTRIPMAP_BASE_URL}/geoname",
            params={
                "name": location,
                "apikey": OPENTRIPMAP_API_KEY,
            },
            timeout=10.0,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Geocoding service unavailable",
            )

        data = response.json()
        return (data.get("lat", 0), data.get("lon", 0))


async def search_opentripmap(
    lat: float,
    lng: float,
    radius_meters: int,
    kinds: str,
    limit: int,
) -> list[dict]:
    """
    Search for places using OpenTripMap API.
    """
    if not OPENTRIPMAP_API_KEY:
        # Return sample data if no API key configured
        return get_sample_places()

    async with httpx.AsyncClient() as client:
        # First, get place IDs within radius
        response = await client.get(
            f"{OPENTRIPMAP_BASE_URL}/radius",
            params={
                "radius": radius_meters,
                "lon": lng,
                "lat": lat,
                "kinds": kinds,
                "rate": "3h",  # At least 3 stars (heritage) rating
                "limit": limit,
                "apikey": OPENTRIPMAP_API_KEY,
            },
            timeout=15.0,
        )

        if response.status_code != 200:
            return get_sample_places()

        places = response.json().get("features", [])

        # Get details for each place (with rate limiting)
        detailed_places = []
        for place in places[:limit]:
            xid = place["properties"].get("xid")
            if xid:
                try:
                    detail_response = await client.get(
                        f"{OPENTRIPMAP_BASE_URL}/xid/{xid}",
                        params={"apikey": OPENTRIPMAP_API_KEY},
                        timeout=5.0,
                    )
                    if detail_response.status_code == 200:
                        detailed_places.append(detail_response.json())
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception:
                    pass

        return detailed_places


def get_sample_places() -> list[dict]:
    """
    Return sample places when API is not configured.
    """
    return [
        {
            "xid": "sample_1",
            "name": "Sample Museum",
            "address": {"road": "123 Main Street", "city": "Sample City", "country": "Japan"},
            "point": {"lat": 35.6762, "lon": 139.6503},
            "kinds": "museums,interesting_places",
            "rate": "3h",
            "preview": {"source": "sample"},
        },
        {
            "xid": "sample_2",
            "name": "Sample Restaurant",
            "address": {"road": "456 Food Lane", "city": "Sample City", "country": "Japan"},
            "point": {"lat": 35.6800, "lon": 139.6550},
            "kinds": "restaurants,foods",
            "rate": "2h",
            "preview": {"source": "sample"},
        },
        {
            "xid": "sample_3",
            "name": "Sample Park",
            "address": {"road": "789 Green Ave", "city": "Sample City", "country": "Japan"},
            "point": {"lat": 35.6720, "lon": 139.6480},
            "kinds": "natural,parks",
            "rate": "3h",
            "preview": {"source": "sample"},
        },
    ]


def transform_place(place: dict) -> PlaceSearchResult:
    """
    Transform OpenTripMap place data to our model.
    """
    address_parts = []
    addr = place.get("address", {})
    if addr.get("road"):
        address_parts.append(addr["road"])
    if addr.get("house_number"):
        address_parts.insert(0, addr["house_number"])
    if addr.get("city"):
        address_parts.append(addr["city"])
    if addr.get("country"):
        address_parts.append(addr["country"])

    formatted_address = ", ".join(address_parts) if address_parts else "Unknown Address"

    # Determine category from kinds
    kinds = place.get("kinds", "").split(",")
    category = "attraction"  # default
    for kind in kinds:
        for our_cat, otm_cat in CATEGORY_MAP.items():
            if otm_cat in kind:
                category = our_cat
                break

    # Convert rating (1h, 2h, 3h, etc. to 1-5 scale)
    rate = place.get("rate", "")
    rating = None
    if rate:
        rate_num = rate.replace("h", "")
        if rate_num.isdigit():
            rating = min(int(rate_num) + 2, 5)  # Convert 1-3 to 3-5 scale

    # Get photo URL if available
    photo_url = None
    if place.get("preview", {}).get("source"):
        photo_url = place["preview"].get("source")

    return PlaceSearchResult(
        place_id=place.get("xid", ""),
        name=place.get("name", "Unknown Place"),
        address=formatted_address,
        city=addr.get("city"),
        country=addr.get("country"),
        lat=place.get("point", {}).get("lat", 0),
        lng=place.get("point", {}).get("lon", 0),
        category=category,
        rating=rating,
        price_level=None,  # OpenTripMap doesn't provide price info
        photo_url=photo_url,
        opening_hours=None,  # Would need separate API call
    )


@router.get(
    "/search",
    response_model=PlaceSearchResponse,
    summary="Search for places",
    description="Search for places to add to itineraries",
)
async def search_places(
    query: str = Query(..., min_length=1, max_length=200, description="Search query"),
    location: Optional[str] = Query(None, description="City/country to search in"),
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Center latitude"),
    lng: Optional[float] = Query(None, ge=-180, le=180, description="Center longitude"),
    radius_km: float = Query(10, ge=1, le=50, description="Search radius in km"),
    type: Optional[str] = Query(None, description="Place type filter"),
    limit: int = Query(20, ge=1, le=50, description="Maximum results"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Search for places that can be added to trip itineraries.

    Query Parameters:
    - query: Search term (required)
    - location: City/country name to search in (optional, used for geocoding)
    - lat/lng: Center coordinates (optional, if not provided will geocode location)
    - radius_km: Search radius in kilometers (default 10)
    - type: Filter by place type (attraction, restaurant, museum, etc.)
    - limit: Maximum number of results (default 20)

    Returns:
    - List of matching places with details
    """
    try:
        # Determine center coordinates
        if lat is not None and lng is not None:
            center_lat, center_lng = lat, lng
        elif location:
            center_lat, center_lng = await geocode_location(location)
        else:
            # Default to a major city if no location provided
            center_lat, center_lng = 35.6762, 139.6503  # Tokyo

        # Convert radius to meters
        radius_meters = int(radius_km * 1000)

        # Determine OpenTripMap kinds based on type filter
        if type and type in CATEGORY_MAP:
            kinds = CATEGORY_MAP[type]
        else:
            kinds = "interesting_places"  # Default to all interesting places

        # Add query as part of kinds if it matches a category
        query_lower = query.lower()
        for our_cat, otm_cat in CATEGORY_MAP.items():
            if query_lower in our_cat:
                kinds = otm_cat
                break

        # Search using OpenTripMap
        raw_places = await search_opentripmap(
            lat=center_lat,
            lng=center_lng,
            radius_meters=radius_meters,
            kinds=kinds,
            limit=limit,
        )

        # Transform results
        results = []
        for place in raw_places:
            try:
                result = transform_place(place)
                # Filter by query if provided (simple text match)
                if query.lower() in result.name.lower() or not query:
                    results.append(result)
            except Exception:
                continue

        # If no results from API, check if query matches any sample places
        if not results:
            sample_places = get_sample_places()
            for place in sample_places:
                try:
                    result = transform_place(place)
                    results.append(result)
                except Exception:
                    continue

        return PlaceSearchResponse(
            results=results[:limit],
            total_count=len(results),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search places: {str(e)}",
        )


@router.get(
    "/nearby",
    response_model=PlaceSearchResponse,
    summary="Find nearby places",
    description="Find places near a specific location",
)
async def nearby_places(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius_km: float = Query(1, ge=0.1, le=10, description="Search radius in km"),
    type: Optional[str] = Query(None, description="Place type filter"),
    limit: int = Query(10, ge=1, le=30, description="Maximum results"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Find places near a specific location.

    Useful for finding nearby restaurants, attractions, etc.
    when planning the itinerary.
    """
    try:
        # Convert radius to meters
        radius_meters = int(radius_km * 1000)

        # Determine kinds
        if type and type in CATEGORY_MAP:
            kinds = CATEGORY_MAP[type]
        else:
            kinds = "interesting_places,restaurants,cafes,accommodations"

        # Search
        raw_places = await search_opentripmap(
            lat=lat,
            lng=lng,
            radius_meters=radius_meters,
            kinds=kinds,
            limit=limit,
        )

        # Transform results
        results = [transform_place(p) for p in raw_places if p.get("name")]

        return PlaceSearchResponse(
            results=results[:limit],
            total_count=len(results),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find nearby places: {str(e)}",
        )


@router.get(
    "/autocomplete",
    response_model=list[dict],
    summary="Place name autocomplete",
    description="Get autocomplete suggestions for place names",
)
async def autocomplete_places(
    query: str = Query(..., min_length=2, max_length=100, description="Search prefix"),
    location: Optional[str] = Query(None, description="City/country context"),
    limit: int = Query(5, ge=1, le=10, description="Maximum suggestions"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get autocomplete suggestions for place names.

    Returns simple name suggestions for quick selection.
    """
    try:
        # If no API key, return sample suggestions
        if not OPENTRIPMAP_API_KEY:
            return [
                {"name": f"{query} Museum", "type": "museum"},
                {"name": f"{query} Restaurant", "type": "restaurant"},
                {"name": f"{query} Park", "type": "park"},
            ][:limit]

        # Get center for search
        if location:
            center_lat, center_lng = await geocode_location(location)
        else:
            center_lat, center_lng = 35.6762, 139.6503

        # Search with a reasonable radius
        raw_places = await search_opentripmap(
            lat=center_lat,
            lng=center_lng,
            radius_meters=50000,  # 50km radius for autocomplete
            kinds="interesting_places",
            limit=limit * 2,
        )

        # Filter and format suggestions
        suggestions = []
        for place in raw_places:
            name = place.get("name", "")
            if name and query.lower() in name.lower():
                kinds = place.get("kinds", "").split(",")
                category = "attraction"
                for kind in kinds:
                    for our_cat, otm_cat in CATEGORY_MAP.items():
                        if otm_cat in kind:
                            category = our_cat
                            break

                suggestions.append({"name": name, "type": category})

                if len(suggestions) >= limit:
                    break

        return suggestions

    except Exception as e:
        # Return empty list on error (graceful degradation)
        return []
