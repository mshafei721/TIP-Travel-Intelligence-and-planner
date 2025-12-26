"""
Tests for Amadeus Flight Client

Covers:
- Input validation
- Token authentication
- Flight search parsing
- Airport info lookup
- Error handling
"""

from datetime import date
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services.flight.amadeus_client import (
    AmadeusFlightClient,
    FlightOffer,
    FlightSearchResult,
    FlightSegment,
)


class TestAmadeusFlightClient:
    """Test suite for AmadeusFlightClient"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return AmadeusFlightClient(
            api_key="test_api_key",
            api_secret="test_api_secret",
            test_mode=True,
        )

    @pytest.fixture
    def mock_token_response(self):
        """Mock OAuth token response"""
        return {
            "access_token": "test_access_token_123",
            "token_type": "Bearer",
            "expires_in": 1800,
        }

    @pytest.fixture
    def mock_flight_response(self):
        """Mock flight search API response"""
        return {
            "data": [
                {
                    "id": "1",
                    "source": "GDS",
                    "instantTicketingRequired": False,
                    "nonHomogeneous": False,
                    "lastTicketingDate": "2025-06-01",
                    "numberOfBookableSeats": 9,
                    "itineraries": [
                        {
                            "duration": "PT7H30M",
                            "segments": [
                                {
                                    "departure": {
                                        "iataCode": "JFK",
                                        "at": "2025-06-15T19:00:00",
                                    },
                                    "arrival": {
                                        "iataCode": "LHR",
                                        "at": "2025-06-16T07:30:00",
                                    },
                                    "carrierCode": "BA",
                                    "number": "178",
                                    "aircraft": {"code": "777"},
                                    "duration": "PT7H30M",
                                    "numberOfStops": 0,
                                }
                            ],
                        }
                    ],
                    "price": {
                        "currency": "USD",
                        "total": "650.00",
                        "grandTotal": "650.00",
                    },
                    "travelerPricings": [
                        {
                            "travelerId": "1",
                            "travelerType": "ADULT",
                            "price": {"total": "650.00"},
                            "fareDetailsBySegment": [
                                {
                                    "cabin": "ECONOMY",
                                    "class": "Y",
                                    "includedCheckedBags": {"weight": 23},
                                }
                            ],
                        }
                    ],
                    "validatingAirlineCodes": ["BA"],
                }
            ],
            "dictionaries": {
                "carriers": {"BA": "British Airways"},
                "aircraft": {"777": "Boeing 777"},
            },
        }

    # ===========================================
    # Input Validation Tests
    # ===========================================

    def test_validate_iata_code_valid(self, client):
        """Test valid IATA code passes validation"""
        # Should not raise
        client._validate_iata_code("JFK", "origin")
        client._validate_iata_code("lhr", "destination")

    def test_validate_iata_code_invalid_length(self, client):
        """Test invalid IATA code length raises error"""
        with pytest.raises(ValueError, match="Must be 3-letter IATA code"):
            client._validate_iata_code("NY", "origin")

    def test_validate_iata_code_invalid_chars(self, client):
        """Test invalid IATA code characters raises error"""
        with pytest.raises(ValueError, match="Must be 3-letter IATA code"):
            client._validate_iata_code("12A", "origin")

    def test_validate_iata_code_empty(self, client):
        """Test empty IATA code raises error"""
        with pytest.raises(ValueError, match="Must be 3-letter IATA code"):
            client._validate_iata_code("", "origin")

    # ===========================================
    # Token Authentication Tests
    # ===========================================

    def test_get_access_token_success(self, client, mock_token_response):
        """Test successful token retrieval"""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_token_response
            mock_response.raise_for_status = MagicMock()
            mock_client.return_value.__enter__.return_value.post.return_value = (
                mock_response
            )

            token = client._get_access_token()

            assert token == "test_access_token_123"
            assert client._access_token == "test_access_token_123"

    def test_get_access_token_cached(self, client, mock_token_response):
        """Test token caching works"""
        import time

        client._access_token = "cached_token"
        client._token_expires_at = time.time() + 1000  # Not expired

        token = client._get_access_token()

        assert token == "cached_token"

    def test_get_access_token_expired_refreshes(self, client, mock_token_response):
        """Test expired token is refreshed"""
        import time

        client._access_token = "old_token"
        client._token_expires_at = time.time() - 100  # Expired

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_token_response
            mock_response.raise_for_status = MagicMock()
            mock_client.return_value.__enter__.return_value.post.return_value = (
                mock_response
            )

            token = client._get_access_token()

            assert token == "test_access_token_123"

    # ===========================================
    # Flight Search Tests
    # ===========================================

    def test_search_flights_success(
        self, client, mock_token_response, mock_flight_response
    ):
        """Test successful flight search"""
        with patch("httpx.Client") as mock_client:
            # Mock token request
            token_response = MagicMock()
            token_response.json.return_value = mock_token_response
            token_response.raise_for_status = MagicMock()

            # Mock search request
            search_response = MagicMock()
            search_response.json.return_value = mock_flight_response
            search_response.raise_for_status = MagicMock()

            # Configure mock to return different responses
            mock_context = mock_client.return_value.__enter__.return_value
            mock_context.post.return_value = token_response
            mock_context.get.return_value = search_response

            result = client.search_flights(
                origin="JFK",
                destination="LHR",
                departure_date=date(2025, 6, 15),
                adults=1,
            )

            assert isinstance(result, FlightSearchResult)
            assert result.origin == "JFK"
            assert result.destination == "LHR"
            assert result.total_offers == 1
            assert len(result.offers) == 1

    def test_search_flights_parses_offer_correctly(
        self, client, mock_token_response, mock_flight_response
    ):
        """Test flight offer parsing"""
        with patch("httpx.Client") as mock_client:
            token_response = MagicMock()
            token_response.json.return_value = mock_token_response
            token_response.raise_for_status = MagicMock()

            search_response = MagicMock()
            search_response.json.return_value = mock_flight_response
            search_response.raise_for_status = MagicMock()

            mock_context = mock_client.return_value.__enter__.return_value
            mock_context.post.return_value = token_response
            mock_context.get.return_value = search_response

            result = client.search_flights(
                origin="JFK",
                destination="LHR",
                departure_date=date(2025, 6, 15),
            )

            offer = result.offers[0]
            assert isinstance(offer, FlightOffer)
            assert offer.total_price == 650.0
            assert offer.currency == "USD"
            assert offer.cabin_class == "ECONOMY"
            assert offer.validating_airline == "BA"
            assert offer.one_way is True
            assert len(offer.outbound_segments) == 1

    def test_search_flights_parses_segment_correctly(
        self, client, mock_token_response, mock_flight_response
    ):
        """Test flight segment parsing"""
        with patch("httpx.Client") as mock_client:
            token_response = MagicMock()
            token_response.json.return_value = mock_token_response
            token_response.raise_for_status = MagicMock()

            search_response = MagicMock()
            search_response.json.return_value = mock_flight_response
            search_response.raise_for_status = MagicMock()

            mock_context = mock_client.return_value.__enter__.return_value
            mock_context.post.return_value = token_response
            mock_context.get.return_value = search_response

            result = client.search_flights(
                origin="JFK",
                destination="LHR",
                departure_date=date(2025, 6, 15),
            )

            segment = result.offers[0].outbound_segments[0]
            assert isinstance(segment, FlightSegment)
            assert segment.departure_airport == "JFK"
            assert segment.arrival_airport == "LHR"
            assert segment.carrier_code == "BA"
            assert segment.carrier_name == "British Airways"
            assert segment.flight_number == "178"

    def test_search_flights_invalid_origin(self, client):
        """Test invalid origin raises error"""
        with pytest.raises(ValueError, match="Invalid origin code"):
            client.search_flights(
                origin="INVALID",
                destination="LHR",
                departure_date=date(2025, 6, 15),
            )

    def test_search_flights_no_adults(self, client):
        """Test zero adults raises error"""
        with pytest.raises(ValueError, match="At least 1 adult passenger required"):
            client.search_flights(
                origin="JFK",
                destination="LHR",
                departure_date=date(2025, 6, 15),
                adults=0,
            )

    # ===========================================
    # Airport Info Tests
    # ===========================================

    def test_get_airport_info_success(self, client, mock_token_response):
        """Test successful airport lookup"""
        mock_airport_response = {
            "data": [
                {
                    "iataCode": "JFK",
                    "name": "John F. Kennedy International Airport",
                    "address": {
                        "cityName": "New York",
                        "countryName": "United States",
                        "countryCode": "US",
                    },
                    "timeZoneOffset": "-05:00",
                    "geoCode": {"latitude": 40.6413, "longitude": -73.7781},
                }
            ]
        }

        with patch("httpx.Client") as mock_client:
            token_response = MagicMock()
            token_response.json.return_value = mock_token_response
            token_response.raise_for_status = MagicMock()

            airport_response = MagicMock()
            airport_response.json.return_value = mock_airport_response
            airport_response.raise_for_status = MagicMock()

            mock_context = mock_client.return_value.__enter__.return_value
            mock_context.post.return_value = token_response
            mock_context.get.return_value = airport_response

            result = client.get_airport_info("JFK")

            assert result["iata_code"] == "JFK"
            assert result["city"] == "New York"
            assert result["country"] == "United States"

    def test_get_airport_info_not_found(self, client, mock_token_response):
        """Test airport not found returns error"""
        with patch("httpx.Client") as mock_client:
            token_response = MagicMock()
            token_response.json.return_value = mock_token_response
            token_response.raise_for_status = MagicMock()

            airport_response = MagicMock()
            airport_response.json.return_value = {"data": []}
            airport_response.raise_for_status = MagicMock()

            mock_context = mock_client.return_value.__enter__.return_value
            mock_context.post.return_value = token_response
            mock_context.get.return_value = airport_response

            result = client.get_airport_info("XXX")

            assert "error" in result

    # ===========================================
    # Data Class Tests
    # ===========================================

    def test_flight_segment_to_dict(self):
        """Test FlightSegment serialization"""
        segment = FlightSegment(
            departure_airport="JFK",
            arrival_airport="LHR",
            departure_time="2025-06-15T19:00:00",
            arrival_time="2025-06-16T07:30:00",
            carrier_code="BA",
            carrier_name="British Airways",
            flight_number="178",
            aircraft="Boeing 777",
            duration="PT7H30M",
            stops=0,
        )

        result = segment.to_dict()

        assert result["departure_airport"] == "JFK"
        assert result["carrier_name"] == "British Airways"

    def test_flight_offer_to_dict(self):
        """Test FlightOffer serialization"""
        segment = FlightSegment(
            departure_airport="JFK",
            arrival_airport="LHR",
            departure_time="2025-06-15T19:00:00",
            arrival_time="2025-06-16T07:30:00",
            carrier_code="BA",
            carrier_name="British Airways",
            flight_number="178",
            aircraft="Boeing 777",
            duration="PT7H30M",
        )

        offer = FlightOffer(
            offer_id="1",
            source="GDS",
            instant_ticketing_required=False,
            non_homogeneous=False,
            one_way=True,
            last_ticketing_date="2025-06-01",
            number_of_bookable_seats=9,
            outbound_segments=[segment],
            return_segments=[],
            total_price=650.0,
            currency="USD",
            price_per_adult=650.0,
            cabin_class="ECONOMY",
            included_baggage="23kg checked bag",
            booking_class="Y",
            validating_airline="BA",
        )

        result = offer.to_dict()

        assert result["total_price"] == 650.0
        assert len(result["outbound_segments"]) == 1

    def test_flight_search_result_to_dict(self):
        """Test FlightSearchResult serialization"""
        segment = FlightSegment(
            departure_airport="JFK",
            arrival_airport="LHR",
            departure_time="2025-06-15T19:00:00",
            arrival_time="2025-06-16T07:30:00",
            carrier_code="BA",
            carrier_name="British Airways",
            flight_number="178",
            aircraft="Boeing 777",
            duration="PT7H30M",
        )

        offer = FlightOffer(
            offer_id="1",
            source="GDS",
            instant_ticketing_required=False,
            non_homogeneous=False,
            one_way=True,
            last_ticketing_date="2025-06-01",
            number_of_bookable_seats=9,
            outbound_segments=[segment],
            return_segments=[],
            total_price=650.0,
            currency="USD",
            price_per_adult=650.0,
            cabin_class="ECONOMY",
            included_baggage="23kg",
            booking_class="Y",
            validating_airline="BA",
        )

        result = FlightSearchResult(
            origin="JFK",
            destination="LHR",
            departure_date="2025-06-15",
            return_date=None,
            adults=1,
            offers=[offer],
            dictionaries={"carriers": {"BA": "British Airways"}},
            total_offers=1,
        )

        dict_result = result.to_dict()

        assert dict_result["origin"] == "JFK"
        assert dict_result["total_offers"] == 1


# ===========================================
# Async Tests (requires pytest-asyncio)
# ===========================================


@pytest.mark.asyncio
class TestAmadeusFlightClientAsync:
    """Async test suite for AmadeusFlightClient"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return AmadeusFlightClient(
            api_key="test_api_key",
            api_secret="test_api_secret",
            test_mode=True,
        )

    @pytest.fixture
    def mock_token_response(self):
        """Mock OAuth token response"""
        return {
            "access_token": "test_access_token_123",
            "token_type": "Bearer",
            "expires_in": 1800,
        }

    @pytest.fixture
    def mock_flight_response(self):
        """Mock flight search API response"""
        return {
            "data": [
                {
                    "id": "1",
                    "source": "GDS",
                    "instantTicketingRequired": False,
                    "nonHomogeneous": False,
                    "itineraries": [
                        {
                            "segments": [
                                {
                                    "departure": {
                                        "iataCode": "JFK",
                                        "at": "2025-06-15T19:00:00",
                                    },
                                    "arrival": {
                                        "iataCode": "LHR",
                                        "at": "2025-06-16T07:30:00",
                                    },
                                    "carrierCode": "BA",
                                    "number": "178",
                                    "aircraft": {"code": "777"},
                                    "duration": "PT7H30M",
                                }
                            ]
                        }
                    ],
                    "price": {"currency": "USD", "grandTotal": "650.00"},
                    "travelerPricings": [
                        {
                            "travelerType": "ADULT",
                            "price": {"total": "650.00"},
                            "fareDetailsBySegment": [{"cabin": "ECONOMY"}],
                        }
                    ],
                    "validatingAirlineCodes": ["BA"],
                }
            ],
            "dictionaries": {"carriers": {"BA": "British Airways"}},
        }

    async def test_search_flights_async_success(
        self, client, mock_token_response, mock_flight_response
    ):
        """Test async flight search"""
        with patch("httpx.AsyncClient") as mock_client:
            token_response = MagicMock()
            token_response.json.return_value = mock_token_response
            token_response.raise_for_status = MagicMock()

            search_response = MagicMock()
            search_response.json.return_value = mock_flight_response
            search_response.raise_for_status = MagicMock()

            mock_context = mock_client.return_value.__aenter__.return_value
            mock_context.post.return_value = token_response
            mock_context.get.return_value = search_response

            result = await client.search_flights_async(
                origin="JFK",
                destination="LHR",
                departure_date=date(2025, 6, 15),
            )

            assert isinstance(result, FlightSearchResult)
            assert result.total_offers == 1


# ===========================================
# Integration Tests (skipped if no API key)
# ===========================================


@pytest.mark.skipif(
    not __import__("app.core.config", fromlist=["settings"]).settings.AMADEUS_API_KEY,
    reason="Amadeus API key not configured",
)
class TestAmadeusFlightClientIntegration:
    """Integration tests with real API (requires credentials)"""

    @pytest.fixture
    def client(self):
        """Create client with real credentials"""
        return AmadeusFlightClient(test_mode=True)

    def test_real_flight_search(self, client):
        """Test real API flight search"""
        result = client.search_flights(
            origin="JFK",
            destination="LHR",
            departure_date=date(2025, 7, 15),
            max_offers=3,
        )

        assert isinstance(result, FlightSearchResult)
        assert result.total_offers > 0
        assert result.offers[0].total_price > 0

    def test_real_airport_lookup(self, client):
        """Test real API airport lookup"""
        result = client.get_airport_info("JFK")

        assert result.get("iata_code") == "JFK"
        assert "New York" in result.get("city", "")
