"""
Pytest configuration and fixtures

This file contains shared fixtures used across all tests.
"""

import os

import pytest
from celery import Celery

from app.agents.config import AgentConfig


# ============================================================================
# API Key Detection
# ============================================================================

ANTHROPIC_API_KEY_AVAILABLE = bool(os.getenv("ANTHROPIC_API_KEY"))
WEATHERAPI_KEY_AVAILABLE = bool(os.getenv("WEATHERAPI_KEY"))


def pytest_configure(config):
    """Register custom markers and configure test environment."""
    config.addinivalue_line(
        "markers", "requires_anthropic_key: mark test as requiring ANTHROPIC_API_KEY"
    )
    config.addinivalue_line(
        "markers", "requires_weather_key: mark test as requiring WEATHERAPI_KEY"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically skip integration tests when API keys are not available.

    This ensures CI/CD doesn't fail due to missing API keys while still
    allowing tests to run locally when keys are configured.
    """
    skip_anthropic = pytest.mark.skip(
        reason="ANTHROPIC_API_KEY not set - skipping integration test"
    )
    skip_weather = pytest.mark.skip(
        reason="WEATHERAPI_KEY not set - skipping weather test"
    )

    for item in items:
        # Skip integration tests if no Anthropic key
        if "integration" in item.keywords and not ANTHROPIC_API_KEY_AVAILABLE:
            item.add_marker(skip_anthropic)

        # Skip slow tests if no Anthropic key (they usually need API)
        if "slow" in item.keywords and not ANTHROPIC_API_KEY_AVAILABLE:
            item.add_marker(skip_anthropic)

        # Skip weather-specific tests if no weather key
        if "requires_weather_key" in item.keywords and not WEATHERAPI_KEY_AVAILABLE:
            item.add_marker(skip_weather)


# ============================================================================
# Agent Configuration Fixtures
# ============================================================================


@pytest.fixture
def mock_agent_config():
    """Mock AgentConfig for testing base agent functionality."""
    return AgentConfig(
        agent_type="mock",
        name="Mock Agent",
        description="Mock agent for testing",
        version="1.0.0-test",
        llm_model="claude-3-5-sonnet-20241022",
        temperature=0.1,
        max_tokens=4000,
        verbose=False,
    )


@pytest.fixture
def visa_agent_config():
    """AgentConfig for Visa Agent tests."""
    return AgentConfig(
        agent_type="visa",
        name="Visa Agent",
        description="Visa requirements specialist",
        version="1.0.0",
    )


@pytest.fixture
def country_agent_config():
    """AgentConfig for Country Agent tests."""
    return AgentConfig(
        agent_type="country",
        name="Country Agent",
        description="Country information specialist",
        version="1.0.0",
    )


@pytest.fixture
def attractions_agent_config():
    """AgentConfig for Attractions Agent tests."""
    return AgentConfig(
        agent_type="attractions",
        name="Attractions Agent",
        description="Tourist attractions specialist",
        version="1.0.0",
    )


@pytest.fixture
def weather_agent_config():
    """AgentConfig for Weather Agent tests."""
    return AgentConfig(
        agent_type="weather",
        name="Weather Agent",
        description="Weather forecasting specialist",
        version="1.0.0",
    )


@pytest.fixture
def culture_agent_config():
    """AgentConfig for Culture Agent tests."""
    return AgentConfig(
        agent_type="culture",
        name="Culture Agent",
        description="Cultural information specialist",
        version="1.0.0",
    )


@pytest.fixture
def food_agent_config():
    """AgentConfig for Food Agent tests."""
    return AgentConfig(
        agent_type="food",
        name="Food Agent",
        description="Local cuisine specialist",
        version="1.0.0",
    )


@pytest.fixture
def currency_agent_config():
    """AgentConfig for Currency Agent tests."""
    return AgentConfig(
        agent_type="currency",
        name="Currency Agent",
        description="Currency exchange specialist",
        version="1.0.0",
    )


@pytest.fixture(scope="session")
def celery_config():
    """Celery configuration for testing"""
    return {
        "broker_url": "redis://localhost:6379/1",  # Use DB 1 for tests
        "result_backend": "redis://localhost:6379/1",
        "task_always_eager": True,  # Execute tasks synchronously in tests
        "task_eager_propagates": True,  # Propagate exceptions in eager mode
    }


@pytest.fixture(scope="session")
def celery_app_instance(celery_config):
    """Celery app instance for testing"""
    app = Celery("tip-test")
    app.config_from_object(celery_config)
    return app


@pytest.fixture()
def mock_redis():
    """Mock Redis connection for testing"""
    import fakeredis

    return fakeredis.FakeStrictRedis()


@pytest.fixture()
def sample_trip_data():
    """Sample trip data for testing"""
    return {
        "trip_id": "test-trip-123",
        "user_id": "test-user-456",
        "destination_country": "FR",
        "destination_city": "Paris",
        "user_nationality": "US",
        "trip_purpose": "tourism",
        "duration_days": 14,
        "departure_date": "2025-06-01",
        "traveler_count": 1,
    }


@pytest.fixture()
def sample_visa_input():
    """Sample Visa Agent input for testing"""
    return {
        "trip_id": "test-trip-123",
        "user_nationality": "US",
        "destination_country": "FR",
        "destination_city": "Paris",
        "trip_purpose": "tourism",
        "duration_days": 14,
        "departure_date": "2025-06-01",
        "traveler_count": 1,
    }
