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
import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ValidationError

# Common country name to ISO 3166-1 alpha-2 code mapping
COUNTRY_NAME_TO_CODE: dict[str, str] = {
    # Common countries - add more as needed
    "afghanistan": "AF", "albania": "AL", "algeria": "DZ", "argentina": "AR",
    "armenia": "AM", "australia": "AU", "austria": "AT", "azerbaijan": "AZ",
    "bahrain": "BH", "bangladesh": "BD", "belarus": "BY", "belgium": "BE",
    "bolivia": "BO", "bosnia and herzegovina": "BA", "brazil": "BR", "bulgaria": "BG",
    "cambodia": "KH", "cameroon": "CM", "canada": "CA", "chile": "CL",
    "china": "CN", "colombia": "CO", "costa rica": "CR", "croatia": "HR",
    "cuba": "CU", "cyprus": "CY", "czech republic": "CZ", "czechia": "CZ",
    "denmark": "DK", "dominican republic": "DO", "ecuador": "EC", "egypt": "EG",
    "el salvador": "SV", "estonia": "EE", "ethiopia": "ET", "fiji": "FJ",
    "finland": "FI", "france": "FR", "georgia": "GE", "germany": "DE",
    "ghana": "GH", "greece": "GR", "guatemala": "GT", "honduras": "HN",
    "hong kong": "HK", "hungary": "HU", "iceland": "IS", "india": "IN",
    "indonesia": "ID", "iran": "IR", "iraq": "IQ", "ireland": "IE",
    "israel": "IL", "italy": "IT", "jamaica": "JM", "japan": "JP",
    "jordan": "JO", "kazakhstan": "KZ", "kenya": "KE", "kuwait": "KW",
    "kyrgyzstan": "KG", "laos": "LA", "latvia": "LV", "lebanon": "LB",
    "libya": "LY", "lithuania": "LT", "luxembourg": "LU", "macau": "MO",
    "malaysia": "MY", "maldives": "MV", "malta": "MT", "mexico": "MX",
    "moldova": "MD", "mongolia": "MN", "montenegro": "ME", "morocco": "MA",
    "myanmar": "MM", "nepal": "NP", "netherlands": "NL", "new zealand": "NZ",
    "nicaragua": "NI", "nigeria": "NG", "north korea": "KP", "north macedonia": "MK",
    "norway": "NO", "oman": "OM", "pakistan": "PK", "panama": "PA",
    "paraguay": "PY", "peru": "PE", "philippines": "PH", "poland": "PL",
    "portugal": "PT", "qatar": "QA", "romania": "RO", "russia": "RU",
    "russian federation": "RU", "rwanda": "RW", "saudi arabia": "SA", "senegal": "SN",
    "serbia": "RS", "singapore": "SG", "slovakia": "SK", "slovenia": "SI",
    "south africa": "ZA", "south korea": "KR", "korea": "KR", "spain": "ES",
    "sri lanka": "LK", "sudan": "SD", "sweden": "SE", "switzerland": "CH",
    "syria": "SY", "taiwan": "TW", "tajikistan": "TJ", "tanzania": "TZ",
    "thailand": "TH", "tunisia": "TN", "turkey": "TR", "turkmenistan": "TM",
    "uganda": "UG", "ukraine": "UA", "united arab emirates": "AE", "uae": "AE",
    "united kingdom": "GB", "uk": "GB", "england": "GB", "scotland": "GB", "wales": "GB",
    "united states": "US", "usa": "US", "america": "US", "united states of america": "US",
    "uruguay": "UY", "uzbekistan": "UZ", "venezuela": "VE", "vietnam": "VN",
    "yemen": "YE", "zambia": "ZM", "zimbabwe": "ZW",
}


def get_country_code(country_name: str) -> str:
    """
    Convert country name to ISO 3166-1 alpha-2 code.

    Args:
        country_name: Full country name or already an ISO code

    Returns:
        2-letter ISO country code, or original if already a code
    """
    if not country_name:
        return "US"  # Default

    # If already a 2-letter code, return uppercase
    if len(country_name) == 2 and country_name.isalpha():
        return country_name.upper()

    # Look up in mapping
    normalized = country_name.lower().strip()
    if normalized in COUNTRY_NAME_TO_CODE:
        return COUNTRY_NAME_TO_CODE[normalized]

    # Try partial match
    for name, code in COUNTRY_NAME_TO_CODE.items():
        if name in normalized or normalized in name:
            return code

    # Last resort: return first 2 chars uppercase (may be wrong but won't crash)
    return country_name[:2].upper() if len(country_name) >= 2 else "XX"

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

try:
    from app.agents.currency.agent import CurrencyAgent

    CURRENCY_AGENT_AVAILABLE = True
except ImportError:
    CURRENCY_AGENT_AVAILABLE = False

try:
    from app.agents.culture.agent import CultureAgent

    CULTURE_AGENT_AVAILABLE = True
except ImportError:
    CULTURE_AGENT_AVAILABLE = False

try:
    from app.agents.food.agent import FoodAgent

    FOOD_AGENT_AVAILABLE = True
except ImportError:
    FOOD_AGENT_AVAILABLE = False

try:
    from app.agents.attractions.agent import AttractionsAgent

    ATTRACTIONS_AGENT_AVAILABLE = True
except ImportError:
    ATTRACTIONS_AGENT_AVAILABLE = False

try:
    from app.agents.itinerary.agent import ItineraryAgent

    ITINERARY_AGENT_AVAILABLE = True
except ImportError:
    ITINERARY_AGENT_AVAILABLE = False

try:
    from app.agents.flight.agent import FlightAgent

    FLIGHT_AGENT_AVAILABLE = True
except ImportError:
    FLIGHT_AGENT_AVAILABLE = False


# Section type to title mapping for report_sections table
SECTION_TITLES: dict[str, str] = {
    "visa": "Visa Requirements",
    "country": "Country Overview",
    "weather": "Weather & Climate",
    "currency": "Currency & Money",
    "culture": "Culture & Customs",
    "food": "Food & Dining",
    "attractions": "Attractions & Activities",
    "safety": "Safety Information",
    "packing": "Packing List",
    "flights": "Flight Information",
    "accommodation": "Accommodation",
    "transportation": "Transportation",
    "itinerary": "Day-by-Day Itinerary",
}


def get_section_title(section_type: str) -> str:
    """Get the display title for a section type."""
    return SECTION_TITLES.get(section_type, section_type.replace("_", " ").title())


class TripData(BaseModel):
    """Trip data model for orchestrator input"""

    trip_id: str
    user_nationality: str
    destination_country: str
    destination_city: str
    departure_date: date | None = None
    return_date: date | None = None
    trip_purpose: str = "tourism"
    origin_city: str | None = None  # For flight agent
    group_size: int = 1
    budget_level: str = "mid-range"
    interests: list[str] | None = None
    dietary_restrictions: list[str] | None = None

    def validate_dates(self) -> None:
        """Validate that dates are present and valid for report generation"""
        if self.departure_date is None or self.return_date is None:
            raise ValueError(
                "Trip dates are required for report generation. "
                "Please set departure and return dates."
            )
        if self.return_date < self.departure_date:
            raise ValueError(
                "Return date must be after departure date."
            )


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

        if CURRENCY_AGENT_AVAILABLE:
            self.available_agents["currency"] = CurrencyAgent

        if CULTURE_AGENT_AVAILABLE:
            self.available_agents["culture"] = CultureAgent

        if FOOD_AGENT_AVAILABLE:
            self.available_agents["food"] = FoodAgent

        if ATTRACTIONS_AGENT_AVAILABLE:
            self.available_agents["attractions"] = AttractionsAgent

        if ITINERARY_AGENT_AVAILABLE:
            self.available_agents["itinerary"] = ItineraryAgent

        if FLIGHT_AGENT_AVAILABLE:
            self.available_agents["flight"] = FlightAgent

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

        # Validate dates are present
        validated_data.validate_dates()

        # Update job status to running
        await self._update_job_status(
            validated_data.trip_id, "running", {"message": "Starting report generation"}
        )

        # Run agents in phases
        sections = {}

        try:
            # Phase 1: Independent agents (can run in parallel)
            # These agents don't depend on each other and can run simultaneously
            phase1_agents = ["visa", "country", "weather", "currency", "culture"]
            print(f"[Orchestrator] Starting Phase 1 with agents: {phase1_agents}")
            phase1_results = await self._run_phase(validated_data, phase1_agents)
            print(f"[Orchestrator] Phase 1 completed. Results: {list(phase1_results.keys())}, Errors: {len(self.errors)}")
            sections.update(phase1_results)

            # Phase 2: Dependent agents (depend on culture/country)
            phase2_agents = ["food", "attractions"]
            print(f"[Orchestrator] Starting Phase 2 with agents: {phase2_agents}")
            phase2_results = await self._run_phase(validated_data, phase2_agents)
            print(f"[Orchestrator] Phase 2 completed. Results: {list(phase2_results.keys())}, Errors: {len(self.errors)}")
            sections.update(phase2_results)

            # Phase 3: Synthesis agents (itinerary depends on Phase 1-2 results)
            phase3_agents = ["itinerary"]
            print(f"[Orchestrator] Starting Phase 3 with agents: {phase3_agents}")
            phase3_results = await self._run_phase(validated_data, phase3_agents)
            print(f"[Orchestrator] Phase 3 completed. Results: {list(phase3_results.keys())}, Errors: {len(self.errors)}")
            sections.update(phase3_results)

            # Phase 4: Flight agent (requires origin city from trip data)
            if validated_data.origin_city:
                phase4_agents = ["flight"]
                print(f"[Orchestrator] Starting Phase 4 with agents: {phase4_agents}")
                phase4_results = await self._run_phase(validated_data, phase4_agents)
                print(f"[Orchestrator] Phase 4 completed. Results: {list(phase4_results.keys())}, Errors: {len(self.errors)}")
                sections.update(phase4_results)
            else:
                print("[Orchestrator] Skipping Phase 4 (flight): no origin_city provided")

            # Save results to database
            print(f"[Orchestrator] Saving {len(sections)} sections to database")
            await self._save_results(validated_data.trip_id, sections)
            print(f"[Orchestrator] Sections saved successfully")

            # Update job status to completed
            await self._update_job_status(
                validated_data.trip_id,
                "completed",
                {"sections_generated": list(sections.keys())},
            )
            print(f"[Orchestrator] Job status updated to completed")

            # Aggregate and return results
            result = self._aggregate_results(
                {
                    "trip_id": validated_data.trip_id,
                    "sections": sections,
                    "errors": self.errors,
                }
            )
            print(f"[Orchestrator] Returning result with {len(sections)} sections and {len(self.errors)} errors")
            return result

        except Exception as e:
            # Update job status to failed
            print(f"[Orchestrator] ERROR: {str(e)}")
            await self._update_job_status(validated_data.trip_id, "failed", {"error": str(e)})
            raise

    async def _run_phase(self, trip_data: TripData, agent_names: list[str]) -> dict[str, Any]:
        """
        Run a phase of agents sequentially to avoid API rate limits.
        Each agent's result is saved immediately after completion for incremental progress.

        Args:
            trip_data: Validated trip data
            agent_names: List of agent names to run

        Returns:
            Dictionary of agent results
        """
        results = {}

        # Filter to only available agents
        available_agents_in_phase = [name for name in agent_names if name in self.available_agents]

        # Run agents sequentially with delay to avoid rate limits
        # Anthropic free tier: 30,000 input tokens/minute
        DELAY_BETWEEN_AGENTS = 5  # seconds delay between agents

        for agent_name in available_agents_in_phase:
            print(f"[Orchestrator] Running agent: {agent_name}")
            try:
                result = await self._run_agent(trip_data, agent_name)
                results[agent_name] = result
                print(f"[Orchestrator] Agent {agent_name} completed successfully")

                # Save section immediately after agent completes (incremental save)
                # This allows users to see partial results while generation continues
                await self._save_section_incremental(trip_data.trip_id, agent_name, result)
                print(f"[Orchestrator] Agent {agent_name} result saved to database")
            except Exception as e:
                # Log error and continue with next agent
                print(f"[Orchestrator] Agent {agent_name} failed: {str(e)}")
                self.errors.append(
                    {
                        "agent": agent_name,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Add delay between agents to avoid rate limiting
            if agent_name != available_agents_in_phase[-1]:
                print(f"[Orchestrator] Waiting {DELAY_BETWEEN_AGENTS}s before next agent...")
                await asyncio.sleep(DELAY_BETWEEN_AGENTS)

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
            # Convert country names to ISO codes for visa agent
            nationality_code = get_country_code(trip_data.user_nationality)
            destination_code = get_country_code(trip_data.destination_country)
            return VisaAgentInput(
                trip_id=trip_data.trip_id,
                user_nationality=nationality_code,
                destination_country=destination_code,
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

        # For currency agent
        if agent_name == "currency":
            from app.agents.currency.models import CurrencyAgentInput

            return CurrencyAgentInput(
                trip_id=trip_data.trip_id,
                destination_country=trip_data.destination_country,
                destination_city=trip_data.destination_city,
                departure_date=trip_data.departure_date,
                return_date=trip_data.return_date,
                traveler_nationality=trip_data.user_nationality,
                base_currency="USD",  # Default to USD, can be extended later
            )

        # For culture agent
        if agent_name == "culture":
            from app.agents.culture.models import CultureAgentInput

            return CultureAgentInput(
                trip_id=trip_data.trip_id,
                destination_country=trip_data.destination_country,
                destination_city=trip_data.destination_city,
                departure_date=trip_data.departure_date,
                return_date=trip_data.return_date,
                traveler_nationality=trip_data.user_nationality,
            )

        # For food agent
        if agent_name == "food":
            from app.agents.food.models import FoodAgentInput

            return FoodAgentInput(
                trip_id=trip_data.trip_id,
                destination_country=trip_data.destination_country,
                destination_city=trip_data.destination_city,
                departure_date=trip_data.departure_date,
                return_date=trip_data.return_date,
                traveler_nationality=trip_data.user_nationality,
                dietary_restrictions=None,  # Can be extended to include user preferences
            )

        # For attractions agent
        if agent_name == "attractions":
            from app.agents.attractions.models import AttractionsAgentInput

            return AttractionsAgentInput(
                trip_id=trip_data.trip_id,
                destination_country=trip_data.destination_country,
                destination_city=trip_data.destination_city,
                departure_date=trip_data.departure_date,
                return_date=trip_data.return_date,
                traveler_nationality=trip_data.user_nationality,
                interests=trip_data.interests,
            )

        # For itinerary agent
        if agent_name == "itinerary":
            from app.agents.itinerary.models import ItineraryAgentInput

            return ItineraryAgentInput(
                trip_id=trip_data.trip_id,
                destination_country=trip_data.destination_country,
                destination_city=trip_data.destination_city,
                departure_date=trip_data.departure_date,
                return_date=trip_data.return_date,
                traveler_nationality=trip_data.user_nationality,
                group_size=trip_data.group_size,
                budget_level=trip_data.budget_level,
                interests=trip_data.interests,
                dietary_restrictions=trip_data.dietary_restrictions,
            )

        # For flight agent
        if agent_name == "flight":
            from app.agents.flight.models import FlightAgentInput

            return FlightAgentInput(
                trip_id=trip_data.trip_id,
                origin_city=trip_data.origin_city or "Unknown",
                destination_city=trip_data.destination_city,
                departure_date=trip_data.departure_date,
                return_date=trip_data.return_date,
                passengers=trip_data.group_size,
            )

        raise ValueError(f"Unknown agent: {agent_name}")

    def _serialize_for_json(self, obj: Any) -> Any:
        """
        Recursively serialize an object for JSON compatibility.

        Converts datetime and date objects to ISO format strings.

        Args:
            obj: Object to serialize

        Returns:
            JSON-serializable object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        elif hasattr(obj, "model_dump"):
            # Pydantic model - convert to dict first
            return self._serialize_for_json(obj.model_dump())
        return obj

    async def _save_section_incremental(self, trip_id: str, section_type: str, content: Any) -> None:
        """
        Save a single section to database immediately after agent completes.
        Uses upsert to handle re-runs and partial failures.

        Args:
            trip_id: Trip ID
            section_type: Type of section (visa, country, weather, etc.)
            content: Section content to save
        """
        try:
            # Serialize content to ensure all datetime objects are converted
            serialized_content = self._serialize_for_json(content)

            # Use upsert to handle cases where section already exists
            # This is important for:
            # 1. Re-running after partial failures
            # 2. Regeneration requests
            # 3. Avoiding duplicate entries
            supabase.table("report_sections").upsert(
                {
                    "trip_id": trip_id,
                    "section_type": section_type,
                    "title": get_section_title(section_type),
                    "content": serialized_content,
                    "generated_at": datetime.utcnow().isoformat(),
                },
                on_conflict="trip_id,section_type"
            ).execute()
        except Exception as e:
            # Log error but don't fail the agent - section will be saved at end
            self.errors.append(
                {
                    "operation": "save_section_incremental",
                    "section": section_type,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    async def _save_results(self, trip_id: str, sections: dict[str, Any]) -> None:
        """
        Save results to database (final batch save, kept for backward compatibility).
        Note: Sections are now also saved incrementally in _run_phase.

        Args:
            trip_id: Trip ID
            sections: Dictionary of section results
        """
        for section_type, content in sections.items():
            try:
                # Serialize content to ensure all datetime objects are converted
                serialized_content = self._serialize_for_json(content)
                # Use upsert instead of insert to handle incremental saves
                supabase.table("report_sections").upsert(
                    {
                        "trip_id": trip_id,
                        "section_type": section_type,
                        "title": get_section_title(section_type),
                        "content": serialized_content,
                        "generated_at": datetime.utcnow().isoformat(),
                    },
                    on_conflict="trip_id,section_type"
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

        # Serialize sections to ensure JSON compatibility
        serialized_sections = self._serialize_for_json(sections)

        return {
            "trip_id": trip_id,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": serialized_sections,
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
