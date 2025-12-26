"""Tools for Weather Agent."""

import logging
from datetime import date, timedelta
from typing import Any

from crewai.tools import tool

from app.core.config import settings
from app.services.weather import WeatherAPIClient, VisualCrossingClient

logger = logging.getLogger(__name__)


def _try_visual_crossing_forecast(
    location: str, start_date: date, end_date: date
) -> dict[str, Any] | None:
    """
    Try to get forecast from Visual Crossing API.

    Returns None if API key not configured or request fails.
    """
    if not settings.VISUAL_CROSSING_API_KEY:
        return None

    try:
        client = VisualCrossingClient(api_key=settings.VISUAL_CROSSING_API_KEY)
        weather_data = client.get_forecast(
            location=location,
            start_date=start_date,
            end_date=end_date,
        )

        # Transform to common format
        formatted_days = []
        for day in weather_data.days:
            formatted_days.append({
                "date": day.datetime,
                "tempmax": day.tempmax,
                "tempmin": day.tempmin,
                "temp": day.temp,
                "conditions": day.conditions,
                "icon": day.icon,
                "precip": day.precip,
                "precipprob": day.precipprob,
                "humidity": day.humidity,
                "windspeed": day.windspeed,
                "uvindex": day.uvindex,
                "sunrise": day.sunrise,
                "sunset": day.sunset,
                "description": day.description,
            })

        return {
            "source": "visual_crossing",
            "location": weather_data.resolvedAddress,
            "latitude": weather_data.latitude,
            "longitude": weather_data.longitude,
            "timezone": weather_data.timezone,
            "days": formatted_days,
            "alerts": [
                {"event": a.event, "headline": a.headline, "severity": a.severity}
                for a in (weather_data.alerts or [])
            ],
        }
    except Exception as e:
        logger.warning(f"Visual Crossing API failed: {e}")
        return None


@tool("Get Weather Forecast")
def get_weather_forecast(location: str, start_date: str, end_date: str) -> dict[str, Any]:
    """
    Get weather forecast for a location and date range.

    Uses WeatherAPI.com as primary source with Visual Crossing as fallback.
    Provides accurate weather forecasts including:
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

    Example:
        >>> get_weather_forecast("Tokyo, Japan", "2025-06-15", "2025-06-20")
        {
            "location": "Tokyo, Japan",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "days": [
                {
                    "date": "2025-06-15",
                    "tempmax": 28.5,
                    "tempmin": 20.1,
                    "conditions": "Partly cloudy",
                    ...
                }
            ]
        }
    """
    try:
        # Convert string dates to date objects
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        # Try Visual Crossing first if available (better for date ranges)
        vc_result = _try_visual_crossing_forecast(location, start, end)
        if vc_result:
            return vc_result

        # Fallback to WeatherAPI
        api_key = settings.WEATHERAPI_KEY
        if not api_key:
            return {
                "error": "Weather API key not configured",
                "message": "Please set WEATHERAPI_KEY or VISUAL_CROSSING_API_KEY environment variable",
            }

        client = WeatherAPIClient(api_key=api_key)
        today = date.today()

        # Calculate days for forecast (WeatherAPI uses days from today, max 14 days in paid, 3 in free)
        days_diff = (end - today).days + 1
        days_to_fetch = min(max(days_diff, 1), 14)  # Limit to 14 days

        # Get forecast
        weather_data = client.get_forecast(
            location=location,
            days=days_to_fetch,
            aqi=False,
            alerts=True,
        )

        # Transform response to match expected format
        formatted_days = []
        for day in weather_data.forecast.forecastday:
            day_date = date.fromisoformat(day.date)
            # Only include days within the requested range
            if start <= day_date <= end:
                formatted_day = {
                    "date": day.date,
                    "tempmax": day.day.get("maxtemp_c"),
                    "tempmin": day.day.get("mintemp_c"),
                    "temp": day.day.get("avgtemp_c"),
                    "conditions": day.day.get("condition", {}).get("text", ""),
                    "icon": day.day.get("condition", {}).get("icon", ""),
                    "precip": day.day.get("totalprecip_mm"),
                    "precipprob": day.day.get("daily_chance_of_rain"),
                    "humidity": day.day.get("avghumidity"),
                    "windspeed": day.day.get("maxwind_kph"),
                    "uvindex": day.day.get("uv"),
                    "sunrise": day.astro.get("sunrise"),
                    "sunset": day.astro.get("sunset"),
                    "description": day.day.get("condition", {}).get("text", ""),
                }
                formatted_days.append(formatted_day)

        # Convert to dictionary for CrewAI
        return {
            "location": f"{weather_data.location.name}, {weather_data.location.country}",
            "latitude": weather_data.location.lat,
            "longitude": weather_data.location.lon,
            "timezone": weather_data.location.tz_id,
            "days": formatted_days,
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
