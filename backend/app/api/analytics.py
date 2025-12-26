"""Analytics API endpoints for user usage and trip statistics"""

from datetime import datetime, timedelta
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import verify_jwt_token
from app.core.supabase import supabase
from app.models.analytics import (
    AgentUsageResponse,
    AgentUsageStats,
    BudgetRange,
    DateRange,
    DestinationCount,
    PurposeCount,
    SeasonalCount,
    TripAnalytics,
    TripAnalyticsResponse,
    UsageStats,
    UsageStatsResponse,
    UsageTrend,
    UsageTrendsResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_date_range_bounds(period: DateRange) -> tuple[datetime, datetime]:
    """Calculate start and end dates for a given period"""
    now = datetime.utcnow()
    end = now

    if period == DateRange.WEEK:
        start = now - timedelta(days=7)
    elif period == DateRange.MONTH:
        start = now - timedelta(days=30)
    elif period == DateRange.QUARTER:
        start = now - timedelta(days=90)
    elif period == DateRange.YEAR:
        start = now - timedelta(days=365)
    else:  # ALL_TIME
        start = datetime(2020, 1, 1)  # Project inception date

    return start, end


def get_season(month: int) -> str:
    """Get season name from month number"""
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"


def calculate_budget_ranges(budgets: list[float]) -> list[BudgetRange]:
    """Calculate budget distribution into ranges"""
    if not budgets:
        return []

    ranges = [
        ("$0-500", 0, 500),
        ("$500-1000", 500, 1000),
        ("$1000-2000", 1000, 2000),
        ("$2000-5000", 2000, 5000),
        ("$5000+", 5000, None),
    ]

    total = len(budgets)
    result = []

    for label, min_val, max_val in ranges:
        if max_val is not None:
            count = len([b for b in budgets if min_val <= b < max_val])
        else:
            count = len([b for b in budgets if b >= min_val])

        if count > 0:
            result.append(
                BudgetRange(
                    range_label=label,
                    min_value=min_val,
                    max_value=max_val,
                    count=count,
                    percentage=round((count / total) * 100, 1),
                )
            )

    return result


# =============================================================================
# Usage Analytics Endpoints
# =============================================================================


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    period: DateRange = Query(DateRange.MONTH, description="Time period for analytics"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get user usage statistics summary

    Returns aggregated usage metrics including:
    - Trip counts (total, created, completed, in progress)
    - Report generation counts
    - Agent invocation counts
    - Average generation time
    - Destinations and countries explored
    """
    user_id = token_payload["user_id"]
    start_date, end_date = get_date_range_bounds(period)

    try:
        # Fetch trips within date range
        trips_response = (
            supabase.table("trips")
            .select("id, status, destinations, budget, created_at, updated_at")
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .execute()
        )

        trips = trips_response.data if trips_response.data else []

        # Fetch agent jobs within date range
        agent_jobs_response = (
            supabase.table("agent_jobs")
            .select("id, agent_type, status, started_at, completed_at")
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .execute()
        )

        agent_jobs = agent_jobs_response.data if agent_jobs_response.data else []

        # Calculate trip stats
        total_trips = len(trips)
        trips_created = len([t for t in trips if t["status"] == "draft"])
        trips_completed = len([t for t in trips if t["status"] == "completed"])
        trips_in_progress = len(
            [t for t in trips if t["status"] in ["pending", "processing"]]
        )
        trips_draft = len([t for t in trips if t["status"] == "draft"])

        # Calculate unique destinations/countries
        countries = set()
        destinations = set()
        for trip in trips:
            if trip.get("destinations"):
                for dest in trip["destinations"]:
                    country = dest.get("country")
                    city = dest.get("city")
                    if country:
                        countries.add(country)
                    if city and country:
                        destinations.add(f"{city}, {country}")

        # Calculate agent invocations
        agents_invoked: dict[str, int] = {}
        for job in agent_jobs:
            agent_type = job.get("agent_type", "unknown")
            agents_invoked[agent_type] = agents_invoked.get(agent_type, 0) + 1

        # Calculate average generation time (from completed jobs)
        generation_times = []
        for job in agent_jobs:
            if job.get("status") == "completed" and job.get("started_at") and job.get("completed_at"):
                try:
                    start = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
                    end = datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00"))
                    duration = (end - start).total_seconds()
                    generation_times.append(duration)
                except (ValueError, TypeError):
                    pass

        avg_generation_time = (
            round(sum(generation_times) / len(generation_times), 2)
            if generation_times
            else None
        )

        # Count reports generated (completed agent jobs)
        reports_generated = len(
            [j for j in agent_jobs if j.get("status") == "completed"]
        )

        stats = UsageStats(
            period=period,
            period_start=start_date,
            period_end=end_date,
            total_trips=total_trips,
            trips_created=trips_created,
            trips_completed=trips_completed,
            trips_in_progress=trips_in_progress,
            trips_draft=trips_draft,
            reports_generated=reports_generated,
            agents_invoked=agents_invoked,
            avg_generation_time_seconds=avg_generation_time,
            destinations_explored=len(destinations),
            countries_planned=len(countries),
        )

        return UsageStatsResponse(success=True, data=stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch usage statistics: {str(e)}",
        )


@router.get("/usage/trends", response_model=UsageTrendsResponse)
async def get_usage_trends(
    period: DateRange = Query(DateRange.MONTH, description="Time period for trends"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get usage trends over time for charts

    Returns daily/weekly data points for:
    - Trips created
    - Reports generated
    - Countries visited
    """
    user_id = token_payload["user_id"]
    start_date, end_date = get_date_range_bounds(period)

    try:
        # Fetch trips within date range
        trips_response = (
            supabase.table("trips")
            .select("id, status, destinations, created_at")
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .order("created_at")
            .execute()
        )

        trips = trips_response.data if trips_response.data else []

        # Fetch agent jobs within date range
        agent_jobs_response = (
            supabase.table("agent_jobs")
            .select("id, status, created_at")
            .eq("user_id", user_id)
            .eq("status", "completed")
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .order("created_at")
            .execute()
        )

        agent_jobs = agent_jobs_response.data if agent_jobs_response.data else []

        # Group by date
        trends: dict[str, UsageTrend] = {}

        for trip in trips:
            date_str = trip["created_at"][:10]  # YYYY-MM-DD
            if date_str not in trends:
                trends[date_str] = UsageTrend(date=date_str)
            trends[date_str].trips_created += 1

            # Count countries
            if trip.get("destinations"):
                countries = set()
                for dest in trip["destinations"]:
                    if dest.get("country"):
                        countries.add(dest["country"])
                trends[date_str].countries_visited += len(countries)

        for job in agent_jobs:
            date_str = job["created_at"][:10]
            if date_str not in trends:
                trends[date_str] = UsageTrend(date=date_str)
            trends[date_str].reports_generated += 1

        # Sort by date and return
        sorted_trends = sorted(trends.values(), key=lambda x: x.date)

        return UsageTrendsResponse(
            success=True,
            period=period,
            data=sorted_trends,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch usage trends: {str(e)}",
        )


@router.get("/usage/agents", response_model=AgentUsageResponse)
async def get_agent_usage_stats(
    period: DateRange = Query(DateRange.MONTH, description="Time period for analytics"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get detailed agent usage statistics

    Returns per-agent metrics:
    - Total invocations
    - Average duration
    - Success rate
    """
    user_id = token_payload["user_id"]
    start_date, end_date = get_date_range_bounds(period)

    try:
        # Fetch agent jobs within date range
        agent_jobs_response = (
            supabase.table("agent_jobs")
            .select("id, agent_type, status, started_at, completed_at")
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .execute()
        )

        agent_jobs = agent_jobs_response.data if agent_jobs_response.data else []

        # Group by agent type
        agent_stats: dict[str, dict] = {}

        for job in agent_jobs:
            agent_type = job.get("agent_type", "unknown")
            if agent_type not in agent_stats:
                agent_stats[agent_type] = {
                    "total": 0,
                    "completed": 0,
                    "failed": 0,
                    "durations": [],
                }

            agent_stats[agent_type]["total"] += 1

            if job.get("status") == "completed":
                agent_stats[agent_type]["completed"] += 1
            elif job.get("status") == "failed":
                agent_stats[agent_type]["failed"] += 1

            # Calculate duration for completed jobs
            if (
                job.get("status") == "completed"
                and job.get("started_at")
                and job.get("completed_at")
            ):
                try:
                    start = datetime.fromisoformat(
                        job["started_at"].replace("Z", "+00:00")
                    )
                    end = datetime.fromisoformat(
                        job["completed_at"].replace("Z", "+00:00")
                    )
                    duration = (end - start).total_seconds()
                    agent_stats[agent_type]["durations"].append(duration)
                except (ValueError, TypeError):
                    pass

        # Build response
        stats_list = []
        total_invocations = 0

        for agent_type, stats in agent_stats.items():
            total = stats["total"]
            total_invocations += total
            completed = stats["completed"]
            durations = stats["durations"]

            avg_duration = (
                round(sum(durations) / len(durations), 2) if durations else None
            )
            success_rate = round((completed / total) * 100, 1) if total > 0 else 0.0

            stats_list.append(
                AgentUsageStats(
                    agent_type=agent_type,
                    invocations=total,
                    avg_duration_seconds=avg_duration,
                    success_rate=success_rate,
                )
            )

        # Sort by invocations (descending)
        stats_list.sort(key=lambda x: x.invocations, reverse=True)

        return AgentUsageResponse(
            success=True,
            period=period,
            data=stats_list,
            total_invocations=total_invocations,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch agent usage statistics: {str(e)}",
        )


# =============================================================================
# Trip Analytics Endpoints
# =============================================================================


@router.get("/trips", response_model=TripAnalyticsResponse)
async def get_trip_analytics(
    period: DateRange = Query(DateRange.YEAR, description="Time period for analytics"),
    limit_destinations: int = Query(10, ge=1, le=50, description="Max destinations to return"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get comprehensive trip analytics

    Returns:
    - Top destinations with counts
    - Budget distribution
    - Trip duration statistics
    - Seasonal preferences
    - Purpose distribution
    """
    user_id = token_payload["user_id"]
    start_date, end_date = get_date_range_bounds(period)

    try:
        # Fetch trips within date range
        trips_response = (
            supabase.table("trips")
            .select(
                "id, status, destinations, budget, start_date, end_date, "
                "purpose, created_at"
            )
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .execute()
        )

        trips = trips_response.data if trips_response.data else []

        # Calculate destination counts
        destination_counts: Counter = Counter()
        countries: set = set()
        cities: set = set()

        for trip in trips:
            if trip.get("destinations"):
                for dest in trip["destinations"]:
                    country = dest.get("country", "Unknown")
                    city = dest.get("city")
                    country_code = dest.get("country_code")

                    countries.add(country)
                    key = f"{city}|{country}|{country_code}" if city else f"|{country}|{country_code}"
                    destination_counts[key] += 1

                    if city:
                        cities.add(f"{city}, {country}")

        # Build top destinations
        total_dest_mentions = sum(destination_counts.values()) or 1
        top_destinations = []
        for dest_key, count in destination_counts.most_common(limit_destinations):
            parts = dest_key.split("|")
            city = parts[0] if parts[0] else None
            country = parts[1]
            country_code = parts[2] if len(parts) > 2 and parts[2] else None

            top_destinations.append(
                DestinationCount(
                    country=country,
                    country_code=country_code,
                    city=city,
                    count=count,
                    percentage=round((count / total_dest_mentions) * 100, 1),
                )
            )

        # Calculate budget statistics
        budgets = [
            float(trip["budget"])
            for trip in trips
            if trip.get("budget") is not None
        ]
        budget_ranges = calculate_budget_ranges(budgets)
        avg_budget = round(sum(budgets) / len(budgets), 2) if budgets else None
        total_planned_budget = sum(budgets)

        # Calculate duration statistics
        durations = []
        for trip in trips:
            if trip.get("start_date") and trip.get("end_date"):
                try:
                    start = datetime.fromisoformat(trip["start_date"])
                    end = datetime.fromisoformat(trip["end_date"])
                    duration = (end - start).days + 1
                    if duration > 0:
                        durations.append(duration)
                except (ValueError, TypeError):
                    pass

        avg_duration = round(sum(durations) / len(durations), 1) if durations else None
        shortest_trip = min(durations) if durations else None
        longest_trip = max(durations) if durations else None

        # Calculate seasonal distribution
        season_counts: Counter = Counter()
        for trip in trips:
            if trip.get("start_date"):
                try:
                    start = datetime.fromisoformat(trip["start_date"])
                    season = get_season(start.month)
                    season_counts[season] += 1
                except (ValueError, TypeError):
                    pass

        total_seasonal = sum(season_counts.values()) or 1
        seasonal_distribution = [
            SeasonalCount(
                season=season,
                count=count,
                percentage=round((count / total_seasonal) * 100, 1),
            )
            for season, count in season_counts.items()
        ]

        # Calculate purpose distribution
        purpose_counts: Counter = Counter()
        for trip in trips:
            purpose = trip.get("purpose", "leisure")
            purpose_counts[purpose] += 1

        total_purposes = sum(purpose_counts.values()) or 1
        purpose_distribution = [
            PurposeCount(
                purpose=purpose,
                count=count,
                percentage=round((count / total_purposes) * 100, 1),
            )
            for purpose, count in purpose_counts.items()
        ]

        analytics = TripAnalytics(
            period=period,
            period_start=start_date,
            period_end=end_date,
            top_destinations=top_destinations,
            unique_countries=len(countries),
            unique_cities=len(cities),
            budget_ranges=budget_ranges,
            avg_budget=avg_budget,
            total_planned_budget=total_planned_budget,
            avg_trip_duration_days=avg_duration,
            shortest_trip_days=shortest_trip,
            longest_trip_days=longest_trip,
            seasonal_distribution=seasonal_distribution,
            purpose_distribution=purpose_distribution,
        )

        return TripAnalyticsResponse(success=True, data=analytics)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trip analytics: {str(e)}",
        )


@router.get("/trips/destinations")
async def get_destination_analytics(
    period: DateRange = Query(DateRange.YEAR, description="Time period"),
    limit: int = Query(20, ge=1, le=100, description="Max destinations"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get detailed destination analytics

    Returns top destinations with:
    - Visit counts
    - Percentage of total trips
    - Country codes for map visualization
    """
    user_id = token_payload["user_id"]
    start_date, end_date = get_date_range_bounds(period)

    try:
        trips_response = (
            supabase.table("trips")
            .select("destinations")
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .execute()
        )

        trips = trips_response.data if trips_response.data else []

        destination_counts: Counter = Counter()

        for trip in trips:
            if trip.get("destinations"):
                for dest in trip["destinations"]:
                    country = dest.get("country", "Unknown")
                    city = dest.get("city")
                    country_code = dest.get("country_code")
                    key = f"{city or ''}|{country}|{country_code or ''}"
                    destination_counts[key] += 1

        total = sum(destination_counts.values()) or 1
        destinations = []

        for dest_key, count in destination_counts.most_common(limit):
            parts = dest_key.split("|")
            city = parts[0] if parts[0] else None
            country = parts[1]
            country_code = parts[2] if parts[2] else None

            destinations.append(
                DestinationCount(
                    country=country,
                    country_code=country_code,
                    city=city,
                    count=count,
                    percentage=round((count / total) * 100, 1),
                )
            )

        return {
            "success": True,
            "period": period,
            "data": [d.model_dump() for d in destinations],
            "total_destinations": len(destination_counts),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch destination analytics: {str(e)}",
        )


@router.get("/trips/budgets")
async def get_budget_analytics(
    period: DateRange = Query(DateRange.YEAR, description="Time period"),
    token_payload: dict = Depends(verify_jwt_token),
):
    """
    Get budget analytics

    Returns:
    - Budget distribution by ranges
    - Average budget
    - Total planned spending
    """
    user_id = token_payload["user_id"]
    start_date, end_date = get_date_range_bounds(period)

    try:
        trips_response = (
            supabase.table("trips")
            .select("budget, currency")
            .eq("user_id", user_id)
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .not_.is_("budget", "null")
            .execute()
        )

        trips = trips_response.data if trips_response.data else []

        budgets = [float(t["budget"]) for t in trips if t.get("budget")]
        budget_ranges = calculate_budget_ranges(budgets)

        avg_budget = round(sum(budgets) / len(budgets), 2) if budgets else None
        total_budget = sum(budgets)
        min_budget = min(budgets) if budgets else None
        max_budget = max(budgets) if budgets else None

        return {
            "success": True,
            "period": period,
            "data": {
                "budget_ranges": [br.model_dump() for br in budget_ranges],
                "average_budget": avg_budget,
                "total_planned_budget": total_budget,
                "min_budget": min_budget,
                "max_budget": max_budget,
                "trip_count": len(budgets),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch budget analytics: {str(e)}",
        )
