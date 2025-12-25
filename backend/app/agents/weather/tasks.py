"""Task definitions for Weather Agent."""

from crewai import Task

from .prompts import (
    CLIMATE_ANALYSIS_TASK,
    PACKING_RECOMMENDATIONS_TASK,
    WEATHER_FORECAST_TASK,
    WEATHER_TRAVEL_TIPS_TASK,
)


def create_weather_forecast_task(
    agent,
    destination_city: str,
    destination_country: str,
    departure_date: str,
    return_date: str,
    duration_days: int,
) -> Task:
    """
    Create task for retrieving and analyzing weather forecast.

    Args:
        agent: The CrewAI agent to assign the task to
        destination_city: Destination city name
        destination_country: Destination country name
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        duration_days: Trip duration in days

    Returns:
        CrewAI Task for weather forecast analysis
    """
    description = WEATHER_FORECAST_TASK.format(
        destination_city=destination_city,
        destination_country=destination_country,
        departure_date=departure_date,
        return_date=return_date,
        duration_days=duration_days,
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="""JSON object containing:
        - daily_forecasts: Array of daily weather data
        - average_temp: Overall average temperature
        - temp_range_min: Lowest expected temperature
        - temp_range_max: Highest expected temperature
        - precipitation_chance: Overall precipitation probability
        - weather_alerts: Any active alerts
        - data_sources: Sources used""",
    )


def create_packing_recommendations_task(
    agent,
    average_temp: float,
    temp_min: float,
    temp_max: float,
    precipitation_prob: float,
    destination_city: str,
    destination_country: str,
) -> Task:
    """
    Create task for generating packing recommendations.

    Args:
        agent: The CrewAI agent to assign the task to
        average_temp: Average temperature for the trip
        temp_min: Minimum expected temperature
        temp_max: Maximum expected temperature
        precipitation_prob: Precipitation probability
        destination_city: Destination city name
        destination_country: Destination country name

    Returns:
        CrewAI Task for packing recommendations
    """
    description = PACKING_RECOMMENDATIONS_TASK.format(
        average_temp=average_temp,
        temp_min=temp_min,
        temp_max=temp_max,
        precipitation_prob=precipitation_prob,
        destination_city=destination_city,
        destination_country=destination_country,
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="""JSON array of packing suggestions, each containing:
        - item: What to pack (string)
        - reason: Why to pack it (string)
        - priority: Priority level (essential/recommended/optional)""",
    )


def create_climate_analysis_task(
    agent,
    destination_city: str,
    destination_country: str,
    departure_date: str,
    return_date: str,
) -> Task:
    """
    Create task for climate analysis and seasonal recommendations.

    Args:
        agent: The CrewAI agent to assign the task to
        destination_city: Destination city name
        destination_country: Destination country name
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)

    Returns:
        CrewAI Task for climate analysis
    """
    description = CLIMATE_ANALYSIS_TASK.format(
        destination_city=destination_city,
        destination_country=destination_country,
        departure_date=departure_date,
        return_date=return_date,
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="""JSON object containing:
        - climate_type: Climate classification (string)
        - best_time_to_visit: Ideal months/season (string)
        - worst_time_to_visit: Months to avoid (string or null)
        - seasonal_notes: Array of seasonal considerations
        - is_good_time_to_visit: Boolean assessment
        - seasonal_recommendation: Detailed recommendation (string)""",
    )


def create_weather_travel_tips_task(
    agent,
    destination_city: str,
    destination_country: str,
    weather_summary: str,
    weather_alerts: str,
) -> Task:
    """
    Create task for generating weather-related travel tips.

    Args:
        agent: The CrewAI agent to assign the task to
        destination_city: Destination city name
        destination_country: Destination country name
        weather_summary: Summary of weather conditions
        weather_alerts: Any active weather alerts

    Returns:
        CrewAI Task for travel tips generation
    """
    description = WEATHER_TRAVEL_TIPS_TASK.format(
        destination_city=destination_city,
        destination_country=destination_country,
        weather_summary=weather_summary,
        weather_alerts=weather_alerts,
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="""JSON array of 5-8 specific, actionable travel tips (strings)
        covering health, safety, activities, and practical advice.""",
    )


def create_comprehensive_weather_task(
    agent,
    destination_city: str,
    destination_country: str,
    departure_date: str,
    return_date: str,
    duration_days: int,
) -> Task:
    """
    Create comprehensive task combining all weather analysis aspects.

    This task combines forecast retrieval, packing recommendations,
    climate analysis, and travel tips into a single comprehensive report.

    Args:
        agent: The CrewAI agent to assign the task to
        destination_city: Destination city name
        destination_country: Destination country name
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        duration_days: Trip duration in days

    Returns:
        CrewAI Task for comprehensive weather analysis
    """
    description = f"""Provide comprehensive weather intelligence for the trip.

**Trip Details:**
- Destination: {destination_city}, {destination_country}
- Travel Dates: {departure_date} to {return_date}
- Duration: {duration_days} days

**Your Complete Analysis Must Include:**

1. **Weather Forecast:**
   - Retrieve accurate forecast data for all trip days
   - Daily temperature ranges, conditions, precipitation
   - Weather alerts if any active

2. **Packing Recommendations:**
   - Essential, recommended, and optional items
   - Weather-appropriate clothing and gear
   - Clear reasoning for each recommendation

3. **Climate Assessment:**
   - Climate type and seasonal context
   - Evaluation of trip timing (good time to visit?)
   - Best/worst times to visit this destination

4. **Travel Tips:**
   - Health and safety considerations
   - Activity planning suggestions
   - Practical weather-related advice

**Output Format:**
Complete JSON object with all sections populated with accurate, specific data.
Use metric units and provide factual, source-backed information."""

    return Task(
        description=description,
        agent=agent,
        expected_output="""Complete JSON object containing:
        - location: Resolved location name
        - latitude: Location latitude
        - longitude: Location longitude
        - timezone: Location timezone
        - forecast: Array of daily forecasts
        - average_temp: Trip average temperature
        - temp_range_min: Minimum temperature
        - temp_range_max: Maximum temperature
        - precipitation_chance: Overall precipitation probability
        - total_precipitation: Total expected precipitation
        - packing_suggestions: Array of packing items with priorities
        - climate_info: Climate analysis object
        - weather_alerts: Array of active alerts
        - travel_tips: Array of actionable tips
        - is_good_time_to_visit: Boolean
        - seasonal_recommendation: String
        - confidence_score: Float (0.0-1.0)
        - sources: Array of data sources
        - warnings: Array of caveats""",
    )
