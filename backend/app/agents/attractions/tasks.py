"""
Attractions Agent Tasks

Defines task creation for the Attractions Agent.
"""

from crewai import Task

from .models import AttractionsAgentInput
from .prompts import ATTRACTIONS_TASK_DESCRIPTION


def create_attractions_task(
    agent, input_data: AttractionsAgentInput
) -> Task:
    """
    Create a CrewAI task for the Attractions Agent.

    Args:
        agent: The CrewAI agent instance
        input_data: AttractionsAgentInput with trip details

    Returns:
        CrewAI Task configured for attractions research
    """
    trip_duration = (input_data.return_date - input_data.departure_date).days
    interests = (
        ", ".join(input_data.interests) if input_data.interests else "general tourism"
    )

    description = ATTRACTIONS_TASK_DESCRIPTION.format(
        destination_city=input_data.destination_city or input_data.destination_country,
        destination_country=input_data.destination_country,
        trip_duration=trip_duration,
        departure_date=input_data.departure_date.isoformat(),
        return_date=input_data.return_date.isoformat(),
        interests=interests,
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="JSON object matching AttractionsAgentOutput schema with comprehensive attractions recommendations",
    )
