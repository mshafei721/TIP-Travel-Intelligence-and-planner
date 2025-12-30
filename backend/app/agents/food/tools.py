"""
Food Agent CrewAI Tools

Tools for food research, restaurant recommendations, and culinary intelligence.
Uses Firecrawl for real-time web search when configured.
"""

import json
import logging

from crewai.tools import tool

from app.core.config import settings

logger = logging.getLogger(__name__)


def _search_food_info(query: str, limit: int = 3) -> list[dict]:
    """
    Search web for food/culinary information using Firecrawl.

    Args:
        query: Search query
        limit: Max results

    Returns:
        List of search results with content
    """
    if not settings.FIRECRAWL_API_KEY:
        logger.warning("Firecrawl API key not configured - using static data")
        return []

    try:
        from app.services.web_search import search_web

        results = search_web(query, limit=limit)
        return results
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []


@tool("Search food and restaurant information")
def search_food_info(country: str, topic: str) -> str:
    """
    Search the web for current food and restaurant information about a country.

    Uses Firecrawl to find up-to-date food guides, restaurant recommendations,
    and culinary travel information.

    Args:
        country: Country or city name (e.g., "Japan", "Paris")
        topic: Specific topic (e.g., "street food", "best restaurants", "local dishes")

    Returns:
        JSON string with search results containing real-time food information

    Example:
        >>> search_food_info("Tokyo", "best ramen restaurants")
    """
    query = f"{country} {topic} food travel guide restaurant recommendations"

    results = _search_food_info(query, limit=3)

    if results:
        # Extract relevant content from search results
        extracted = []
        for r in results:
            extracted.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("markdown", r.get("content", ""))[:2000],  # Limit content size
            })

        logger.info(f"Found {len(extracted)} web results for {country} {topic}")
        return json.dumps({
            "country": country,
            "topic": topic,
            "source": "web_search",
            "results": extracted,
        })
    else:
        logger.info(f"No web results for {country} {topic}, using static data")
        return json.dumps({
            "country": country,
            "topic": topic,
            "source": "static",
            "results": [],
            "note": "No web search results available. Using built-in food knowledge.",
        })


@tool("Get must-try dishes")
def get_must_try_dishes(country: str) -> str:
    """
    Get must-try dishes and local specialties for a country.

    Args:
        country: Country name (e.g., "Japan", "Italy")

    Returns:
        JSON string with must-try dishes

    Note: This provides curated dish recommendations for common destinations.
    """
    country_lower = country.lower()

    dishes_map = {
        "japan": [
            {
                "name": "Sushi",
                "description": "Fresh raw fish on vinegared rice",
                "category": "main",
                "spicy_level": 0,
                "is_vegetarian": False,
                "price_range": "$$-$$$",
            },
            {
                "name": "Ramen",
                "description": "Noodle soup with various broths and toppings",
                "category": "main",
                "spicy_level": 1,
                "is_vegetarian": False,
                "price_range": "$-$$",
            },
            {
                "name": "Tempura",
                "description": "Lightly battered and fried seafood/vegetables",
                "category": "main",
                "spicy_level": 0,
                "is_vegetarian": False,
                "price_range": "$$",
            },
        ],
        "italy": [
            {
                "name": "Pizza Margherita",
                "description": "Classic Neapolitan pizza with tomato, mozzarella, basil",
                "category": "main",
                "spicy_level": 0,
                "is_vegetarian": True,
                "price_range": "$-$$",
            },
            {
                "name": "Pasta Carbonara",
                "description": "Pasta with eggs, pecorino cheese, guanciale, black pepper",
                "category": "main",
                "spicy_level": 0,
                "is_vegetarian": False,
                "price_range": "$$",
            },
            {
                "name": "Gelato",
                "description": "Italian ice cream with intense flavors",
                "category": "dessert",
                "spicy_level": 0,
                "is_vegetarian": True,
                "price_range": "$",
            },
        ],
        "thailand": [
            {
                "name": "Pad Thai",
                "description": "Stir-fried rice noodles with shrimp, tofu, peanuts",
                "category": "main",
                "spicy_level": 2,
                "is_vegetarian": False,
                "price_range": "$",
            },
            {
                "name": "Tom Yum Goong",
                "description": "Spicy and sour shrimp soup",
                "category": "main",
                "spicy_level": 3,
                "is_vegetarian": False,
                "price_range": "$-$$",
            },
            {
                "name": "Green Curry",
                "description": "Coconut curry with chicken or vegetables",
                "category": "main",
                "spicy_level": 3,
                "is_vegetarian": False,
                "price_range": "$-$$",
            },
        ],
    }

    result = {
        "country": country,
        "dishes": dishes_map.get(country_lower, []),
    }

    logger.info(f"Must-try dishes for {country}: {len(result['dishes'])} found")
    return str(result)


@tool("Get dietary availability")
def get_dietary_availability(country: str) -> str:
    """
    Get availability of dietary options (vegetarian, vegan, halal, kosher, gluten-free).

    Args:
        country: Country name (e.g., "India", "Israel")

    Returns:
        JSON string with dietary availability levels

    Note: Levels are: widespread, common, limited, rare
    """
    country_lower = country.lower()

    # High vegetarian/vegan availability
    high_veg = ["india", "thailand", "vietnam", "taiwan", "israel"]
    # Moderate vegetarian availability
    moderate_veg = ["italy", "japan", "uk", "united kingdom", "usa", "united states", "spain"]
    # High halal availability
    high_halal = ["malaysia", "indonesia", "turkey", "uae", "dubai", "saudi", "arabia", "egypt", "morocco"]
    # High kosher availability
    high_kosher = ["israel"]

    result = {
        "country": country,
        "vegetarian": "limited",
        "vegan": "limited",
        "halal": "limited",
        "kosher": "rare",
        "gluten_free": "limited",
    }

    if any(c in country_lower for c in high_veg):
        result.update({
            "vegetarian": "widespread",
            "vegan": "common" if "india" in country_lower else "common",
        })
    elif any(c in country_lower for c in moderate_veg):
        result.update({
            "vegetarian": "common",
            "vegan": "limited",
        })

    if any(c in country_lower for c in high_halal):
        result["halal"] = "widespread"
    elif "muslim" in country_lower or any(c in country_lower for c in ["pakistan", "bangladesh", "afghanistan"]):
        result["halal"] = "widespread"

    if any(c in country_lower for c in high_kosher):
        result["kosher"] = "widespread"

    # Gluten-free awareness is generally better in Western countries
    if any(c in country_lower for c in ["usa", "united states", "uk", "united kingdom", "australia", "canada"]):
        result["gluten_free"] = "common"

    logger.info(f"Dietary availability for {country}: vegetarian={result['vegetarian']}, vegan={result['vegan']}")
    return str(result)


@tool("Get food safety information")
def get_food_safety_info(country: str) -> str:
    """
    Get food safety and hygiene information for a country.

    Args:
        country: Country name (e.g., "Mexico", "France")

    Returns:
        JSON string with food safety tips and water safety

    Note: This provides general food safety guidance.
    """
    country_lower = country.lower()

    # Countries with generally safe tap water
    safe_water = [
        "usa", "united states", "canada", "uk", "united kingdom", "australia",
        "new zealand", "japan", "germany", "france", "italy", "spain", "portugal",
        "netherlands", "belgium", "switzerland", "austria", "denmark", "sweden",
        "norway", "finland", "singapore", "south korea"
    ]

    # Countries where caution is needed
    caution_water = [
        "mexico", "thailand", "vietnam", "cambodia", "india", "china", "philippines",
        "indonesia", "egypt", "morocco", "turkey", "brazil", "peru", "ecuador"
    ]

    water_status = "use-caution"
    if any(c in country_lower for c in safe_water):
        water_status = "safe-to-drink"
    elif any(c in country_lower for c in caution_water):
        water_status = "avoid-tap-water"

    safety_tips = [
        "Wash hands before eating",
        "Choose busy, popular food vendors",
        "Ensure food is cooked thoroughly",
        "Avoid raw vegetables washed in local water",
    ]

    if water_status == "avoid-tap-water":
        safety_tips.extend([
            "Drink only bottled or boiled water",
            "Avoid ice in drinks",
            "Use bottled water for brushing teeth",
        ])

    if any(c in country_lower for c in ["thailand", "vietnam", "india", "mexico"]):
        safety_tips.append("Build up tolerance gradually - start with milder foods")

    result = {
        "country": country,
        "water_safety": water_status,
        "food_safety_tips": safety_tips,
        "street_food_safety": "Choose vendors with high turnover and clean practices",
    }

    logger.info(f"Food safety for {country}: water={water_status}")
    return str(result)


@tool("Get restaurant price ranges")
def get_restaurant_price_ranges(country: str) -> str:
    """
    Get typical meal price ranges for different dining levels.

    Args:
        country: Country name (e.g., "Thailand", "Switzerland")

    Returns:
        JSON string with price ranges

    Note: Prices are approximate in USD.
    """
    country_lower = country.lower()

    # Budget-friendly destinations
    budget_countries = ["thailand", "vietnam", "india", "cambodia", "laos", "philippines", "indonesia", "egypt"]
    # Moderate pricing
    moderate_countries = ["mexico", "portugal", "spain", "greece", "turkey", "poland", "czech", "hungary"]
    # Expensive destinations
    expensive_countries = ["switzerland", "norway", "denmark", "iceland", "singapore", "japan", "australia"]

    if any(c in country_lower for c in budget_countries):
        ranges = {
            "street_food": "$1-3",
            "casual": "$3-8",
            "mid_range": "$10-20",
            "fine_dining": "$30-60",
        }
    elif any(c in country_lower for c in moderate_countries):
        ranges = {
            "street_food": "$3-6",
            "casual": "$8-15",
            "mid_range": "$20-40",
            "fine_dining": "$60-100",
        }
    elif any(c in country_lower for c in expensive_countries):
        ranges = {
            "street_food": "$6-12",
            "casual": "$15-30",
            "mid_range": "$40-80",
            "fine_dining": "$100-200+",
        }
    else:
        # Default moderate
        ranges = {
            "street_food": "$3-6",
            "casual": "$10-20",
            "mid_range": "$25-50",
            "fine_dining": "$70-120",
        }

    result = {
        "country": country,
        "meal_price_ranges": ranges,
    }

    logger.info(f"Price ranges for {country}: casual={ranges['casual']}")
    return str(result)


@tool("Get dining etiquette")
def get_dining_etiquette(country: str) -> str:
    """
    Get dining etiquette and customs for a country.

    Args:
        country: Country name (e.g., "France", "Japan")

    Returns:
        JSON string with dining etiquette rules

    Note: This provides cultural dining guidance.
    """
    country_lower = country.lower()

    etiquette_map = {
        "japan": [
            "Say 'itadakimasu' before eating and 'gochisosama' after",
            "Slurp noodles to show enjoyment",
            "Never stick chopsticks upright in rice",
            "Don't pass food chopstick to chopstick",
            "Finish everything on your plate",
        ],
        "france": [
            "Keep hands on the table (not in lap)",
            "Bread goes on the table, not on a plate",
            "Don't ask for substitutions or changes to dishes",
            "Wait for everyone to be served before eating",
            "Don't rush - meals are leisurely",
        ],
        "india": [
            "Wash hands before and after eating",
            "Use right hand for eating (left is unclean)",
            "Don't waste food - take only what you'll eat",
            "Remove shoes before entering dining area in homes",
            "It's polite to accept food offered by hosts",
        ],
        "china": [
            "Don't stick chopsticks upright in rice (funeral custom)",
            "Try a bit of everything offered",
            "Burping is acceptable",
            "Bones and shells go on table or separate plate",
            "The host pays - don't fight over the bill",
        ],
    }

    result = {
        "country": country,
        "dining_etiquette": etiquette_map.get(country_lower, [
            "Observe local dining customs",
            "Wait for host or elders to start eating",
            "Use utensils appropriately",
            "Don't talk with mouth full",
        ]),
    }

    logger.info(f"Dining etiquette for {country}: {len(result['dining_etiquette'])} rules")
    return str(result)


@tool("Get street food information")
def get_street_food_info(country: str) -> str:
    """
    Get street food recommendations and safety information.

    Args:
        country: Country name (e.g., "Thailand", "Mexico")

    Returns:
        JSON string with street food details

    Note: Emphasizes safety and popular items.
    """
    country_lower = country.lower()

    street_food_map = {
        "thailand": [
            {
                "name": "Pad Thai",
                "where": "Street carts and night markets",
                "safety": "generally-safe",
                "price": "$1-2",
            },
            {
                "name": "Som Tam (Papaya Salad)",
                "where": "Street vendors throughout",
                "safety": "use-caution",
                "price": "$1",
            },
            {
                "name": "Mango Sticky Rice",
                "where": "Dessert stalls and markets",
                "safety": "safe",
                "price": "$1-2",
            },
        ],
        "mexico": [
            {
                "name": "Tacos",
                "where": "Taquerías and street corners",
                "safety": "generally-safe",
                "price": "$1-2 each",
            },
            {
                "name": "Elote (Street Corn)",
                "where": "Street carts",
                "safety": "safe",
                "price": "$1-2",
            },
        ],
        "japan": [
            {
                "name": "Takoyaki",
                "where": "Street festivals and busy areas",
                "safety": "safe",
                "price": "$3-5",
            },
            {
                "name": "Yakitori",
                "where": "Street stalls and izakayas",
                "safety": "safe",
                "price": "$2-4 per skewer",
            },
        ],
    }

    result = {
        "country": country,
        "street_food": street_food_map.get(country_lower, []),
        "general_tips": [
            "Choose vendors with high customer turnover",
            "Look for clean cooking area and practices",
            "Trust your instincts - if it looks questionable, skip it",
            "Cooked-to-order items are generally safer than pre-cooked",
        ],
    }

    logger.info(f"Street food for {country}: {len(result['street_food'])} items")
    return str(result)
