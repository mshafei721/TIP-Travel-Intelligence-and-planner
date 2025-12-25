"""
Culture Agent CrewAI Tasks

Defines tasks for cultural research and etiquette intelligence gathering.
"""

from crewai import Task

from .prompts import (
    COMPREHENSIVE_CULTURE_TASK_DESC,
    CULTURE_DRESS_CODE_TASK_DESC,
    CULTURE_ETIQUETTE_TASK_DESC,
    CULTURE_GREETING_TASK_DESC,
    CULTURE_LANGUAGE_TASK_DESC,
    CULTURE_RELIGIOUS_TASK_DESC,
    CULTURE_TABOOS_TASK_DESC,
)


def create_greeting_task(agent, destination_country: str) -> Task:
    """
    Create task for researching greeting customs and communication norms.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for greeting customs research
    """
    return Task(
        description=CULTURE_GREETING_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Detailed greeting customs, communication styles, and body language norms",
    )


def create_dress_code_task(agent, destination_country: str) -> Task:
    """
    Create task for analyzing dress code expectations.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for dress code research
    """
    return Task(
        description=CULTURE_DRESS_CODE_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Comprehensive dress code guidelines for various contexts",
    )


def create_religious_task(agent, destination_country: str) -> Task:
    """
    Create task for compiling religious considerations.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for religious considerations research
    """
    return Task(
        description=CULTURE_RELIGIOUS_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Religious considerations categorized by severity level",
    )


def create_taboos_task(agent, destination_country: str) -> Task:
    """
    Create task for identifying cultural taboos.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for cultural taboos research
    """
    return Task(
        description=CULTURE_TABOOS_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Cultural taboos with explanations, alternatives, and severity ratings",
    )


def create_etiquette_task(agent, destination_country: str) -> Task:
    """
    Create task for compiling etiquette guidelines.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for etiquette research
    """
    return Task(
        description=CULTURE_ETIQUETTE_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Comprehensive etiquette guidelines for dining, social, and business contexts",
    )


def create_language_task(agent, destination_country: str) -> Task:
    """
    Create task for compiling essential language information.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for language research
    """
    return Task(
        description=CULTURE_LANGUAGE_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Essential phrases with translations, pronunciations, and language tips",
    )


def create_comprehensive_culture_task(agent, destination_country: str) -> Task:
    """
    Create task for generating comprehensive cultural intelligence guide.

    Args:
        agent: CrewAI agent to perform the task
        destination_country: Destination country name

    Returns:
        CrewAI Task for comprehensive cultural guide
    """
    return Task(
        description=COMPREHENSIVE_CULTURE_TASK_DESC.format(destination_country=destination_country),
        agent=agent,
        expected_output="Complete cultural intelligence guide in JSON format matching CultureAgentOutput schema",
    )
