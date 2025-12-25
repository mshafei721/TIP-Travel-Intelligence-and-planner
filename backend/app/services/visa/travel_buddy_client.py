"""
Travel Buddy AI API Client

Provides visa requirement checking using the Travel Buddy AI Visa API via RapidAPI.
Supports both sync and async operations.

API Documentation: https://travel-buddy.ai/api/
RapidAPI: https://rapidapi.com/TravelBuddyAI/api/visa-requirement
"""

from dataclasses import asdict, dataclass

import httpx

from app.core.config import settings


@dataclass
class VisaCheckResult:
    """
    Result from Travel Buddy AI visa check

    Attributes:
        passport_code: ISO Alpha-2 passport country code (e.g., "US", "GB")
        destination_code: ISO Alpha-2 destination country code (e.g., "FR", "JP")
        visa_required: Whether a visa is required
        visa_type: Type of visa requirement (visa-free, visa_required, evisa, etc.)
        max_stay_days: Maximum allowed stay in days (None if not applicable)
        passport_validity_months: Required passport validity in months
        evisa_url: Official eVisa application URL (if applicable)
        embassy_url: Embassy website URL
        currency: Destination country currency code
        timezone: Destination country timezone
    """

    passport_code: str
    destination_code: str
    visa_required: bool
    visa_type: str
    max_stay_days: int | None = None
    passport_validity_months: int | None = None
    evisa_url: str | None = None
    embassy_url: str | None = None
    currency: str | None = None
    timezone: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class TravelBuddyClient:
    """
    Travel Buddy AI API client for visa requirements

    Uses RapidAPI to access Travel Buddy AI Visa API.
    Supports both synchronous and asynchronous requests.

    Example:
        >>> client = TravelBuddyClient(api_key="your-rapidapi-key")
        >>> result = client.check_visa(passport="US", destination="FR")
        >>> print(f"Visa required: {result.visa_required}")
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize Travel Buddy AI client

        Args:
            api_key: RapidAPI key (defaults to settings.RAPIDAPI_KEY)
        """
        self.api_key = api_key or settings.RAPIDAPI_KEY
        self.base_url = "https://visa-requirement.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "visa-requirement.p.rapidapi.com",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _validate_country_code(self, code: str, code_type: str) -> None:
        """
        Validate ISO Alpha-2 country code

        Args:
            code: Country code to validate
            code_type: Type of code ("passport" or "destination")

        Raises:
            ValueError: If code is invalid
        """
        if not code or len(code) != 2 or not code.isalpha():
            raise ValueError(f"Invalid {code_type} code: {code}. Must be ISO Alpha-2 (2 letters)")

    def check_visa(self, passport: str, destination: str) -> VisaCheckResult:
        """
        Check visa requirements (synchronous)

        Args:
            passport: ISO Alpha-2 passport country code (e.g., "US")
            destination: ISO Alpha-2 destination country code (e.g., "FR")

        Returns:
            VisaCheckResult with visa requirements

        Raises:
            ValueError: If country codes are invalid
            httpx.HTTPError: If API request fails
        """
        # Validate inputs
        self._validate_country_code(passport, "passport")
        self._validate_country_code(destination, "destination")

        # Make API request
        url = f"{self.base_url}/v2/visa/check"
        data = {"passport": passport.upper(), "destination": destination.upper()}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            return self._parse_response(response.json(), passport, destination)

    async def check_visa_async(self, passport: str, destination: str) -> VisaCheckResult:
        """
        Check visa requirements (asynchronous)

        Args:
            passport: ISO Alpha-2 passport country code (e.g., "US")
            destination: ISO Alpha-2 destination country code (e.g., "FR")

        Returns:
            VisaCheckResult with visa requirements

        Raises:
            ValueError: If country codes are invalid
            httpx.HTTPError: If API request fails
        """
        # Validate inputs
        self._validate_country_code(passport, "passport")
        self._validate_country_code(destination, "destination")

        # Make async API request
        url = f"{self.base_url}/v2/visa/check"
        data = {"passport": passport.upper(), "destination": destination.upper()}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            return self._parse_response(response.json(), passport, destination)

    def _parse_response(self, data: dict, passport: str, destination: str) -> VisaCheckResult:
        """
        Parse Travel Buddy AI API response

        Args:
            data: API response JSON
            passport: Passport country code
            destination: Destination country code

        Returns:
            VisaCheckResult with parsed data
        """
        # Extract primary visa rule
        primary_rule = data.get("primary", {})
        category = primary_rule.get("category", "")
        duration = primary_rule.get("duration", None)

        # Determine if visa is required
        visa_free_categories = [
            "visa-free",
            "freedom_of_movement",
            "visa_free_days",
            "visa_free_months",
        ]
        visa_required = category not in visa_free_categories

        # Parse duration (convert to days if needed)
        max_stay_days = None
        if duration:
            if isinstance(duration, int):
                max_stay_days = duration
            elif isinstance(duration, str):
                # Parse "90 days", "6 months", etc.
                duration_lower = duration.lower()
                if "day" in duration_lower:
                    max_stay_days = int(duration_lower.split()[0])
                elif "month" in duration_lower:
                    months = int(duration_lower.split()[0])
                    max_stay_days = months * 30  # Approximate

        # Extract passport validity
        passport_validity = primary_rule.get("passport_validity", {})
        validity_months = passport_validity.get("months")

        # Extract URLs
        evisa_url = None
        if "evisa" in category.lower() or "eta" in category.lower():
            # Look for official eVisa URL in response
            evisa_info = data.get("evisa", {})
            evisa_url = evisa_info.get("url")

        embassy_data = data.get("embassy", {})
        embassy_url = embassy_data.get("url")

        # Extract country info
        destination_info = data.get("destination", {})
        currency = destination_info.get("currency")
        timezone = destination_info.get("timezone")

        return VisaCheckResult(
            passport_code=passport.upper(),
            destination_code=destination.upper(),
            visa_required=visa_required,
            visa_type=category,
            max_stay_days=max_stay_days,
            passport_validity_months=validity_months,
            evisa_url=evisa_url,
            embassy_url=embassy_url,
            currency=currency,
            timezone=timezone,
        )
