"""
Country Agent CrewAI Tasks

Defines CrewAI tasks for country information gathering and analysis.
"""

from crewai import Task
from .models import CountryAgentInput
from .prompts import (
    RESEARCH_TASK_PROMPT,
    VERIFICATION_TASK_PROMPT,
    PRACTICAL_INFO_TASK_PROMPT,
    COMPREHENSIVE_INFO_TASK_PROMPT,
)


def create_country_research_task(agent, input_data: CountryAgentInput) -> Task:
    """
    Create a research task for gathering country information.

    Args:
        agent: CrewAI agent
        input_data: Country Agent input parameters

    Returns:
        CrewAI Task for country research
    """
    description = RESEARCH_TASK_PROMPT.format(
        destination_country=input_data.destination_country,
        departure_date=input_data.departure_date.isoformat(),
        return_date=input_data.return_date.isoformat(),
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="JSON object with comprehensive country information including basic facts, emergency services, power standards, and safety data",
    )


def create_country_verification_task(agent, input_data: CountryAgentInput) -> Task:
    """
    Create a verification task for validating country information.

    Args:
        agent: CrewAI agent
        input_data: Country Agent input parameters

    Returns:
        CrewAI Task for information verification
    """
    description = VERIFICATION_TASK_PROMPT.format(
        destination_country=input_data.destination_country,
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="Validated JSON object with verified country data and confidence score",
    )


def create_practical_info_task(agent, input_data: CountryAgentInput) -> Task:
    """
    Create a task for gathering practical travel information.

    Args:
        agent: CrewAI agent
        input_data: Country Agent input parameters

    Returns:
        CrewAI Task for practical information
    """
    description = PRACTICAL_INFO_TASK_PROMPT.format(
        destination_country=input_data.destination_country,
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="JSON object with practical travel tips, notable facts, and actionable information",
    )


def create_comprehensive_country_task(agent, input_data: CountryAgentInput) -> Task:
    """
    Create a single comprehensive task for complete country intelligence.

    This is the recommended task for most use cases.

    Args:
        agent: CrewAI agent
        input_data: Country Agent input parameters

    Returns:
        CrewAI Task for comprehensive country analysis
    """
    description = COMPREHENSIVE_INFO_TASK_PROMPT.format(
        destination_country=input_data.destination_country,
        departure_date=input_data.departure_date.isoformat(),
        return_date=input_data.return_date.isoformat(),
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="""Complete CountryAgentOutput JSON with:
- Basic country profile (name, capital, region, population, area)
- Communication details (languages, time zones)
- Emergency services (comprehensive contact list)
- Infrastructure (power, driving, currency)
- Safety assessment (rating, advisories)
- Travel tips (notable facts, best time to visit)
- Confidence score and source references""",
    )
