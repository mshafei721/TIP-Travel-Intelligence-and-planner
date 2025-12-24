"""
Tests for Travel Buddy AI client

Following TDD (RED-GREEN-REFACTOR):
1. RED: Write failing tests
2. GREEN: Write minimal code to pass
3. REFACTOR: Improve code quality
"""

import pytest
from app.services.visa.travel_buddy_client import TravelBuddyClient, VisaCheckResult


class TestTravelBuddyClient:
    """Test suite for Travel Buddy AI API client"""

    @pytest.fixture
    def client(self):
        """Create client with test API key"""
        return TravelBuddyClient(api_key="test-key-123")

    def test_client_initialization(self, client):
        """Test client initializes with API key"""
        assert client.api_key == "test-key-123"
        assert client.base_url == "https://visa-requirement.p.rapidapi.com"

    def test_check_visa_us_to_france_visa_free(self, client):
        """Test US citizen to France returns visa-free"""
        # This will fail initially (RED phase)
        result = client.check_visa(passport="US", destination="FR")

        assert isinstance(result, VisaCheckResult)
        assert result.visa_required == False
        assert result.visa_type in ["visa-free", "freedom_of_movement"]
        assert result.max_stay_days == 90
        assert result.passport_code == "US"
        assert result.destination_code == "FR"

    def test_check_visa_india_to_usa_visa_required(self, client):
        """Test Indian citizen to USA requires visa"""
        result = client.check_visa(passport="IN", destination="US")

        assert isinstance(result, VisaCheckResult)
        assert result.visa_required == True
        assert result.visa_type == "visa_required"
        assert result.passport_code == "IN"
        assert result.destination_code == "US"

    def test_check_visa_invalid_passport_code(self, client):
        """Test invalid passport code raises ValueError"""
        with pytest.raises(ValueError, match="Invalid passport code"):
            client.check_visa(passport="INVALID", destination="FR")

    def test_check_visa_invalid_destination_code(self, client):
        """Test invalid destination code raises ValueError"""
        with pytest.raises(ValueError, match="Invalid destination code"):
            client.check_visa(passport="US", destination="INVALID")

    def test_check_visa_api_error_handling(self, client):
        """Test API error handling"""
        # Test with invalid API key
        client_with_bad_key = TravelBuddyClient(api_key="invalid-key")

        with pytest.raises(Exception):  # Should raise an API error
            client_with_bad_key.check_visa(passport="US", destination="FR")

    @pytest.mark.asyncio
    async def test_check_visa_async(self, client):
        """Test async visa checking"""
        result = await client.check_visa_async(passport="US", destination="JP")

        assert isinstance(result, VisaCheckResult)
        assert result.passport_code == "US"
        assert result.destination_code == "JP"


class TestVisaCheckResult:
    """Test suite for VisaCheckResult data class"""

    def test_visa_check_result_creation(self):
        """Test VisaCheckResult creation with all fields"""
        result = VisaCheckResult(
            passport_code="US",
            destination_code="FR",
            visa_required=False,
            visa_type="visa-free",
            max_stay_days=90,
            passport_validity_months=6,
            evisa_url=None,
            embassy_url="https://fr.usembassy.gov/",
            currency="EUR",
            timezone="CET",
        )

        assert result.passport_code == "US"
        assert result.destination_code == "FR"
        assert result.visa_required == False
        assert result.visa_type == "visa-free"
        assert result.max_stay_days == 90
        assert result.passport_validity_months == 6
        assert result.currency == "EUR"
        assert result.timezone == "CET"

    def test_visa_check_result_to_dict(self):
        """Test VisaCheckResult serialization to dict"""
        result = VisaCheckResult(
            passport_code="US",
            destination_code="FR",
            visa_required=False,
            visa_type="visa-free",
            max_stay_days=90,
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["passport_code"] == "US"
        assert result_dict["destination_code"] == "FR"
        assert result_dict["visa_required"] == False
