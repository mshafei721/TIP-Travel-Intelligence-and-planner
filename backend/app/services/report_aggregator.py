"""
Report Aggregator Service

Aggregates all report sections for a trip into a unified report structure.
This service is used by:
- GET /trips/{id}/report - Returns full aggregated report
- POST /trips/{id}/report/pdf - Generates PDF from aggregated report
"""

import logging
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.supabase import supabase

logger = logging.getLogger(__name__)


class ReportSection(BaseModel):
    """Individual report section."""

    section_type: str
    title: str
    content: dict[str, Any]
    confidence_score: float  # 0.0 - 1.0
    generated_at: datetime
    sources: list[dict[str, Any]] = Field(default_factory=list)


class TripInfo(BaseModel):
    """Basic trip information for the report header."""

    trip_id: str
    title: str
    destination_country: str
    destination_city: str | None = None
    departure_date: str
    return_date: str | None = None
    travelers: int = 1
    status: str
    created_at: datetime


class AggregatedReport(BaseModel):
    """Complete aggregated report with all sections."""

    trip_id: str
    trip_info: TripInfo
    sections: dict[str, ReportSection] = Field(default_factory=dict)
    available_sections: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    overall_confidence: float = 0.0  # Average confidence across sections
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    is_complete: bool = False  # True if all expected sections are present


# Expected sections for a complete report
EXPECTED_SECTIONS = [
    "visa",
    "country",
    "weather",
    "currency",
    "culture",
    "food",
    "attractions",
    "itinerary",
    "flight",
]


class ReportAggregator:
    """
    Service for aggregating trip report sections.

    Fetches all generated sections from the database and combines them
    into a unified report structure suitable for display or PDF export.
    """

    def __init__(self):
        """Initialize the report aggregator."""
        self.supabase = supabase

    async def get_trip_info(self, trip_id: str) -> TripInfo | None:
        """
        Fetch basic trip information.

        Args:
            trip_id: Trip ID

        Returns:
            TripInfo or None if trip not found
        """
        try:
            response = self.supabase.table("trips").select("*").eq("id", trip_id).single().execute()

            if not response.data:
                return None

            trip = response.data

            # Build title from destination
            destination = trip.get("destination_city") or trip.get("destination_country", "Unknown")
            title = f"Trip to {destination}"

            return TripInfo(
                trip_id=trip["id"],
                title=title,
                destination_country=trip.get("destination_country", "Unknown"),
                destination_city=trip.get("destination_city"),
                departure_date=trip.get("departure_date", ""),
                return_date=trip.get("return_date"),
                travelers=trip.get("travelers", 1),
                status=trip.get("status", "draft"),
                created_at=datetime.fromisoformat(trip["created_at"].replace("Z", "+00:00")),
            )

        except Exception as e:
            logger.error(f"Error fetching trip info for {trip_id}: {e}")
            return None

    async def get_all_sections(self, trip_id: str) -> list[ReportSection]:
        """
        Fetch all report sections for a trip.

        Args:
            trip_id: Trip ID

        Returns:
            List of ReportSection objects
        """
        try:
            response = (
                self.supabase.table("report_sections")
                .select("*")
                .eq("trip_id", trip_id)
                .order("generated_at", desc=True)
                .execute()
            )

            if not response.data:
                return []

            # Group by section_type, keeping only the latest for each
            sections_by_type: dict[str, dict] = {}
            for row in response.data:
                section_type = row["section_type"]
                if section_type not in sections_by_type:
                    sections_by_type[section_type] = row

            sections = []
            for section_type, row in sections_by_type.items():
                # Convert confidence from integer (0-100) to float (0.0-1.0)
                confidence = (
                    float(row.get("confidence_score", 0)) / 100.0
                    if row.get("confidence_score")
                    else 0.0
                )

                sections.append(
                    ReportSection(
                        section_type=section_type,
                        title=row.get("title", section_type.title()),
                        content=row.get("content", {}),
                        confidence_score=confidence,
                        generated_at=datetime.fromisoformat(
                            row["generated_at"].replace("Z", "+00:00")
                        ),
                        sources=row.get("sources", []),
                    )
                )

            return sections

        except Exception as e:
            logger.error(f"Error fetching sections for trip {trip_id}: {e}")
            return []

    async def aggregate_report(self, trip_id: str) -> AggregatedReport | None:
        """
        Aggregate all report sections into a unified report.

        Args:
            trip_id: Trip ID

        Returns:
            AggregatedReport or None if trip not found
        """
        # Get trip info
        trip_info = await self.get_trip_info(trip_id)
        if not trip_info:
            logger.warning(f"Trip not found: {trip_id}")
            return None

        # Get all sections
        sections_list = await self.get_all_sections(trip_id)

        # Build sections dict
        sections: dict[str, ReportSection] = {}
        for section in sections_list:
            sections[section.section_type] = section

        # Determine available and missing sections
        available_sections = list(sections.keys())
        missing_sections = [s for s in EXPECTED_SECTIONS if s not in available_sections]

        # Calculate overall confidence
        if sections:
            total_confidence = sum(s.confidence_score for s in sections.values())
            overall_confidence = total_confidence / len(sections)
        else:
            overall_confidence = 0.0

        # Check if report is complete
        is_complete = len(missing_sections) == 0

        return AggregatedReport(
            trip_id=trip_id,
            trip_info=trip_info,
            sections=sections,
            available_sections=available_sections,
            missing_sections=missing_sections,
            overall_confidence=overall_confidence,
            generated_at=datetime.utcnow(),
            is_complete=is_complete,
        )

    async def get_section(self, trip_id: str, section_type: str) -> ReportSection | None:
        """
        Get a specific section for a trip.

        Args:
            trip_id: Trip ID
            section_type: Type of section (visa, country, etc.)

        Returns:
            ReportSection or None if not found
        """
        try:
            response = (
                self.supabase.table("report_sections")
                .select("*")
                .eq("trip_id", trip_id)
                .eq("section_type", section_type)
                .order("generated_at", desc=True)
                .limit(1)
                .execute()
            )

            if not response.data or len(response.data) == 0:
                return None

            row = response.data[0]

            # Convert confidence from integer (0-100) to float (0.0-1.0)
            confidence = (
                float(row.get("confidence_score", 0)) / 100.0
                if row.get("confidence_score")
                else 0.0
            )

            return ReportSection(
                section_type=section_type,
                title=row.get("title", section_type.title()),
                content=row.get("content", {}),
                confidence_score=confidence,
                generated_at=datetime.fromisoformat(row["generated_at"].replace("Z", "+00:00")),
                sources=row.get("sources", []),
            )

        except Exception as e:
            logger.error(f"Error fetching section {section_type} for trip {trip_id}: {e}")
            return None


# Singleton instance
report_aggregator = ReportAggregator()
