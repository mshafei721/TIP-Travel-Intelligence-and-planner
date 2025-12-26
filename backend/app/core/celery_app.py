"""
Celery application configuration for async task processing

This module configures Celery for handling background agent jobs,
report generation, and other async operations.

Architecture:
- Redis as message broker and result backend
- Prefork worker pool for CPU-bound agent tasks
- JSON serialization for task arguments and results
- Auto-discovery of tasks from app.tasks module
- Idempotent tasks to prevent duplicate database entries
"""

import logging
from typing import Any

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

logger = logging.getLogger(__name__)

# Transient exceptions that should trigger retry
TRANSIENT_EXCEPTIONS = (
    TimeoutError,
    ConnectionError,
    ConnectionResetError,
    ConnectionRefusedError,
    OSError,  # Network-related OS errors
)

# ==============================================
# Celery Application Instance
# ==============================================

celery_app = Celery(
    "tip",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"],  # Auto-discover tasks
)

# ==============================================
# Celery Configuration
# ==============================================

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task routing and execution
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    task_acks_late=True,  # Acknowledge after task completion
    worker_prefetch_multiplier=1,  # One task per worker at a time
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Store task args/kwargs with results
    # Worker settings
    worker_send_task_events=True,  # Send task events for monitoring
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (prevent memory leaks)
    # Retry settings
    task_default_retry_delay=60,  # Retry after 1 minute
    task_max_retries=3,
    # Task priority (0-9, lower = higher priority)
    task_default_priority=5,
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-expired-tasks": {
            "task": "app.tasks.cleanup.cleanup_expired_tasks",
            "schedule": crontab(hour=2, minute=0),  # Run at 2 AM daily
        },
        "process-deletion-queue": {
            "task": "app.tasks.cleanup.process_deletion_queue",
            "schedule": crontab(hour=3, minute=0),  # Run at 3 AM daily
        },
    },
)

# ==============================================
# Task Base Class
# ==============================================


class BaseTipTask(celery_app.Task):
    """
    Base task class with common error handling and logging

    All TIP tasks should inherit from this class to get:
    - Automatic retry on TRANSIENT failures only
    - Structured logging
    - Error reporting to Sentry (when configured)

    IMPORTANT: Only transient errors (network, timeout) trigger retry.
    Non-transient errors (validation, business logic) should NOT retry
    as they will fail again with the same input.
    """

    # Only retry on transient errors - not all exceptions!
    autoretry_for = TRANSIENT_EXCEPTIONS
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes between retries
    retry_jitter = True  # Add randomness to retry delays

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failures"""
        logger.error(
            f"Task {self.name} failed",
            extra={
                "task_id": task_id,
                "exception": str(exc),
                "exception_type": type(exc).__name__,
            },
            exc_info=True,
        )
        # Try Sentry integration
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(exc)
        except ImportError:
            pass
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Log task successes"""
        logger.info(f"Task {self.name} succeeded", extra={"task_id": task_id})
        super().on_success(retval, task_id, args, kwargs)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log task retries"""
        logger.warning(
            f"Task {self.name} retrying",
            extra={
                "task_id": task_id,
                "exception": str(exc),
                "retry_count": self.request.retries,
            },
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)


class IdempotentTipTask(BaseTipTask):
    """
    Base task class for idempotent operations.

    Use this for tasks that insert data to the database.
    Ensures the same task execution with the same ID won't
    create duplicate entries.

    Usage:
        @shared_task(bind=True, base=IdempotentTipTask)
        def my_task(self, trip_id: str):
            # Check if already processed using task_id or trip_id
            if is_already_processed(trip_id, self.request.id):
                return existing_result
            # Otherwise process and store
            result = do_work()
            store_result(trip_id, self.request.id, result)
            return result
    """

    def before_start(self, task_id: str, args: tuple, kwargs: dict) -> None:
        """
        Called before task starts.
        Can be overridden to check for existing results.
        """
        logger.debug(f"Starting idempotent task {self.name}", extra={"task_id": task_id})
        super().before_start(task_id, args, kwargs)


def check_existing_result(trip_id: str, section_type: str) -> dict[str, Any] | None:
    """
    Check if a report section already exists for a trip.

    Use this in agent tasks to prevent duplicate inserts.

    Args:
        trip_id: The trip ID
        section_type: The section type (visa, country, weather, etc.)

    Returns:
        Existing result if found, None otherwise
    """
    try:
        from app.core.supabase import supabase

        response = (
            supabase.table("report_sections")
            .select("id, content, confidence_score, generated_at")
            .eq("trip_id", trip_id)
            .eq("section_type", section_type)
            .order("generated_at", desc=True)
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            logger.info(
                f"Found existing {section_type} report for trip {trip_id}",
                extra={"trip_id": trip_id, "section_type": section_type},
            )
            return response.data[0]
        return None
    except Exception as e:
        logger.warning(f"Failed to check existing result: {e}")
        return None


def upsert_report_section(
    trip_id: str,
    section_type: str,
    title: str,
    content: dict[str, Any],
    confidence_score: int,
    sources: list[dict] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """
    Upsert a report section (insert or update if exists).

    This ensures idempotency - calling multiple times with the same
    trip_id and section_type won't create duplicates.

    Args:
        trip_id: Trip ID
        section_type: Section type (visa, country, weather, etc.)
        title: Section title
        content: Section content (JSON)
        confidence_score: Confidence score (0-100)
        sources: Optional list of sources
        generated_at: Optional generation timestamp

    Returns:
        The upserted record
    """
    from datetime import datetime

    from app.core.supabase import supabase

    if generated_at is None:
        generated_at = datetime.utcnow().isoformat()

    record = {
        "trip_id": trip_id,
        "section_type": section_type,
        "title": title,
        "content": content,
        "confidence_score": confidence_score,
        "sources": sources or [],
        "generated_at": generated_at,
    }

    # Try to find existing record
    existing = (
        supabase.table("report_sections")
        .select("id")
        .eq("trip_id", trip_id)
        .eq("section_type", section_type)
        .execute()
    )

    if existing.data and len(existing.data) > 0:
        # Update existing record
        existing_id = existing.data[0]["id"]
        response = (
            supabase.table("report_sections")
            .update(record)
            .eq("id", existing_id)
            .execute()
        )
        logger.info(
            f"Updated existing {section_type} report for trip {trip_id}",
            extra={"report_id": existing_id},
        )
    else:
        # Insert new record
        response = supabase.table("report_sections").insert(record).execute()
        logger.info(
            f"Inserted new {section_type} report for trip {trip_id}",
        )

    return response.data[0] if response.data else record
