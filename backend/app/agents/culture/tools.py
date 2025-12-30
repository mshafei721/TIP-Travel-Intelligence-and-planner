"""
Culture Agent CrewAI Tools

Tools for cultural research, etiquette guidance, and cultural intelligence.
Uses Firecrawl for real-time web search when configured.
"""

import json
import logging

from crewai.tools import tool

from app.core.config import settings

logger = logging.getLogger(__name__)


def _search_culture_info(query: str, limit: int = 3) -> list[dict]:
    """
    Search web for cultural information using Firecrawl.

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


@tool("Search cultural information")
def search_cultural_info(country: str, topic: str) -> str:
    """
    Search the web for current cultural information about a country.

    Uses Firecrawl to find up-to-date cultural guides, travel advice,
    and local customs information.

    Args:
        country: Country name (e.g., "Japan", "Morocco")
        topic: Specific topic (e.g., "dining etiquette", "dress code", "greetings")

    Returns:
        JSON string with search results containing real-time cultural information

    Example:
        >>> search_cultural_info("Japan", "business etiquette")
    """
    query = f"{country} {topic} culture travel guide customs"

    results = _search_culture_info(query, limit=3)

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
            "note": "No web search results available. Using built-in cultural knowledge.",
        })


@tool("Get greeting customs")
def get_greeting_customs(country: str) -> str:
    """
    Get greeting customs and communication norms for a country.

    Args:
        country: Country name (e.g., "Japan", "France")

    Returns:
        JSON string with greeting customs and communication style

    Note: This tool provides general cultural guidance.
    Always verify current customs, as cultures evolve.
    """
    country_lower = country.lower()

    # Categorize countries by greeting style
    # Note: These are general patterns; individual variations exist
    bow_cultures = ["japan", "korea", "south korea", "thailand"]
    cheek_kiss_cultures = ["france", "italy", "spain", "belgium", "netherlands", "greece", "portugal"]
    handshake_cultures = ["germany", "uk", "united kingdom", "usa", "united states", "canada", "australia"]
    namaste_cultures = ["india", "nepal", "bhutan"]

    result = {
        "country": country,
        "primary_greeting": "varies",
        "physical_contact": "varies",
        "formality": "moderate",
        "communication_style": "varies",
    }

    if any(c in country_lower for c in bow_cultures):
        result.update({
            "primary_greeting": "Bow",
            "physical_contact": "minimal - bowing preferred over handshakes",
            "formality": "high - use titles and last names",
            "communication_style": "indirect, high-context, emphasis on harmony",
        })
    elif any(c in country_lower for c in cheek_kiss_cultures):
        result.update({
            "primary_greeting": "Cheek kisses (typically 2-3 depending on region)",
            "physical_contact": "moderate to high - cheek kisses common among acquaintances",
            "formality": "moderate - formal in business, casual in social",
            "communication_style": "expressive, direct in France/Spain, moderate elsewhere",
        })
    elif any(c in country_lower for c in handshake_cultures):
        result.update({
            "primary_greeting": "Handshake",
            "physical_contact": "moderate - firm handshakes",
            "formality": "moderate - varies by context",
            "communication_style": "direct, low-context, explicit communication",
        })
    elif any(c in country_lower for c in namaste_cultures):
        result.update({
            "primary_greeting": "Namaste (hands pressed together, slight bow)",
            "physical_contact": "minimal - handshakes acceptable in business",
            "formality": "high - respect for elders and hierarchy",
            "communication_style": "moderate - indirect to avoid confrontation",
        })
    elif "arab" in country_lower or "middle east" in country_lower or any(c in country_lower for c in ["saudi", "uae", "qatar", "egypt"]):
        result.update({
            "primary_greeting": "Handshake (men), verbal greeting (mixed gender)",
            "physical_contact": "varies - gender considerations important",
            "formality": "high - use titles and show respect",
            "communication_style": "indirect, relationship-focused, high-context",
        })
    else:
        result.update({
            "primary_greeting": "Handshake or verbal greeting",
            "physical_contact": "moderate - handshakes common",
            "formality": "moderate",
            "communication_style": "varies by culture",
        })

    logger.info(f"Greeting customs for {country}: {result['primary_greeting']}")
    return str(result)


@tool("Get dress code guidelines")
def get_dress_code_guidelines(country: str) -> str:
    """
    Get dress code and modesty expectations for a country.

    Args:
        country: Country name (e.g., "Saudi Arabia", "Italy")

    Returns:
        JSON string with dress code guidelines

    Note: Dress codes vary by region, season, and context.
    """
    country_lower = country.lower()

    conservative_dress = ["saudi", "arabia", "iran", "afghanistan", "pakistan", "yemen", "egypt"]
    moderate_dress = ["turkey", "morocco", "tunisia", "india", "indonesia", "malaysia", "jordan"]
    western_casual = ["usa", "united states", "canada", "australia", "uk", "united kingdom", "germany", "france"]

    result = {
        "country": country,
        "general_modesty_level": "moderate",
        "casual_dress": "smart casual recommended",
        "religious_sites": "conservative dress required",
        "beach_attire": "varies by location",
    }

    if any(c in country_lower for c in conservative_dress):
        result.update({
            "general_modesty_level": "high - conservative dress required in public",
            "casual_dress": "Long sleeves, long pants/skirts. Women should cover hair in some areas.",
            "religious_sites": "Full coverage required. Women: headscarf, abaya. Men: long pants.",
            "beach_attire": "Gender-segregated beaches may exist. Conservative swimwear.",
        })
    elif any(c in country_lower for c in moderate_dress):
        result.update({
            "general_modesty_level": "moderate - dress conservatively, especially in rural areas",
            "casual_dress": "Cover shoulders and knees. Modest clothing preferred.",
            "religious_sites": "Conservative dress required. Remove shoes. Women may need headscarf.",
            "beach_attire": "Varies - tourist beaches more relaxed, local beaches conservative.",
        })
    elif any(c in country_lower for c in western_casual):
        result.update({
            "general_modesty_level": "relaxed - dress as you would at home",
            "casual_dress": "Casual wear acceptable. Smart casual for upscale venues.",
            "religious_sites": "Cover shoulders and knees. Remove hats indoors.",
            "beach_attire": "Standard swimwear acceptable at beaches.",
        })
    else:
        result.update({
            "general_modesty_level": "moderate - dress respectfully",
            "casual_dress": "Cover shoulders and knees in public areas.",
            "religious_sites": "Conservative dress required. Ask locally about specific requirements.",
            "beach_attire": "Varies by location and local customs.",
        })

    logger.info(f"Dress code for {country}: {result['general_modesty_level']}")
    return str(result)


@tool("Get religious considerations")
def get_religious_considerations(country: str) -> str:
    """
    Get religious considerations and sensitivities for a country.

    Args:
        country: Country name (e.g., "Thailand", "Israel")

    Returns:
        JSON string with religious considerations

    Note: Religious practices vary. Show respect for all beliefs.
    """
    country_lower = country.lower()

    result = {
        "country": country,
        "primary_religion": "varies",
        "considerations": [],
    }

    if "thai" in country_lower:
        result.update({
            "primary_religion": "Buddhism (95%)",
            "considerations": [
                {"topic": "Buddha images", "guideline": "Never touch or climb on Buddha statues. They are sacred.", "severity": "critical"},
                {"topic": "Monks", "guideline": "Women should not touch monks. Give offerings respectfully.", "severity": "critical"},
                {"topic": "Temples", "guideline": "Remove shoes before entering. Dress modestly.", "severity": "critical"},
                {"topic": "Head and feet", "guideline": "Head is sacred, feet are lowest. Don't point feet at Buddha or people.", "severity": "advisory"},
            ],
        })
    elif "saudi" in country_lower or "arabia" in country_lower:
        result.update({
            "primary_religion": "Islam (Sunni majority)",
            "considerations": [
                {"topic": "Prayer times", "guideline": "Business closes 5 times daily for prayer. Plan accordingly.", "severity": "advisory"},
                {"topic": "Ramadan", "guideline": "No eating/drinking/smoking in public during fasting hours.", "severity": "critical"},
                {"topic": "Alcohol", "guideline": "Alcohol is completely prohibited.", "severity": "critical"},
                {"topic": "Mosques", "guideline": "Non-Muslims generally not permitted. Ask permission. Women cover fully.", "severity": "critical"},
                {"topic": "Public behavior", "guideline": "No public displays of affection. Gender segregation in many spaces.", "severity": "critical"},
            ],
        })
    elif "israel" in country_lower:
        result.update({
            "primary_religion": "Judaism (majority), Islam, Christianity",
            "considerations": [
                {"topic": "Shabbat", "guideline": "Friday sunset to Saturday sunset. Public transport stops, many businesses close.", "severity": "advisory"},
                {"topic": "Kosher", "guideline": "Many restaurants are kosher. Respect dietary laws.", "severity": "info"},
                {"topic": "Holy sites", "guideline": "Dress modestly. Men cover heads at Western Wall. Women at mosques.", "severity": "critical"},
                {"topic": "Religious holidays", "guideline": "Major holidays affect transportation and business hours.", "severity": "advisory"},
            ],
        })
    elif "india" in country_lower or "nepal" in country_lower:
        result.update({
            "primary_religion": "Hinduism (India 80%), Buddhism (Nepal)",
            "considerations": [
                {"topic": "Temples", "guideline": "Remove shoes. Non-Hindus may be restricted in some temples.", "severity": "critical"},
                {"topic": "Sacred cows", "guideline": "Cows are sacred in Hinduism. Do not harm or disrespect them.", "severity": "critical"},
                {"topic": "Modest dress", "guideline": "Cover shoulders and knees at temples. Women may need to cover head.", "severity": "advisory"},
                {"topic": "Offerings", "guideline": "It's respectful to make small offerings at temples.", "severity": "info"},
            ],
        })
    elif "italy" in country_lower or "spain" in country_lower or "portugal" in country_lower:
        result.update({
            "primary_religion": "Christianity (Catholic majority)",
            "considerations": [
                {"topic": "Churches", "guideline": "Cover shoulders and knees. Remove hats. Silence inside.", "severity": "critical"},
                {"topic": "Mass times", "guideline": "Churches may be closed to tourists during mass/services.", "severity": "advisory"},
                {"topic": "Religious holidays", "guideline": "Easter and Christmas are major. Cities celebrate patron saints.", "severity": "info"},
            ],
        })
    else:
        result.update({
            "primary_religion": "Varies by country",
            "considerations": [
                {"topic": "Religious sites", "guideline": "Dress modestly. Remove shoes if required. Ask before photographing.", "severity": "advisory"},
                {"topic": "Local customs", "guideline": "Research specific religious practices before travel.", "severity": "advisory"},
            ],
        })

    logger.info(f"Religious considerations for {country}: {result['primary_religion']}")
    return str(result)


@tool("Get cultural taboos")
def get_cultural_taboos(country: str) -> str:
    """
    Get cultural taboos and behaviors to avoid for a country.

    Args:
        country: Country name (e.g., "China", "Brazil")

    Returns:
        JSON string with cultural taboos and alternatives

    Note: Taboos vary by region. Exercise cultural sensitivity.
    """
    country_lower = country.lower()

    result = {
        "country": country,
        "taboos": [],
    }

    if "china" in country_lower or "chinese" in country_lower:
        result["taboos"] = [
            {"behavior": "Sticking chopsticks upright in rice", "explanation": "Resembles incense at funerals - very inauspicious", "alternative": "Rest chopsticks on holder or bowl edge", "severity": "major"},
            {"behavior": "Giving clocks as gifts", "explanation": "Clock sounds like 'death' in Chinese", "alternative": "Give tea, art, or sweets instead", "severity": "major"},
            {"behavior": "Opening gifts immediately", "explanation": "Considered rude - shows impatience", "alternative": "Thank giver, open gift privately later", "severity": "moderate"},
            {"behavior": "Tipping", "explanation": "Can be seen as insulting or pitying", "alternative": "Tipping becoming more common in tourist areas, but not expected", "severity": "minor"},
        ]
    elif "japan" in country_lower or "japanese" in country_lower:
        result["taboos"] = [
            {"behavior": "Wearing shoes indoors", "explanation": "Homes and many restaurants require shoe removal", "alternative": "Look for shoe racks at entrance, wear clean socks", "severity": "major"},
            {"behavior": "Pointing with chopsticks", "explanation": "Considered very rude", "alternative": "Use hand to gesture, not chopsticks", "severity": "moderate"},
            {"behavior": "Tipping", "explanation": "Seen as insulting - good service is expected", "alternative": "Express gratitude verbally instead", "severity": "moderate"},
            {"behavior": "Blowing nose in public", "explanation": "Considered very rude and unhygienic", "alternative": "Excuse yourself to restroom", "severity": "moderate"},
        ]
    elif "middle east" in country_lower or any(c in country_lower for c in ["saudi", "uae", "dubai", "qatar"]):
        result["taboos"] = [
            {"behavior": "Showing soles of feet", "explanation": "Feet are considered unclean", "alternative": "Keep feet flat on ground when sitting", "severity": "major"},
            {"behavior": "Public displays of affection", "explanation": "Illegal or highly offensive in conservative areas", "alternative": "Avoid all physical contact with partner in public", "severity": "critical"},
            {"behavior": "Eating with left hand", "explanation": "Left hand considered unclean", "alternative": "Always use right hand for eating and handshakes", "severity": "major"},
            {"behavior": "Photography of people (especially women)", "explanation": "Privacy concerns and religious sensitivities", "alternative": "Always ask permission before photographing people", "severity": "major"},
        ]
    elif "india" in country_lower:
        result["taboos"] = [
            {"behavior": "Touching someone's head", "explanation": "Head is sacred in Hinduism", "alternative": "Avoid touching anyone's head, including children", "severity": "major"},
            {"behavior": "Public displays of affection", "explanation": "Conservative society, PDA is offensive", "alternative": "Refrain from kissing or extensive touching in public", "severity": "moderate"},
            {"behavior": "Pointing feet at people or religious objects", "explanation": "Feet are considered lowest/unclean", "alternative": "Keep feet flat on ground, never point at people", "severity": "moderate"},
            {"behavior": "Refusing tea or food offers", "explanation": "Hospitality is sacred - refusal can offend", "alternative": "Accept politely, even if just a small amount", "severity": "minor"},
        ]
    else:
        result["taboos"] = [
            {"behavior": "Inappropriate photography", "explanation": "Privacy and cultural sensitivities", "alternative": "Always ask permission before photographing people", "severity": "moderate"},
            {"behavior": "Disrespecting local customs", "explanation": "Cultural insensitivity", "alternative": "Research local customs and show respect", "severity": "moderate"},
        ]

    logger.info(f"Cultural taboos for {country}: {len(result['taboos'])} identified")
    return str(result)


@tool("Get etiquette guidelines")
def get_etiquette_guidelines(country: str) -> str:
    """
    Get etiquette guidelines for dining, social, and business contexts.

    Args:
        country: Country name (e.g., "France", "South Korea")

    Returns:
        JSON string with etiquette do's and don'ts

    Note: Etiquette varies by context and formality level.
    """
    country_lower = country.lower()

    result = {
        "country": country,
        "dining_etiquette": [],
        "social_etiquette": [],
    }

    if "france" in country_lower or "french" in country_lower:
        result["dining_etiquette"] = [
            {"category": "Dining", "rule": "Keep hands on table", "do": ["Keep wrists on table edge", "Use knife and fork properly"], "dont": ["Put hands in lap", "Eat with just fork", "Start eating before host"]},
            {"category": "Dining", "rule": "Bread etiquette", "do": ["Break bread with hands", "Place bread on table, not plate"], "dont": ["Cut bread with knife", "Use bread plate (doesn't exist)"]},
        ]
        result["social_etiquette"] = [
            {"category": "Greetings", "rule": "Cheek kisses", "do": ["Two kisses (some regions do more)", "Kiss on both cheeks"], "dont": ["Hug instead", "Kiss on lips"]},
            {"category": "Communication", "rule": "Formal address", "do": ["Use 'vous' with strangers/elders", "Use titles (Monsieur/Madame)"], "dont": ["Use 'tu' with people you just met", "Be overly casual"]},
        ]
    elif "japan" in country_lower:
        result["dining_etiquette"] = [
            {"category": "Dining", "rule": "Chopstick etiquette", "do": ["Rest on holder when not using", "Say 'itadakimasu' before eating"], "dont": ["Stick upright in rice", "Pass food chopstick to chopstick", "Point with chopsticks"]},
            {"category": "Dining", "rule": "Slurping noodles", "do": ["Slurp noodles - shows appreciation", "Finish your food"], "dont": ["Eat silently", "Leave food on plate (wasteful)"]},
        ]
        result["social_etiquette"] = [
            {"category": "Greetings", "rule": "Bowing", "do": ["Bow when greeting", "Deeper bow for elders/superiors"], "dont": ["Hug or kiss", "Pat on back"]},
            {"category": "Gift giving", "rule": "Gift presentation", "do": ["Use both hands to give/receive", "Wrap gifts nicely"], "dont": ["Open gifts immediately", "Give gifts in sets of 4 (unlucky)"]},
        ]
    elif "italy" in country_lower:
        result["dining_etiquette"] = [
            {"category": "Dining", "rule": "Coffee culture", "do": ["Drink cappuccino only before 11am", "Espresso after meals"], "dont": ["Order cappuccino after lunch/dinner", "Drink coffee to-go while walking"]},
            {"category": "Dining", "rule": "Meal pacing", "do": ["Take time with meals", "Accept multiple courses"], "dont": ["Rush through meal", "Ask for doggy bag"]},
        ]
        result["social_etiquette"] = [
            {"category": "Greetings", "rule": "Cheek kisses", "do": ["Two kisses on both cheeks", "Greet everyone in small group"], "dont": ["Kiss just once", "Skip people in greeting"]},
            {"category": "Communication", "rule": "Expressive communication", "do": ["Use hand gestures", "Be animated in conversation"], "dont": ["Be overly reserved", "Speak very quietly"]},
        ]
    else:
        result["dining_etiquette"] = [
            {"category": "Dining", "rule": "General table manners", "do": ["Wait for host to start", "Use utensils properly", "Thank the host"], "dont": ["Start eating first", "Talk with mouth full", "Use phone at table"]},
        ]
        result["social_etiquette"] = [
            {"category": "Social", "rule": "Be respectful", "do": ["Observe local customs", "Be polite and courteous"], "dont": ["Assume your customs apply", "Be loud or disruptive"]},
        ]

    logger.info(f"Etiquette guidelines for {country}: {len(result['dining_etiquette']) + len(result['social_etiquette'])} rules")
    return str(result)


@tool("Get essential phrases")
def get_essential_phrases(country: str) -> str:
    """
    Get essential phrases in the local language(s).

    Args:
        country: Country name (e.g., "Spain", "Japan")

    Returns:
        JSON string with essential phrases and pronunciation

    Note: Pronunciation guides are approximate. Consider language apps for audio.
    """
    country_lower = country.lower()

    phrases_map = {
        "japan": {
            "language": "Japanese",
            "phrases": [
                {"english": "Hello", "local": "こんにちは", "pronunciation": "Kon-nee-chee-wa", "context": "Daytime greeting"},
                {"english": "Thank you", "local": "ありがとうございます", "pronunciation": "Ah-ree-gah-toh goh-zah-ee-mas", "context": "Formal thanks"},
                {"english": "Excuse me / Sorry", "local": "すみません", "pronunciation": "Soo-mee-mah-sen", "context": "Getting attention or apologizing"},
                {"english": "Yes / No", "local": "はい / いいえ", "pronunciation": "High / Ee-eh", "context": "Basic responses"},
                {"english": "How much?", "local": "いくらですか", "pronunciation": "Ee-koo-rah des-kah", "context": "Asking prices"},
            ],
        },
        "france": {
            "language": "French",
            "phrases": [
                {"english": "Hello", "local": "Bonjour", "pronunciation": "Bon-zhoor", "context": "General greeting"},
                {"english": "Thank you", "local": "Merci", "pronunciation": "Mare-see", "context": "Thanks"},
                {"english": "Excuse me", "local": "Excusez-moi", "pronunciation": "Ex-koo-zay mwah", "context": "Getting attention"},
                {"english": "Do you speak English?", "local": "Parlez-vous anglais?", "pronunciation": "Par-lay voo on-glay", "context": "Language barrier"},
                {"english": "Please", "local": "S'il vous plaît", "pronunciation": "Seal voo play", "context": "Polite requests"},
            ],
        },
        "spain": {
            "language": "Spanish",
            "phrases": [
                {"english": "Hello", "local": "Hola", "pronunciation": "Oh-lah", "context": "General greeting"},
                {"english": "Thank you", "local": "Gracias", "pronunciation": "Grah-see-ahs", "context": "Thanks"},
                {"english": "Please", "local": "Por favor", "pronunciation": "Por fah-vor", "context": "Polite requests"},
                {"english": "Excuse me", "local": "Perdón", "pronunciation": "Pair-dohn", "context": "Getting attention or apologizing"},
                {"english": "How much?", "local": "¿Cuánto cuesta?", "pronunciation": "Kwan-toh kwes-tah", "context": "Asking prices"},
            ],
        },
    }

    result = {
        "country": country,
        "official_languages": ["English"],  # Default
        "phrases": [
            {"english": "Hello", "local": "Hello", "pronunciation": None, "context": "General greeting"},
            {"english": "Thank you", "local": "Thank you", "pronunciation": None, "context": "Thanks"},
            {"english": "Please", "local": "Please", "pronunciation": None, "context": "Requests"},
        ],
    }

    # Check for exact matches first
    for key, data in phrases_map.items():
        if key in country_lower:
            result["official_languages"] = [data["language"]]
            result["phrases"] = data["phrases"]
            logger.info(f"Essential phrases for {country}: {data['language']}")
            return str(result)

    logger.info(f"Using default English phrases for {country}")
    return str(result)
