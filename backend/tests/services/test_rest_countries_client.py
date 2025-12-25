"""
Tests for REST Countries API Client

Tests both sync and async methods with real API calls.
"""

import pytest
import httpx
from app.services.country.rest_countries_client import RestCountriesClient, CountryInfo


class TestRestCountriesClient:
    """Test suite for RestCountriesClient."""

    @pytest.fixture
    def client(self):
        """Create REST Countries client instance."""
        return RestCountriesClient(timeout=10.0)

    # Sync Tests

    def test_get_france_by_name_sync(self, client):
        """Test getting France by name (sync)."""
        result = client.get_country_by_name_sync("France")

        assert isinstance(result, CountryInfo)
        assert result.name_common == "France"
        assert result.cca2 == "FR"
        assert result.cca3 == "FRA"
        assert "Paris" in result.capital
        assert result.region == "Europe"
        assert result.subregion == "Western Europe"
        assert result.population > 60_000_000
        assert "French" in result.languages.values()
        assert result.car_side == "right"
        assert len(result.currencies) > 0

    def test_get_usa_by_code_sync(self, client):
        """Test getting USA by ISO code (sync)."""
        result = client.get_country_by_code_sync("US")

        assert isinstance(result, CountryInfo)
        assert result.name_common == "United States"
        assert result.cca2 == "US"
        assert result.cca3 == "USA"
        assert "Washington, D.C." in result.capital
        assert result.region == "Americas"
        assert result.car_side == "right"
        assert "English" in result.languages.values()

    def test_get_japan_by_name_sync(self, client):
        """Test getting Japan by name (sync)."""
        result = client.get_country_by_name_sync("Japan")

        assert isinstance(result, CountryInfo)
        assert result.name_common == "Japan"
        assert result.cca2 == "JP"
        assert "Tokyo" in result.capital
        assert result.region == "Asia"
        assert result.car_side == "left"  # Japan drives on left
        assert "Japanese" in result.languages.values()

    def test_invalid_country_name_sync(self, client):
        """Test error handling for invalid country name (sync)."""
        with pytest.raises(ValueError, match="Country not found"):
            client.get_country_by_name_sync("InvalidCountryXYZ123")

    def test_empty_country_name_sync(self, client):
        """Test error handling for empty country name (sync)."""
        with pytest.raises(ValueError, match="Country name cannot be empty"):
            client.get_country_by_name_sync("")

    def test_invalid_country_code_sync(self, client):
        """Test error handling for invalid country code (sync)."""
        with pytest.raises(ValueError, match="Country not found"):
            client.get_country_by_code_sync("ZZ")

    def test_empty_country_code_sync(self, client):
        """Test error handling for empty country code (sync)."""
        with pytest.raises(ValueError, match="Country code cannot be empty"):
            client.get_country_by_code_sync("")

    def test_invalid_code_length_sync(self, client):
        """Test error handling for invalid code length (sync)."""
        with pytest.raises(ValueError, match="Invalid country code"):
            client.get_country_by_code_sync("ABCD")

    # Async Tests

    @pytest.mark.asyncio
    async def test_get_france_by_name_async(self, client):
        """Test getting France by name (async)."""
        async with client:
            result = await client.get_country_by_name("France")

            assert isinstance(result, CountryInfo)
            assert result.name_common == "France"
            assert result.cca2 == "FR"
            assert "Paris" in result.capital
            assert result.region == "Europe"

    @pytest.mark.asyncio
    async def test_get_usa_by_code_async(self, client):
        """Test getting USA by ISO code (async)."""
        async with client:
            result = await client.get_country_by_code("US")

            assert isinstance(result, CountryInfo)
            assert result.name_common == "United States"
            assert result.cca2 == "US"
            assert "Washington, D.C." in result.capital

    @pytest.mark.asyncio
    async def test_invalid_country_name_async(self, client):
        """Test error handling for invalid country name (async)."""
        async with client:
            with pytest.raises(ValueError, match="Country not found"):
                await client.get_country_by_name("InvalidCountryXYZ123")

    @pytest.mark.asyncio
    async def test_empty_country_name_async(self, client):
        """Test error handling for empty country name (async)."""
        async with client:
            with pytest.raises(ValueError, match="Country name cannot be empty"):
                await client.get_country_by_name("")

    @pytest.mark.asyncio
    async def test_multiple_requests_async(self, client):
        """Test multiple async requests."""
        async with client:
            france = await client.get_country_by_name("France")
            japan = await client.get_country_by_name("Japan")
            usa = await client.get_country_by_code("US")

            assert france.cca2 == "FR"
            assert japan.cca2 == "JP"
            assert usa.cca2 == "US"

    # Edge Cases

    def test_country_with_multiple_capitals(self, client):
        """Test country with multiple capitals (South Africa)."""
        result = client.get_country_by_name_sync("South Africa")

        assert result.cca2 == "ZA"
        # South Africa has 3 capitals
        assert len(result.capital) >= 3

    def test_small_island_nation(self, client):
        """Test small island nation (Maldives)."""
        result = client.get_country_by_name_sync("Maldives")

        assert result.cca2 == "MV"
        assert result.region == "Asia"
        assert result.area is not None
        assert result.area < 1000  # Very small area

    def test_landlocked_country(self, client):
        """Test landlocked country (Switzerland)."""
        result = client.get_country_by_name_sync("Switzerland")

        assert result.cca2 == "CH"
        assert result.borders is not None
        assert len(result.borders) > 0  # Has land borders

    def test_country_with_no_borders(self, client):
        """Test island nation with no land borders (Australia)."""
        result = client.get_country_by_name_sync("Australia")

        assert result.cca2 == "AU"
        # Australia is an island continent with no land borders
        assert result.borders is None or len(result.borders) == 0
