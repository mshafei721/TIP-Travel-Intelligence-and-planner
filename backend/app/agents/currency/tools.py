"""
Currency Agent CrewAI Tools

Tools for currency research, exchange rates, and financial intelligence.
"""

import logging
from crewai.tools import tool
from app.services.currency import CurrencyExchangeClient

logger = logging.getLogger(__name__)

# Initialize API client
currency_client = CurrencyExchangeClient()


@tool("Get exchange rates")
def get_exchange_rates(
    base_currency: str,
    target_currency: str
) -> str:
    """
    Get current exchange rate between two currencies.

    Args:
        base_currency: Base currency code (e.g., "USD")
        target_currency: Target currency code (e.g., "JPY")

    Returns:
        JSON string with exchange rate information
    """
    try:
        rate_data = currency_client.get_exchange_rate(
            base_currency=base_currency,
            target_currency=target_currency
        )

        result = {
            "base_currency": rate_data.base_currency,
            "target_currency": rate_data.target_currency,
            "exchange_rate": rate_data.rate,
            "date": rate_data.date.isoformat(),
            "conversion_example": f"1 {rate_data.base_currency} = {rate_data.rate} {rate_data.target_currency}"
        }

        logger.info(f"Exchange rate: 1 {rate_data.base_currency} = {rate_data.rate} {rate_data.target_currency}")
        return str(result)

    except Exception as e:
        logger.error(f"Error getting exchange rate: {e}")
        return f"Error: {str(e)}"


@tool("Get currency information")
def get_currency_info(country_code: str) -> str:
    """
    Get local currency information for a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g., "JP" for Japan)

    Returns:
        JSON string with currency details

    Note: This tool provides currency mapping for common countries.
    For real-time exchange rates, use get_exchange_rates tool.
    """
    # Currency mapping for common countries
    # This is a static mapping; for production, consider integrating REST Countries API
    currency_map = {
        # Major currencies
        "US": {"code": "USD", "name": "United States Dollar", "symbol": "$"},
        "GB": {"code": "GBP", "name": "British Pound Sterling", "symbol": "£"},
        "JP": {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
        "CN": {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
        "IN": {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
        "AU": {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
        "CA": {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
        "CH": {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF"},
        "KR": {"code": "KRW", "name": "South Korean Won", "symbol": "₩"},
        "SG": {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$"},
        "HK": {"code": "HKD", "name": "Hong Kong Dollar", "symbol": "HK$"},
        "NZ": {"code": "NZD", "name": "New Zealand Dollar", "symbol": "NZ$"},
        "TH": {"code": "THB", "name": "Thai Baht", "symbol": "฿"},
        "MY": {"code": "MYR", "name": "Malaysian Ringgit", "symbol": "RM"},
        "ID": {"code": "IDR", "name": "Indonesian Rupiah", "symbol": "Rp"},
        "PH": {"code": "PHP", "name": "Philippine Peso", "symbol": "₱"},
        "VN": {"code": "VND", "name": "Vietnamese Dong", "symbol": "₫"},
        "BR": {"code": "BRL", "name": "Brazilian Real", "symbol": "R$"},
        "MX": {"code": "MXN", "name": "Mexican Peso", "symbol": "Mex$"},
        "ZA": {"code": "ZAR", "name": "South African Rand", "symbol": "R"},
        "RU": {"code": "RUB", "name": "Russian Ruble", "symbol": "₽"},
        "TR": {"code": "TRY", "name": "Turkish Lira", "symbol": "₺"},
        "AE": {"code": "AED", "name": "UAE Dirham", "symbol": "د.إ"},
        "SA": {"code": "SAR", "name": "Saudi Riyal", "symbol": "﷼"},
        "EG": {"code": "EGP", "name": "Egyptian Pound", "symbol": "E£"},
        "IL": {"code": "ILS", "name": "Israeli New Shekel", "symbol": "₪"},
        "AR": {"code": "ARS", "name": "Argentine Peso", "symbol": "$"},
        "CL": {"code": "CLP", "name": "Chilean Peso", "symbol": "$"},
        "CO": {"code": "COP", "name": "Colombian Peso", "symbol": "$"},
        "PE": {"code": "PEN", "name": "Peruvian Sol", "symbol": "S/"},
        "NO": {"code": "NOK", "name": "Norwegian Krone", "symbol": "kr"},
        "SE": {"code": "SEK", "name": "Swedish Krona", "symbol": "kr"},
        "DK": {"code": "DKK", "name": "Danish Krone", "symbol": "kr"},
        "PL": {"code": "PLN", "name": "Polish Zloty", "symbol": "zł"},
        "CZ": {"code": "CZK", "name": "Czech Koruna", "symbol": "Kč"},
        "HU": {"code": "HUF", "name": "Hungarian Forint", "symbol": "Ft"},
        # Eurozone countries
        "FR": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "DE": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "IT": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "ES": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "PT": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "NL": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "BE": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "AT": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "GR": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "IE": {"code": "EUR", "name": "Euro", "symbol": "€"},
        "FI": {"code": "EUR", "name": "Euro", "symbol": "€"},
    }

    country_code_upper = country_code.upper()

    if country_code_upper in currency_map:
        currency = currency_map[country_code_upper]
        logger.info(f"Currency for {country_code}: {currency['code']}")
        return str(currency)
    else:
        return f"Currency information not available for country code: {country_code}"


@tool("Get ATM and payment information")
def get_atm_payment_info(country: str) -> str:
    """
    Get ATM availability, fees, and payment method information for a country.

    Args:
        country: Country name (e.g., "Japan", "France")

    Returns:
        JSON string with ATM and payment details

    Note: This provides general guidance. Specific fees vary by bank.
    """
    # General ATM and payment patterns by development level
    # In production, this could be enhanced with real data sources
    country_lower = country.lower()

    # Categorize countries
    widespread_atm = [
        "japan", "south korea", "singapore", "hong kong", "australia",
        "united states", "canada", "united kingdom", "france", "germany",
        "italy", "spain", "netherlands", "switzerland", "sweden", "norway", "denmark"
    ]

    common_atm = [
        "thailand", "malaysia", "philippines", "vietnam", "indonesia",
        "china", "india", "mexico", "brazil", "argentina", "chile",
        "turkey", "greece", "portugal", "poland", "czech republic"
    ]

    if any(c in country_lower for c in widespread_atm):
        return str({
            "atm_availability": "widespread",
            "atm_fees": "Typically $2-5 per withdrawal, plus foreign transaction fees from your bank",
            "credit_card_acceptance": "widespread",
            "recommended_payment_methods": ["Credit/Debit cards", "ATM withdrawals", "Mobile payments"],
            "notes": "Major credit cards widely accepted. Contactless payments common."
        })
    elif any(c in country_lower for c in common_atm):
        return str({
            "atm_availability": "common",
            "atm_fees": "Variable, typically $2-7 per withdrawal plus foreign transaction fees",
            "credit_card_acceptance": "common",
            "recommended_payment_methods": ["Cash (local currency)", "ATM withdrawals", "Credit cards at major establishments"],
            "notes": "Cash still preferred in many places. Keep mix of cash and cards."
        })
    else:
        return str({
            "atm_availability": "limited",
            "atm_fees": "Variable, can be higher in tourist areas",
            "credit_card_acceptance": "limited",
            "recommended_payment_methods": ["Cash (local currency)", "Exchange currency before arrival"],
            "notes": "Cash preferred. ATMs may be limited outside major cities."
        })


@tool("Get tipping customs")
def get_tipping_customs(country: str) -> str:
    """
    Get tipping culture and expectations for a country.

    Args:
        country: Country name (e.g., "Japan", "United States")

    Returns:
        JSON string with tipping information
    """
    country_lower = country.lower()

    # Tipping culture database
    tipping_data = {
        "japan": {
            "culture": "Tipping is not customary and can be considered rude",
            "percentage": 0,
            "notes": "Exceptional service is built into the culture. Tipping may cause confusion or offense."
        },
        "united states": {
            "culture": "Tipping is expected and major source of service worker income",
            "percentage": 15-20,
            "notes": "15-20% at restaurants, $1-2 per drink at bars, 15-20% for taxis, $2-5 per bag for hotel staff"
        },
        "canada": {
            "culture": "Tipping is customary and expected",
            "percentage": 15-20,
            "notes": "Similar to US. 15-20% at restaurants, $1-2 per drink, 10-15% for taxis"
        },
        "united kingdom": {
            "culture": "Tipping is appreciated but not always expected",
            "percentage": 10-15,
            "notes": "10-15% at restaurants if service charge not included. Round up taxi fares. £1-2 per bag for porters."
        },
        "france": {
            "culture": "Service charge usually included, small tip appreciated",
            "percentage": 5-10,
            "notes": "Service charge (15%) typically included. Round up or add 5-10% for excellent service."
        },
        "germany": {
            "culture": "Small tips appreciated, round up bills",
            "percentage": 5-10,
            "notes": "Round up bills or add 5-10%. Say 'stimmt so' (keep the change) when paying."
        },
        "australia": {
            "culture": "Tipping not obligatory but becoming more common",
            "percentage": 10,
            "notes": "10% at restaurants for good service. Not required for cafes or bars."
        },
        "china": {
            "culture": "Tipping not expected in most situations",
            "percentage": 0,
            "notes": "Generally not expected. May be accepted at high-end hotels and restaurants in major cities."
        },
        "thailand": {
            "culture": "Not required but appreciated for good service",
            "percentage": 10,
            "notes": "10% at restaurants if service charge not included. 20-50 baht for hotel staff. Not needed for street food or taxis."
        },
        "mexico": {
            "culture": "Tipping is customary and expected",
            "percentage": 10-15,
            "notes": "10-15% at restaurants. $1-2 USD per day for housekeeping. 10-20 pesos for parking attendants."
        }
    }

    # Find matching country
    for key, data in tipping_data.items():
        if key in country_lower:
            logger.info(f"Tipping info for {country}: {data['culture']}")
            return str(data)

    # Default for unknown countries
    return str({
        "culture": "Tipping customs vary. Research specific to this destination recommended.",
        "percentage": None,
        "notes": "Check local travel guides or ask locals about tipping expectations."
    })


@tool("Get cost of living estimates")
def get_cost_estimates(country: str, city: str = None) -> str:
    """
    Get cost of living estimates for common items and services.

    Args:
        country: Country name (e.g., "Japan")
        city: Optional city name for more specific estimates (e.g., "Tokyo")

    Returns:
        JSON string with cost estimates and overall cost level
    """
    country_lower = country.lower()
    city_lower = city.lower() if city else ""

    # Cost level categories
    very_high_cost = ["switzerland", "norway", "iceland", "singapore", "hong kong"]
    high_cost = ["japan", "australia", "united kingdom", "france", "germany", "sweden", "denmark"]
    moderate_cost = ["spain", "italy", "south korea", "canada", "united states"]
    low_cost = ["thailand", "vietnam", "indonesia", "philippines", "mexico", "india"]
    very_low_cost = ["cambodia", "laos", "nepal", "bolivia"]

    # Determine cost level
    if any(c in country_lower for c in very_high_cost):
        cost_level = "very-high"
        budget, mid_range, luxury = 80, 150, 300
    elif any(c in country_lower for c in high_cost):
        cost_level = "high"
        budget, mid_range, luxury = 60, 120, 250
    elif any(c in country_lower for c in moderate_cost):
        cost_level = "moderate"
        budget, mid_range, luxury = 50, 100, 200
    elif any(c in country_lower for c in low_cost):
        cost_level = "low"
        budget, mid_range, luxury = 25, 60, 150
    else:  # very_low_cost
        cost_level = "very-low"
        budget, mid_range, luxury = 15, 40, 100

    result = {
        "cost_level": cost_level,
        "daily_budget": {
            "budget": budget,
            "mid_range": mid_range,
            "luxury": luxury
        },
        "notes": f"Estimated daily budgets in USD for {country}. Actual costs vary by city and season."
    }

    logger.info(f"Cost level for {country}: {cost_level}")
    return str(result)
