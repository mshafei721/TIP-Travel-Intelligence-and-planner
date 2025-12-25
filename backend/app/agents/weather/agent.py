"""Weather Agent implementation using CrewAI."""

import json
import logging
from datetime import date, datetime

from crewai import Agent, Crew

from ..base import BaseAgent
from ..config import AgentConfig
from ..interfaces import AgentInput, AgentResult
from .models import (
    ClimateInfo,
    DailyForecast,
    PackingSuggestion,
    WeatherAgentInput,
    WeatherAgentOutput,
)
from .prompts import WEATHER_AGENT_BACKSTORY, WEATHER_AGENT_GOAL, WEATHER_AGENT_ROLE
from .tasks import create_comprehensive_weather_task
from .tools import (
    calculate_packing_needs,
    get_climate_information,
    get_weather_by_coordinates,
    get_weather_forecast,
)

logger = logging.getLogger(__name__)


class WeatherAgent(BaseAgent):
    """
    Weather Agent for travel weather intelligence.

    Provides comprehensive weather forecasts, climate analysis, packing
    recommendations, and weather-related travel tips using Visual Crossing
    Weather API and CrewAI framework.

    Features:
    - Accurate 15-day weather forecasts
    - Daily temperature, precipitation, wind, UV forecasts
    - Climate type and seasonal recommendations
    - Smart packing suggestions based on conditions
    - Weather alerts and safety information
    - Travel tips for weather-appropriate planning

    Data Source:
    - Visual Crossing Weather API (1,000 records/day free tier)
    """

    agent_type = "weather"

    def __init__(self, config: AgentConfig | None = None):
        """
        Initialize Weather Agent.

        Args:
            config: Agent configuration. If None, uses default config with Claude 3.5 Sonnet.
        """
        super().__init__(config)
        self.crew_agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """
        Create CrewAI agent for weather intelligence.

        Returns:
            Configured CrewAI Agent with weather tools
        """
        return Agent(
            role=WEATHER_AGENT_ROLE,
            goal=WEATHER_AGENT_GOAL,
            backstory=WEATHER_AGENT_BACKSTORY,
            tools=[
                get_weather_forecast,
                get_weather_by_coordinates,
                get_climate_information,
                calculate_packing_needs,
            ],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    def run(self, agent_input: AgentInput) -> AgentResult:
        """
        Execute Weather Agent to generate weather intelligence.

        Args:
            agent_input: WeatherAgentInput with trip details

        Returns:
            WeatherAgentOutput with complete weather intelligence

        Raises:
            ValueError: If input validation fails
            Exception: If agent execution fails
        """
        # Validate input type
        if not isinstance(agent_input, WeatherAgentInput):
            raise ValueError(f"Expected WeatherAgentInput, got {type(agent_input).__name__}")

        input_data: WeatherAgentInput = agent_input  # type: ignore

        logger.info(
            f"Starting Weather Agent for trip {input_data.trip_id} to "
            f"{input_data.destination_city}, {input_data.destination_country}"
        )

        try:
            # Calculate trip duration
            duration = (input_data.return_date - input_data.departure_date).days + 1

            # Create comprehensive weather task
            task = create_comprehensive_weather_task(
                agent=self.crew_agent,
                destination_city=input_data.destination_city,
                destination_country=input_data.destination_country,
                departure_date=input_data.departure_date.isoformat(),
                return_date=input_data.return_date.isoformat(),
                duration_days=duration,
            )

            # Execute CrewAI workflow
            crew = Crew(agents=[self.crew_agent], tasks=[task], verbose=True)

            result = crew.kickoff()

            # Parse result
            output = self._parse_result(result, input_data)

            logger.info(
                f"Weather Agent completed for trip {input_data.trip_id} with "
                f"confidence {output.confidence_score}"
            )

            return output

        except Exception as e:
            logger.error(f"Weather Agent failed for trip {input_data.trip_id}: {str(e)}")
            # Return fallback result
            return self._create_fallback_output(input_data, str(e))

    def _parse_result(self, crew_result: str, input_data: WeatherAgentInput) -> WeatherAgentOutput:
        """
        Parse CrewAI result into WeatherAgentOutput.

        Args:
            crew_result: Raw result from CrewAI
            input_data: Original input data

        Returns:
            Structured WeatherAgentOutput
        """
        try:
            # Try to parse as JSON
            if isinstance(crew_result, str):
                # Extract JSON from markdown code blocks if present
                if "```json" in crew_result:
                    json_start = crew_result.find("```json") + 7
                    json_end = crew_result.find("```", json_start)
                    crew_result = crew_result[json_start:json_end].strip()
                elif "```" in crew_result:
                    json_start = crew_result.find("```") + 3
                    json_end = crew_result.find("```", json_start)
                    crew_result = crew_result[json_start:json_end].strip()

                data = json.loads(crew_result)
            else:
                data = crew_result  # type: ignore

            # Parse daily forecasts
            forecasts = []
            for day_data in data.get("forecast", []):
                try:
                    forecast = DailyForecast(
                        date=date.fromisoformat(day_data.get("date")),
                        temp_max=float(day_data.get("temp_max", 0)),
                        temp_min=float(day_data.get("temp_min", 0)),
                        temp_avg=(
                            float(day_data.get("temp_avg")) if day_data.get("temp_avg") else None
                        ),
                        conditions=day_data.get("conditions", "Unknown"),
                        icon=day_data.get("icon"),
                        precipitation_prob=float(day_data.get("precipitation_prob", 0)),
                        precipitation_amount=(
                            float(day_data.get("precipitation_amount"))
                            if day_data.get("precipitation_amount")
                            else None
                        ),
                        humidity=(
                            float(day_data.get("humidity")) if day_data.get("humidity") else None
                        ),
                        wind_speed=(
                            float(day_data.get("wind_speed"))
                            if day_data.get("wind_speed")
                            else None
                        ),
                        wind_direction=day_data.get("wind_direction"),
                        uv_index=(
                            int(day_data.get("uv_index")) if day_data.get("uv_index") else None
                        ),
                        sunrise=day_data.get("sunrise"),
                        sunset=day_data.get("sunset"),
                        description=day_data.get("description"),
                    )
                    forecasts.append(forecast)
                except Exception as e:
                    logger.warning(f"Failed to parse daily forecast: {str(e)}")
                    continue

            # Parse packing suggestions
            packing = []
            for item_data in data.get("packing_suggestions", []):
                try:
                    packing.append(
                        PackingSuggestion(
                            item=item_data.get("item", ""),
                            reason=item_data.get("reason", ""),
                            priority=item_data.get("priority", "optional"),
                        )
                    )
                except Exception as e:
                    logger.warning(f"Failed to parse packing suggestion: {str(e)}")
                    continue

            # Parse climate info
            climate_info = None
            if "climate_info" in data and data["climate_info"]:
                try:
                    climate_data = data["climate_info"]
                    climate_info = ClimateInfo(
                        climate_type=climate_data.get("climate_type", "Unknown"),
                        best_time_to_visit=climate_data.get("best_time_to_visit", "Not specified"),
                        worst_time_to_visit=climate_data.get("worst_time_to_visit"),
                        seasonal_notes=climate_data.get("seasonal_notes", []),
                    )
                except Exception as e:
                    logger.warning(f"Failed to parse climate info: {str(e)}")

            # Create output
            return WeatherAgentOutput(
                trip_id=input_data.trip_id,
                agent_type="weather",
                generated_at=datetime.utcnow(),
                location=data.get(
                    "location",
                    f"{input_data.destination_city}, {input_data.destination_country}",
                ),
                latitude=data.get("latitude", input_data.latitude),
                longitude=data.get("longitude", input_data.longitude),
                timezone=data.get("timezone"),
                forecast=forecasts,
                average_temp=float(data.get("average_temp", 0)),
                temp_range_min=float(data.get("temp_range_min", 0)),
                temp_range_max=float(data.get("temp_range_max", 0)),
                precipitation_chance=float(data.get("precipitation_chance", 0)),
                total_precipitation=(
                    float(data.get("total_precipitation"))
                    if data.get("total_precipitation")
                    else None
                ),
                packing_suggestions=packing,
                climate_info=climate_info,
                weather_alerts=data.get("weather_alerts", []),
                travel_tips=data.get("travel_tips", []),
                confidence_score=float(data.get("confidence_score", 0.8)),
                sources=data.get("sources", ["Visual Crossing Weather API"]),
                warnings=data.get("warnings", []),
                is_good_time_to_visit=data.get("is_good_time_to_visit"),
                seasonal_recommendation=data.get("seasonal_recommendation"),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON result: {str(e)}")
            return self._create_fallback_output(input_data, f"JSON parsing error: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to parse result: {str(e)}")
            return self._create_fallback_output(input_data, f"Parsing error: {str(e)}")

    def _create_fallback_output(
        self, input_data: WeatherAgentInput, error: str
    ) -> WeatherAgentOutput:
        """
        Create fallback output when agent execution fails.

        Args:
            input_data: Original input data
            error: Error message

        Returns:
            Basic WeatherAgentOutput with error information
        """
        logger.warning(f"Creating fallback weather output due to: {error}")

        return WeatherAgentOutput(
            trip_id=input_data.trip_id,
            agent_type="weather",
            generated_at=datetime.utcnow(),
            location=f"{input_data.destination_city}, {input_data.destination_country}",
            latitude=input_data.latitude,
            longitude=input_data.longitude,
            timezone=None,
            forecast=[],
            average_temp=20.0,  # Default moderate temperature
            temp_range_min=15.0,
            temp_range_max=25.0,
            precipitation_chance=30.0,
            total_precipitation=None,
            packing_suggestions=[
                PackingSuggestion(
                    item="Layers (versatile clothing)",
                    reason="Unable to retrieve specific forecast",
                    priority="essential",
                ),
                PackingSuggestion(
                    item="Light rain jacket",
                    reason="General precaution",
                    priority="recommended",
                ),
            ],
            climate_info=None,
            weather_alerts=[],
            travel_tips=[
                "Check local weather forecast closer to departure date",
                "Pack versatile clothing for various conditions",
                "Bring adaptable layers for temperature changes",
            ],
            confidence_score=0.3,  # Low confidence for fallback
            sources=["Fallback data - API unavailable"],
            warnings=[
                "Weather Agent execution failed",
                f"Error: {error}",
                "Using generic fallback data",
                "Please check weather forecast from alternative sources",
            ],
            is_good_time_to_visit=None,
            seasonal_recommendation="Unable to provide seasonal assessment",
        )
