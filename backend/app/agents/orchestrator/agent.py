"""
Orchestrator Agent

Coordinates all specialist agents and manages the travel report generation workflow.

Architecture:
- Phase 1: Independent agents (can run in parallel)
- Phase 2: Dependent agents (require Phase 1 results)
- Phase 3: Synthesis agents (require all previous phases)

This orchestrator follows the TDD approach and implements comprehensive
error handling and result aggregation.
"""

import asyncio
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ValidationError

from app.core.supabase import supabase

# Import specialist agents as they become available
try:
    from app.agents.visa.agent import VisaAgent

    VISA_AGENT_AVAILABLE = True
except ImportError:
    VISA_AGENT_AVAILABLE = False

try:
    from app.agents.country.agent import CountryAgent

    COUNTRY_AGENT_AVAILABLE = True
except ImportError:
    COUNTRY_AGENT_AVAILABLE = False

try:
    from app.agents.weather.agent import WeatherAgent

    WEATHER_AGENT_AVAILABLE = True
except ImportError:
    WEATHER_AGENT_AVAILABLE = False


class TripData(BaseModel):
    """Trip data model for orchestrator input"""

    trip_id: str
    user_nationality: str
    destination_country: str
    destination_city: str
    departure_date: date
    return_date: date
    trip_purpose: str = "tourism"


class OrchestratorResult(BaseModel):
    """Result from orchestrator"""

    trip_id: str
    generated_at: datetime
    sections: dict[str, Any]
    errors: list[dict[str, str]]
    metadata: dict[str, Any]


class OrchestratorAgent:
    """
    Orchestrator Agent

    Coordinates all specialist agents to generate comprehensive travel reports.
    Handles agent lifecycle, error recovery, and result aggregation.
    """

    def __init__(self):
        """Initialize orchestrator with available agents"""
        self.available_agents: dict[str, Any] = {}

        # Register available agents
        if VISA_AGENT_AVAILABLE:
            self.available_agents["visa"] = VisaAgent

        if COUNTRY_AGENT_AVAILABLE:
            self.available_agents["country"] = CountryAgent

        if WEATHER_AGENT_AVAILABLE:
            self.available_agents["weather"] = WeatherAgent

        # Placeholder for future agents
        # self.available_agents['currency'] = CurrencyAgent
        # self.available_agents['culture'] = CultureAgent
        # self.available_agents['food'] = FoodAgent
        # self.available_agents['attractions'] = AttractionsAgent
        # self.available_agents['itinerary'] = ItineraryAgent
        # self.available_agents['flight'] = FlightAgent

        self.errors: list[dict[str, str]] = []

    async def generate_report(self, trip_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate complete travel report

        Args:
            trip_data: Trip information dictionary

        Returns:
            Complete travel report with all sections

        Raises:
            ValueError: If trip data is invalid
        """
        # Validate trip data
        validated_data = self._validate_trip_data(trip_data)

        # Update job status to running
        await self._update_job_status(
            validated_data.trip_id, "running", {"message": "Starting report generation"}
        )

        # Run agents in phases
        sections = {}

        try:
            # Phase 1: Independent agents (can run in parallel)
            # These agents don't depend on each other and can run simultaneously
            phase1_agents = ["visa", "country", "weather"]
            phase1_results = await self._run_phase(validated_data, phase1_agents)
            sections.update(phase1_results)

            # Phase 2: Dependent agents (future implementation)
            # phase2_agents = ['currency', 'culture']
            # phase2_results = await self._run_phase(validated_data, phase2_agents)
            # sections.update(phase2_results)

            # Phase 3: Synthesis agents (future implementation)
            # phase3_agents = ['food', 'attractions']
            # phase3_results = await self._run_phase(validated_data, phase3_agents)
            # sections.update(phase3_results)

            # Phase 4: Final agents (future implementation)
            # phase4_agents = ['itinerary', 'flight']
            # phase4_results = await self._run_phase(validated_data, phase4_agents)
            # sections.update(phase4_results)

            # Save results to database
            await self._save_results(validated_data.trip_id, sections)

            # Update job status to completed
            await self._update_job_status(
                validated_data.trip_id,
                "completed",
                {"sections_generated": list(sections.keys())},
            )

            # Aggregate and return results
            return self._aggregate_results(
                {
                    "trip_id": validated_data.trip_id,
                    "sections": sections,
                    "errors": self.errors,
                }
            )

        except Exception as e:
            # Update job status to failed
            await self._update_job_status(validated_data.trip_id, "failed", {"error": str(e)})
            raise

    async def _run_phase(self, trip_data: TripData, agent_names: list[str]) -> dict[str, Any]:
        """
        Run a phase of agents

        Args:
            trip_data: Validated trip data
            agent_names: List of agent names to run

        Returns:
            Dictionary of agent results
        """
        results = {}

        # Filter to only available agents
        available_agents_in_phase = [name for name in agent_names if name in self.available_agents]

        # Run agents in parallel
        tasks = [self._run_agent(trip_data, agent_name) for agent_name in available_agents_in_phase]

        # Gather results with error handling
        agent_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for agent_name, result in zip(available_agents_in_phase, agent_results, strict=False):
            if isinstance(result, Exception):
                # Log error and continue
                self.errors.append(
                    {
                        "agent": agent_name,
                        "error": str(result),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            else:
                results[agent_name] = result

        return results

    async def _run_agent(self, trip_data: TripData, agent_name: str) -> dict[str, Any]:
        """
        Run a single agent

        Args:
            trip_data: Validated trip data
            agent_name: Name of agent to run

        Returns:
            Agent result
        """
        if agent_name not in self.available_agents:
            raise ValueError(f"Agent '{agent_name}' is not available")

        # Create agent input
        agent_input = self._create_agent_input(trip_data, agent_name)

        # Get agent class and instantiate
        agent_class = self.available_agents[agent_name]
        agent_instance = agent_class()

        # Run agent
        result = await agent_instance.run_async(agent_input)

        return result.model_dump() if hasattr(result, "model_dump") else result

    def _validate_trip_data(self, trip_data: dict[str, Any]) -> TripData:
        """
        Validate trip data

        Args:
            trip_data: Raw trip data dictionary

        Returns:
            Validated TripData model

        Raises:
            ValueError: If trip data is invalid
        """
        try:
            return TripData(**trip_data)
        except ValidationError as e:
            raise ValueError(f"Invalid trip data: {str(e)}")

    def _create_agent_input(self, trip_data: TripData, agent_name: str) -> Any:
        """
        Create input for specific agent

        Args:
            trip_data: Validated trip data (TripData object)
            agent_name: Name of agent

        Returns:
            Agent-specific input object
        """
        # For visa agent
        if agent_name == "visa":
            from app.agents.visa.models import VisaAgentInput

            duration_days = (trip_data.return_date - trip_data.departure_date).days
            return VisaAgentInput(
                trip_id=trip_data.trip_id,
                user_nationality=trip_data.user_nationality,
                destination_country=trip_data.destination_country,
                destination_city=trip_data.destination_city,
                trip_purpose=trip_data.trip_purpose,
                duration_days=duration_days,
                departure_date=trip_data.departure_date,
                traveler_count=1,
            )

        # For country agent
        if agent_name == "country":
            from app.agents.country.models import CountryAgentInput

            return CountryAgentInput(
                trip_id=trip_data.trip_id,
                destination_country=trip_data.destination_country,
                destination_city=trip_data.destination_city,
                departure_date=trip_data.departure_date,
                return_date=trip_data.return_date,
                traveler_nationality=trip_data.user_nationality,
            )

        # For weather agent
        if agent_name == "weather":
            from app.agents.weather.models import WeatherAgentInput

            return WeatherAgentInput(
                trip_id=trip_data.trip_id,
                user_nationality=trip_data.user_nationality,
                destination_country=trip_data.destination_country,
                destination_city=trip_data.destination_city,
                departure_date=trip_data.departure_date,
                return_date=trip_data.return_date,
                latitude=None,  # Will be populated by geocoding in future
                longitude=None,  # Will be populated by geocoding in future
            )

        # Add more agent input creators as agents are implemented
        raise ValueError(f"Unknown agent: {agent_name}")

    async def _save_results(self, trip_id: str, sections: dict[str, Any]) -> None:
        """
        Save results to database

        Args:
            trip_id: Trip ID
            sections: Dictionary of section results
        """
        for section_type, content in sections.items():
            try:
                supabase.table("report_sections").insert(
                    {
                        "trip_id": trip_id,
                        "section_type": section_type,
                        "content": content,
                        "generated_at": datetime.utcnow().isoformat(),
                    }
                ).execute()
            except Exception as e:
                self.errors.append(
                    {
                        "operation": "save_results",
                        "section": section_type,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

    async def _update_job_status(self, trip_id: str, status: str, metadata: dict[str, Any]) -> None:
        """
        Update agent job status

        Args:
            trip_id: Trip ID
            status: New status
            metadata: Additional metadata
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }

            if status == "running":
                update_data["started_at"] = datetime.utcnow().isoformat()
            elif status == "completed":
                update_data["completed_at"] = datetime.utcnow().isoformat()
            elif status == "failed":
                update_data["error_message"] = metadata.get("error", "Unknown error")

            supabase.table("agent_jobs").update(update_data).eq("trip_id", trip_id).eq(
                "agent_type", "orchestrator"
            ).execute()

        except Exception as e:
            # Log but don't fail on status update errors
            self.errors.append(
                {
                    "operation": "update_job_status",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    def _aggregate_results(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Aggregate results from all agents

        Args:
            data: Raw results data (can be dict with trip_id or dict with just sections)

        Returns:
            Aggregated report
        """
        # Handle case where data is a simple dict with sections
        if isinstance(data, dict) and "visa" in data:
            # data is actually the sections dict
            sections = data
            trip_id = "unknown"
            errors = []
        else:
            # data is the full result dict
            sections = data.get("sections", {})
            trip_id = data.get("trip_id", "unknown")
            errors = data.get("errors", [])

        return {
            "trip_id": trip_id,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": sections,
            "errors": errors,
            "metadata": {
                "agent_count": len(sections),
                "error_count": len(errors),
                "orchestrator_version": "1.0.0",
            },
        }

    def list_available_agents(self) -> list[str]:
        """
        List all available agents

        Returns:
            List of agent names
        """
        return list(self.available_agents.keys())

    def is_agent_available(self, agent_name: str) -> bool:
        """
        Check if agent is available

        Args:
            agent_name: Name of agent to check

        Returns:
            True if agent is available, False otherwise
        """
        return agent_name in self.available_agents
