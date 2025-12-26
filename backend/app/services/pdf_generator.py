"""
PDF Generator Service

Generates PDF reports from aggregated trip data using Playwright.
"""

import asyncio
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from app.services.report_aggregator import AggregatedReport, ReportSection

logger = logging.getLogger(__name__)


class PDFGenerationError(Exception):
    """Error during PDF generation."""

    pass


class PDFGenerator:
    """
    Service for generating PDF reports from trip data.

    Uses Playwright to render HTML templates and convert to PDF.
    Falls back to simple HTML-to-PDF if Playwright is not available.
    """

    def __init__(self):
        """Initialize PDF generator."""
        self._playwright_available: bool | None = None

    async def _check_playwright(self) -> bool:
        """Check if Playwright is available."""
        if self._playwright_available is not None:
            return self._playwright_available

        try:
            from playwright.async_api import async_playwright

            self._playwright_available = True
        except ImportError:
            logger.warning("Playwright not installed. PDF generation will use fallback method.")
            self._playwright_available = False

        return self._playwright_available

    def _generate_html(self, report: AggregatedReport) -> str:
        """
        Generate HTML content for the PDF.

        Args:
            report: Aggregated report data

        Returns:
            HTML string
        """
        # Build sections HTML
        sections_html = ""

        # Order sections for display
        section_order = [
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

        for section_type in section_order:
            if section_type in report.sections:
                section = report.sections[section_type]
                sections_html += self._render_section(section)

        # Format dates
        departure_date = report.trip_info.departure_date
        return_date = report.trip_info.return_date or "One-way"

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trip Report - {report.trip_info.title}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background: #fff;
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #3b82f6;
        }}

        .header h1 {{
            font-size: 28px;
            color: #1e3a5f;
            margin-bottom: 8px;
        }}

        .header .subtitle {{
            font-size: 16px;
            color: #64748b;
        }}

        .trip-info {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}

        .trip-info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}

        .trip-info-item {{
            display: flex;
            flex-direction: column;
        }}

        .trip-info-label {{
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .trip-info-value {{
            font-size: 16px;
            color: #1e3a5f;
            font-weight: 500;
        }}

        .section {{
            margin-bottom: 30px;
            page-break-inside: avoid;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .section-icon {{
            width: 32px;
            height: 32px;
            background: #3b82f6;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
        }}

        .section-title {{
            font-size: 20px;
            color: #1e3a5f;
            font-weight: 600;
        }}

        .section-confidence {{
            margin-left: auto;
            font-size: 12px;
            color: #64748b;
            background: #f1f5f9;
            padding: 4px 8px;
            border-radius: 4px;
        }}

        .section-content {{
            padding: 15px;
            background: #fafafa;
            border-radius: 8px;
        }}

        .content-item {{
            margin-bottom: 12px;
        }}

        .content-label {{
            font-weight: 600;
            color: #374151;
            margin-bottom: 4px;
        }}

        .content-value {{
            color: #4b5563;
        }}

        .list-item {{
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }}

        .list-item:last-child {{
            border-bottom: none;
        }}

        .warning {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 0 4px 4px 0;
        }}

        .tip {{
            background: #d1fae5;
            border-left: 4px solid #10b981;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 0 4px 4px 0;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
        }}

        .missing-sections {{
            background: #fef2f2;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}

        .missing-sections h3 {{
            color: #991b1b;
            font-size: 14px;
            margin-bottom: 8px;
        }}

        .missing-sections ul {{
            list-style: none;
            color: #7f1d1d;
        }}

        @media print {{
            body {{
                padding: 20px;
            }}
            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report.trip_info.title}</h1>
        <p class="subtitle">Travel Intelligence Report</p>
    </div>

    <div class="trip-info">
        <div class="trip-info-grid">
            <div class="trip-info-item">
                <span class="trip-info-label">Destination</span>
                <span class="trip-info-value">{report.trip_info.destination_city or report.trip_info.destination_country}</span>
            </div>
            <div class="trip-info-item">
                <span class="trip-info-label">Country</span>
                <span class="trip-info-value">{report.trip_info.destination_country}</span>
            </div>
            <div class="trip-info-item">
                <span class="trip-info-label">Departure</span>
                <span class="trip-info-value">{departure_date}</span>
            </div>
            <div class="trip-info-item">
                <span class="trip-info-label">Return</span>
                <span class="trip-info-value">{return_date}</span>
            </div>
            <div class="trip-info-item">
                <span class="trip-info-label">Travelers</span>
                <span class="trip-info-value">{report.trip_info.travelers}</span>
            </div>
            <div class="trip-info-item">
                <span class="trip-info-label">Overall Confidence</span>
                <span class="trip-info-value">{report.overall_confidence:.0%}</span>
            </div>
        </div>
    </div>

    {self._render_missing_sections(report.missing_sections) if report.missing_sections else ""}

    {sections_html}

    <div class="footer">
        <p>Generated by TIP - Travel Intelligence & Planner</p>
        <p>Report generated on {report.generated_at.strftime('%B %d, %Y at %H:%M UTC')}</p>
    </div>
</body>
</html>
"""
        return html

    def _render_missing_sections(self, missing: list[str]) -> str:
        """Render missing sections warning."""
        items = "".join(f"<li>{s.title()}</li>" for s in missing)
        return f"""
        <div class="missing-sections">
            <h3>Missing Sections</h3>
            <p>The following sections are not yet generated:</p>
            <ul>{items}</ul>
        </div>
        """

    def _render_section(self, section: ReportSection) -> str:
        """
        Render a single section as HTML.

        Args:
            section: Report section data

        Returns:
            HTML string for the section
        """
        icon_map = {
            "visa": "🛂",
            "country": "🌍",
            "weather": "☀️",
            "currency": "💰",
            "culture": "🎭",
            "food": "🍽️",
            "attractions": "🏛️",
            "itinerary": "📅",
            "flight": "✈️",
        }

        icon = icon_map.get(section.section_type, "📄")

        # Render content based on section type
        content_html = self._render_section_content(section)

        return f"""
        <div class="section">
            <div class="section-header">
                <div class="section-icon">{icon}</div>
                <h2 class="section-title">{section.title}</h2>
                <span class="section-confidence">{section.confidence_score:.0%} confidence</span>
            </div>
            <div class="section-content">
                {content_html}
            </div>
        </div>
        """

    def _render_section_content(self, section: ReportSection) -> str:
        """
        Render section content as HTML based on section type.

        Args:
            section: Report section

        Returns:
            HTML content string
        """
        content = section.content

        if section.section_type == "visa":
            return self._render_visa_content(content)
        elif section.section_type == "country":
            return self._render_country_content(content)
        elif section.section_type == "weather":
            return self._render_weather_content(content)
        elif section.section_type == "itinerary":
            return self._render_itinerary_content(content)
        elif section.section_type == "flight":
            return self._render_flight_content(content)
        else:
            # Generic rendering for other sections
            return self._render_generic_content(content)

    def _render_visa_content(self, content: dict[str, Any]) -> str:
        """Render visa section content."""
        visa_req = content.get("visa_requirement", {})
        app_process = content.get("application_process", {})
        entry_req = content.get("entry_requirements", {})

        html = f"""
        <div class="content-item">
            <div class="content-label">Visa Required</div>
            <div class="content-value">{"Yes" if visa_req.get("visa_required") else "No"}</div>
        </div>
        """

        if visa_req.get("visa_type"):
            html += f"""
            <div class="content-item">
                <div class="content-label">Visa Type</div>
                <div class="content-value">{visa_req.get("visa_type")}</div>
            </div>
            """

        if visa_req.get("max_stay_days"):
            html += f"""
            <div class="content-item">
                <div class="content-label">Maximum Stay</div>
                <div class="content-value">{visa_req.get("max_stay_days")} days</div>
            </div>
            """

        if app_process.get("processing_time"):
            html += f"""
            <div class="content-item">
                <div class="content-label">Processing Time</div>
                <div class="content-value">{app_process.get("processing_time")}</div>
            </div>
            """

        # Warnings
        for warning in content.get("warnings", []):
            html += f'<div class="warning">{warning}</div>'

        # Tips
        for tip in content.get("tips", []):
            html += f'<div class="tip">{tip}</div>'

        return html

    def _render_country_content(self, content: dict[str, Any]) -> str:
        """Render country section content."""
        html = f"""
        <div class="content-item">
            <div class="content-label">Capital</div>
            <div class="content-value">{content.get("capital", "N/A")}</div>
        </div>
        <div class="content-item">
            <div class="content-label">Languages</div>
            <div class="content-value">{", ".join(content.get("official_languages", []))}</div>
        </div>
        <div class="content-item">
            <div class="content-label">Currency</div>
            <div class="content-value">{", ".join(content.get("currencies", []))}</div>
        </div>
        <div class="content-item">
            <div class="content-label">Time Zones</div>
            <div class="content-value">{", ".join(content.get("time_zones", []))}</div>
        </div>
        <div class="content-item">
            <div class="content-label">Safety Rating</div>
            <div class="content-value">{content.get("safety_rating", 0)}/5.0</div>
        </div>
        """
        return html

    def _render_weather_content(self, content: dict[str, Any]) -> str:
        """Render weather section content."""
        climate = content.get("climate_info", {})
        html = f"""
        <div class="content-item">
            <div class="content-label">Climate Type</div>
            <div class="content-value">{climate.get("climate_type", "N/A")}</div>
        </div>
        <div class="content-item">
            <div class="content-label">Best Time to Visit</div>
            <div class="content-value">{climate.get("best_months", "N/A")}</div>
        </div>
        """

        # Packing suggestions
        packing = content.get("packing_suggestions", [])
        if packing:
            items = "".join(f'<div class="list-item">{p.get("item", p) if isinstance(p, dict) else p}</div>' for p in packing[:5])
            html += f"""
            <div class="content-item">
                <div class="content-label">Packing Suggestions</div>
                <div class="content-value">{items}</div>
            </div>
            """

        return html

    def _render_itinerary_content(self, content: dict[str, Any]) -> str:
        """Render itinerary section content."""
        daily_plans = content.get("daily_plans", [])

        html = ""
        for i, day in enumerate(daily_plans[:7], 1):  # Show first 7 days
            date = day.get("date", f"Day {i}")
            activities = day.get("activities", [])

            activity_html = ""
            for act in activities[:4]:  # Show first 4 activities per day
                name = act.get("name", "Activity")
                time = act.get("time", "")
                activity_html += f'<div class="list-item">{time} - {name}</div>'

            html += f"""
            <div class="content-item">
                <div class="content-label">{date}</div>
                <div class="content-value">{activity_html}</div>
            </div>
            """

        if len(daily_plans) > 7:
            html += f'<div class="tip">+ {len(daily_plans) - 7} more days in full report</div>'

        return html

    def _render_flight_content(self, content: dict[str, Any]) -> str:
        """Render flight section content."""
        price_range = content.get("price_range", {})
        airport_info = content.get("airport_info", {})

        html = f"""
        <div class="content-item">
            <div class="content-label">Price Range</div>
            <div class="content-value">${price_range.get("min", 0):.0f} - ${price_range.get("max", 0):.0f} USD</div>
        </div>
        <div class="content-item">
            <div class="content-label">Average Price</div>
            <div class="content-value">${price_range.get("average", 0):.0f} USD</div>
        </div>
        """

        # Booking tips
        tips = content.get("booking_tips", [])
        if tips:
            for tip in tips[:3]:
                html += f'<div class="tip">{tip}</div>'

        return html

    def _render_generic_content(self, content: dict[str, Any]) -> str:
        """Render generic section content."""
        html = ""
        for key, value in content.items():
            if key in ["sources", "generated_at", "trip_id"]:
                continue

            if isinstance(value, list):
                if value and isinstance(value[0], str):
                    items = "".join(f'<div class="list-item">{v}</div>' for v in value[:5])
                    html += f"""
                    <div class="content-item">
                        <div class="content-label">{key.replace("_", " ").title()}</div>
                        <div class="content-value">{items}</div>
                    </div>
                    """
            elif isinstance(value, (str, int, float, bool)):
                html += f"""
                <div class="content-item">
                    <div class="content-label">{key.replace("_", " ").title()}</div>
                    <div class="content-value">{value}</div>
                </div>
                """

        return html if html else "<p>No content available</p>"

    async def generate_pdf(self, report: AggregatedReport) -> bytes:
        """
        Generate PDF from aggregated report.

        Args:
            report: Aggregated report data

        Returns:
            PDF content as bytes

        Raises:
            PDFGenerationError: If PDF generation fails
        """
        html = self._generate_html(report)

        if await self._check_playwright():
            return await self._generate_with_playwright(html)
        else:
            return await self._generate_fallback(html)

    async def _generate_with_playwright(self, html: str) -> bytes:
        """Generate PDF using Playwright."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Set content
                await page.set_content(html, wait_until="networkidle")

                # Generate PDF
                pdf_bytes = await page.pdf(
                    format="A4",
                    margin={
                        "top": "20mm",
                        "bottom": "20mm",
                        "left": "15mm",
                        "right": "15mm",
                    },
                    print_background=True,
                )

                await browser.close()
                return pdf_bytes

        except Exception as e:
            logger.error(f"Playwright PDF generation failed: {e}")
            raise PDFGenerationError(f"Failed to generate PDF: {e}")

    async def _generate_fallback(self, html: str) -> bytes:
        """
        Fallback PDF generation without Playwright.

        Uses simple HTML file that can be printed to PDF.
        """
        # For fallback, we return the HTML as bytes
        # The frontend can open this in a new window and use print-to-PDF
        logger.warning("Using fallback PDF generation (HTML only)")
        return html.encode("utf-8")

    async def save_pdf_to_storage(
        self, trip_id: str, pdf_bytes: bytes, user_id: str
    ) -> str | None:
        """
        Save PDF to Supabase Storage.

        Args:
            trip_id: Trip ID
            pdf_bytes: PDF content
            user_id: User ID for folder path

        Returns:
            Public URL to the PDF or None if failed
        """
        try:
            from app.core.supabase import supabase

            filename = f"{user_id}/{trip_id}/report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

            # Upload to storage
            response = supabase.storage.from_("trip-reports").upload(
                filename,
                pdf_bytes,
                {"content-type": "application/pdf"},
            )

            if response:
                # Get public URL
                public_url = supabase.storage.from_("trip-reports").get_public_url(filename)
                return public_url

            return None

        except Exception as e:
            logger.error(f"Failed to save PDF to storage: {e}")
            return None


# Singleton instance
pdf_generator = PDFGenerator()
