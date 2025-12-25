"""Trips API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from typing import Optional
from datetime import datetime, date
from uuid import uuid4
from app.core.supabase import supabase
from app.core.auth import verify_jwt_token
from app.core.config import settings
from app.models.trips import (
    TripCreateRequest,
    TripUpdateRequest,
    TripResponse,
    TripStatus,
    DraftSaveRequest,
    DraftResponse
)
from app.models.report import (
    VisaReportResponse,
    ReportNotFoundError,
    ReportUnauthorizedError,
    VisaRequirementResponse,
    ApplicationProcessResponse,
    EntryRequirementResponse,
    SourceReferenceResponse,
    CountryReportResponse,
    EmergencyContactResponse,
    PowerOutletResponse,
    TravelAdvisoryResponse,
)

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("")
async def list_trips(
    status_filter: Optional[str] = Query(None, description="Filter by trip status"),
    limit: int = Query(20, ge=1, le=100, description="Number of trips to return"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    token_payload: dict = Depends(verify_jwt_token)
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
        query = supabase.table("trips").select(
            "id, created_at, updated_at, status, trip_details, destinations"
        ).eq("user_id", user_id).order("created_at", desc=True).limit(limit)

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
                destination_name = f"{first_dest.get('city', '')}, {first_dest.get('country', '')}".strip(", ")

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

            items.append({
                "id": trip["id"],
                "destination": destination_name,
                "startDate": start_date,
                "endDate": end_date,
                "status": display_status,
                "createdAt": trip["created_at"],
                "deletionDate": trip.get("auto_delete_at", "")
            })

        # Determine if there are more results (simple pagination)
        next_cursor = None
        if len(items) == limit:
            # There might be more results
            next_cursor = items[-1]["createdAt"]

        return {
            "items": items,
            "nextCursor": next_cursor
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trips: {str(e)}"
        )


@router.get("/{trip_id}")
async def get_trip(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get detailed trip information

    Path Parameters:
    - trip_id: UUID of the trip

    Returns:
    - Complete trip object with all fields
    """
    user_id = token_payload["user_id"]

    try:
        response = supabase.table("trips").select("*").eq(
            "id", trip_id
        ).eq("user_id", user_id).single().execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trip: {str(e)}"
        )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TripResponse)
async def create_trip(
    trip_data: TripCreateRequest,
    token_payload: dict = Depends(verify_jwt_token),
    idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key")
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
            existing_response = supabase.table("trips").select("*").eq(
                "user_id", user_id
            ).eq("idempotency_key", idempotency_key).execute()

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
            "trip_details": trip_data.trip_details.model_dump(mode='json'),  # Convert dates to strings
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
                detail="Failed to create trip: No data returned from database"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trip: {str(e)}"
        )


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    trip_data: TripUpdateRequest,
    token_payload: dict = Depends(verify_jwt_token)
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
        existing_response = supabase.table("trips").select("*").eq(
            "id", trip_id
        ).eq("user_id", user_id).single().execute()

        if not existing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        existing_trip = existing_response.data

        # Check if trip status allows updates
        if existing_trip["status"] not in [TripStatus.DRAFT.value, TripStatus.PENDING.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update trip with status '{existing_trip['status']}'. Only 'draft' and 'pending' trips can be updated."
            )

        # Prepare update data (only include fields that are provided)
        update_record = {}

        if trip_data.traveler_details is not None:
            update_record["traveler_details"] = trip_data.traveler_details.model_dump()

        if trip_data.destinations is not None:
            update_record["destinations"] = [dest.model_dump() for dest in trip_data.destinations]

        if trip_data.trip_details is not None:
            update_record["trip_details"] = trip_data.trip_details.model_dump(mode='json')

        if trip_data.preferences is not None:
            update_record["preferences"] = trip_data.preferences.model_dump()

        # If no fields to update, return existing trip
        if not update_record:
            return existing_trip

        # Update trip in database
        response = supabase.table("trips").update(update_record).eq(
            "id", trip_id
        ).eq("user_id", user_id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update trip: No data returned from database"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update trip: {str(e)}"
        )


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
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
        existing_response = supabase.table("trips").select("status").eq(
            "id", trip_id
        ).eq("user_id", user_id).single().execute()

        if not existing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        trip_status = existing_response.data["status"]

        # Check if trip status allows deletion
        if trip_status == TripStatus.PROCESSING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete trip that is currently processing. Please wait for completion."
            )

        if trip_status == TripStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete completed trip. Completed trips are automatically deleted 30 days after return date."
            )

        # Delete trip
        delete_response = supabase.table("trips").delete().eq(
            "id", trip_id
        ).eq("user_id", user_id).execute()

        # Return 204 No Content on success
        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete trip: {str(e)}"
        )


@router.post("/{trip_id}/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_trip_report(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
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
        existing_response = supabase.table("trips").select("*").eq(
            "id", trip_id
        ).eq("user_id", user_id).single().execute()

        if not existing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        existing_trip = existing_response.data

        # Check if trip status allows report generation
        if existing_trip["status"] == TripStatus.PROCESSING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report generation already in progress for this trip"
            )

        if existing_trip["status"] == TripStatus.COMPLETED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report already generated for this trip"
            )

        if existing_trip["status"] == TripStatus.FAILED.value:
            # Allow retry for failed trips
            pass

        # Update trip status to 'processing'
        update_response = supabase.table("trips").update({
            "status": TripStatus.PROCESSING.value
        }).eq("id", trip_id).eq("user_id", user_id).execute()

        # Queue Celery task for report generation
        from app.tasks.agent_jobs import execute_orchestrator
        task = execute_orchestrator.delay(trip_id)

        return {
            "status": "queued",
            "task_id": task.id,
            "message": "Report generation started. You will be notified when complete."
        }

    except HTTPException:
        raise
    except Exception as e:
        # Rollback status update on failure
        try:
            supabase.table("trips").update({
                "status": TripStatus.FAILED.value
            }).eq("id", trip_id).eq("user_id", user_id).execute()
        except:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start report generation: {str(e)}"
        )


@router.get("/{trip_id}/status")
async def get_generation_status(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
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
        trip_response = supabase.table("trips").select("status, created_at, updated_at").eq(
            "id", trip_id
        ).eq("user_id", user_id).single().execute()

        if not trip_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        trip = trip_response.data

        # Get agent jobs for this trip
        jobs_response = supabase.table("agent_jobs").select("*").eq(
            "trip_id", trip_id
        ).order("created_at").execute()

        agent_jobs = jobs_response.data if jobs_response.data else []

        # Calculate progress
        total_agents = 10  # 10 specialized agents
        completed_count = sum(1 for job in agent_jobs if job["status"] == "completed")
        failed_count = sum(1 for job in agent_jobs if job["status"] == "failed")
        processing_job = next((job for job in agent_jobs if job["status"] == "processing"), None)

        progress = int((completed_count / total_agents) * 100) if total_agents > 0 else 0

        return {
            "status": trip["status"],
            "progress": progress,
            "current_agent": processing_job["agent_type"] if processing_job else None,
            "agents_completed": [job["agent_type"] for job in agent_jobs if job["status"] == "completed"],
            "agents_failed": [job["agent_type"] for job in agent_jobs if job["status"] == "failed"],
            "error": processing_job.get("error") if processing_job and processing_job.get("status") == "failed" else None,
            "started_at": agent_jobs[0]["created_at"] if agent_jobs else None,
            "completed_at": trip["updated_at"] if trip["status"] == "completed" else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get generation status: {str(e)}"
        )


# Draft Management Endpoints
@router.post("/drafts", status_code=status.HTTP_201_CREATED, response_model=DraftResponse)
async def save_draft(
    draft_data: DraftSaveRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
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
            "draft_data": draft_data.model_dump(exclude_none=True)
        }

        # Insert draft into database
        # Note: Using a separate 'trip_drafts' table (not in schema yet - would need migration)
        # For now, we'll store drafts as trips with 'draft' status
        trip_record = {
            "id": draft_id,
            "user_id": user_id,
            "status": TripStatus.DRAFT.value,
            "traveler_details": draft_data.traveler_details.model_dump() if draft_data.traveler_details else {},
            "destinations": [dest.model_dump() for dest in draft_data.destinations] if draft_data.destinations else [],
            "trip_details": draft_data.trip_details.model_dump(mode='json') if draft_data.trip_details else {},
            "preferences": draft_data.preferences.model_dump() if draft_data.preferences else {},
        }

        response = supabase.table("trips").insert(trip_record).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save draft"
            )

        return {
            "id": draft_id,
            "user_id": user_id,
            "created_at": response.data[0]["created_at"],
            "updated_at": response.data[0]["updated_at"],
            "draft_data": draft_data.model_dump(exclude_none=True)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save draft: {str(e)}"
        )


@router.get("/drafts")
async def get_drafts(
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Get all drafts for the authenticated user

    Returns:
    - List of draft objects
    """
    user_id = token_payload["user_id"]

    try:
        # Get all draft trips
        response = supabase.table("trips").select("*").eq(
            "user_id", user_id
        ).eq("status", TripStatus.DRAFT.value).order("updated_at", desc=True).execute()

        if not response.data:
            return []

        # Transform to draft format
        drafts = []
        for trip in response.data:
            drafts.append({
                "id": trip["id"],
                "user_id": trip["user_id"],
                "created_at": trip["created_at"],
                "updated_at": trip["updated_at"],
                "draft_data": {
                    "traveler_details": trip.get("traveler_details"),
                    "destinations": trip.get("destinations"),
                    "trip_details": trip.get("trip_details"),
                    "preferences": trip.get("preferences")
                }
            })

        return drafts

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get drafts: {str(e)}"
        )


@router.put("/drafts/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    draft_data: DraftSaveRequest,
    token_payload: dict = Depends(verify_jwt_token)
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
        existing_response = supabase.table("trips").select("*").eq(
            "id", draft_id
        ).eq("user_id", user_id).eq("status", TripStatus.DRAFT.value).single().execute()

        if not existing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )

        # Prepare update data
        update_record = {}

        if draft_data.traveler_details is not None:
            update_record["traveler_details"] = draft_data.traveler_details.model_dump()

        if draft_data.destinations is not None:
            update_record["destinations"] = [dest.model_dump() for dest in draft_data.destinations]

        if draft_data.trip_details is not None:
            update_record["trip_details"] = draft_data.trip_details.model_dump(mode='json')

        if draft_data.preferences is not None:
            update_record["preferences"] = draft_data.preferences.model_dump()

        # If no fields to update, return existing draft
        if not update_record:
            return {
                "id": draft_id,
                "user_id": user_id,
                "created_at": existing_response.data["created_at"],
                "updated_at": existing_response.data["updated_at"],
                "draft_data": draft_data.model_dump(exclude_none=True)
            }

        # Update draft
        response = supabase.table("trips").update(update_record).eq(
            "id", draft_id
        ).eq("user_id", user_id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update draft"
            )

        return {
            "id": draft_id,
            "user_id": user_id,
            "created_at": response.data[0]["created_at"],
            "updated_at": response.data[0]["updated_at"],
            "draft_data": draft_data.model_dump(exclude_none=True)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update draft: {str(e)}"
        )


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
    """
    Delete a draft

    Path Parameters:
    - draft_id: UUID of the draft
    """
    user_id = token_payload["user_id"]

    try:
        # Verify draft exists
        existing_response = supabase.table("trips").select("id").eq(
            "id", draft_id
        ).eq("user_id", user_id).eq("status", TripStatus.DRAFT.value).single().execute()

        if not existing_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )

        # Delete draft
        supabase.table("trips").delete().eq(
            "id", draft_id
        ).eq("user_id", user_id).execute()

        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete draft: {str(e)}"
        )


@router.get(
    "/{trip_id}/report/visa",
    response_model=VisaReportResponse,
    responses={
        404: {"model": ReportNotFoundError, "description": "Report not found"},
        403: {"model": ReportUnauthorizedError, "description": "Unauthorized access"},
    }
)
async def get_visa_report(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
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
        trip_response = supabase.table("trips").select("id, user_id").eq(
            "id", trip_id
        ).single().execute()

        if not trip_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        # 2. Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this report"
            )

        # 3. Retrieve visa report from report_sections table
        report_response = supabase.table("report_sections").select("*").eq(
            "trip_id", trip_id
        ).eq("section_type", "visa").order("generated_at", desc=True).limit(1).execute()

        if not report_response.data or len(report_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visa report not found for this trip. Generate the trip report first using POST /trips/{id}/generate"
            )

        # 4. Parse report data
        report = report_response.data[0]
        content = report["content"]

        # Convert confidence from integer (0-100) back to float (0.0-1.0)
        confidence_float = float(report["confidence_score"]) / 100.0 if report.get("confidence_score") else 0.0

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
            last_verified=datetime.fromisoformat(content["last_verified"].replace("Z", "+00:00"))
        )

    except HTTPException:
        raise
    except KeyError as e:
        # Handle missing fields in content data
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid report data format: missing field {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve visa report: {str(e)}"
        )


@router.get(
    "/{trip_id}/report/destination",
    response_model=CountryReportResponse,
    responses={
        404: {"model": ReportNotFoundError, "description": "Report not found"},
        403: {"model": ReportUnauthorizedError, "description": "Unauthorized access"},
    }
)
async def get_destination_report(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token)
):
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
        trip_response = supabase.table("trips").select("id, user_id").eq(
            "id", trip_id
        ).single().execute()

        if not trip_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        # 2. Check ownership
        if trip_response.data["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this report"
            )

        # 3. Retrieve country report from report_sections table
        report_response = supabase.table("report_sections").select("*").eq(
            "trip_id", trip_id
        ).eq("section_type", "country").order("generated_at", desc=True).limit(1).execute()

        if not report_response.data or len(report_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination report not found for this trip. Generate the trip report first using POST /trips/{id}/generate"
            )

        # 4. Parse report data
        report = report_response.data[0]
        content = report["content"]

        # Convert confidence from integer (0-100) back to float (0.0-1.0)
        confidence_float = float(report["confidence_score"]) / 100.0 if report.get("confidence_score") else 0.0

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
                EmergencyContactResponse(**contact)
                for contact in content["emergency_numbers"]
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
            warnings=content.get("warnings", [])
        )

    except HTTPException:
        raise
    except KeyError as e:
        # Handle missing fields in content data
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid report data format: missing field {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve destination report: {str(e)}"
        )
