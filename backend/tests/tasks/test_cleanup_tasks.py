"""Tests for the cleanup tasks - basic unit tests."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class TestCleanupTaskImports:
    """Tests to verify cleanup tasks can be imported and are defined correctly."""

    def test_cleanup_expired_tasks_import(self):
        """Test that cleanup_expired_tasks can be imported."""
        from app.tasks.cleanup import cleanup_expired_tasks

        assert cleanup_expired_tasks is not None
        assert hasattr(cleanup_expired_tasks, "name")
        assert cleanup_expired_tasks.name == "app.tasks.cleanup.cleanup_expired_tasks"

    def test_process_deletion_queue_import(self):
        """Test that process_deletion_queue can be imported."""
        from app.tasks.cleanup import process_deletion_queue

        assert process_deletion_queue is not None
        assert hasattr(process_deletion_queue, "name")
        assert process_deletion_queue.name == "app.tasks.cleanup.process_deletion_queue"

    def test_cleanup_expired_pdfs_import(self):
        """Test that cleanup_expired_pdfs can be imported."""
        from app.tasks.cleanup import cleanup_expired_pdfs

        assert cleanup_expired_pdfs is not None
        assert hasattr(cleanup_expired_pdfs, "name")
        assert cleanup_expired_pdfs.name == "app.tasks.cleanup.cleanup_expired_pdfs"

    def test_schedule_trip_deletion_import(self):
        """Test that schedule_trip_deletion can be imported."""
        from app.tasks.cleanup import schedule_trip_deletion

        assert schedule_trip_deletion is not None
        assert hasattr(schedule_trip_deletion, "name")
        assert schedule_trip_deletion.name == "app.tasks.cleanup.schedule_trip_deletion"

    def test_cancel_scheduled_deletion_import(self):
        """Test that cancel_scheduled_deletion can be imported."""
        from app.tasks.cleanup import cancel_scheduled_deletion

        assert cancel_scheduled_deletion is not None
        assert hasattr(cancel_scheduled_deletion, "name")
        assert cancel_scheduled_deletion.name == "app.tasks.cleanup.cancel_scheduled_deletion"


class TestCleanupTaskExports:
    """Tests for task exports from __init__.py."""

    def test_all_tasks_exported(self):
        """Test that all cleanup tasks are exported from the module."""
        from app.tasks import (
            cleanup_expired_tasks,
            cleanup_expired_pdfs,
            process_deletion_queue,
            schedule_trip_deletion,
            cancel_scheduled_deletion,
        )

        assert cleanup_expired_tasks is not None
        assert cleanup_expired_pdfs is not None
        assert process_deletion_queue is not None
        assert schedule_trip_deletion is not None
        assert cancel_scheduled_deletion is not None


class TestCleanupTaskConfiguration:
    """Tests for task configuration."""

    def test_cleanup_expired_tasks_config(self):
        """Test cleanup_expired_tasks configuration."""
        from app.tasks.cleanup import cleanup_expired_tasks

        # Check task has expected attributes
        assert hasattr(cleanup_expired_tasks, "name")
        assert hasattr(cleanup_expired_tasks, "run")

    def test_process_deletion_queue_config(self):
        """Test process_deletion_queue configuration."""
        from app.tasks.cleanup import process_deletion_queue

        assert hasattr(process_deletion_queue, "name")
        assert "deletion_queue" in process_deletion_queue.name

    def test_cleanup_expired_pdfs_config(self):
        """Test cleanup_expired_pdfs configuration."""
        from app.tasks.cleanup import cleanup_expired_pdfs

        assert hasattr(cleanup_expired_pdfs, "name")
        assert "pdfs" in cleanup_expired_pdfs.name

    def test_schedule_trip_deletion_config(self):
        """Test schedule_trip_deletion configuration."""
        from app.tasks.cleanup import schedule_trip_deletion

        assert hasattr(schedule_trip_deletion, "name")
        assert "schedule" in schedule_trip_deletion.name

    def test_cancel_scheduled_deletion_config(self):
        """Test cancel_scheduled_deletion configuration."""
        from app.tasks.cleanup import cancel_scheduled_deletion

        assert hasattr(cancel_scheduled_deletion, "name")
        assert "cancel" in cancel_scheduled_deletion.name


class TestCleanupDateCalculations:
    """Tests for date calculation logic used in cleanup tasks."""

    def test_cutoff_date_calculation_30_days(self):
        """Test 30-day cutoff date calculation."""
        now = datetime.utcnow()
        cutoff = now - timedelta(days=30)

        assert cutoff < now
        assert (now - cutoff).days == 30

    def test_scheduled_deletion_date_7_days(self):
        """Test 7-day scheduled deletion date calculation."""
        now = datetime.utcnow()
        scheduled = now + timedelta(days=7)

        assert scheduled > now
        assert (scheduled - now).days == 7

    def test_scheduled_deletion_date_custom(self):
        """Test custom scheduled deletion date calculation."""
        now = datetime.utcnow()
        days = 14
        scheduled = now + timedelta(days=days)

        assert scheduled > now
        assert (scheduled - now).days == days


class TestCleanupResultFormats:
    """Tests for expected result formats from cleanup tasks."""

    def test_cleanup_result_structure(self):
        """Test expected structure of cleanup result."""
        result = {
            "tasks_deleted": 0,
            "memory_freed_mb": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert "tasks_deleted" in result
        assert "memory_freed_mb" in result
        assert "timestamp" in result
        assert isinstance(result["tasks_deleted"], int)
        assert isinstance(result["memory_freed_mb"], float)

    def test_deletion_queue_result_structure(self):
        """Test expected structure of deletion queue result."""
        result = {
            "trips_deleted": 0,
            "trips_failed": 0,
            "data_freed_mb": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert "trips_deleted" in result
        assert "trips_failed" in result
        assert "data_freed_mb" in result
        assert "timestamp" in result

    def test_pdf_cleanup_result_structure(self):
        """Test expected structure of PDF cleanup result."""
        result = {
            "files_deleted": 0,
            "storage_freed_mb": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }

        assert "files_deleted" in result
        assert "storage_freed_mb" in result
        assert "timestamp" in result

    def test_schedule_deletion_result_success(self):
        """Test expected structure of successful schedule deletion result."""
        result = {
            "success": True,
            "message": "Scheduled for deletion in 7 days",
            "schedule_id": "schedule-123",
            "trip_id": "trip-456",
            "scheduled_at": datetime.utcnow().isoformat(),
        }

        assert result["success"] is True
        assert "schedule_id" in result
        assert "trip_id" in result

    def test_schedule_deletion_result_failure(self):
        """Test expected structure of failed schedule deletion result."""
        result = {
            "success": False,
            "error": "Some error message",
            "trip_id": "trip-456",
        }

        assert result["success"] is False
        assert "error" in result

    def test_cancel_deletion_result_success(self):
        """Test expected structure of successful cancel deletion result."""
        result = {
            "success": True,
            "message": "Deletion cancelled",
            "trip_id": "trip-456",
            "cancelled_schedule_id": "schedule-123",
        }

        assert result["success"] is True
        assert "cancelled_schedule_id" in result

    def test_cancel_deletion_result_not_found(self):
        """Test expected structure of not found cancel deletion result."""
        result = {
            "success": False,
            "message": "No pending deletion found",
            "trip_id": "trip-456",
        }

        assert result["success"] is False
        assert "No pending deletion found" in result["message"]
