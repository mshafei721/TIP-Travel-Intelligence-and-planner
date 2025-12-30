"""Flight Agent implementation using CrewAI."""

import json
import logging
import re
from datetime import datetime

from crewai import Agent, Crew

from ..base import BaseAgent
from ..config import AgentConfig, get_llm
from ..interfaces import AgentResult, SourceReference
from .models import (
    Airport,
    CabinClass,
    Flight,
    FlightAgentInput,
    FlightAgentOutput,
    FlightOption,
    FlightSegment,
    AirportInfo,
)
from .prompts import FLIGHT_AGENT_BACKSTORY, FLIGHT_AGENT_GOAL, FLIGHT_AGENT_ROLE
from .tasks import create_flight_search_task
from .tools import (
    analyze_baggage_policies,
    calculate_layover_requirements,
    estimate_flight_pricing,
    get_airport_info,
    get_booking_timing_advice,
    search_flight_routes,
)

logger = logging.getLogger(__name__)


class FlightAgent(BaseAgent):
    """
    Flight Agent for travel flight search and booking recommendations.

    Provides comprehensive flight options, pricing analysis, booking timing
    guidance, and practical travel tips using AI knowledge base and CrewAI framework.

    Features:
    - Flight route search and analysis
    - Price range estimation and booking timing advice
    - Airport information and ground transportation
    - Layover analysis and connection guidance
    - Baggage policy information
    - Seasonal pricing patterns
    - Alternative routing suggestions

    Note:
    Currently uses AI knowledge base for flight information. In production,
    integrate with Amadeus Self-Service API, Skyscanner API, or Kiwi Tequila API
    for real-time flight data and pricing.

    Data Sources:
    - AI knowledge base (routes, airports, airlines)
    - Historical pricing patterns
    - Airline policies and schedules
    """

    @property
    def agent_type(self) -> str:
        """Return agent type identifier."""
        return "flight"

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_model: str = "claude-3-5-sonnet-20241022",
    ):
        """
        Initialize Flight Agent.

        Args:
            config: Agent configuration (optional)
            llm_model: Claude AI model to use
        """
        # Initialize config
        if config is None:
            config = AgentConfig(
                name="Flight Agent",
                agent_type=self.agent_type,
                description="Expert flight search and booking advisor",
                version="1.0.0",
            )

        super().__init__(config)

        # Initialize LLM with fallback support (Anthropic -> Gemini -> OpenAI)
        self.llm = get_llm(temperature=0.15)

        # Create CrewAI agent
        self.agent = self._create_agent()

        logger.info(f"FlightAgent initialized with model: {llm_model}")

    def _create_agent(self) -> Agent:
        """
        Create the CrewAI Flight Agent.

        Returns:
            Configured Agent with flight search tools
        """
        return Agent(
            role=FLIGHT_AGENT_ROLE,
            goal=FLIGHT_AGENT_GOAL,
            backstory=FLIGHT_AGENT_BACKSTORY,
            tools=[
                search_flight_routes,
                get_airport_info,
                calculate_layover_requirements,
                estimate_flight_pricing,
                get_booking_timing_advice,
                analyze_baggage_policies,
            ],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    def run(self, agent_input: FlightAgentInput) -> AgentResult:
        """
        Execute Flight Agent to generate flight recommendations.

        Args:
            agent_input: FlightAgentInput with trip details

        Returns:
            AgentResult with flight recommendations and booking guidance

        Raises:
            Exception: If agent execution fails
        """
        logger.info(
            f"FlightAgent executing for trip {agent_input.trip_id}: "
            f"{agent_input.origin_city} -> {agent_input.destination_city}"
        )

        try:
            # Create task
            task = create_flight_search_task(self.agent, agent_input)

            # Create and execute crew
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)

            result = crew.kickoff()

            # Parse result
            flight_output = self._parse_flight_result(result, agent_input)

            # Create AgentResult
            return AgentResult(
                trip_id=agent_input.trip_id,
                agent_type=self.agent_type,
                data=flight_output.model_dump(),
                generated_at=datetime.utcnow(),
                confidence_score=flight_output.confidence_score,
                sources=[
                    SourceReference(
                        title=source,
                        url=f"internal://flight-source-{source.lower().replace(' ', '-')}",
                        verified_at=datetime.utcnow(),
                    )
                    for source in flight_output.sources
                ],
            )

        except Exception as e:
            logger.error(f"FlightAgent failed: {str(e)}", exc_info=True)
            raise

    def _parse_flight_result(
        self, raw_result: str, agent_input: FlightAgentInput
    ) -> FlightAgentOutput:
        """
        Parse raw CrewAI result into FlightAgentOutput.

        Args:
            raw_result: Raw JSON string from CrewAI
            agent_input: Original input for context

        Returns:
            Validated FlightAgentOutput

        Raises:
            ValueError: If parsing or validation fails
        """
        try:
            # Extract JSON from markdown if present
            json_str = self._extract_json(str(raw_result))

            # Parse JSON
            data = json.loads(json_str)

            # Ensure trip_id is set
            data["trip_id"] = agent_input.trip_id

            # Set defaults if missing
            if "generated_at" not in data:
                data["generated_at"] = datetime.utcnow().isoformat()
            if "confidence_score" not in data:
                data["confidence_score"] = 0.7  # Default confidence
            if "sources" not in data:
                data["sources"] = ["AI knowledge base", "Historical flight data"]

            # Validate and create output model
            output = FlightAgentOutput(**data)

            logger.info(
                f"FlightAgent parsed {len(output.recommended_flights)} flight options "
                f"with confidence {output.confidence_score}"
            )

            return output

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Raw result: {raw_result}")
            raise ValueError(f"Invalid JSON from flight agent: {e}")

        except Exception as e:
            logger.error(f"Failed to parse flight result: {e}")
            raise ValueError(f"Failed to create FlightAgentOutput: {e}")

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from markdown code blocks or raw text.

        Args:
            text: Raw text potentially containing JSON

        Returns:
            Clean JSON string

        Raises:
            ValueError: If no valid JSON found
        """
        # Try to find JSON in markdown code block
        json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        matches = re.findall(json_pattern, text, re.DOTALL)

        if matches:
            return matches[0]

        # Try to find JSON object directly
        json_obj_pattern = r"\{.*\}"
        matches = re.findall(json_obj_pattern, text, re.DOTALL)

        if matches:
            # Return the longest match (most likely to be complete)
            return max(matches, key=len)

        # If no JSON found, assume entire text is JSON
        return text.strip()
