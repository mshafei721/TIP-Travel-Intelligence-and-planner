"""Tests for the feedback API endpoint"""

import pytest
from unittest.mock import patch, MagicMock


class TestFeedbackAPI:
    """Test cases for feedback API"""

    def test_feedback_create_schema(self):
        """Test FeedbackCreate schema validation"""
        from app.api.feedback import FeedbackCreate, FeedbackType

        # Valid feedback
        feedback = FeedbackCreate(
            type=FeedbackType.BUG,
            title="Test bug report",
            description="This is a test bug report with enough description.",
            email="test@example.com",
            route="/test/route",
        )

        assert feedback.type == FeedbackType.BUG
        assert feedback.title == "Test bug report"
        assert feedback.email == "test@example.com"

    def test_feedback_type_enum(self):
        """Test FeedbackType enum values"""
        from app.api.feedback import FeedbackType

        assert FeedbackType.BUG.value == "bug"
        assert FeedbackType.FEATURE.value == "feature"

    def test_feedback_response_schema(self):
        """Test FeedbackResponse schema"""
        from app.api.feedback import FeedbackResponse, FeedbackType
        from datetime import datetime

        response = FeedbackResponse(
            id="test-uuid",
            type=FeedbackType.BUG,
            title="Test bug",
            description="Test description",
            status="new",
            created_at=datetime.now(),
        )

        assert response.id == "test-uuid"
        assert response.status == "new"

    def test_feedback_create_requires_title(self):
        """Test that title is required"""
        from pydantic import ValidationError
        from app.api.feedback import FeedbackCreate, FeedbackType

        with pytest.raises(ValidationError):
            FeedbackCreate(
                type=FeedbackType.BUG,
                title="",  # Empty title should fail
                description="This is a valid description.",
            )

    def test_feedback_create_requires_description(self):
        """Test that description is required and has min length"""
        from pydantic import ValidationError
        from app.api.feedback import FeedbackCreate, FeedbackType

        with pytest.raises(ValidationError):
            FeedbackCreate(
                type=FeedbackType.BUG,
                title="Valid title",
                description="Short",  # Too short
            )


class TestOptionalJWTToken:
    """Test cases for optional_jwt_token dependency"""

    def test_optional_jwt_returns_none_without_header(self):
        """Test that optional_jwt_token returns None without authorization header"""
        from app.core.auth import optional_jwt_token
        from unittest.mock import MagicMock

        request = MagicMock()
        request.state = MagicMock()

        result = optional_jwt_token(request, authorization=None)

        assert result is None

    def test_optional_jwt_returns_none_with_invalid_format(self):
        """Test that optional_jwt_token returns None with invalid format"""
        from app.core.auth import optional_jwt_token
        from unittest.mock import MagicMock

        request = MagicMock()
        request.state = MagicMock()

        result = optional_jwt_token(request, authorization="InvalidFormat")

        assert result is None

    def test_optional_jwt_returns_none_with_wrong_scheme(self):
        """Test that optional_jwt_token returns None with wrong scheme"""
        from app.core.auth import optional_jwt_token
        from unittest.mock import MagicMock

        request = MagicMock()
        request.state = MagicMock()

        result = optional_jwt_token(request, authorization="Basic sometoken")

        assert result is None
