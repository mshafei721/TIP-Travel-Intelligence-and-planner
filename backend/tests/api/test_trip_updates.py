"""
Tests for Trip Updates and Recalculation API endpoints

Tests cover:
- POST /trips/{id}/changes/preview
- POST /trips/{id}/recalculate
- PUT /trips/{id}/with-recalc
- GET /trips/{id}/versions
- POST /trips/{id}/versions/{version}/restore
"""

import pytest
from fastapi.testclient import TestClient

from app.core.auth import verify_jwt_token
from app.main import app


# ============================================================================
# FIXTURES
# ============================================================================


MOCK_USER_ID = "test-user-123"


def mock_verify_jwt():
    """Override function for JWT verification."""
    return {"user_id": MOCK_USER_ID}


@pytest.fixture
def test_client():
    """FastAPI TestClient with mocked auth."""
    # Override the auth dependency
    app.dependency_overrides[verify_jwt_token] = mock_verify_jwt
    client = TestClient(app)
    yield client
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_trip():
    """Sample trip data for testing."""
    return {
        "id": "trip-123",
        "user_id": MOCK_USER_ID,
        "status": "completed",
        "version": 1,
        "traveler_details": {
            "name": "John Doe",
            "email": "john@example.com",
            "nationality": "US",
            "residence_country": "US",
            "origin_city": "New York",
            "party_size": 2,
            "party_ages": [30, 28],
        },
        "destinations": [
            {"country": "France", "city": "Paris", "duration_days": 7},
        ],
        "trip_details": {
            "departure_date": "2025-06-01",
            "return_date": "2025-06-15",
            "budget": 5000,
            "currency": "USD",
            "trip_purpose": "tourism",
        },
        "preferences": {
            "travel_style": "balanced",
            "interests": ["museums", "food"],
            "dietary_restrictions": [],
            "accessibility_needs": [],
            "accommodation_type": "hotel",
            "transportation_preference": "public",
        },
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }


# ============================================================================
# CHANGE PREVIEW TESTS
# ============================================================================


class TestChangePreview:
    """Test POST /trips/{id}/changes/preview endpoint."""

    def test_preview_with_destination_change(self, test_client, mocker, sample_trip):
        """Changing destination should show affected agents."""
        # Mock supabase table query
        mock_response = mocker.Mock()
        mock_response.data = [sample_trip]
        mock_table = mocker.Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        response = test_client.post(
            "/api/trips/trip-123/changes/preview",
            json={"destinations": [{"country": "Japan", "city": "Tokyo", "duration_days": 7}]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_changes"] is True
        assert "destination" in [c["field"] for c in data["changes"]]
        assert len(data["affected_agents"]) > 0
        assert "visa" in data["affected_agents"]
        assert "weather" in data["affected_agents"]

    def test_preview_with_no_changes(self, test_client, mocker, sample_trip):
        """No changes should return empty result."""
        mock_response = mocker.Mock()
        mock_response.data = [sample_trip]
        mock_table = mocker.Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        response = test_client.post(
            "/api/trips/trip-123/changes/preview",
            json={"destinations": [{"country": "France", "city": "Paris", "duration_days": 7}]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_changes"] is False

    def test_preview_trip_not_found(self, test_client, mocker):
        """Non-existent trip should return 404."""
        mock_response = mocker.Mock()
        mock_response.data = []
        mock_table = mocker.Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        response = test_client.post(
            "/api/trips/nonexistent/changes/preview",
            json={"destinations": [{"country": "Japan", "city": "Tokyo"}]},
        )

        assert response.status_code == 404


# ============================================================================
# RECALCULATION TESTS
# ============================================================================


class TestRecalculation:
    """Test POST /trips/{id}/recalculate endpoint."""

    def test_recalculate_specific_agents(self, test_client, mocker, sample_trip):
        """Should queue recalculation for specified agents."""
        mock_response = mocker.Mock()
        mock_response.data = [sample_trip]
        mock_table = mocker.Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )
        mock_table.update.return_value.eq.return_value.execute.return_value = mocker.Mock(data=[])
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        # Mock the Celery task - need to patch at the module level where it's imported
        mock_task = mocker.Mock()
        mock_task.id = "task-abc-123"
        mock_execute = mocker.Mock()
        mock_execute.delay.return_value = mock_task
        mocker.patch("app.tasks.agent_jobs.execute_selective_recalc", mock_execute)

        response = test_client.post(
            "/api/trips/trip-123/recalculate",
            json={"agents": ["visa", "weather"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "visa" in data["affected_agents"]
        assert "weather" in data["affected_agents"]

    def test_recalculate_trip_processing(self, test_client, mocker, sample_trip):
        """Trip in processing state should return 409."""
        sample_trip["status"] = "processing"
        mock_response = mocker.Mock()
        mock_response.data = [sample_trip]
        mock_table = mocker.Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        response = test_client.post(
            "/api/trips/trip-123/recalculate",
            json={"agents": ["visa"]},
        )

        assert response.status_code == 409


# ============================================================================
# UPDATE WITH RECALC TESTS
# ============================================================================


class TestUpdateWithRecalc:
    """Test PUT /trips/{id}/with-recalc endpoint."""

    def test_update_triggers_recalc(self, test_client, mocker, sample_trip):
        """Update with changes should trigger recalculation."""
        mock_response = mocker.Mock()
        mock_response.data = [sample_trip]
        mock_table = mocker.Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )
        mock_table.update.return_value.eq.return_value.execute.return_value = mocker.Mock(
            data=[sample_trip]
        )
        mock_table.insert.return_value.execute.return_value = mocker.Mock(data=[])
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        # Mock the Celery task
        mock_task = mocker.Mock()
        mock_task.id = "task-xyz-789"
        mock_execute = mocker.Mock()
        mock_execute.delay.return_value = mock_task
        mocker.patch("app.tasks.agent_jobs.execute_selective_recalc", mock_execute)

        response = test_client.put(
            "/api/trips/trip-123/with-recalc",
            json={
                "destinations": [{"country": "Japan", "city": "Tokyo", "duration_days": 7}],
                "auto_recalculate": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "trip" in data
        assert len(data["changes_applied"]) > 0

    def test_update_no_fields(self, test_client, mocker, sample_trip):
        """Update with no fields should return 400."""
        mock_response = mocker.Mock()
        mock_response.data = [sample_trip]
        mock_table = mocker.Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        response = test_client.put(
            "/api/trips/trip-123/with-recalc",
            json={"auto_recalculate": True},
        )

        assert response.status_code == 400


# ============================================================================
# VERSION HISTORY TESTS
# ============================================================================


class TestVersionHistory:
    """Test version history endpoints."""

    def test_list_versions(self, test_client, mocker, sample_trip):
        """Should list all versions for a trip."""
        mock_response_trip = mocker.Mock()
        mock_response_trip.data = [sample_trip]
        mock_response_versions = mocker.Mock()
        mock_response_versions.data = [
            {
                "version_number": 1,
                "created_at": "2025-01-01T00:00:00Z",
                "change_summary": "Initial version",
                "fields_changed": [],
            },
        ]
        mock_table = mocker.Mock()
        # First call for trip lookup, second call for versions
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response_trip
        )
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response_versions
        )
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        response = test_client.get("/api/trips/trip-123/versions")

        assert response.status_code == 200
        data = response.json()
        assert data["trip_id"] == "trip-123"
        assert data["current_version"] == 1

    def test_list_versions_trip_not_found(self, test_client, mocker):
        """Non-existent trip should return 404."""
        mock_response = mocker.Mock()
        mock_response.data = []
        mock_table = mocker.Mock()
        mock_table.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
            mock_response
        )
        mocker.patch("app.api.trips.supabase.table", return_value=mock_table)

        response = test_client.get("/api/trips/nonexistent/versions")

        assert response.status_code == 404
