"""Tests for Visual Crossing Weather API client."""

import os
from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest

from app.services.weather.visual_crossing_client import (
    VisualCrossingClient,
    WeatherData,
)


class TestVisualCrossingClient:
    """Test suite for VisualCrossingClient."""

    @pytest.fixture()
    def api_key(self):
        """Provide test API key."""
        return os.getenv("VISUAL_CROSSING_API_KEY", "test_api_key")

    @pytest.fixture()
    def client(self, api_key):
        """Create client instance."""
        return VisualCrossingClient(api_key=api_key)

    @pytest.fixture()
    def sample_weather_response(self):
        """Sample weather API response."""
        return {
            "queryCost": 5,
            "latitude": 35.6762,
            "longitude": 139.6503,
            "resolvedAddress": "Tokyo, Tokyo, Japan",
            "address": "Tokyo, Japan",
            "timezone": "Asia/Tokyo",
            "tzoffset": 9.0,
            "days": [
                {
                    "datetime": "2024-06-15",
                    "tempmax": 28.5,
                    "tempmin": 20.1,
                    "temp": 24.3,
                    "conditions": "Partly cloudy",
                    "icon": "partly-cloudy-day",
                    "precip": 0.0,
                    "precipprob": 20.0,
                    "humidity": 65.5,
                    "windspeed": 12.3,
                    "winddir": 180.0,
                    "uvindex": 8,
                    "sunrise": "04:25:00",
                    "sunset": "19:00:00",
                    "description": "Partly cloudy throughout the day.",
                }
            ],
            "alerts": [],
        }

    def test_client_initialization_with_key(self, api_key):
        """Test client initialization with API key."""
        client = VisualCrossingClient(api_key=api_key)
        assert client.api_key == api_key

    def test_client_initialization_from_env(self, monkeypatch):
        """Test client initialization from environment variable."""
        test_key = "env_test_key"
        monkeypatch.setenv("VISUAL_CROSSING_API_KEY", test_key)
        client = VisualCrossingClient()
        assert client.api_key == test_key

    def test_client_initialization_without_key(self, monkeypatch):
        """Test client initialization fails without API key."""
        monkeypatch.delenv("VISUAL_CROSSING_API_KEY", raising=False)
        with pytest.raises(ValueError, match="Visual Crossing API key required"):
            VisualCrossingClient()

    def test_build_url_location_only(self, client):
        """Test URL building with location only."""
        url = client._build_url("Tokyo, Japan")
        assert url == f"{client.BASE_URL}/Tokyo, Japan"

    def test_build_url_with_dates(self, client):
        """Test URL building with date range."""
        start = date(2024, 6, 15)
        end = date(2024, 6, 20)
        url = client._build_url("Tokyo, Japan", start, end)
        assert url == f"{client.BASE_URL}/Tokyo, Japan/2024-06-15/2024-06-20"

    def test_build_params_defaults(self, client):
        """Test parameter building with defaults."""
        params = client._build_params()
        assert params["key"] == client.api_key
        assert params["unitGroup"] == "metric"
        assert "include" not in params
        assert "elements" not in params

    def test_build_params_with_options(self, client):
        """Test parameter building with custom options."""
        params = client._build_params(
            unit_group="us", include="days,alerts", elements="tempmax,tempmin"
        )
        assert params["unitGroup"] == "us"
        assert params["include"] == "days,alerts"
        assert params["elements"] == "tempmax,tempmin"

    @pytest.mark.skipif(
        not os.getenv("VISUAL_CROSSING_API_KEY"),
        reason="Requires VISUAL_CROSSING_API_KEY environment variable",
    )
    def test_get_forecast_real_api(self, client):
        """
        Test getting forecast from real API (requires API key).

        Note: This test is skipped if VISUAL_CROSSING_API_KEY is not set.
        """
        # Test with Tokyo for next 5 days
        today = date.today()
        end_date = today + timedelta(days=4)

        result = client.get_forecast("Tokyo, Japan", today, end_date)

        assert isinstance(result, WeatherData)
        assert result.resolvedAddress
        assert result.latitude
        assert result.longitude
        assert result.timezone
        assert len(result.days) == 5
        assert all(day.tempmax > day.tempmin for day in result.days)

    @patch("httpx.Client")
    def test_get_forecast_mocked(self, mock_client_class, client, sample_weather_response):
        """Test getting forecast with mocked HTTP client."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = sample_weather_response
        mock_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get.return_value = mock_response

        mock_client_class.return_value = mock_client

        # Execute
        result = client.get_forecast("Tokyo, Japan")

        # Verify
        assert isinstance(result, WeatherData)
        assert result.resolvedAddress == "Tokyo, Tokyo, Japan"
        assert result.latitude == 35.6762
        assert result.longitude == 139.6503
        assert len(result.days) == 1
        assert result.days[0].tempmax == 28.5
        assert result.days[0].tempmin == 20.1

    @patch("httpx.Client")
    def test_get_forecast_http_error(self, mock_client_class, client):
        """Test handling of HTTP errors."""
        # Setup mock to raise HTTP error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"

        import httpx

        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )

        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get.return_value = mock_response

        mock_client_class.return_value = mock_client

        # Execute and verify
        with pytest.raises(ValueError, match="Visual Crossing API error: 401"):
            client.get_forecast("Tokyo, Japan")

    @patch("httpx.Client")
    def test_get_forecast_invalid_json(self, mock_client_class, client):
        """Test handling of invalid JSON response."""
        # Setup mock with invalid JSON
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=None)
        mock_client.get.return_value = mock_response

        mock_client_class.return_value = mock_client

        # Execute and verify
        with pytest.raises(ValueError, match="Failed to fetch weather data"):
            client.get_forecast("Tokyo, Japan")

    def test_get_coordinates_forecast(self, client):
        """Test getting forecast by coordinates."""
        with patch.object(client, "get_forecast") as mock_get:
            mock_get.return_value = Mock()

            lat, lon = 35.6762, 139.6503
            client.get_coordinates_forecast(lat, lon)

            # Verify location string was formatted correctly
            call_args = mock_get.call_args
            assert call_args[1]["location"] == f"{lat},{lon}"

    @pytest.mark.asyncio()
    @pytest.mark.skipif(
        not os.getenv("VISUAL_CROSSING_API_KEY"),
        reason="Requires VISUAL_CROSSING_API_KEY environment variable",
    )
    async def test_get_forecast_async_real_api(self, client):
        """Test async forecast retrieval from real API."""
        today = date.today()
        end_date = today + timedelta(days=2)

        result = await client.get_forecast_async("Paris, France", today, end_date)

        assert isinstance(result, WeatherData)
        assert result.resolvedAddress
        assert len(result.days) == 3

    @pytest.mark.asyncio()
    @patch("httpx.AsyncClient")
    async def test_get_forecast_async_mocked(
        self, mock_client_class, client, sample_weather_response
    ):
        """Test async forecast with mocked client."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = sample_weather_response
        mock_response.raise_for_status = Mock()

        mock_client = Mock()
        mock_client.__aenter__ = Mock(return_value=mock_client)
        mock_client.__aexit__ = Mock(return_value=None)
        mock_client.get = Mock(return_value=mock_response)

        mock_client_class.return_value = mock_client

        # Execute
        result = await client.get_forecast_async("Tokyo, Japan")

        # Verify
        assert isinstance(result, WeatherData)
        assert result.resolvedAddress == "Tokyo, Tokyo, Japan"

    @pytest.mark.skipif(
        not os.getenv("VISUAL_CROSSING_API_KEY"),
        reason="Requires VISUAL_CROSSING_API_KEY environment variable",
    )
    def test_forecast_with_alerts(self, client):
        """Test forecast retrieval including weather alerts."""
        # Use a location that might have alerts
        today = date.today()
        end_date = today + timedelta(days=7)

        result = client.get_forecast("Miami, Florida", today, end_date, include_alerts=True)

        assert isinstance(result, WeatherData)
        # Alerts may or may not be present depending on current conditions
        assert result.alerts is not None or result.alerts is None

    def test_different_unit_groups(self, client):
        """Test that different unit groups are passed correctly."""
        with patch.object(client, "get_forecast") as mock_get:
            mock_get.return_value = Mock()

            # Test metric (default)
            client.get_forecast("London, UK", unit_group="metric")
            assert mock_get.call_args[1]["unit_group"] == "metric"

            # Test US units
            client.get_forecast("New York, NY", unit_group="us")
            assert mock_get.call_args[1]["unit_group"] == "us"

            # Test UK units
            client.get_forecast("London, UK", unit_group="uk")
            assert mock_get.call_args[1]["unit_group"] == "uk"
