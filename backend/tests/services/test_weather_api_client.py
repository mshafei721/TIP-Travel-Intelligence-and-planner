"""Tests for WeatherAPI.com client."""

import os
from unittest.mock import Mock, patch

import httpx
import pytest

from app.services.weather import (
    WeatherAPIClient,
    CurrentWeatherResponse,
    ForecastWeatherResponse,
)


class TestWeatherAPIClient:
    """Test WeatherAPI client initialization and configuration."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        client = WeatherAPIClient(api_key="test_key_123")
        assert client.api_key == "test_key_123"
        assert client.BASE_URL == "http://api.weatherapi.com/v1"

    def test_init_with_env_var(self, monkeypatch):
        """Test initialization with environment variable."""
        monkeypatch.setenv("WEATHERAPI_KEY", "env_key_456")
        client = WeatherAPIClient()
        assert client.api_key == "env_key_456"

    def test_init_without_api_key(self, monkeypatch):
        """Test initialization fails without API key."""
        monkeypatch.delenv("WEATHERAPI_KEY", raising=False)
        with pytest.raises(ValueError, match="WeatherAPI key required"):
            WeatherAPIClient()


class TestGetCurrentWeather:
    """Test current weather endpoint."""

    @pytest.fixture()
    def client(self):
        """Create client instance."""
        return WeatherAPIClient(api_key="test_key")

    @pytest.fixture()
    def mock_current_response(self):
        """Mock current weather response."""
        return {
            "location": {
                "name": "London",
                "region": "City of London, Greater London",
                "country": "United Kingdom",
                "lat": 51.52,
                "lon": -0.11,
                "tz_id": "Europe/London",
                "localtime": "2024-06-15 14:30",
            },
            "current": {
                "temp_c": 20.0,
                "temp_f": 68.0,
                "condition": {"text": "Partly cloudy", "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png"},
                "wind_kph": 15.0,
                "wind_mph": 9.3,
                "wind_dir": "WSW",
                "pressure_mb": 1013.0,
                "precip_mm": 0.0,
                "humidity": 65,
                "cloud": 50,
                "feelslike_c": 20.0,
                "feelslike_f": 68.0,
                "uv": 5.0,
            },
        }

    def test_get_current_weather_success(self, client, mock_current_response):
        """Test successful current weather request."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_current_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            result = client.get_current_weather("London")

            assert isinstance(result, CurrentWeatherResponse)
            assert result.location.name == "London"
            assert result.location.country == "United Kingdom"
            assert result.current.temp_c == 20.0
            assert result.current.condition["text"] == "Partly cloudy"

            # Verify API call
            mock_client.return_value.__enter__.return_value.get.assert_called_once()
            call_args = mock_client.return_value.__enter__.return_value.get.call_args
            assert call_args[0][0] == "http://api.weatherapi.com/v1/current.json"
            assert call_args[1]["params"]["key"] == "test_key"
            assert call_args[1]["params"]["q"] == "London"
            assert call_args[1]["params"]["aqi"] == "no"

    def test_get_current_weather_with_aqi(self, client, mock_current_response):
        """Test current weather request with AQI enabled."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_current_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            client.get_current_weather("London", aqi=True)

            call_args = mock_client.return_value.__enter__.return_value.get.call_args
            assert call_args[1]["params"]["aqi"] == "yes"

    def test_get_current_weather_http_error(self, client):
        """Test handling of HTTP errors."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "401 Unauthorized", request=Mock(), response=mock_response
            )
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            with pytest.raises(ValueError, match="WeatherAPI error: 401"):
                client.get_current_weather("London")

    def test_get_current_weather_coordinates(self, client, mock_current_response):
        """Test current weather with coordinates."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_current_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            client.get_current_weather("51.52,-0.11")

            call_args = mock_client.return_value.__enter__.return_value.get.call_args
            assert call_args[1]["params"]["q"] == "51.52,-0.11"


class TestGetForecast:
    """Test forecast endpoint."""

    @pytest.fixture()
    def client(self):
        """Create client instance."""
        return WeatherAPIClient(api_key="test_key")

    @pytest.fixture()
    def mock_forecast_response(self):
        """Mock forecast response."""
        return {
            "location": {
                "name": "Tokyo",
                "region": "Tokyo",
                "country": "Japan",
                "lat": 35.69,
                "lon": 139.69,
                "tz_id": "Asia/Tokyo",
                "localtime": "2024-06-15 22:30",
            },
            "current": {
                "temp_c": 25.0,
                "temp_f": 77.0,
                "condition": {"text": "Clear", "icon": "//cdn.weatherapi.com/weather/64x64/night/113.png"},
                "wind_kph": 10.0,
                "wind_mph": 6.2,
                "wind_dir": "E",
                "pressure_mb": 1010.0,
                "precip_mm": 0.0,
                "humidity": 70,
                "cloud": 0,
                "feelslike_c": 25.0,
                "feelslike_f": 77.0,
                "uv": 0.0,
            },
            "forecast": {
                "forecastday": [
                    {
                        "date": "2024-06-15",
                        "date_epoch": 1718409600,
                        "day": {
                            "maxtemp_c": 28.5,
                            "mintemp_c": 20.1,
                            "avgtemp_c": 24.3,
                            "maxwind_kph": 15.0,
                            "totalprecip_mm": 0.0,
                            "avghumidity": 65.0,
                            "daily_chance_of_rain": 20,
                            "condition": {"text": "Partly cloudy", "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png"},
                            "uv": 8.0,
                        },
                        "astro": {
                            "sunrise": "04:25 AM",
                            "sunset": "07:00 PM",
                            "moonrise": "11:30 PM",
                            "moonset": "08:15 AM",
                        },
                    }
                ]
            },
        }

    def test_get_forecast_success(self, client, mock_forecast_response):
        """Test successful forecast request."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_forecast_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            result = client.get_forecast("Tokyo", days=3)

            assert isinstance(result, ForecastWeatherResponse)
            assert result.location.name == "Tokyo"
            assert result.current.temp_c == 25.0
            assert len(result.forecast.forecastday) == 1
            assert result.forecast.forecastday[0].date == "2024-06-15"
            assert result.forecast.forecastday[0].day["maxtemp_c"] == 28.5

            # Verify API call
            call_args = mock_client.return_value.__enter__.return_value.get.call_args
            assert call_args[0][0] == "http://api.weatherapi.com/v1/forecast.json"
            assert call_args[1]["params"]["days"] == "3"

    def test_get_forecast_with_alerts(self, client, mock_forecast_response):
        """Test forecast request with alerts enabled."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_forecast_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            client.get_forecast("Tokyo", days=3, alerts=True)

            call_args = mock_client.return_value.__enter__.return_value.get.call_args
            assert call_args[1]["params"]["alerts"] == "yes"

    def test_get_coordinates_forecast(self, client, mock_forecast_response):
        """Test forecast with coordinates."""
        with patch("httpx.Client") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_forecast_response
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response

            result = client.get_coordinates_forecast(35.69, 139.69, days=3)

            assert isinstance(result, ForecastWeatherResponse)
            call_args = mock_client.return_value.__enter__.return_value.get.call_args
            assert call_args[1]["params"]["q"] == "35.69,139.69"


@pytest.mark.skipif(
    not os.getenv("WEATHERAPI_KEY"),
    reason="Requires WEATHERAPI_KEY for integration test",
)
class TestWeatherAPIClientIntegration:
    """Integration tests with real API (requires API key)."""

    @pytest.fixture()
    def client(self):
        """Create client with real API key."""
        return WeatherAPIClient()

    def test_real_current_weather(self, client):
        """Test real API call for current weather."""
        result = client.get_current_weather("London")

        assert isinstance(result, CurrentWeatherResponse)
        assert result.location.name
        assert result.current.temp_c
        assert result.current.condition

    def test_real_forecast(self, client):
        """Test real API call for forecast."""
        result = client.get_forecast("Tokyo", days=3)

        assert isinstance(result, ForecastWeatherResponse)
        assert result.location.name
        assert len(result.forecast.forecastday) > 0
        assert result.forecast.forecastday[0].day

    def test_real_coordinates(self, client):
        """Test real API call with coordinates."""
        result = client.get_coordinates_forecast(40.7128, -74.0060, days=3)

        assert isinstance(result, ForecastWeatherResponse)
        assert result.location.lat
        assert result.location.lon
