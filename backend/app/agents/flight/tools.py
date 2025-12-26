"""
Flight Agent - Tools

Tools for flight search, airport information, and booking guidance.
Integrates with Amadeus API when credentials are available,
falls back to AI knowledge base otherwise.
"""

import json
import logging
from datetime import date as DateType
from datetime import datetime

from crewai.tools import tool

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependencies
_flight_client = None


def _get_flight_client():
    """Get or create Amadeus flight client (lazy initialization)."""
    global _flight_client
    if _flight_client is None:
        if settings.AMADEUS_API_KEY and settings.AMADEUS_API_SECRET:
            from app.services.flight.amadeus_client import AmadeusFlightClient

            _flight_client = AmadeusFlightClient(test_mode=True)
            logger.info("Amadeus flight client initialized")
        else:
            logger.warning("Amadeus API not configured - using AI knowledge base")
    return _flight_client


def _has_api_credentials() -> bool:
    """Check if Amadeus API credentials are configured."""
    return bool(settings.AMADEUS_API_KEY and settings.AMADEUS_API_SECRET)


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

    Uses Amadeus API when available, falls back to AI knowledge base.
    Returns actual flight offers with real-time pricing when API is configured.

    Args:
        origin_city: Departure city or IATA airport code (e.g., "JFK" or "New York")
        destination_city: Arrival city or IATA airport code (e.g., "LHR" or "London")
        departure_date: Departure date in ISO format (YYYY-MM-DD)
        return_date: Return date in ISO format (optional for one-way)
        cabin_class: Cabin class (economy, premium_economy, business, first)

    Returns:
        JSON string with flight offers including prices, airlines, and schedules

    Example:
        >>> search_flight_routes("JFK", "LHR", "2025-06-15", "2025-06-22")
    """
    logger.info(
        f"Searching flight routes: {origin_city} -> {destination_city} "
        f"({departure_date} to {return_date})"
    )

    client = _get_flight_client()

    # Try real API search if client is available
    if client and _has_api_credentials():
        try:
            # Parse dates
            dep_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            ret_date = (
                datetime.strptime(return_date, "%Y-%m-%d").date()
                if return_date
                else None
            )

            # Map cabin class to API format
            cabin_map = {
                "economy": "ECONOMY",
                "premium_economy": "PREMIUM_ECONOMY",
                "business": "BUSINESS",
                "first": "FIRST",
            }
            travel_class = cabin_map.get(cabin_class.lower(), "ECONOMY")

            # Search flights
            result = client.search_flights(
                origin=origin_city.upper()[:3],  # Use first 3 chars as IATA code
                destination=destination_city.upper()[:3],
                departure_date=dep_date,
                return_date=ret_date,
                travel_class=travel_class,
                max_offers=10,
            )

            # Format response
            offers_data = []
            for offer in result.offers[:5]:  # Limit to top 5
                segments_info = []
                for seg in offer.outbound_segments:
                    segments_info.append(
                        {
                            "from": seg.departure_airport,
                            "to": seg.arrival_airport,
                            "departure": seg.departure_time,
                            "arrival": seg.arrival_time,
                            "airline": seg.carrier_name or seg.carrier_code,
                            "flight": f"{seg.carrier_code}{seg.flight_number}",
                            "duration": seg.duration,
                            "stops": seg.stops,
                        }
                    )

                return_info = []
                for seg in offer.return_segments:
                    return_info.append(
                        {
                            "from": seg.departure_airport,
                            "to": seg.arrival_airport,
                            "departure": seg.departure_time,
                            "arrival": seg.arrival_time,
                            "airline": seg.carrier_name or seg.carrier_code,
                            "flight": f"{seg.carrier_code}{seg.flight_number}",
                            "duration": seg.duration,
                        }
                    )

                offers_data.append(
                    {
                        "price": offer.total_price,
                        "currency": offer.currency,
                        "cabin_class": offer.cabin_class,
                        "airline": offer.validating_airline,
                        "baggage": offer.included_baggage,
                        "is_direct": len(offer.outbound_segments) == 1,
                        "outbound": segments_info,
                        "return": return_info if return_info else None,
                        "seats_available": offer.number_of_bookable_seats,
                        "last_ticketing_date": offer.last_ticketing_date,
                    }
                )

            response = {
                "source": "amadeus_api",
                "origin": result.origin,
                "destination": result.destination,
                "departure_date": result.departure_date,
                "return_date": result.return_date,
                "total_offers": result.total_offers,
                "offers": offers_data,
                "carriers": result.dictionaries.get("carriers", {}),
            }

            return json.dumps(response, indent=2)

        except Exception as e:
            logger.warning(f"Amadeus API search failed: {e}. Falling back to AI.")

    # Fallback to AI knowledge base
    search_context = {
        "origin": origin_city,
        "destination": destination_city,
        "departure_date": departure_date,
        "return_date": return_date,
        "cabin_class": cabin_class,
        "request_time": datetime.utcnow().isoformat(),
        "source": "ai_knowledge_base",
    }

    return f"""Search flight routes from {origin_city} to {destination_city}.
Departure: {departure_date}, Return: {return_date or 'One-way'}
Cabin Class: {cabin_class}

NOTE: Real-time API not available. Using AI knowledge base for estimates.

Provide detailed information about:
1. Major airlines serving this route
2. Whether direct flights exist
3. Common connection hubs (if no direct flights)
4. Estimated flight times
5. Typical frequency (flights per day/week)
6. Estimated price ranges in USD

Context: {json.dumps(search_context)}"""


@tool("Get Airport Information")
def get_airport_info(city: str, country: str | None = None) -> str:
    """
    Get comprehensive airport information for a city.

    Uses Amadeus API when available for accurate IATA codes and locations.

    Args:
        city: City name or IATA code (e.g., "Paris", "JFK")
        country: Country name for disambiguation (optional, e.g., "France", "USA")

    Returns:
        JSON string with airport information including IATA codes and facilities

    Example:
        >>> get_airport_info("Paris", "France")
    """
    logger.info(f"Getting airport info for: {city}, {country}")

    client = _get_flight_client()

    # Try real API lookup if client is available
    if client and _has_api_credentials():
        try:
            # If city looks like IATA code (3 letters), look it up directly
            if len(city) == 3 and city.isalpha():
                result = client.get_airport_info(city.upper())

                if "error" not in result:
                    response = {
                        "source": "amadeus_api",
                        "airports": [
                            {
                                "iata_code": result["iata_code"],
                                "name": result["name"],
                                "city": result["city"],
                                "country": result["country"],
                                "country_code": result["country_code"],
                                "timezone": result["timezone"],
                                "coordinates": {
                                    "latitude": result["latitude"],
                                    "longitude": result["longitude"],
                                },
                            }
                        ],
                    }
                    return json.dumps(response, indent=2)

        except Exception as e:
            logger.warning(f"Amadeus airport lookup failed: {e}. Falling back to AI.")

    # Fallback to AI knowledge base
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
    logger.info(
        f"Analyzing layover at {layover_airport}: {origin_airline} -> {destination_airline}"
    )

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

    Uses real API data when available, otherwise provides AI-based estimates.

    Args:
        origin: Origin city or IATA code
        destination: Destination city or IATA code
        departure_date: Departure date (YYYY-MM-DD)
        cabin_class: Cabin class (economy, premium_economy, business, first)
        is_direct: Whether it's a direct flight

    Returns:
        JSON with estimated pricing including low/medium/high ranges

    Example:
        >>> estimate_flight_pricing("JFK", "LHR", "2025-07-15", "economy", True)
    """
    logger.info(f"Estimating prices: {origin} -> {destination} on {departure_date}")

    client = _get_flight_client()

    # Try real API search for actual prices
    if client and _has_api_credentials():
        try:
            dep_date = datetime.strptime(departure_date, "%Y-%m-%d").date()

            cabin_map = {
                "economy": "ECONOMY",
                "premium_economy": "PREMIUM_ECONOMY",
                "business": "BUSINESS",
                "first": "FIRST",
            }
            travel_class = cabin_map.get(cabin_class.lower(), "ECONOMY")

            result = client.search_flights(
                origin=origin.upper()[:3],
                destination=destination.upper()[:3],
                departure_date=dep_date,
                travel_class=travel_class,
                non_stop=is_direct,
                max_offers=20,
            )

            if result.offers:
                prices = [o.total_price for o in result.offers]
                currencies = [o.currency for o in result.offers]

                response = {
                    "source": "amadeus_api",
                    "route": f"{origin} → {destination}",
                    "departure_date": departure_date,
                    "cabin_class": cabin_class,
                    "direct_flights_only": is_direct,
                    "pricing": {
                        "low": min(prices),
                        "average": sum(prices) / len(prices),
                        "high": max(prices),
                        "currency": currencies[0] if currencies else "USD",
                        "sample_size": len(prices),
                    },
                    "note": "Prices are real-time from Amadeus API",
                }
                return json.dumps(response, indent=2)

        except Exception as e:
            logger.warning(f"Amadeus pricing search failed: {e}. Falling back to AI.")

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
    origin: str,
    destination: str,
    departure_date: str,
    current_price: float | None = None,
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
        >>> get_booking_timing_advice("Paris", "Tokyo", "2025-08-20", 850.0)
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
