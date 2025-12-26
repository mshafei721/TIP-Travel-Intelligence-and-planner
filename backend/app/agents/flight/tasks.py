"""
Flight Agent - Task Creation

Functions to create CrewAI tasks for the Flight Agent.
"""

from datetime import date as DateType

from crewai import Agent, Task

from .models import CabinClass, FlightAgentInput
from .prompts import FLIGHT_SEARCH_PROMPT_TEMPLATE


def create_flight_search_task(agent: Agent, agent_input: FlightAgentInput) -> Task:
    """
    Create comprehensive flight search task.

    Args:
        agent: CrewAI Flight Agent
        agent_input: Flight search parameters

    Returns:
        Configured CrewAI Task for flight search
    """
    # Format dates
    departure_str = agent_input.departure_date.strftime("%Y-%m-%d (%A)")
    return_str = (
        agent_input.return_date.strftime("%Y-%m-%d (%A)")
        if agent_input.return_date
        else "One-way trip"
    )

    # Format budget
    budget_info = (
        f"Up to ${agent_input.budget_usd:.2f} per person"
        if agent_input.budget_usd
        else "No strict budget specified"
    )

    # Create task description
    description = FLIGHT_SEARCH_PROMPT_TEMPLATE.format(
        origin_city=agent_input.origin_city,
        destination_city=agent_input.destination_city,
        departure_date=departure_str,
        return_date=return_str,
        passengers=agent_input.passengers,
        cabin_class=agent_input.cabin_class.value,
        budget_info=budget_info,
        direct_only="Yes" if agent_input.direct_flights_only else "No",
        flexible_dates="Yes" if agent_input.flexible_dates else "No",
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="""Valid JSON matching FlightAgentOutput schema with:
        - 3-5 recommended flight options with detailed segments
        - Realistic pricing in USD
        - Airport and transportation information
        - Booking timing and strategy advice
        - Practical travel tips and warnings
        - Confidence scores and data sources""",
    )
