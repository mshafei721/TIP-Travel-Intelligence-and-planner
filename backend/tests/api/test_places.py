"""
Tests for Places API endpoints.

Tests place search functionality for itinerary building.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def client():
    """FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture
def mock_auth(mocker):
    """Mock authentication."""
    user_id = str(uuid.uuid4())
    mocker.patch(
        "app.core.auth.verify_jwt_token",
        return_value={"user_id": user_id},
    )
    return {"Authorization": "Bearer mock_token"}


@pytest.fixture
def sample_opentripmap_response():
    """Sample response from OpenTripMap API."""
    return {
        "features": [
            {
                "properties": {
                    "xid": "Q625",
                    "name": "Tokyo Tower",
                },
            },
            {
                "properties": {
                    "xid": "Q219761",
                    "name": "Senso-ji",
                },
            },
        ]
    }


@pytest.fixture
def sample_place_detail():
    """Sample place detail from OpenTripMap."""
    return {
        "xid": "Q625",
        "name": "Tokyo Tower",
        "address": {
            "road": "4-2-8 Shibakoen",
            "city": "Minato",
            "country": "Japan",
        },
        "point": {"lat": 35.6586, "lon": 139.7454},
        "kinds": "towers,interesting_places",
        "rate": "3h",
        "preview": {"source": "https://example.com/tokyo-tower.jpg"},
    }


# ============================================================================
# GET /places/search Tests
# ============================================================================


class TestPlaceSearch:
    """Tests for GET /places/search endpoint."""

    def test_search_returns_sample_data_without_api_key(self, client, mock_auth, mocker):
        """Should return sample data when API key is not configured."""
        # Ensure no API key is set
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": "museum"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_count" in data
        assert len(data["results"]) > 0

    def test_search_with_location(self, client, mock_auth, mocker):
        """Should geocode location when provided."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": "temple", "location": "Tokyo, Japan"},
        )

        assert response.status_code == 200

    def test_search_with_coordinates(self, client, mock_auth, mocker):
        """Should use provided coordinates."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": "restaurant", "lat": 35.6762, "lng": 139.6503},
        )

        assert response.status_code == 200

    def test_search_with_type_filter(self, client, mock_auth, mocker):
        """Should filter by place type."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": "food", "type": "restaurant"},
        )

        assert response.status_code == 200

    def test_search_with_custom_radius(self, client, mock_auth, mocker):
        """Should accept custom radius."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": "park", "radius_km": 5},
        )

        assert response.status_code == 200

    def test_search_validates_query_length(self, client, mock_auth):
        """Should reject empty query."""
        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": ""},
        )

        assert response.status_code == 422

    def test_search_validates_radius_range(self, client, mock_auth):
        """Should reject invalid radius."""
        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": "test", "radius_km": 100},  # Max is 50
        )

        assert response.status_code == 422

    def test_search_validates_limit(self, client, mock_auth):
        """Should reject invalid limit."""
        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": "test", "limit": 100},  # Max is 50
        )

        assert response.status_code == 422


# ============================================================================
# GET /places/nearby Tests
# ============================================================================


class TestNearbyPlaces:
    """Tests for GET /places/nearby endpoint."""

    def test_nearby_requires_coordinates(self, client, mock_auth):
        """Should require lat and lng parameters."""
        response = client.get(
            "/api/places/nearby",
            headers=mock_auth,
            params={},
        )

        assert response.status_code == 422

    def test_nearby_with_valid_coordinates(self, client, mock_auth, mocker):
        """Should return nearby places."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/nearby",
            headers=mock_auth,
            params={"lat": 35.6762, "lng": 139.6503},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_nearby_with_type_filter(self, client, mock_auth, mocker):
        """Should filter by type."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/nearby",
            headers=mock_auth,
            params={"lat": 35.6762, "lng": 139.6503, "type": "restaurant"},
        )

        assert response.status_code == 200

    def test_nearby_validates_coordinates(self, client, mock_auth):
        """Should validate coordinate ranges."""
        # Invalid latitude
        response = client.get(
            "/api/places/nearby",
            headers=mock_auth,
            params={"lat": 100, "lng": 139.6503},  # Lat must be -90 to 90
        )

        assert response.status_code == 422

        # Invalid longitude
        response = client.get(
            "/api/places/nearby",
            headers=mock_auth,
            params={"lat": 35.6762, "lng": 200},  # Lng must be -180 to 180
        )

        assert response.status_code == 422


# ============================================================================
# GET /places/autocomplete Tests
# ============================================================================


class TestPlaceAutocomplete:
    """Tests for GET /places/autocomplete endpoint."""

    def test_autocomplete_returns_suggestions(self, client, mock_auth, mocker):
        """Should return autocomplete suggestions."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/autocomplete",
            headers=mock_auth,
            params={"query": "tok"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_autocomplete_with_location_context(self, client, mock_auth, mocker):
        """Should use location context for better suggestions."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/autocomplete",
            headers=mock_auth,
            params={"query": "tem", "location": "Kyoto, Japan"},
        )

        assert response.status_code == 200

    def test_autocomplete_validates_query_length(self, client, mock_auth):
        """Should require minimum query length."""
        response = client.get(
            "/api/places/autocomplete",
            headers=mock_auth,
            params={"query": "a"},  # Min length is 2
        )

        assert response.status_code == 422

    def test_autocomplete_respects_limit(self, client, mock_auth, mocker):
        """Should respect limit parameter."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/autocomplete",
            headers=mock_auth,
            params={"query": "tokyo", "limit": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3


# ============================================================================
# Place Result Model Tests
# ============================================================================


class TestPlaceResultTransformation:
    """Tests for place result transformation."""

    def test_place_result_has_required_fields(self, client, mock_auth, mocker):
        """Should include all required fields in results."""
        mocker.patch("app.api.places.OPENTRIPMAP_API_KEY", "")

        response = client.get(
            "/api/places/search",
            headers=mock_auth,
            params={"query": "museum"},
        )

        assert response.status_code == 200
        data = response.json()

        if data["results"]:
            result = data["results"][0]
            assert "place_id" in result
            assert "name" in result
            assert "address" in result
            assert "lat" in result
            assert "lng" in result


# ============================================================================
# Authentication Tests
# ============================================================================


class TestPlacesAuthentication:
    """Tests for places API authentication."""

    def test_search_requires_auth(self, client):
        """Should require authentication."""
        response = client.get(
            "/api/places/search",
            params={"query": "test"},
        )

        # Should fail without auth
        assert response.status_code in [401, 403, 422]

    def test_nearby_requires_auth(self, client):
        """Should require authentication."""
        response = client.get(
            "/api/places/nearby",
            params={"lat": 35.6762, "lng": 139.6503},
        )

        assert response.status_code in [401, 403, 422]

    def test_autocomplete_requires_auth(self, client):
        """Should require authentication."""
        response = client.get(
            "/api/places/autocomplete",
            params={"query": "tokyo"},
        )

        assert response.status_code in [401, 403, 422]
