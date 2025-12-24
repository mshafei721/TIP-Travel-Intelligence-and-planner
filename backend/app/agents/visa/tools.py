"""
Visa Agent CrewAI Tools

Tools that the Visa Agent can use to gather visa information.
Each tool is decorated with @tool for CrewAI integration.
"""

from crewai.tools import tool
from app.services.visa.travel_buddy_client import TravelBuddyClient, VisaCheckResult
from app.core.config import settings


# Initialize Travel Buddy AI client
_visa_client = TravelBuddyClient(api_key=settings.RAPIDAPI_KEY)


@tool("Visa Requirements Checker")
def check_visa_requirements(passport_country: str, destination_country: str) -> dict:
    """
    Check visa requirements for a specific passport and destination country.

    This tool queries the Travel Buddy AI API for official visa requirements.
    Use this as the primary source for visa information.

    Args:
        passport_country: ISO Alpha-2 code of passport country (e.g., "US", "GB", "IN")
        destination_country: ISO Alpha-2 code of destination country (e.g., "FR", "JP", "TH")

    Returns:
        dict: Visa requirements including:
            - visa_required: bool
            - visa_type: str (visa-free, tourist, business, e-visa, etc.)
            - max_stay_days: int or None
            - passport_validity_months: int or None
            - evisa_url: str or None (official eVisa application URL)
            - embassy_url: str or None
            - currency: str (destination currency code)
            - timezone: str

    Example:
        >>> result = check_visa_requirements("US", "FR")
        >>> print(result["visa_required"])  # False (Schengen visa-free)
    """
    try:
        result = _visa_client.check_visa(
            passport=passport_country.upper(),
            destination=destination_country.upper(),
        )
        return result.to_dict()
    except Exception as e:
        return {
            "error": str(e),
            "visa_required": None,
            "confidence": 0.0,
        }


@tool("Embassy Information Lookup")
def get_embassy_info(destination_country: str) -> dict:
    """
    Get embassy and consulate information for a destination country.

    Use this tool to find official embassy websites and contact information.

    Args:
        destination_country: ISO Alpha-2 code (e.g., "FR", "JP")

    Returns:
        dict: Embassy information including URL and contact details

    Note:
        This is extracted from the visa check result.
        For more detailed embassy info, recommend the traveler visit official sources.
    """
    try:
        # We can enhance this later with a dedicated embassy API
        # For now, we'll return the embassy URL from visa check
        result = _visa_client.check_visa(
            passport="US",  # Dummy passport to get destination info
            destination=destination_country.upper(),
        )
        return {
            "embassy_url": result.embassy_url,
            "destination_country": destination_country.upper(),
        }
    except Exception as e:
        return {"error": str(e), "embassy_url": None}


@tool("Visa Document Checklist Generator")
def generate_document_checklist(visa_type: str, trip_purpose: str) -> list:
    """
    Generate a checklist of required documents for visa application.

    Args:
        visa_type: Type of visa (tourist, business, e-visa, etc.)
        trip_purpose: Purpose of trip (tourism, business, transit)

    Returns:
        list: List of required documents

    Example:
        >>> docs = generate_document_checklist("tourist", "tourism")
        >>> print(docs)
        ['Valid passport', 'Passport photo', 'Application form', ...]
    """
    base_documents = [
        "Valid passport (with at least 6 months validity)",
        "Recent passport-sized photo (2x2 inches)",
        "Completed visa application form",
        "Proof of travel arrangements (flight bookings)",
        "Proof of accommodation (hotel reservations)",
    ]

    if visa_type in ["tourist", "visa_required"]:
        base_documents.extend(
            [
                "Travel itinerary",
                "Proof of sufficient funds (bank statements)",
                "Travel insurance certificate",
            ]
        )

    if trip_purpose == "business" or visa_type == "business":
        base_documents.extend(
            [
                "Business invitation letter",
                "Company registration documents",
                "Letter from employer",
            ]
        )

    if visa_type in ["evisa", "e-visa"]:
        base_documents.append("Valid email address for eVisa delivery")

    return base_documents


@tool("Visa Processing Time Estimator")
def estimate_processing_time(visa_type: str, application_method: str) -> dict:
    """
    Estimate visa processing time based on visa type and application method.

    Args:
        visa_type: Type of visa
        application_method: How visa is applied for (online, embassy, on-arrival)

    Returns:
        dict: Processing time estimate with min/max days
    """
    # Standard processing times (these are estimates)
    processing_times = {
        "evisa": {"min_days": 1, "max_days": 3, "description": "1-3 business days"},
        "e-visa": {"min_days": 1, "max_days": 3, "description": "1-3 business days"},
        "online": {"min_days": 3, "max_days": 7, "description": "3-7 business days"},
        "embassy": {"min_days": 5, "max_days": 15, "description": "5-15 business days"},
        "on-arrival": {"min_days": 0, "max_days": 1, "description": "Same day (at airport)"},
        "visa-free": {"min_days": 0, "max_days": 0, "description": "No processing needed"},
    }

    method = visa_type.lower() if visa_type else application_method.lower()
    return processing_times.get(method, {"min_days": 7, "max_days": 21, "description": "7-21 business days"})


@tool("Travel Advisory Checker")
def check_travel_advisories(destination_country: str) -> dict:
    """
    Check for travel advisories and warnings for a destination country.

    Args:
        destination_country: ISO Alpha-2 code

    Returns:
        dict: Travel advisory information

    Note:
        This is a placeholder. In production, integrate with State Department or FCO APIs.
    """
    # Placeholder implementation
    # TODO: Integrate with travel.state.gov API or similar
    return {
        "destination": destination_country.upper(),
        "advisory_level": "Check official sources",
        "note": "Always verify with your government's travel advisory service",
        "sources": [
            "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html/",
            "https://www.gov.uk/foreign-travel-advice",
        ],
    }
