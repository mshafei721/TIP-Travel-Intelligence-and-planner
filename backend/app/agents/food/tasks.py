"""
Food Agent CrewAI Tasks

Defines tasks for food research and culinary intelligence gathering.
"""

from crewai import Task

from .prompts import (
    COMPREHENSIVE_FOOD_TASK_DESC,
    FOOD_DIETARY_TASK_DESC,
    FOOD_DISHES_TASK_DESC,
    FOOD_PRICES_TASK_DESC,
    FOOD_RESTAURANTS_TASK_DESC,
    FOOD_SAFETY_TASK_DESC,
)


def create_dishes_task(agent, destination_country: str) -> Task:
    """
    Create task for researching must-try dishes.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for dish research
    """
    return Task(
        description=FOOD_DISHES_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="List of must-try local dishes with descriptions, categories, and details",
    )


def create_restaurants_task(
    agent, destination_country: str, destination_city: str
) -> Task:
    """
    Create task for compiling restaurant recommendations.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name
        destination_city: Destination city name

    Returns:
        CrewAI Task for restaurant research
    """
    return Task(
        description=FOOD_RESTAURANTS_TASK_DESC.format(
            destination_country=destination_country,
            destination_city=destination_city or "major cities",
        ),
        agent=agent,
        expected_output="Restaurant and food venue recommendations with details",
    )


def create_dietary_task(agent, destination_country: str) -> Task:
    """
    Create task for analyzing dietary accommodations.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for dietary research
    """
    return Task(
        description=FOOD_DIETARY_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Dietary accommodation availability and guidance",
    )


def create_safety_task(agent, destination_country: str) -> Task:
    """
    Create task for compiling food safety information.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for food safety research
    """
    return Task(
        description=FOOD_SAFETY_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Food safety tips, water safety, and hygiene guidance",
    )


def create_prices_task(agent, destination_country: str) -> Task:
    """
    Create task for analyzing meal prices.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for price analysis
    """
    return Task(
        description=FOOD_PRICES_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Meal price ranges for different dining levels",
    )


def create_comprehensive_food_task(agent, destination_country: str) -> Task:
    """
    Create task for generating comprehensive food guide.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for comprehensive food guide
    """
    return Task(
        description=COMPREHENSIVE_FOOD_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Complete food and culinary guide in JSON format matching FoodAgentOutput schema",
    )
