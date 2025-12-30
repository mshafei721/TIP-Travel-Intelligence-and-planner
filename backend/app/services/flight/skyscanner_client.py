"""
Skyscanner Flight Search API Client via RapidAPI

Provides flight search functionality using the Skyscanner API through RapidAPI.
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

RAPIDAPI_HOST = "skyscanner44.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}/search"


@dataclass
class FlightSegment:
    """Flight segment information."""
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    carrier_code: str
    carrier_name: str | None
    flight_number: str
    duration: str | None
    stops: int


@dataclass
class FlightOffer:
    """Flight offer details."""
    total_price: float
    currency: str
    cabin_class: str
    validating_airline: str | None
    outbound_segments: list[FlightSegment]
    return_segments: list[FlightSegment]
    included_baggage: str | None
    number_of_bookable_seats: int | None
    last_ticketing_date: str | None
    deep_link: str | None


@dataclass
class FlightSearchResult:
    """Flight search result."""
    origin: str
    destination: str
    departure_date: str
    return_date: str | None
    total_offers: int
    offers: list[FlightOffer]
    dictionaries: dict[str, Any]


class SkyscannerClient:
    """
    Skyscanner API client via RapidAPI.

    Uses the Skyscanner44 API on RapidAPI for flight search.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize Skyscanner client.

        Args:
            api_key: RapidAPI key (defaults to settings.RAPIDAPI_KEY)
        """
        self.api_key = api_key or settings.RAPIDAPI_KEY
        self._client = httpx.Client(timeout=30.0)

    def _headers(self) -> dict[str, str]:
        """Get request headers."""
        return {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": RAPIDAPI_HOST,
        }

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date | None = None,
        adults: int = 1,
        cabin_class: str = "economy",
        non_stop: bool = False,
        max_offers: int = 10,
    ) -> FlightSearchResult:
        """
        Search for flights using Skyscanner API.

        Args:
            origin: Origin airport IATA code (e.g., "JFK")
            destination: Destination airport IATA code (e.g., "LHR")
            departure_date: Departure date
            return_date: Return date (None for one-way)
            adults: Number of adult passengers
            cabin_class: Cabin class (economy, premium_economy, business, first)
            non_stop: Only show non-stop flights
            max_offers: Maximum number of offers to return

        Returns:
            FlightSearchResult with offers
        """
        if not self.api_key:
            logger.warning("RapidAPI key not configured")
            return FlightSearchResult(
                origin=origin,
                destination=destination,
                departure_date=str(departure_date),
                return_date=str(return_date) if return_date else None,
                total_offers=0,
                offers=[],
                dictionaries={},
            )

        try:
            # Build search parameters
            params = {
                "adults": str(adults),
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departureDate": departure_date.isoformat(),
                "currency": "USD",
                "locale": "en-US",
                "market": "US",
            }

            if return_date:
                params["returnDate"] = return_date.isoformat()

            if cabin_class != "economy":
                cabin_map = {
                    "premium_economy": "premium_economy",
                    "business": "business",
                    "first": "first",
                }
                params["cabinClass"] = cabin_map.get(cabin_class, "economy")

            logger.info(f"Searching Skyscanner: {origin} -> {destination} on {departure_date}")

            response = self._client.get(
                RAPIDAPI_BASE_URL,
                headers=self._headers(),
                params=params,
            )

            if response.status_code != 200:
                logger.error(f"Skyscanner API error: {response.status_code} - {response.text}")
                return FlightSearchResult(
                    origin=origin,
                    destination=destination,
                    departure_date=str(departure_date),
                    return_date=str(return_date) if return_date else None,
                    total_offers=0,
                    offers=[],
                    dictionaries={},
                )

            data = response.json()
            offers = self._parse_offers(data, cabin_class, max_offers)

            return FlightSearchResult(
                origin=origin,
                destination=destination,
                departure_date=str(departure_date),
                return_date=str(return_date) if return_date else None,
                total_offers=len(offers),
                offers=offers,
                dictionaries=data.get("context", {}),
            )

        except Exception as e:
            logger.error(f"Skyscanner search error: {e}")
            return FlightSearchResult(
                origin=origin,
                destination=destination,
                departure_date=str(departure_date),
                return_date=str(return_date) if return_date else None,
                total_offers=0,
                offers=[],
                dictionaries={},
            )

    def _parse_offers(
        self,
        data: dict,
        cabin_class: str,
        max_offers: int
    ) -> list[FlightOffer]:
        """Parse Skyscanner API response into FlightOffer objects."""
        offers = []

        # Skyscanner API returns itineraries
        itineraries = data.get("itineraries", {}).get("results", [])

        for itin in itineraries[:max_offers]:
            try:
                pricing = itin.get("pricing_options", [{}])[0]
                price_info = pricing.get("price", {})

                # Parse legs (outbound and return)
                legs = itin.get("legs", [])
                outbound_segments = []
                return_segments = []

                for i, leg in enumerate(legs):
                    segments = []
                    for seg in leg.get("segments", []):
                        segments.append(FlightSegment(
                            departure_airport=seg.get("origin", {}).get("displayCode", ""),
                            arrival_airport=seg.get("destination", {}).get("displayCode", ""),
                            departure_time=seg.get("departure", ""),
                            arrival_time=seg.get("arrival", ""),
                            carrier_code=seg.get("operatingCarrier", {}).get("id", ""),
                            carrier_name=seg.get("operatingCarrier", {}).get("name"),
                            flight_number=str(seg.get("flightNumber", "")),
                            duration=str(seg.get("durationInMinutes", "")) + " min",
                            stops=0,
                        ))

                    if i == 0:
                        outbound_segments = segments
                    else:
                        return_segments = segments

                offers.append(FlightOffer(
                    total_price=float(price_info.get("amount", 0)),
                    currency=price_info.get("currency", "USD"),
                    cabin_class=cabin_class,
                    validating_airline=outbound_segments[0].carrier_name if outbound_segments else None,
                    outbound_segments=outbound_segments,
                    return_segments=return_segments,
                    included_baggage=None,
                    number_of_bookable_seats=None,
                    last_ticketing_date=None,
                    deep_link=pricing.get("items", [{}])[0].get("deepLink"),
                ))

            except Exception as e:
                logger.warning(f"Error parsing offer: {e}")
                continue

        return offers

    def close(self):
        """Close the HTTP client."""
        self._client.close()
