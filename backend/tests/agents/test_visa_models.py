"""
Tests for Visa Agent Models

Covers:
- Visa category classification
- Confidence score calculation
- VisaRequirement from API response
- VisaAgentOutput confidence recalculation
"""

from datetime import datetime, timedelta

import pytest

from app.agents.visa.models import (
    ApplicationProcess,
    ConfidenceLevel,
    EnhancedSourceReference,
    EntryRequirement,
    SourceType,
    VisaAgentOutput,
    VisaCategory,
    VisaRequirement,
    calculate_confidence_score,
    classify_visa_type,
)


class TestVisaCategoryClassification:
    """Test suite for visa type classification"""

    def test_classify_visa_free(self):
        """Test visa-free classification"""
        assert classify_visa_type("visa-free") == VisaCategory.VISA_FREE
        assert classify_visa_type("Visa Free Entry") == VisaCategory.VISA_FREE
        assert classify_visa_type("No visa required") == VisaCategory.VISA_FREE
        assert classify_visa_type("visa exempt") == VisaCategory.VISA_FREE

    def test_classify_freedom_of_movement(self):
        """Test freedom of movement classification"""
        assert classify_visa_type("freedom of movement") == VisaCategory.FREEDOM_OF_MOVEMENT
        assert classify_visa_type("Schengen Area") == VisaCategory.FREEDOM_OF_MOVEMENT
        assert classify_visa_type("EU Citizen") == VisaCategory.FREEDOM_OF_MOVEMENT

    def test_classify_visa_on_arrival(self):
        """Test visa on arrival classification"""
        assert classify_visa_type("visa on arrival") == VisaCategory.VISA_ON_ARRIVAL
        assert classify_visa_type("VOA") == VisaCategory.VISA_ON_ARRIVAL
        assert classify_visa_type("Get visa at airport") == VisaCategory.VISA_ON_ARRIVAL

    def test_classify_evisa(self):
        """Test e-visa classification"""
        assert classify_visa_type("e-visa") == VisaCategory.EVISA
        assert classify_visa_type("eVisa") == VisaCategory.EVISA
        assert classify_visa_type("electronic visa") == VisaCategory.EVISA
        assert classify_visa_type("online visa") == VisaCategory.EVISA

    def test_classify_eta(self):
        """Test ETA classification"""
        assert classify_visa_type("ETA") == VisaCategory.ETA
        assert classify_visa_type("Electronic Travel Authorization") == VisaCategory.ETA
        assert classify_visa_type("ESTA") == VisaCategory.ETA

    def test_classify_tourist_visa(self):
        """Test tourist visa classification"""
        assert classify_visa_type("tourist visa") == VisaCategory.TOURIST_VISA
        assert classify_visa_type("tourism visa") == VisaCategory.TOURIST_VISA
        assert classify_visa_type("vacation visa") == VisaCategory.TOURIST_VISA

    def test_classify_business_visa(self):
        """Test business visa classification"""
        assert classify_visa_type("business visa") == VisaCategory.BUSINESS_VISA
        assert classify_visa_type("commercial visa") == VisaCategory.BUSINESS_VISA

    def test_classify_transit_visa(self):
        """Test transit visa classification"""
        assert classify_visa_type("transit visa") == VisaCategory.TRANSIT_VISA
        assert classify_visa_type("passing through") == VisaCategory.TRANSIT_VISA

    def test_classify_work_visa(self):
        """Test work visa classification"""
        assert classify_visa_type("work visa") == VisaCategory.WORK_VISA
        assert classify_visa_type("employment visa") == VisaCategory.WORK_VISA

    def test_classify_student_visa(self):
        """Test student visa classification"""
        assert classify_visa_type("student visa") == VisaCategory.STUDENT_VISA
        assert classify_visa_type("study visa") == VisaCategory.STUDENT_VISA

    def test_classify_restricted(self):
        """Test restricted classification"""
        assert classify_visa_type("restricted entry") == VisaCategory.RESTRICTED
        assert classify_visa_type("special permit required") == VisaCategory.RESTRICTED

    def test_classify_not_allowed(self):
        """Test not allowed classification"""
        assert classify_visa_type("not allowed") == VisaCategory.NOT_ALLOWED
        assert classify_visa_type("travel banned") == VisaCategory.NOT_ALLOWED
        assert classify_visa_type("no entry permitted") == VisaCategory.NOT_ALLOWED

    def test_classify_unknown(self):
        """Test unknown classification"""
        assert classify_visa_type("") == VisaCategory.UNKNOWN
        assert classify_visa_type(None) == VisaCategory.UNKNOWN
        assert classify_visa_type("random text") == VisaCategory.UNKNOWN

    def test_classify_visa_required_default(self):
        """Test 'visa required' defaults to tourist visa"""
        assert classify_visa_type("visa required") == VisaCategory.TOURIST_VISA


class TestConfidenceScoreCalculation:
    """Test suite for confidence score calculation"""

    def test_high_confidence_government_source(self):
        """Test high confidence with government source"""
        score, level = calculate_confidence_score(
            source_types=[SourceType.GOVERNMENT],
            sources_count=2,
            data_freshness_days=5,
            has_official_source=True,
            data_completeness=0.9,
        )
        assert score >= 0.8
        assert level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERIFIED]

    def test_medium_confidence_api_source(self):
        """Test medium confidence with API source only"""
        score, level = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=1,
            data_freshness_days=30,
            has_official_source=False,
            data_completeness=0.7,
        )
        assert 0.5 <= score <= 0.8
        assert level in [ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]

    def test_low_confidence_ai_inference(self):
        """Test low confidence with AI inference only"""
        score, level = calculate_confidence_score(
            source_types=[SourceType.AI_INFERENCE],
            sources_count=1,
            data_freshness_days=100,
            has_official_source=False,
            data_completeness=0.3,
        )
        assert score < 0.5
        assert level in [ConfidenceLevel.LOW, ConfidenceLevel.UNCERTAIN]

    def test_multiple_sources_bonus(self):
        """Test bonus for multiple sources"""
        single_score, _ = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=1,
            data_freshness_days=10,
            has_official_source=False,
            data_completeness=0.5,
        )
        multi_score, _ = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=3,
            data_freshness_days=10,
            has_official_source=False,
            data_completeness=0.5,
        )
        assert multi_score > single_score

    def test_freshness_decay(self):
        """Test that older data reduces confidence"""
        fresh_score, _ = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=1,
            data_freshness_days=5,
            has_official_source=False,
            data_completeness=0.5,
        )
        stale_score, _ = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=1,
            data_freshness_days=200,
            has_official_source=False,
            data_completeness=0.5,
        )
        assert fresh_score > stale_score

    def test_official_source_bonus(self):
        """Test bonus for official source"""
        no_official, _ = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=1,
            data_freshness_days=10,
            has_official_source=False,
            data_completeness=0.5,
        )
        with_official, _ = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=1,
            data_freshness_days=10,
            has_official_source=True,
            data_completeness=0.5,
        )
        assert with_official > no_official

    def test_data_completeness_impact(self):
        """Test that data completeness affects score"""
        incomplete_score, _ = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=1,
            data_freshness_days=10,
            has_official_source=False,
            data_completeness=0.2,
        )
        complete_score, _ = calculate_confidence_score(
            source_types=[SourceType.API],
            sources_count=1,
            data_freshness_days=10,
            has_official_source=False,
            data_completeness=1.0,
        )
        assert complete_score > incomplete_score

    def test_score_clamped_to_range(self):
        """Test that score is always between 0 and 1"""
        score, _ = calculate_confidence_score(
            source_types=[SourceType.GOVERNMENT],
            sources_count=5,
            data_freshness_days=1,
            has_official_source=True,
            data_completeness=1.0,
        )
        assert 0.0 <= score <= 1.0

    def test_confidence_levels_correct(self):
        """Test that confidence levels are assigned correctly"""
        # Verified level (>0.9)
        score, level = calculate_confidence_score(
            source_types=[SourceType.GOVERNMENT],
            sources_count=3,
            data_freshness_days=1,
            has_official_source=True,
            data_completeness=1.0,
        )
        if score >= 0.9:
            assert level == ConfidenceLevel.VERIFIED


class TestVisaRequirementFromAPI:
    """Test suite for VisaRequirement.from_api_response"""

    def test_from_api_visa_free(self):
        """Test creating VisaRequirement from visa-free API response"""
        api_data = {
            "visa_type": "visa-free",
            "max_stay_days": 90,
            "validity_period": "90 days",
        }
        requirement = VisaRequirement.from_api_response(api_data)

        assert requirement.visa_required is False
        assert requirement.visa_category == VisaCategory.VISA_FREE
        assert requirement.max_stay_days == 90

    def test_from_api_evisa(self):
        """Test creating VisaRequirement from e-visa API response"""
        api_data = {
            "category": "e-visa",
            "max_stay_days": 30,
            "multiple_entry": True,
        }
        requirement = VisaRequirement.from_api_response(api_data)

        assert requirement.visa_required is True
        assert requirement.visa_category == VisaCategory.EVISA
        assert requirement.multiple_entry is True

    def test_from_api_tourist_visa(self):
        """Test creating VisaRequirement from tourist visa API response"""
        api_data = {
            "visa_type": "tourist visa required",
            "max_stay_days": 60,
            "urgency_level": "high",
        }
        requirement = VisaRequirement.from_api_response(api_data)

        assert requirement.visa_required is True
        assert requirement.visa_category == VisaCategory.TOURIST_VISA
        assert requirement.urgency_level == "high"


class TestVisaAgentOutputConfidence:
    """Test suite for VisaAgentOutput confidence recalculation"""

    def test_recalculate_confidence(self):
        """Test confidence recalculation"""
        output = VisaAgentOutput(
            trip_id="test-trip-123",
            confidence_score=0.5,
            confidence_level=ConfidenceLevel.MEDIUM,
            visa_requirement=VisaRequirement(
                visa_required=True,
                visa_type="tourist visa",
                max_stay_days=30,
            ),
            application_process=ApplicationProcess(
                application_method="embassy",
                processing_time="5-10 days",
            ),
            entry_requirements=EntryRequirement(
                passport_validity="6 months",
            ),
            tips=["Apply early", "Bring photos"],
            enhanced_sources=[
                EnhancedSourceReference(
                    source_type=SourceType.GOVERNMENT,
                    url="https://example.gov/visa",
                    description="Official visa page",
                    is_official=True,
                ),
                EnhancedSourceReference(
                    source_type=SourceType.API,
                    url="https://api.example.com/visa",
                    description="Travel API",
                ),
            ],
            last_verified=datetime.utcnow(),
        )

        old_score = output.confidence_score
        output.recalculate_confidence()

        # With government source and good data completeness, should be higher
        assert output.confidence_score >= 0.6
        assert output.confidence_level in [
            ConfidenceLevel.MEDIUM,
            ConfidenceLevel.HIGH,
            ConfidenceLevel.VERIFIED,
        ]

    def test_recalculate_with_stale_data(self):
        """Test confidence with stale data"""
        output = VisaAgentOutput(
            trip_id="test-trip-456",
            confidence_score=0.9,
            confidence_level=ConfidenceLevel.VERIFIED,
            visa_requirement=VisaRequirement(
                visa_required=False,
                visa_type="visa-free",
            ),
            application_process=ApplicationProcess(),
            entry_requirements=EntryRequirement(),
            enhanced_sources=[
                EnhancedSourceReference(
                    source_type=SourceType.AI_INFERENCE,
                    description="AI inference",
                ),
            ],
            last_verified=datetime.utcnow() - timedelta(days=200),
        )

        output.recalculate_confidence()

        # With old data and AI inference, should be lower
        assert output.confidence_score < 0.5
        assert output.confidence_level in [
            ConfidenceLevel.LOW,
            ConfidenceLevel.UNCERTAIN,
        ]
