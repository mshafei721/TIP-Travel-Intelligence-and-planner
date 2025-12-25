"""Currency Agent implementation using CrewAI."""

import json
import logging
import re
from datetime import datetime

from crewai import Agent, Crew
from langchain_anthropic import ChatAnthropic

from ..base import BaseAgent
from ..config import AgentConfig
from ..interfaces import SourceReference
from app.core.config import settings
from .models import (
    CurrencyAgentInput,
    CurrencyAgentOutput,
    LocalCurrency,
)
from .prompts import (
    CURRENCY_AGENT_BACKSTORY,
    CURRENCY_AGENT_GOAL,
    CURRENCY_AGENT_ROLE,
)
from .tasks import (
    create_comprehensive_currency_task,
)
from .tools import (
    get_atm_payment_info,
    get_cost_estimates,
    get_currency_info,
    get_exchange_rates,
    get_tipping_customs,
)

logger = logging.getLogger(__name__)


class CurrencyAgent(BaseAgent):
    """
    Currency Agent for travel financial intelligence.

    Provides comprehensive currency and financial information including exchange rates,
    payment methods, tipping customs, cost estimates, and practical money management tips
    using the free fawazahmed0/exchange-api and CrewAI framework.

    Features:
    - Real-time exchange rates for 200+ currencies
    - ATM availability and fee information
    - Credit card acceptance levels
    - Tipping culture and percentages
    - Cost of living estimates
    - Daily budget recommendations
    - Currency exchange tips
    - Common scams and safety advice

    Data Sources:
    - fawazahmed0/exchange-api (free, no rate limits)
    - Currency and tipping knowledge base
    - Cost of living databases
    """

    @property
    def agent_type(self) -> str:
        """Return agent type identifier."""
        return "currency"

    @property
    def config(self) -> AgentConfig:
        """Return agent configuration."""
        return AgentConfig(
            name="Currency Agent",
            agent_type=self.agent_type,
            description="Travel currency and financial intelligence specialist",
            version="1.0.0",
        )

    def __init__(self, anthropic_api_key: str | None = None):
        """
        Initialize Currency Agent with CrewAI.

        Args:
            anthropic_api_key: Anthropic API key for Claude (defaults to settings)
        """
        super().__init__()

        # Initialize Claude AI (Anthropic)
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,  # Low temperature for factual accuracy
            anthropic_api_key=anthropic_api_key or settings.ANTHROPIC_API_KEY,
        )

        # Initialize CrewAI Agent
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """
        Create the CrewAI Currency Agent.

        Returns:
            Configured CrewAI Agent with currency analysis tools
        """
        return Agent(
            role=CURRENCY_AGENT_ROLE,
            goal=CURRENCY_AGENT_GOAL,
            backstory=CURRENCY_AGENT_BACKSTORY,
            llm=self.llm,
            tools=[
                get_exchange_rates,
                get_currency_info,
                get_atm_payment_info,
                get_tipping_customs,
                get_cost_estimates,
            ],
            verbose=True,
            allow_delegation=False,
        )

    def _extract_json_from_text(self, text: str) -> dict | None:
        """
        Extract JSON from text that may contain markdown or other formatting.

        Args:
            text: Text possibly containing JSON

        Returns:
            Parsed JSON dict or None if extraction fails
        """
        # Try to find JSON block in markdown code fences
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON object
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Try parsing entire text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _calculate_confidence(self, result: dict) -> float:
        """
        Calculate confidence score based on data completeness.

        Args:
            result: Parsed agent result

        Returns:
            Confidence score from 0.0 to 1.0
        """
        score = 0.0
        total_checks = 10

        # Check for required fields (0.6 total)
        required_fields = [
            "local_currency",
            "exchange_rate",
            "atm_availability",
            "credit_card_acceptance",
            "tipping_customs",
            "cost_of_living_level",
        ]
        for field in required_fields:
            if result.get(field):
                score += 0.1

        # Check for cost estimates (0.2)
        if result.get("cost_estimates") and len(result.get("cost_estimates", [])) > 5:
            score += 0.2

        # Check for safety tips (0.1)
        if result.get("money_safety_tips") and len(result.get("money_safety_tips", [])) > 3:
            score += 0.1

        # Check for exchange tips (0.1)
        if (
            result.get("currency_exchange_tips")
            and len(result.get("currency_exchange_tips", [])) > 2
        ):
            score += 0.1

        return min(score, 1.0)

    def run(self, input_data: CurrencyAgentInput) -> CurrencyAgentOutput:
        """
        Execute the currency agent to generate financial intelligence.

        Args:
            input_data: CurrencyAgentInput with trip details

        Returns:
            CurrencyAgentOutput with comprehensive currency and financial information

        Raises:
            ValueError: If execution fails or output cannot be parsed
        """
        logger.info(f"Running Currency Agent for {input_data.destination_country}")

        try:
            # Create comprehensive currency task
            task = create_comprehensive_currency_task(
                agent=self.agent,
                destination_country=input_data.destination_country,
                base_currency=input_data.base_currency,
            )

            # Create crew and execute
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)

            # Execute crew
            result = crew.kickoff()
            logger.info("Currency Agent execution completed")

            # Parse result
            result_text = str(result)
            parsed_result = self._extract_json_from_text(result_text)

            if not parsed_result:
                logger.warning("Could not parse JSON from result, using fallback")
                # Create minimal fallback result
                parsed_result = self._create_fallback_result(input_data)

            # Calculate confidence
            confidence = self._calculate_confidence(parsed_result)
            logger.info(f"Currency Agent confidence: {confidence:.2f}")

            # Build output model
            output = CurrencyAgentOutput(
                trip_id=input_data.trip_id,
                agent_type=self.agent_type,
                generated_at=datetime.utcnow(),
                confidence_score=confidence,
                sources=[
                    SourceReference(
                        source="fawazahmed0/exchange-api",
                        url="https://github.com/fawazahmed0/exchange-api",
                        retrieved_at=datetime.utcnow(),
                    ),
                    SourceReference(
                        source="Currency Knowledge Base",
                        url="internal",
                        retrieved_at=datetime.utcnow(),
                    ),
                ],
                warnings=[],
                # Currency data
                local_currency=parsed_result.get(
                    "local_currency", LocalCurrency(code="USD", name="US Dollar", symbol="$")
                ),
                exchange_rate=parsed_result.get("exchange_rate", 1.0),
                base_currency=input_data.base_currency,
                atm_availability=parsed_result.get("atm_availability", "common"),
                atm_fees=parsed_result.get("atm_fees", "Variable fees apply"),
                credit_card_acceptance=parsed_result.get("credit_card_acceptance", "common"),
                recommended_payment_methods=parsed_result.get(
                    "recommended_payment_methods", ["Cash", "Credit cards"]
                ),
                tipping_customs=parsed_result.get("tipping_customs", "Tipping customs vary"),
                tipping_percentage=parsed_result.get("tipping_percentage"),
                bargaining_customs=parsed_result.get("bargaining_customs"),
                cost_of_living_level=parsed_result.get("cost_of_living_level", "moderate"),
                cost_estimates=parsed_result.get("cost_estimates", []),
                currency_exchange_tips=parsed_result.get(
                    "currency_exchange_tips", ["Use ATMs for best rates", "Avoid airport exchanges"]
                ),
                best_exchange_locations=parsed_result.get(
                    "best_exchange_locations", ["Banks", "ATMs"]
                ),
                avoid_exchange_locations=parsed_result.get(
                    "avoid_exchange_locations", ["Airport kiosks", "Hotels"]
                ),
                daily_budget_recommendation=parsed_result.get(
                    "daily_budget_recommendation",
                    {"budget": 50.0, "mid_range": 100.0, "luxury": 200.0},
                ),
                currency_restrictions=parsed_result.get("currency_restrictions"),
                common_scams=parsed_result.get("common_scams", []),
                money_safety_tips=parsed_result.get(
                    "money_safety_tips", ["Keep valuables secure", "Use ATMs in safe locations"]
                ),
            )

            logger.info(f"Currency Agent completed for {input_data.destination_country}")
            return output

        except Exception as e:
            logger.error(f"Currency Agent execution failed: {e}", exc_info=True)
            raise ValueError(f"Failed to execute Currency Agent: {str(e)}")

    def _create_fallback_result(self, input_data: CurrencyAgentInput) -> dict:
        """
        Create fallback result when parsing fails.

        Args:
            input_data: Original input data

        Returns:
            Dictionary with minimal currency information
        """
        return {
            "local_currency": {"code": "USD", "name": "US Dollar", "symbol": "$"},
            "exchange_rate": 1.0,
            "base_currency": input_data.base_currency,
            "atm_availability": "common",
            "atm_fees": "Fees vary by bank and location",
            "credit_card_acceptance": "common",
            "recommended_payment_methods": ["Cash", "Credit/Debit cards", "ATM withdrawals"],
            "tipping_customs": "Research local tipping customs before your trip",
            "cost_of_living_level": "moderate",
            "cost_estimates": [],
            "currency_exchange_tips": [
                "Use ATMs for best exchange rates",
                "Avoid airport currency exchange kiosks",
                "Notify your bank before traveling",
            ],
            "best_exchange_locations": ["Banks", "ATMs"],
            "avoid_exchange_locations": ["Airport kiosks", "Hotels", "Tourist areas"],
            "daily_budget_recommendation": {"budget": 50.0, "mid_range": 100.0, "luxury": 200.0},
            "money_safety_tips": [
                "Keep cash secure in multiple locations",
                "Use ATMs in well-lit, secure areas",
                "Carry backup payment methods",
            ],
        }
