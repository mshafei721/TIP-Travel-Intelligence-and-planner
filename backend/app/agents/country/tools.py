"""
Country Agent CrewAI Tools

Provides tools for accessing country information, emergency services,
safety data, and travel advisories.
"""

from crewai.tools import tool
from app.services.country.rest_countries_client import RestCountriesClient, CountryInfo


@tool("Get Country Information")
def get_country_info(country_name: str) -> dict:
    """
    Get comprehensive country information from REST Countries API.

    Args:
        country_name: Name of the country (e.g., "France", "Japan")

    Returns:
        Dictionary with country data including name, capital, population,
        languages, time zones, currencies, and more.
    """
    try:
        client = RestCountriesClient()
        country = client.get_country_by_name_sync(country_name)

        return {
            "success": True,
            "country_name": country.name_common,
            "official_name": country.name_official,
            "country_code": country.cca2,
            "capital": country.capital,
            "region": country.region,
            "subregion": country.subregion,
            "population": country.population,
            "area_km2": country.area,
            "languages": country.languages,
            "timezones": country.timezones,
            "coordinates": {
                "latitude": country.latlng[0] if country.latlng else None,
                "longitude": country.latlng[1] if country.latlng else None,
            },
            "borders": country.borders,
            "currencies": country.currencies,
            "driving_side": country.car_side,
            "idd_root": country.idd_root,
            "idd_suffixes": country.idd_suffixes,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool("Get Emergency Services")
def get_emergency_services(country_code: str) -> dict:
    """
    Get emergency service contact numbers for a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., "FR", "US", "JP")

    Returns:
        Dictionary with emergency contact numbers (police, ambulance, fire, etc.)
    """
    # Emergency numbers database (simplified version)
    # In production, this should query a comprehensive database or API
    emergency_numbers = {
        "FR": [  # France
            {"service": "Emergency (All Services)", "number": "112", "notes": "EU standard emergency number"},
            {"service": "Police", "number": "17", "notes": "National police"},
            {"service": "Ambulance (SAMU)", "number": "15", "notes": "Medical emergency"},
            {"service": "Fire", "number": "18", "notes": "Fire brigade"},
        ],
        "US": [  # United States
            {"service": "Emergency (All Services)", "number": "911", "notes": "Police, Fire, Ambulance"},
        ],
        "GB": [  # United Kingdom
            {"service": "Emergency (All Services)", "number": "112", "notes": "EU standard (still works post-Brexit)"},
            {"service": "Emergency (All Services)", "number": "999", "notes": "UK traditional emergency number"},
        ],
        "JP": [  # Japan
            {"service": "Police", "number": "110", "notes": "Police emergency"},
            {"service": "Ambulance/Fire", "number": "119", "notes": "Medical emergency and fire"},
        ],
        "DE": [  # Germany
            {"service": "Emergency (All Services)", "number": "112", "notes": "EU standard emergency number"},
            {"service": "Police", "number": "110", "notes": "Police emergency"},
        ],
        "IT": [  # Italy
            {"service": "Emergency (All Services)", "number": "112", "notes": "EU standard emergency number"},
            {"service": "Police (Carabinieri)", "number": "112", "notes": "Military police"},
            {"service": "Police (State Police)", "number": "113", "notes": "State police"},
            {"service": "Ambulance", "number": "118", "notes": "Medical emergency"},
            {"service": "Fire", "number": "115", "notes": "Fire brigade"},
        ],
        "ES": [  # Spain
            {"service": "Emergency (All Services)", "number": "112", "notes": "EU standard emergency number"},
        ],
        "CA": [  # Canada
            {"service": "Emergency (All Services)", "number": "911", "notes": "Police, Fire, Ambulance"},
        ],
        "AU": [  # Australia
            {"service": "Emergency (All Services)", "number": "000", "notes": "Police, Fire, Ambulance"},
            {"service": "Emergency (Mobile)", "number": "112", "notes": "Works on mobile phones"},
        ],
        "NZ": [  # New Zealand
            {"service": "Emergency (All Services)", "number": "111", "notes": "Police, Fire, Ambulance"},
        ],
        "CN": [  # China
            {"service": "Police", "number": "110", "notes": "Police emergency"},
            {"service": "Ambulance", "number": "120", "notes": "Medical emergency"},
            {"service": "Fire", "number": "119", "notes": "Fire brigade"},
        ],
        "IN": [  # India
            {"service": "Police", "number": "100", "notes": "Police emergency"},
            {"service": "Ambulance", "number": "102", "notes": "Medical emergency"},
            {"service": "Fire", "number": "101", "notes": "Fire brigade"},
        ],
        "BR": [  # Brazil
            {"service": "Police", "number": "190", "notes": "Military police"},
            {"service": "Ambulance", "number": "192", "notes": "Medical emergency"},
            {"service": "Fire", "number": "193", "notes": "Fire brigade"},
        ],
    }

    code = country_code.upper()

    if code in emergency_numbers:
        return {
            "success": True,
            "country_code": code,
            "emergency_services": emergency_numbers[code],
        }
    else:
        # Fallback for countries not in database
        return {
            "success": True,
            "country_code": code,
            "emergency_services": [
                {
                    "service": "Emergency (International)",
                    "number": "112",
                    "notes": "International emergency number (may work in many countries)",
                }
            ],
            "warning": "Specific emergency numbers not available. Verify locally upon arrival.",
        }


@tool("Get Power Outlet Information")
def get_power_outlet_info(country_code: str) -> dict:
    """
    Get power outlet and voltage information for a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., "FR", "US", "JP")

    Returns:
        Dictionary with plug types, voltage, and frequency information
    """
    # Power outlet database (simplified version)
    # Source: https://www.worldstandards.eu/electricity/plugs-and-sockets/
    power_info = {
        "FR": {"plug_types": ["C", "E"], "voltage": "230V", "frequency": "50Hz"},
        "US": {"plug_types": ["A", "B"], "voltage": "120V", "frequency": "60Hz"},
        "GB": {"plug_types": ["G"], "voltage": "230V", "frequency": "50Hz"},
        "JP": {"plug_types": ["A", "B"], "voltage": "100V", "frequency": "50/60Hz"},
        "DE": {"plug_types": ["C", "F"], "voltage": "230V", "frequency": "50Hz"},
        "IT": {"plug_types": ["C", "F", "L"], "voltage": "230V", "frequency": "50Hz"},
        "ES": {"plug_types": ["C", "F"], "voltage": "230V", "frequency": "50Hz"},
        "CA": {"plug_types": ["A", "B"], "voltage": "120V", "frequency": "60Hz"},
        "AU": {"plug_types": ["I"], "voltage": "230V", "frequency": "50Hz"},
        "NZ": {"plug_types": ["I"], "voltage": "230V", "frequency": "50Hz"},
        "CN": {"plug_types": ["A", "C", "I"], "voltage": "220V", "frequency": "50Hz"},
        "IN": {"plug_types": ["C", "D", "M"], "voltage": "230V", "frequency": "50Hz"},
        "BR": {"plug_types": ["C", "N"], "voltage": "127/220V", "frequency": "60Hz"},
    }

    code = country_code.upper()

    if code in power_info:
        return {"success": True, "country_code": code, **power_info[code]}
    else:
        return {
            "success": False,
            "country_code": code,
            "error": "Power outlet information not available. Check locally upon arrival.",
        }


@tool("Get Travel Safety Rating")
def get_travel_safety_rating(country_name: str) -> dict:
    """
    Get travel safety rating and advisories for a country.

    Args:
        country_name: Name of the country

    Returns:
        Dictionary with safety rating (0-5) and current travel advisories
    """
    # Safety rating database (simplified version)
    # In production, integrate with official travel advisory APIs:
    # - US State Department Travel Advisories
    # - UK Foreign Office Travel Advice
    # - Canadian Travel Advisories
    # - Australian DFAT Smartraveller

    safety_ratings = {
        "France": {
            "rating": 4.5,
            "level": "Exercise normal precautions",
            "advisories": [],
            "last_updated": "2025-12-01",
        },
        "United States": {
            "rating": 4.3,
            "level": "Exercise normal precautions",
            "advisories": [],
            "last_updated": "2025-12-01",
        },
        "Japan": {
            "rating": 4.8,
            "level": "Exercise normal precautions",
            "advisories": [],
            "last_updated": "2025-12-01",
        },
        "United Kingdom": {
            "rating": 4.6,
            "level": "Exercise normal precautions",
            "advisories": [],
            "last_updated": "2025-12-01",
        },
        "Germany": {
            "rating": 4.7,
            "level": "Exercise normal precautions",
            "advisories": [],
            "last_updated": "2025-12-01",
        },
        "Italy": {
            "rating": 4.4,
            "level": "Exercise normal precautions",
            "advisories": [
                {
                    "title": "Pickpocketing in Tourist Areas",
                    "level": "Minor",
                    "summary": "Be aware of pickpockets in crowded tourist areas and on public transport.",
                }
            ],
            "last_updated": "2025-12-01",
        },
        "Spain": {
            "rating": 4.5,
            "level": "Exercise normal precautions",
            "advisories": [],
            "last_updated": "2025-12-01",
        },
        "Canada": {
            "rating": 4.8,
            "level": "Exercise normal precautions",
            "advisories": [],
            "last_updated": "2025-12-01",
        },
        "Australia": {
            "rating": 4.7,
            "level": "Exercise normal precautions",
            "advisories": [],
            "last_updated": "2025-12-01",
        },
    }

    if country_name in safety_ratings:
        return {"success": True, "country": country_name, **safety_ratings[country_name]}
    else:
        # Default safety rating for countries not in database
        return {
            "success": True,
            "country": country_name,
            "rating": 3.5,
            "level": "Exercise increased caution",
            "advisories": [],
            "last_updated": "2025-12-01",
            "warning": "Official safety rating not available. Check government travel advisories.",
        }


@tool("Get Notable Country Facts")
def get_notable_facts(country_name: str) -> dict:
    """
    Get interesting and notable facts about a country.

    Args:
        country_name: Name of the country

    Returns:
        Dictionary with notable facts and travel tips
    """
    # Notable facts database (simplified version)
    facts = {
        "France": {
            "facts": [
                "Most visited country in the world with over 89 million tourists annually",
                "Home to 45 UNESCO World Heritage Sites",
                "French is the official language, but English is widely spoken in tourist areas",
                "The metric system was invented in France",
                "France has 12 time zones (including overseas territories)",
            ],
            "best_time_to_visit": "April to June or September to November (spring and fall)",
        },
        "Japan": {
            "facts": [
                "Consists of 6,852 islands",
                "Tokyo is the world's largest metropolitan area",
                "Punctuality is extremely important in Japanese culture",
                "Tipping is not customary and can be considered rude",
                "Japan has one of the world's highest life expectancies",
            ],
            "best_time_to_visit": "March to May (cherry blossoms) or September to November (fall colors)",
        },
        "United States": {
            "facts": [
                "Third largest country by area and population",
                "Home to the world's largest economy",
                "Tipping is expected (15-20% in restaurants)",
                "Sales tax is added at checkout (not included in displayed prices)",
                "Diverse climates across the country",
            ],
            "best_time_to_visit": "Varies by region - generally April to June or September to November",
        },
    }

    if country_name in facts:
        return {"success": True, "country": country_name, **facts[country_name]}
    else:
        return {
            "success": True,
            "country": country_name,
            "facts": [
                "Research local customs and etiquette before visiting",
                "Learn a few phrases in the local language",
                "Check visa requirements well in advance",
            ],
            "best_time_to_visit": "Research seasonal weather and tourist patterns",
        }
