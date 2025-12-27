"""Trips API endpoints"""

import logging
from datetime import date, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.core.auth import verify_jwt_token
from app.core.errors import log_and_raise_http_error
from app.core.supabase import supabase

logger = logging.getLogger(__name__)
from app.models.report import (
    ApplicationProcessResponse,
    CountryReportResponse,
    EmergencyContactResponse,
    EntryRequirementResponse,
    FlightReportResponse,
    FullReportResponse,
    ItineraryReportResponse,
    PDFExportError,
    PDFExportResponse,
    PowerOutletResponse,
    ReportNotFoundError,
    ReportSectionResponse,
    ReportUnauthorizedError,
    SourceReferenceResponse,
    TravelAdvisoryResponse,
    TripInfoResponse,
    VisaReportResponse,
    VisaRequirementResponse,
)
from app.models.template import CreateTripFromTemplateRequest
from app.models.trips import (
    ArchiveResponse,
    ChangePreviewRequest,
    ChangePreviewResponse,
    DraftResponse,
    DraftSaveRequest,
    FieldChange,
    RecalculationCancelResponse,
    RecalculationRequest,
    RecalculationResponse,
    RecalculationStatusEnum,
    RecalculationStatusResponse,
    TripCreateRequest,
    TripResponse,
    TripStatus,
    TripUpdateRequest,
    TripUpdateWithRecalcRequest,
    TripUpdateWithRecalcResponse,
    TripVersionListResponse,
    TripVersionRestoreResponse,
    TripVersionSummary,
    VersionCompareResponse,
)
from app.services.change_detector import ChangeDetector

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("")
async def list_trips(
    status_filter: str | None = Query(None, description="Filter by trip status"),
    limit: int = Query(20, ge=1, le=100, description="Number of trips to return"),
    cursor: str | None = Query(None, description="Pagination cursor"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    List trips for the authenticated user

    Query Parameters:
    - status: Filter by trip status (draft, pending, processing, completed, failed)
    - limit: Number of trips to return (1-100, default 20)
    - cursor: Pagination cursor for next page

    Returns:
    - items: List of trip summaries
    - nextCursor: Cursor for next page (if more results exist)
    """
    user_id = token_payload["user_id"]

    try:
        # Build query
        query = (
            supabase.table("trips")
            .select("id, created_at, updated_at, status, trip_details, destinations")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
        )

        # Apply status filter if provided
        if status_filter:
            query = query.eq("status", status_filter)

        # Execute query
        response = query.execute()

        if not response.data:
            return {"items": [], "nextCursor": None}

        # Transform to TripListItem format
        items = []
        for trip in response.data:
            # Extract destination from first destination in array
            destination_name = "Unknown"
            if trip.get("destinations") and len(trip["destinations"]) > 0:
                first_dest = trip["destinations"][0]
                destination_name = (
                    f"{first_dest.get('city', '')}, {first_dest.get('country', '')}".strip(", ")
                )

            # Extract dates from trip_details
            trip_details = trip.get("trip_details", {})
            start_date = trip_details.get("departureDate", "")
            end_date = trip_details.get("returnDate", "")

            # Determine display status
            if trip["status"] == "completed":
                display_status = "completed"
            elif trip["status"] in ["draft", "pending", "processing"]:
                # Check if trip is in future or past
                if start_date:
                    try:
                        departure = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                        if departure.date() > date.today():
                            display_status = "upcoming"
                        elif end_date:
                            return_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                            if return_date.date() >= date.today():
                                display_status = "in-progress"
                            else:
                                display_status = "completed"
                        else:
                            display_status = "in-progress"
                    except (ValueError, AttributeError):
                        display_status = "upcoming"
                else:
                    display_status = "upcoming"
            else:
                display_status = "completed"

            items.append(
                {
                    "id": trip["id"],
                    "destination": destination_name,
                    "startDate": start_date,
                    "endDate": end_date,
                    "status": display_status,
                    "createdAt": trip["created_at"],
                    "deletionDate": trip.get("auto_delete_at", ""),
                }
            )

        # Determine if there are more results (simple pagination)
        next_cursor = None
        if len(items) == limit:
            # There might be more results
            next_cursor = items[-1]["createdAt"]

        return {"items": items, "nextCursor": next_cursor}

    except Exception as e:
        log_and_raise_http_error("fetch trips", e, "Failed to fetch trips. Please try again.")


@router.get("/{trip_id}")
async def get_trip(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get detailed trip information

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - Complete trip object with all fields
    """
    user_id = token_payload["user_id"]

    try:
        response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("fetch trip", e, "Failed to fetch trip. Please try again.")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TripResponse)
async def create_trip(
    trip_data: TripCreateRequest,
    token_payload: dict = Depends(verify_jwt_token),
    idempotency_key: str | None = Header(None, alias="X-Idempotency-Key"),
):
    """
    Create a new trip

    Request Body:
    - traveler_details: Traveler information (name, email, nationality, etc.)
    - destinations: List of destinations (at least one required)
    - trip_details: Trip planning details (dates, budget, purpose)
    - preferences: Travel preferences (style, interests, etc.)
    - template_id: Optional template ID to base this trip on

    Headers:
    - X-Idempotency-Key: Optional idempotency key for duplicate request prevention

    Returns:
    - Complete trip object with generated ID and timestamps
    """
    user_id = token_payload["user_id"]

    try:
        # Check for duplicate request using idempotency key
        if idempotency_key:
            # Check if a trip with this idempotency key already exists
            existing_response = (
                supabase.table("trips")
                .select("*")
                .eq("user_id", user_id)
                .eq("idempotency_key", idempotency_key)
                .execute()
            )

            if existing_response.data and len(existing_response.data) > 0:
                # Return existing trip (idempotent operation)
                return existing_response.data[0]

        # Prepare trip data for database
        trip_id = str(uuid4())
        trip_record = {
            "id": trip_id,
            "user_id": user_id,
            "status": TripStatus.DRAFT.value,
            "traveler_details": trip_data.traveler_details.model_dump(),
            "destinations": [dest.model_dump() for dest in trip_data.destinations],
            "trip_details": trip_data.trip_details.model_dump(
                mode="json"
            ),  # Convert dates to strings
            "preferences": trip_data.preferences.model_dump(),
            "template_id": trip_data.template_id,
        }

        # Add idempotency key if provided
        if idempotency_key:
            trip_record["idempotency_key"] = idempotency_key

        # Insert trip into database
        response = supabase.table("trips").insert(trip_record).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create trip: No data returned from database",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("create trip", e, "Failed to create trip. Please try again.")


@router.post("/from-template/{template_id}", status_code=status.HTTP_201_CREATED, response_model=TripResponse)
async def create_trip_from_template(
    template_id: str,
    template_data: CreateTripFromTemplateRequest | None = None,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Create a new trip from a template

    Path Parameters:
    - template_id: UUID of the template to use

    Request Body (optional):
    - title: Custom trip title
    - start_date: Trip start date (ISO format)
    - end_date: Trip end date (ISO format)
    - override_traveler_details: Override template traveler details
    - override_preferences: Override template preferences

    Returns:
    - Created trip object based on template

    Notes:
    - Template must be public or owned by user
    - Increments template use_count
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch the template
        template_response = (
            supabase.table("trip_templates")
            .select("*")
            .eq("id", template_id)
            .execute()
        )

        if not template_response.data or len(template_response.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        template = template_response.data[0]

        # Check if user can access this template
        if not template.get("is_public") and template.get("user_id") != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this template")

        # Prepare trip data from template
        request_data = template_data or CreateTripFromTemplateRequest()

        # Generate title
        destinations = template.get("destinations", [])
        first_dest = destinations[0] if destinations else {}
        default_title = f"Trip to {first_dest.get('city', first_dest.get('country', 'Unknown'))}"
        trip_title = request_data.title or default_title

        # Build traveler details (from template or override)
        traveler_details = template.get("traveler_details", {})
        if request_data.override_traveler_details:
            traveler_details = {**traveler_details, **request_data.override_traveler_details}

        # Build trip details
        trip_details = {
            "departureDate": request_data.start_date,
            "returnDate": request_data.end_date,
            "budget": template.get("estimated_budget", 0),
            "currency": template.get("currency", "USD"),
            "tripPurpose": "tourism",
        }

        # Build preferences
        preferences = template.get("preferences", {})
        if request_data.override_preferences:
            preferences = {**preferences, **request_data.override_preferences}

        # Create trip record
        trip_id = str(uuid4())
        trip_record = {
            "id": trip_id,
            "user_id": user_id,
            "title": trip_title,
            "status": TripStatus.DRAFT.value,
            "traveler_details": traveler_details,
            "destinations": destinations,
            "trip_details": trip_details,
            "preferences": preferences,
            "template_id": template_id,
        }

        # Insert trip
        response = supabase.table("trips").insert(trip_record).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create trip from template",
            )

        # Increment template use_count
        current_use_count = template.get("use_count", 0)
        supabase.table("trip_templates").update(
            {"use_count": current_use_count + 1}
        ).eq("id", template_id).execute()

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("create trip from template", e, "Failed to create trip from template. Please try again.")


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    trip_data: TripUpdateRequest,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Update an existing trip

    Path Parameters:
    - trip_id: UUID of the trip to update

    Request Body:
    - All fields are optional - only provided fields will be updated
    - traveler_details: Updated traveler information
    - destinations: Updated list of destinations
    - trip_details: Updated trip planning details
    - preferences: Updated travel preferences

    Returns:
    - Updated trip object

    Notes:
    - Can only update trips in 'draft' or 'pending' status
    - Cannot update trips that are 'processing', 'completed', or 'failed'
    """
    user_id = token_payload["user_id"]

    try:
        # First, verify the trip exists and belongs to the user
        existing_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not existing_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        existing_trip = existing_response.data

        # Check if trip status allows updates
        if existing_trip["status"] not in [
            TripStatus.DRAFT.value,
            TripStatus.PENDING.value,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update trip with status '{existing_trip['status']}'. Only 'draft' and 'pending' trips can be updated.",
            )

        # Prepare update data (only include fields that are provided)
        update_record = {}

        if trip_data.traveler_details is not None:
            update_record["traveler_details"] = trip_data.traveler_details.model_dump()

        if trip_data.destinations is not None:
            update_record["destinations"] = [dest.model_dump() for dest in trip_data.destinations]

        if trip_data.trip_details is not None:
            update_record["trip_details"] = trip_data.trip_details.model_dump(mode="json")

        if trip_data.preferences is not None:
            update_record["preferences"] = trip_data.preferences.model_dump()

        # If no fields to update, return existing trip
        if not update_record:
            return existing_trip

        # Update trip in database
        response = (
            supabase.table("trips")
            .update(update_record)
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update trip: No data returned from database",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("update trip", e, "Failed to update trip. Please try again.")


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Delete a trip

    Path Parameters:
    - trip_id: UUID of the trip to delete

    Notes:
    - Can only delete trips in 'draft', 'pending', or 'failed' status
    - Cannot delete trips that are 'processing' or 'completed'
    - For completed trips, use the auto-deletion schedule instead
    """
    user_id = token_payload["user_id"]

    try:
        # First, verify the trip exists and belongs to the user
        existing_response = (
            supabase.table("trips")
            .select("status")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not existing_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        trip_status = existing_response.data["status"]

        # Check if trip status allows deletion
        if trip_status == TripStatus.PROCESSING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete trip that is currently processing. Please wait for completion.",
            )

        if trip_status == TripStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete completed trip. Completed trips are automatically deleted 30 days after return date.",
            )

        # Delete trip
        delete_response = (
            supabase.table("trips").delete().eq("id", trip_id).eq("user_id", user_id).execute()
        )

        # Return 204 No Content on success
        return

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("delete trip", e, "Failed to delete trip. Please try again.")


@router.post("/{trip_id}/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_trip_report(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Start AI report generation for a trip

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - status: "queued"
    - task_id: Celery task ID for tracking
    - message: Human-readable message

    Notes:
    - Trip status must be 'draft' or 'pending'
    - Trip status will be updated to 'processing'
    - Report generation is handled asynchronously by Celery workers
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        existing_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not existing_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        existing_trip = existing_response.data

        # Check if trip status allows report generation
        if existing_trip["status"] == TripStatus.PROCESSING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report generation already in progress for this trip",
            )

        if existing_trip["status"] == TripStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report already generated for this trip",
            )

        if existing_trip["status"] == TripStatus.FAILED.value:
            # Allow retry for failed trips
            pass

        # Update trip status to 'processing'
        update_response = (
            supabase.table("trips")
            .update({"status": TripStatus.PROCESSING.value})
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        # Queue Celery task for report generation
        from app.tasks.agent_jobs import execute_orchestrator

        task = execute_orchestrator.delay(trip_id)

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Report generation started. You will be notified when complete.",
        }

    except HTTPException:
        raise
    except Exception as e:
        # Rollback status update on failure
        try:
            supabase.table("trips").update({"status": TripStatus.FAILED.value}).eq(
                "id", trip_id
            ).eq("user_id", user_id).execute()
        except:
            pass

        log_and_raise_http_error("start report generation", e, "Failed to start report generation. Please try again.")


@router.get("/{trip_id}/status")
async def get_generation_status(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get current report generation status for a trip

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - status: Trip status (draft, pending, processing, completed, failed)
    - progress: Overall completion percentage (0-100)
    - current_agent: Current agent being executed (if processing)
    - agents_completed: List of completed agents
    - agents_failed: List of failed agents
    - error: Error message (if failed)
    - started_at: When report generation started
    - completed_at: When report generation completed (if done)
    """
    user_id = token_payload["user_id"]

    try:
        # Get trip status
        trip_response = (
            supabase.table("trips")
            .select("status, created_at, updated_at")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        trip = trip_response.data

        # Optimized: Get only the fields we need with a single query
        # Using selective fields instead of SELECT * for better performance
        jobs_response = (
            supabase.table("agent_jobs")
            .select("agent_type, status, error, created_at")
            .eq("trip_id", trip_id)
            .order("created_at")
            .execute()
        )

        agent_jobs = jobs_response.data if jobs_response.data else []

        # Calculate progress using list comprehensions (more efficient)
        total_agents = 10  # 10 specialized agents
        agents_completed = []
        agents_failed = []
        current_agent = None
        first_error = None
        started_at = None

        for job in agent_jobs:
            if started_at is None:
                started_at = job["created_at"]

            job_status = job["status"]
            agent_type = job["agent_type"]

            if job_status == "completed":
                agents_completed.append(agent_type)
            elif job_status == "failed":
                agents_failed.append(agent_type)
                if first_error is None:
                    first_error = job.get("error")
            elif job_status in ("processing", "running"):
                current_agent = agent_type

        completed_count = len(agents_completed)
        progress = int((completed_count / total_agents) * 100) if total_agents > 0 else 0

        return {
            "status": trip["status"],
            "progress": progress,
            "current_agent": current_agent,
            "agents_completed": agents_completed,
            "agents_failed": agents_failed,
            "error": first_error,
            "started_at": started_at,
            "completed_at": (trip["updated_at"] if trip["status"] == "completed" else None),
        }

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("get generation status", e, "Failed to get generation status. Please try again.")


# Draft Management Endpoints
@router.post("/drafts", status_code=status.HTTP_201_CREATED, response_model=DraftResponse)
async def save_draft(draft_data: DraftSaveRequest, token_payload: dict = Depends(verify_jwt_token)):
    """
    Save a trip draft (partial trip data for auto-save)

    Request Body:
    - All fields optional - save whatever the user has filled in so far
    - traveler_details: Partial traveler information
    - destinations: Partial destinations
    - trip_details: Partial trip details
    - preferences: Partial preferences

    Returns:
    - Draft object with generated ID

    Notes:
    - Drafts do not require complete data
    - Multiple drafts can exist per user
    - Drafts can be converted to full trips later
    """
    user_id = token_payload["user_id"]

    try:
        # Prepare draft data
        draft_id = str(uuid4())
        draft_record = {
            "id": draft_id,
            "user_id": user_id,
            "draft_data": draft_data.model_dump(exclude_none=True),
        }

        # Insert draft into database
        # Note: Using a separate 'trip_drafts' table (not in schema yet - would need migration)
        # For now, we'll store drafts as trips with 'draft' status
        trip_record = {
            "id": draft_id,
            "user_id": user_id,
            "status": TripStatus.DRAFT.value,
            "traveler_details": (
                draft_data.traveler_details.model_dump() if draft_data.traveler_details else {}
            ),
            "destinations": (
                [dest.model_dump() for dest in draft_data.destinations]
                if draft_data.destinations
                else []
            ),
            "trip_details": (
                draft_data.trip_details.model_dump(mode="json") if draft_data.trip_details else {}
            ),
            "preferences": (draft_data.preferences.model_dump() if draft_data.preferences else {}),
        }

        response = supabase.table("trips").insert(trip_record).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save draft",
            )

        return {
            "id": draft_id,
            "user_id": user_id,
            "created_at": response.data[0]["created_at"],
            "updated_at": response.data[0]["updated_at"],
            "draft_data": draft_data.model_dump(exclude_none=True),
        }

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("save draft", e, "Failed to save draft. Please try again.")


@router.get("/drafts")
async def get_drafts(token_payload: dict = Depends(verify_jwt_token)):
    """
    Get all drafts for the authenticated user

    Returns:
    - List of draft objects
    """
    user_id = token_payload["user_id"]

    try:
        # Get all draft trips
        response = (
            supabase.table("trips")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", TripStatus.DRAFT.value)
            .order("updated_at", desc=True)
            .execute()
        )

        if not response.data:
            return []

        # Transform to draft format
        drafts = []
        for trip in response.data:
            drafts.append(
                {
                    "id": trip["id"],
                    "user_id": trip["user_id"],
                    "created_at": trip["created_at"],
                    "updated_at": trip["updated_at"],
                    "draft_data": {
                        "traveler_details": trip.get("traveler_details"),
                        "destinations": trip.get("destinations"),
                        "trip_details": trip.get("trip_details"),
                        "preferences": trip.get("preferences"),
                    },
                }
            )

        return drafts

    except Exception as e:
        log_and_raise_http_error("get drafts", e, "Failed to get drafts. Please try again.")


@router.put("/drafts/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    draft_data: DraftSaveRequest,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Update an existing draft

    Path Parameters:
    - draft_id: UUID of the draft

    Request Body:
    - All fields optional - update whatever fields are provided

    Returns:
    - Updated draft object
    """
    user_id = token_payload["user_id"]

    try:
        # Verify draft exists
        existing_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", draft_id)
            .eq("user_id", user_id)
            .eq("status", TripStatus.DRAFT.value)
            .single()
            .execute()
        )

        if not existing_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")

        # Prepare update data
        update_record = {}

        if draft_data.traveler_details is not None:
            update_record["traveler_details"] = draft_data.traveler_details.model_dump()

        if draft_data.destinations is not None:
            update_record["destinations"] = [dest.model_dump() for dest in draft_data.destinations]

        if draft_data.trip_details is not None:
            update_record["trip_details"] = draft_data.trip_details.model_dump(mode="json")

        if draft_data.preferences is not None:
            update_record["preferences"] = draft_data.preferences.model_dump()

        # If no fields to update, return existing draft
        if not update_record:
            return {
                "id": draft_id,
                "user_id": user_id,
                "created_at": existing_response.data["created_at"],
                "updated_at": existing_response.data["updated_at"],
                "draft_data": draft_data.model_dump(exclude_none=True),
            }

        # Update draft
        response = (
            supabase.table("trips")
            .update(update_record)
            .eq("id", draft_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update draft",
            )

        return {
            "id": draft_id,
            "user_id": user_id,
            "created_at": response.data[0]["created_at"],
            "updated_at": response.data[0]["updated_at"],
            "draft_data": draft_data.model_dump(exclude_none=True),
        }

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("update draft", e, "Failed to update draft. Please try again.")


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(draft_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Delete a draft

    Path Parameters:
    - draft_id: UUID of the draft
    """
    user_id = token_payload["user_id"]

    try:
        # Verify draft exists
        existing_response = (
            supabase.table("trips")
            .select("id")
            .eq("id", draft_id)
            .eq("user_id", user_id)
            .eq("status", TripStatus.DRAFT.value)
            .single()
            .execute()
        )

        if not existing_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")

        # Delete draft
        supabase.table("trips").delete().eq("id", draft_id).eq("user_id", user_id).execute()

        return

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("delete draft", e, "Failed to delete draft. Please try again.")


@router.get(
    "/{trip_id}/report/visa",
    response_model=VisaReportResponse,
    responses={
        404: {"model": ReportNotFoundError, "description": "Report not found"},
        403: {"model": ReportUnauthorizedError, "description": "Unauthorized access"},
    },
)
async def get_visa_report(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get visa report for a trip

    Retrieves the generated visa requirements analysis for the specified trip.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - Complete visa report with requirements, application process, and entry requirements

    Errors:
    - 404: Visa report not found (generate it first using POST /trips/{trip_id}/generate)
    - 403: User does not own this trip
    - 500: Database error

    Example:
        GET /trips/550e8400-e29b-41d4-a716-446655440000/report/visa

        Response:
        {
            "report_id": "...",
            "trip_id": "...",
            "generated_at": "2025-12-25T10:00:00Z",
            "confidence_score": 0.95,
            "visa_requirement": {
                "visa_required": false,
                "visa_type": "visa-free",
                "max_stay_days": 90
            },
            ...
        }
    """
    user_id = token_payload["user_id"]

    try:
        # 1. Verify trip exists and user owns it
        trip_response = (
            supabase.table("trips").select("id, user_id").eq("id", trip_id).single().execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # 2. Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this report",
            )

        # 3. Retrieve visa report from report_sections table
        report_response = (
            supabase.table("report_sections")
            .select("*")
            .eq("trip_id", trip_id)
            .eq("section_type", "visa")
            .order("generated_at", desc=True)
            .limit(1)
            .execute()
        )

        if not report_response.data or len(report_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa report not found for this trip. Generate the trip report first using POST /trips/{id}/generate",
            )

        # 4. Parse report data
        report = report_response.data[0]
        content = report["content"]

        # Convert confidence from integer (0-100) back to float (0.0-1.0)
        confidence_float = (
            float(report["confidence_score"]) / 100.0 if report.get("confidence_score") else 0.0
        )

        # 5. Build response
        return VisaReportResponse(
            report_id=report["id"],
            trip_id=report["trip_id"],
            generated_at=datetime.fromisoformat(report["generated_at"].replace("Z", "+00:00")),
            confidence_score=confidence_float,
            visa_requirement=VisaRequirementResponse(**content["visa_requirement"]),
            application_process=ApplicationProcessResponse(**content["application_process"]),
            entry_requirements=EntryRequirementResponse(**content["entry_requirements"]),
            tips=content.get("tips", []),
            warnings=content.get("warnings", []),
            sources=[SourceReferenceResponse(**source) for source in content.get("sources", [])],
            last_verified=datetime.fromisoformat(content["last_verified"].replace("Z", "+00:00")),
        )

    except HTTPException:
        raise
    except KeyError as e:
        # Handle missing fields in content data
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid report data format. Please regenerate the report.",
        )
    except Exception as e:
        log_and_raise_http_error("retrieve visa report", e, "Failed to retrieve visa report. Please try again.")


@router.get(
    "/{trip_id}/report/destination",
    response_model=CountryReportResponse,
    responses={
        404: {"model": ReportNotFoundError, "description": "Report not found"},
        403: {"model": ReportUnauthorizedError, "description": "Unauthorized access"},
    },
)
async def get_destination_report(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get destination/country intelligence report for a trip

    Retrieves the generated country intelligence for the specified trip,
    including demographics, practical information, safety ratings, and travel advisories.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - Complete destination intelligence report with country facts, emergency contacts,
      safety information, and travel advisories

    Errors:
    - 404: Destination report not found (generate it first using POST /trips/{trip_id}/generate)
    - 403: User does not own this trip
    - 500: Database error

    Example:
        GET /trips/550e8400-e29b-41d4-a716-446655440000/report/destination

        Response:
        {
            "report_id": "...",
            "trip_id": "...",
            "generated_at": "2025-12-25T10:00:00Z",
            "confidence_score": 0.95,
            "country_name": "Japan",
            "country_code": "JP",
            "capital": "Tokyo",
            "region": "Asia",
            ...
        }
    """
    user_id = token_payload["user_id"]

    try:
        # 1. Verify trip exists and user owns it
        trip_response = (
            supabase.table("trips").select("id, user_id").eq("id", trip_id).single().execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # 2. Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this report",
            )

        # 3. Retrieve country report from report_sections table
        report_response = (
            supabase.table("report_sections")
            .select("*")
            .eq("trip_id", trip_id)
            .eq("section_type", "country")
            .order("generated_at", desc=True)
            .limit(1)
            .execute()
        )

        if not report_response.data or len(report_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination report not found for this trip. Generate the trip report first using POST /trips/{id}/generate",
            )

        # 4. Parse report data
        report = report_response.data[0]
        content = report["content"]

        # Convert confidence from integer (0-100) back to float (0.0-1.0)
        confidence_float = (
            float(report["confidence_score"]) / 100.0 if report.get("confidence_score") else 0.0
        )

        # 5. Build response
        return CountryReportResponse(
            report_id=report["id"],
            trip_id=report["trip_id"],
            generated_at=datetime.fromisoformat(report["generated_at"].replace("Z", "+00:00")),
            confidence_score=confidence_float,
            country_name=content["country_name"],
            country_code=content["country_code"],
            capital=content["capital"],
            region=content["region"],
            subregion=content.get("subregion"),
            population=content["population"],
            area_km2=content.get("area_km2"),
            population_density=content.get("population_density"),
            official_languages=content["official_languages"],
            common_languages=content.get("common_languages"),
            time_zones=content["time_zones"],
            coordinates=content.get("coordinates"),
            borders=content.get("borders"),
            emergency_numbers=[
                EmergencyContactResponse(**contact) for contact in content["emergency_numbers"]
            ],
            power_outlet=PowerOutletResponse(**content["power_outlet"]),
            driving_side=content["driving_side"],
            currencies=content["currencies"],
            currency_codes=content["currency_codes"],
            safety_rating=content["safety_rating"],
            travel_advisories=[
                TravelAdvisoryResponse(**advisory)
                for advisory in content.get("travel_advisories", [])
            ],
            notable_facts=content.get("notable_facts", []),
            best_time_to_visit=content.get("best_time_to_visit"),
            sources=[SourceReferenceResponse(**source) for source in content.get("sources", [])],
            warnings=content.get("warnings", []),
        )

    except HTTPException:
        raise
    except KeyError as e:
        # Handle missing fields in content data
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid report data format. Please regenerate the report.",
        )
    except Exception as e:
        log_and_raise_http_error("retrieve destination report", e, "Failed to retrieve destination report. Please try again.")


@router.get(
    "/{trip_id}/report/itinerary",
    response_model=ItineraryReportResponse,
    responses={
        404: {"model": ReportNotFoundError, "description": "Report not found"},
        403: {"model": ReportUnauthorizedError, "description": "Unauthorized access"},
    },
)
async def get_itinerary_report(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get itinerary report for a trip

    Retrieves the generated day-by-day itinerary for the specified trip,
    including activities, accommodations, transportation, and budget breakdown.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - Complete itinerary report with daily plans, accommodations, and tips

    Errors:
    - 404: Itinerary report not found (generate it first using POST /trips/{trip_id}/generate)
    - 403: User does not own this trip
    - 500: Database error

    Example:
        GET /trips/550e8400-e29b-41d4-a716-446655440000/report/itinerary

        Response:
        {
            "report_id": "...",
            "trip_id": "...",
            "generated_at": "2025-12-26T10:00:00Z",
            "confidence_score": 0.85,
            "content": {
                "daily_plans": [...],
                "accommodations": [...],
                "transportation": [...],
                "budget_summary": {...}
            },
            "sources": [...],
            "warnings": [...]
        }
    """
    user_id = token_payload["user_id"]

    try:
        # 1. Verify trip exists and user owns it
        trip_response = (
            supabase.table("trips").select("id, user_id").eq("id", trip_id).single().execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # 2. Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this report",
            )

        # 3. Retrieve itinerary report from report_sections table
        report_response = (
            supabase.table("report_sections")
            .select("*")
            .eq("trip_id", trip_id)
            .eq("section_type", "itinerary")
            .order("generated_at", desc=True)
            .limit(1)
            .execute()
        )

        if not report_response.data or len(report_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary report not found for this trip. Generate the trip report first using POST /trips/{id}/generate",
            )

        # 4. Parse report data
        report = report_response.data[0]
        content = report["content"]

        # Convert confidence from integer (0-100) back to float (0.0-1.0)
        confidence_float = (
            float(report["confidence_score"]) / 100.0 if report.get("confidence_score") else 0.0
        )

        # 5. Build response
        return ItineraryReportResponse(
            report_id=report["id"],
            trip_id=report["trip_id"],
            generated_at=datetime.fromisoformat(report["generated_at"].replace("Z", "+00:00")),
            confidence_score=confidence_float,
            content=content,
            sources=[
                SourceReferenceResponse(**source) for source in report.get("sources", [])
            ],
            warnings=content.get("warnings", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("retrieve itinerary report", e, "Failed to retrieve itinerary report. Please try again.")


@router.get(
    "/{trip_id}/report/flight",
    response_model=FlightReportResponse,
    responses={
        404: {"model": ReportNotFoundError, "description": "Report not found"},
        403: {"model": ReportUnauthorizedError, "description": "Unauthorized access"},
    },
)
async def get_flight_report(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get flight report for a trip

    Retrieves the generated flight recommendations for the specified trip,
    including flight options, pricing, airport information, and booking tips.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - Complete flight report with recommended flights, pricing, and airport info

    Errors:
    - 404: Flight report not found (generate it first using POST /trips/{trip_id}/generate)
    - 403: User does not own this trip
    - 500: Database error

    Example:
        GET /trips/550e8400-e29b-41d4-a716-446655440000/report/flight

        Response:
        {
            "report_id": "...",
            "trip_id": "...",
            "generated_at": "2025-12-26T10:00:00Z",
            "confidence_score": 0.80,
            "content": {
                "recommended_flights": [...],
                "price_range": {"min": 450, "max": 1200, "average": 750},
                "airport_info": {...},
                "booking_tips": [...]
            },
            "sources": [...],
            "warnings": [...]
        }
    """
    user_id = token_payload["user_id"]

    try:
        # 1. Verify trip exists and user owns it
        trip_response = (
            supabase.table("trips").select("id, user_id").eq("id", trip_id).single().execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # 2. Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this report",
            )

        # 3. Retrieve flight report from report_sections table
        report_response = (
            supabase.table("report_sections")
            .select("*")
            .eq("trip_id", trip_id)
            .eq("section_type", "flight")
            .order("generated_at", desc=True)
            .limit(1)
            .execute()
        )

        if not report_response.data or len(report_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flight report not found for this trip. Generate the trip report first using POST /trips/{id}/generate",
            )

        # 4. Parse report data
        report = report_response.data[0]
        content = report["content"]

        # Convert confidence from integer (0-100) back to float (0.0-1.0)
        confidence_float = (
            float(report["confidence_score"]) / 100.0 if report.get("confidence_score") else 0.0
        )

        # 5. Build response
        return FlightReportResponse(
            report_id=report["id"],
            trip_id=report["trip_id"],
            generated_at=datetime.fromisoformat(report["generated_at"].replace("Z", "+00:00")),
            confidence_score=confidence_float,
            content=content,
            sources=[
                SourceReferenceResponse(**source) for source in report.get("sources", [])
            ],
            warnings=content.get("warnings", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("retrieve flight report", e, "Failed to retrieve flight report. Please try again.")


@router.get(
    "/{trip_id}/report",
    response_model=FullReportResponse,
    responses={
        404: {"model": ReportNotFoundError, "description": "Trip not found"},
        403: {"model": ReportUnauthorizedError, "description": "Unauthorized access"},
    },
)
async def get_full_report(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Get complete aggregated report for a trip

    Retrieves all generated report sections and combines them into a unified report.
    This endpoint returns the full trip intelligence including visa, destination,
    weather, itinerary, and flight information.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - Complete aggregated report with all available sections
    - List of available and missing sections
    - Overall confidence score

    Errors:
    - 404: Trip not found
    - 403: User does not own this trip
    - 500: Database error

    Example:
        GET /trips/550e8400-e29b-41d4-a716-446655440000/report

        Response:
        {
            "trip_id": "...",
            "trip_info": {...},
            "sections": {
                "visa": {...},
                "country": {...},
                "itinerary": {...}
            },
            "available_sections": ["visa", "country", "itinerary"],
            "missing_sections": ["flight", "weather"],
            "overall_confidence": 0.85,
            "is_complete": false
        }
    """
    from app.services.report_aggregator import report_aggregator

    user_id = token_payload["user_id"]

    try:
        # 1. Verify trip exists and user owns it
        trip_response = (
            supabase.table("trips").select("id, user_id").eq("id", trip_id).single().execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # 2. Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this report",
            )

        # 3. Aggregate report
        report = await report_aggregator.aggregate_report(trip_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found or no report data available",
            )

        # 4. Convert to response format
        sections_response = {}
        for section_type, section in report.sections.items():
            sections_response[section_type] = ReportSectionResponse(
                section_type=section.section_type,
                title=section.title,
                content=section.content,
                confidence_score=section.confidence_score,
                generated_at=section.generated_at,
                sources=section.sources,
            )

        return FullReportResponse(
            trip_id=report.trip_id,
            trip_info=TripInfoResponse(
                trip_id=report.trip_info.trip_id,
                title=report.trip_info.title,
                destination_country=report.trip_info.destination_country,
                destination_city=report.trip_info.destination_city,
                departure_date=report.trip_info.departure_date,
                return_date=report.trip_info.return_date,
                travelers=report.trip_info.travelers,
                status=report.trip_info.status,
                created_at=report.trip_info.created_at,
            ),
            sections=sections_response,
            available_sections=report.available_sections,
            missing_sections=report.missing_sections,
            overall_confidence=report.overall_confidence,
            generated_at=report.generated_at,
            is_complete=report.is_complete,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("retrieve report", e, "Failed to retrieve report. Please try again.")


@router.post(
    "/{trip_id}/report/pdf",
    response_model=PDFExportResponse,
    responses={
        404: {"model": ReportNotFoundError, "description": "Trip not found"},
        403: {"model": ReportUnauthorizedError, "description": "Unauthorized access"},
        500: {"model": PDFExportError, "description": "PDF generation failed"},
    },
)
async def export_report_pdf(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """
    Export trip report as PDF

    Generates a PDF document containing the complete trip report.
    The PDF is stored in Supabase Storage and a download URL is returned.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - PDF download URL

    Errors:
    - 404: Trip not found or no report sections available
    - 403: User does not own this trip
    - 500: PDF generation failed

    Example:
        POST /trips/550e8400-e29b-41d4-a716-446655440000/report/pdf

        Response:
        {
            "success": true,
            "pdf_url": "https://storage.supabase.co/..../report.pdf",
            "message": "PDF generated successfully"
        }
    """
    from app.services.pdf_generator import PDFGenerationError, pdf_generator
    from app.services.report_aggregator import report_aggregator

    user_id = token_payload["user_id"]

    try:
        # 1. Verify trip exists and user owns it
        trip_response = (
            supabase.table("trips").select("id, user_id").eq("id", trip_id).single().execute()
        )

        if not trip_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        # 2. Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to export this report",
            )

        # 3. Aggregate report
        report = await report_aggregator.aggregate_report(trip_id)

        if not report or len(report.sections) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No report sections available. Generate the trip report first.",
            )

        # 4. Generate PDF
        pdf_bytes = await pdf_generator.generate_pdf(report)

        # 5. Save to storage
        pdf_url = await pdf_generator.save_pdf_to_storage(trip_id, pdf_bytes, user_id)

        if pdf_url:
            return PDFExportResponse(
                success=True,
                pdf_url=pdf_url,
                message="PDF generated successfully",
            )
        else:
            # Fallback: Return PDF as base64 data URL if storage fails
            import base64

            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
            return PDFExportResponse(
                success=True,
                pdf_url=f"data:application/pdf;base64,{pdf_base64}",
                message="PDF generated (inline data)",
            )

    except HTTPException:
        raise
    except PDFGenerationError as e:
        log_and_raise_http_error("generate PDF", e, "PDF generation failed. Please try again.")
    except Exception as e:
        log_and_raise_http_error("export PDF", e, "Failed to export PDF. Please try again.")


# ============================================================================
# TRIP UPDATES AND RECALCULATION ENDPOINTS
# ============================================================================


@router.post("/{trip_id}/changes/preview", response_model=ChangePreviewResponse)
async def preview_changes(
    trip_id: str,
    preview_data: ChangePreviewRequest,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Preview changes before applying them to a trip.

    Returns a list of detected changes, affected agents, and estimated
    recalculation time. This helps users understand the impact of their
    changes before committing them.

    Path Parameters:
    - trip_id: UUID of the trip to preview changes for

    Request Body:
    - traveler_details: New traveler information (optional)
    - destinations: New list of destinations (optional)
    - trip_details: New trip planning details (optional)
    - preferences: New travel preferences (optional)

    Returns:
    - has_changes: Whether any changes were detected
    - changes: List of specific field changes
    - affected_agents: List of agents that will need recalculation
    - estimated_recalc_time: Estimated time for recalculation in seconds
    - requires_recalculation: Whether recalculation is recommended
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch existing trip
        existing_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not existing_response.data or len(existing_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )

        existing_trip = existing_response.data[0]

        # Prepare old and new trip data for comparison
        old_trip = {
            "traveler_details": existing_trip.get("traveler_details"),
            "destinations": existing_trip.get("destinations", []),
            "trip_details": existing_trip.get("trip_details"),
            "preferences": existing_trip.get("preferences"),
        }

        # Build new trip data (only include fields that were provided)
        new_trip = old_trip.copy()
        if preview_data.traveler_details:
            new_trip["traveler_details"] = preview_data.traveler_details.model_dump()
        if preview_data.destinations:
            new_trip["destinations"] = [d.model_dump() for d in preview_data.destinations]
        if preview_data.trip_details:
            new_trip["trip_details"] = preview_data.trip_details.model_dump(mode="json")
        if preview_data.preferences:
            new_trip["preferences"] = preview_data.preferences.model_dump()

        # Use ChangeDetector to analyze changes
        detector = ChangeDetector()
        result = detector.detect_changes(old_trip, new_trip)

        # Convert changes dict to list of FieldChange
        field_changes = [
            FieldChange(
                field=field,
                old_value=change.get("old"),
                new_value=change.get("new"),
            )
            for field, change in result.changes.items()
        ]

        # Determine if recalculation is needed
        # Only recommend recalc if trip has been generated before
        has_reports = existing_trip.get("status") in ["completed", "failed"]
        requires_recalc = result.has_changes and has_reports and len(result.affected_agents) > 0

        return ChangePreviewResponse(
            has_changes=result.has_changes,
            changes=field_changes,
            affected_agents=result.affected_agents,
            estimated_recalc_time=result.estimated_recalc_time,
            requires_recalculation=requires_recalc,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("preview changes", e, "Failed to preview changes. Please try again.")


@router.post("/{trip_id}/recalculate", response_model=RecalculationResponse)
async def recalculate_trip(
    trip_id: str,
    recalc_request: RecalculationRequest | None = None,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Trigger selective recalculation of AI agents for a trip.

    This endpoint queues a Celery task to re-run specified agents
    based on trip changes. If no agents are specified, it recalculates
    all agents that have been previously generated.

    Path Parameters:
    - trip_id: UUID of the trip to recalculate

    Request Body (optional):
    - agents: List of specific agents to recalculate (e.g., ["visa", "weather"])
    - force: Force recalculation even if no changes detected (default: false)

    Returns:
    - task_id: Celery task ID for tracking progress
    - status: Current status of recalculation
    - affected_agents: List of agents being recalculated
    - estimated_time: Estimated time in seconds
    - message: Status message
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        existing_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not existing_response.data or len(existing_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )

        existing_trip = existing_response.data[0]

        # Check if trip is in a recalculable state
        if existing_trip.get("status") == "processing":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trip is currently being processed. Please wait for completion.",
            )

        # Determine which agents to recalculate
        request_data = recalc_request or RecalculationRequest()
        agents_to_recalc = request_data.agents

        if not agents_to_recalc:
            # If no agents specified, get all agents that have reports
            reports_response = (
                supabase.table("report_sections")
                .select("section_type")
                .eq("trip_id", trip_id)
                .execute()
            )

            if reports_response.data:
                agents_to_recalc = list(set(r["section_type"] for r in reports_response.data))
            else:
                # No existing reports - use all default agents
                agents_to_recalc = [
                    "visa", "country", "weather", "currency",
                    "culture", "food", "attractions", "itinerary"
                ]

        # Calculate estimated time
        detector = ChangeDetector()
        estimated_time = detector.estimate_recalc_time(agents_to_recalc)

        # Queue the Celery task for selective recalculation
        try:
            from app.tasks.agent_jobs import execute_selective_recalc

            task = execute_selective_recalc.delay(trip_id, agents_to_recalc)
            task_id = task.id
        except Exception as celery_error:
            # If Celery is not available, return a mock response
            import uuid
            task_id = str(uuid.uuid4())

        # Update trip status to processing
        supabase.table("trips").update({
            "status": TripStatus.PROCESSING.value,
        }).eq("id", trip_id).execute()

        return RecalculationResponse(
            task_id=task_id,
            status=RecalculationStatusEnum.QUEUED,
            affected_agents=agents_to_recalc,
            estimated_time=estimated_time,
            message=f"Recalculation queued for {len(agents_to_recalc)} agent(s)",
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("trigger recalculation", e, "Failed to trigger recalculation. Please try again.")


@router.get("/{trip_id}/recalculation/status", response_model=RecalculationStatusResponse)
async def get_recalculation_status(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get the status of an ongoing recalculation for a trip.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - task_id: Celery task ID
    - status: Current status (queued, in_progress, completed, failed)
    - progress: Percentage complete (0-100)
    - completed_agents: List of agents that have completed
    - pending_agents: List of agents still pending
    - current_agent: Agent currently being processed
    - started_at: When recalculation started
    - estimated_completion: Estimated completion time
    - error: Error message if failed
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        trip_response = (
            supabase.table("trips")
            .select("id, status, recalc_task_id, recalc_started_at")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not trip_response.data or len(trip_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )

        trip = trip_response.data[0]
        task_id = trip.get("recalc_task_id")

        # If no active recalculation
        if not task_id or trip.get("status") != TripStatus.PROCESSING.value:
            return RecalculationStatusResponse(
                task_id=task_id or "",
                status=RecalculationStatusEnum.COMPLETED,
                progress=100.0,
                completed_agents=[],
                pending_agents=[],
                current_agent=None,
                started_at=None,
                estimated_completion=None,
                error=None,
            )

        # Try to get Celery task status
        try:
            from celery.result import AsyncResult
            from app.core.celery_app import celery_app

            result = AsyncResult(task_id, app=celery_app)

            if result.state == "PENDING":
                return RecalculationStatusResponse(
                    task_id=task_id,
                    status=RecalculationStatusEnum.QUEUED,
                    progress=0.0,
                    completed_agents=[],
                    pending_agents=[],
                    current_agent=None,
                    started_at=trip.get("recalc_started_at"),
                    estimated_completion=None,
                    error=None,
                )
            elif result.state == "STARTED" or result.state == "PROGRESS":
                info = result.info or {}
                return RecalculationStatusResponse(
                    task_id=task_id,
                    status=RecalculationStatusEnum.IN_PROGRESS,
                    progress=info.get("progress", 0.0),
                    completed_agents=info.get("completed_agents", []),
                    pending_agents=info.get("pending_agents", []),
                    current_agent=info.get("current_agent"),
                    started_at=trip.get("recalc_started_at"),
                    estimated_completion=info.get("estimated_completion"),
                    error=None,
                )
            elif result.state == "SUCCESS":
                return RecalculationStatusResponse(
                    task_id=task_id,
                    status=RecalculationStatusEnum.COMPLETED,
                    progress=100.0,
                    completed_agents=result.result.get("completed_agents", []) if result.result else [],
                    pending_agents=[],
                    current_agent=None,
                    started_at=trip.get("recalc_started_at"),
                    estimated_completion=None,
                    error=None,
                )
            elif result.state == "FAILURE":
                return RecalculationStatusResponse(
                    task_id=task_id,
                    status=RecalculationStatusEnum.FAILED,
                    progress=0.0,
                    completed_agents=[],
                    pending_agents=[],
                    current_agent=None,
                    started_at=trip.get("recalc_started_at"),
                    estimated_completion=None,
                    error=str(result.result) if result.result else "Unknown error",
                )
        except ImportError:
            # Celery not available, return based on trip status
            pass

        # Default response based on trip status
        return RecalculationStatusResponse(
            task_id=task_id or "",
            status=RecalculationStatusEnum.IN_PROGRESS if trip.get("status") == TripStatus.PROCESSING.value else RecalculationStatusEnum.COMPLETED,
            progress=50.0 if trip.get("status") == TripStatus.PROCESSING.value else 100.0,
            completed_agents=[],
            pending_agents=[],
            current_agent=None,
            started_at=trip.get("recalc_started_at"),
            estimated_completion=None,
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("get recalculation status", e, "Failed to get recalculation status.")


@router.post("/{trip_id}/recalculation/cancel", response_model=RecalculationCancelResponse)
async def cancel_recalculation(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Cancel an ongoing recalculation for a trip.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - task_id: The cancelled task ID
    - cancelled: Whether cancellation was successful
    - message: Status message
    - completed_agents: Agents that completed before cancellation
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        trip_response = (
            supabase.table("trips")
            .select("id, status, recalc_task_id")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not trip_response.data or len(trip_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )

        trip = trip_response.data[0]
        task_id = trip.get("recalc_task_id")

        # Check if there's an active recalculation
        if trip.get("status") != TripStatus.PROCESSING.value:
            return RecalculationCancelResponse(
                task_id=task_id or "",
                cancelled=False,
                message="No active recalculation to cancel",
                completed_agents=[],
            )

        completed_agents = []

        # Try to revoke Celery task
        if task_id:
            try:
                from celery.result import AsyncResult
                from app.core.celery_app import celery_app

                result = AsyncResult(task_id, app=celery_app)

                # Get completed agents before revoking
                if result.info and isinstance(result.info, dict):
                    completed_agents = result.info.get("completed_agents", [])

                # Revoke the task
                celery_app.control.revoke(task_id, terminate=True)

            except ImportError:
                # Celery not available
                pass

        # Update trip status back to completed (or previous state)
        supabase.table("trips").update({
            "status": TripStatus.COMPLETED.value,
            "recalc_task_id": None,
        }).eq("id", trip_id).execute()

        return RecalculationCancelResponse(
            task_id=task_id or "",
            cancelled=True,
            message="Recalculation cancelled successfully",
            completed_agents=completed_agents,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("cancel recalculation", e, "Failed to cancel recalculation.")


@router.put("/{trip_id}/with-recalc", response_model=TripUpdateWithRecalcResponse)
async def update_trip_with_recalc(
    trip_id: str,
    update_data: TripUpdateWithRecalcRequest,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Update a trip and optionally trigger selective recalculation.

    This is an enhanced update endpoint that:
    1. Detects what changed
    2. Updates the trip data
    3. Creates a version history entry
    4. Optionally triggers recalculation for affected agents

    Path Parameters:
    - trip_id: UUID of the trip to update

    Request Body:
    - traveler_details: Updated traveler information (optional)
    - destinations: Updated list of destinations (optional)
    - trip_details: Updated trip planning details (optional)
    - preferences: Updated travel preferences (optional)
    - auto_recalculate: Whether to automatically trigger recalculation (default: true)

    Returns:
    - trip: Updated trip object
    - recalculation: Recalculation task info (if triggered)
    - changes_applied: List of changes that were applied
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch existing trip
        existing_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not existing_response.data or len(existing_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )

        existing_trip = existing_response.data[0]

        # Check if trip can be updated
        if existing_trip.get("status") == "processing":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot update trip while processing. Please wait for completion.",
            )

        # Prepare old and new trip data
        old_trip = {
            "traveler_details": existing_trip.get("traveler_details"),
            "destinations": existing_trip.get("destinations", []),
            "trip_details": existing_trip.get("trip_details"),
            "preferences": existing_trip.get("preferences"),
        }

        # Build update data
        update_fields = {}
        new_trip = old_trip.copy()

        if update_data.traveler_details:
            update_fields["traveler_details"] = update_data.traveler_details.model_dump()
            new_trip["traveler_details"] = update_fields["traveler_details"]

        if update_data.destinations:
            update_fields["destinations"] = [d.model_dump() for d in update_data.destinations]
            new_trip["destinations"] = update_fields["destinations"]

        if update_data.trip_details:
            update_fields["trip_details"] = update_data.trip_details.model_dump(mode="json")
            new_trip["trip_details"] = update_fields["trip_details"]

        if update_data.preferences:
            update_fields["preferences"] = update_data.preferences.model_dump()
            new_trip["preferences"] = update_fields["preferences"]

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        # Detect changes
        detector = ChangeDetector()
        change_result = detector.detect_changes(old_trip, new_trip)

        # Create version history entry before updating
        version_number = existing_trip.get("version", 0) + 1
        try:
            supabase.table("trip_versions").insert({
                "trip_id": trip_id,
                "version_number": version_number - 1,  # Store the old version
                "trip_data": old_trip,
                "change_summary": f"Update before version {version_number}",
                "fields_changed": list(change_result.changes.keys()),
            }).execute()
        except Exception:
            # Version history table might not exist yet - that's OK
            pass

        # Update the trip
        update_fields["version"] = version_number
        update_response = (
            supabase.table("trips")
            .update(update_fields)
            .eq("id", trip_id)
            .execute()
        )

        if not update_response.data or len(update_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update trip",
            )

        updated_trip = update_response.data[0]

        # Convert changes to FieldChange list
        field_changes = [
            FieldChange(
                field=field,
                old_value=change.get("old"),
                new_value=change.get("new"),
            )
            for field, change in change_result.changes.items()
        ]

        # Optionally trigger recalculation
        recalculation = None
        if update_data.auto_recalculate and change_result.affected_agents:
            # Check if trip has been generated before
            has_reports = existing_trip.get("status") in ["completed", "failed"]

            if has_reports:
                try:
                    from app.tasks.agent_jobs import execute_selective_recalc

                    task = execute_selective_recalc.delay(trip_id, change_result.affected_agents)
                    task_id = task.id

                    # Update trip status
                    supabase.table("trips").update({
                        "status": TripStatus.PROCESSING.value,
                    }).eq("id", trip_id).execute()

                    recalculation = RecalculationResponse(
                        task_id=task_id,
                        status=RecalculationStatusEnum.QUEUED,
                        affected_agents=change_result.affected_agents,
                        estimated_time=change_result.estimated_recalc_time,
                        message=f"Recalculation queued for {len(change_result.affected_agents)} agent(s)",
                    )
                except Exception:
                    # Celery not available
                    pass

        # Build TripResponse from updated data
        trip_response = TripResponse(
            id=updated_trip["id"],
            user_id=updated_trip["user_id"],
            status=updated_trip.get("status", "draft"),
            created_at=updated_trip["created_at"],
            updated_at=updated_trip["updated_at"],
            traveler_details=updated_trip.get("traveler_details", {}),
            destinations=updated_trip.get("destinations", []),
            trip_details=updated_trip.get("trip_details", {}),
            preferences=updated_trip.get("preferences", {}),
            template_id=updated_trip.get("template_id"),
            auto_delete_at=updated_trip.get("auto_delete_at"),
        )

        return TripUpdateWithRecalcResponse(
            trip=trip_response,
            recalculation=recalculation,
            changes_applied=field_changes,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("update trip with recalc", e, "Failed to update trip. Please try again.")


# ============================================================================
# VERSION HISTORY ENDPOINTS
# ============================================================================


@router.get("/{trip_id}/versions", response_model=TripVersionListResponse)
async def list_trip_versions(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    List all versions of a trip.

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - trip_id: The trip ID
    - current_version: Current version number
    - versions: List of version summaries
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        trip_response = (
            supabase.table("trips")
            .select("id, version")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not trip_response.data or len(trip_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )

        current_version = trip_response.data[0].get("version", 1)

        # Fetch version history
        versions_response = (
            supabase.table("trip_versions")
            .select("*")
            .eq("trip_id", trip_id)
            .order("version_number", desc=True)
            .execute()
        )

        versions = []
        if versions_response.data:
            for v in versions_response.data:
                versions.append(TripVersionSummary(
                    version_number=v["version_number"],
                    created_at=v["created_at"],
                    change_summary=v.get("change_summary", ""),
                    fields_changed=v.get("fields_changed", []),
                ))

        return TripVersionListResponse(
            trip_id=trip_id,
            current_version=current_version,
            versions=versions,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("list versions", e, "Failed to list versions. Please try again.")


@router.get("/{trip_id}/versions/compare", response_model=VersionCompareResponse)
async def compare_trip_versions(
    trip_id: str,
    version_a: int = Query(..., ge=1, description="First version number to compare"),
    version_b: int = Query(..., ge=1, description="Second version number to compare"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Compare two versions of a trip to see what changed.

    Path Parameters:
    - trip_id: UUID of the trip

    Query Parameters:
    - version_a: First version number to compare
    - version_b: Second version number to compare

    Returns:
    - trip_id: The trip ID
    - version_a: First version number
    - version_b: Second version number
    - changes: List of field changes between versions
    - summary: Human-readable summary of changes
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        trip_response = (
            supabase.table("trips")
            .select("id")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not trip_response.data or len(trip_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )

        # Ensure version_a < version_b for consistent comparison
        v_min, v_max = min(version_a, version_b), max(version_a, version_b)

        # Fetch both versions
        versions_response = (
            supabase.table("trip_versions")
            .select("*")
            .eq("trip_id", trip_id)
            .in_("version_number", [v_min, v_max])
            .execute()
        )

        if not versions_response.data or len(versions_response.data) < 2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"One or both versions not found. Available versions may not include {version_a} and {version_b}.",
            )

        # Map versions by number
        version_map = {v["version_number"]: v for v in versions_response.data}

        if v_min not in version_map or v_max not in version_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {v_min if v_min not in version_map else v_max} not found",
            )

        data_a = version_map[v_min].get("trip_data", {})
        data_b = version_map[v_max].get("trip_data", {})

        # Compare the two versions
        changes = []
        all_keys = set(data_a.keys()) | set(data_b.keys())

        def compare_values(key: str, val_a, val_b, prefix: str = ""):
            """Recursively compare values and generate FieldChange objects."""
            field_name = f"{prefix}{key}" if prefix else key

            if val_a == val_b:
                return []

            # If both are dicts, compare nested
            if isinstance(val_a, dict) and isinstance(val_b, dict):
                nested_changes = []
                nested_keys = set(val_a.keys()) | set(val_b.keys())
                for nested_key in nested_keys:
                    nested_changes.extend(
                        compare_values(
                            nested_key,
                            val_a.get(nested_key),
                            val_b.get(nested_key),
                            f"{field_name}.",
                        )
                    )
                return nested_changes

            # Different values
            return [FieldChange(field=field_name, old_value=val_a, new_value=val_b)]

        for key in all_keys:
            val_a = data_a.get(key)
            val_b = data_b.get(key)
            changes.extend(compare_values(key, val_a, val_b))

        # Generate summary
        change_count = len(changes)
        if change_count == 0:
            summary = f"No changes between version {version_a} and version {version_b}"
        elif change_count == 1:
            summary = f"1 field changed between version {version_a} and version {version_b}"
        else:
            summary = f"{change_count} fields changed between version {version_a} and version {version_b}"

        return VersionCompareResponse(
            trip_id=trip_id,
            version_a=version_a,
            version_b=version_b,
            changes=changes,
            summary=summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("compare versions", e, "Failed to compare versions. Please try again.")


@router.post("/{trip_id}/versions/{version_number}/restore", response_model=TripVersionRestoreResponse)
async def restore_trip_version(
    trip_id: str,
    version_number: int,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Restore a trip to a previous version.

    This creates a new version with the restored data and optionally
    triggers recalculation.

    Path Parameters:
    - trip_id: UUID of the trip
    - version_number: Version number to restore

    Returns:
    - trip_id: The trip ID
    - restored_version: The version that was restored
    - new_version: The new version number after restore
    - recalculation: Recalculation task info (if triggered)
    """
    user_id = token_payload["user_id"]

    try:
        # Verify trip exists and belongs to user
        trip_response = (
            supabase.table("trips")
            .select("*")
            .eq("id", trip_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not trip_response.data or len(trip_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip {trip_id} not found",
            )

        current_trip = trip_response.data[0]
        current_version = current_trip.get("version", 1)

        # Fetch the version to restore
        version_response = (
            supabase.table("trip_versions")
            .select("*")
            .eq("trip_id", trip_id)
            .eq("version_number", version_number)
            .execute()
        )

        if not version_response.data or len(version_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_number} not found for trip {trip_id}",
            )

        version_data = version_response.data[0]
        trip_data = version_data.get("trip_data", {})

        # Save current state as a new version entry
        supabase.table("trip_versions").insert({
            "trip_id": trip_id,
            "version_number": current_version,
            "trip_data": {
                "traveler_details": current_trip.get("traveler_details"),
                "destinations": current_trip.get("destinations", []),
                "trip_details": current_trip.get("trip_details"),
                "preferences": current_trip.get("preferences"),
            },
            "change_summary": f"State before restoring to version {version_number}",
            "fields_changed": [],
        }).execute()

        # Restore the old version data
        new_version = current_version + 1
        update_fields = {
            "version": new_version,
            "traveler_details": trip_data.get("traveler_details"),
            "destinations": trip_data.get("destinations"),
            "trip_details": trip_data.get("trip_details"),
            "preferences": trip_data.get("preferences"),
        }

        supabase.table("trips").update(update_fields).eq("id", trip_id).execute()

        # Trigger full recalculation since we're restoring an old version
        recalculation = None
        if current_trip.get("status") in ["completed", "failed"]:
            all_agents = [
                "visa", "country", "weather", "currency",
                "culture", "food", "attractions", "itinerary"
            ]
            try:
                from app.tasks.agent_jobs import execute_selective_recalc

                task = execute_selective_recalc.delay(trip_id, all_agents)

                supabase.table("trips").update({
                    "status": TripStatus.PROCESSING.value,
                }).eq("id", trip_id).execute()

                detector = ChangeDetector()
                recalculation = RecalculationResponse(
                    task_id=task.id,
                    status=RecalculationStatusEnum.QUEUED,
                    affected_agents=all_agents,
                    estimated_time=detector.estimate_recalc_time(all_agents),
                    message="Full recalculation triggered after version restore",
                )
            except Exception:
                pass

        return TripVersionRestoreResponse(
            trip_id=trip_id,
            restored_version=version_number,
            new_version=new_version,
            recalculation=recalculation,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("restore version", e, "Failed to restore version. Please try again.")
