"""
Tests for Culture Agent

Comprehensive test suite for CultureAgent implementation.
"""

from datetime import date, datetime

import pytest

from app.agents.culture import (
    CommonPhrase,
    CultureAgent,
    CultureAgentInput,
    CultureAgentOutput,
    DressCodeInfo,
)


# ============================================================================
# Input Validation Tests
# ============================================================================


def test_culture_agent_input_valid():
    """Test valid CultureAgentInput creation."""
    input_data = CultureAgentInput(
        trip_id="test-123",
        destination_country="Japan",
        destination_city="Tokyo",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
        traveler_nationality="USA",
    )

    assert input_data.trip_id == "test-123"
    assert input_data.destination_country == "Japan"
    assert input_data.destination_city == "Tokyo"
    assert input_data.departure_date == date(2025, 6, 1)
    assert input_data.return_date == date(2025, 6, 15)
    assert input_data.traveler_nationality == "USA"


def test_culture_agent_input_empty_country_rejected():
    """Test that empty country name is rejected."""
    with pytest.raises(ValueError, match="Destination country cannot be empty"):
        CultureAgentInput(
            trip_id="test-123",
            destination_country="",
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 15),
        )


def test_culture_agent_input_invalid_dates_rejected():
    """Test that return date before departure date is rejected."""
    with pytest.raises(ValueError, match="Return date must be after departure date"):
        CultureAgentInput(
            trip_id="test-123",
            destination_country="France",
            departure_date=date(2025, 6, 15),
            return_date=date(2025, 6, 1),  # Before departure
        )


def test_culture_agent_input_country_whitespace_trimmed():
    """Test that country name whitespace is trimmed."""
    input_data = CultureAgentInput(
        trip_id="test-123",
        destination_country="  Italy  ",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
    )

    assert input_data.destination_country == "Italy"


def test_culture_agent_input_minimal_required_fields():
    """Test CultureAgentInput with minimal required fields."""
    input_data = CultureAgentInput(
        trip_id="test-123",
        destination_country="Spain",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
    )

    assert input_data.trip_id == "test-123"
    assert input_data.destination_country == "Spain"
    assert input_data.destination_city is None
    assert input_data.traveler_nationality is None


# ============================================================================
# Agent Integration Tests
# ============================================================================


@pytest.mark.integration
def test_culture_agent_initialization():
    """Test CultureAgent initialization."""
    agent = CultureAgent()

    assert agent.agent_type == "culture"
    assert agent.config.name == "Culture Agent"
    assert agent.config.agent_type == "culture"
    assert agent.config.version == "1.0.0"
    assert agent.agent is not None


@pytest.mark.integration
def test_culture_agent_run_japan():
    """Test CultureAgent execution for Japan."""
    agent = CultureAgent()

    input_data = CultureAgentInput(
        trip_id="test-japan-001",
        destination_country="Japan",
        destination_city="Tokyo",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
        traveler_nationality="USA",
    )

    result = agent.run(input_data)

    # Validate result type
    assert isinstance(result, CultureAgentOutput)

    # Validate metadata
    assert result.trip_id == "test-japan-001"
    assert result.agent_type == "culture"
    assert isinstance(result.generated_at, datetime)
    assert 0.0 <= result.confidence_score <= 1.0
    assert len(result.sources) >= 1

    # Validate greeting customs
    assert isinstance(result.greeting_customs, list)
    assert len(result.greeting_customs) > 0

    # Validate communication style
    assert isinstance(result.communication_style, str)
    assert len(result.communication_style) > 0

    # Validate dress code
    assert isinstance(result.dress_code, DressCodeInfo)
    assert result.dress_code.casual is not None

    # Validate languages
    assert isinstance(result.official_languages, list)
    assert len(result.official_languages) > 0

    # Validate phrases
    assert isinstance(result.common_phrases, list)
    assert len(result.common_phrases) > 0
    for phrase in result.common_phrases:
        assert isinstance(phrase, CommonPhrase)
        assert phrase.english
        assert phrase.local

    # Validate cultural sensitivity
    assert isinstance(result.cultural_sensitivity_tips, list)
    assert len(result.cultural_sensitivity_tips) > 0
    assert isinstance(result.respect_local_customs_summary, str)


@pytest.mark.integration
def test_culture_agent_run_france():
    """Test CultureAgent execution for France."""
    agent = CultureAgent()

    input_data = CultureAgentInput(
        trip_id="test-france-001",
        destination_country="France",
        destination_city="Paris",
        departure_date=date(2025, 7, 1),
        return_date=date(2025, 7, 10),
    )

    result = agent.run(input_data)

    # Validate result type
    assert isinstance(result, CultureAgentOutput)
    assert result.trip_id == "test-france-001"

    # Validate greeting customs (France has cheek kisses)
    assert isinstance(result.greeting_customs, list)
    assert len(result.greeting_customs) > 0

    # Validate etiquette
    assert isinstance(result.dining_etiquette, list)
    assert isinstance(result.social_etiquette, list)


@pytest.mark.integration
def test_culture_agent_run_saudi_arabia():
    """Test CultureAgent execution for Saudi Arabia (conservative culture)."""
    agent = CultureAgent()

    input_data = CultureAgentInput(
        trip_id="test-saudi-001",
        destination_country="Saudi Arabia",
        destination_city="Riyadh",
        departure_date=date(2025, 9, 1),
        return_date=date(2025, 9, 7),
    )

    result = agent.run(input_data)

    # Validate result type
    assert isinstance(result, CultureAgentOutput)

    # Saudi Arabia should have primary religion
    assert result.primary_religion is not None

    # Should have religious considerations
    assert isinstance(result.religious_considerations, list)

    # Should have dress code guidelines
    assert result.dress_code is not None


# ============================================================================
# Output Structure Tests
# ============================================================================


def test_culture_agent_output_structure():
    """Test CultureAgentOutput model structure."""
    output = CultureAgentOutput(
        trip_id="test-123",
        agent_type="culture",
        generated_at=datetime.utcnow(),
        confidence_score=0.85,
        sources=[],
        warnings=[],
        greeting_customs=["Bow when greeting"],
        communication_style="Indirect, high-context",
        body_language_notes=["Avoid pointing with feet"],
        dress_code=DressCodeInfo(
            casual="Modest clothing",
            religious_sites="Cover shoulders and knees",
        ),
        official_languages=["Japanese"],
        common_phrases=[
            CommonPhrase(
                english="Hello",
                local="こんにちは",
                pronunciation="Kon-nee-chee-wa",
            ),
        ],
        cultural_sensitivity_tips=["Remove shoes indoors"],
        respect_local_customs_summary="Show respect for Japanese customs",
    )

    assert output.trip_id == "test-123"
    assert output.agent_type == "culture"
    assert output.confidence_score == 0.85
    assert len(output.greeting_customs) == 1
    assert len(output.common_phrases) == 1


def test_common_phrase_model():
    """Test CommonPhrase model."""
    phrase = CommonPhrase(
        english="Thank you",
        local="Merci",
        pronunciation="Mare-see",
        context="Expressing gratitude",
    )

    assert phrase.english == "Thank you"
    assert phrase.local == "Merci"
    assert phrase.pronunciation == "Mare-see"
    assert phrase.context == "Expressing gratitude"


def test_dress_code_info_model():
    """Test DressCodeInfo model."""
    dress_code = DressCodeInfo(
        casual="Smart casual",
        formal="Business attire",
        religious_sites="Cover shoulders and knees",
        beaches="Standard swimwear",
        general_notes="Dress respectfully",
    )

    assert dress_code.casual == "Smart casual"
    assert dress_code.formal == "Business attire"
    assert dress_code.religious_sites == "Cover shoulders and knees"


# ============================================================================
# Helper Method Tests
# ============================================================================


def test_extract_json_from_markdown():
    """Test JSON extraction from markdown."""
    agent = CultureAgent()

    # Test with markdown code fence
    markdown_text = """
    Here is the result:
    ```json
    {"greeting_customs": ["Bow"], "communication_style": "Indirect"}
    ```
    """
    result = agent._extract_json_from_text(markdown_text)
    assert result is not None
    assert result.get("greeting_customs") == ["Bow"]


def test_extract_json_from_plain_text():
    """Test JSON extraction from plain text."""
    agent = CultureAgent()

    plain_text = '{"greeting_customs": ["Handshake"], "communication_style": "Direct"}'
    result = agent._extract_json_from_text(plain_text)
    assert result is not None
    assert result.get("greeting_customs") == ["Handshake"]


def test_extract_json_from_invalid_text():
    """Test JSON extraction from invalid text."""
    agent = CultureAgent()

    invalid_text = "This is not JSON at all"
    result = agent._extract_json_from_text(invalid_text)
    assert result is None


def test_calculate_confidence_high():
    """Test confidence calculation with complete data."""
    agent = CultureAgent()

    complete_result = {
        "greeting_customs": ["Bow"],
        "communication_style": "Indirect",
        "dress_code": {"casual": "Modest"},
        "official_languages": ["Japanese"],
        "common_phrases": [{"english": "Hello", "local": "こんにちは"}],
        "religious_considerations": [{"topic": "Temples"}],
        "taboos": [{"behavior": "Pointing"}, {"behavior": "Shoes indoors"}, {"behavior": "Chopstick etiquette"}],
        "dining_etiquette": [{"category": "Dining"}],
        "social_etiquette": [{"category": "Social"}],
        "cultural_sensitivity_tips": ["Tip 1", "Tip 2", "Tip 3", "Tip 4"],
    }

    confidence = agent._calculate_confidence(complete_result)
    assert confidence >= 0.8  # Should be high with complete data


def test_calculate_confidence_low():
    """Test confidence calculation with minimal data."""
    agent = CultureAgent()

    minimal_result = {
        "greeting_customs": ["Hello"],
        "communication_style": "varies",
    }

    confidence = agent._calculate_confidence(minimal_result)
    assert confidence < 0.5  # Should be low with minimal data


def test_fallback_result_creation():
    """Test fallback result creation."""
    agent = CultureAgent()

    input_data = CultureAgentInput(
        trip_id="test-123",
        destination_country="Unknown Country",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
    )

    fallback = agent._create_fallback_result(input_data)

    # Validate fallback structure
    assert "greeting_customs" in fallback
    assert "communication_style" in fallback
    assert "dress_code" in fallback
    assert "official_languages" in fallback
    assert "common_phrases" in fallback
    assert "cultural_sensitivity_tips" in fallback
    assert "respect_local_customs_summary" in fallback

    # Validate fallback content
    assert len(fallback["greeting_customs"]) > 0
    assert len(fallback["common_phrases"]) >= 3  # At least Hello, Thank you, Please


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


@pytest.mark.integration
def test_culture_agent_run_with_minimal_country():
    """Test CultureAgent with a less common country."""
    agent = CultureAgent()

    input_data = CultureAgentInput(
        trip_id="test-minimal-001",
        destination_country="Bhutan",
        departure_date=date(2025, 8, 1),
        return_date=date(2025, 8, 10),
    )

    result = agent.run(input_data)

    # Should still return valid result
    assert isinstance(result, CultureAgentOutput)
    assert result.trip_id == "test-minimal-001"
    assert result.confidence_score > 0.0


def test_culture_agent_agent_type():
    """Test agent type property."""
    agent = CultureAgent()
    assert agent.agent_type == "culture"


def test_culture_agent_config():
    """Test agent configuration."""
    agent = CultureAgent()
    config = agent.config

    assert config.name == "Culture Agent"
    assert config.agent_type == "culture"
    assert config.description == "Cross-cultural intelligence and etiquette specialist"
    assert config.version == "1.0.0"
