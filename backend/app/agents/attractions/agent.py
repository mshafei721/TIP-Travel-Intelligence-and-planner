"""Attractions Agent implementation using CrewAI."""

import json
import logging
import re
from datetime import UTC, datetime

from crewai import Agent, Crew
from langchain_anthropic import ChatAnthropic

from ..base import BaseAgent
from ..config import AgentConfig, DEFAULT_LLM_MODEL
from ..interfaces import SourceReference
from .models import (
    Attraction,
    AttractionsAgentInput,
    AttractionsAgentOutput,
    HiddenGem,
)
from .prompts import (
    ATTRACTIONS_AGENT_BACKSTORY,
    ATTRACTIONS_AGENT_GOAL,
    ATTRACTIONS_AGENT_ROLE,
)
from .tasks import create_attractions_task
from .tools import (
    get_attraction_details_tool,
    get_city_coordinates_tool,
    search_attractions_tool,
)

# Confidence score thresholds
MIN_TOP_ATTRACTIONS = 8
MIN_HIDDEN_GEMS = 3
MIN_DAY_TRIPS = 2

logger = logging.getLogger(__name__)


class AttractionsAgent(BaseAgent):
    """
    Attractions Agent for tourist attractions and points of interest intelligence.

    Provides comprehensive attractions guidance including must-see landmarks,
    museums, historical sites, natural wonders, hidden gems, day trips, and
    practical visiting information using CrewAI framework and OpenTripMap API.

    Features:
    - Top attractions and must-see landmarks
    - Museums, galleries, and cultural institutions
    - Historical sites and monuments
    - Natural wonders and outdoor spaces
    - Religious and spiritual sites
    - Hidden gems off the beaten path
    - Day trip recommendations
    - Visiting information (hours, fees, booking, accessibility)
    - Photography tips and crowd avoidance strategies

    Data Sources:
    - OpenTripMap API (10M+ attractions worldwide)
    - OpenStreetMap, Wikidata, Wikipedia
    - Tourism knowledge bases
    """

    @property
    def agent_type(self) -> str:
        """Return agent type identifier."""
        return "attractions"

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_model: str = DEFAULT_LLM_MODEL,
    ):
        """
        Initialize Attractions Agent.

        Args:
            config: Agent configuration (optional)
            llm_model: Claude AI model to use
        """
        # Initialize config
        if config is None:
            config = AgentConfig(
                name="Attractions Agent",
                agent_type=self.agent_type,
                description="Tourist attractions and points of interest specialist",
                version="1.0.0",
            )

        super().__init__(config)

        # Initialize Claude AI LLM
        self.llm = ChatAnthropic(
            model=llm_model,
            temperature=0.1,  # Low temperature for factual information
            timeout=60.0,
        )

        # Create CrewAI agent
        self.agent = self._create_agent()

        logger.info("AttractionsAgent initialized with model: %s", llm_model)

    def _create_agent(self) -> Agent:
        """
        Create the CrewAI Attractions Agent.

        Returns:
            Configured CrewAI Agent with attractions intelligence tools
        """
        return Agent(
            role=ATTRACTIONS_AGENT_ROLE,
            goal=ATTRACTIONS_AGENT_GOAL,
            backstory=ATTRACTIONS_AGENT_BACKSTORY,
            llm=self.llm,
            tools=[
                get_city_coordinates_tool,
                search_attractions_tool,
                get_attraction_details_tool,
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

        # Check for required fields (0.5 total)
        required_fields = [
            "top_attractions",
            "estimated_costs",
            "booking_tips",
        ]
        for field in required_fields:
            if result.get(field):
                score += 0.17  # ~0.5 total for required fields

        # Check for top attractions count (0.2)
        top_attractions = result.get("top_attractions", [])
        if top_attractions and len(top_attractions) >= MIN_TOP_ATTRACTIONS:
            score += 0.2

        # Check for hidden gems (0.1)
        hidden_gems = result.get("hidden_gems", [])
        if hidden_gems and len(hidden_gems) >= MIN_HIDDEN_GEMS:
            score += 0.1

        # Check for day trips (0.1)
        day_trips = result.get("day_trips", [])
        if day_trips and len(day_trips) >= MIN_DAY_TRIPS:
            score += 0.1

        # Check for categorized attractions (0.1)
        categorized = [
            result.get("museums_and_galleries"),
            result.get("historical_sites"),
            result.get("natural_attractions"),
        ]
        if all(categorized):
            score += 0.1

        return min(score, 1.0)

    def run(self, input_data: AttractionsAgentInput) -> AttractionsAgentOutput:
        """
        Execute the attractions agent to generate attractions intelligence.

        Args:
            input_data: AttractionsAgentInput with trip details

        Returns:
            AttractionsAgentOutput with comprehensive attractions information

        Raises:
            ValueError: If execution fails or output cannot be parsed
        """
        destination = input_data.destination_city or input_data.destination_country
        logger.info("Running Attractions Agent for %s", destination)

        try:
            # Create attractions task
            task = create_attractions_task(
                agent=self.agent,
                input_data=input_data,
            )

            # Create crew and execute
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)

            # Execute crew
            result = crew.kickoff()
            logger.info("Attractions Agent execution completed")

            # Parse result
            result_text = str(result)
            parsed_result = self._extract_json_from_text(result_text)

            if not parsed_result:
                logger.warning("Could not parse JSON from result, using fallback")
                # Create minimal fallback result
                parsed_result = self._create_fallback_result(input_data)

            # Calculate confidence
            confidence = self._calculate_confidence(parsed_result)
            logger.info("Attractions Agent confidence: %.2f", confidence)

            # Build output model
            now = datetime.now(tz=UTC)
            output = AttractionsAgentOutput(
                trip_id=input_data.trip_id,
                agent_type=self.agent_type,
                generated_at=now,
                confidence_score=confidence,
                sources=[
                    SourceReference(
                        source="OpenTripMap API",
                        url="https://opentripmap.io",
                        retrieved_at=now,
                    ),
                    SourceReference(
                        source="Tourism Knowledge Base",
                        url="internal",
                        retrieved_at=now,
                    ),
                ],
                warnings=[],
                # Top attractions
                top_attractions=parsed_result.get("top_attractions", []),
                # Hidden gems
                hidden_gems=parsed_result.get("hidden_gems", []),
                # Day trips
                day_trips=parsed_result.get("day_trips", []),
                # Categorized attractions
                museums_and_galleries=parsed_result.get("museums_and_galleries", []),
                historical_sites=parsed_result.get("historical_sites", []),
                natural_attractions=parsed_result.get("natural_attractions", []),
                religious_sites=parsed_result.get("religious_sites", []),
                viewpoints_and_landmarks=parsed_result.get(
                    "viewpoints_and_landmarks", []
                ),
                # Estimated costs
                estimated_costs=parsed_result.get(
                    "estimated_costs",
                    {
                        "museums": "$10-$25 per museum",
                        "historical": "$5-$15 per site",
                        "tours": "$30-$100 per tour",
                    },
                ),
                # Booking & practical tips
                booking_tips=parsed_result.get("booking_tips", []),
                crowd_avoidance_tips=parsed_result.get("crowd_avoidance_tips", []),
                photography_tips=parsed_result.get("photography_tips", []),
                # Accessibility
                accessibility_notes=parsed_result.get("accessibility_notes", []),
            )

            logger.info("Attractions Agent completed for %s", destination)

        except Exception as e:
            logger.exception("Attractions Agent execution failed")
            msg = f"Failed to execute Attractions Agent: {e!s}"
            raise ValueError(msg) from e
        else:
            return output

    def _create_fallback_result(self, input_data: AttractionsAgentInput) -> dict:
        """
        Create fallback result when parsing fails.

        Args:
            input_data: Original input data

        Returns:
            Dictionary with minimal attractions information
        """
        destination = (
            input_data.destination_city or input_data.destination_country
        )

        return {
            "top_attractions": [
                Attraction(
                    name=f"Main Square - {destination}",
                    category="viewpoint",
                    description="Central gathering place and starting point for exploration",
                    popularity_score=8,
                ).model_dump(),
                Attraction(
                    name=f"National Museum - {destination}",
                    category="museum",
                    description="Learn about local history, culture, and art",
                    popularity_score=7,
                ).model_dump(),
            ],
            "hidden_gems": [
                HiddenGem(
                    name="Local Market",
                    category="market",
                    description="Authentic local market with fresh produce and crafts",
                    why_hidden="Off the main tourist trail",
                    best_for=["photographers", "culture enthusiasts"],
                ).model_dump()
            ],
            "day_trips": [],
            "museums_and_galleries": [f"National Museum - {destination}"],
            "historical_sites": [f"Historic District - {destination}"],
            "natural_attractions": [],
            "religious_sites": [],
            "viewpoints_and_landmarks": [f"Main Square - {destination}"],
            "estimated_costs": {
                "museums": "$10-$25 per museum",
                "historical": "$5-$15 per site",
                "tours": "$30-$100 per tour",
            },
            "booking_tips": [
                "Book popular attractions online in advance",
                "Consider city tourist cards for savings",
                "Check official websites for latest hours and prices",
            ],
            "crowd_avoidance_tips": [
                "Visit major attractions early morning or late afternoon",
                "Weekdays typically less crowded than weekends",
                "Purchase skip-the-line tickets when available",
            ],
            "photography_tips": [
                "Golden hour (sunrise/sunset) provides best lighting",
                "Check photography restrictions before visiting",
                "Respect local customs and ask before photographing people",
            ],
            "accessibility_notes": [
                "Contact attractions in advance for accessibility information",
                "Many historic sites may have limited accessibility",
                "Major museums typically wheelchair accessible",
            ],
        }
