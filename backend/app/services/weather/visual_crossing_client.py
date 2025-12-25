"""Visual Crossing Weather API client."""

import os
from datetime import date

import httpx
from pydantic import BaseModel, Field


class DailyWeather(BaseModel):
    """Daily weather data from Visual Crossing API."""

    datetime: str = Field(description="Date in YYYY-MM-DD format")
    tempmax: float = Field(description="Maximum temperature")
    tempmin: float = Field(description="Minimum temperature")
    temp: float | None = Field(None, description="Average temperature")
    conditions: str = Field(description="Weather conditions")
    icon: str | None = Field(None, description="Weather icon identifier")
    precip: float | None = Field(None, description="Precipitation amount")
    precipprob: float | None = Field(None, description="Precipitation probability")
    humidity: float | None = Field(None, description="Humidity percentage")
    windspeed: float | None = Field(None, description="Wind speed")
    winddir: float | None = Field(None, description="Wind direction in degrees")
    uvindex: int | None = Field(None, description="UV index")
    sunrise: str | None = Field(None, description="Sunrise time")
    sunset: str | None = Field(None, description="Sunset time")
    description: str | None = Field(None, description="Detailed description")


class WeatherAlert(BaseModel):
    """Weather alert information."""

    event: str = Field(description="Alert event type")
    headline: str = Field(description="Alert headline")
    description: str = Field(description="Alert description")
    severity: str | None = Field(None, description="Alert severity")


class WeatherData(BaseModel):
    """Complete weather data response from Visual Crossing API."""

    queryCost: int | None = Field(None, description="API query cost")
    latitude: float = Field(description="Location latitude")
    longitude: float = Field(description="Location longitude")
    resolvedAddress: str = Field(description="Resolved location address")
    address: str = Field(description="Original address query")
    timezone: str = Field(description="Location timezone")
    tzoffset: float | None = Field(None, description="Timezone offset")
    days: list[DailyWeather] = Field(description="Daily weather data")
    alerts: list[WeatherAlert] | None = Field(None, description="Weather alerts if any")


class VisualCrossingClient:
    """
    Client for Visual Crossing Weather API.

    Provides access to weather forecasts, historical data, and climate information.
    Free tier: 1,000 records/day with 15-day forecast.
    """

    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

    def __init__(self, api_key: str | None = None):
        """
        Initialize Visual Crossing client.

        Args:
            api_key: Visual Crossing API key. If not provided, reads from VISUAL_CROSSING_API_KEY env var.

        Raises:
            ValueError: If API key is not provided or found in environment.
        """
        self.api_key = api_key or os.getenv("VISUAL_CROSSING_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Visual Crossing API key required. "
                "Provide via api_key parameter or VISUAL_CROSSING_API_KEY environment variable."
            )

    def _build_url(
        self,
        location: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> str:
        """
        Build API URL for weather query.

        Args:
            location: City name, coordinates (lat,lon), or address
            start_date: Start date for weather data (optional)
            end_date: End date for weather data (optional)

        Returns:
            Complete API URL
        """
        url = f"{self.BASE_URL}/{location}"

        if start_date:
            url += f"/{start_date.isoformat()}"
            if end_date:
                url += f"/{end_date.isoformat()}"

        return url

    def _build_params(
        self,
        unit_group: str = "metric",
        include: str | None = None,
        elements: str | None = None,
    ) -> dict[str, str]:
        """
        Build query parameters for API request.

        Args:
            unit_group: Unit system (metric, us, uk, base). Default: metric
            include: Sections to include (days, hours, current, alerts)
            elements: Specific elements to include (comma-separated)

        Returns:
            Dictionary of query parameters
        """
        params: dict[str, str] = {
            "key": self.api_key,  # type: ignore
            "unitGroup": unit_group,
        }

        if include:
            params["include"] = include

        if elements:
            params["elements"] = elements

        return params

    def get_forecast(
        self,
        location: str,
        start_date: date | None = None,
        end_date: date | None = None,
        unit_group: str = "metric",
        include_alerts: bool = True,
    ) -> WeatherData:
        """
        Get weather forecast for a location.

        Args:
            location: City name, coordinates (lat,lon), or address
            start_date: Start date for forecast (optional, defaults to today)
            end_date: End date for forecast (optional, defaults to 15 days from start)
            unit_group: Unit system (metric, us, uk, base). Default: metric
            include_alerts: Whether to include weather alerts

        Returns:
            WeatherData object with forecast information

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If response cannot be parsed
        """
        url = self._build_url(location, start_date, end_date)

        include_sections = "days,current"
        if include_alerts:
            include_sections += ",alerts"

        params = self._build_params(
            unit_group=unit_group,
            include=include_sections,
        )

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                return WeatherData(**data)

        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Visual Crossing API error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise ValueError(f"Failed to fetch weather data: {str(e)}") from e

    async def get_forecast_async(
        self,
        location: str,
        start_date: date | None = None,
        end_date: date | None = None,
        unit_group: str = "metric",
        include_alerts: bool = True,
    ) -> WeatherData:
        """
        Get weather forecast for a location (async version).

        Args:
            location: City name, coordinates (lat,lon), or address
            start_date: Start date for forecast (optional, defaults to today)
            end_date: End date for forecast (optional, defaults to 15 days from start)
            unit_group: Unit system (metric, us, uk, base). Default: metric
            include_alerts: Whether to include weather alerts

        Returns:
            WeatherData object with forecast information

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If response cannot be parsed
        """
        url = self._build_url(location, start_date, end_date)

        include_sections = "days,current"
        if include_alerts:
            include_sections += ",alerts"

        params = self._build_params(
            unit_group=unit_group,
            include=include_sections,
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                return WeatherData(**data)

        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Visual Crossing API error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise ValueError(f"Failed to fetch weather data: {str(e)}") from e

    def get_coordinates_forecast(
        self,
        latitude: float,
        longitude: float,
        start_date: date | None = None,
        end_date: date | None = None,
        unit_group: str = "metric",
        include_alerts: bool = True,
    ) -> WeatherData:
        """
        Get weather forecast using latitude/longitude coordinates.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date for forecast (optional)
            end_date: End date for forecast (optional)
            unit_group: Unit system (metric, us, uk, base). Default: metric
            include_alerts: Whether to include weather alerts

        Returns:
            WeatherData object with forecast information
        """
        location = f"{latitude},{longitude}"
        return self.get_forecast(
            location=location,
            start_date=start_date,
            end_date=end_date,
            unit_group=unit_group,
            include_alerts=include_alerts,
        )

    async def get_coordinates_forecast_async(
        self,
        latitude: float,
        longitude: float,
        start_date: date | None = None,
        end_date: date | None = None,
        unit_group: str = "metric",
        include_alerts: bool = True,
    ) -> WeatherData:
        """
        Get weather forecast using latitude/longitude coordinates (async).

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date for forecast (optional)
            end_date: End date for forecast (optional)
            unit_group: Unit system (metric, us, uk, base). Default: metric
            include_alerts: Whether to include weather alerts

        Returns:
            WeatherData object with forecast information
        """
        location = f"{latitude},{longitude}"
        return await self.get_forecast_async(
            location=location,
            start_date=start_date,
            end_date=end_date,
            unit_group=unit_group,
            include_alerts=include_alerts,
        )
