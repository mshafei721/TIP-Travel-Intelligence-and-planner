"""
GDPR Compliance Module for TIP API

Implements GDPR requirements:
- Right to Access (Article 15): Data export functionality
- Right to Erasure (Article 17): Account and data deletion
- Right to Data Portability (Article 20): Machine-readable export
- Consent Management: Track and manage user consent
- Data Retention: Automatic cleanup of expired data
- Audit Logging: Track data access and modifications
"""

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.supabase import supabase

logger = logging.getLogger(__name__)


# =============================================================================
# GDPR Configuration
# =============================================================================

class GDPRConfig:
    """GDPR compliance configuration."""

    # Data retention periods (in days)
    TRIP_RETENTION_DAYS: int = settings.TRIP_DATA_RETENTION_DAYS  # Default 30
    AGENT_JOB_RETENTION_DAYS: int = 30
    AUDIT_LOG_RETENTION_DAYS: int = 365  # 1 year for compliance
    DELETION_GRACE_PERIOD_DAYS: int = 7  # Time before actual deletion

    # Data categories
    PERSONAL_DATA_FIELDS = [
        "email",
        "display_name",
        "date_of_birth",
        "nationality",
        "residency_country",
        "residency_status",
        "avatar_url",
    ]

    # Consent types
    CONSENT_TYPES = [
        "terms_of_service",
        "privacy_policy",
        "marketing_emails",
        "data_processing",
        "third_party_sharing",
    ]


# =============================================================================
# Consent Types
# =============================================================================

class ConsentType(str, Enum):
    """Types of consent that can be given/revoked."""

    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    MARKETING_EMAILS = "marketing_emails"
    DATA_PROCESSING = "data_processing"
    THIRD_PARTY_SHARING = "third_party_sharing"
    ANALYTICS = "analytics"


class ConsentAction(str, Enum):
    """Actions on consent."""

    GRANTED = "granted"
    REVOKED = "revoked"
    UPDATED = "updated"


# =============================================================================
# Audit Event Types
# =============================================================================

class AuditEventType(str, Enum):
    """Types of audit events for GDPR compliance."""

    # Data Access
    DATA_ACCESSED = "data_accessed"
    DATA_EXPORTED = "data_exported"

    # Data Modification
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"

    # Account Events
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_DELETED = "account_deleted"
    DELETION_REQUESTED = "deletion_requested"
    DELETION_CANCELLED = "deletion_cancelled"

    # Consent Events
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"

    # Security Events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"


# =============================================================================
# Models
# =============================================================================

class ConsentRecord(BaseModel):
    """Record of user consent."""

    consent_type: ConsentType
    granted: bool
    granted_at: datetime | None = None
    revoked_at: datetime | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    version: str = "1.0"  # Version of terms/policy consented to


class AuditLogEntry(BaseModel):
    """Audit log entry for GDPR compliance."""

    event_type: AuditEventType
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resource_type: str | None = None  # e.g., "trip", "profile", "report"
    resource_id: str | None = None
    action: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    details: dict | None = None


class DataExportResult(BaseModel):
    """Result of a data export request."""

    user_id: str
    export_date: datetime
    data_categories: list[str]
    data: dict[str, Any]
    format: str = "json"
    gdpr_notice: str = (
        "This export contains all personal data we hold about you, "
        "in compliance with GDPR Article 15 (Right of Access) and "
        "Article 20 (Right to Data Portability)."
    )


# =============================================================================
# Audit Logging
# =============================================================================

class GDPRAuditLogger:
    """Handles GDPR-compliant audit logging."""

    def __init__(self):
        self.logger = logging.getLogger("app.gdpr.audit")

    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        action: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict | None = None,
    ) -> None:
        """Log a GDPR audit event."""
        entry = AuditLogEntry(
            event_type=event_type,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )

        # Log to structured logger
        self.logger.info(
            f"GDPR Audit: {event_type.value}",
            extra={
                "gdpr_audit": True,
                "event_type": event_type.value,
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
            }
        )

        # Store in database for compliance records
        try:
            supabase.table("gdpr_audit_log").insert({
                "event_type": event_type.value,
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details,
                "created_at": entry.timestamp.isoformat(),
            }).execute()
        except Exception as e:
            # Log error but don't fail the operation
            self.logger.error(f"Failed to store audit log: {e}")

    async def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Log data access for GDPR compliance."""
        await self.log_event(
            event_type=AuditEventType.DATA_ACCESSED,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
        )

    async def log_data_export(
        self,
        user_id: str,
        export_categories: list[str],
        ip_address: str | None = None,
    ) -> None:
        """Log data export request."""
        await self.log_event(
            event_type=AuditEventType.DATA_EXPORTED,
            user_id=user_id,
            action="full_export",
            details={"categories": export_categories},
            ip_address=ip_address,
        )

    async def log_deletion_request(
        self,
        user_id: str,
        deletion_type: str,
        resource_id: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Log deletion request for GDPR compliance."""
        await self.log_event(
            event_type=AuditEventType.DELETION_REQUESTED,
            user_id=user_id,
            resource_type=deletion_type,
            resource_id=resource_id,
            ip_address=ip_address,
        )


# Global audit logger instance
audit_logger = GDPRAuditLogger()


# =============================================================================
# Data Export (Right to Access / Portability)
# =============================================================================

class DataExporter:
    """
    Handles GDPR data export requests.

    Implements:
    - Article 15: Right of Access
    - Article 20: Right to Data Portability
    """

    async def export_user_data(self, user_id: str) -> DataExportResult:
        """
        Export all personal data for a user.

        Returns a comprehensive export including:
        - Profile data
        - Traveler preferences
        - All trips and reports
        - Consent records
        - Activity history
        """
        export_data: dict[str, Any] = {}
        categories: list[str] = []

        # 1. User Profile
        try:
            profile_response = (
                supabase.table("user_profiles")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
            if profile_response.data:
                export_data["profile"] = self._sanitize_for_export(
                    profile_response.data
                )
                categories.append("profile")
        except Exception as e:
            logger.warning(f"Could not export profile: {e}")

        # 2. Traveler Profile
        try:
            traveler_response = (
                supabase.table("traveler_profiles")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            if traveler_response.data:
                export_data["traveler_profile"] = self._sanitize_for_export(
                    traveler_response.data[0] if traveler_response.data else None
                )
                categories.append("traveler_profile")
        except Exception as e:
            logger.warning(f"Could not export traveler profile: {e}")

        # 3. All Trips
        try:
            trips_response = (
                supabase.table("trips")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            if trips_response.data:
                export_data["trips"] = [
                    self._sanitize_for_export(trip)
                    for trip in trips_response.data
                ]
                categories.append("trips")
        except Exception as e:
            logger.warning(f"Could not export trips: {e}")

        # 4. Report Sections (for all trips)
        try:
            if export_data.get("trips"):
                trip_ids = [trip["id"] for trip in export_data["trips"]]
                reports_response = (
                    supabase.table("report_sections")
                    .select("*")
                    .in_("trip_id", trip_ids)
                    .execute()
                )
                if reports_response.data:
                    export_data["reports"] = [
                        self._sanitize_for_export(report)
                        for report in reports_response.data
                    ]
                    categories.append("reports")
        except Exception as e:
            logger.warning(f"Could not export reports: {e}")

        # 5. Consent Records
        try:
            consent_response = (
                supabase.table("user_consents")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            if consent_response.data:
                export_data["consent_history"] = consent_response.data
                categories.append("consent_history")
        except Exception as e:
            # Consent table may not exist yet
            logger.debug(f"Could not export consent records: {e}")

        # 6. Preferences
        if export_data.get("profile", {}).get("preferences"):
            export_data["preferences"] = export_data["profile"]["preferences"]
            categories.append("preferences")

        # Log the export for audit trail
        await audit_logger.log_data_export(user_id, categories)

        return DataExportResult(
            user_id=user_id,
            export_date=datetime.now(timezone.utc),
            data_categories=categories,
            data=export_data,
        )

    def _sanitize_for_export(self, data: dict | None) -> dict | None:
        """Remove internal fields not relevant to the user."""
        if data is None:
            return None

        # Fields to exclude from export
        internal_fields = [
            "idempotency_key",
            "internal_notes",
        ]

        return {k: v for k, v in data.items() if k not in internal_fields}

    def export_to_json(self, export_result: DataExportResult) -> str:
        """Convert export to JSON string."""
        return json.dumps(
            export_result.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
        )


# Global exporter instance
data_exporter = DataExporter()


# =============================================================================
# Consent Management
# =============================================================================

class ConsentManager:
    """
    Manages user consent for GDPR compliance.

    Tracks:
    - Terms of service acceptance
    - Privacy policy acceptance
    - Marketing consent
    - Data processing consent
    """

    async def record_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        granted: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
        version: str = "1.0",
    ) -> dict:
        """Record a consent action."""
        now = datetime.now(timezone.utc)

        consent_record = {
            "user_id": user_id,
            "consent_type": consent_type.value,
            "granted": granted,
            "granted_at": now.isoformat() if granted else None,
            "revoked_at": now.isoformat() if not granted else None,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "version": version,
            "created_at": now.isoformat(),
        }

        try:
            # Upsert consent record
            supabase.table("user_consents").upsert(
                consent_record, on_conflict="user_id,consent_type"
            ).execute()

            # Log the consent action
            event_type = (
                AuditEventType.CONSENT_GRANTED
                if granted
                else AuditEventType.CONSENT_REVOKED
            )
            await audit_logger.log_event(
                event_type=event_type,
                user_id=user_id,
                action=consent_type.value,
                ip_address=ip_address,
                details={"version": version, "granted": granted},
            )

            logger.info(
                f"Consent {'granted' if granted else 'revoked'}",
                extra={
                    "user_id": user_id,
                    "consent_type": consent_type.value,
                    "granted": granted,
                }
            )

            return consent_record

        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
            raise

    async def get_user_consents(self, user_id: str) -> list[dict]:
        """Get all consent records for a user."""
        try:
            response = (
                supabase.table("user_consents")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to get consents: {e}")
            return []

    async def has_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
    ) -> bool:
        """Check if user has granted a specific consent."""
        try:
            response = (
                supabase.table("user_consents")
                .select("granted")
                .eq("user_id", user_id)
                .eq("consent_type", consent_type.value)
                .single()
                .execute()
            )
            return response.data.get("granted", False) if response.data else False
        except Exception:
            return False

    async def revoke_all_marketing_consent(self, user_id: str) -> None:
        """Revoke all marketing-related consent."""
        marketing_consents = [
            ConsentType.MARKETING_EMAILS,
            ConsentType.ANALYTICS,
        ]

        for consent_type in marketing_consents:
            await self.record_consent(
                user_id=user_id,
                consent_type=consent_type,
                granted=False,
            )


# Global consent manager instance
consent_manager = ConsentManager()


# =============================================================================
# Data Retention
# =============================================================================

class DataRetentionManager:
    """Manages data retention policies for GDPR compliance."""

    def get_retention_policy(self, data_type: str) -> int:
        """Get retention period in days for a data type."""
        policies = {
            "trips": GDPRConfig.TRIP_RETENTION_DAYS,
            "agent_jobs": GDPRConfig.AGENT_JOB_RETENTION_DAYS,
            "audit_logs": GDPRConfig.AUDIT_LOG_RETENTION_DAYS,
            "reports": GDPRConfig.TRIP_RETENTION_DAYS,
            "pdfs": GDPRConfig.TRIP_RETENTION_DAYS,
        }
        return policies.get(data_type, 30)

    def get_deletion_grace_period(self) -> int:
        """Get the grace period before actual deletion."""
        return GDPRConfig.DELETION_GRACE_PERIOD_DAYS

    async def get_data_scheduled_for_deletion(self, user_id: str) -> list[dict]:
        """Get all data scheduled for deletion for a user."""
        try:
            response = (
                supabase.table("deletion_schedule")
                .select("*")
                .eq("status", "pending")
                .execute()
            )

            # Filter to get trips belonging to this user
            if response.data:
                trip_ids = [d["trip_id"] for d in response.data]
                trips_response = (
                    supabase.table("trips")
                    .select("id, user_id")
                    .in_("id", trip_ids)
                    .eq("user_id", user_id)
                    .execute()
                )
                user_trip_ids = {t["id"] for t in (trips_response.data or [])}

                return [
                    d for d in response.data
                    if d["trip_id"] in user_trip_ids
                ]

            return []

        except Exception as e:
            logger.error(f"Failed to get scheduled deletions: {e}")
            return []


# Global retention manager instance
retention_manager = DataRetentionManager()


# =============================================================================
# GDPR Rights Summary
# =============================================================================

GDPR_RIGHTS_INFO = {
    "right_to_access": {
        "article": "Article 15",
        "description": (
            "You have the right to obtain confirmation of whether personal "
            "data concerning you is being processed and access to that data."
        ),
        "endpoint": "GET /api/profile/data-export",
        "implemented": True,
    },
    "right_to_rectification": {
        "article": "Article 16",
        "description": "You have the right to have inaccurate personal data corrected.",
        "endpoint": "PUT /api/profile",
        "implemented": True,
    },
    "right_to_erasure": {
        "article": "Article 17",
        "description": (
            "You have the right to have your personal data erased "
            "('right to be forgotten')."
        ),
        "endpoint": "DELETE /api/profile",
        "implemented": True,
    },
    "right_to_portability": {
        "article": "Article 20",
        "description": (
            "You have the right to receive your personal data in a structured, "
            "commonly used, machine-readable format."
        ),
        "endpoint": "GET /api/profile/data-export",
        "implemented": True,
    },
    "right_to_object": {
        "article": "Article 21",
        "description": (
            "You have the right to object to processing of your personal "
            "data for direct marketing."
        ),
        "endpoint": "PUT /api/profile/preferences",
        "implemented": True,
    },
    "right_to_withdraw_consent": {
        "article": "Article 7",
        "description": "You have the right to withdraw consent at any time.",
        "endpoint": "PUT /api/profile/consent",
        "implemented": True,
    },
}


def get_gdpr_rights_summary() -> dict:
    """Get a summary of implemented GDPR rights."""
    return GDPR_RIGHTS_INFO
