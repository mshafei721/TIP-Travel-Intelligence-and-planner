"""
Currency Agent Pydantic Models

Defines input and output data structures for the Currency Agent.
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator

from ..interfaces import AgentResult


class CurrencyAgentInput(BaseModel):
    """Input model for Currency Agent."""

    trip_id: str = Field(..., description="Unique trip identifier")
    destination_country: str = Field(..., description="Country name or ISO code")
    destination_city: str | None = Field(None, description="Primary destination city")
    departure_date: date = Field(..., description="Trip departure date")
    return_date: date = Field(..., description="Trip return date")
    traveler_nationality: str | None = Field(None, description="Traveler's nationality")
    base_currency: str = Field(default="USD", description="Traveler's base currency (ISO code)")

    @field_validator("destination_country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Ensure country name is not empty."""
        if not v or not v.strip():
            raise ValueError("Destination country cannot be empty")
        return v.strip()

    @field_validator("return_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Ensure return date is after departure date."""
        if "departure_date" in info.data and v < info.data["departure_date"]:
            raise ValueError("Return date must be after departure date")
        return v

    @field_validator("base_currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Normalize currency code."""
        return v.upper().strip()


class LocalCurrency(BaseModel):
    """Local currency information."""

    code: str = Field(..., description="ISO 4217 currency code")
    name: str = Field(..., description="Currency name")
    symbol: str = Field(..., description="Currency symbol")


class CostEstimate(BaseModel):
    """Cost estimate for common items."""

    category: str = Field(..., description="Item category (e.g., 'Meal at restaurant')")
    cost_min: float = Field(..., description="Minimum cost in local currency")
    cost_max: float = Field(..., description="Maximum cost in local currency")
    currency: str = Field(..., description="Currency code")
    notes: str | None = Field(None, description="Additional notes")


class CurrencyAgentOutput(AgentResult):
    """Output model for Currency Agent."""

    # Currency Information
    local_currency: LocalCurrency = Field(..., description="Local currency details")
    exchange_rate: float = Field(..., description="Exchange rate to base currency")
    base_currency: str = Field(..., description="Base currency code (e.g., USD)")

    # ATM & Banking
    atm_availability: str = Field(
        ..., description="ATM availability level (widespread/common/limited/rare)"
    )
    atm_fees: str = Field(..., description="Typical ATM fees and surcharges")
    credit_card_acceptance: str = Field(..., description="Credit card acceptance level")
    recommended_payment_methods: list[str] = Field(..., description="Best payment methods")

    # Tipping & Customs
    tipping_customs: str = Field(..., description="Tipping culture and expectations")
    tipping_percentage: float | None = Field(None, description="Standard tipping percentage")
    bargaining_customs: str | None = Field(None, description="Haggling/bargaining culture")

    # Cost of Living
    cost_of_living_level: str = Field(
        ..., description="Overall cost level (very-low/low/moderate/high/very-high)"
    )
    cost_estimates: list[CostEstimate] = Field(
        ..., description="Typical costs for common items/services"
    )

    # Exchange Tips
    currency_exchange_tips: list[str] = Field(..., description="Tips for exchanging currency")
    best_exchange_locations: list[str] = Field(..., description="Where to exchange currency")
    avoid_exchange_locations: list[str] = Field(..., description="Where to avoid exchanging")

    # Budget Planning
    daily_budget_recommendation: dict[str, float] = Field(
        ..., description="Recommended daily budget by travel style (budget/mid-range/luxury)"
    )

    # Additional Information
    currency_restrictions: str | None = Field(
        None, description="Currency import/export restrictions"
    )
    common_scams: list[str] = Field(
        default_factory=list, description="Common currency-related scams"
    )
    money_safety_tips: list[str] = Field(..., description="Tips for safely handling money")
