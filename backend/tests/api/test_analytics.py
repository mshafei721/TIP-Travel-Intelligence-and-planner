"""Tests for Analytics API endpoints"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


# Mock the JWT verification
def mock_verify_jwt_token():
    return {"user_id": "test-user-123", "email": "test@example.com"}


class TestUsageAnalytics:
    """Tests for usage analytics endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client with mocked auth"""
        from app.main import app
        from app.core.auth import verify_jwt_token
        from app.api.analytics import router

        app.dependency_overrides[verify_jwt_token] = mock_verify_jwt_token
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        with patch("app.api.analytics.supabase") as mock:
            # Mock trips response
            mock_trips_response = MagicMock()
            mock_trips_response.data = [
                {
                    "id": "trip-1",
                    "status": "completed",
                    "destinations": [
                        {"country": "Japan", "city": "Tokyo", "country_code": "JP"}
                    ],
                    "budget": 3000,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": "trip-2",
                    "status": "draft",
                    "destinations": [
                        {"country": "France", "city": "Paris", "country_code": "FR"}
                    ],
                    "budget": 2500,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                },
            ]

            # Mock agent_jobs response
            mock_jobs_response = MagicMock()
            mock_jobs_response.data = [
                {
                    "id": "job-1",
                    "agent_type": "visa",
                    "status": "completed",
                    "started_at": (datetime.utcnow() - timedelta(seconds=30)).isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": "job-2",
                    "agent_type": "weather",
                    "status": "completed",
                    "started_at": (datetime.utcnow() - timedelta(seconds=15)).isoformat(),
                    "completed_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                },
            ]

            # Setup mock chain
            mock.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                mock_trips_response
            )
            mock.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = (
                mock_trips_response
            )

            yield mock, mock_trips_response, mock_jobs_response

    def test_get_usage_stats_success(self, client, mock_supabase):
        """Test successful usage stats retrieval"""
        mock, mock_trips_response, mock_jobs_response = mock_supabase

        # Configure mock to return different data for trips vs agent_jobs
        def table_side_effect(table_name):
            mock_table = MagicMock()
            if table_name == "trips":
                mock_table.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    mock_trips_response
                )
            elif table_name == "agent_jobs":
                mock_table.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                    mock_jobs_response
                )
            return mock_table

        mock.table.side_effect = table_side_effect

        response = client.get(
            "/api/analytics/usage",
            params={"period": "month"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_trips" in data["data"]
        assert "period" in data["data"]

    def test_get_usage_stats_with_different_periods(self, client, mock_supabase):
        """Test usage stats with different time periods"""
        mock, mock_trips_response, mock_jobs_response = mock_supabase

        mock.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
            mock_trips_response
        )

        for period in ["week", "month", "quarter", "year", "all_time"]:
            response = client.get(
                "/api/analytics/usage",
                params={"period": period},
                headers={"Authorization": "Bearer test-token"},
            )
            assert response.status_code == 200
            assert response.json()["data"]["period"] == period

    def test_get_usage_trends_success(self, client, mock_supabase):
        """Test usage trends endpoint"""
        mock, mock_trips_response, mock_jobs_response = mock_supabase

        mock.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = (
            mock_trips_response
        )
        mock.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = (
            mock_jobs_response
        )

        response = client.get(
            "/api/analytics/usage/trends",
            params={"period": "month"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_agent_usage_stats_success(self, client, mock_supabase):
        """Test agent usage statistics endpoint"""
        mock, _, mock_jobs_response = mock_supabase

        mock.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
            mock_jobs_response
        )

        response = client.get(
            "/api/analytics/usage/agents",
            params={"period": "month"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total_invocations" in data


class TestTripAnalytics:
    """Tests for trip analytics endpoints"""

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
        with patch("app.api.analytics.supabase") as mock:
            mock_response = MagicMock()
            mock_response.data = [
                {
                    "id": "trip-1",
                    "status": "completed",
                    "destinations": [
                        {"country": "Japan", "city": "Tokyo", "country_code": "JP"},
                        {"country": "Japan", "city": "Kyoto", "country_code": "JP"},
                    ],
                    "trip_details": {
                        "budget": 3000,
                        "departureDate": "2025-06-15",
                        "returnDate": "2025-06-22",
                        "tripPurposes": ["Tourism"],
                    },
                    "created_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": "trip-2",
                    "status": "completed",
                    "destinations": [
                        {"country": "France", "city": "Paris", "country_code": "FR"}
                    ],
                    "trip_details": {
                        "budget": 2500,
                        "departureDate": "2025-12-20",
                        "returnDate": "2025-12-27",
                        "tripPurposes": ["Tourism"],
                    },
                    "created_at": datetime.utcnow().isoformat(),
                },
            ]

            mock.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = (
                mock_response
            )
            mock.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.not_.return_value.is_.return_value.execute.return_value = (
                mock_response
            )

            yield mock, mock_response

    def test_get_trip_analytics_success(self, client, mock_supabase):
        """Test successful trip analytics retrieval"""
        mock, mock_response = mock_supabase

        response = client.get(
            "/api/analytics/trips",
            params={"period": "year", "limit_destinations": 10},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "top_destinations" in data["data"]
        assert "unique_countries" in data["data"]

    def test_get_destination_analytics_success(self, client, mock_supabase):
        """Test destination analytics endpoint"""
        mock, mock_response = mock_supabase

        response = client.get(
            "/api/analytics/trips/destinations",
            params={"period": "year", "limit": 20},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_budget_analytics_success(self, client, mock_supabase):
        """Test budget analytics endpoint"""
        mock, mock_response = mock_supabase

        response = client.get(
            "/api/analytics/trips/budgets",
            params={"period": "year"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "budget_ranges" in data["data"]
        assert "average_budget" in data["data"]

    def test_trip_analytics_empty_data(self, client, mock_supabase):
        """Test analytics with no trip data"""
        mock, mock_response = mock_supabase
        mock_response.data = []

        response = client.get(
            "/api/analytics/trips",
            params={"period": "year"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["unique_countries"] == 0


class TestAnalyticsModels:
    """Tests for analytics Pydantic models"""

    def test_date_range_enum(self):
        """Test DateRange enum values"""
        from app.models.analytics import DateRange

        assert DateRange.WEEK.value == "week"
        assert DateRange.MONTH.value == "month"
        assert DateRange.QUARTER.value == "quarter"
        assert DateRange.YEAR.value == "year"
        assert DateRange.ALL_TIME.value == "all_time"

    def test_destination_count_model(self):
        """Test DestinationCount model"""
        from app.models.analytics import DestinationCount

        dest = DestinationCount(
            country="Japan",
            country_code="JP",
            city="Tokyo",
            count=5,
            percentage=25.0,
        )

        assert dest.country == "Japan"
        assert dest.percentage == 25.0

    def test_budget_range_model(self):
        """Test BudgetRange model"""
        from app.models.analytics import BudgetRange

        budget = BudgetRange(
            range_label="$500-1000",
            min_value=500,
            max_value=1000,
            count=8,
            percentage=40.0,
        )

        assert budget.range_label == "$500-1000"
        assert budget.min_value == 500

    def test_usage_stats_model(self):
        """Test UsageStats model with defaults"""
        from app.models.analytics import DateRange, UsageStats

        stats = UsageStats(period=DateRange.MONTH)

        assert stats.period == DateRange.MONTH
        assert stats.total_trips == 0
        assert stats.agents_invoked == {}

    def test_trip_analytics_model(self):
        """Test TripAnalytics model with defaults"""
        from app.models.analytics import DateRange, TripAnalytics

        analytics = TripAnalytics(period=DateRange.YEAR)

        assert analytics.period == DateRange.YEAR
        assert analytics.unique_countries == 0
        assert analytics.top_destinations == []


class TestAnalyticsHelpers:
    """Tests for analytics helper functions"""

    def test_get_date_range_bounds_week(self):
        """Test date range calculation for week"""
        from app.api.analytics import DateRange, get_date_range_bounds

        start, end = get_date_range_bounds(DateRange.WEEK)
        diff = (end - start).days
        assert diff == 7

    def test_get_date_range_bounds_month(self):
        """Test date range calculation for month"""
        from app.api.analytics import DateRange, get_date_range_bounds

        start, end = get_date_range_bounds(DateRange.MONTH)
        diff = (end - start).days
        assert diff == 30

    def test_get_season(self):
        """Test season determination from month"""
        from app.api.analytics import get_season

        assert get_season(3) == "spring"
        assert get_season(6) == "summer"
        assert get_season(9) == "fall"
        assert get_season(12) == "winter"

    def test_calculate_budget_ranges(self):
        """Test budget range calculation"""
        from app.api.analytics import calculate_budget_ranges

        budgets = [250, 750, 1500, 3000, 6000]
        ranges = calculate_budget_ranges(budgets)

        assert len(ranges) > 0
        total_percentage = sum(r.percentage for r in ranges)
        assert abs(total_percentage - 100.0) < 1  # Allow small floating point error

    def test_calculate_budget_ranges_empty(self):
        """Test budget range calculation with no data"""
        from app.api.analytics import calculate_budget_ranges

        ranges = calculate_budget_ranges([])
        assert ranges == []
