"""
AI Agents Package

This package contains the multi-agent system for generating travel intelligence reports.
Each agent specializes in a specific domain (visa, weather, culture, etc.) and follows
a common BaseAgent interface.

Agent Types:
- Orchestrator: Coordinates all sub-agents
- Visa: Visa requirements and entry regulations
- Country: Country information and facts
- Weather: Weather forecasts and climate data
- Currency: Exchange rates and cost of living
- Culture: Cultural tips and etiquette
- Food: Food recommendations and cuisine info
- Attractions: Points of interest
- Itinerary: Day-by-day itinerary generation
- Flight: Flight search and recommendations
"""

from app.agents.base import BaseAgent
from app.agents.config import AgentConfig
from app.agents.interfaces import AgentResult, SourceReference
from app.agents.exceptions import AgentExecutionError

__all__ = [
    "BaseAgent",
    "AgentConfig",
    "AgentResult",
    "SourceReference",
    "AgentExecutionError",
]
