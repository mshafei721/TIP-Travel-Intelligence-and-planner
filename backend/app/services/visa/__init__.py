"""
Visa services package

Includes:
- Travel Buddy AI client (primary visa data source)
- Redis caching layer
- Fallback data sources
"""

from .travel_buddy_client import TravelBuddyClient, VisaCheckResult

__all__ = ["TravelBuddyClient", "VisaCheckResult"]
