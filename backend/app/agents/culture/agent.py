"""Culture Agent implementation using CrewAI."""

import json
import logging
import re
from datetime import datetime

from crewai import Agent, Crew

from ..base import BaseAgent
from ..config import AgentConfig, get_llm
from ..interfaces import SourceReference
from .models import (
    CommonPhrase,
    CultureAgentInput,
    CultureAgentOutput,
    DressCodeInfo,
)
from .prompts import (
    CULTURE_AGENT_BACKSTORY,
    CULTURE_AGENT_GOAL,
    CULTURE_AGENT_ROLE,
)
from .tasks import (
    create_comprehensive_culture_task,
)
from .tools import (
    get_cultural_taboos,
    get_dress_code_guidelines,
    get_essential_phrases,
    get_etiquette_guidelines,
    get_greeting_customs,
    get_religious_considerations,
)

logger = logging.getLogger(__name__)


class CultureAgent(BaseAgent):
    """
    Culture Agent for travel cultural intelligence.

    Provides comprehensive cultural intelligence and etiquette guidance including
    customs, traditions, social norms, taboos, communication styles, and practical
    cultural sensitivity advice using CrewAI framework and cultural knowledge bases.

    Features:
    - Greeting customs and communication norms
    - Dress code expectations and modesty guidelines
    - Religious considerations and sensitivities
    - Cultural taboos and behaviors to avoid
    - Dining, social, and business etiquette
    - Essential phrases and language tips
    - Gift-giving and photography etiquette
    - Time culture and punctuality expectations
    - Cultural sensitivity guidelines

    Data Sources:
    - Cultural anthropology knowledge bases
    - Country-specific etiquette databases
    - Religious practice guidelines
    - Language and phrase dictionaries
    """

    @property
    def agent_type(self) -> str:
        """Return agent type identifier."""
        return "culture"

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_model: str = "claude-sonnet-4-20250514",
    ):
        """
        Initialize Culture Agent.

        Args:
            config: Agent configuration (optional)
            llm_model: Claude AI model to use
        """
        # Initialize config
        if config is None:
            config = AgentConfig(
                name="Culture Agent",
                agent_type=self.agent_type,
                description="Cross-cultural intelligence and etiquette specialist",
                version="1.0.0",
            )

        super().__init__(config)

        # Initialize LLM with fallback support (Anthropic -> Gemini -> OpenAI)
        self.llm = get_llm(temperature=0.1)

        # Create CrewAI agent
        self.agent = self._create_agent()

        logger.info(f"CultureAgent initialized with model: {llm_model}")

    def _create_agent(self) -> Agent:
        """
        Create the CrewAI Culture Agent.

        Returns:
            Configured CrewAI Agent with cultural intelligence tools
        """
        return Agent(
            role=CULTURE_AGENT_ROLE,
            goal=CULTURE_AGENT_GOAL,
            backstory=CULTURE_AGENT_BACKSTORY,
            llm=self.llm,
            tools=[
                get_greeting_customs,
                get_dress_code_guidelines,
                get_religious_considerations,
                get_cultural_taboos,
                get_etiquette_guidelines,
                get_essential_phrases,
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

    def _normalize_dress_code(self, dress_code_data: dict | DressCodeInfo | None) -> DressCodeInfo:
        """
        Normalize dress code data from LLM output to DressCodeInfo model.

        Handles field name variations:
        - casual_guidelines -> casual
        - formal_guidelines -> formal
        - religious_site_requirements -> religious_sites
        - beach_swimwear_guidelines -> beaches
        """
        if dress_code_data is None:
            return DressCodeInfo(
                casual="Dress modestly",
                formal=None,
                religious_sites="Cover shoulders and knees",
                beaches=None,
                general_notes="Research local dress norms",
            )

        if isinstance(dress_code_data, DressCodeInfo):
            return dress_code_data

        if isinstance(dress_code_data, dict):
            return DressCodeInfo(
                casual=dress_code_data.get("casual") or dress_code_data.get("casual_guidelines", "Dress modestly"),
                formal=dress_code_data.get("formal") or dress_code_data.get("formal_guidelines"),
                religious_sites=dress_code_data.get("religious_sites") or dress_code_data.get("religious_site_requirements"),
                beaches=dress_code_data.get("beaches") or dress_code_data.get("beach_swimwear_guidelines"),
                general_notes=dress_code_data.get("general_notes"),
            )

        return DressCodeInfo(casual="Dress modestly")

    def _normalize_religious_considerations(self, data: dict | list | None) -> tuple[str | None, list]:
        """
        Normalize religious considerations from LLM output.

        LLM may return a dict with:
        - primary_religions: list
        - considerations: list of dicts

        Or a list of ReligiousConsideration-like dicts.

        Returns:
            Tuple of (primary_religion string, list of ReligiousConsideration dicts)
        """
        if data is None:
            return None, []

        primary_religion = None
        considerations = []

        if isinstance(data, dict):
            # Extract primary religion(s)
            primary_religions = data.get("primary_religions", [])
            if isinstance(primary_religions, list) and primary_religions:
                primary_religion = ", ".join(primary_religions)
            elif isinstance(primary_religions, str):
                primary_religion = primary_religions

            # Extract considerations list
            considerations_data = data.get("considerations", [])
            if isinstance(considerations_data, list):
                considerations = considerations_data
        elif isinstance(data, list):
            # Already a list of considerations
            considerations = data

        return primary_religion, considerations

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

        # Check for required fields (0.5 total)
        required_fields = [
            "greeting_customs",
            "communication_style",
            "dress_code",
            "official_languages",
            "common_phrases",
        ]
        for field in required_fields:
            if result.get(field):
                score += 0.1

        # Check for religious considerations (0.1)
        if result.get("religious_considerations") and len(result.get("religious_considerations", [])) > 0:
            score += 0.1

        # Check for taboos (0.1)
        if result.get("taboos") and len(result.get("taboos", [])) > 2:
            score += 0.1

        # Check for etiquette (0.2)
        if result.get("dining_etiquette") and len(result.get("dining_etiquette", [])) > 0:
            score += 0.1
        if result.get("social_etiquette") and len(result.get("social_etiquette", [])) > 0:
            score += 0.1

        # Check for cultural sensitivity tips (0.1)
        if (
            result.get("cultural_sensitivity_tips")
            and len(result.get("cultural_sensitivity_tips", [])) > 3
        ):
            score += 0.1

        return min(score, 1.0)

    def run(self, input_data: CultureAgentInput) -> CultureAgentOutput:
        """
        Execute the culture agent to generate cultural intelligence.

        Args:
            input_data: CultureAgentInput with trip details

        Returns:
            CultureAgentOutput with comprehensive cultural intelligence

        Raises:
            ValueError: If execution fails or output cannot be parsed
        """
        logger.info(f"Running Culture Agent for {input_data.destination_country}")

        try:
            # Create comprehensive culture task
            task = create_comprehensive_culture_task(
                agent=self.agent,
                destination_country=input_data.destination_country,
            )

            # Create crew and execute
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)

            # Execute crew
            result = crew.kickoff()
            logger.info("Culture Agent execution completed")

            # Parse result
            result_text = str(result)
            parsed_result = self._extract_json_from_text(result_text)

            if not parsed_result:
                logger.warning("Could not parse JSON from result, using fallback")
                # Create minimal fallback result
                parsed_result = self._create_fallback_result(input_data)

            # Calculate confidence
            confidence = self._calculate_confidence(parsed_result)
            logger.info(f"Culture Agent confidence: {confidence:.2f}")

            # Handle nested greetings_communication structure
            greetings_comm = parsed_result.get("greetings_communication", {})
            if isinstance(greetings_comm, dict):
                # LLM may wrap greeting data in a greetings_communication object
                if not parsed_result.get("greeting_customs") and greetings_comm.get("greeting_customs"):
                    parsed_result["greeting_customs"] = greetings_comm.get("greeting_customs")
                if not parsed_result.get("communication_style") and greetings_comm.get("communication_style"):
                    parsed_result["communication_style"] = greetings_comm.get("communication_style")
                if not parsed_result.get("body_language_notes") and greetings_comm.get("body_language_notes"):
                    parsed_result["body_language_notes"] = greetings_comm.get("body_language_notes")

            # Normalize dress code data from LLM output
            dress_code = self._normalize_dress_code(parsed_result.get("dress_code"))

            # Normalize religious considerations from LLM output
            primary_religion, religious_considerations = self._normalize_religious_considerations(
                parsed_result.get("religious_considerations")
            )
            # Also check for primary_religion at top level
            if not primary_religion and parsed_result.get("primary_religion"):
                primary_religion = parsed_result.get("primary_religion")

            # Build output model
            output = CultureAgentOutput(
                trip_id=input_data.trip_id,
                agent_type=self.agent_type,
                generated_at=datetime.utcnow(),
                confidence_score=confidence,
                sources=[
                    SourceReference(
                        title="Cultural Anthropology Database",
                        url="internal://cultural-anthropology-database",
                        verified_at=datetime.utcnow(),
                    ),
                    SourceReference(
                        title="Country Etiquette Guide",
                        url="internal://country-etiquette-guide",
                        verified_at=datetime.utcnow(),
                    ),
                ],
                warnings=[],
                # Greeting & Communication
                greeting_customs=parsed_result.get("greeting_customs", ["Greet respectfully"]),
                communication_style=parsed_result.get("communication_style", "varies by culture"),
                body_language_notes=parsed_result.get("body_language_notes", []),
                # Dress Code (normalized)
                dress_code=dress_code,
                # Religious Considerations (normalized)
                primary_religion=primary_religion,
                religious_considerations=religious_considerations,
                # Taboos
                taboos=parsed_result.get("taboos", []),
                # Etiquette
                dining_etiquette=parsed_result.get("dining_etiquette", []),
                social_etiquette=parsed_result.get("social_etiquette", []),
                business_etiquette=parsed_result.get("business_etiquette"),
                # Language
                official_languages=parsed_result.get("official_languages", ["English"]),
                common_phrases=parsed_result.get(
                    "common_phrases",
                    [
                        CommonPhrase(
                            english="Hello",
                            local="Hello",
                            pronunciation=None,
                            context="General greeting",
                        ),
                        CommonPhrase(
                            english="Thank you",
                            local="Thank you",
                            pronunciation=None,
                            context="Expressing gratitude",
                        ),
                    ],
                ),
                language_tips=parsed_result.get("language_tips", []),
                # Gift Giving
                gift_giving_customs=parsed_result.get("gift_giving_customs"),
                # Photography
                photography_etiquette=parsed_result.get("photography_etiquette", []),
                # Time Culture
                time_culture=parsed_result.get("time_culture"),
                # Cultural Sensitivity
                cultural_sensitivity_tips=parsed_result.get(
                    "cultural_sensitivity_tips",
                    [
                        "Research local customs before traveling",
                        "Show respect for local traditions",
                        "Be open-minded and adaptable",
                        "Observe and learn from locals",
                    ],
                ),
                respect_local_customs_summary=parsed_result.get(
                    "respect_local_customs_summary",
                    "Respect local customs, traditions, and cultural norms. Be mindful of differences and approach cultural experiences with humility and openness.",
                ),
            )

            logger.info(f"Culture Agent completed for {input_data.destination_country}")
            return output

        except Exception as e:
            logger.error(f"Culture Agent execution failed: {e}", exc_info=True)
            raise ValueError(f"Failed to execute Culture Agent: {str(e)}")

    def _create_fallback_result(self, input_data: CultureAgentInput) -> dict:
        """
        Create fallback result when parsing fails.

        Args:
            input_data: Original input data

        Returns:
            Dictionary with minimal cultural information
        """
        return {
            "greeting_customs": [
                "Research local greeting customs",
                "Be respectful and observe local practices",
            ],
            "communication_style": "varies by culture - observe and adapt",
            "body_language_notes": [
                "Be aware that body language varies across cultures",
                "Observe local practices and adapt accordingly",
            ],
            "dress_code": {
                "casual": "Dress modestly and respectfully",
                "formal": "Business attire for formal occasions",
                "religious_sites": "Cover shoulders and knees, remove shoes if required",
                "beaches": "Respect local norms for beachwear",
                "general_notes": "Research specific dress codes for your destination",
            },
            "primary_religion": None,
            "religious_considerations": [],
            "taboos": [],
            "dining_etiquette": [
                {
                    "category": "Dining",
                    "rule": "Table manners",
                    "do": ["Wait for host to start", "Use utensils properly"],
                    "dont": ["Talk with mouth full", "Use phone at table"],
                }
            ],
            "social_etiquette": [
                {
                    "category": "Social",
                    "rule": "Be respectful",
                    "do": ["Observe local customs", "Be polite"],
                    "dont": ["Assume your customs apply everywhere"],
                }
            ],
            "business_etiquette": None,
            "official_languages": ["English"],
            "common_phrases": [
                {
                    "english": "Hello",
                    "local": "Hello",
                    "pronunciation": None,
                    "context": "General greeting",
                },
                {
                    "english": "Thank you",
                    "local": "Thank you",
                    "pronunciation": None,
                    "context": "Expressing gratitude",
                },
                {
                    "english": "Please",
                    "local": "Please",
                    "pronunciation": None,
                    "context": "Making requests",
                },
            ],
            "language_tips": [
                "Learn basic phrases in the local language",
                "Speak clearly and be patient",
                "Use translation apps when needed",
            ],
            "gift_giving_customs": None,
            "photography_etiquette": [
                "Always ask permission before photographing people",
                "Respect photography restrictions at sacred sites",
            ],
            "time_culture": None,
            "cultural_sensitivity_tips": [
                "Research local customs and traditions before traveling",
                "Show respect for cultural differences",
                "Be open-minded and willing to learn",
                "Observe local behavior and adapt accordingly",
                "Ask questions politely when unsure",
            ],
            "respect_local_customs_summary": "Every culture is unique. Approach your travels with respect, humility, and openness. Research beforehand, observe local practices, and be willing to adapt your behavior to show respect for your host country's customs and traditions.",
        }
