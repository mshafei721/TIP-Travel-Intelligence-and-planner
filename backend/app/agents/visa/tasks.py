"""
Visa Agent CrewAI Tasks

Defines the tasks that the Visa Agent executes using CrewAI.
Tasks are structured workflows that use the agent's tools to gather and analyze visa information.
"""

from crewai import Task
from .prompts import (
    VISA_RESEARCH_TASK_PROMPT,
    VISA_VERIFICATION_TASK_PROMPT,
)


def create_visa_research_task(agent, input_data) -> Task:
    """
    Create the main visa research task

    This task uses the visa_check_tool and other tools to gather
    comprehensive visa requirements for the trip.

    Args:
        agent: The CrewAI Agent instance
        input_data: VisaAgentInput with trip details

    Returns:
        Task: CrewAI Task for visa research
    """
    description = VISA_RESEARCH_TASK_PROMPT.format(
        user_nationality=input_data.user_nationality,
        destination_country=input_data.destination_country,
        destination_city=input_data.destination_city,
        trip_purpose=input_data.trip_purpose,
        duration_days=input_data.duration_days,
        departure_date=input_data.departure_date.isoformat(),
    )

    return Task(
        description=description,
        agent=agent,
        expected_output="""
        A comprehensive visa requirements report including:
        1. Visa requirement status (required/not required)
        2. Visa type and category
        3. Maximum stay duration
        4. Application process details
        5. Required documents list
        6. Processing time and costs
        7. Entry requirements (passport validity, vaccinations, etc.)
        8. Practical tips for travelers
        9. Important warnings
        10. Source references with URLs

        Return as JSON matching VisaAgentOutput schema.
        """,
    )


def create_visa_verification_task(agent, research_result) -> Task:
    """
    Create the verification task

    This task verifies and enhances the initial research,
    cross-checks sources, and calculates final confidence scores.

    Args:
        agent: The CrewAI Agent instance
        research_result: Results from the research task

    Returns:
        Task: CrewAI Task for verification
    """
    description = VISA_VERIFICATION_TASK_PROMPT.format(initial_research=research_result)

    return Task(
        description=description,
        agent=agent,
        expected_output="""
        A verified and enhanced visa requirements report with:
        1. Verified visa requirement determination
        2. Cross-checked application process details
        3. Validated document requirements
        4. Enhanced practical tips
        5. Critical warnings identified
        6. Confidence score (0.0 - 1.0)
        7. All source references verified

        Return as JSON matching VisaAgentOutput schema.
        """,
    )


def create_single_step_task(agent, input_data) -> Task:
    """
    Create a simplified single-step task (for MVP or testing)

    This combines research and verification into one task.
    Use this for faster execution when verification isn't critical.

    Args:
        agent: The CrewAI Agent instance
        input_data: VisaAgentInput with trip details

    Returns:
        Task: CrewAI Task for single-step visa analysis
    """
    description = f"""
    Analyze visa requirements for this trip:

    Traveler: {input_data.user_nationality} national
    Destination: {input_data.destination_country} ({input_data.destination_city})
    Purpose: {input_data.trip_purpose}
    Duration: {input_data.duration_days} days
    Departure: {input_data.departure_date}

    Steps:
    1. Check visa requirements using check_visa_requirements tool
    2. Determine if visa is required
    3. Identify visa type and maximum stay
    4. Generate document checklist using generate_document_checklist tool
    5. Estimate processing time using estimate_processing_time tool
    6. Provide practical tips and warnings
    7. Include all source references

    Return comprehensive visa intelligence as JSON.
    """

    return Task(
        description=description,
        agent=agent,
        expected_output="Complete visa requirements report as JSON matching VisaAgentOutput schema",
    )
