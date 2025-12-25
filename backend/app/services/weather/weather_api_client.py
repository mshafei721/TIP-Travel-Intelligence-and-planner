"""WeatherAPI.com client."""

import os
from datetime import date

import httpx
from pydantic import BaseModel, Field


class CurrentWeather(BaseModel):
    """Current weather data from WeatherAPI.com."""

    temp_c: float = Field(description="Temperature in Celsius")
    temp_f: float = Field(description="Temperature in Fahrenheit")
    condition: dict = Field(description="Weather condition with text and icon")
    wind_kph: float = Field(description="Wind speed in km/h")
    wind_mph: float = Field(description="Wind speed in mph")
    wind_dir: str = Field(description="Wind direction as compass point")
    pressure_mb: float = Field(description="Pressure in millibars")
    precip_mm: float = Field(description="Precipitation in millimeters")
    humidity: int = Field(description="Humidity as percentage")
    cloud: int = Field(description="Cloud cover as percentage")
    feelslike_c: float = Field(description="Feels like temperature in Celsius")
    feelslike_f: float = Field(description="Feels like temperature in Fahrenheit")
    uv: float = Field(description="UV Index")


class Location(BaseModel):
    """Location data from WeatherAPI.com."""

    name: str = Field(description="Location name")
    region: str = Field(description="Region or state")
    country: str = Field(description="Country")
    lat: float = Field(description="Latitude")
    lon: float = Field(description="Longitude")
    tz_id: str = Field(description="Time zone")
    localtime: str = Field(description="Local date and time")


class ForecastDay(BaseModel):
    """Forecast day data from WeatherAPI.com."""

    date: str = Field(description="Forecast date")
    date_epoch: int = Field(description="Forecast date as unix time")
    day: dict = Field(description="Day forecast data including min/max temps")
    astro: dict = Field(description="Astronomical data including sunrise/sunset")
    hour: list[dict] | None = Field(None, description="Hourly forecast data")


class Forecast(BaseModel):
    """Forecast data from WeatherAPI.com."""

    forecastday: list[ForecastDay] = Field(description="Array of forecast days")


class CurrentWeatherResponse(BaseModel):
    """Current weather API response."""

    location: Location = Field(description="Location information")
    current: CurrentWeather = Field(description="Current weather data")


class ForecastWeatherResponse(BaseModel):
    """Forecast weather API response."""

    location: Location = Field(description="Location information")
    current: CurrentWeather = Field(description="Current weather data")
    forecast: Forecast = Field(description="Forecast data")


class WeatherAPIClient:
    """
    Client for WeatherAPI.com.

    Provides access to current weather and forecast data.
    Free tier: 1,000,000 calls/month with 3-day forecast.
    """

    BASE_URL = "http://api.weatherapi.com/v1"

    def __init__(self, api_key: str | None = None):
        """
        Initialize WeatherAPI client.

        Args:
            api_key: WeatherAPI.com API key. If not provided, reads from WEATHERAPI_KEY env var.

        Raises:
            ValueError: If API key is not provided or found in environment.
        """
        self.api_key = api_key or os.getenv("WEATHERAPI_KEY")
        if not self.api_key:
            raise ValueError(
                "WeatherAPI key required. "
                "Provide via api_key parameter or WEATHERAPI_KEY environment variable."
            )

    def get_current_weather(self, location: str, aqi: bool = False) -> CurrentWeatherResponse:
        """
        Get current weather for a location.

        Args:
            location: City name, coordinates (lat,lon), US zipcode, UK postcode,
                     Canada postal code, or IP address
            aqi: Include air quality data (default: False)

        Returns:
            CurrentWeatherResponse object with current weather data

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If response cannot be parsed

        Example:
            >>> client = WeatherAPIClient(api_key="your_key")
            >>> weather = client.get_current_weather("London")
            >>> print(f"Temperature: {weather.current.temp_c}°C")
        """
        url = f"{self.BASE_URL}/current.json"
        params = {
            "key": self.api_key,
            "q": location,
            "aqi": "yes" if aqi else "no",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                return CurrentWeatherResponse(**data)

        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"WeatherAPI error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise ValueError(f"Failed to fetch current weather: {str(e)}") from e

    def get_forecast(
        self,
        location: str,
        days: int = 3,
        aqi: bool = False,
        alerts: bool = False,
    ) -> ForecastWeatherResponse:
        """
        Get weather forecast for a location.

        Args:
            location: City name, coordinates (lat,lon), US zipcode, UK postcode,
                     Canada postal code, or IP address
            days: Number of days of forecast (1-14, free tier limited to 3)
            aqi: Include air quality data (default: False)
            alerts: Include weather alerts (default: False)

        Returns:
            ForecastWeatherResponse object with forecast data

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If response cannot be parsed

        Example:
            >>> client = WeatherAPIClient(api_key="your_key")
            >>> forecast = client.get_forecast("Tokyo", days=3)
            >>> for day in forecast.forecast.forecastday:
            ...     print(f"{day.date}: {day.day['condition']['text']}")
        """
        url = f"{self.BASE_URL}/forecast.json"
        params = {
            "key": self.api_key,
            "q": location,
            "days": str(days),
            "aqi": "yes" if aqi else "no",
            "alerts": "yes" if alerts else "no",
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                return ForecastWeatherResponse(**data)

        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"WeatherAPI error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise ValueError(f"Failed to fetch forecast: {str(e)}") from e

    async def get_current_weather_async(
        self, location: str, aqi: bool = False
    ) -> CurrentWeatherResponse:
        """
        Get current weather for a location (async version).

        Args:
            location: City name, coordinates (lat,lon), US zipcode, UK postcode,
                     Canada postal code, or IP address
            aqi: Include air quality data (default: False)

        Returns:
            CurrentWeatherResponse object with current weather data

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If response cannot be parsed
        """
        url = f"{self.BASE_URL}/current.json"
        params = {
            "key": self.api_key,
            "q": location,
            "aqi": "yes" if aqi else "no",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                return CurrentWeatherResponse(**data)

        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"WeatherAPI error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise ValueError(f"Failed to fetch current weather: {str(e)}") from e

    async def get_forecast_async(
        self,
        location: str,
        days: int = 3,
        aqi: bool = False,
        alerts: bool = False,
    ) -> ForecastWeatherResponse:
        """
        Get weather forecast for a location (async version).

        Args:
            location: City name, coordinates (lat,lon), US zipcode, UK postcode,
                     Canada postal code, or IP address
            days: Number of days of forecast (1-14, free tier limited to 3)
            aqi: Include air quality data (default: False)
            alerts: Include weather alerts (default: False)

        Returns:
            ForecastWeatherResponse object with forecast data

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If response cannot be parsed
        """
        url = f"{self.BASE_URL}/forecast.json"
        params = {
            "key": self.api_key,
            "q": location,
            "days": str(days),
            "aqi": "yes" if aqi else "no",
            "alerts": "yes" if alerts else "no",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                return ForecastWeatherResponse(**data)

        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"WeatherAPI error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise ValueError(f"Failed to fetch forecast: {str(e)}") from e

    def get_coordinates_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 3,
        aqi: bool = False,
        alerts: bool = False,
    ) -> ForecastWeatherResponse:
        """
        Get weather forecast using latitude/longitude coordinates.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days of forecast (1-14, free tier limited to 3)
            aqi: Include air quality data (default: False)
            alerts: Include weather alerts (default: False)

        Returns:
            ForecastWeatherResponse object with forecast data
        """
        location = f"{latitude},{longitude}"
        return self.get_forecast(location=location, days=days, aqi=aqi, alerts=alerts)

    async def get_coordinates_forecast_async(
        self,
        latitude: float,
        longitude: float,
        days: int = 3,
        aqi: bool = False,
        alerts: bool = False,
    ) -> ForecastWeatherResponse:
        """
        Get weather forecast using latitude/longitude coordinates (async).

        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days of forecast (1-14, free tier limited to 3)
            aqi: Include air quality data (default: False)
            alerts: Include weather alerts (default: False)

        Returns:
            ForecastWeatherResponse object with forecast data
        """
        location = f"{latitude},{longitude}"
        return await self.get_forecast_async(
            location=location, days=days, aqi=aqi, alerts=alerts
        )
