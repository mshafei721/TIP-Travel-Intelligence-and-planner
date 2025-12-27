"""Profile and statistics API endpoints"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.auth import verify_jwt_token
from app.core.errors import log_and_raise_http_error

logger = logging.getLogger(__name__)
from app.core.gdpr import (
    AuditEventType,
    ConsentType,
    audit_logger,
    consent_manager,
    data_exporter,
    get_gdpr_rights_summary,
    retention_manager,
)
from app.core.supabase import supabase
from app.models.profile import (
    AccountDeletionRequest,
    ConsentUpdate,
    TravelerProfileUpdate,
    UserPreferences,
    UserProfileUpdate,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/statistics")
async def get_statistics(token_payload: dict = Depends(verify_jwt_token)):
    """
    Get user travel statistics

    Aggregates data from trips to calculate:
    - Total trips created
    - Unique countries visited (from completed trips)
    - Unique destinations explored (from completed trips)
    - Active trips (draft, pending, processing statuses)

    Returns:
    - statistics: Object with totalTrips, countriesVisited, destinationsExplored, activeTrips
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch all trips for user
        response = (
            supabase.table("trips")
            .select("id, status, destinations")
            .eq("user_id", user_id)
            .execute()
        )

        trips = response.data if response.data else []

        # Calculate statistics
        total_trips = len(trips)
        active_trips = len([t for t in trips if t["status"] in ["draft", "pending", "processing"]])

        # Count unique countries and destinations from completed trips
        completed_trips = [t for t in trips if t["status"] == "completed"]
        countries = set()
        destinations = set()

        for trip in completed_trips:
            if trip.get("destinations"):
                for dest in trip["destinations"]:
                    country = dest.get("country")
                    city = dest.get("city")
                    if country:
                        countries.add(country)
                    if city and country:
                        destinations.add(f"{city}, {country}")

        statistics = {
            "totalTrips": total_trips,
            "countriesVisited": len(countries),
            "destinationsExplored": len(destinations),
            "activeTrips": active_trips,
        }

        return {"statistics": statistics}

    except Exception as e:
        log_and_raise_http_error("calculate statistics", e, "Failed to calculate statistics. Please try again.")


@router.get("")
async def get_profile(token_payload: dict = Depends(verify_jwt_token)):
    """
    Get complete user profile

    Returns:
    - user: User profile from user_profiles table
    - travelerProfile: Traveler preferences from traveler_profiles table (if exists)
    - notificationSettings: Notification preferences (placeholder for now)
    """
    user_id = token_payload["user_id"]

    try:
        # Fetch user profile
        user_response = (
            supabase.table("user_profiles").select("*").eq("id", user_id).single().execute()
        )

        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        user_profile = user_response.data

        # Fetch traveler profile (optional)
        traveler_response = (
            supabase.table("traveler_profiles")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        traveler_profile = traveler_response.data if traveler_response.data else None

        # Notification settings (placeholder - will be implemented in user settings section)
        notification_settings = {
            "deletionReminders": True,
            "reportCompletion": True,
            "productUpdates": False,
        }

        return {
            "user": user_profile,
            "travelerProfile": traveler_profile,
            "notificationSettings": notification_settings,
        }

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("fetch profile", e, "Failed to fetch profile. Please try again.")


@router.put("")
async def update_profile(
    profile_update: UserProfileUpdate, token_payload: dict = Depends(verify_jwt_token)
):
    """
    Update user profile

    Updates display_name and/or avatar_url in user_profiles table

    Args:
    - profile_update: UserProfileUpdate with optional display_name and avatar_url

    Returns:
    - Updated user profile
    """
    user_id = token_payload["user_id"]

    # Build update dict with only provided fields
    update_data = {}
    if profile_update.display_name is not None:
        update_data["display_name"] = profile_update.display_name
    if profile_update.avatar_url is not None:
        update_data["avatar_url"] = profile_update.avatar_url

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    try:
        response = supabase.table("user_profiles").update(update_data).eq("id", user_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("update profile", e, "Failed to update profile. Please try again.")


@router.get("/traveler")
async def get_traveler_profile(token_payload: dict = Depends(verify_jwt_token)):
    """
    Get traveler profile

    Returns traveler profile from traveler_profiles table if it exists

    Returns:
    - Traveler profile or null if not yet created
    """
    user_id = token_payload["user_id"]

    try:
        response = (
            supabase.table("traveler_profiles")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        return response.data if response.data else None

    except Exception as e:
        log_and_raise_http_error("fetch traveler profile", e, "Failed to fetch traveler profile. Please try again.")


@router.put("/traveler")
async def update_traveler_profile(
    traveler_update: TravelerProfileUpdate,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Create or update traveler profile

    Creates a new traveler profile if one doesn't exist, otherwise updates existing

    Args:
    - traveler_update: TravelerProfileUpdate with optional fields

    Returns:
    - Created or updated traveler profile
    """
    user_id = token_payload["user_id"]

    try:
        # Check if traveler profile exists
        existing = (
            supabase.table("traveler_profiles")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        # Build update dict with only provided fields
        update_data = {}
        if traveler_update.nationality is not None:
            update_data["nationality"] = traveler_update.nationality
        if traveler_update.residency_country is not None:
            update_data["residency_country"] = traveler_update.residency_country
        if traveler_update.residency_status is not None:
            update_data["residency_status"] = traveler_update.residency_status
        if traveler_update.date_of_birth is not None:
            update_data["date_of_birth"] = traveler_update.date_of_birth.isoformat()
        if traveler_update.travel_style is not None:
            update_data["travel_style"] = traveler_update.travel_style.value
        if traveler_update.dietary_restrictions is not None:
            update_data["dietary_restrictions"] = traveler_update.dietary_restrictions
        if traveler_update.accessibility_needs is not None:
            update_data["accessibility_needs"] = traveler_update.accessibility_needs

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        if existing.data:
            # Update existing profile
            response = (
                supabase.table("traveler_profiles")
                .update(update_data)
                .eq("user_id", user_id)
                .execute()
            )
        else:
            # Create new profile - need all required fields
            if not all(
                key in update_data
                for key in ["nationality", "residency_country", "residency_status"]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Creating traveler profile requires nationality, "
                    "residency_country, and residency_status",
                )

            update_data["user_id"] = user_id
            if "travel_style" not in update_data:
                update_data["travel_style"] = "balanced"
            if "dietary_restrictions" not in update_data:
                update_data["dietary_restrictions"] = []

            response = supabase.table("traveler_profiles").insert(update_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or update traveler profile",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("update traveler profile", e, "Failed to update traveler profile. Please try again.")


@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferences, token_payload: dict = Depends(verify_jwt_token)
):
    """
    Update user preferences

    Updates preferences stored in user_profiles.preferences JSONB field

    Args:
    - preferences: UserPreferences with notification, language, currency, and unit settings

    Returns:
    - Updated user profile with new preferences
    """
    user_id = token_payload["user_id"]

    try:
        # Convert Pydantic model to dict for JSONB storage
        preferences_dict = preferences.model_dump()

        response = (
            supabase.table("user_profiles")
            .update({"preferences": preferences_dict})
            .eq("id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("update preferences", e, "Failed to update preferences. Please try again.")


@router.delete("")
async def delete_account(
    deletion_request: AccountDeletionRequest,
    request: Request,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Delete user account (GDPR Article 17 - Right to Erasure)

    Permanently deletes the user's account and all associated data.
    Requires confirmation text "DELETE MY ACCOUNT" to proceed.

    Due to CASCADE delete constraints, this will automatically delete:
    - user_profiles
    - traveler_profiles
    - trips
    - agent_jobs
    - report_sections
    - notifications
    - deletion_schedule entries
    - consent records

    This action is irreversible and complies with GDPR Article 17.

    Args:
    - deletion_request: AccountDeletionRequest with confirmation text

    Returns:
    - Success message
    """
    user_id = token_payload["user_id"]

    try:
        # Get client IP for audit logging
        client_ip = request.client.host if request.client else None

        # Log the deletion request for audit trail (before deletion)
        await audit_logger.log_event(
            event_type=AuditEventType.DELETION_REQUESTED,
            user_id=user_id,
            resource_type="account",
            action="full_account_deletion",
            ip_address=client_ip,
            details={"gdpr_article": "Article 17 - Right to Erasure"},
        )

        # Delete from user_profiles table
        # This will CASCADE delete all related data due to foreign key constraints
        response = supabase.table("user_profiles").delete().eq("id", user_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        # Log successful deletion
        await audit_logger.log_event(
            event_type=AuditEventType.ACCOUNT_DELETED,
            user_id=user_id,
            action="account_deleted",
            ip_address=client_ip,
        )

        return {"message": "Account deleted successfully", "user_id": user_id}

    except HTTPException:
        raise
    except Exception as e:
        log_and_raise_http_error("delete account", e, "Failed to delete account. Please try again.")


# =============================================================================
# GDPR Compliance Endpoints
# =============================================================================


@router.get("/data-export")
async def export_user_data(
    request: Request,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Export all user data (GDPR Articles 15 & 20)

    Implements Right to Access (Article 15) and Right to Data Portability (Article 20).
    Returns all personal data in a structured, machine-readable JSON format.

    Exported data includes:
    - User profile information
    - Traveler preferences
    - All trips and their details
    - Generated reports
    - Consent history
    - User preferences

    Returns:
    - Complete data export with GDPR compliance notice
    """
    user_id = token_payload["user_id"]

    try:
        # Get client IP for audit logging
        client_ip = request.client.host if request.client else None

        # Export all user data
        export_result = await data_exporter.export_user_data(user_id)

        # Log the data access for audit trail
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_EXPORTED,
            user_id=user_id,
            action="full_export",
            ip_address=client_ip,
            details={"categories": export_result.data_categories},
        )

        return export_result.model_dump(mode="json")

    except Exception as e:
        log_and_raise_http_error("export data", e, "Failed to export data. Please try again.")


@router.get("/consent")
async def get_user_consent(token_payload: dict = Depends(verify_jwt_token)):
    """
    Get user consent records (GDPR Article 7)

    Returns all consent records for the authenticated user, including:
    - Type of consent (terms, privacy, marketing, etc.)
    - Whether consent is currently granted
    - Timestamps for when consent was granted/revoked
    - Version of terms/policy consented to

    Returns:
    - List of consent records
    """
    user_id = token_payload["user_id"]

    try:
        consents = await consent_manager.get_user_consents(user_id)

        return {
            "user_id": user_id,
            "consents": consents,
            "available_consent_types": [ct.value for ct in ConsentType],
        }

    except Exception as e:
        log_and_raise_http_error("get consent records", e, "Failed to get consent records. Please try again.")


@router.put("/consent")
async def update_user_consent(
    consent_update: ConsentUpdate,
    request: Request,
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Update user consent (GDPR Article 7)

    Record a consent grant or revocation. Users can:
    - Grant consent for data processing, marketing, etc.
    - Revoke previously granted consent

    Args:
    - consent_update: ConsentUpdate with consent_type, granted, and version

    Returns:
    - Updated consent record
    """
    user_id = token_payload["user_id"]

    try:
        # Get client info for audit trail
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Convert string to ConsentType enum
        consent_type = ConsentType(consent_update.consent_type)

        # Record the consent
        result = await consent_manager.record_consent(
            user_id=user_id,
            consent_type=consent_type,
            granted=consent_update.granted,
            ip_address=client_ip,
            user_agent=user_agent,
            version=consent_update.version,
        )

        return {
            "message": f"Consent {'granted' if consent_update.granted else 'revoked'} successfully",
            "consent": result,
        }

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid consent type or value provided.",
        )
    except Exception as e:
        log_and_raise_http_error("update consent", e, "Failed to update consent. Please try again.")


@router.get("/gdpr-rights")
async def get_gdpr_rights():
    """
    Get GDPR rights information

    Returns information about implemented GDPR rights and how to exercise them.
    This endpoint is public and does not require authentication.

    Returns:
    - Summary of GDPR rights with corresponding API endpoints
    """
    return {
        "gdpr_rights": get_gdpr_rights_summary(),
        "data_retention": {
            "trips": f"{retention_manager.get_retention_policy('trips')} days",
            "reports": f"{retention_manager.get_retention_policy('reports')} days",
            "audit_logs": f"{retention_manager.get_retention_policy('audit_logs')} days",
            "deletion_grace_period": f"{retention_manager.get_deletion_grace_period()} days",
        },
        "contact": {
            "data_protection_officer": "dpo@tip-travel.com",
            "support_email": "privacy@tip-travel.com",
        },
    }


@router.get("/scheduled-deletions")
async def get_scheduled_deletions(token_payload: dict = Depends(verify_jwt_token)):
    """
    Get data scheduled for deletion

    Returns all trips and data scheduled for automatic deletion,
    allowing users to cancel deletion if needed.

    Returns:
    - List of items scheduled for deletion with their deletion dates
    """
    user_id = token_payload["user_id"]

    try:
        scheduled = await retention_manager.get_data_scheduled_for_deletion(user_id)

        return {
            "user_id": user_id,
            "scheduled_deletions": scheduled,
            "grace_period_days": retention_manager.get_deletion_grace_period(),
        }

    except Exception as e:
        log_and_raise_http_error("get scheduled deletions", e, "Failed to get scheduled deletions. Please try again.")
