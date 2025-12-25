"""
Tests for Currency Exchange API Client

Tests the fawazahmed0/exchange-api integration.
"""

import pytest
from datetime import date
from app.services.currency import CurrencyExchangeClient, ExchangeRateData


class TestCurrencyExchangeClient:
    """Tests for CurrencyExchangeClient."""

    @pytest.fixture
    def client(self):
        """Create client instance."""
        return CurrencyExchangeClient(timeout=15.0)

    # Basic functionality tests
    def test_client_initialization(self, client):
        """Test client initializes correctly."""
        assert client.timeout == 15.0
        assert client._currencies_cache is None

    def test_get_all_currencies(self, client):
        """Test fetching all available currencies."""
        currencies = client.get_all_currencies()

        assert isinstance(currencies, dict)
        assert len(currencies) > 100  # Should have 200+ currencies
        assert "usd" in currencies
        assert "eur" in currencies
        assert "jpy" in currencies

        # Check cache
        assert client._currencies_cache is not None
        assert client._currencies_cache == currencies

    # Exchange rate tests
    def test_get_exchange_rates_usd_to_jpy(self, client):
        """Test getting USD to JPY exchange rate."""
        rates = client.get_exchange_rates(
            base_currency="usd",
            target_currencies=["jpy"]
        )

        assert isinstance(rates, dict)
        assert "jpy" in rates
        assert isinstance(rates["jpy"], (int, float))
        assert rates["jpy"] > 100  # USD to JPY typically > 100

    def test_get_exchange_rates_eur_to_multiple(self, client):
        """Test getting EUR to multiple currencies."""
        rates = client.get_exchange_rates(
            base_currency="eur",
            target_currencies=["usd", "gbp", "jpy"]
        )

        assert isinstance(rates, dict)
        assert "usd" in rates
        assert "gbp" in rates
        assert "jpy" in rates
        assert all(isinstance(v, (int, float)) for v in rates.values())

    def test_get_exchange_rates_all(self, client):
        """Test getting all exchange rates for a currency."""
        rates = client.get_exchange_rates(base_currency="usd")

        assert isinstance(rates, dict)
        assert len(rates) > 100  # Should have many currencies
        assert "eur" in rates
        assert "jpy" in rates
        assert "gbp" in rates

    def test_get_exchange_rate_single(self, client):
        """Test getting single exchange rate."""
        rate_data = client.get_exchange_rate(
            base_currency="usd",
            target_currency="eur"
        )

        assert isinstance(rate_data, ExchangeRateData)
        assert rate_data.base_currency == "USD"
        assert rate_data.target_currency == "EUR"
        assert isinstance(rate_data.rate, (int, float))
        assert 0.5 < rate_data.rate < 1.5  # Reasonable EUR rate
        assert rate_data.rate_date == date.today()

    def test_get_exchange_rate_case_insensitive(self, client):
        """Test that currency codes are case-insensitive."""
        rate1 = client.get_exchange_rate("USD", "JPY")
        rate2 = client.get_exchange_rate("usd", "jpy")
        rate3 = client.get_exchange_rate("Usd", "Jpy")

        # All should return same rate (within small margin for timing)
        assert rate1.base_currency == rate2.base_currency == rate3.base_currency
        assert rate1.target_currency == rate2.target_currency == rate3.target_currency
        assert abs(rate1.rate - rate2.rate) < 0.1
        assert abs(rate2.rate - rate3.rate) < 0.1

    # Async tests
    @pytest.mark.asyncio
    async def test_aget_exchange_rates(self, client):
        """Test async exchange rates."""
        rates = await client.aget_exchange_rates(
            base_currency="usd",
            target_currencies=["eur", "gbp"]
        )

        assert isinstance(rates, dict)
        assert "eur" in rates
        assert "gbp" in rates

    @pytest.mark.asyncio
    async def test_aget_exchange_rate_single(self, client):
        """Test async single exchange rate."""
        rate_data = await client.aget_exchange_rate(
            base_currency="usd",
            target_currency="jpy"
        )

        assert isinstance(rate_data, ExchangeRateData)
        assert rate_data.base_currency == "USD"
        assert rate_data.target_currency == "JPY"
        assert rate_data.rate > 100

    # Error handling tests
    def test_invalid_base_currency(self, client):
        """Test handling of invalid base currency."""
        with pytest.raises(Exception):  # Will raise httpx or ValueError
            client.get_exchange_rates(base_currency="INVALID")

    def test_invalid_target_currency(self, client):
        """Test handling of invalid target currency."""
        with pytest.raises(ValueError, match="Invalid target currency"):
            client.get_exchange_rate(
                base_currency="usd",
                target_currency="INVALID"
            )

    # Edge cases
    def test_same_currency_conversion(self, client):
        """Test converting currency to itself."""
        rate_data = client.get_exchange_rate(
            base_currency="usd",
            target_currency="usd"
        )

        # USD to USD should be 1.0
        assert rate_data.rate == 1.0

    def test_cryptocurrency_support(self, client):
        """Test that cryptocurrencies are supported."""
        rates = client.get_exchange_rates(
            base_currency="usd",
            target_currencies=["btc"]
        )

        assert "btc" in rates
        assert rates["btc"] > 0  # Should have a rate for Bitcoin

    def test_precious_metals_support(self, client):
        """Test that precious metals are supported."""
        rates = client.get_exchange_rates(
            base_currency="usd",
            target_currencies=["xau"]  # Gold
        )

        assert "xau" in rates
        assert rates["xau"] > 0
