"""
Currency Exchange API Client

Uses the free fawazahmed0/exchange-api for currency exchange rates.
API Documentation: https://github.com/fawazahmed0/exchange-api

Features:
- Free & no rate limits
- 200+ currencies including cryptocurrencies and metals
- Daily updated rates
- Historical data support
"""

import logging
from datetime import date, datetime

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExchangeRateData(BaseModel):
    """Exchange rate data model."""

    base_currency: str = Field(..., description="Base currency code (e.g., USD)")
    target_currency: str = Field(..., description="Target currency code (e.g., JPY)")
    rate: float = Field(..., description="Exchange rate")
    rate_date: date = Field(..., description="Date of exchange rate")
    last_updated: datetime = Field(
        default_factory=datetime.utcnow, description="Last updated timestamp"
    )


class CurrencyExchangeClient:
    """
    Client for fawazahmed0/exchange-api.

    Provides free currency exchange rates with no API key required.
    """

    BASE_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{version}/v1"

    def __init__(self, timeout: float = 10.0):
        """
        Initialize the currency exchange client.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self._currencies_cache: dict[str, str] | None = None

    def _get_url(self, version: str = "latest") -> str:
        """Get base URL with version."""
        return self.BASE_URL.format(version=version)

    def get_all_currencies(self) -> dict[str, str]:
        """
        Get list of all available currencies.

        Returns:
            Dictionary mapping currency codes to names
            Example: {"usd": "United States Dollar", "eur": "Euro"}

        Raises:
            httpx.HTTPError: If API request fails
        """
        if self._currencies_cache:
            return self._currencies_cache

        url = f"{self._get_url()}/currencies.json"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                currencies = response.json()

                # Cache the result
                self._currencies_cache = currencies
                logger.info(f"Fetched {len(currencies)} currencies")
                return currencies

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch currencies: {e}")
            raise

    def get_exchange_rates(
        self,
        base_currency: str,
        target_currencies: list[str] | None = None,
        date_str: str | None = None,
    ) -> dict[str, float]:
        """
        Get exchange rates for a base currency.

        Args:
            base_currency: Base currency code (e.g., "usd")
            target_currencies: List of target currency codes. If None, returns all.
            date_str: Date in YYYY-MM-DD format. If None, uses latest.

        Returns:
            Dictionary mapping currency codes to exchange rates
            Example: {"jpy": 149.50, "eur": 0.92}

        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If base currency is invalid
        """
        base_currency = base_currency.lower().strip()

        # Determine version (date or latest)
        version = date_str if date_str else "latest"
        url = f"{self._get_url(version)}/currencies/{base_currency}.json"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()

                # Extract rates
                if base_currency not in data:
                    raise ValueError(f"Invalid base currency: {base_currency}")

                rates = data[base_currency]

                # Filter to target currencies if specified
                if target_currencies:
                    target_currencies_lower = [c.lower() for c in target_currencies]
                    rates = {k: v for k, v in rates.items() if k.lower() in target_currencies_lower}

                logger.info(f"Fetched {len(rates)} exchange rates for {base_currency}")
                return rates

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch exchange rates for {base_currency}: {e}")
            raise

    def get_exchange_rate(
        self, base_currency: str, target_currency: str, date_str: str | None = None
    ) -> ExchangeRateData:
        """
        Get exchange rate between two currencies.

        Args:
            base_currency: Base currency code (e.g., "usd")
            target_currency: Target currency code (e.g., "jpy")
            date_str: Date in YYYY-MM-DD format. If None, uses latest.

        Returns:
            ExchangeRateData with rate information

        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If currencies are invalid
        """
        rates = self.get_exchange_rates(
            base_currency=base_currency, target_currencies=[target_currency], date_str=date_str
        )

        target_currency_lower = target_currency.lower()
        if target_currency_lower not in rates:
            raise ValueError(f"Invalid target currency: {target_currency}")

        rate = rates[target_currency_lower]
        rate_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

        return ExchangeRateData(
            base_currency=base_currency.upper(),
            target_currency=target_currency.upper(),
            rate=rate,
            rate_date=rate_date,
        )

    async def aget_exchange_rates(
        self,
        base_currency: str,
        target_currencies: list[str] | None = None,
        date_str: str | None = None,
    ) -> dict[str, float]:
        """
        Async version of get_exchange_rates.

        Args:
            base_currency: Base currency code (e.g., "usd")
            target_currencies: List of target currency codes. If None, returns all.
            date_str: Date in YYYY-MM-DD format. If None, uses latest.

        Returns:
            Dictionary mapping currency codes to exchange rates

        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If base currency is invalid
        """
        base_currency = base_currency.lower().strip()

        # Determine version (date or latest)
        version = date_str if date_str else "latest"
        url = f"{self._get_url(version)}/currencies/{base_currency}.json"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                # Extract rates
                if base_currency not in data:
                    raise ValueError(f"Invalid base currency: {base_currency}")

                rates = data[base_currency]

                # Filter to target currencies if specified
                if target_currencies:
                    target_currencies_lower = [c.lower() for c in target_currencies]
                    rates = {k: v for k, v in rates.items() if k.lower() in target_currencies_lower}

                logger.info(f"Fetched {len(rates)} exchange rates for {base_currency}")
                return rates

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch exchange rates for {base_currency}: {e}")
            raise

    async def aget_exchange_rate(
        self, base_currency: str, target_currency: str, date_str: str | None = None
    ) -> ExchangeRateData:
        """
        Async version of get_exchange_rate.

        Args:
            base_currency: Base currency code (e.g., "usd")
            target_currency: Target currency code (e.g., "jpy")
            date_str: Date in YYYY-MM-DD format. If None, uses latest.

        Returns:
            ExchangeRateData with rate information

        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If currencies are invalid
        """
        rates = await self.aget_exchange_rates(
            base_currency=base_currency, target_currencies=[target_currency], date_str=date_str
        )

        target_currency_lower = target_currency.lower()
        if target_currency_lower not in rates:
            raise ValueError(f"Invalid target currency: {target_currency}")

        rate = rates[target_currency_lower]
        rate_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()

        return ExchangeRateData(
            base_currency=base_currency.upper(),
            target_currency=target_currency.upper(),
            rate=rate,
            rate_date=rate_date,
        )
