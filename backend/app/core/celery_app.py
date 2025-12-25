"""
Celery application configuration for async task processing

This module configures Celery for handling background agent jobs,
report generation, and other async operations.

Architecture:
- Redis as message broker and result backend
- Prefork worker pool for CPU-bound agent tasks
- JSON serialization for task arguments and results
- Auto-discovery of tasks from app.tasks module
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

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
    - Automatic retry on failure
    - Structured logging
    - Error reporting to Sentry (when configured)
    """

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes between retries
    retry_jitter = True  # Add randomness to retry delays

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failures"""
        # TODO: Add Sentry integration for production error tracking
        print(f"Task {self.name} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Log task successes"""
        print(f"Task {self.name} succeeded")
        super().on_success(retval, task_id, args, kwargs)
