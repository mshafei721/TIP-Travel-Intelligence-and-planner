"""Tests for Settings API endpoints"""

import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


# Mock the JWT verification
def mock_verify_jwt_token():
    return {"user_id": "test-user-123", "email": "test@example.com"}


class TestUserSettingsEndpoints:
    """Tests for user settings CRUD endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked auth"""
        from app.main import app
        from app.core.auth import verify_jwt_token

        app.dependency_overrides[verify_jwt_token] = mock_verify_jwt_token
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        with patch("app.api.settings.supabase") as mock:
            mock_response = MagicMock()
            mock_response.data = {
                "id": "test-user-123",
                "preferences": {
                    "settings": {
                        "appearance": {
                            "theme": "dark",
                            "language": "en",
                            "timezone": "UTC",
                            "date_format": "MM/DD/YYYY",
                            "currency": "USD",
                            "units": "metric",
                        },
                        "notifications": {
                            "email_notifications": True,
                            "email_trip_updates": True,
                            "push_notifications": False,
                        },
                        "privacy": {
                            "profile_visibility": "private",
                            "analytics_opt_in": True,
                        },
                        "ai_preferences": {
                            "ai_temperature": 0.7,
                            "preferred_detail_level": "balanced",
                        },
                    }
                },
            }

            mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
                mock_response
            )
            mock.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                MagicMock(data=[mock_response.data])
            )

            yield mock, mock_response

    def test_get_all_settings_success(self, client, mock_supabase):
        """Test successful retrieval of all settings"""
        mock, mock_response = mock_supabase

        response = client.get(
            "/api/settings",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "appearance" in data["data"]
        assert "notifications" in data["data"]
        assert "privacy" in data["data"]
        # Note: API returns camelCase aliases
        assert "aiPreferences" in data["data"]

    def test_get_all_settings_with_defaults(self, client, mock_supabase):
        """Test settings retrieval with default values"""
        mock, mock_response = mock_supabase
        # Set empty preferences to test default values
        mock_response.data = {"id": "test-user-123", "preferences": {}}

        response = client.get(
            "/api/settings",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        # Should return default values
        # Note: API returns camelCase aliases
        assert data["data"]["appearance"]["theme"] == "system"
        assert data["data"]["notifications"]["emailNotifications"] is True

    def test_update_all_settings_success(self, client, mock_supabase):
        """Test successful update of settings"""
        mock, mock_response = mock_supabase

        response = client.put(
            "/api/settings",
            json={
                "appearance": {"theme": "dark"},
                "notifications": {"email_notifications": False},
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_settings_user_not_found(self, client, mock_supabase):
        """Test settings retrieval with non-existent user"""
        mock, mock_response = mock_supabase
        mock_response.data = None

        response = client.get(
            "/api/settings",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 404


class TestAppearanceSettings:
    """Tests for appearance settings endpoints"""

    @pytest.fixture
    def client(self):
        from app.main import app
        from app.core.auth import verify_jwt_token

        app.dependency_overrides[verify_jwt_token] = mock_verify_jwt_token
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_supabase(self):
        with patch("app.api.settings.supabase") as mock:
            mock_response = MagicMock()
            mock_response.data = {
                "preferences": {
                    "settings": {
                        "appearance": {
                            "theme": "dark",
                            "language": "en",
                            "timezone": "America/New_York",
                            "date_format": "MM/DD/YYYY",
                            "currency": "USD",
                            "units": "metric",
                        }
                    }
                }
            }

            mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
                mock_response
            )
            mock.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                MagicMock(data=[mock_response.data])
            )

            yield mock, mock_response

    def test_get_appearance_settings(self, client, mock_supabase):
        """Test get appearance settings"""
        response = client.get(
            "/api/settings/appearance",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["theme"] == "dark"

    def test_update_appearance_settings(self, client, mock_supabase):
        """Test update appearance settings"""
        response = client.put(
            "/api/settings/appearance",
            json={"theme": "light", "timezone": "Europe/London"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200


class TestNotificationSettings:
    """Tests for notification settings endpoints"""

    @pytest.fixture
    def client(self):
        from app.main import app
        from app.core.auth import verify_jwt_token

        app.dependency_overrides[verify_jwt_token] = mock_verify_jwt_token
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_supabase(self):
        with patch("app.api.settings.supabase") as mock:
            mock_response = MagicMock()
            mock_response.data = {
                "preferences": {
                    "settings": {
                        "notifications": {
                            "email_notifications": True,
                            "email_trip_updates": True,
                            "email_report_completion": True,
                            "push_notifications": False,
                        }
                    }
                }
            }

            mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
                mock_response
            )
            mock.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                MagicMock(data=[mock_response.data])
            )

            yield mock, mock_response

    def test_get_notification_settings(self, client, mock_supabase):
        """Test get notification settings"""
        response = client.get(
            "/api/settings/notifications",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Note: API returns camelCase aliases
        assert data["data"]["emailNotifications"] is True

    def test_update_notification_settings(self, client, mock_supabase):
        """Test update notification settings"""
        response = client.put(
            "/api/settings/notifications",
            json={"email_notifications": False, "push_notifications": True},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200


class TestPrivacySettings:
    """Tests for privacy settings endpoints"""

    @pytest.fixture
    def client(self):
        from app.main import app
        from app.core.auth import verify_jwt_token

        app.dependency_overrides[verify_jwt_token] = mock_verify_jwt_token
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_supabase(self):
        with patch("app.api.settings.supabase") as mock:
            mock_response = MagicMock()
            mock_response.data = {
                "preferences": {
                    "settings": {
                        "privacy": {
                            "profile_visibility": "private",
                            "show_travel_history": False,
                            "allow_template_sharing": True,
                            "analytics_opt_in": True,
                        }
                    }
                }
            }

            mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
                mock_response
            )
            mock.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                MagicMock(data=[mock_response.data])
            )

            yield mock, mock_response

    def test_get_privacy_settings(self, client, mock_supabase):
        """Test get privacy settings"""
        response = client.get(
            "/api/settings/privacy",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Note: API returns camelCase aliases
        assert data["data"]["profileVisibility"] == "private"

    def test_update_privacy_settings(self, client, mock_supabase):
        """Test update privacy settings"""
        response = client.put(
            "/api/settings/privacy",
            json={"profile_visibility": "friends", "show_travel_history": True},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200


class TestAIPreferences:
    """Tests for AI preferences endpoints"""

    @pytest.fixture
    def client(self):
        from app.main import app
        from app.core.auth import verify_jwt_token

        app.dependency_overrides[verify_jwt_token] = mock_verify_jwt_token
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_supabase(self):
        with patch("app.api.settings.supabase") as mock:
            mock_response = MagicMock()
            mock_response.data = {
                "preferences": {
                    "settings": {
                        "ai_preferences": {
                            "ai_temperature": 0.7,
                            "preferred_detail_level": "balanced",
                            "include_budget_estimates": True,
                            "include_local_tips": True,
                            "preferred_pace": "balanced",
                        }
                    }
                }
            }

            mock.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
                mock_response
            )
            mock.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                MagicMock(data=[mock_response.data])
            )

            yield mock, mock_response

    def test_get_ai_preferences(self, client, mock_supabase):
        """Test get AI preferences"""
        response = client.get(
            "/api/settings/ai",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Note: API returns camelCase aliases
        assert data["data"]["aiTemperature"] == 0.7

    def test_update_ai_preferences(self, client, mock_supabase):
        """Test update AI preferences"""
        response = client.put(
            "/api/settings/ai",
            json={"ai_temperature": 0.9, "preferred_detail_level": "detailed"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200


class TestDataExport:
    """Tests for data export endpoints"""

    @pytest.fixture
    def client(self):
        from app.main import app
        from app.core.auth import verify_jwt_token

        app.dependency_overrides[verify_jwt_token] = mock_verify_jwt_token
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_supabase(self):
        with patch("app.api.settings.supabase") as mock:
            mock_trips = MagicMock()
            mock_trips.data = [{"id": "trip-1", "title": "Test Trip"}]

            mock_reports = MagicMock()
            mock_reports.data = []

            mock_templates = MagicMock()
            mock_templates.data = []

            mock_profile = MagicMock()
            mock_profile.data = {"preferences": {"settings": {}}}

            # Configure different responses based on table name
            def table_side_effect(table_name):
                mock_table = MagicMock()
                if table_name == "trips":
                    mock_table.select.return_value.eq.return_value.execute.return_value = (
                        mock_trips
                    )
                elif table_name == "report_sections":
                    mock_table.select.return_value.eq.return_value.execute.return_value = (
                        mock_reports
                    )
                elif table_name == "trip_templates":
                    mock_table.select.return_value.eq.return_value.execute.return_value = (
                        mock_templates
                    )
                elif table_name == "user_profiles":
                    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
                        mock_profile
                    )
                return mock_table

            mock.table.side_effect = table_side_effect

            yield mock

    def test_request_data_export_success(self, client, mock_supabase):
        """Test requesting a data export"""
        response = client.post(
            "/api/settings/data/export",
            json={
                "format": "json",
                "include_trips": True,
                "include_reports": True,
                "include_templates": True,
                "include_settings": True,
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Note: API returns camelCase aliases
        assert "exportId" in data
        assert data["status"] == "completed"

    def test_get_export_status(self, client, mock_supabase):
        """Test getting export status"""
        response = client.get(
            "/api/settings/data/export/exp_test123",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200

    def test_delete_all_data_redirects(self, client, mock_supabase):
        """Test that delete data endpoint redirects to profile deletion"""
        response = client.delete(
            "/api/settings/data",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 400


class TestSettingsModels:
    """Tests for settings Pydantic models"""

    def test_theme_enum(self):
        """Test Theme enum values"""
        from app.models.settings import Theme

        assert Theme.LIGHT.value == "light"
        assert Theme.DARK.value == "dark"
        assert Theme.SYSTEM.value == "system"

    def test_profile_visibility_enum(self):
        """Test ProfileVisibility enum values"""
        from app.models.settings import ProfileVisibility

        assert ProfileVisibility.PRIVATE.value == "private"
        assert ProfileVisibility.FRIENDS.value == "friends"
        assert ProfileVisibility.PUBLIC.value == "public"

    def test_appearance_settings_model(self):
        """Test AppearanceSettings model with defaults"""
        from app.models.settings import AppearanceSettings

        settings = AppearanceSettings()

        assert settings.theme.value == "system"
        assert settings.language == "en"
        assert settings.timezone == "UTC"

    def test_appearance_settings_validation(self):
        """Test AppearanceSettings currency validation"""
        from app.models.settings import AppearanceSettings

        settings = AppearanceSettings(currency="eur")
        assert settings.currency == "EUR"  # Should be uppercased

    def test_notification_settings_model(self):
        """Test NotificationSettings model with defaults"""
        from app.models.settings import NotificationSettings

        settings = NotificationSettings()

        assert settings.email_notifications is True
        assert settings.push_notifications is False

    def test_privacy_settings_model(self):
        """Test PrivacySettings model with defaults"""
        from app.models.settings import PrivacySettings, ProfileVisibility

        settings = PrivacySettings()

        assert settings.profile_visibility == ProfileVisibility.PRIVATE
        assert settings.personalization_opt_in is True

    def test_ai_preferences_model(self):
        """Test AIPreferences model with defaults"""
        from app.models.settings import AIPreferences

        settings = AIPreferences()

        assert settings.ai_temperature == 0.7
        assert settings.preferred_detail_level.value == "balanced"
        assert settings.preferred_pace == "balanced"

    def test_ai_preferences_temperature_validation(self):
        """Test AIPreferences temperature validation"""
        from app.models.settings import AIPreferences
        import pytest

        # Valid range
        settings = AIPreferences(ai_temperature=0.5)
        assert settings.ai_temperature == 0.5

        # Invalid - too high
        with pytest.raises(ValueError):
            AIPreferences(ai_temperature=1.5)

        # Invalid - too low
        with pytest.raises(ValueError):
            AIPreferences(ai_temperature=-0.1)

    def test_ai_preferences_pace_validation(self):
        """Test AIPreferences pace validation"""
        from app.models.settings import AIPreferences
        import pytest

        # Valid paces
        for pace in ["relaxed", "balanced", "packed"]:
            settings = AIPreferences(preferred_pace=pace)
            assert settings.preferred_pace == pace

        # Invalid pace
        with pytest.raises(ValueError):
            AIPreferences(preferred_pace="invalid")

    def test_user_settings_complete_model(self):
        """Test UserSettings complete model"""
        from app.models.settings import UserSettings

        settings = UserSettings()

        assert settings.appearance is not None
        assert settings.notifications is not None
        assert settings.privacy is not None
        assert settings.ai_preferences is not None

    def test_data_export_request_model(self):
        """Test DataExportRequest model"""
        from app.models.settings import DataExportRequest

        request = DataExportRequest()

        assert request.format == "json"
        assert request.include_trips is True

    def test_data_export_format_validation(self):
        """Test DataExportRequest format validation"""
        from app.models.settings import DataExportRequest
        import pytest

        # Valid formats
        for fmt in ["json", "csv"]:
            request = DataExportRequest(format=fmt)
            assert request.format == fmt

        # Invalid format
        with pytest.raises(ValueError):
            DataExportRequest(format="xml")
