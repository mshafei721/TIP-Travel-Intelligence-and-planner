"""Tools for Weather Agent."""

import os
from datetime import date
from typing import Any

from crewai.tools import tool

from app.services.weather import VisualCrossingClient


@tool("Get Weather Forecast")
def get_weather_forecast(location: str, start_date: str, end_date: str) -> dict[str, Any]:
    """
    Get weather forecast for a location and date range using Visual Crossing API.

    This tool provides accurate weather forecasts including:
    - Daily temperature ranges (min/max/average)
    - Precipitation probability and amounts
    - Wind speed and direction
    - Humidity levels
    - UV index
    - Sunrise/sunset times
    - Weather conditions and descriptions

    Args:
        location: City name or "latitude,longitude" coordinates
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Dictionary containing:
        - location: Resolved location name
        - latitude: Location latitude
        - longitude: Location longitude
        - timezone: Location timezone
        - days: List of daily forecasts with weather details
        - alerts: Any active weather alerts (if available)

    Example:
        >>> get_weather_forecast("Tokyo, Japan", "2024-06-15", "2024-06-20")
        {
            "location": "Tokyo, Japan",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "days": [
                {
                    "date": "2024-06-15",
                    "tempmax": 28.5,
                    "tempmin": 20.1,
                    "conditions": "Partly cloudy",
                    ...
                }
            ]
        }
    """
    try:
        api_key = os.getenv("VISUAL_CROSSING_API_KEY")
        if not api_key:
            return {
                "error": "Visual Crossing API key not configured",
                "message": "Please set VISUAL_CROSSING_API_KEY environment variable",
            }

        client = VisualCrossingClient(api_key=api_key)

        # Convert string dates to date objects
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        # Get forecast
        weather_data = client.get_forecast(
            location=location,
            start_date=start,
            end_date=end,
            unit_group="metric",
            include_alerts=True,
        )

        # Convert to dictionary for CrewAI
        return {
            "location": weather_data.resolvedAddress,
            "latitude": weather_data.latitude,
            "longitude": weather_data.longitude,
            "timezone": weather_data.timezone,
            "days": [day.model_dump() for day in weather_data.days],
            "alerts": (
                [alert.model_dump() for alert in weather_data.alerts] if weather_data.alerts else []
            ),
        }

    except ValueError as e:
        return {"error": "API Error", "message": str(e)}
    except Exception as e:
        return {"error": "Unexpected Error", "message": str(e)}


@tool("Get Weather by Coordinates")
def get_weather_by_coordinates(
    latitude: float, longitude: float, start_date: str, end_date: str
) -> dict[str, Any]:
    """
    Get weather forecast using exact latitude/longitude coordinates.

    Use this tool when you have precise coordinates for the destination.
    Provides the same weather data as get_weather_forecast but with
    coordinate-based location specification.

    Args:
        latitude: Location latitude (-90 to 90)
        longitude: Location longitude (-180 to 180)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Dictionary containing weather forecast data

    Example:
        >>> get_weather_by_coordinates(35.6762, 139.6503, "2024-06-15", "2024-06-20")
        {
            "location": "Tokyo, Tōkyō-to, Japan",
            "latitude": 35.6762,
            "longitude": 139.6503,
            ...
        }
    """
    location = f"{latitude},{longitude}"
    return get_weather_forecast(location, start_date, end_date)


@tool("Get Climate Information")
def get_climate_information(location: str) -> dict[str, Any]:
    """
    Get general climate classification and seasonal information for a location.

    Provides insights about the destination's climate type and seasonal patterns
    to help assess the best time to visit.

    Args:
        location: City name or country

    Returns:
        Dictionary containing:
        - climate_type: Köppen climate classification or general description
        - typical_seasons: Description of seasonal patterns
        - best_months: Recommended months to visit
        - notes: Additional climate-related information

    Example:
        >>> get_climate_information("Bangkok, Thailand")
        {
            "climate_type": "Tropical Savanna",
            "typical_seasons": "Hot and humid year-round with monsoon season",
            "best_months": "November to February (cool and dry season)",
            "notes": ["Avoid April-May (hottest months)", "Monsoon: June-October"]
        }

    Note:
        This tool provides general climate knowledge. For specific forecast data,
        use get_weather_forecast instead.
    """
    # Climate knowledge base (expandable)
    climate_data = {
        # Asia
        "tokyo": {
            "climate_type": "Humid Subtropical",
            "best_months": "March-May (spring), September-November (fall)",
            "notes": [
                "Hot, humid summers with typhoon risk (June-September)",
                "Cold winters with occasional snow (December-February)",
                "Cherry blossom season: Late March to early April",
            ],
        },
        "bangkok": {
            "climate_type": "Tropical Savanna",
            "best_months": "November-February (cool season)",
            "notes": [
                "Hot season: March-May (very hot, up to 40°C)",
                "Rainy season: June-October (daily afternoon showers)",
                "Humidity high year-round",
            ],
        },
        "singapore": {
            "climate_type": "Tropical Rainforest",
            "best_months": "February-April (slightly drier)",
            "notes": [
                "Consistent temperatures year-round (25-32°C)",
                "Monsoon seasons: November-January, June-September",
                "Brief but heavy rain showers possible any time",
            ],
        },
        # Europe
        "paris": {
            "climate_type": "Oceanic",
            "best_months": "April-June, September-October",
            "notes": [
                "Mild summers, cold winters",
                "Rain possible year-round",
                "Peak tourist season: July-August (crowded, hot)",
            ],
        },
        "barcelona": {
            "climate_type": "Mediterranean",
            "best_months": "May-June, September-October",
            "notes": [
                "Hot, dry summers (July-August)",
                "Mild, wet winters",
                "Beach season: June-September",
            ],
        },
        # Americas
        "new york": {
            "climate_type": "Humid Subtropical",
            "best_months": "April-June, September-November",
            "notes": [
                "Hot, humid summers with occasional heat waves",
                "Cold, snowy winters (December-March)",
                "Fall foliage peak: October",
            ],
        },
    }

    # Normalize location for lookup
    location_key = location.lower().split(",")[0].strip()

    if location_key in climate_data:
        data = climate_data[location_key]
        return {
            "location": location,
            "climate_type": data["climate_type"],
            "best_months": data["best_months"],
            "notes": data["notes"],
        }
    else:
        # Default response for unknown locations
        return {
            "location": location,
            "climate_type": "Climate data not available",
            "best_months": "Consult weather forecast for specific dates",
            "notes": [
                "Use weather forecast tool for accurate data",
                "Research destination-specific climate patterns",
            ],
        }


@tool("Calculate Packing Needs")
def calculate_packing_needs(
    temp_min: float, temp_max: float, precipitation_prob: float, destination: str
) -> dict[str, Any]:
    """
    Calculate packing recommendations based on weather conditions.

    Analyzes temperature ranges and precipitation probability to suggest
    appropriate clothing and gear.

    Args:
        temp_min: Minimum temperature expected (Celsius)
        temp_max: Maximum temperature expected (Celsius)
        precipitation_prob: Precipitation probability (0-100%)
        destination: Destination name (for cultural context)

    Returns:
        Dictionary with packing recommendations categorized by priority:
        - essential: Must-pack items
        - recommended: Should-pack items
        - optional: Nice-to-have items

    Example:
        >>> calculate_packing_needs(15, 25, 60, "London")
        {
            "essential": ["Light rain jacket", "Layers (cardigan/sweater)"],
            "recommended": ["Umbrella", "Closed-toe walking shoes"],
            "optional": ["Light scarf", "Sunglasses"]
        }
    """
    essential = []
    recommended = []
    optional = []

    # Temperature-based recommendations
    if temp_max >= 30:
        essential.extend(
            [
                "Light, breathable clothing",
                "Sun hat or cap",
                "Sunscreen (SPF 30+)",
            ]
        )
        recommended.extend(["Sunglasses", "Light scarf for sun protection"])
        optional.append("Cooling towel")

    elif temp_max >= 25:
        essential.extend(["Light layers", "Sunscreen", "Comfortable walking shoes"])
        recommended.extend(["Sun hat", "Light cardigan for AC"])
        optional.append("Sunglasses")

    elif temp_max >= 15:
        essential.extend(["Medium-weight layers", "Light jacket", "Long pants"])
        recommended.extend(["Sweater or fleece", "Scarf"])
        optional.append("Light gloves for early morning/evening")

    elif temp_max >= 5:
        essential.extend(["Warm coat", "Warm layers", "Long pants", "Closed-toe shoes"])
        recommended.extend(["Scarf", "Gloves", "Warm hat"])
        optional.append("Thermal underwear")

    else:  # temp_max < 5
        essential.extend(
            [
                "Winter coat",
                "Thermal layers",
                "Warm boots",
                "Heavy gloves",
                "Warm hat",
                "Scarf",
            ]
        )
        recommended.extend(["Thermal socks", "Hand warmers"])
        optional.append("Neck gaiter or balaclava")

    # Precipitation-based recommendations
    if precipitation_prob >= 70:
        essential.append("Waterproof rain jacket")
        recommended.extend(["Compact umbrella", "Waterproof shoes/boots"])
        optional.append("Rain pants for heavy rain")

    elif precipitation_prob >= 40:
        recommended.extend(["Light rain jacket or umbrella", "Water-resistant shoes"])
        optional.append("Packable poncho")

    elif precipitation_prob >= 20:
        optional.append("Small umbrella (just in case)")

    # Temperature range considerations
    temp_range = temp_max - temp_min
    if temp_range > 15:
        essential.append("Versatile layers for varying temperatures")
        recommended.append("Day-to-night outfit options")

    return {"essential": essential, "recommended": recommended, "optional": optional}
