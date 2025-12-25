"""Tests for trip creation and management endpoints"""

from datetime import date, timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest


# Valid trip data fixtures
@pytest.fixture()
def valid_trip_data():
    """Valid trip creation data"""
    return {
        "traveler_details": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "nationality": "US",
            "residence_country": "US",
            "origin_city": "New York",
            "party_size": 2,
            "party_ages": [30, 28],
        },
        "destinations": [{"country": "France", "city": "Paris", "duration_days": 7}],
        "trip_details": {
            "departure_date": (date.today() + timedelta(days=30)).isoformat(),
            "return_date": (date.today() + timedelta(days=40)).isoformat(),
            "budget": 5000.00,
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
    }


@pytest.fixture()
def multi_city_trip_data():
    """Valid multi-city trip data"""
    return {
        "traveler_details": {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "nationality": "GB",
            "residence_country": "GB",
            "origin_city": "London",
            "party_size": 1,
            "party_ages": [35],
        },
        "destinations": [
            {"country": "Italy", "city": "Rome", "duration_days": 5},
            {"country": "Italy", "city": "Florence", "duration_days": 3},
            {"country": "Italy", "city": "Venice", "duration_days": 2},
        ],
        "trip_details": {
            "departure_date": (date.today() + timedelta(days=60)).isoformat(),
            "return_date": (date.today() + timedelta(days=70)).isoformat(),
            "budget": 3000.00,
            "currency": "EUR",
            "trip_purpose": "tourism",
        },
        "preferences": {
            "travel_style": "balanced",
            "interests": ["art", "history", "architecture"],
            "dietary_restrictions": ["vegetarian"],
            "accessibility_needs": [],
            "accommodation_type": "airbnb",
            "transportation_preference": "public",
        },
    }


class TestCreateTrip:
    """Test POST /api/trips - Create new trip"""

    def test_create_trip_valid(self, client, auth_headers, valid_trip_data):
        """Should create trip with valid data"""
        response = client.post("/api/trips", json=valid_trip_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert "user_id" in data
        assert data["status"] == "draft"
        assert "created_at" in data
        assert "updated_at" in data

        # Verify traveler details
        assert data["traveler_details"]["name"] == "John Doe"
        assert data["traveler_details"]["email"] == "john.doe@example.com"
        assert data["traveler_details"]["nationality"] == "US"

        # Verify destinations
        assert len(data["destinations"]) == 1
        assert data["destinations"][0]["country"] == "France"
        assert data["destinations"][0]["city"] == "Paris"

        # Verify trip details
        assert data["trip_details"]["budget"] == 5000.00
        assert data["trip_details"]["currency"] == "USD"

    def test_create_trip_missing_destination(self, client, auth_headers, valid_trip_data):
        """Should reject trip without destination"""
        invalid_data = {**valid_trip_data}
        invalid_data["destinations"] = []

        response = client.post("/api/trips", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422  # Validation error
        assert "destinations" in response.json()["detail"][0]["loc"]

    def test_create_trip_invalid_dates(self, client, auth_headers, valid_trip_data):
        """Should reject trip with return before departure"""
        invalid_data = {**valid_trip_data}
        # Set return date before departure date
        invalid_data["trip_details"]["return_date"] = (
            date.today() + timedelta(days=20)
        ).isoformat()
        invalid_data["trip_details"]["departure_date"] = (
            date.today() + timedelta(days=30)
        ).isoformat()

        response = client.post("/api/trips", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422
        assert "return_date" in str(response.json())

    def test_create_multi_city_trip(self, client, auth_headers, multi_city_trip_data):
        """Should support multiple destinations"""
        response = client.post("/api/trips", json=multi_city_trip_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()

        # Verify all destinations
        assert len(data["destinations"]) == 3
        cities = [dest["city"] for dest in data["destinations"]]
        assert "Rome" in cities
        assert "Florence" in cities
        assert "Venice" in cities

    def test_create_trip_idempotency(self, client, auth_headers, valid_trip_data):
        """Should return same trip for duplicate requests with idempotency key"""
        idempotency_key = str(uuid4())
        headers = {**auth_headers, "X-Idempotency-Key": idempotency_key}

        # First request
        response1 = client.post("/api/trips", json=valid_trip_data, headers=headers)
        assert response1.status_code == 201
        trip_id_1 = response1.json()["id"]

        # Second request with same idempotency key
        response2 = client.post("/api/trips", json=valid_trip_data, headers=headers)
        assert response2.status_code == 201
        trip_id_2 = response2.json()["id"]

        # Should return the same trip
        assert trip_id_1 == trip_id_2

    def test_create_trip_unauthorized(self, client, valid_trip_data):
        """Should reject request without authentication"""
        response = client.post("/api/trips", json=valid_trip_data)
        assert response.status_code == 401  # Unauthorized

    def test_create_trip_invalid_country_code(self, client, auth_headers, valid_trip_data):
        """Should reject invalid country code format"""
        invalid_data = {**valid_trip_data}
        invalid_data["traveler_details"]["nationality"] = "usa"  # Should be uppercase "US"

        response = client.post("/api/trips", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_trip_negative_budget(self, client, auth_headers, valid_trip_data):
        """Should reject negative budget"""
        invalid_data = {**valid_trip_data}
        invalid_data["trip_details"]["budget"] = -100.00

        response = client.post("/api/trips", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_trip_invalid_party_ages(self, client, auth_headers, valid_trip_data):
        """Should reject party_ages > party_size"""
        invalid_data = {**valid_trip_data}
        invalid_data["traveler_details"]["party_size"] = 2
        invalid_data["traveler_details"]["party_ages"] = [
            30,
            28,
            25,
        ]  # 3 ages for 2 people

        response = client.post("/api/trips", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422


class TestUpdateTrip:
    """Test PUT /api/trips/{id} - Update trip"""

    def test_update_trip_success(self, client, auth_headers, valid_trip_data):
        """Should update trip with new data"""
        # Create trip first
        create_response = client.post("/api/trips", json=valid_trip_data, headers=auth_headers)
        trip_id = create_response.json()["id"]

        # Update trip
        update_data = {
            "trip_details": {
                "departure_date": (date.today() + timedelta(days=45)).isoformat(),
                "return_date": (date.today() + timedelta(days=55)).isoformat(),
                "budget": 6000.00,
                "currency": "USD",
                "trip_purpose": "business",
            }
        }

        response = client.put(f"/api/trips/{trip_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Verify updated fields
        assert data["trip_details"]["budget"] == 6000.00
        assert data["trip_details"]["trip_purpose"] == "business"

    def test_update_trip_not_found(self, client, auth_headers):
        """Should return 404 for non-existent trip"""
        fake_trip_id = str(uuid4())
        update_data = {"preferences": {"travel_style": "luxury"}}

        response = client.put(f"/api/trips/{fake_trip_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 404

    def test_update_trip_unauthorized(self, client, valid_trip_data):
        """Should reject update without authentication"""
        response = client.put(
            f"/api/trips/{str(uuid4())}",
            json={"preferences": {"travel_style": "luxury"}},
        )
        assert response.status_code == 401


class TestDeleteTrip:
    """Test DELETE /api/trips/{id} - Delete trip"""

    def test_delete_trip_draft_success(self, client, auth_headers, valid_trip_data):
        """Should delete draft trip"""
        # Create trip
        create_response = client.post("/api/trips", json=valid_trip_data, headers=auth_headers)
        trip_id = create_response.json()["id"]

        # Delete trip
        response = client.delete(f"/api/trips/{trip_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify trip is deleted
        get_response = client.get(f"/api/trips/{trip_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_trip_not_found(self, client, auth_headers):
        """Should return 404 for non-existent trip"""
        fake_trip_id = str(uuid4())
        response = client.delete(f"/api/trips/{fake_trip_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_trip_unauthorized(self, client):
        """Should reject delete without authentication"""
        response = client.delete(f"/api/trips/{str(uuid4())}")
        assert response.status_code == 401


class TestGenerateReport:
    """Test POST /api/trips/{id}/generate - Start AI report generation"""

    @patch("app.tasks.agent_jobs.execute_orchestrator")
    def test_generate_report_queues_task(
        self, mock_orchestrator, client, auth_headers, valid_trip_data
    ):
        """Should queue Celery task for report generation"""
        # Create trip
        create_response = client.post("/api/trips", json=valid_trip_data, headers=auth_headers)
        trip_id = create_response.json()["id"]

        # Mock Celery task
        mock_task = Mock()
        mock_task.id = "task-123"
        mock_orchestrator.delay.return_value = mock_task

        # Generate report
        response = client.post(f"/api/trips/{trip_id}/generate", headers=auth_headers)
        assert response.status_code == 202
        data = response.json()

        # Verify response
        assert data["status"] == "queued"
        assert data["task_id"] == "task-123"
        assert "message" in data

        # Verify task was queued
        mock_orchestrator.delay.assert_called_once_with(trip_id)


class TestGetGenerationStatus:
    """Test GET /api/trips/{id}/status - Get generation status"""

    def test_get_generation_status(self, client, auth_headers, valid_trip_data):
        """Should return current generation status"""
        # Create trip
        create_response = client.post("/api/trips", json=valid_trip_data, headers=auth_headers)
        trip_id = create_response.json()["id"]

        # Get status
        response = client.get(f"/api/trips/{trip_id}/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # Verify status structure
        assert "status" in data
        assert "progress" in data
        assert "current_agent" in data
        assert "agents_completed" in data
        assert "agents_failed" in data
        assert data["status"] == "draft"  # Initial status


class TestDraftManagement:
    """Test draft management endpoints"""

    def test_save_draft(self, client, auth_headers):
        """Should save partial trip as draft"""
        partial_data = {
            "traveler_details": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "nationality": "US",
                "residence_country": "US",
                "origin_city": "New York",
                "party_size": 1,
                "party_ages": [],
            }
        }

        response = client.post("/api/trips/drafts", json=partial_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert "draft_data" in data
        assert data["draft_data"]["traveler_details"]["name"] == "John Doe"

    def test_resume_from_draft(self, client, auth_headers):
        """Should load draft into form"""
        # Save draft
        partial_data = {
            "traveler_details": {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "nationality": "GB",
                "residence_country": "GB",
                "origin_city": "London",
                "party_size": 1,
                "party_ages": [],
            },
            "destinations": [{"country": "Spain", "city": "Barcelona", "duration_days": 5}],
        }

        create_response = client.post("/api/trips/drafts", json=partial_data, headers=auth_headers)
        draft_id = create_response.json()["id"]

        # Get drafts
        response = client.get("/api/trips/drafts", headers=auth_headers)
        assert response.status_code == 200
        drafts = response.json()

        assert len(drafts) > 0
        draft = next(d for d in drafts if d["id"] == draft_id)
        assert draft["draft_data"]["destinations"][0]["city"] == "Barcelona"

    def test_update_draft(self, client, auth_headers):
        """Should update existing draft"""
        # Create draft
        initial_data = {
            "traveler_details": {
                "name": "Test User",
                "email": "test@example.com",
                "nationality": "US",
                "residence_country": "US",
                "origin_city": "NYC",
                "party_size": 1,
                "party_ages": [],
            }
        }
        create_response = client.post("/api/trips/drafts", json=initial_data, headers=auth_headers)
        draft_id = create_response.json()["id"]

        # Update draft
        update_data = {"destinations": [{"country": "Japan", "city": "Tokyo", "duration_days": 7}]}
        response = client.put(
            f"/api/trips/drafts/{draft_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["draft_data"]["destinations"][0]["city"] == "Tokyo"

    def test_delete_draft(self, client, auth_headers):
        """Should delete draft"""
        # Create draft
        draft_data = {
            "traveler_details": {
                "name": "Delete Me",
                "email": "delete@example.com",
                "nationality": "US",
                "residence_country": "US",
                "origin_city": "NYC",
                "party_size": 1,
                "party_ages": [],
            }
        }
        create_response = client.post("/api/trips/drafts", json=draft_data, headers=auth_headers)
        draft_id = create_response.json()["id"]

        # Delete draft
        response = client.delete(f"/api/trips/drafts/{draft_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get("/api/trips/drafts", headers=auth_headers)
        drafts = get_response.json()
        assert not any(d["id"] == draft_id for d in drafts)
