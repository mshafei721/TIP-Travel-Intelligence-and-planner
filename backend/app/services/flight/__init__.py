"""
Flight search services.

Provides integration with flight search APIs for finding
flight options, prices, and booking information.
"""

from .amadeus_client import AmadeusFlightClient, FlightOffer, FlightSearchResult

__all__ = ["AmadeusFlightClient", "FlightOffer", "FlightSearchResult"]
