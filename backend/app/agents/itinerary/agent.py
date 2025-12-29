"""Itinerary Agent implementation using CrewAI."""

import json
import logging
import re
from datetime import datetime

from crewai import Agent, Crew
from langchain_anthropic import ChatAnthropic

from ..base import BaseAgent
from ..config import AgentConfig
from ..interfaces import SourceReference
from .models import ItineraryAgentInput, ItineraryAgentOutput
from .prompts import (
    ITINERARY_AGENT_BACKSTORY,
    ITINERARY_AGENT_GOAL,
    ITINERARY_AGENT_ROLE,
)
from .tasks import create_itinerary_task
from .tools import (
    calculate_trip_duration,
    estimate_activity_duration,
    estimate_daily_budget,
    estimate_transportation_time,
    generate_meal_suggestions,
    optimize_daily_schedule,
)

logger = logging.getLogger(__name__)


class ItineraryAgent(BaseAgent):
    """
    Itinerary Agent for comprehensive trip itinerary generation.

    Synthesizes data from all other agents (visa, country, weather, currency,
    culture, food, attractions) to create optimized day-by-day trip plans.

    Features:
    - Day-by-day activity planning with optimal sequencing
    - Geographic clustering to minimize travel time
    - Budget-optimized activity and meal suggestions
    - Transportation planning and cost estimates
    - Accommodation recommendations
    - Balanced pacing (relaxed, moderate, packed)
    - Flexible alternatives for weather or preference changes
    - Packing checklists and pro tips

    Data Sources:
    - Synthesizes all other agent outputs
    - Local knowledge bases
    - Activity timing and logistics optimization
    """

    @property
    def agent_type(self) -> str:
        """Return agent type identifier."""
        return "itinerary"

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_model: str = "claude-3-5-sonnet-20241022",
    ):
        """
        Initialize Itinerary Agent.

        Args:
            config: Agent configuration (optional)
            llm_model: Claude AI model to use
        """
        # Initialize config
        if config is None:
            config = AgentConfig(
                name="Itinerary Agent",
                agent_type=self.agent_type,
                description="Expert trip itinerary planner and optimizer",
                version="1.0.0",
            )

        super().__init__(config)

        # Initialize Claude AI LLM
        self.llm = ChatAnthropic(
            model=llm_model,
            temperature=0.2,  # Slightly higher for creative itinerary planning
            timeout=90.0,  # Longer timeout for complex planning
        )

        # Create CrewAI agent
        self.agent = self._create_agent()

        logger.info(f"ItineraryAgent initialized with model: {llm_model}")

    def _create_agent(self) -> Agent:
        """
        Create the CrewAI Itinerary Agent.

        Returns:
            Configured CrewAI Agent with itinerary planning tools
        """
        return Agent(
            role=ITINERARY_AGENT_ROLE,
            goal=ITINERARY_AGENT_GOAL,
            backstory=ITINERARY_AGENT_BACKSTORY,
            llm=self.llm,
            tools=[
                calculate_trip_duration,
                estimate_activity_duration,
                estimate_transportation_time,
                optimize_daily_schedule,
                estimate_daily_budget,
                generate_meal_suggestions,
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
        Calculate confidence score based on itinerary completeness.

        Args:
            result: Parsed agent result

        Returns:
            Confidence score from 0.0 to 1.0
        """
        score = 0.0

        # Check for required fields (0.4 total)
        required_fields = [
            "daily_plans",
            "total_estimated_cost",
            "accommodation_suggestions",
        ]
        for field in required_fields:
            if result.get(field):
                score += 0.13

        # Check for daily plans completeness (0.3)
        daily_plans = result.get("daily_plans", [])
        if daily_plans:
            score += 0.1
            # Check if each day has activities
            days_with_activities = sum(
                1
                for day in daily_plans
                if (
                    day.get("morning_activities")
                    or day.get("afternoon_activities")
                    or day.get("evening_activities")
                )
            )
            if days_with_activities > 0:
                completeness = days_with_activities / len(daily_plans)
                score += 0.2 * completeness

        # Check for accommodation suggestions (0.1)
        if result.get("accommodation_suggestions") and len(
            result.get("accommodation_suggestions", [])
        ) >= 2:
            score += 0.1

        # Check for optimization notes (0.1)
        if result.get("optimization_notes") and len(result.get("optimization_notes", [])) >= 2:
            score += 0.1

        # Check for pro tips and packing (0.1)
        if result.get("pro_tips") or result.get("packing_checklist"):
            score += 0.1

        return min(score, 1.0)

    def run(self, input_data: ItineraryAgentInput) -> ItineraryAgentOutput:
        """
        Execute the itinerary agent to generate comprehensive trip plan.

        Args:
            input_data: ItineraryAgentInput with trip and traveler details

        Returns:
            ItineraryAgentOutput with complete day-by-day itinerary

        Raises:
            ValueError: If execution fails or output cannot be parsed
        """
        logger.info(
            f"Running Itinerary Agent for {input_data.destination_city or input_data.destination_country}"
        )
        logger.info(f"Trip duration: {(input_data.return_date - input_data.departure_date).days} days")
        logger.info(f"Budget level: {input_data.budget_level}, Pace: {input_data.pace}")

        try:
            # Create itinerary task
            task = create_itinerary_task(
                agent=self.agent,
                input_data=input_data,
            )

            # Create crew and execute
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)

            # Execute crew
            result = crew.kickoff()
            logger.info("Itinerary Agent execution completed")

            # Parse result
            result_text = str(result)
            parsed_result = self._extract_json_from_text(result_text)

            if not parsed_result:
                logger.warning("Could not parse JSON from result, using fallback")
                parsed_result = self._create_fallback_result(input_data)

            # Calculate confidence
            confidence = self._calculate_confidence(parsed_result)
            logger.info(f"Itinerary Agent confidence: {confidence:.2f}")

            # Build output model
            output = ItineraryAgentOutput(
                trip_id=input_data.trip_id,
                agent_type=self.agent_type,
                generated_at=datetime.utcnow(),
                confidence_score=confidence,
                sources=[
                    SourceReference(
                        title="Itinerary Planning Algorithm",
                        url="internal://itinerary-planning-algorithm",
                        verified_at=datetime.utcnow(),
                    ),
                    SourceReference(
                        title="Destination Knowledge Base",
                        url="internal://destination-knowledge-base",
                        verified_at=datetime.utcnow(),
                    ),
                ],
                warnings=[],
                # Core itinerary data
                daily_plans=parsed_result.get("daily_plans", []),
                total_estimated_cost=parsed_result.get("total_estimated_cost"),
                cost_breakdown=parsed_result.get("cost_breakdown"),
                transportation_plan=parsed_result.get("transportation_plan"),
                getting_around_tips=parsed_result.get("getting_around_tips"),
                accommodation_suggestions=parsed_result.get("accommodation_suggestions", []),
                optimization_notes=parsed_result.get("optimization_notes"),
                packing_checklist=parsed_result.get("packing_checklist"),
                pro_tips=parsed_result.get("pro_tips"),
                flexible_alternatives=parsed_result.get("flexible_alternatives"),
            )

            logger.info(
                f"Itinerary Agent completed for {input_data.destination_city or input_data.destination_country}"
            )
            logger.info(f"Generated {len(output.daily_plans)} daily plans")
            return output

        except Exception as e:
            logger.error(f"Itinerary Agent execution failed: {e}", exc_info=True)
            raise ValueError(f"Failed to execute Itinerary Agent: {str(e)}")

    def _create_fallback_result(self, input_data: ItineraryAgentInput) -> dict:
        """
        Create fallback result when parsing fails.

        Args:
            input_data: Original input data

        Returns:
            Dictionary with minimal itinerary information
        """
        destination = input_data.destination_city or input_data.destination_country
        duration = (input_data.return_date - input_data.departure_date).days

        # Generate basic daily plans
        daily_plans = []
        for day_num in range(1, duration + 1):
            daily_plans.append({
                "day_number": day_num,
                "date": (
                    input_data.departure_date.isoformat()
                    if day_num == 1
                    else input_data.return_date.isoformat()
                ),
                "theme": f"Explore {destination}" if day_num == 1 else f"Day {day_num}",
                "morning_activities": [],
                "afternoon_activities": [],
                "evening_activities": [],
                "meals": [],
                "transportation": [],
                "daily_cost_estimate": "$50-$150",
                "notes": ["Custom itinerary to be planned"],
            })

        return {
            "daily_plans": daily_plans,
            "total_estimated_cost": f"${duration * 100}-${duration * 200}",
            "cost_breakdown": {
                "activities": "$40-$80 per day",
                "meals": "$30-$60 per day",
                "transportation": "$15-$30 per day",
                "accommodation": "$50-$150 per night",
            },
            "transportation_plan": "Mix of public transportation and walking. Consider day passes for metro/bus systems.",
            "getting_around_tips": [
                "Research public transportation options",
                "Consider purchasing multi-day transit passes",
                "Walking is often the best way to explore",
            ],
            "accommodation_suggestions": [
                {
                    "name": f"Hotel in {destination}",
                    "type": "hotel",
                    "neighborhood": "City Center",
                    "price_range": "$80-$150 per night",
                    "rating": 4.0,
                    "why_recommended": "Centrally located for easy access to attractions",
                }
            ],
            "optimization_notes": [
                "This is a basic itinerary template",
                "Customize based on your interests and pace",
                "Book major attractions in advance",
            ],
            "packing_checklist": [
                "Comfortable walking shoes",
                "Weather-appropriate clothing",
                "Travel adapter",
                "Reusable water bottle",
                "Day pack for excursions",
            ],
            "pro_tips": [
                "Start major sightseeing early to avoid crowds",
                "Take breaks to avoid exhaustion",
                "Try local cuisine at authentic restaurants",
                "Learn a few basic phrases in the local language",
            ],
            "flexible_alternatives": {},
        }
