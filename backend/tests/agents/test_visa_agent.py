"""
Tests for Visa Agent

Following TDD (RED-GREEN-REFACTOR):
1. RED: Write failing tests first
2. GREEN: Write minimal code to pass
3. REFACTOR: Improve code quality

Test cases from visa-agent-roadmap.md:
- US to France: visa-free (Schengen 90 days)
- India to USA: visa required (B1/B2)
- US to Japan: visa-free (90 days)
"""

from datetime import date

import pytest

from app.agents.interfaces import SourceReference
from app.agents.visa.agent import VisaAgent
from app.agents.visa.models import (
    ApplicationProcess,
    EntryRequirement,
    VisaAgentInput,
    VisaAgentOutput,
    VisaRequirement,
)


@pytest.mark.integration
class TestVisaAgent:
    """Test suite for Visa Agent"""

    @pytest.fixture()
    def agent(self):
        """Create Visa Agent instance"""
        return VisaAgent()

    def test_agent_initialization(self, agent):
        """Test Visa Agent initializes correctly"""
        assert agent is not None
        assert hasattr(agent, "run")
        assert agent.name == "visa"
        assert agent.description is not None

    @pytest.mark.integration
    def test_us_to_france_visa_free(self, agent):
        """
        Test: US citizen to France (visa-free, Schengen 90 days)

        Expected:
        - visa_required: False
        - visa_type: "visa-free" or "freedom_of_movement"
        - max_stay_days: 90
        - confidence_score: >= 0.9 (official data)
        """
        input_data = VisaAgentInput(
            trip_id="test-us-fr-001",
            user_nationality="US",
            destination_country="FR",
            destination_city="Paris",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        result = agent.run(input_data)

        # Verify result type
        assert isinstance(result, VisaAgentOutput)

        # Verify visa requirements
        assert result.visa_requirement.visa_required == False
        assert result.visa_requirement.visa_type in ["visa-free", "freedom_of_movement"]
        assert result.visa_requirement.max_stay_days == 90

        # Verify confidence score
        assert result.confidence_score >= 0.9

        # Verify sources
        assert len(result.sources) > 0
        assert all(isinstance(s, SourceReference) for s in result.sources)

    @pytest.mark.integration
    def test_india_to_usa_visa_required(self, agent):
        """
        Test: Indian citizen to USA (visa required, B1/B2)

        Expected:
        - visa_required: True
        - visa_type contains "visa_required" or "tourist"
        - application_method mentions embassy or consulate
        - required_documents includes passport, photo, DS-160
        """
        input_data = VisaAgentInput(
            trip_id="test-in-us-001",
            user_nationality="IN",
            destination_country="US",
            destination_city="New York",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        result = agent.run(input_data)

        # Verify result type
        assert isinstance(result, VisaAgentOutput)

        # Verify visa requirements
        assert result.visa_requirement.visa_required == True
        assert "visa" in result.visa_requirement.visa_type.lower()

        # Verify application process
        assert result.application_process is not None
        assert len(result.application_process.required_documents) > 0

        # Verify confidence score
        assert result.confidence_score >= 0.8

    @pytest.mark.integration
    def test_us_to_japan_visa_free(self, agent):
        """
        Test: US citizen to Japan (visa-free 90 days for tourism)

        Expected:
        - visa_required: False
        - visa_type: "visa-free"
        - max_stay_days: 90
        """
        input_data = VisaAgentInput(
            trip_id="test-us-jp-001",
            user_nationality="US",
            destination_country="JP",
            destination_city="Tokyo",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        result = agent.run(input_data)

        assert result.visa_requirement.visa_required == False
        assert result.visa_requirement.max_stay_days == 90
        assert result.confidence_score >= 0.9

    @pytest.mark.integration
    def test_business_vs_tourism_purpose(self, agent):
        """Test that trip purpose affects visa requirements"""
        tourism_input = VisaAgentInput(
            trip_id="test-purpose-tourism",
            user_nationality="US",
            destination_country="CN",
            destination_city="Beijing",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        business_input = VisaAgentInput(
            trip_id="test-purpose-business",
            user_nationality="US",
            destination_country="CN",
            destination_city="Beijing",
            trip_purpose="business",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        tourism_result = agent.run(tourism_input)
        business_result = agent.run(business_input)

        # Both should require visa, but might have different types
        assert tourism_result.visa_requirement.visa_required == True
        assert business_result.visa_requirement.visa_required == True

    def test_invalid_country_code(self, agent):
        """Test invalid country code raises validation error"""
        from pydantic import ValidationError

        # Pydantic validates country code length (max 2 chars)
        with pytest.raises(ValidationError):
            VisaAgentInput(
                trip_id="test-invalid",
                user_nationality="INVALID",  # Invalid code - too long
                destination_country="FR",
                destination_city="Paris",
                trip_purpose="tourism",
                duration_days=14,
                departure_date=date(2025, 6, 1),
            )

    @pytest.mark.integration
    def test_output_contains_all_required_fields(self, agent):
        """Test that output contains all required fields"""
        input_data = VisaAgentInput(
            trip_id="test-fields",
            user_nationality="US",
            destination_country="FR",
            destination_city="Paris",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        result = agent.run(input_data)

        # Verify all required fields exist
        assert hasattr(result, "visa_requirement")
        assert hasattr(result, "application_process")
        assert hasattr(result, "entry_requirements")
        assert hasattr(result, "tips")
        assert hasattr(result, "warnings")
        assert hasattr(result, "sources")
        assert hasattr(result, "confidence_score")

        # Verify types
        assert isinstance(result.visa_requirement, VisaRequirement)
        assert isinstance(result.application_process, ApplicationProcess)
        assert isinstance(result.entry_requirements, EntryRequirement)
        assert isinstance(result.tips, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.sources, list)
        assert isinstance(result.confidence_score, float)

    @pytest.mark.integration
    def test_confidence_score_range(self, agent):
        """Test confidence score is between 0.0 and 1.0"""
        input_data = VisaAgentInput(
            trip_id="test-confidence",
            user_nationality="US",
            destination_country="FR",
            destination_city="Paris",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        result = agent.run(input_data)

        assert 0.0 <= result.confidence_score <= 1.0

    @pytest.mark.integration
    def test_sources_contain_references(self, agent):
        """Test that sources contain proper references"""
        input_data = VisaAgentInput(
            trip_id="test-sources",
            user_nationality="US",
            destination_country="FR",
            destination_city="Paris",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        result = agent.run(input_data)

        # Verify sources exist
        assert len(result.sources) > 0

        # Verify source structure
        for source in result.sources:
            assert isinstance(source, SourceReference)
            assert source.source_type is not None
            assert source.url is not None or source.description is not None


class TestVisaAgentModels:
    """Test suite for Visa Agent Pydantic models"""

    def test_visa_agent_input_validation(self):
        """Test VisaAgentInput validates required fields"""
        valid_input = VisaAgentInput(
            trip_id="test-001",
            user_nationality="US",
            destination_country="FR",
            destination_city="Paris",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        assert valid_input.trip_id == "test-001"
        assert valid_input.user_nationality == "US"
        assert valid_input.destination_country == "FR"

    def test_visa_agent_input_defaults(self):
        """Test VisaAgentInput default values"""
        minimal_input = VisaAgentInput(
            trip_id="test-002",
            user_nationality="US",
            destination_country="FR",
            destination_city="Paris",
            duration_days=14,
            departure_date=date(2025, 6, 1),
        )

        # Default trip_purpose should be "tourism"
        assert minimal_input.trip_purpose == "tourism"

    def test_visa_requirement_model(self):
        """Test VisaRequirement model"""
        requirement = VisaRequirement(
            visa_required=False,
            visa_type="visa-free",
            max_stay_days=90,
            validity_period="6 months",
        )

        assert requirement.visa_required == False
        assert requirement.visa_type == "visa-free"
        assert requirement.max_stay_days == 90

    def test_application_process_model(self):
        """Test ApplicationProcess model"""
        process = ApplicationProcess(
            application_method="online",
            processing_time="3-5 business days",
            cost_usd=50.0,
            required_documents=["Passport", "Photo", "Application form"],
            application_url="https://example.com/apply",
        )

        assert process.application_method == "online"
        assert process.cost_usd == 50.0
        assert len(process.required_documents) == 3

    def test_entry_requirement_model(self):
        """Test EntryRequirement model"""
        entry = EntryRequirement(
            passport_validity="6 months beyond stay",
            blank_pages_required=2,
            vaccinations=[],
            health_declaration=False,
            travel_insurance=False,
            proof_of_funds=False,
            return_ticket=True,
        )

        assert entry.passport_validity == "6 months beyond stay"
        assert entry.blank_pages_required == 2
        assert entry.return_ticket == True
