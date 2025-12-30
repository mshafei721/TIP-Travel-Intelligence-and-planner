"""
Country Agent Implementation

Provides comprehensive country intelligence using CrewAI and Claude AI.
"""

import json
import logging
from datetime import datetime

from crewai import Agent, Crew, Process

from ..base import BaseAgent
from ..config import AgentConfig, get_llm
from ..exceptions import AgentExecutionError
from ..interfaces import AgentResult, SourceReference
from .models import (
    CountryAgentInput,
    CountryAgentOutput,
    EmergencyContact,
    PowerOutletInfo,
    TravelAdvisory,
)
from .prompts import COUNTRY_AGENT_BACKSTORY, COUNTRY_AGENT_GOAL, COUNTRY_AGENT_ROLE
from .tasks import create_comprehensive_country_task
from .tools import (
    get_country_info,
    get_emergency_services,
    get_notable_facts,
    get_power_outlet_info,
    get_travel_safety_rating,
)

logger = logging.getLogger(__name__)


class CountryAgent(BaseAgent):
    """
    Country Intelligence Agent.

    Provides comprehensive country information including basic facts,
    emergency services, power standards, safety ratings, and travel tips.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_model: str = "claude-sonnet-4-20250514",
    ):
        """
        Initialize Country Agent.

        Args:
            config: Agent configuration (optional)
            llm_model: Claude AI model to use
        """
        super().__init__(config or AgentConfig(agent_type="country"))

        # Initialize LLM with fallback support (Anthropic -> Gemini -> OpenAI)
        self.llm = get_llm(temperature=0.1)

        # Create CrewAI agent
        self.agent = self._create_crewai_agent()

        logger.info(f"CountryAgent initialized with model: {llm_model}")

    def _create_crewai_agent(self) -> Agent:
        """
        Create the CrewAI agent with tools.

        Returns:
            Configured CrewAI Agent
        """
        return Agent(
            role=COUNTRY_AGENT_ROLE,
            goal=COUNTRY_AGENT_GOAL,
            backstory=COUNTRY_AGENT_BACKSTORY,
            llm=self.llm,
            tools=[
                get_country_info,
                get_emergency_services,
                get_power_outlet_info,
                get_travel_safety_rating,
                get_notable_facts,
            ],
            verbose=True,
            allow_delegation=False,
        )

    def run(self, input_data: CountryAgentInput) -> AgentResult:
        """
        Execute the Country Agent.

        Args:
            input_data: Country Agent input parameters

        Returns:
            CountryAgentOutput with comprehensive country intelligence

        Raises:
            AgentExecutionError: If agent execution fails
        """
        try:
            logger.info(
                f"Executing CountryAgent for trip_id={input_data.trip_id}, "
                f"country={input_data.destination_country}"
            )

            # Create task
            task = create_comprehensive_country_task(self.agent, input_data)

            # Create crew
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )

            # Execute crew
            result = crew.kickoff()

            logger.info(f"CountryAgent execution complete. Raw result type: {type(result)}")

            # Parse result
            output = self._parse_result(result, input_data)

            logger.info(
                f"CountryAgent success: trip_id={input_data.trip_id}, "
                f"confidence={output.confidence_score}"
            )

            return output

        except Exception as e:
            logger.error(f"CountryAgent execution failed: {str(e)}", exc_info=True)
            raise AgentExecutionError(f"Country agent failed: {str(e)}")

    def _parse_result(self, result: str, input_data: CountryAgentInput) -> CountryAgentOutput:
        """
        Parse CrewAI result into CountryAgentOutput.

        Args:
            result: Raw CrewAI output
            input_data: Original input data

        Returns:
            Structured CountryAgentOutput

        Raises:
            AgentExecutionError: If parsing fails
        """
        try:
            # Extract JSON from result
            result_str = str(result)

            # Try to find JSON in the result
            json_start = result_str.find("{")
            json_end = result_str.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = result_str[json_start:json_end]
                data = json.loads(json_str)
            else:
                # Fallback: try parsing entire result as JSON
                data = json.loads(result_str)

            # Build CountryAgentOutput
            return CountryAgentOutput(
                trip_id=input_data.trip_id,
                agent_type="country",
                generated_at=datetime.utcnow(),
                confidence_score=data.get("confidence_score", 0.85),
                sources=self._build_sources(data),
                warnings=data.get("warnings", []),
                # Basic Information
                country_name=data.get("country_name", input_data.destination_country),
                country_code=data.get("country_code", ""),
                capital=data.get("capital", ""),
                region=data.get("region", ""),
                subregion=data.get("subregion"),
                # Demographics
                population=data.get("population", 0),
                area_km2=data.get("area_km2"),
                population_density=data.get("population_density"),
                # Languages
                official_languages=data.get("official_languages", []),
                common_languages=data.get("common_languages"),
                # Time and Geography
                time_zones=data.get("time_zones", []),
                coordinates=data.get("coordinates"),
                borders=data.get("borders"),
                # Emergency Services
                emergency_numbers=self._build_emergency_contacts(data.get("emergency_numbers", [])),
                # Power and Driving
                power_outlet=self._build_power_outlet(data.get("power_outlet", {})),
                driving_side=data.get("driving_side", "right"),
                # Currency
                currencies=data.get("currencies", []),
                currency_codes=data.get("currency_codes", []),
                # Safety
                safety_rating=data.get("safety_rating", 3.5),
                travel_advisories=self._build_travel_advisories(data.get("travel_advisories", [])),
                # Additional
                notable_facts=data.get("notable_facts", []),
                best_time_to_visit=data.get("best_time_to_visit"),
            )

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed, using fallback: {str(e)}")
            return self._create_fallback_output(input_data)
        except (AttributeError, TypeError) as e:
            # Handle cases where data is not a dict (e.g., string)
            logger.warning(f"Data structure issue, using fallback: {str(e)}")
            return self._create_fallback_output(input_data)
        except Exception as e:
            logger.error(f"Result parsing failed: {str(e)}", exc_info=True)
            # Use fallback instead of raising to ensure agent completes
            logger.warning("Using fallback output due to parsing error")
            return self._create_fallback_output(input_data)

    def _build_sources(self, data: dict) -> list[SourceReference]:
        """Build source references from data."""
        sources = []

        # Add REST Countries API as primary source
        sources.append(
            SourceReference(
                title="REST Countries API",
                url="https://restcountries.com/",
                verified_at=datetime.utcnow(),
            )
        )

        # Add any additional sources from data
        if "sources" in data:
            for source in data["sources"]:
                sources.append(
                    SourceReference(
                        title=source.get("name", source.get("title", "Unknown")),
                        url=source.get("url", "internal://unknown-source"),
                        verified_at=(
                            datetime.fromisoformat(source.get("accessed_at"))
                            if source.get("accessed_at")
                            else datetime.utcnow()
                        ),
                    )
                )

        return sources

    def _build_emergency_contacts(self, contacts_data: list[dict]) -> list[EmergencyContact]:
        """Build emergency contact objects from data."""
        contacts = []
        for contact in contacts_data:
            contacts.append(
                EmergencyContact(
                    service=contact.get("service", "Unknown"),
                    number=contact.get("number", ""),
                    notes=contact.get("notes"),
                )
            )
        return contacts

    def _build_power_outlet(self, power_data: dict) -> PowerOutletInfo:
        """Build power outlet info from data."""
        return PowerOutletInfo(
            plug_types=power_data.get("plug_types", ["Unknown"]),
            voltage=power_data.get("voltage", "Unknown"),
            frequency=power_data.get("frequency", "Unknown"),
        )

    def _build_travel_advisories(self, advisories_data: list[dict]) -> list[TravelAdvisory]:
        """Build travel advisory objects from data."""
        advisories = []
        for advisory in advisories_data:
            advisories.append(
                TravelAdvisory(
                    level=advisory.get("level", "Unknown"),
                    title=advisory.get("title", "Unknown"),
                    summary=advisory.get("summary", ""),
                    updated_at=advisory.get("updated_at"),
                    source=advisory.get("source", "Unknown"),
                )
            )
        return advisories

    def _create_fallback_output(self, input_data: CountryAgentInput) -> CountryAgentOutput:
        """
        Create fallback output when parsing fails.

        Args:
            input_data: Original input data

        Returns:
            Basic CountryAgentOutput with minimal data
        """
        logger.warning("Creating fallback output for Country Agent")

        return CountryAgentOutput(
            trip_id=input_data.trip_id,
            agent_type="country",
            generated_at=datetime.utcnow(),
            confidence_score=0.5,
            sources=[
                SourceReference(
                    title="Fallback Data",
                    url="internal://fallback-data",
                    verified_at=datetime.utcnow(),
                )
            ],
            warnings=["Failed to parse complete country information. Using fallback data."],
            country_name=input_data.destination_country,
            country_code="",
            capital="Unknown",
            region="Unknown",
            subregion=None,
            population=0,
            area_km2=None,
            population_density=None,
            official_languages=["Unknown"],
            common_languages=None,
            time_zones=["Unknown"],
            coordinates=None,
            borders=None,
            emergency_numbers=[
                EmergencyContact(
                    service="Emergency (International)",
                    number="112",
                    notes="May work in many countries",
                )
            ],
            power_outlet=PowerOutletInfo(
                plug_types=["Unknown"],
                voltage="Unknown",
                frequency="Unknown",
            ),
            driving_side="right",
            currencies=["Unknown"],
            currency_codes=[],
            safety_rating=3.0,
            travel_advisories=[],
            notable_facts=[],
            best_time_to_visit=None,
        )
