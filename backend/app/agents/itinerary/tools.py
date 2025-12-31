"""
Tools for Itinerary Agent

Provides helper functions for itinerary optimization, activity scheduling,
and cost estimation.
"""

from datetime import timedelta
from datetime import date as date_type
from datetime import time as datetime_time

from crewai.tools import tool


@tool("Calculate Trip Duration")
def calculate_trip_duration(departure_date_str: str, return_date_str: str) -> dict:
    """
    Calculate trip duration in days.

    Args:
        departure_date_str: Departure date in ISO format (YYYY-MM-DD)
        return_date_str: Return date in ISO format (YYYY-MM-DD)

    Returns:
        Dictionary with duration information
    """
    try:
        departure = date.fromisoformat(departure_date_str)
        return_date = date.fromisoformat(return_date_str)

        duration = (return_date - departure).days
        full_days = duration  # Including arrival and departure days

        return {
            "total_days": full_days,
            "full_days": max(full_days - 1, 1),  # Exclude travel days if needed
            "nights": duration,
            "departure_date": departure_date_str,
            "return_date": return_date_str,
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_days": 0,
        }


@tool("Estimate Activity Duration")
def estimate_activity_duration(activity_type: str) -> dict:
    """
    Estimate typical duration for different activity types.

    Args:
        activity_type: Type of activity (museum, monument, park, etc.)

    Returns:
        Dictionary with duration estimates
    """
    durations = {
        "museum": {"min": 90, "max": 180, "typical": 120},
        "gallery": {"min": 60, "max": 120, "typical": 90},
        "monument": {"min": 30, "max": 90, "typical": 60},
        "historical_site": {"min": 45, "max": 120, "typical": 75},
        "park": {"min": 60, "max": 180, "typical": 90},
        "garden": {"min": 45, "max": 90, "typical": 60},
        "temple": {"min": 30, "max": 90, "typical": 45},
        "church": {"min": 20, "max": 60, "typical": 30},
        "viewpoint": {"min": 20, "max": 60, "typical": 30},
        "market": {"min": 60, "max": 120, "typical": 90},
        "shopping": {"min": 90, "max": 240, "typical": 120},
        "restaurant": {"min": 60, "max": 120, "typical": 90},
        "cafe": {"min": 30, "max": 60, "typical": 45},
        "show": {"min": 90, "max": 180, "typical": 120},
        "tour": {"min": 120, "max": 240, "typical": 180},
        "beach": {"min": 120, "max": 300, "typical": 180},
        "hiking": {"min": 120, "max": 360, "typical": 180},
        "day_trip": {"min": 360, "max": 600, "typical": 480},
    }

    activity_lower = activity_type.lower()

    for key, value in durations.items():
        if key in activity_lower:
            return {
                "activity_type": activity_type,
                "min_minutes": value["min"],
                "max_minutes": value["max"],
                "typical_minutes": value["typical"],
            }

    # Default for unknown types
    return {
        "activity_type": activity_type,
        "min_minutes": 60,
        "max_minutes": 120,
        "typical_minutes": 90,
    }


@tool("Estimate Transportation Time")
def estimate_transportation_time(distance_km: float, mode: str) -> dict:
    """
    Estimate transportation time based on distance and mode.

    Args:
        distance_km: Distance in kilometers
        mode: Transportation mode (walk, metro, bus, taxi, train, car)

    Returns:
        Dictionary with time and cost estimates
    """
    # Average speeds in km/h
    speeds = {
        "walk": 5,
        "bike": 15,
        "metro": 30,
        "bus": 20,
        "taxi": 25,
        "car": 30,
        "train": 50,
    }

    # Cost per km (approximate, in USD)
    costs_per_km = {
        "walk": 0,
        "bike": 0.1,  # Rental cost
        "metro": 0.5,
        "bus": 0.4,
        "taxi": 1.5,
        "car": 1.0,
        "train": 0.8,
    }

    mode_lower = mode.lower()
    speed = speeds.get(mode_lower, 25)  # Default 25 km/h
    cost_rate = costs_per_km.get(mode_lower, 1.0)

    # Calculate time in minutes
    time_hours = distance_km / speed
    time_minutes = int(time_hours * 60)

    # Add buffer for traffic, waiting, etc.
    buffer_minutes = {
        "walk": 0,
        "bike": 5,
        "metro": 10,
        "bus": 15,
        "taxi": 10,
        "car": 15,
        "train": 20,
    }.get(mode_lower, 10)

    total_minutes = time_minutes + buffer_minutes
    estimated_cost = distance_km * cost_rate

    return {
        "mode": mode,
        "distance_km": distance_km,
        "estimated_minutes": total_minutes,
        "estimated_cost_usd": round(estimated_cost, 2),
        "cost_range": f"${max(1, int(estimated_cost * 0.8))}-${int(estimated_cost * 1.2)}",
    }


@tool("Optimize Daily Schedule")
def optimize_daily_schedule(activities: list[dict]) -> dict:
    """
    Optimize daily activity schedule to minimize travel and maximize enjoyment.

    Args:
        activities: List of activities with locations and priorities

    Returns:
        Optimized schedule with suggestions
    """
    if not activities:
        return {
            "optimized": [],
            "suggestions": ["No activities to optimize"],
        }

    # Simple heuristic: Group by location proximity
    # In production, this would use actual geocoding and routing
    morning_activities = []
    afternoon_activities = []
    evening_activities = []

    suggestions = []

    for activity in activities:
        priority = activity.get("priority", "recommended")
        category = activity.get("category", "")

        # Time-of-day recommendations
        if category in ["museum", "gallery", "historical_site"]:
            morning_activities.append(activity)
            suggestions.append(
                f"Visit {activity.get('name', 'museum')} in the morning to avoid crowds"
            )
        elif category in ["park", "beach", "outdoor"]:
            afternoon_activities.append(activity)
        elif category in ["show", "dining", "nightlife"]:
            evening_activities.append(activity)
        else:
            afternoon_activities.append(activity)

    return {
        "morning": morning_activities,
        "afternoon": afternoon_activities,
        "evening": evening_activities,
        "suggestions": suggestions or ["Activities distributed throughout the day"],
        "total_activities": len(activities),
    }


@tool("Estimate Daily Budget")
def estimate_daily_budget(budget_level: str, destination_type: str = "city") -> dict:
    """
    Estimate daily budget based on budget level and destination type.

    Args:
        budget_level: Budget level (budget, mid-range, luxury)
        destination_type: Type of destination (city, beach, countryside)

    Returns:
        Daily budget breakdown
    """
    # Base costs (in USD per day per person)
    budgets = {
        "budget": {
            "accommodation": 30,
            "meals": 25,
            "activities": 20,
            "transportation": 15,
            "miscellaneous": 10,
        },
        "mid-range": {
            "accommodation": 80,
            "meals": 50,
            "activities": 40,
            "transportation": 25,
            "miscellaneous": 20,
        },
        "luxury": {
            "accommodation": 200,
            "meals": 100,
            "activities": 80,
            "transportation": 50,
            "miscellaneous": 50,
        },
    }

    # Multipliers for destination types
    multipliers = {
        "city": 1.0,
        "beach": 0.9,
        "countryside": 0.8,
        "capital": 1.2,
        "tourist_hotspot": 1.3,
    }

    budget = budgets.get(budget_level, budgets["mid-range"])
    multiplier = multipliers.get(destination_type, 1.0)

    adjusted_budget = {category: int(cost * multiplier) for category, cost in budget.items()}

    total = sum(adjusted_budget.values())

    return {
        "budget_level": budget_level,
        "destination_type": destination_type,
        "daily_breakdown": adjusted_budget,
        "total_per_day": total,
        "total_range": f"${int(total * 0.8)}-${int(total * 1.2)}",
    }


@tool("Generate Meal Suggestions")
def generate_meal_suggestions(destination: str, cuisine_preferences: list[str]) -> dict:
    """
    Generate meal suggestions based on destination and preferences.

    Args:
        destination: Destination city/country
        cuisine_preferences: List of preferred cuisines

    Returns:
        Meal timing and type suggestions
    """
    return {
        "breakfast": {
            "time": "08:00-09:30",
            "suggestions": [
                "Local cafe for authentic breakfast",
                "Hotel breakfast if included",
                "Street food breakfast market",
            ],
            "budget": "$5-$15",
        },
        "lunch": {
            "time": "12:30-14:00",
            "suggestions": [
                "Local restaurant near main activity",
                "Quick cafe or food court",
                "Picnic in park (if weather permits)",
            ],
            "budget": "$10-$25",
        },
        "dinner": {
            "time": "19:00-21:00",
            "suggestions": [
                "Recommended local restaurant",
                "Try traditional cuisine",
                "Rooftop or scenic dining",
            ],
            "budget": "$20-$50",
        },
        "snacks": {
            "budget": "$5-$10 throughout day",
        },
    }
