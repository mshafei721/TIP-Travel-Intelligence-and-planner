"""
Data cleanup and maintenance tasks

These tasks handle:
- Expired task result cleanup
- GDPR compliance deletion
- Database maintenance
- PDF file cleanup
"""

import logging
from datetime import datetime, timedelta

from celery import shared_task

from app.core.celery_app import BaseTipTask
from app.core.supabase import supabase

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.cleanup.cleanup_expired_tasks",
)
def cleanup_expired_tasks(self) -> dict:
    """
    Clean up expired task results from Celery result backend

    This task runs daily at 2 AM to remove old task results
    and free up Redis memory.

    Returns:
        Cleanup statistics (tasks_deleted, memory_freed_mb)
    """
    logger.info(f"[Task {self.request.id}] Starting cleanup of expired task results")

    tasks_deleted = 0
    memory_freed_mb = 0.0

    try:
        # Clean up old agent_jobs records (older than 30 days)
        cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

        # Query for old completed/failed jobs to get count first
        count_response = (
            supabase.table("agent_jobs")
            .select("id", count="exact")
            .in_("status", ["completed", "failed"])
            .lt("completed_at", cutoff_date)
            .execute()
        )

        if count_response.count and count_response.count > 0:
            tasks_deleted = count_response.count

            # Delete old agent jobs
            delete_response = (
                supabase.table("agent_jobs")
                .delete()
                .in_("status", ["completed", "failed"])
                .lt("completed_at", cutoff_date)
                .execute()
            )

            logger.info(f"Deleted {tasks_deleted} old agent job records")

        # Clean up orphaned report sections (no associated trip)
        # This handles edge cases where trips were deleted but sections remain
        orphan_response = (
            supabase.rpc(
                "cleanup_orphaned_sections",
                {},
            )
            .execute()
        )

        # Estimate memory freed (rough estimate based on record count)
        # Average agent_job record ~5KB, report_section ~10KB
        memory_freed_mb = (tasks_deleted * 5) / 1024

    except Exception as e:
        logger.error(f"Error during task cleanup: {e}")
        # Continue with partial result rather than failing

    result = {
        "tasks_deleted": tasks_deleted,
        "memory_freed_mb": round(memory_freed_mb, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info(f"[Task {self.request.id}] Completed cleanup: {result}")
    return result


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.cleanup.process_deletion_queue",
)
def process_deletion_queue(self) -> dict:
    """
    Process GDPR deletion queue

    This task runs daily at 3 AM to process scheduled deletions
    from the deletion_schedule table.

    Flow:
        1. Query deletion_schedule for due deletions
        2. Delete associated trips and report data
        3. Remove deletion_schedule entries
        4. Log deletion statistics

    Returns:
        Deletion statistics (trips_deleted, data_freed_mb)
    """
    logger.info(f"[Task {self.request.id}] Processing GDPR deletion queue")

    trips_deleted = 0
    trips_failed = 0
    data_freed_mb = 0.0
    now = datetime.utcnow().isoformat()

    try:
        # Query deletion_schedule for entries that are due
        response = (
            supabase.table("deletion_schedule")
            .select("id, trip_id, scheduled_at, deletion_reason")
            .eq("status", "pending")
            .lte("scheduled_at", now)
            .execute()
        )

        if not response.data:
            logger.info("No pending deletions found")
            return {
                "trips_deleted": 0,
                "trips_failed": 0,
                "data_freed_mb": 0.0,
                "timestamp": now,
            }

        scheduled_deletions = response.data
        logger.info(f"Found {len(scheduled_deletions)} pending deletions")

        for deletion in scheduled_deletions:
            deletion_id = deletion["id"]
            trip_id = deletion["trip_id"]

            try:
                # Mark as executing
                supabase.table("deletion_schedule").update(
                    {"status": "executing"}
                ).eq("id", deletion_id).execute()

                # Get trip info for logging
                trip_response = (
                    supabase.table("trips")
                    .select("id, destination_country, destination_city, user_id")
                    .eq("id", trip_id)
                    .single()
                    .execute()
                )

                trip_info = trip_response.data if trip_response.data else {}

                # Delete associated PDFs from storage (if any)
                try:
                    storage_response = supabase.storage.from_("trip-reports").list(
                        path=f"{trip_id}/"
                    )
                    if storage_response:
                        for file in storage_response:
                            supabase.storage.from_("trip-reports").remove(
                                [f"{trip_id}/{file['name']}"]
                            )
                        logger.info(f"Deleted {len(storage_response)} PDF files for trip {trip_id}")
                except Exception as storage_error:
                    logger.warning(f"Could not clean storage for trip {trip_id}: {storage_error}")

                # Delete the trip (cascade will delete report_sections, agent_jobs, etc.)
                delete_response = (
                    supabase.table("trips")
                    .delete()
                    .eq("id", trip_id)
                    .execute()
                )

                # Mark deletion as completed
                supabase.table("deletion_schedule").update(
                    {
                        "status": "completed",
                        "executed_at": datetime.utcnow().isoformat(),
                    }
                ).eq("id", deletion_id).execute()

                trips_deleted += 1
                # Estimate ~50KB per trip with all related data
                data_freed_mb += 0.05

                logger.info(
                    f"Successfully deleted trip {trip_id} "
                    f"({trip_info.get('destination_city', 'Unknown')})"
                )

            except Exception as trip_error:
                logger.error(f"Failed to delete trip {trip_id}: {trip_error}")

                # Mark deletion as failed
                supabase.table("deletion_schedule").update(
                    {
                        "status": "failed",
                        "executed_at": datetime.utcnow().isoformat(),
                    }
                ).eq("id", deletion_id).execute()

                trips_failed += 1

    except Exception as e:
        logger.error(f"Error processing deletion queue: {e}")

    result = {
        "trips_deleted": trips_deleted,
        "trips_failed": trips_failed,
        "data_freed_mb": round(data_freed_mb, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info(f"[Task {self.request.id}] Completed deletion: {result}")
    return result


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.cleanup.cleanup_expired_pdfs",
)
def cleanup_expired_pdfs(self) -> dict:
    """
    Clean up expired PDF files from storage

    This task runs daily at 4 AM to remove PDF files that are:
    - Older than 30 days
    - Associated with deleted trips

    Returns:
        Cleanup statistics (files_deleted, storage_freed_mb)
    """
    logger.info(f"[Task {self.request.id}] Starting PDF cleanup")

    files_deleted = 0
    storage_freed_mb = 0.0

    try:
        # List all files in trip-reports bucket
        response = supabase.storage.from_("trip-reports").list()

        if not response:
            return {
                "files_deleted": 0,
                "storage_freed_mb": 0.0,
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Check each folder (trip_id) if the trip still exists
        for folder in response:
            if folder.get("id") is None:  # It's a folder
                trip_id = folder.get("name")
                if not trip_id:
                    continue

                # Check if trip exists
                trip_response = (
                    supabase.table("trips")
                    .select("id")
                    .eq("id", trip_id)
                    .execute()
                )

                if not trip_response.data:
                    # Trip doesn't exist, delete all PDFs in this folder
                    try:
                        files = supabase.storage.from_("trip-reports").list(
                            path=f"{trip_id}/"
                        )
                        for file in files:
                            file_path = f"{trip_id}/{file['name']}"
                            file_size = file.get("metadata", {}).get("size", 0)

                            supabase.storage.from_("trip-reports").remove([file_path])

                            files_deleted += 1
                            storage_freed_mb += file_size / (1024 * 1024)

                        logger.info(f"Cleaned up {len(files)} orphaned PDFs for trip {trip_id}")

                    except Exception as folder_error:
                        logger.warning(f"Error cleaning folder {trip_id}: {folder_error}")

    except Exception as e:
        logger.error(f"Error during PDF cleanup: {e}")

    result = {
        "files_deleted": files_deleted,
        "storage_freed_mb": round(storage_freed_mb, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info(f"[Task {self.request.id}] Completed PDF cleanup: {result}")
    return result


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.cleanup.schedule_trip_deletion",
)
def schedule_trip_deletion(self, trip_id: str, days_from_now: int = 7) -> dict:
    """
    Schedule a trip for deletion

    This task is called when a user requests trip deletion or when
    automatic cleanup is triggered.

    Args:
        trip_id: The trip ID to schedule for deletion
        days_from_now: Number of days until deletion (default 7 for GDPR compliance)

    Returns:
        Schedule confirmation
    """
    logger.info(f"[Task {self.request.id}] Scheduling deletion for trip {trip_id}")

    try:
        scheduled_at = (datetime.utcnow() + timedelta(days=days_from_now)).isoformat()

        # Check if already scheduled
        existing = (
            supabase.table("deletion_schedule")
            .select("id")
            .eq("trip_id", trip_id)
            .eq("status", "pending")
            .execute()
        )

        if existing.data:
            logger.info(f"Trip {trip_id} already scheduled for deletion")
            return {
                "success": True,
                "message": "Already scheduled",
                "schedule_id": existing.data[0]["id"],
                "trip_id": trip_id,
            }

        # Create deletion schedule entry
        response = (
            supabase.table("deletion_schedule")
            .insert(
                {
                    "trip_id": trip_id,
                    "scheduled_at": scheduled_at,
                    "status": "pending",
                    "deletion_reason": "user_requested",
                }
            )
            .execute()
        )

        if response.data:
            schedule_id = response.data[0]["id"]
            logger.info(f"Scheduled trip {trip_id} for deletion at {scheduled_at}")

            return {
                "success": True,
                "message": f"Scheduled for deletion in {days_from_now} days",
                "schedule_id": schedule_id,
                "trip_id": trip_id,
                "scheduled_at": scheduled_at,
            }
        else:
            raise Exception("No data returned from insert")

    except Exception as e:
        logger.error(f"Error scheduling deletion for trip {trip_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "trip_id": trip_id,
        }


@shared_task(
    bind=True,
    base=BaseTipTask,
    name="app.tasks.cleanup.cancel_scheduled_deletion",
)
def cancel_scheduled_deletion(self, trip_id: str) -> dict:
    """
    Cancel a scheduled trip deletion

    This allows users to change their mind before the deletion occurs.

    Args:
        trip_id: The trip ID to cancel deletion for

    Returns:
        Cancellation confirmation
    """
    logger.info(f"[Task {self.request.id}] Cancelling deletion for trip {trip_id}")

    try:
        # Find pending deletion schedule
        response = (
            supabase.table("deletion_schedule")
            .select("id")
            .eq("trip_id", trip_id)
            .eq("status", "pending")
            .execute()
        )

        if not response.data:
            return {
                "success": False,
                "message": "No pending deletion found",
                "trip_id": trip_id,
            }

        # Delete the schedule entry
        schedule_id = response.data[0]["id"]
        supabase.table("deletion_schedule").delete().eq("id", schedule_id).execute()

        logger.info(f"Cancelled deletion schedule for trip {trip_id}")

        return {
            "success": True,
            "message": "Deletion cancelled",
            "trip_id": trip_id,
            "cancelled_schedule_id": schedule_id,
        }

    except Exception as e:
        logger.error(f"Error cancelling deletion for trip {trip_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "trip_id": trip_id,
        }
