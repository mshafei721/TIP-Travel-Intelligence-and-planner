"""
Tasks for Itinerary Agent

Defines CrewAI tasks for comprehensive trip itinerary generation.
"""

from crewai import Agent, Task
from datetime import date

from .models import ItineraryAgentInput
from .prompts import ITINERARY_COMPREHENSIVE_TASK


def create_itinerary_task(
    agent: Agent,
    input_data: ItineraryAgentInput,
) -> Task:
    """
    Create comprehensive itinerary generation task.

    Args:
        agent: The CrewAI ItineraryAgent
        input_data: Trip and traveler information

    Returns:
        CrewAI Task configured for itinerary generation
    """
    # Calculate trip duration
    duration_days = (input_data.return_date - input_data.departure_date).days

    # Format age information
    age_info = ""
    if input_data.traveler_ages:
        ages_str = ", ".join(str(age) for age in input_data.traveler_ages)
        age_info = f" (ages: {ages_str})"

    # Format interests
    interests_str = (
        ", ".join(input_data.interests) if input_data.interests else "general sightseeing"
    )

    # Format constraints
    constraints_list = []
    if input_data.mobility_constraints:
        constraints_list.append(f"Mobility: {', '.join(input_data.mobility_constraints)}")
    if input_data.dietary_restrictions:
        constraints_list.append(f"Dietary: {', '.join(input_data.dietary_restrictions)}")
    constraints_str = "\n".join(constraints_list) if constraints_list else "None specified"

    # Format available agent data
    agent_data_summary = _format_agent_data_summary(input_data)

    # Format the task description
    task_description = ITINERARY_COMPREHENSIVE_TASK.format(
        destination_city=input_data.destination_city or "Various cities",
        destination_country=input_data.destination_country,
        duration_days=duration_days,
        departure_date=input_data.departure_date.isoformat(),
        return_date=input_data.return_date.isoformat(),
        group_size=input_data.group_size,
        age_info=age_info,
        budget_level=input_data.budget_level,
        pace=input_data.pace,
        interests=interests_str,
        constraints=constraints_str,
        agent_data_summary=agent_data_summary,
    )

    return Task(
        description=task_description,
        agent=agent,
        expected_output="""A comprehensive JSON object containing:
- daily_plans: Array of detailed day-by-day plans with activities, meals, and transportation
- accommodation_suggestions: List of recommended hotels/accommodations
- total_estimated_cost: Overall trip cost estimate
- cost_breakdown: Breakdown by category
- transportation_plan: Transportation strategy
- optimization_notes: How the itinerary was optimized
- packing_checklist: What to pack
- pro_tips: Insider tips for the destination
- flexible_alternatives: Backup activities for each day

The itinerary should be practical, well-paced, and optimized for the traveler's preferences.""",
    )


def _format_agent_data_summary(input_data: ItineraryAgentInput) -> str:
    """
    Format summary of available agent data.

    Args:
        input_data: Input with optional agent data

    Returns:
        Formatted summary string
    """
    summaries = []

    if input_data.visa_info:
        visa_required = input_data.visa_info.get("visa_required", "unknown")
        summaries.append(f"Visa: {'Required' if visa_required else 'Not required'}")

    if input_data.country_info:
        country_name = input_data.country_info.get("country_name", input_data.destination_country)
        summaries.append(f"Country: {country_name} country intelligence available")

    if input_data.weather_info:
        avg_temp = input_data.weather_info.get("average_temp")
        if avg_temp:
            summaries.append(f"Weather: ~{avg_temp}°C average temperature")

    if input_data.attractions_info:
        top_attractions = input_data.attractions_info.get("top_attractions", [])
        if top_attractions:
            summaries.append(f"Attractions: {len(top_attractions)} top attractions identified")

    if not summaries:
        return "No additional agent data available. Use general destination knowledge."

    return "\n".join(f"- {s}" for s in summaries)
