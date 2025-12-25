"""Destination recommendations service"""

from app.core.supabase import supabase

# Popular destinations database (algorithm-based recommendations)
POPULAR_DESTINATIONS = [
    {
        "destination": "Barcelona, Spain",
        "country": "Spain",
        "reason": "Vibrant culture, stunning architecture, and Mediterranean beaches",
        "imageUrl": "/images/destinations/barcelona.jpg",
        "confidence": 0.90,
        "tags": ["culture", "beach", "architecture", "food"],
    },
    {
        "destination": "Seoul, South Korea",
        "country": "South Korea",
        "reason": "Modern technology meets traditional culture with world-class cuisine",
        "imageUrl": "/images/destinations/seoul.jpg",
        "confidence": 0.92,
        "tags": ["culture", "technology", "food", "shopping"],
    },
    {
        "destination": "Reykjavik, Iceland",
        "country": "Iceland",
        "reason": "Unique natural wonders, Northern Lights, and adventure activities",
        "imageUrl": "/images/destinations/reykjavik.jpg",
        "confidence": 0.85,
        "tags": ["adventure", "nature", "photography"],
    },
    {
        "destination": "Lisbon, Portugal",
        "country": "Portugal",
        "reason": "Coastal charm, rich history, vibrant nightlife, and delicious seafood",
        "imageUrl": "/images/destinations/lisbon.jpg",
        "confidence": 0.88,
        "tags": ["culture", "beach", "history", "food"],
    },
    {
        "destination": "Kyoto, Japan",
        "country": "Japan",
        "reason": "Ancient temples, traditional gardens, and authentic Japanese culture",
        "imageUrl": "/images/destinations/kyoto.jpg",
        "confidence": 0.93,
        "tags": ["culture", "history", "nature", "spirituality"],
    },
    {
        "destination": "Cape Town, South Africa",
        "country": "South Africa",
        "reason": "Stunning landscapes, wildlife safaris, and diverse cultural experiences",
        "imageUrl": "/images/destinations/capetown.jpg",
        "confidence": 0.87,
        "tags": ["adventure", "nature", "wildlife", "beach"],
    },
    {
        "destination": "Prague, Czech Republic",
        "country": "Czech Republic",
        "reason": "Fairytale architecture, rich history, and affordable European charm",
        "imageUrl": "/images/destinations/prague.jpg",
        "confidence": 0.86,
        "tags": ["culture", "history", "architecture", "budget"],
    },
    {
        "destination": "Bali, Indonesia",
        "country": "Indonesia",
        "reason": "Tropical paradise with temples, rice terraces, and yoga retreats",
        "imageUrl": "/images/destinations/bali.jpg",
        "confidence": 0.91,
        "tags": ["beach", "culture", "nature", "relaxation"],
    },
    {
        "destination": "Dubai, UAE",
        "country": "United Arab Emirates",
        "reason": "Modern luxury, world-class shopping, and desert adventures",
        "imageUrl": "/images/destinations/dubai.jpg",
        "confidence": 0.84,
        "tags": ["luxury", "shopping", "modern", "adventure"],
    },
    {
        "destination": "Amsterdam, Netherlands",
        "country": "Netherlands",
        "reason": "Picturesque canals, world-class museums, and cycling culture",
        "imageUrl": "/images/destinations/amsterdam.jpg",
        "confidence": 0.89,
        "tags": ["culture", "history", "art", "cycling"],
    },
]


def get_recommendations(user_id: str, limit: int = 3) -> list[dict]:
    """
    Get personalized destination recommendations for a user

    Algorithm (Version 1.0 - Simple):
    1. Fetch user's trip history
    2. Extract visited countries
    3. Filter out destinations in visited countries
    4. Return top N unvisited popular destinations

    Future enhancements:
    - Use ML to analyze user preferences (travel style, interests)
    - Consider similar destinations to user's favorites
    - Factor in budget, season, and travel party size

    Args:
        user_id: User ID to get recommendations for
        limit: Number of recommendations to return (default 3)

    Returns:
        List of recommendation objects with destination, country, reason, imageUrl, confidence, tags
    """
    try:
        # Fetch user's trip history
        response = (
            supabase.table("trips")
            .select("destinations")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .execute()
        )

        trips = response.data if response.data else []

        # Extract visited countries
        visited_countries = set()
        for trip in trips:
            if trip.get("destinations"):
                for dest in trip["destinations"]:
                    country = dest.get("country")
                    if country:
                        visited_countries.add(country)

        # Filter recommendations (exclude visited countries for new experiences)
        recommendations = [
            rec for rec in POPULAR_DESTINATIONS if rec["country"] not in visited_countries
        ]

        # If user has visited all countries, return all recommendations
        if not recommendations:
            recommendations = POPULAR_DESTINATIONS.copy()

        # Sort by confidence score (highest first)
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)

        # Return top N
        return recommendations[:limit]

    except Exception as e:
        print(f"[ERROR] Failed to generate recommendations: {str(e)}")
        # Return default popular destinations on error
        return POPULAR_DESTINATIONS[:limit]


def get_recommendation_by_destination(destination_name: str) -> dict:
    """
    Get detailed recommendation for a specific destination

    Args:
        destination_name: Name of destination (e.g., "Barcelona, Spain")

    Returns:
        Recommendation object or None if not found
    """
    for rec in POPULAR_DESTINATIONS:
        if rec["destination"].lower() == destination_name.lower():
            return rec
    return None
