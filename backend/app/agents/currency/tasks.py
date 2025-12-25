"""
Currency Agent CrewAI Tasks

Defines tasks for currency research and financial intelligence gathering.
"""

from crewai import Task
from .prompts import (
    CURRENCY_RESEARCH_TASK_DESC,
    CURRENCY_COST_ANALYSIS_TASK_DESC,
    CURRENCY_SAFETY_TASK_DESC,
    COMPREHENSIVE_CURRENCY_TASK_DESC,
)


def create_currency_research_task(
    agent,
    destination_country: str,
    base_currency: str
) -> Task:
    """
    Create task for researching currency and payment information.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name
        base_currency: Traveler's base currency code

    Returns:
        CrewAI Task for currency research
    """
    return Task(
        description=CURRENCY_RESEARCH_TASK_DESC.format(
            destination_country=destination_country,
            base_currency=base_currency
        ),
        agent=agent,
        expected_output="Detailed currency information including exchange rates, ATM availability, payment methods, and tipping customs"
    )


def create_cost_analysis_task(
    agent,
    destination_country: str,
    destination_city: str
) -> Task:
    """
    Create task for analyzing cost of living and budgeting.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name
        destination_city: Destination city name

    Returns:
        CrewAI Task for cost analysis
    """
    return Task(
        description=CURRENCY_COST_ANALYSIS_TASK_DESC.format(
            destination_country=destination_country,
            destination_city=destination_city or "major cities"
        ),
        agent=agent,
        expected_output="Comprehensive cost estimates and daily budget recommendations"
    )


def create_safety_task(
    agent,
    destination_country: str
) -> Task:
    """
    Create task for financial safety and exchange guidance.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for safety guidance
    """
    return Task(
        description=CURRENCY_SAFETY_TASK_DESC.format(
            destination_country=destination_country
        ),
        agent=agent,
        expected_output="Practical currency exchange tips, safety warnings, and scam prevention advice"
    )


def create_comprehensive_currency_task(
    agent,
    destination_country: str,
    base_currency: str
) -> Task:
    """
    Create task for generating comprehensive currency guide.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name
        base_currency: Traveler's base currency code

    Returns:
        CrewAI Task for comprehensive currency guide
    """
    return Task(
        description=COMPREHENSIVE_CURRENCY_TASK_DESC.format(
            destination_country=destination_country,
            base_currency=base_currency
        ),
        agent=agent,
        expected_output="Complete currency and financial guide in JSON format matching CurrencyAgentOutput schema"
    )
