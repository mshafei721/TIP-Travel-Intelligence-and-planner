"""
Celery tasks package

This package contains all Celery tasks for async processing:
- Agent job execution (visa, country, weather, etc.)
- Report generation
- Data cleanup and maintenance
- Email notifications

All tasks are auto-discovered by Celery from this module.
"""

from app.tasks.agent_jobs import (
    execute_agent_job,
    execute_orchestrator,
    execute_visa_agent,
)
from app.tasks.cleanup import (
    cancel_scheduled_deletion,
    cleanup_expired_pdfs,
    cleanup_expired_tasks,
    process_deletion_queue,
    schedule_trip_deletion,
)
from app.tasks.example import add, multiply

__all__ = [
    # Agent tasks
    "execute_agent_job",
    "execute_visa_agent",
    "execute_orchestrator",
    # Cleanup tasks
    "cleanup_expired_tasks",
    "cleanup_expired_pdfs",
    "process_deletion_queue",
    "schedule_trip_deletion",
    "cancel_scheduled_deletion",
    # Example tasks
    "add",
    "multiply",
]
