"""
Tests for Food Agent

Comprehensive test suite for FoodAgent implementation.
"""

from datetime import date, datetime

import pytest

from app.agents.food import (
    DietaryAvailability,
    Dish,
    FoodAgent,
    FoodAgentInput,
    FoodAgentOutput,
    Restaurant,
    StreetFood,
)


# ============================================================================
# Input Validation Tests
# ============================================================================


def test_food_agent_input_valid():
    """Test valid FoodAgentInput creation."""
    input_data = FoodAgentInput(
        trip_id="test-123",
        destination_country="Italy",
        destination_city="Rome",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
        traveler_nationality="USA",
        dietary_restrictions=["vegetarian"],
    )

    assert input_data.trip_id == "test-123"
    assert input_data.destination_country == "Italy"
    assert input_data.destination_city == "Rome"
    assert input_data.dietary_restrictions == ["vegetarian"]


def test_food_agent_input_empty_country_rejected():
    """Test that empty country name is rejected."""
    with pytest.raises(ValueError, match="Destination country cannot be empty"):
        FoodAgentInput(
            trip_id="test-123",
            destination_country="",
            departure_date=date(2025, 6, 1),
            return_date=date(2025, 6, 15),
        )


def test_food_agent_input_invalid_dates_rejected():
    """Test that return date before departure date is rejected."""
    with pytest.raises(ValueError, match="Return date must be after departure date"):
        FoodAgentInput(
            trip_id="test-123",
            destination_country="Thailand",
            departure_date=date(2025, 6, 15),
            return_date=date(2025, 6, 1),
        )


def test_food_agent_input_minimal_required_fields():
    """Test FoodAgentInput with minimal required fields."""
    input_data = FoodAgentInput(
        trip_id="test-123",
        destination_country="Japan",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
    )

    assert input_data.trip_id == "test-123"
    assert input_data.destination_city is None
    assert input_data.dietary_restrictions is None


# ============================================================================
# Agent Integration Tests
# ============================================================================


@pytest.mark.integration
def test_food_agent_initialization():
    """Test FoodAgent initialization."""
    agent = FoodAgent()

    assert agent.agent_type == "food"
    assert agent.config.name == "Food Agent"
    assert agent.config.agent_type == "food"
    assert agent.config.version == "1.0.0"
    assert agent.agent is not None


@pytest.mark.integration
def test_food_agent_run_italy():
    """Test FoodAgent execution for Italy."""
    agent = FoodAgent()

    input_data = FoodAgentInput(
        trip_id="test-italy-001",
        destination_country="Italy",
        destination_city="Rome",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
    )

    result = agent.run(input_data)

    # Validate result type
    assert isinstance(result, FoodAgentOutput)

    # Validate metadata
    assert result.trip_id == "test-italy-001"
    assert result.agent_type == "food"
    assert isinstance(result.generated_at, datetime)
    assert 0.0 <= result.confidence_score <= 1.0
    assert len(result.sources) >= 1

    # Validate must-try dishes
    assert isinstance(result.must_try_dishes, list)
    assert len(result.must_try_dishes) > 0
    for dish in result.must_try_dishes:
        assert isinstance(dish, Dish)
        assert dish.name
        assert dish.category

    # Validate restaurants
    assert isinstance(result.restaurant_recommendations, list)

    # Validate dietary availability
    assert isinstance(result.dietary_availability, DietaryAvailability)

    # Validate price ranges
    assert isinstance(result.meal_price_ranges, dict)
    assert "street_food" in result.meal_price_ranges

    # Validate food safety
    assert isinstance(result.food_safety_tips, list)
    assert len(result.food_safety_tips) > 0
    assert isinstance(result.water_safety, str)


@pytest.mark.integration
def test_food_agent_run_japan():
    """Test FoodAgent execution for Japan."""
    agent = FoodAgent()

    input_data = FoodAgentInput(
        trip_id="test-japan-001",
        destination_country="Japan",
        destination_city="Tokyo",
        departure_date=date(2025, 7, 1),
        return_date=date(2025, 7, 10),
        dietary_restrictions=["vegetarian"],
    )

    result = agent.run(input_data)

    assert isinstance(result, FoodAgentOutput)
    assert result.trip_id == "test-japan-001"

    # Japan should have dining etiquette
    assert isinstance(result.dining_etiquette, list)
    assert len(result.dining_etiquette) > 0


@pytest.mark.integration
def test_food_agent_run_thailand():
    """Test FoodAgent execution for Thailand (street food culture)."""
    agent = FoodAgent()

    input_data = FoodAgentInput(
        trip_id="test-thailand-001",
        destination_country="Thailand",
        destination_city="Bangkok",
        departure_date=date(2025, 8, 1),
        return_date=date(2025, 8, 7),
    )

    result = agent.run(input_data)

    assert isinstance(result, FoodAgentOutput)
    assert result.trip_id == "test-thailand-001"

    # Thailand is known for street food
    assert isinstance(result.street_food, list)


# ============================================================================
# Output Structure Tests
# ============================================================================


def test_food_agent_output_structure():
    """Test FoodAgentOutput model structure."""
    output = FoodAgentOutput(
        trip_id="test-123",
        agent_type="food",
        generated_at=datetime.utcnow(),
        confidence_score=0.85,
        sources=[],
        warnings=[],
        must_try_dishes=[
            Dish(
                name="Sushi",
                description="Raw fish on rice",
                category="main",
                spicy_level=0,
            ),
        ],
        restaurant_recommendations=[
            Restaurant(
                name="Sushi Dai",
                type="restaurant",
                cuisine="Japanese",
                price_level="$$$",
            ),
        ],
        dining_etiquette=["Use chopsticks properly"],
        dietary_availability=DietaryAvailability(
            vegetarian="common",
            vegan="limited",
            halal="limited",
            kosher="rare",
            gluten_free="limited",
        ),
        meal_price_ranges={"street_food": "$5-10"},
        food_safety_tips=["Wash hands before eating"],
        water_safety="safe-to-drink",
    )

    assert output.trip_id == "test-123"
    assert output.agent_type == "food"
    assert len(output.must_try_dishes) == 1
    assert len(output.restaurant_recommendations) == 1


def test_dish_model():
    """Test Dish model."""
    dish = Dish(
        name="Pad Thai",
        description="Stir-fried noodles",
        category="main",
        spicy_level=2,
        is_vegetarian=False,
        typical_price_range="$",
    )

    assert dish.name == "Pad Thai"
    assert dish.spicy_level == 2
    assert dish.is_vegetarian is False


def test_restaurant_model():
    """Test Restaurant model."""
    restaurant = Restaurant(
        name="Trattoria Roma",
        type="restaurant",
        cuisine="Italian",
        price_level="$$",
        location="Trastevere",
        specialties=["Carbonara", "Cacio e Pepe"],
    )

    assert restaurant.name == "Trattoria Roma"
    assert restaurant.price_level == "$$"
    assert len(restaurant.specialties) == 2


def test_street_food_model():
    """Test StreetFood model."""
    street_food = StreetFood(
        name="Tacos",
        description="Street tacos",
        where_to_find="Street corners",
        safety_rating="generally-safe",
        price_range="$1-2",
    )

    assert street_food.name == "Tacos"
    assert street_food.safety_rating == "generally-safe"


# ============================================================================
# Helper Method Tests
# ============================================================================


def test_extract_json_from_markdown():
    """Test JSON extraction from markdown."""
    agent = FoodAgent()

    markdown_text = """
    Here is the result:
    ```json
    {"must_try_dishes": [], "dining_etiquette": ["Use chopsticks"]}
    ```
    """
    result = agent._extract_json_from_text(markdown_text)
    assert result is not None
    assert result.get("dining_etiquette") == ["Use chopsticks"]


def test_extract_json_from_plain_text():
    """Test JSON extraction from plain text."""
    agent = FoodAgent()

    plain_text = '{"must_try_dishes": [], "water_safety": "safe"}'
    result = agent._extract_json_from_text(plain_text)
    assert result is not None
    assert result.get("water_safety") == "safe"


def test_extract_json_from_invalid_text():
    """Test JSON extraction from invalid text."""
    agent = FoodAgent()

    invalid_text = "This is not JSON at all"
    result = agent._extract_json_from_text(invalid_text)
    assert result is None


def test_calculate_confidence_high():
    """Test confidence calculation with complete data."""
    agent = FoodAgent()

    complete_result = {
        "must_try_dishes": [{"name": "Dish 1"} for _ in range(6)],
        "restaurant_recommendations": [{"name": "Rest 1"} for _ in range(5)],
        "dining_etiquette": ["Tip 1"],
        "dietary_availability": {"vegetarian": "common"},
        "meal_price_ranges": {"street_food": "$5"},
        "food_safety_tips": ["Tip 1", "Tip 2", "Tip 3"],
        "water_safety": "safe",
    }

    confidence = agent._calculate_confidence(complete_result)
    assert confidence >= 0.8


def test_calculate_confidence_low():
    """Test confidence calculation with minimal data."""
    agent = FoodAgent()

    minimal_result = {
        "must_try_dishes": [],
        "dining_etiquette": [],
    }

    confidence = agent._calculate_confidence(minimal_result)
    assert confidence < 0.5


def test_fallback_result_creation():
    """Test fallback result creation."""
    agent = FoodAgent()

    input_data = FoodAgentInput(
        trip_id="test-123",
        destination_country="Unknown Country",
        departure_date=date(2025, 6, 1),
        return_date=date(2025, 6, 15),
    )

    fallback = agent._create_fallback_result(input_data)

    assert "must_try_dishes" in fallback
    assert "dining_etiquette" in fallback
    assert "food_safety_tips" in fallback
    assert "water_safety" in fallback
    assert len(fallback["food_safety_tips"]) >= 3


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


@pytest.mark.integration
def test_food_agent_run_with_dietary_restrictions():
    """Test FoodAgent with dietary restrictions."""
    agent = FoodAgent()

    input_data = FoodAgentInput(
        trip_id="test-dietary-001",
        destination_country="India",
        destination_city="Delhi",
        departure_date=date(2025, 9, 1),
        return_date=date(2025, 9, 10),
        dietary_restrictions=["vegetarian", "gluten-free"],
    )

    result = agent.run(input_data)

    assert isinstance(result, FoodAgentOutput)
    assert result.trip_id == "test-dietary-001"


def test_food_agent_agent_type():
    """Test agent type property."""
    agent = FoodAgent()
    assert agent.agent_type == "food"


def test_food_agent_config():
    """Test agent configuration."""
    agent = FoodAgent()
    config = agent.config

    assert config.name == "Food Agent"
    assert config.agent_type == "food"
    assert config.description == "Culinary travel intelligence and food culture specialist"
    assert config.version == "1.0.0"
