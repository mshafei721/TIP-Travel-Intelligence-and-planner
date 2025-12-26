"""
Flight Agent - Tools

Tools for flight search, airport information, and booking guidance.
"""

import logging
import re
from datetime import date as DateType
from datetime import datetime, timedelta
from typing import Any

from crewai.tools import tool

logger = logging.getLogger(__name__)


@tool("Search Flight Routes")
def search_flight_routes(
    origin_city: str,
    destination_city: str,
    departure_date: str,
    return_date: str | None = None,
    cabin_class: str = "economy",
) -> str:
    """
    Search for available flight routes between origin and destination.

    Uses AI knowledge base to identify major airlines, typical routes, connection
    hubs, and estimated flight durations. This tool provides route structure which
    can be used to build realistic flight options.

    Args:
        origin_city: Departure city (e.g., "New York" or "New York, USA")
        destination_city: Arrival city (e.g., "Tokyo" or "Tokyo, Japan")
        departure_date: Departure date in ISO format (YYYY-MM-DD)
        return_date: Return date in ISO format (optional for one-way)
        cabin_class: Cabin class (economy, premium_economy, business, first)

    Returns:
        JSON string with route information including:
        - Major airlines operating this route
        - Whether direct flights are available
        - Common connection hubs if no direct flights
        - Estimated flight durations
        - Typical number of daily flights
        - Peak/off-peak season information

    Example:
        >>> search_flight_routes("New York", "London", "2024-06-15", "2024-06-22")
    """
    logger.info(
        f"Searching flight routes: {origin_city} -> {destination_city} "
        f"({departure_date} to {return_date})"
    )

    # Note: In production, this would call a real flight API like Amadeus
    # For now, we rely on the LLM's knowledge base to generate realistic routes

    search_context = {
        "origin": origin_city,
        "destination": destination_city,
        "departure_date": departure_date,
        "return_date": return_date,
        "cabin_class": cabin_class,
        "request_time": datetime.utcnow().isoformat(),
    }

    return f"""Search flight routes from {origin_city} to {destination_city}.
Departure: {departure_date}, Return: {return_date or 'One-way'}
Cabin Class: {cabin_class}

Provide detailed information about:
1. Major airlines serving this route
2. Whether direct flights exist
3. Common connection hubs (if no direct flights)
4. Estimated flight times
5. Typical frequency (flights per day/week)
6. Seasonal patterns or peak travel times

Context: {search_context}"""


@tool("Get Airport Information")
def get_airport_info(city: str, country: str | None = None) -> str:
    """
    Get comprehensive airport information for a city.

    Retrieves details about major airports serving a city, including IATA codes,
    full names, terminals, and ground transportation options.

    Args:
        city: City name (e.g., "Paris", "New York")
        country: Country name for disambiguation (optional, e.g., "France", "USA")

    Returns:
        JSON string with airport information including:
        - IATA airport codes
        - Full airport names
        - Number of terminals
        - Distance to city center
        - Transportation options (metro, bus, taxi, rideshare)
        - Average costs and travel times
        - Key facilities (lounges, wifi, shopping)

    Example:
        >>> get_airport_info("Paris", "France")
    """
    logger.info(f"Getting airport info for: {city}, {country}")

    location = f"{city}, {country}" if country else city

    return f"""Provide comprehensive airport information for {location}.

Include:
1. Main airport(s) with IATA codes and full names
2. Terminal information
3. Distance to city center (km/miles)
4. Transportation options:
   - Public transit (metro, bus, train)
   - Taxis and rideshare services
   - Airport shuttles
   - Rental cars
5. Costs and average travel times for each option
6. Airport facilities (lounges, wifi, restaurants, duty-free)
7. Special tips for international travelers
8. Rush hour considerations

Format as structured JSON."""


@tool("Calculate Layover Requirements")
def calculate_layover_requirements(
    layover_airport: str, origin_airline: str, destination_airline: str
) -> str:
    """
    Calculate minimum connection time and provide layover guidance.

    Analyzes layover airport to determine safe connection times, terminal changes,
    visa requirements, and layover tips.

    Args:
        layover_airport: IATA code or name of layover airport (e.g., "LHR", "London Heathrow")
        origin_airline: Airline of incoming flight
        destination_airline: Airline of connecting flight

    Returns:
        JSON string with layover information:
        - Minimum connection time (domestic/international)
        - Whether terminal change is required
        - Visa transit requirements
        - Layover activities (if time permits)
        - Connection risk assessment

    Example:
        >>> calculate_layover_requirements("DXB", "Emirates", "British Airways")
    """
    logger.info(f"Analyzing layover at {layover_airport}: {origin_airline} -> {destination_airline}")

    return f"""Analyze layover connection at {layover_airport}.

**Flight Connection:**
- Arriving airline: {origin_airline}
- Departing airline: {destination_airline}

**Provide:**
1. Minimum connection time (MCT)
   - Same airline/alliance
   - Different airlines
   - Domestic vs international
2. Terminal information
   - Will passenger need to change terminals?
   - How to transfer between terminals
3. Immigration/customs requirements
   - Visa transit requirements
   - Security re-screening needed?
4. Connection risk assessment
   - Is MCT sufficient?
   - What if delayed?
5. Layover tips
   - What to do during layover
   - Facilities available
   - Food and rest options

Format as detailed JSON."""


@tool("Estimate Flight Pricing")
def estimate_flight_pricing(
    origin: str,
    destination: str,
    departure_date: str,
    cabin_class: str = "economy",
    is_direct: bool = False,
) -> str:
    """
    Estimate flight pricing based on route, timing, and historical patterns.

    Provides price range estimates using knowledge of typical pricing for the route,
    seasonal variations, and booking timing factors.

    Args:
        origin: Origin city
        destination: Destination city
        departure_date: Departure date (YYYY-MM-DD)
        cabin_class: Cabin class (economy, premium_economy, business, first)
        is_direct: Whether it's a direct flight

    Returns:
        JSON with estimated pricing:
        - Low/medium/high price range in USD
        - Factors affecting price (season, advance booking, etc.)
        - Comparison to typical prices for route
        - Budget airline availability

    Example:
        >>> estimate_flight_pricing("London", "New York", "2024-07-15", "economy", True)
    """
    logger.info(f"Estimating prices: {origin} -> {destination} on {departure_date}")

    # Parse date to determine season
    try:
        dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
        days_until_departure = (dep_date - datetime.now()).days
    except ValueError:
        days_until_departure = None

    return f"""Estimate flight pricing for this route:

**Route:** {origin} → {destination}
**Departure:** {departure_date} ({days_until_departure} days from now)
**Cabin Class:** {cabin_class}
**Direct Flight:** {is_direct}

**Provide pricing estimate with:**
1. Price range (low/medium/high) in USD
2. Average typical price for this route
3. Seasonal factors affecting price
   - Is this peak/off-peak season?
   - Major holidays or events?
4. Booking timing impact
   - Optimal booking window
   - Current booking relative to optimal
5. Direct vs connection price difference
6. Budget airline options if available
7. Historical price trends
8. Price forecast (increase/decrease expected?)

Return as structured JSON with confidence level."""


@tool("Get Booking Timing Advice")
def get_booking_timing_advice(
    origin: str, destination: str, departure_date: str, current_price: float | None = None
) -> str:
    """
    Provide optimal booking timing and price tracking recommendations.

    Analyzes when to book flights for this route to get best prices, based on
    historical patterns and current pricing trends.

    Args:
        origin: Origin city
        destination: Destination city
        departure_date: Planned departure date (YYYY-MM-DD)
        current_price: Current observed price in USD (optional)

    Returns:
        JSON with booking advice:
        - Optimal booking window (weeks before departure)
        - Whether to book now or wait
        - Price alert recommendations
        - Day-of-week pricing patterns
        - Alternative date suggestions

    Example:
        >>> get_booking_timing_advice("Paris", "Tokyo", "2024-08-20", 850.0)
    """
    logger.info(f"Getting booking advice: {origin} -> {destination} on {departure_date}")

    try:
        dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
        days_until = (dep_date - datetime.now()).days
        weeks_until = days_until / 7
    except ValueError:
        days_until = None
        weeks_until = None

    return f"""Provide booking timing strategy for:

**Route:** {origin} → {destination}
**Departure Date:** {departure_date}
**Days Until Departure:** {days_until}
**Current Price:** ${current_price if current_price else 'Unknown'}

**Advise on:**
1. Optimal booking window for this route
   - Typical best time (weeks before departure)
   - Current timing assessment
2. Book now vs wait recommendation
   - If price is good, book now
   - If likely to drop, wait and set alerts
3. Price tracking strategy
   - Set up price alerts
   - Monitor frequency
4. Day-of-week patterns
   - Best days to search/book
   - Best days to fly for lower fares
5. Flexible dates analysis
   - Cheaper nearby dates
   - Weekend vs weekday pricing
6. Alternative strategies
   - Open-jaw routes
   - Nearby airports
   - Separate one-ways vs round-trip

Provide actionable, time-sensitive recommendations."""


@tool("Analyze Baggage Policies")
def analyze_baggage_policies(airlines: str, cabin_class: str = "economy") -> str:
    """
    Analyze baggage allowances and policies for airlines.

    Provides comprehensive baggage information to help travelers pack appropriately
    and avoid unexpected fees.

    Args:
        airlines: Comma-separated airline names or codes
        cabin_class: Cabin class (economy, premium_economy, business, first)

    Returns:
        JSON with baggage policy details:
        - Carry-on allowances (size, weight)
        - Checked baggage included
        - Fees for additional bags
        - Special items (sports equipment, musical instruments)
        - Weight/size restrictions

    Example:
        >>> analyze_baggage_policies("United,Lufthansa", "economy")
    """
    logger.info(f"Analyzing baggage policies for: {airlines} ({cabin_class})")

    airline_list = [a.strip() for a in airlines.split(",")]

    return f"""Provide comprehensive baggage policy information.

**Airlines:** {', '.join(airline_list)}
**Cabin Class:** {cabin_class}

**For each airline, detail:**
1. Carry-on allowance
   - Dimensions and weight limits
   - Personal item allowance
2. Checked baggage
   - Number of bags included
   - Weight limit per bag
   - Size restrictions
3. Additional baggage fees
   - Cost for extra bags
   - Overweight/oversized fees
4. Special items
   - Sports equipment policies
   - Musical instruments
   - Infant items
5. Important restrictions
   - Lithium battery rules
   - Liquid restrictions
   - Prohibited items
6. Tips to maximize allowance
   - How to pack efficiently
   - Wearing heavy items
   - Shipping vs flying with items

Format as comparison table in JSON."""
