"""
REST Countries API Client

Provides access to comprehensive country data from restcountries.com API.

API Documentation: https://restcountries.com/
"""

import httpx
from typing import Optional
from pydantic import BaseModel, Field


class CountryInfo(BaseModel):
    """Country information from REST Countries API."""

    name_common: str = Field(..., description="Common country name")
    name_official: str = Field(..., description="Official country name")
    cca2: str = Field(..., description="ISO 3166-1 alpha-2 code")
    cca3: str = Field(..., description="ISO 3166-1 alpha-3 code")
    capital: list[str] = Field(default_factory=list, description="Capital cities")
    region: str = Field(..., description="Geographic region")
    subregion: Optional[str] = Field(None, description="Geographic subregion")
    population: int = Field(..., description="Population")
    area: Optional[float] = Field(None, description="Area in km²")
    languages: dict[str, str] = Field(
        default_factory=dict, description="Languages (code: name)"
    )
    timezones: list[str] = Field(default_factory=list, description="Time zones")
    latlng: Optional[list[float]] = Field(None, description="Coordinates [lat, lng]")
    borders: Optional[list[str]] = Field(None, description="Bordering country codes")
    currencies: dict[str, dict[str, str]] = Field(
        default_factory=dict, description="Currencies (code: {name, symbol})"
    )
    idd_root: Optional[str] = Field(None, description="International dialing root")
    idd_suffixes: Optional[list[str]] = Field(None, description="Dialing suffixes")
    car_side: str = Field(..., description="Driving side: 'left' or 'right'")
    flags_svg: Optional[str] = Field(None, description="SVG flag URL")
    flags_png: Optional[str] = Field(None, description="PNG flag URL")


class RestCountriesClient:
    """Client for REST Countries API."""

    BASE_URL = "https://restcountries.com/v3.1"

    def __init__(self, timeout: float = 10.0):
        """
        Initialize REST Countries client.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _parse_country_response(self, data: dict) -> CountryInfo:
        """
        Parse country data from API response.

        Args:
            data: Raw API response dictionary

        Returns:
            CountryInfo object
        """
        return CountryInfo(
            name_common=data.get("name", {}).get("common", "Unknown"),
            name_official=data.get("name", {}).get("official", "Unknown"),
            cca2=data.get("cca2", ""),
            cca3=data.get("cca3", ""),
            capital=data.get("capital", []),
            region=data.get("region", "Unknown"),
            subregion=data.get("subregion"),
            population=data.get("population", 0),
            area=data.get("area"),
            languages=data.get("languages", {}),
            timezones=data.get("timezones", []),
            latlng=data.get("latlng"),
            borders=data.get("borders"),
            currencies=data.get("currencies", {}),
            idd_root=data.get("idd", {}).get("root"),
            idd_suffixes=data.get("idd", {}).get("suffixes"),
            car_side=data.get("car", {}).get("side", "right"),
            flags_svg=data.get("flags", {}).get("svg"),
            flags_png=data.get("flags", {}).get("png"),
        )

    async def get_country_by_name(self, name: str) -> CountryInfo:
        """
        Get country information by name.

        Args:
            name: Country name (common or official)

        Returns:
            CountryInfo object

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If country not found or invalid response
        """
        if not name or not name.strip():
            raise ValueError("Country name cannot be empty")

        url = f"{self.BASE_URL}/name/{name.strip()}"

        try:
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data, list):
                raise ValueError(f"Invalid API response for country: {name}")

            # API returns a list, take the first match
            country_data = data[0]
            return self._parse_country_response(country_data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Country not found: {name}")
            raise

    async def get_country_by_code(self, code: str) -> CountryInfo:
        """
        Get country information by ISO code.

        Args:
            code: ISO 3166-1 alpha-2 or alpha-3 code (e.g., 'US', 'USA')

        Returns:
            CountryInfo object

        Raises:
            httpx.HTTPStatusError: If API request fails
            ValueError: If country not found or invalid response
        """
        if not code or not code.strip():
            raise ValueError("Country code cannot be empty")

        code = code.strip().upper()

        # Validate code length (2 or 3 characters)
        if len(code) not in [2, 3]:
            raise ValueError(f"Invalid country code: {code}")

        url = f"{self.BASE_URL}/alpha/{code}"

        try:
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data, dict):
                raise ValueError(f"Invalid API response for code: {code}")

            return self._parse_country_response(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Country not found with code: {code}")
            raise

    def get_country_by_name_sync(self, name: str) -> CountryInfo:
        """
        Synchronous version of get_country_by_name.

        Args:
            name: Country name

        Returns:
            CountryInfo object
        """
        if not name or not name.strip():
            raise ValueError("Country name cannot be empty")

        url = f"{self.BASE_URL}/name/{name.strip()}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()

                if not data or not isinstance(data, list):
                    raise ValueError(f"Invalid API response for country: {name}")

                country_data = data[0]
                return self._parse_country_response(country_data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Country not found: {name}")
            raise

    def get_country_by_code_sync(self, code: str) -> CountryInfo:
        """
        Synchronous version of get_country_by_code.

        Args:
            code: ISO 3166-1 alpha-2 or alpha-3 code

        Returns:
            CountryInfo object
        """
        if not code or not code.strip():
            raise ValueError("Country code cannot be empty")

        code = code.strip().upper()

        if len(code) not in [2, 3]:
            raise ValueError(f"Invalid country code: {code}")

        url = f"{self.BASE_URL}/alpha/{code}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()

                if not data or not isinstance(data, dict):
                    raise ValueError(f"Invalid API response for code: {code}")

                return self._parse_country_response(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Country not found with code: {code}")
            raise
