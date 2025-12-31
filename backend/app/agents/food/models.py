"""
Food Agent Pydantic Models

Defines input and output data structures for the Food Agent.
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator

from ..interfaces import AgentResult


class FoodAgentInput(BaseModel):
    """Input model for Food Agent."""

    trip_id: str = Field(..., description="Unique trip identifier")
    destination_country: str = Field(..., description="Country name or ISO code")
    destination_city: str | None = Field(None, description="Primary destination city")
    departure_date: date = Field(..., description="Trip departure date")
    return_date: date = Field(..., description="Trip return date")
    traveler_nationality: str | None = Field(None, description="Traveler's nationality")
    dietary_restrictions: list[str] | None = Field(
        None, description="Dietary restrictions (vegetarian, vegan, halal, kosher, gluten-free)"
    )

    @field_validator("destination_country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Ensure country name is not empty."""
        if not v or not v.strip():
            raise ValueError("Destination country cannot be empty")
        return v.strip()

    @field_validator("return_date")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Ensure return date is after departure date."""
        if "departure_date" in info.data and v < info.data["departure_date"]:
            raise ValueError("Return date must be after departure date")
        return v


class Dish(BaseModel):
    """A must-try local dish."""

    name: str = Field(..., description="Dish name")
    description: str = Field(..., description="Description of the dish")
    category: str = Field(..., description="Category (main/appetizer/dessert/beverage/snack)")
    spicy_level: int | None = Field(
        None, description="Spicy level (0=not spicy, 4=very spicy)", ge=0, le=4
    )
    is_vegetarian: bool = Field(default=False, description="Is vegetarian")
    is_vegan: bool = Field(default=False, description="Is vegan")
    typical_price_range: str | None = Field(None, description="Price range ($-$$$$)")


class Restaurant(BaseModel):
    """Restaurant or food venue recommendation."""

    name: str = Field(..., description="Restaurant/venue name")
    type: str = Field(..., description="Type (restaurant/street-food/market/cafe/food-hall)")
    cuisine: str = Field(..., description="Cuisine type")
    price_level: str = Field(..., description="Price level ($-$$$$)")
    location: str | None = Field(None, description="Location/neighborhood")
    specialties: list[str] = Field(default_factory=list, description="Specialty dishes")
    notes: str | None = Field(None, description="Additional notes")


class StreetFood(BaseModel):
    """Street food recommendation."""

    name: str = Field(..., description="Street food name")
    description: str = Field(..., description="What it is")
    where_to_find: str = Field(..., description="Where to find it")
    safety_rating: str = Field(..., description="Safety rating (safe/generally-safe/use-caution)")
    price_range: str = Field(..., description="Typical price range")


class DietaryAvailability(BaseModel):
    """Availability of dietary options."""

    vegetarian: str = Field(
        ..., description="Vegetarian availability (widespread/common/limited/rare)"
    )
    vegan: str = Field(..., description="Vegan availability (widespread/common/limited/rare)")
    halal: str = Field(..., description="Halal availability (widespread/common/limited/rare)")
    kosher: str = Field(..., description="Kosher availability (widespread/common/limited/rare)")
    gluten_free: str = Field(
        ..., description="Gluten-free availability (widespread/common/limited/rare)"
    )


class FoodAgentOutput(AgentResult):
    """Output model for Food Agent."""

    # AgentResult requires data field - we provide it as empty since we use specific fields
    data: dict = Field(default_factory=dict, description="Legacy field for compatibility")

    # Must-Try Dishes
    must_try_dishes: list[Dish] = Field(..., description="Essential local dishes to try")

    # Street Food
    street_food: list[StreetFood] = Field(
        default_factory=list, description="Street food recommendations"
    )

    # Restaurants & Venues
    restaurant_recommendations: list[Restaurant] = Field(
        ..., description="Recommended restaurants and food venues"
    )

    # Dining Etiquette
    dining_etiquette: list[str] = Field(..., description="Important dining customs and etiquette")

    # Dietary Options
    dietary_availability: DietaryAvailability = Field(
        ..., description="Availability of dietary options"
    )
    dietary_notes: list[str] = Field(
        default_factory=list, description="Additional dietary considerations"
    )

    # Price Ranges
    meal_price_ranges: dict[str, str] = Field(
        ...,
        description="Price ranges for different meal types (street-food/casual/mid-range/fine-dining)",
    )

    # Food Safety
    food_safety_tips: list[str] = Field(..., description="Food safety and hygiene tips")
    water_safety: str = Field(..., description="Tap water safety information")

    # Additional Information
    local_ingredients: list[str] = Field(
        default_factory=list, description="Notable local ingredients"
    )
    food_markets: list[str] = Field(default_factory=list, description="Recommended food markets")
    cooking_classes: list[str] | None = Field(None, description="Cooking class recommendations")
    food_tours: list[str] | None = Field(None, description="Food tour recommendations")
