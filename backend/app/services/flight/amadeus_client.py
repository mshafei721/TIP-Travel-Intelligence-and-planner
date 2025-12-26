"""
Amadeus Flight Search API Client

Provides flight search functionality using the Amadeus Self-Service API.
Free tier available for testing (rate limited).

API Documentation: https://developers.amadeus.com/self-service/category/flights
Python SDK: https://github.com/amadeus4dev/amadeus-python

Features:
- Flight offers search (one-way and round-trip)
- Flight price confirmation
- Airport information lookup
- Sync and async operations
"""

from dataclasses import asdict, dataclass
from datetime import date
from typing import Literal

import httpx

from app.core.config import settings


@dataclass
class FlightSegment:
    """
    A single flight segment (leg) of a journey.

    Attributes:
        departure_airport: IATA airport code (e.g., "JFK")
        arrival_airport: IATA airport code (e.g., "LHR")
        departure_time: ISO 8601 datetime string
        arrival_time: ISO 8601 datetime string
        carrier_code: IATA airline code (e.g., "BA")
        carrier_name: Full airline name
        flight_number: Flight number (e.g., "117")
        aircraft: Aircraft type code
        duration: Flight duration in ISO 8601 duration format (e.g., "PT7H30M")
        stops: Number of stops (0 = non-stop)
    """

    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    carrier_code: str
    carrier_name: str | None
    flight_number: str
    aircraft: str | None
    duration: str
    stops: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class FlightOffer:
    """
    A complete flight offer with pricing.

    Attributes:
        offer_id: Unique offer identifier
        source: Data source ("GDS" for global distribution system)
        instant_ticketing_required: Whether immediate booking is required
        non_homogeneous: Whether different carriers are in the itinerary
        one_way: Whether this is a one-way flight
        last_ticketing_date: Last date to book this offer
        number_of_bookable_seats: Available seats
        outbound_segments: List of outbound flight segments
        return_segments: List of return flight segments (empty for one-way)
        total_price: Total price in the specified currency
        currency: Price currency code
        price_per_adult: Price per adult traveler
        cabin_class: Cabin class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
        included_baggage: Baggage allowance description
        booking_class: Fare booking class code
        validating_airline: Airline validating the ticket
    """

    offer_id: str
    source: str
    instant_ticketing_required: bool
    non_homogeneous: bool
    one_way: bool
    last_ticketing_date: str | None
    number_of_bookable_seats: int
    outbound_segments: list[FlightSegment]
    return_segments: list[FlightSegment]
    total_price: float
    currency: str
    price_per_adult: float
    cabin_class: str
    included_baggage: str | None
    booking_class: str | None
    validating_airline: str | None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = asdict(self)
        result["outbound_segments"] = [s.to_dict() for s in self.outbound_segments]
        result["return_segments"] = [s.to_dict() for s in self.return_segments]
        return result


@dataclass
class FlightSearchResult:
    """
    Complete flight search results.

    Attributes:
        origin: Origin IATA airport code
        destination: Destination IATA airport code
        departure_date: Departure date
        return_date: Return date (None for one-way)
        adults: Number of adult travelers
        offers: List of flight offers
        dictionaries: Reference data (carriers, aircraft, etc.)
        total_offers: Total number of offers found
    """

    origin: str
    destination: str
    departure_date: str
    return_date: str | None
    adults: int
    offers: list[FlightOffer]
    dictionaries: dict
    total_offers: int

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "departure_date": self.departure_date,
            "return_date": self.return_date,
            "adults": self.adults,
            "offers": [o.to_dict() for o in self.offers],
            "dictionaries": self.dictionaries,
            "total_offers": self.total_offers,
        }


class AmadeusFlightClient:
    """
    Amadeus Self-Service API client for flight search.

    Uses OAuth2 for authentication with client credentials flow.
    Supports both synchronous and asynchronous operations.

    Note: Free tier limitations:
    - Rate limited (10 requests/second)
    - Test environment only (no booking)
    - Published rates only (no negotiated rates)
    - Some carriers unavailable (LCCs, American Airlines)

    Example:
        >>> client = AmadeusFlightClient()
        >>> result = client.search_flights(
        ...     origin="JFK",
        ...     destination="LHR",
        ...     departure_date=date(2025, 6, 15),
        ...     adults=2
        ... )
        >>> for offer in result.offers[:3]:
        ...     print(f"{offer.total_price} {offer.currency}")
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        test_mode: bool = True,
    ):
        """
        Initialize Amadeus client.

        Args:
            api_key: Amadeus API Key (defaults to settings.AMADEUS_API_KEY)
            api_secret: Amadeus API Secret (defaults to settings.AMADEUS_API_SECRET)
            test_mode: Use test environment (default True for safety)
        """
        self.api_key = api_key or settings.AMADEUS_API_KEY
        self.api_secret = api_secret or settings.AMADEUS_API_SECRET

        # Use test or production environment
        if test_mode:
            self.base_url = "https://test.api.amadeus.com"
        else:
            self.base_url = "https://api.amadeus.com"

        self._access_token: str | None = None
        self._token_expires_at: float = 0

    def _validate_iata_code(self, code: str, code_type: str) -> None:
        """
        Validate IATA airport code.

        Args:
            code: Airport code to validate
            code_type: Type of code for error messages

        Raises:
            ValueError: If code is invalid
        """
        if not code or len(code) != 3 or not code.isalpha():
            raise ValueError(
                f"Invalid {code_type} code: {code}. Must be 3-letter IATA code"
            )

    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token (with caching).

        Returns:
            Valid access token

        Raises:
            httpx.HTTPError: If authentication fails
        """
        import time

        # Return cached token if still valid
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        # Request new token
        url = f"{self.base_url}/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            result = response.json()

        self._access_token = result["access_token"]
        # Token expires in X seconds, set expiry with 60s buffer
        expires_in = result.get("expires_in", 1800)
        self._token_expires_at = time.time() + expires_in - 60

        return self._access_token

    async def _get_access_token_async(self) -> str:
        """
        Get OAuth2 access token asynchronously (with caching).

        Returns:
            Valid access token

        Raises:
            httpx.HTTPError: If authentication fails
        """
        import time

        # Return cached token if still valid
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        # Request new token
        url = f"{self.base_url}/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            result = response.json()

        self._access_token = result["access_token"]
        expires_in = result.get("expires_in", 1800)
        self._token_expires_at = time.time() + expires_in - 60

        return self._access_token

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date | None = None,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        travel_class: Literal[
            "ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"
        ] = "ECONOMY",
        non_stop: bool = False,
        max_offers: int = 10,
        currency: str = "USD",
    ) -> FlightSearchResult:
        """
        Search for flight offers (synchronous).

        Args:
            origin: Origin IATA airport code (e.g., "JFK")
            destination: Destination IATA airport code (e.g., "LHR")
            departure_date: Departure date
            return_date: Return date (None for one-way)
            adults: Number of adult passengers (12+ years)
            children: Number of child passengers (2-11 years)
            infants: Number of infant passengers (<2 years)
            travel_class: Cabin class preference
            non_stop: Only non-stop flights
            max_offers: Maximum number of offers to return
            currency: Price currency code

        Returns:
            FlightSearchResult with available offers

        Raises:
            ValueError: If input validation fails
            httpx.HTTPError: If API request fails
        """
        # Validate inputs
        self._validate_iata_code(origin, "origin")
        self._validate_iata_code(destination, "destination")

        if adults < 1:
            raise ValueError("At least 1 adult passenger required")

        # Get access token
        token = self._get_access_token()

        # Build request
        url = f"{self.base_url}/v2/shopping/flight-offers"
        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date.isoformat(),
            "adults": adults,
            "travelClass": travel_class,
            "nonStop": str(non_stop).lower(),
            "max": max_offers,
            "currencyCode": currency,
        }

        if return_date:
            params["returnDate"] = return_date.isoformat()
        if children > 0:
            params["children"] = children
        if infants > 0:
            params["infants"] = infants

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return self._parse_search_response(
                response.json(),
                origin.upper(),
                destination.upper(),
                departure_date.isoformat(),
                return_date.isoformat() if return_date else None,
                adults,
            )

    async def search_flights_async(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        return_date: date | None = None,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        travel_class: Literal[
            "ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"
        ] = "ECONOMY",
        non_stop: bool = False,
        max_offers: int = 10,
        currency: str = "USD",
    ) -> FlightSearchResult:
        """
        Search for flight offers (asynchronous).

        Args:
            origin: Origin IATA airport code (e.g., "JFK")
            destination: Destination IATA airport code (e.g., "LHR")
            departure_date: Departure date
            return_date: Return date (None for one-way)
            adults: Number of adult passengers (12+ years)
            children: Number of child passengers (2-11 years)
            infants: Number of infant passengers (<2 years)
            travel_class: Cabin class preference
            non_stop: Only non-stop flights
            max_offers: Maximum number of offers to return
            currency: Price currency code

        Returns:
            FlightSearchResult with available offers

        Raises:
            ValueError: If input validation fails
            httpx.HTTPError: If API request fails
        """
        # Validate inputs
        self._validate_iata_code(origin, "origin")
        self._validate_iata_code(destination, "destination")

        if adults < 1:
            raise ValueError("At least 1 adult passenger required")

        # Get access token
        token = await self._get_access_token_async()

        # Build request
        url = f"{self.base_url}/v2/shopping/flight-offers"
        params = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": departure_date.isoformat(),
            "adults": adults,
            "travelClass": travel_class,
            "nonStop": str(non_stop).lower(),
            "max": max_offers,
            "currencyCode": currency,
        }

        if return_date:
            params["returnDate"] = return_date.isoformat()
        if children > 0:
            params["children"] = children
        if infants > 0:
            params["infants"] = infants

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return self._parse_search_response(
                response.json(),
                origin.upper(),
                destination.upper(),
                departure_date.isoformat(),
                return_date.isoformat() if return_date else None,
                adults,
            )

    def _parse_search_response(
        self,
        data: dict,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None,
        adults: int,
    ) -> FlightSearchResult:
        """
        Parse Amadeus flight search response.

        Args:
            data: API response JSON
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date
            return_date: Return date or None
            adults: Number of adults

        Returns:
            FlightSearchResult with parsed offers
        """
        dictionaries = data.get("dictionaries", {})
        carriers = dictionaries.get("carriers", {})
        aircraft_dict = dictionaries.get("aircraft", {})

        offers = []
        for offer_data in data.get("data", []):
            # Parse itineraries
            itineraries = offer_data.get("itineraries", [])
            outbound_segments = []
            return_segments = []

            for idx, itinerary in enumerate(itineraries):
                segments = []
                for seg in itinerary.get("segments", []):
                    segment = FlightSegment(
                        departure_airport=seg.get("departure", {}).get("iataCode", ""),
                        arrival_airport=seg.get("arrival", {}).get("iataCode", ""),
                        departure_time=seg.get("departure", {}).get("at", ""),
                        arrival_time=seg.get("arrival", {}).get("at", ""),
                        carrier_code=seg.get("carrierCode", ""),
                        carrier_name=carriers.get(seg.get("carrierCode", ""), None),
                        flight_number=seg.get("number", ""),
                        aircraft=aircraft_dict.get(
                            seg.get("aircraft", {}).get("code", ""), None
                        ),
                        duration=seg.get("duration", ""),
                        stops=seg.get("numberOfStops", 0),
                    )
                    segments.append(segment)

                if idx == 0:
                    outbound_segments = segments
                else:
                    return_segments = segments

            # Parse pricing
            price_data = offer_data.get("price", {})
            total_price = float(price_data.get("grandTotal", 0))
            currency = price_data.get("currency", "USD")

            # Get price per adult from traveler pricing
            traveler_pricings = offer_data.get("travelerPricings", [])
            price_per_adult = total_price / adults if adults > 0 else total_price
            if traveler_pricings:
                adult_pricing = next(
                    (
                        tp
                        for tp in traveler_pricings
                        if tp.get("travelerType") == "ADULT"
                    ),
                    None,
                )
                if adult_pricing:
                    price_per_adult = float(
                        adult_pricing.get("price", {}).get("total", price_per_adult)
                    )

            # Get cabin class and baggage from first segment
            cabin_class = "ECONOMY"
            included_baggage = None
            booking_class = None
            if traveler_pricings:
                fare_details = (
                    traveler_pricings[0].get("fareDetailsBySegment", [{}])[0]
                )
                cabin_class = fare_details.get("cabin", "ECONOMY")
                booking_class = fare_details.get("class")
                baggage = fare_details.get("includedCheckedBags", {})
                if baggage:
                    weight = baggage.get("weight")
                    quantity = baggage.get("quantity")
                    if weight:
                        included_baggage = f"{weight}kg checked bag"
                    elif quantity:
                        included_baggage = f"{quantity} checked bag(s)"

            offer = FlightOffer(
                offer_id=offer_data.get("id", ""),
                source=offer_data.get("source", "GDS"),
                instant_ticketing_required=offer_data.get(
                    "instantTicketingRequired", False
                ),
                non_homogeneous=offer_data.get("nonHomogeneous", False),
                one_way=len(itineraries) == 1,
                last_ticketing_date=offer_data.get("lastTicketingDate"),
                number_of_bookable_seats=offer_data.get("numberOfBookableSeats", 0),
                outbound_segments=outbound_segments,
                return_segments=return_segments,
                total_price=total_price,
                currency=currency,
                price_per_adult=price_per_adult,
                cabin_class=cabin_class,
                included_baggage=included_baggage,
                booking_class=booking_class,
                validating_airline=offer_data.get("validatingAirlineCodes", [None])[0],
            )
            offers.append(offer)

        return FlightSearchResult(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            offers=offers,
            dictionaries=dictionaries,
            total_offers=len(offers),
        )

    def get_airport_info(self, iata_code: str) -> dict:
        """
        Get airport information by IATA code.

        Args:
            iata_code: 3-letter IATA airport code

        Returns:
            Airport information dictionary

        Raises:
            ValueError: If IATA code is invalid
            httpx.HTTPError: If API request fails
        """
        self._validate_iata_code(iata_code, "airport")

        token = self._get_access_token()
        url = f"{self.base_url}/v1/reference-data/locations"
        params = {
            "subType": "AIRPORT",
            "keyword": iata_code.upper(),
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Find exact match
            for location in data.get("data", []):
                if location.get("iataCode", "").upper() == iata_code.upper():
                    return {
                        "iata_code": location.get("iataCode"),
                        "name": location.get("name"),
                        "city": location.get("address", {}).get("cityName"),
                        "country": location.get("address", {}).get("countryName"),
                        "country_code": location.get("address", {}).get("countryCode"),
                        "timezone": location.get("timeZoneOffset"),
                        "latitude": location.get("geoCode", {}).get("latitude"),
                        "longitude": location.get("geoCode", {}).get("longitude"),
                    }

            return {"error": f"Airport not found: {iata_code}"}

    async def get_airport_info_async(self, iata_code: str) -> dict:
        """
        Get airport information by IATA code (async).

        Args:
            iata_code: 3-letter IATA airport code

        Returns:
            Airport information dictionary
        """
        self._validate_iata_code(iata_code, "airport")

        token = await self._get_access_token_async()
        url = f"{self.base_url}/v1/reference-data/locations"
        params = {
            "subType": "AIRPORT",
            "keyword": iata_code.upper(),
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            for location in data.get("data", []):
                if location.get("iataCode", "").upper() == iata_code.upper():
                    return {
                        "iata_code": location.get("iataCode"),
                        "name": location.get("name"),
                        "city": location.get("address", {}).get("cityName"),
                        "country": location.get("address", {}).get("countryName"),
                        "country_code": location.get("address", {}).get("countryCode"),
                        "timezone": location.get("timeZoneOffset"),
                        "latitude": location.get("geoCode", {}).get("latitude"),
                        "longitude": location.get("geoCode", {}).get("longitude"),
                    }

            return {"error": f"Airport not found: {iata_code}"}
