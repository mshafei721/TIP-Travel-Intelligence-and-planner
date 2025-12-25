"""
Tests for Currency Agent

Comprehensive test suite for CurrencyAgent implementation.
"""

from datetime import date, datetime

import pytest

from app.agents.currency import CurrencyAgent, CurrencyAgentInput, CurrencyAgentOutput
from app.agents.currency.models import LocalCurrency


class TestCurrencyAgentInput:
    """Tests for CurrencyAgentInput validation."""

    def test_valid_input(self):
        """Test creating valid input."""
        input_data = CurrencyAgentInput(
            trip_id="trip_123",
            destination_country="Japan",
            destination_city="Tokyo",
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 10),
            traveler_nationality="US",
            base_currency="USD",
        )

        assert input_data.trip_id == "trip_123"
        assert input_data.destination_country == "Japan"
        assert input_data.destination_city == "Tokyo"
        assert input_data.base_currency == "USD"

    def test_empty_country_validation(self):
        """Test that empty country is rejected."""
        with pytest.raises(ValueError, match="Destination country cannot be empty"):
            CurrencyAgentInput(
                trip_id="trip_123",
                destination_country="",
                departure_date=date(2025, 6, 1),
                return_date=date(2025, 6, 10),
            )

    def test_invalid_dates_validation(self):
        """Test that invalid dates are rejected."""
        with pytest.raises(ValueError, match="Return date must be after departure date"):
            CurrencyAgentInput(
                trip_id="trip_123",
                destination_country="Japan",
                departure_date=date(2025, 6, 10),
                return_date=date(2025, 6, 1),  # Before departure
            )

    def test_currency_normalization(self):
        """Test that currency code is normalized to uppercase."""
        input_data = CurrencyAgentInput(
            trip_id="trip_123",
            destination_country="Japan",
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 10),
            base_currency="usd",
        )

        assert input_data.base_currency == "USD"

    def test_default_base_currency(self):
        """Test default base currency is USD."""
        input_data = CurrencyAgentInput(
            trip_id="trip_123",
            destination_country="Japan",
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 10),
        )

        assert input_data.base_currency == "USD"


class TestCurrencyAgent:
    """Tests for CurrencyAgent execution."""

    @pytest.fixture()
    def agent(self):
        """Create CurrencyAgent instance."""
        return CurrencyAgent()

    @pytest.fixture()
    def sample_input(self):
        """Create sample input data."""
        return CurrencyAgentInput(
            trip_id="trip_test_123",
            destination_country="Japan",
            destination_city="Tokyo",
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 10),
            traveler_nationality="US",
            base_currency="USD",
        )

    # Agent configuration tests
    def test_agent_type(self, agent):
        """Test agent type identifier."""
        assert agent.agent_type == "currency"

    def test_agent_config(self, agent):
        """Test agent configuration."""
        config = agent.config
        assert config.name == "Currency Agent"
        assert config.agent_type == "currency"
        assert "currency" in config.description.lower() or "financial" in config.description.lower()
        assert config.version == "1.0.0"

    def test_agent_creation(self, agent):
        """Test CrewAI agent is created."""
        assert agent.agent is not None
        assert len(agent.agent.tools) == 5  # 5 tools

    # Output structure tests
    def test_output_structure(self, agent, sample_input):
        """Test that output has correct structure."""
        result = agent.run(sample_input)

        assert isinstance(result, CurrencyAgentOutput)
        assert result.trip_id == sample_input.trip_id
        assert result.agent_type == "currency"
        assert isinstance(result.generated_at, datetime)
        assert 0.0 <= result.confidence_score <= 1.0

    def test_output_has_currency_info(self, agent, sample_input):
        """Test that output contains currency information."""
        result = agent.run(sample_input)

        assert isinstance(result.local_currency, LocalCurrency)
        assert result.local_currency.code
        assert result.local_currency.name
        assert result.local_currency.symbol
        assert result.exchange_rate > 0
        assert result.base_currency == sample_input.base_currency

    def test_output_has_atm_info(self, agent, sample_input):
        """Test that output contains ATM information."""
        result = agent.run(sample_input)

        assert result.atm_availability in ["widespread", "common", "limited", "rare"]
        assert result.atm_fees
        assert result.credit_card_acceptance in ["widespread", "common", "limited", "rare"]
        assert len(result.recommended_payment_methods) > 0

    def test_output_has_tipping_info(self, agent, sample_input):
        """Test that output contains tipping information."""
        result = agent.run(sample_input)

        assert result.tipping_customs
        # tipping_percentage can be None for countries without tipping

    def test_output_has_cost_info(self, agent, sample_input):
        """Test that output contains cost information."""
        result = agent.run(sample_input)

        assert result.cost_of_living_level in ["very-low", "low", "moderate", "high", "very-high"]
        assert isinstance(result.cost_estimates, list)
        assert isinstance(result.daily_budget_recommendation, dict)
        assert "budget" in result.daily_budget_recommendation
        assert "mid_range" in result.daily_budget_recommendation
        assert "luxury" in result.daily_budget_recommendation

    def test_output_has_exchange_tips(self, agent, sample_input):
        """Test that output contains exchange tips."""
        result = agent.run(sample_input)

        assert len(result.currency_exchange_tips) > 0
        assert len(result.best_exchange_locations) > 0
        assert len(result.avoid_exchange_locations) > 0

    def test_output_has_safety_info(self, agent, sample_input):
        """Test that output contains safety information."""
        result = agent.run(sample_input)

        assert len(result.money_safety_tips) > 0
        # common_scams can be empty list for safe countries

    def test_output_has_sources(self, agent, sample_input):
        """Test that output includes source attribution."""
        result = agent.run(sample_input)

        assert len(result.sources) > 0
        # Should have at least the exchange API source
        source_names = [s.source for s in result.sources]
        assert any("exchange" in s.lower() or "currency" in s.lower() for s in source_names)

    # Different countries tests
    def test_japan_currency(self, agent):
        """Test currency info for Japan."""
        input_data = CurrencyAgentInput(
            trip_id="trip_japan",
            destination_country="Japan",
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 10),
            base_currency="USD",
        )

        result = agent.run(input_data)

        assert result.local_currency.code == "JPY"
        assert "yen" in result.local_currency.name.lower()
        assert result.exchange_rate > 100  # USD to JPY typically > 100

    def test_france_currency(self, agent):
        """Test currency info for France (Euro)."""
        input_data = CurrencyAgentInput(
            trip_id="trip_france",
            destination_country="France",
            departure_date=date(2025, 7, 1),
            return_date=date(2025, 7, 10),
            base_currency="USD",
        )

        result = agent.run(input_data)

        assert result.local_currency.code == "EUR"
        assert "euro" in result.local_currency.name.lower()
        assert 0.5 < result.exchange_rate < 1.5  # Reasonable EUR rate

    def test_uk_currency(self, agent):
        """Test currency info for United Kingdom."""
        input_data = CurrencyAgentInput(
            trip_id="trip_uk",
            destination_country="United Kingdom",
            departure_date=date(2025, 8, 1),
            return_date=date(2025, 8, 10),
            base_currency="USD",
        )

        result = agent.run(input_data)

        assert result.local_currency.code == "GBP"
        assert "pound" in result.local_currency.name.lower()
        assert 0.5 < result.exchange_rate < 1.0  # GBP usually < 1 USD

    # Confidence scoring tests
    def test_confidence_score_range(self, agent, sample_input):
        """Test confidence score is in valid range."""
        result = agent.run(sample_input)

        assert 0.0 <= result.confidence_score <= 1.0

    def test_confidence_increases_with_data(self, agent):
        """Test that more complete data increases confidence."""
        # This test verifies the confidence calculation logic
        complete_result = {
            "local_currency": {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
            "exchange_rate": 149.5,
            "atm_availability": "widespread",
            "credit_card_acceptance": "common",
            "tipping_customs": "Not customary",
            "cost_of_living_level": "high",
            "cost_estimates": [{"category": f"Item {i}"} for i in range(10)],
            "money_safety_tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4"],
            "currency_exchange_tips": ["Tip 1", "Tip 2", "Tip 3"],
        }

        incomplete_result = {
            "local_currency": {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
            "exchange_rate": 149.5,
        }

        complete_conf = agent._calculate_confidence(complete_result)
        incomplete_conf = agent._calculate_confidence(incomplete_result)

        assert complete_conf > incomplete_conf

    # Error handling tests
    def test_handles_parsing_failure_gracefully(self, agent, sample_input):
        """Test that agent handles parsing failures gracefully."""
        # The agent should return fallback data if parsing fails
        result = agent.run(sample_input)

        # Should still return valid output, even if using fallback
        assert isinstance(result, CurrencyAgentOutput)
        assert result.local_currency
        assert result.exchange_rate > 0

    # Helper method tests
    def test_extract_json_from_markdown(self, agent):
        """Test JSON extraction from markdown."""
        markdown_text = """Here is the result:
```json
{"test": "value", "number": 123}
```
That's all."""

        result = agent._extract_json_from_text(markdown_text)
        assert result == {"test": "value", "number": 123}

    def test_extract_json_from_plain_text(self, agent):
        """Test JSON extraction from plain text."""
        text = 'Some text {"test": "value"} more text'

        result = agent._extract_json_from_text(text)
        assert result == {"test": "value"}

    def test_extract_json_handles_invalid(self, agent):
        """Test that JSON extraction handles invalid input."""
        result = agent._extract_json_from_text("Not JSON at all")
        assert result is None
