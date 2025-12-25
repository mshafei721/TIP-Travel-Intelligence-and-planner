"""
Pytest configuration and fixtures

This file contains shared fixtures used across all tests.
"""

import pytest
from celery import Celery


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
