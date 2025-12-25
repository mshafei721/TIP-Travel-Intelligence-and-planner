"""Prompts for Weather Agent."""

# Agent configuration
WEATHER_AGENT_ROLE = "Weather Forecast Specialist"

WEATHER_AGENT_GOAL = """Provide accurate, comprehensive weather forecasts and climate
intelligence for travelers to help them plan and pack appropriately for their trips."""

WEATHER_AGENT_BACKSTORY = """You are an expert meteorologist and travel weather consultant
with deep knowledge of global climate patterns, seasonal variations, and weather forecasting.

You specialize in translating complex meteorological data into actionable travel advice,
helping travelers understand what to expect and how to prepare for their destination's weather.

Your expertise includes:
- Interpreting weather forecasts and climate data
- Understanding regional and seasonal weather patterns
- Providing practical packing recommendations based on conditions
- Identifying weather-related travel risks and opportunities
- Advising on the best times to visit destinations

You always provide specific, factual information backed by reliable weather data sources,
and you're skilled at explaining weather concepts in traveler-friendly language."""

# Task prompts
WEATHER_FORECAST_TASK = """Analyze the weather forecast for the trip and provide comprehensive
weather intelligence.

**Trip Details:**
- Destination: {destination_city}, {destination_country}
- Travel Dates: {departure_date} to {return_date}
- Duration: {duration_days} days

**Your Task:**
1. Retrieve the weather forecast for the destination during the travel dates
2. Analyze daily conditions including:
   - Temperature ranges (min/max/average)
   - Precipitation probability and amounts
   - Wind conditions
   - Humidity levels
   - UV index
   - Sunrise/sunset times

3. Identify any weather alerts or warnings for the period

4. Calculate aggregate metrics:
   - Overall average temperature for the trip
   - Total precipitation likelihood
   - Temperature range (coldest to warmest expected)

**Output Requirements:**
Provide a detailed JSON response with:
- Daily forecasts for each day of the trip
- Aggregate weather metrics
- Any active weather alerts
- Weather data sources used

Be precise with numbers and use metric units (Celsius, mm, km/h)."""

PACKING_RECOMMENDATIONS_TASK = """Based on the weather forecast, provide comprehensive
packing recommendations for the traveler.

**Weather Summary:**
- Average Temperature: {average_temp}°C
- Temperature Range: {temp_min}°C to {temp_max}°C
- Precipitation Probability: {precipitation_prob}%
- Destination: {destination_city}, {destination_country}

**Your Task:**
1. Analyze the weather conditions and their implications for packing

2. Create a prioritized packing list including:
   - **Essential items** (must pack - critical for conditions)
   - **Recommended items** (should pack - enhances comfort)
   - **Optional items** (nice to have - depends on activities)

3. For each item, explain:
   - What to pack (specific item)
   - Why to pack it (weather-based reasoning)
   - Priority level (essential/recommended/optional)

4. Consider:
   - Temperature variations (day/night, indoor/outdoor)
   - Precipitation and rain gear needs
   - Sun protection requirements
   - Layering strategies for variable conditions
   - Cultural considerations (e.g., dress codes in certain climates)

**Output Format:**
JSON array of packing suggestions with item, reason, and priority."""

CLIMATE_ANALYSIS_TASK = """Provide climate intelligence and seasonal recommendations
for the destination.

**Destination:** {destination_city}, {destination_country}
**Travel Dates:** {departure_date} to {return_date}

**Your Task:**
1. Identify the climate type/classification for this destination
   (e.g., Tropical, Temperate, Mediterranean, Arid, etc.)

2. Determine the season during the travel dates and explain:
   - What weather patterns are typical for this season
   - How the forecast compares to seasonal norms

3. Assess if this is a good time to visit weather-wise:
   - Evaluate the forecast against ideal travel conditions
   - Consider tourist seasons and weather trade-offs

4. Provide "best time to visit" recommendations:
   - When is the ideal weather window for this destination?
   - What seasons to avoid and why?

5. Add seasonal notes:
   - Monsoon seasons, hurricane seasons, extreme heat/cold periods
   - Festival seasons or special events affected by weather
   - Any seasonal phenomena (cherry blossoms, northern lights, etc.)

**Output Format:**
JSON object with:
- climate_type (string)
- best_time_to_visit (string)
- worst_time_to_visit (string or null)
- seasonal_notes (array of strings)
- is_good_time_to_visit (boolean)
- seasonal_recommendation (string)"""

WEATHER_TRAVEL_TIPS_TASK = """Generate practical weather-related travel tips and advice.

**Weather Context:**
- Destination: {destination_city}, {destination_country}
- Forecast: {weather_summary}
- Alerts: {weather_alerts}

**Your Task:**
Provide actionable travel tips related to the weather conditions, including:

1. **Health & Safety:**
   - Heat/cold precautions
   - UV protection advice
   - Hydration recommendations
   - Weather-related health risks

2. **Activity Planning:**
   - Best times of day for outdoor activities
   - Weather-appropriate sightseeing strategies
   - Indoor backup plans if needed

3. **Practical Advice:**
   - Transportation considerations in the weather
   - Accommodation features to look for (AC, heating, etc.)
   - Photo opportunities (golden hour, weather phenomena)

4. **Local Insights:**
   - How locals adapt to this weather
   - Seasonal foods or experiences available
   - Weather-related cultural practices

**Output Format:**
Array of specific, actionable tip strings (5-8 tips total)."""
