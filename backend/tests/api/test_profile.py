"""Tests for profile API endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import date
import uuid

client = TestClient(app)

# Mock JWT token for testing (you'll need to generate valid tokens in real tests)
MOCK_USER_ID = str(uuid.uuid4())
MOCK_AUTH_HEADERS = {
    "Authorization": f"Bearer mock_token_for_{MOCK_USER_ID}"
}


class TestGetProfile:
    """Tests for GET /api/profile"""

    def test_get_profile_authenticated(self, mocker):
        """Should return user profile for authenticated user"""
        # Mock verify_jwt_token to return user_id
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        # Mock Supabase responses
        mock_user_profile = {
            "id": MOCK_USER_ID,
            "display_name": "John Doe",
            "avatar_url": "https://example.com/avatar.jpg",
            "preferences": {},
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }

        mocker.patch(
            'app.core.supabase.supabase.table',
            return_value=mocker.Mock(
                select=mocker.Mock(
                    return_value=mocker.Mock(
                        eq=mocker.Mock(
                            return_value=mocker.Mock(
                                single=mocker.Mock(
                                    return_value=mocker.Mock(
                                        execute=mocker.Mock(
                                            return_value=mocker.Mock(data=mock_user_profile)
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )

        response = client.get("/api/profile", headers=MOCK_AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["id"] == MOCK_USER_ID
        assert data["user"]["display_name"] == "John Doe"

    def test_get_profile_unauthenticated(self):
        """Should return 401 for unauthenticated request"""
        response = client.get("/api/profile")
        assert response.status_code == 401


class TestUpdateProfile:
    """Tests for PUT /api/profile"""

    def test_update_profile_valid_data(self, mocker):
        """Should update profile with valid data"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        update_data = {
            "display_name": "Jane Doe",
            "avatar_url": "https://example.com/new-avatar.jpg"
        }

        mock_response = {
            "id": MOCK_USER_ID,
            "display_name": "Jane Doe",
            "avatar_url": "https://example.com/new-avatar.jpg",
            "preferences": {},
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z"
        }

        mocker.patch(
            'app.core.supabase.supabase.table',
            return_value=mocker.Mock(
                update=mocker.Mock(
                    return_value=mocker.Mock(
                        eq=mocker.Mock(
                            return_value=mocker.Mock(
                                execute=mocker.Mock(
                                    return_value=mocker.Mock(data=[mock_response])
                                )
                            )
                        )
                    )
                )
            )
        )

        response = client.put(
            "/api/profile",
            headers=MOCK_AUTH_HEADERS,
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Jane Doe"

    def test_update_profile_empty_name(self, mocker):
        """Should reject empty display name"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        response = client.put(
            "/api/profile",
            headers=MOCK_AUTH_HEADERS,
            json={"display_name": "   "}
        )
        assert response.status_code == 422  # Validation error


class TestGetTravelerProfile:
    """Tests for GET /api/profile/traveler"""

    def test_get_traveler_profile_exists(self, mocker):
        """Should return traveler profile if it exists"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        mock_traveler_profile = {
            "id": str(uuid.uuid4()),
            "user_id": MOCK_USER_ID,
            "nationality": "US",
            "residency_country": "US",
            "residency_status": "citizen",
            "date_of_birth": "1990-01-01",
            "travel_style": "balanced",
            "dietary_restrictions": ["vegetarian"],
            "accessibility_needs": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }

        mocker.patch(
            'app.core.supabase.supabase.table',
            return_value=mocker.Mock(
                select=mocker.Mock(
                    return_value=mocker.Mock(
                        eq=mocker.Mock(
                            return_value=mocker.Mock(
                                maybe_single=mocker.Mock(
                                    return_value=mocker.Mock(
                                        execute=mocker.Mock(
                                            return_value=mocker.Mock(data=mock_traveler_profile)
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )

        response = client.get("/api/profile/traveler", headers=MOCK_AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["nationality"] == "US"
        assert data["travel_style"] == "balanced"


class TestUpdateTravelerProfile:
    """Tests for PUT /api/profile/traveler"""

    def test_create_traveler_profile(self, mocker):
        """Should create traveler profile if it doesn't exist"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        create_data = {
            "nationality": "US",
            "residency_country": "US",
            "residency_status": "citizen",
            "date_of_birth": "1990-01-01",
            "travel_style": "balanced",
            "dietary_restrictions": ["vegetarian"],
            "accessibility_needs": "None"
        }

        mock_response = {
            "id": str(uuid.uuid4()),
            "user_id": MOCK_USER_ID,
            **create_data,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }

        # Mock: First check returns None (no profile exists)
        # Then insert returns new profile
        mocker.patch(
            'app.core.supabase.supabase.table',
            return_value=mocker.Mock(
                insert=mocker.Mock(
                    return_value=mocker.Mock(
                        execute=mocker.Mock(
                            return_value=mocker.Mock(data=[mock_response])
                        )
                    )
                )
            )
        )

        response = client.put(
            "/api/profile/traveler",
            headers=MOCK_AUTH_HEADERS,
            json=create_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nationality"] == "US"

    def test_update_traveler_profile_invalid_country_code(self, mocker):
        """Should reject invalid country code"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        response = client.put(
            "/api/profile/traveler",
            headers=MOCK_AUTH_HEADERS,
            json={
                "nationality": "USA",  # Invalid: should be 2-letter code
                "residency_country": "US",
                "residency_status": "citizen",
                "travel_style": "balanced"
            }
        )
        assert response.status_code == 422


class TestUpdatePreferences:
    """Tests for PUT /api/profile/preferences"""

    def test_update_preferences(self, mocker):
        """Should update user preferences in JSONB field"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        preferences = {
            "email_notifications": False,
            "push_notifications": True,
            "marketing_emails": False,
            "language": "es",
            "currency": "EUR",
            "units": "metric"
        }

        mock_response = {
            "id": MOCK_USER_ID,
            "display_name": "John Doe",
            "avatar_url": None,
            "preferences": preferences,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z"
        }

        mocker.patch(
            'app.core.supabase.supabase.table',
            return_value=mocker.Mock(
                update=mocker.Mock(
                    return_value=mocker.Mock(
                        eq=mocker.Mock(
                            return_value=mocker.Mock(
                                execute=mocker.Mock(
                                    return_value=mocker.Mock(data=[mock_response])
                                )
                            )
                        )
                    )
                )
            )
        )

        response = client.put(
            "/api/profile/preferences",
            headers=MOCK_AUTH_HEADERS,
            json=preferences
        )
        assert response.status_code == 200
        data = response.json()
        assert data["preferences"]["language"] == "es"
        assert data["preferences"]["currency"] == "EUR"

    def test_update_preferences_invalid_currency(self, mocker):
        """Should reject invalid currency code"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        response = client.put(
            "/api/profile/preferences",
            headers=MOCK_AUTH_HEADERS,
            json={
                "currency": "US"  # Invalid: should be 3-letter code
            }
        )
        assert response.status_code == 422


class TestDeleteAccount:
    """Tests for DELETE /api/profile"""

    def test_delete_account_with_correct_confirmation(self, mocker):
        """Should delete account when confirmation matches"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        mocker.patch(
            'app.core.supabase.supabase.table',
            return_value=mocker.Mock(
                delete=mocker.Mock(
                    return_value=mocker.Mock(
                        eq=mocker.Mock(
                            return_value=mocker.Mock(
                                execute=mocker.Mock(
                                    return_value=mocker.Mock(data=[{"id": MOCK_USER_ID}])
                                )
                            )
                        )
                    )
                )
            )
        )

        response = client.delete(
            "/api/profile",
            headers=MOCK_AUTH_HEADERS,
            json={"confirmation": "DELETE MY ACCOUNT"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Account deleted successfully"

    def test_delete_account_wrong_confirmation(self, mocker):
        """Should reject deletion with wrong confirmation"""
        mocker.patch(
            'app.core.auth.verify_jwt_token',
            return_value={"user_id": MOCK_USER_ID}
        )

        response = client.delete(
            "/api/profile",
            headers=MOCK_AUTH_HEADERS,
            json={"confirmation": "delete"}
        )
        assert response.status_code == 422
