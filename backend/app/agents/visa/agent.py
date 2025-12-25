"""
Visa Agent - Production Implementation with CrewAI

Provides comprehensive visa requirements analysis using CrewAI framework.
Integrates with Travel Buddy AI API for official visa data.

Architecture:
- CrewAI Agent with Claude AI (Anthropic)
- Custom tools for API integration
- Multi-task workflow for research and verification
- Confidence scoring and source attribution
"""

import json
from datetime import datetime

from crewai import Agent, Crew, Process
from langchain_anthropic import ChatAnthropic

from app.agents.base import BaseAgent
from app.agents.config import AgentConfig
from app.agents.exceptions import AgentExecutionError
from app.agents.interfaces import AgentResult, SourceReference
from app.core.config import settings

from .models import (
    ApplicationProcess,
    EntryRequirement,
    VisaAgentInput,
    VisaAgentOutput,
    VisaRequirement,
)
from .prompts import VISA_AGENT_BACKSTORY, VISA_AGENT_GOAL, VISA_AGENT_ROLE
from .tasks import create_single_step_task
from .tools import (
    check_travel_advisories,
    check_visa_requirements,
    estimate_processing_time,
    generate_document_checklist,
    get_embassy_info,
)


class VisaAgent(BaseAgent):
    """
    Production-Ready Visa Requirements Agent

    Uses CrewAI framework with Claude AI to provide comprehensive visa intelligence.

    Features:
    - Multi-source data verification
    - Confidence scoring
    - Source attribution
    - Practical tips and warnings
    - Production-ready error handling

    Example:
        >>> agent = VisaAgent()
        >>> input_data = VisaAgentInput(
        ...     trip_id="trip-123",
        ...     user_nationality="US",
        ...     destination_country="FR",
        ...     destination_city="Paris",
        ...     trip_purpose="tourism",
        ...     duration_days=14,
        ...     departure_date=date(2025, 6, 1),
        ... )
        >>> result = agent.run(input_data)
        >>> print(result.data["visa_requirement"]["visa_required"])  # False
    """

    def __init__(self, anthropic_api_key: str | None = None):
        """
        Initialize Visa Agent with CrewAI

        Args:
            anthropic_api_key: Anthropic API key for Claude (defaults to settings)
        """
        super().__init__(
            config=AgentConfig(
                name="visa",
                description="Visa requirements specialist with CrewAI and Claude AI",
                version="1.0.0",
                timeout=180,  # 3 minutes for CrewAI processing
                max_retries=3,
            )
        )

        # Initialize Claude AI (Anthropic)
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,  # Low temperature for factual accuracy
            anthropic_api_key=anthropic_api_key or settings.ANTHROPIC_API_KEY,
        )

        # Initialize CrewAI Agent
        self.crew_agent = Agent(
            role=VISA_AGENT_ROLE,
            goal=VISA_AGENT_GOAL,
            backstory=VISA_AGENT_BACKSTORY,
            llm=self.llm,
            tools=[
                check_visa_requirements,
                get_embassy_info,
                generate_document_checklist,
                estimate_processing_time,
                check_travel_advisories,
            ],
            verbose=True,  # Enable verbose logging for debugging
            allow_delegation=False,  # Single agent, no delegation needed
        )

    def _run(self, input_data: VisaAgentInput) -> AgentResult:
        """
        Execute visa requirements analysis using CrewAI

        Args:
            input_data: VisaAgentInput with traveler and trip details

        Returns:
            AgentResult with VisaAgentOutput data

        Raises:
            AgentExecutionError: If analysis fails
        """
        try:
            # Create CrewAI task
            task = create_single_step_task(self.crew_agent, input_data)

            # Create and execute Crew
            crew = Crew(
                agents=[self.crew_agent],
                tasks=[task],
                process=Process.sequential,  # Single-agent sequential process
                verbose=True,
            )

            # Execute crew and get result
            crew_result = crew.kickoff()

            # Parse and validate result
            output = self._parse_crew_result(crew_result, input_data)

            # Build AgentResult
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=output.model_dump(),
                confidence=output.confidence_score,
                sources=[s.model_dump() for s in output.sources],
                execution_time=0.0,  # Will be set by BaseAgent
            )

        except Exception as e:
            raise AgentExecutionError(
                agent_name=self.name,
                message=f"Visa analysis failed: {str(e)}",
                original_error=e,
            )

    def _parse_crew_result(self, crew_result, input_data: VisaAgentInput) -> VisaAgentOutput:
        """
        Parse CrewAI result into VisaAgentOutput

        Args:
            crew_result: Raw result from CrewAI
            input_data: Original input data

        Returns:
            VisaAgentOutput: Structured output

        Note:
            CrewAI returns results as strings. We need to parse and structure them.
        """
        try:
            # Try to parse as JSON first
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

                result_data = json.loads(crew_result)
            else:
                result_data = crew_result

            # Build VisaRequirement
            visa_req_data = result_data.get("visa_requirement", {})
            visa_requirement = VisaRequirement(
                visa_required=visa_req_data.get("visa_required", False),
                visa_type=visa_req_data.get("visa_type"),
                max_stay_days=visa_req_data.get("max_stay_days"),
                validity_period=visa_req_data.get("validity_period"),
            )

            # Build ApplicationProcess
            app_proc_data = result_data.get("application_process", {})
            application_process = ApplicationProcess(
                application_method=app_proc_data.get("application_method"),
                processing_time=app_proc_data.get("processing_time"),
                cost_usd=app_proc_data.get("cost_usd"),
                cost_local=app_proc_data.get("cost_local"),
                required_documents=app_proc_data.get("required_documents", []),
                application_url=app_proc_data.get("application_url"),
            )

            # Build EntryRequirement
            entry_req_data = result_data.get("entry_requirements", {})
            entry_requirements = EntryRequirement(
                passport_validity=entry_req_data.get("passport_validity"),
                blank_pages_required=entry_req_data.get("blank_pages_required"),
                vaccinations=entry_req_data.get("vaccinations", []),
                health_declaration=entry_req_data.get("health_declaration", False),
                travel_insurance=entry_req_data.get("travel_insurance", False),
                proof_of_funds=entry_req_data.get("proof_of_funds", False),
                return_ticket=entry_req_data.get("return_ticket", False),
            )

            # Build sources
            sources_data = result_data.get("sources", [])
            sources = [
                SourceReference(
                    source_type=s.get("source_type", "api"),
                    url=s.get("url", ""),
                    description=s.get("description", ""),
                    last_accessed=(
                        datetime.fromisoformat(s["last_accessed"])
                        if "last_accessed" in s
                        else datetime.utcnow()
                    ),
                    confidence=s.get("confidence", 0.9),
                )
                for s in sources_data
            ]

            # Create output
            return VisaAgentOutput(
                trip_id=input_data.trip_id,
                generated_at=datetime.utcnow(),
                confidence_score=result_data.get("confidence_score", 0.9),
                visa_requirement=visa_requirement,
                application_process=application_process,
                entry_requirements=entry_requirements,
                tips=result_data.get("tips", []),
                warnings=result_data.get("warnings", []),
                sources=sources,
                last_verified=datetime.utcnow(),
            )

        except (json.JSONDecodeError, KeyError, ValueError):
            # Fallback: Create basic output from crew result text
            return self._create_fallback_output(crew_result, input_data)

    def _create_fallback_output(self, crew_result, input_data: VisaAgentInput) -> VisaAgentOutput:
        """
        Create fallback output when parsing fails

        This ensures we always return a valid VisaAgentOutput even if
        the LLM doesn't return perfect JSON.

        Args:
            crew_result: Raw crew result
            input_data: Original input

        Returns:
            VisaAgentOutput: Basic structured output
        """
        # Extract visa requirement from text
        result_text = str(crew_result).lower()
        visa_required = "visa required" in result_text or "visa is required" in result_text

        return VisaAgentOutput(
            trip_id=input_data.trip_id,
            generated_at=datetime.utcnow(),
            confidence_score=0.7,  # Lower confidence for fallback
            visa_requirement=VisaRequirement(
                visa_required=visa_required,
                visa_type="unknown",
                max_stay_days=None,
            ),
            application_process=ApplicationProcess(),
            entry_requirements=EntryRequirement(),
            tips=["Please verify visa requirements with official sources"],
            warnings=["This is a fallback result. Verification recommended."],
            sources=[
                SourceReference(
                    source_type="agent",
                    url="",
                    description="Visa Agent analysis (fallback mode)",
                    last_accessed=datetime.utcnow(),
                    confidence=0.7,
                )
            ],
            last_verified=datetime.utcnow(),
        )
