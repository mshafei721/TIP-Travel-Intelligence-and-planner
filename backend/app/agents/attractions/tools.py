"""
Attractions Agent Tools

Provides OpenTripMap API integration for fetching tourist attractions data.
"""

import os
from typing import Any

import httpx
from crewai.tools import tool


class OpenTripMapClient:
    """Client for OpenTripMap API."""

    BASE_URL = "https://api.opentripmap.com/0.1/en"

    def __init__(self, api_key: str | None = None):
        """Initialize OpenTripMap client."""
        self.api_key = api_key or os.getenv("OPENTRIPMAP_API_KEY")
        if not self.api_key:
            raise ValueError("OPENTRIPMAP_API_KEY not found in environment variables")

    async def get_location_coordinates(self, city_name: str) -> dict[str, Any] | None:
        """
        Get coordinates for a city using the geoname endpoint.

        Args:
            city_name: Name of the city

        Returns:
            dict with lat, lon, country, timezone info or None if not found
        """
        url = f"{self.BASE_URL}/places/geoname"
        params = {"name": city_name, "apikey": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if data and "lat" in data and "lon" in data:
                    return {
                        "lat": float(data["lat"]),
                        "lon": float(data["lon"]),
                        "country": data.get("country", ""),
                        "timezone": data.get("timezone", ""),
                        "population": data.get("population", 0),
                    }
                return None

        except Exception as e:
            print(f"Error fetching coordinates for {city_name}: {e}")
            return None

    async def get_attractions_by_radius(
        self,
        lat: float,
        lon: float,
        radius: int = 5000,
        kinds: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get attractions within a radius from a point.

        Args:
            lat: Latitude
            lon: Longitude
            radius: Radius in meters (default 5000m = 5km)
            kinds: Categories filter (e.g., "museums,historic,theatres_and_entertainments")
            limit: Maximum number of results (default 50)

        Returns:
            List of attraction dictionaries
        """
        url = f"{self.BASE_URL}/places/radius"
        params = {
            "radius": radius,
            "lat": lat,
            "lon": lon,
            "limit": limit,
            "apikey": self.api_key,
            "format": "json",
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
                elif isinstance(data, dict) and "features" in data:
                    return data["features"]
                return []

        except Exception as e:
            print(f"Error fetching attractions by radius: {e}")
            return []

    async def get_place_details(self, xid: str) -> dict[str, Any] | None:
        """
        Get detailed information about a specific place.

        Args:
            xid: Place ID (from radius or bbox query)

        Returns:
            Detailed place information or None if not found
        """
        url = f"{self.BASE_URL}/places/xid/{xid}"
        params = {"apikey": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            print(f"Error fetching place details for {xid}: {e}")
            return None


# CrewAI Tools


@tool("Get City Coordinates")
def get_city_coordinates_tool(city_name: str) -> str:
    """
    Get geographic coordinates for a city name.

    Args:
        city_name: Name of the city (e.g., "Paris", "Tokyo", "New York")

    Returns:
        JSON string with city coordinates and metadata
    """
    import asyncio
    import json

    client = OpenTripMapClient()

    async def fetch():
        return await client.get_location_coordinates(city_name)

    result = asyncio.run(fetch())

    if result:
        return json.dumps(result, indent=2)
    return json.dumps({"error": f"City '{city_name}' not found"})


@tool("Search Attractions Near Location")
def search_attractions_tool(
    lat: float, lon: float, radius_km: int = 5, categories: str | None = None
) -> str:
    """
    Search for tourist attractions near a geographic point.

    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers (default 5km)
        categories: Comma-separated attraction categories
                   (e.g., "museums,churches,historic,natural,theatres_and_entertainments")

    Returns:
        JSON string with list of attractions
    """
    import asyncio
    import json

    client = OpenTripMapClient()
    radius_meters = radius_km * 1000  # Convert km to meters

    async def fetch():
        return await client.get_attractions_by_radius(
            lat=lat, lon=lon, radius=radius_meters, kinds=categories, limit=100
        )

    results = asyncio.run(fetch())

    return json.dumps(results, indent=2)


@tool("Get Attraction Details")
def get_attraction_details_tool(place_id: str) -> str:
    """
    Get detailed information about a specific attraction.

    Args:
        place_id: OpenTripMap place ID (xid)

    Returns:
        JSON string with detailed place information
    """
    import asyncio
    import json

    client = OpenTripMapClient()

    async def fetch():
        return await client.get_place_details(place_id)

    result = asyncio.run(fetch())

    if result:
        return json.dumps(result, indent=2)
    return json.dumps({"error": f"Place '{place_id}' not found"})


# Fallback data for when API is unavailable or key not configured


def get_fallback_attractions_knowledge() -> str:
    """
    Returns general knowledge about common tourist attractions.
    Used as fallback when OpenTripMap API is unavailable.
    """
    return """
# Global Tourist Attractions Knowledge Base

## Major City Attractions by Category

### Museums & Galleries
- The Louvre (Paris): World's largest art museum, home to Mona Lisa
- British Museum (London): 8 million works, free admission
- Metropolitan Museum (NYC): 2M+ works spanning 5000 years
- Vatican Museums (Rome): Sistine Chapel, Raphael Rooms
- Smithsonian Museums (DC): 19 museums, all free

### Historical Sites
- Colosseum (Rome): Ancient amphitheater, €16 entry
- Acropolis (Athens): Ancient citadel with Parthenon
- Angkor Wat (Cambodia): Largest religious monument
- Machu Picchu (Peru): 15th-century Inca citadel
- Great Wall of China: 13,000+ miles of fortifications

### Natural Wonders
- Grand Canyon (USA): 277 miles long, 18 miles wide
- Great Barrier Reef (Australia): World's largest coral reef
- Victoria Falls (Zambia/Zimbabwe): "The Smoke That Thunders"
- Northern Lights: Best viewed in Iceland, Norway, Finland
- Amazon Rainforest: Largest tropical rainforest

### Religious Sites
- Sagrada Familia (Barcelona): Gaudí's basilica, €26 entry
- Blue Mosque (Istanbul): Active mosque, free entry (dress code)
- Golden Temple (Amritsar): Holiest Sikh gurdwara, free entry
- Western Wall (Jerusalem): Sacred site in Judaism
- St. Peter's Basilica (Vatican): Free entry, dress code required

### Architecture & Landmarks
- Eiffel Tower (Paris): €26 summit, €17 2nd floor
- Burj Khalifa (Dubai): World's tallest building, observation deck AED 149
- Sydney Opera House: Iconic performing arts center, tours $42
- Taj Mahal (India): White marble mausoleum, ₹1050 foreigners
- Statue of Liberty (NYC): Crown access $21.50

## General Visiting Tips

### Booking
- Book major attractions 2-4 weeks in advance
- City passes often save 20-40% on multiple attractions
- Morning and late afternoon slots have smaller crowds

### Timing
- Visit major museums on weekdays (Tuesday-Thursday)
- Arrive 30 minutes before opening for popular sites
- Sunset visits best for viewpoints and photography

### Costs (General Ranges)
- World-class museums: $15-$30
- Historical sites: $10-$25
- Observation decks: $20-$40
- Guided tours: $30-$100
- City passes (1-3 days): $50-$150

### Accessibility
- Major museums typically wheelchair accessible
- Historic sites may have limited accessibility
- Call ahead for special accommodations

### Photography
- Most museums allow non-flash photography
- Some religious sites prohibit all photography
- Golden hour (sunrise/sunset) best for outdoor monuments
"""
