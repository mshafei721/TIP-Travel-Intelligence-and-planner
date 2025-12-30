"""Food Agent implementation using CrewAI."""

import json
import logging
import re
from datetime import datetime

from crewai import Agent, Crew

from ..base import BaseAgent
from ..config import AgentConfig, get_llm
from ..interfaces import SourceReference
from .models import (
    DietaryAvailability,
    Dish,
    FoodAgentInput,
    FoodAgentOutput,
)
from .prompts import (
    FOOD_AGENT_BACKSTORY,
    FOOD_AGENT_GOAL,
    FOOD_AGENT_ROLE,
)
from .tasks import (
    create_comprehensive_food_task,
)
from .tools import (
    get_dietary_availability,
    get_dining_etiquette,
    get_food_safety_info,
    get_must_try_dishes,
    get_restaurant_price_ranges,
    get_street_food_info,
    search_food_info,
)

logger = logging.getLogger(__name__)


class FoodAgent(BaseAgent):
    """
    Food Agent for travel culinary intelligence.

    Provides comprehensive food and culinary guidance including must-try dishes,
    restaurant recommendations, dietary accommodations, street food options,
    food safety tips, and authentic culinary experiences using CrewAI framework
    and food knowledge bases.

    Features:
    - Must-try local dishes and specialties
    - Restaurant and food venue recommendations
    - Street food safety and options
    - Dietary accommodations (vegetarian, vegan, halal, kosher, gluten-free)
    - Food safety and hygiene tips
    - Dining etiquette and customs
    - Price ranges for different dining levels
    - Local ingredients and food markets
    - Cooking classes and food tours

    Data Sources:
    - Culinary knowledge bases
    - Regional food databases
    - Restaurant and venue reviews
    - Food safety guidelines
    """

    @property
    def agent_type(self) -> str:
        """Return agent type identifier."""
        return "food"

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_model: str = "claude-sonnet-4-20250514",
    ):
        """
        Initialize Food Agent.

        Args:
            config: Agent configuration (optional)
            llm_model: Claude AI model to use
        """
        # Initialize config
        if config is None:
            config = AgentConfig(
                name="Food Agent",
                agent_type=self.agent_type,
                description="Culinary travel intelligence and food culture specialist",
                version="1.0.0",
            )

        super().__init__(config)

        # Initialize LLM with fallback support (Anthropic -> Gemini -> OpenAI)
        self.llm = get_llm(temperature=0.1)

        # Create CrewAI agent
        self.agent = self._create_agent()

        logger.info(f"FoodAgent initialized with model: {llm_model}")

    def _create_agent(self) -> Agent:
        """
        Create the CrewAI Food Agent.

        Returns:
            Configured CrewAI Agent with food intelligence tools
        """
        return Agent(
            role=FOOD_AGENT_ROLE,
            goal=FOOD_AGENT_GOAL,
            backstory=FOOD_AGENT_BACKSTORY,
            llm=self.llm,
            tools=[
                search_food_info,  # Web search for real-time food info
                get_must_try_dishes,
                get_dietary_availability,
                get_food_safety_info,
                get_restaurant_price_ranges,
                get_dining_etiquette,
                get_street_food_info,
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

    def _normalize_street_food(self, data: list | dict | None) -> list:
        """
        Normalize street food data from LLM output to StreetFood models.

        LLM may return various formats:
        - List of dicts with typical_prices instead of price_range
        - Dict with popular_items

        Args:
            data: Raw street food data

        Returns:
            List of StreetFood-compatible dicts
        """
        from .models import StreetFood

        if data is None:
            return []

        if isinstance(data, list):
            result = []
            for item in data:
                if isinstance(item, dict):
                    # Map typical_prices -> price_range
                    normalized = {
                        "name": item.get("name", "Unknown"),
                        "description": item.get("description", "Street food item"),
                        "where_to_find": item.get("where_to_find", item.get("location", "Various locations")),
                        "safety_rating": item.get("safety_rating", "generally-safe"),
                        "price_range": item.get("price_range") or item.get("typical_prices", "$1-5"),
                    }
                    try:
                        result.append(StreetFood(**normalized))
                    except Exception:
                        # If validation fails, skip this item
                        pass
                elif isinstance(item, str):
                    # Simple string item - create minimal StreetFood
                    try:
                        result.append(StreetFood(
                            name=item,
                            description=f"{item} - local street food",
                            where_to_find="Street vendors",
                            safety_rating="generally-safe",
                            price_range="$1-5",
                        ))
                    except Exception:
                        pass
            return result

        if isinstance(data, dict):
            # Handle dict with popular_items
            items = data.get("popular_items", [])
            return self._normalize_street_food(items)

        return []

    def _normalize_dining_etiquette(self, data: list | dict | None) -> list[str]:
        """
        Normalize dining etiquette data from LLM output.

        LLM may return a dict like:
        {"important_customs": ["Rule 1", ...], "taboos": ["Don't do X", ...]}

        We need to convert it to a list of strings.

        Args:
            data: Raw dining etiquette data

        Returns:
            List of etiquette tips
        """
        if data is None:
            return ["Observe local dining customs", "Be respectful of cultural differences"]

        if isinstance(data, list):
            # Already a list - ensure items are strings
            result = []
            for item in data:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    # Extract rule or description
                    rule = item.get("rule") or item.get("custom") or item.get("tip") or str(item)
                    result.append(rule)
            return result

        if isinstance(data, dict):
            # Extract etiquette rules from dict
            rules = []
            if "important_customs" in data:
                customs = data["important_customs"]
                if isinstance(customs, list):
                    rules.extend(customs)
            if "dos" in data or "do" in data:
                dos = data.get("dos") or data.get("do", [])
                if isinstance(dos, list):
                    rules.extend([f"Do: {d}" for d in dos])
            if "donts" in data or "dont" in data:
                donts = data.get("donts") or data.get("dont", [])
                if isinstance(donts, list):
                    rules.extend([f"Don't: {d}" for d in donts])
            if "taboos" in data:
                taboos = data["taboos"]
                if isinstance(taboos, list):
                    rules.extend([f"Avoid: {t}" for t in taboos])
            if "general" in data:
                general = data["general"]
                if isinstance(general, list):
                    rules.extend(general)
                else:
                    rules.append(str(general))
            return rules if rules else ["Observe local dining customs"]

        return ["Observe local dining customs"]

    def _normalize_dietary_availability(self, data: dict | DietaryAvailability | None) -> DietaryAvailability:
        """
        Normalize dietary availability from LLM output.

        Args:
            data: Raw dietary availability data

        Returns:
            DietaryAvailability model instance
        """
        if data is None:
            return DietaryAvailability(
                vegetarian="limited",
                vegan="limited",
                halal="limited",
                kosher="rare",
                gluten_free="limited",
            )

        if isinstance(data, DietaryAvailability):
            return data

        if isinstance(data, dict):
            return DietaryAvailability(
                vegetarian=data.get("vegetarian", "limited"),
                vegan=data.get("vegan", "limited"),
                halal=data.get("halal", "limited"),
                kosher=data.get("kosher", "rare"),
                gluten_free=data.get("gluten_free", "limited"),
            )

        return DietaryAvailability(
            vegetarian="limited",
            vegan="limited",
            halal="limited",
            kosher="rare",
            gluten_free="limited",
        )

    def _normalize_restaurant_recommendations(self, data: list | None) -> list:
        """
        Normalize restaurant recommendations from LLM output.

        LLM may return specialties as comma-separated string instead of list.

        Args:
            data: Raw restaurant recommendations data

        Returns:
            List of Restaurant-compatible dicts
        """
        from .models import Restaurant

        if data is None:
            return []

        result = []
        for item in data:
            if isinstance(item, dict):
                # Convert comma-separated specialties to list
                specialties = item.get("specialties", [])
                if isinstance(specialties, str):
                    specialties = [s.strip() for s in specialties.split(",") if s.strip()]

                normalized = {
                    "name": item.get("name", "Restaurant"),
                    "type": item.get("type", "restaurant"),
                    "cuisine": item.get("cuisine", "Local"),
                    "price_level": item.get("price_level", item.get("price_range", "$$")),
                    "location": item.get("location"),
                    "specialties": specialties,
                    "notes": item.get("notes"),
                }
                try:
                    result.append(Restaurant(**normalized))
                except Exception:
                    pass
        return result

    def _normalize_must_try_dishes(self, data: list | None) -> list:
        """
        Normalize must-try dishes from LLM output.

        Args:
            data: Raw dishes data

        Returns:
            List of Dish-compatible dicts
        """
        from .models import Dish

        if data is None:
            return []

        result = []
        for item in data:
            if isinstance(item, dict):
                normalized = {
                    "name": item.get("name", "Local Dish"),
                    "description": item.get("description", "Traditional local dish"),
                    "category": item.get("category", "main"),
                    "spicy_level": item.get("spicy_level"),
                    "is_vegetarian": item.get("is_vegetarian", False),
                    "is_vegan": item.get("is_vegan", False),
                    "typical_price_range": item.get("typical_price_range", item.get("price_range", "$$")),
                }
                try:
                    result.append(Dish(**normalized))
                except Exception:
                    pass
            elif isinstance(item, str):
                try:
                    result.append(Dish(
                        name=item,
                        description=f"{item} - must-try local dish",
                        category="main",
                    ))
                except Exception:
                    pass
        return result

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
            "must_try_dishes",
            "restaurant_recommendations",
            "dining_etiquette",
            "dietary_availability",
            "meal_price_ranges",
        ]
        for field in required_fields:
            if result.get(field):
                score += 0.1

        # Check for must-try dishes count (0.2)
        if result.get("must_try_dishes") and len(result.get("must_try_dishes", [])) >= 5:
            score += 0.2

        # Check for restaurant recommendations (0.1)
        if result.get("restaurant_recommendations") and len(result.get("restaurant_recommendations", [])) >= 3:
            score += 0.1

        # Check for food safety tips (0.1)
        if result.get("food_safety_tips") and len(result.get("food_safety_tips", [])) >= 3:
            score += 0.1

        # Check for water safety (0.1)
        if result.get("water_safety"):
            score += 0.1

        return min(score, 1.0)

    def run(self, input_data: FoodAgentInput) -> FoodAgentOutput:
        """
        Execute the food agent to generate culinary intelligence.

        Args:
            input_data: FoodAgentInput with trip details

        Returns:
            FoodAgentOutput with comprehensive food and culinary information

        Raises:
            ValueError: If execution fails or output cannot be parsed
        """
        logger.info(f"Running Food Agent for {input_data.destination_country}")

        try:
            # Create comprehensive food task
            task = create_comprehensive_food_task(
                agent=self.agent,
                destination_country=input_data.destination_country,
            )

            # Create crew and execute
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)

            # Execute crew
            result = crew.kickoff()
            logger.info("Food Agent execution completed")

            # Parse result
            result_text = str(result)
            parsed_result = self._extract_json_from_text(result_text)

            if not parsed_result:
                logger.warning("Could not parse JSON from result, using fallback")
                # Create minimal fallback result
                parsed_result = self._create_fallback_result(input_data)

            # Calculate confidence
            confidence = self._calculate_confidence(parsed_result)
            logger.info(f"Food Agent confidence: {confidence:.2f}")

            # Normalize complex fields from LLM output
            street_food = self._normalize_street_food(parsed_result.get("street_food"))
            dining_etiquette = self._normalize_dining_etiquette(parsed_result.get("dining_etiquette"))
            dietary_availability = self._normalize_dietary_availability(parsed_result.get("dietary_availability"))
            restaurant_recommendations = self._normalize_restaurant_recommendations(parsed_result.get("restaurant_recommendations"))
            must_try_dishes = self._normalize_must_try_dishes(parsed_result.get("must_try_dishes"))

            # Build output model
            output = FoodAgentOutput(
                trip_id=input_data.trip_id,
                agent_type=self.agent_type,
                generated_at=datetime.utcnow(),
                confidence_score=confidence,
                sources=[
                    SourceReference(
                        title="Culinary Knowledge Base",
                        url="internal://culinary-knowledge-base",
                        verified_at=datetime.utcnow(),
                    ),
                    SourceReference(
                        title="Food Safety Guidelines",
                        url="internal://food-safety-guidelines",
                        verified_at=datetime.utcnow(),
                    ),
                ],
                warnings=[],
                # Must-try dishes (normalized)
                must_try_dishes=must_try_dishes,
                # Street food (normalized)
                street_food=street_food,
                # Restaurants (normalized)
                restaurant_recommendations=restaurant_recommendations,
                # Dining etiquette (normalized)
                dining_etiquette=dining_etiquette,
                # Dietary options (normalized)
                dietary_availability=dietary_availability,
                dietary_notes=parsed_result.get("dietary_notes", []),
                # Price ranges
                meal_price_ranges=parsed_result.get(
                    "meal_price_ranges",
                    {
                        "street_food": "$3-6",
                        "casual": "$10-20",
                        "mid_range": "$25-50",
                        "fine_dining": "$70-120",
                    },
                ),
                # Food safety
                food_safety_tips=parsed_result.get(
                    "food_safety_tips",
                    [
                        "Wash hands before eating",
                        "Choose busy, popular vendors",
                        "Ensure food is cooked thoroughly",
                    ],
                ),
                water_safety=parsed_result.get("water_safety", "Check local advisories"),
                # Additional info
                local_ingredients=parsed_result.get("local_ingredients", []),
                food_markets=parsed_result.get("food_markets", []),
                cooking_classes=parsed_result.get("cooking_classes"),
                food_tours=parsed_result.get("food_tours"),
            )

            logger.info(f"Food Agent completed for {input_data.destination_country}")
            return output

        except Exception as e:
            logger.error(f"Food Agent execution failed: {e}", exc_info=True)
            raise ValueError(f"Failed to execute Food Agent: {str(e)}")

    def _create_fallback_result(self, input_data: FoodAgentInput) -> dict:
        """
        Create fallback result when parsing fails.

        Args:
            input_data: Original input data

        Returns:
            Dictionary with minimal food information
        """
        return {
            "must_try_dishes": [
                Dish(
                    name="Local Specialty",
                    description="Try local specialties at popular restaurants",
                    category="main",
                    typical_price_range="$$",
                ).model_dump()
            ],
            "street_food": [],
            "restaurant_recommendations": [],
            "dining_etiquette": [
                "Observe local dining customs",
                "Be respectful of cultural differences",
                "Ask locals for recommendations",
            ],
            "dietary_availability": {
                "vegetarian": "limited",
                "vegan": "limited",
                "halal": "limited",
                "kosher": "rare",
                "gluten_free": "limited",
            },
            "dietary_notes": [
                "Research dietary options before traveling",
                "Learn key phrases for dietary restrictions",
                "Ask restaurant staff about ingredients",
            ],
            "meal_price_ranges": {
                "street_food": "$3-6",
                "casual": "$10-20",
                "mid_range": "$25-50",
                "fine_dining": "$70-120",
            },
            "food_safety_tips": [
                "Wash hands frequently",
                "Choose busy, popular food vendors",
                "Drink bottled water if tap water safety is uncertain",
                "Ensure food is cooked thoroughly",
                "Trust your instincts - if something seems off, avoid it",
            ],
            "water_safety": "Check local water safety advisories before drinking tap water",
            "local_ingredients": [],
            "food_markets": [],
            "cooking_classes": None,
            "food_tours": None,
        }
