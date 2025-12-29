"""
Attractions Agent Tools

Provides OpenTripMap API integration for fetching tourist attractions data.

Official API Documentation: https://dev.opentripmap.org/docs
OpenAPI Spec: https://dev.opentripmap.org/openapi.en.json
"""

import logging
import os
from typing import Any

import httpx
from crewai.tools import tool

logger = logging.getLogger(__name__)


class OpenTripMapClient:
    """
    Client for OpenTripMap API.

    API Base URL: https://api.opentripmap.com/0.1/{lang}/places/
    Authentication: API key passed as 'apikey' query parameter

    Endpoints:
    - GET /{lang}/places/geoname - Get coordinates for a place name
    - GET /{lang}/places/radius - Search places within radius
    - GET /{lang}/places/bbox - Search places in bounding box
    - GET /{lang}/places/xid/{xid} - Get detailed place information
    - GET /{lang}/places/autosuggest - Autocomplete search
    """

    BASE_URL = "https://api.opentripmap.com/0.1"
    DEFAULT_LANG = "en"

    def __init__(self, api_key: str | None = None, lang: str = "en"):
        """
        Initialize OpenTripMap client.

        Args:
            api_key: OpenTripMap API key (or from OPENTRIPMAP_API_KEY env var)
            lang: Language code (en or ru, default: en)
        """
        self.api_key = api_key or os.getenv("OPENTRIPMAP_API_KEY")
        if not self.api_key:
            raise ValueError("OPENTRIPMAP_API_KEY not found in environment variables")
        self.lang = lang

    async def get_location_coordinates(
        self, name: str, country: str | None = None
    ) -> dict[str, Any] | None:
        """
        Get coordinates for a place name using the geoname endpoint.

        API Endpoint: GET /{lang}/places/geoname

        Args:
            name: Place name to search (required)
            country: ISO-3166 2-letter country code (optional)

        Returns:
            dict with name, country, lon, lat, timezone, population or None if not found
        """
        url = f"{self.BASE_URL}/{self.lang}/places/geoname"
        params = {"name": name, "apikey": self.api_key}

        if country:
            params["country"] = country

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data and "lat" in data and "lon" in data:
                    return {
                        "name": data.get("name", name),
                        "country": data.get("country", ""),
                        "lat": float(data["lat"]),
                        "lon": float(data["lon"]),
                        "timezone": data.get("timezone", ""),
                        "population": data.get("population", 0),
                    }
                return None

        except httpx.HTTPStatusError as e:
            logger.warning("HTTP error fetching coordinates for %s: %s", name, e.response.status_code)
            return None
        except Exception as e:
            logger.error("Error fetching coordinates for %s: %s", name, e)
            return None

    async def get_attractions_by_radius(
        self,
        lon: float,
        lat: float,
        radius: int = 5000,
        kinds: str | None = None,
        rate: str | None = None,
        limit: int = 100,
        format: str = "json",
    ) -> list[dict[str, Any]]:
        """
        Get attractions within a radius from a point.

        API Endpoint: GET /{lang}/places/radius

        Args:
            lon: Longitude of center point (required)
            lat: Latitude of center point (required)
            radius: Search radius in meters (default: 5000m = 5km)
            kinds: Categories filter (e.g., "museums,historic,theatres_and_entertainments,
                   interesting_places,natural,cultural,religion,architecture,
                   amusements,other_hotels,foods,shops,transport")
            rate: Popularity rating filter (1/2/3 or 1h/2h/3h for user-generated ratings)
            limit: Maximum number of results (default: 100, max: 500)
            format: Response format ("json" or "geojson", default: "json")

        Returns:
            List of SimpleFeature objects with xid, name, kinds, point, osm, wikidata, dist
        """
        url = f"{self.BASE_URL}/{self.lang}/places/radius"
        params = {
            "lon": lon,
            "lat": lat,
            "radius": radius,
            "apikey": self.api_key,
            "format": format,
            "limit": limit,
        }

        if kinds:
            params["kinds"] = kinds
        if rate:
            params["rate"] = rate

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Handle both json array and geojson FeatureCollection responses
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "features" in data:
                    return data["features"]
                return []

        except httpx.HTTPStatusError as e:
            logger.warning("HTTP error in radius search: %s", e.response.status_code)
            return []
        except Exception as e:
            logger.error("Error in radius search: %s", e)
            return []

    async def get_place_details(self, xid: str) -> dict[str, Any] | None:
        """
        Get detailed information about a specific place by its OpenTripMap ID.

        API Endpoint: GET /{lang}/places/xid/{xid}

        Args:
            xid: Unique OpenTripMap object identifier (from radius/bbox search)

        Returns:
            Places object with comprehensive details including:
            - xid, name, kinds, rate, point, bbox
            - image, preview (images)
            - wikipedia, wikipedia_extracts (Wikipedia info)
            - voyage (WikiVoyage info)
            - sources (geometry and attribute sources)
            - url, otm (web links)
            - info (additional structured data)
        """
        url = f"{self.BASE_URL}/{self.lang}/places/xid/{xid}"
        params = {"apikey": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.warning("HTTP error fetching place details for %s: %s", xid, e.response.status_code)
            return None
        except Exception as e:
            logger.error("Error fetching place details for %s: %s", xid, e)
            return None

    async def autosuggest(
        self,
        name: str,
        lon: float,
        lat: float,
        radius: int = 50000,
        kinds: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Autocomplete search for place names with location context.

        API Endpoint: GET /{lang}/places/autosuggest

        Args:
            name: Search term (minimum 3 characters required)
            lon: Longitude for location context (required)
            lat: Latitude for location context (required)
            radius: Search radius in meters (default: 50000m = 50km)
            kinds: Categories filter (optional)
            limit: Maximum number of results (default: 10)

        Returns:
            List of SimpleSuggestFeature objects with highlighted_name
        """
        if len(name) < 3:
            return []

        url = f"{self.BASE_URL}/{self.lang}/places/autosuggest"
        params = {
            "name": name,
            "lon": lon,
            "lat": lat,
            "radius": radius,
            "apikey": self.api_key,
            "limit": limit,
        }

        if kinds:
            params["kinds"] = kinds

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if isinstance(data, list):
                    return data
                return []

        except httpx.HTTPStatusError as e:
            logger.warning("HTTP error in autosuggest: %s", e.response.status_code)
            return []
        except Exception as e:
            logger.error("Error in autosuggest: %s", e)
            return []


# ============================================================================
# CrewAI Tools
# ============================================================================


@tool("Get City Coordinates")
def get_city_coordinates_tool(city_name: str, country_code: str | None = None) -> str:
    """
    Get geographic coordinates for a city name.

    Args:
        city_name: Name of the city (e.g., "Paris", "Tokyo", "New York")
        country_code: Optional ISO-3166 2-letter country code (e.g., "FR", "JP", "US")

    Returns:
        JSON string with city coordinates and metadata
    """
    import asyncio
    import json

    # Check if API key is configured
    api_key = os.getenv("OPENTRIPMAP_API_KEY")
    if not api_key:
        # Return a message that helps the AI proceed without coordinates
        return json.dumps({
            "error": "OpenTripMap API not configured",
            "message": "Cannot fetch coordinates. Please provide attraction information based on general knowledge.",
            "city_name": city_name,
            "country_code": country_code,
        })

    try:
        client = OpenTripMapClient(api_key=api_key)

        async def fetch():
            return await client.get_location_coordinates(city_name, country_code)

        result = asyncio.run(fetch())

        if result:
            return json.dumps(result, indent=2)
        return json.dumps({"error": f"City '{city_name}' not found"})
    except Exception as e:
        return json.dumps({"error": str(e), "city_name": city_name})


@tool("Search Attractions Near Location")
def search_attractions_tool(
    lon: float,
    lat: float,
    radius_km: float = 5.0,
    categories: str | None = None,
    min_rating: str | None = None,
) -> str:
    """
    Search for tourist attractions near a geographic point.

    Args:
        lon: Longitude
        lat: Latitude
        radius_km: Search radius in kilometers (default: 5km)
        categories: Comma-separated attraction categories. Options:
                   museums, historic, theatres_and_entertainments, interesting_places,
                   natural, cultural, religion, architecture, amusements, foods, shops
        min_rating: Minimum popularity rating (1/2/3 or 1h/2h/3h for high ratings)

    Returns:
        JSON string with list of attractions (xid, name, kinds, point, distance)
    """
    import asyncio
    import json

    # Check if API key is configured
    api_key = os.getenv("OPENTRIPMAP_API_KEY")
    if not api_key:
        return json.dumps({
            "error": "OpenTripMap API not configured",
            "message": "Cannot search attractions. Please provide attraction recommendations based on general knowledge.",
            "coordinates": {"lon": lon, "lat": lat},
        })

    try:
        client = OpenTripMapClient(api_key=api_key)
        radius_meters = int(radius_km * 1000)  # Convert km to meters

        async def fetch():
            return await client.get_attractions_by_radius(
                lon=lon,
                lat=lat,
                radius=radius_meters,
                kinds=categories,
                rate=min_rating,
                limit=100,
            )

        results = asyncio.run(fetch())
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "coordinates": {"lon": lon, "lat": lat}})


@tool("Get Attraction Details")
def get_attraction_details_tool(place_id: str) -> str:
    """
    Get detailed information about a specific attraction.

    Args:
        place_id: OpenTripMap place ID (xid from search results)

    Returns:
        JSON string with detailed place information including:
        - Full description and images
        - Wikipedia and WikiVoyage content
        - Opening hours, contact info
        - Exact coordinates and address
        - Sources and references
    """
    import asyncio
    import json

    # Check if API key is configured
    api_key = os.getenv("OPENTRIPMAP_API_KEY")
    if not api_key:
        return json.dumps({
            "error": "OpenTripMap API not configured",
            "message": "Cannot fetch attraction details. Please provide information based on general knowledge.",
            "place_id": place_id,
        })

    try:
        client = OpenTripMapClient(api_key=api_key)

        async def fetch():
            return await client.get_place_details(place_id)

        result = asyncio.run(fetch())

        if result:
            return json.dumps(result, indent=2)
        return json.dumps({"error": f"Place '{place_id}' not found"})
    except Exception as e:
        return json.dumps({"error": str(e), "place_id": place_id})


# ============================================================================
# Fallback Knowledge Base
# ============================================================================


def get_fallback_attractions_knowledge() -> str:
    """
    Returns general knowledge about common tourist attractions.
    Used as fallback when OpenTripMap API is unavailable.
    """
    return """
# Global Tourist Attractions Knowledge Base

## OpenTripMap API Categories

### Museums (museums)
- Art museums, science museums, history museums, specialized collections
- Examples: Louvre (Paris), British Museum (London), MET (NYC)

### Historic Sites (historic)
- Ancient ruins, castles, fortifications, archaeological sites
- Examples: Colosseum (Rome), Acropolis (Athens), Machu Picchu (Peru)

### Cultural Attractions (cultural)
- Cultural centers, monuments, memorials, significant buildings
- Examples: Taj Maaj (India), Sagrada Familia (Barcelona)

### Religious Sites (religion)
- Churches, cathedrals, mosques, temples, synagogues, shrines
- Examples: St. Peter's Basilica (Vatican), Blue Mosque (Istanbul)

### Architecture (architecture)
- Notable buildings, modern architecture, historic structures
- Examples: Eiffel Tower (Paris), Burj Khalifa (Dubai), Sydney Opera House

### Natural Attractions (natural)
- Parks, gardens, nature reserves, geological formations, waterfalls
- Examples: Grand Canyon (USA), Victoria Falls (Africa), Great Barrier Reef

### Entertainment (theatres_and_entertainments)
- Theaters, opera houses, concert halls, entertainment venues
- Examples: La Scala (Milan), Royal Opera House (London)

### Amusements (amusements)
- Theme parks, zoos, aquariums, fun attractions
- Examples: Disneyland, Universal Studios

### Interesting Places (interesting_places)
- Viewpoints, observation decks, unique locations
- Examples: Top of the Rock (NYC), The Peak (Hong Kong)

## General Visiting Tips

### Booking Best Practices
- Book major attractions 2-4 weeks in advance
- City tourist cards often save 20-40% on multiple attractions
- Skip-the-line tickets worth it for popular sites (Louvre, Vatican, etc.)

### Timing Strategies
- Visit major museums on weekdays (Tuesday-Thursday typically least crowded)
- Arrive 30 minutes before opening for popular sites
- Late afternoon entry (2-3 hours before closing) often has shorter queues

### Cost Ranges (USD equivalent)
- World-class museums: $15-$30
- Historical sites: $10-$25
- Observation decks/viewpoints: $20-$40
- Guided tours: $30-$100
- City passes (1-3 days): $50-$150

### Accessibility
- Major museums typically wheelchair accessible with advance notice
- Historic sites may have limited accessibility due to age/structure
- Contact attractions directly for specific accommodation needs

### Photography
- Most museums allow non-flash photography
- Some religious sites prohibit all photography (ask first)
- Golden hour (sunrise/sunset) best for outdoor monuments
- Respect "No Photography" signs, especially in religious/sacred spaces
"""
