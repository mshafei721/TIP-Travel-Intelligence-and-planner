-- Migration: 007_performance_optimization.sql
-- Description: Add performance indexes and optimize query patterns
-- Priority: HIGH - Addresses critical performance bottlenecks

-- ============================================================================
-- PART 1: Critical Missing Indexes for High-Traffic Queries
-- ============================================================================

-- Index for agent_jobs: Used by generation status polling (every 3 seconds)
-- Query pattern: SELECT * FROM agent_jobs WHERE trip_id = ? AND status IN (...)
CREATE INDEX IF NOT EXISTS idx_agent_jobs_trip_status
    ON public.agent_jobs(trip_id, status);

-- Index for report_sections: Used when loading trip reports
-- Query pattern: SELECT * FROM report_sections WHERE trip_id = ? AND section_type = ?
CREATE INDEX IF NOT EXISTS idx_report_sections_trip_section
    ON public.report_sections(trip_id, section_type);

-- Index for agent_jobs by created_at for cleanup queries
CREATE INDEX IF NOT EXISTS idx_agent_jobs_created_at
    ON public.agent_jobs(created_at)
    WHERE status IN ('completed', 'failed');

-- ============================================================================
-- PART 2: Composite Indexes for Common Query Patterns
-- ============================================================================

-- Trips listing: ORDER BY created_at DESC with user_id filter
CREATE INDEX IF NOT EXISTS idx_trips_user_created
    ON public.trips(user_id, created_at DESC);

-- Trips by status: For filtering active/completed trips
CREATE INDEX IF NOT EXISTS idx_trips_user_status
    ON public.trips(user_id, status);

-- Report sections by type for faster section lookups
CREATE INDEX IF NOT EXISTS idx_report_sections_type
    ON public.report_sections(section_type);

-- ============================================================================
-- PART 3: Partial Indexes for Frequent Filters
-- ============================================================================

-- Active share links (frequently queried for validation)
CREATE INDEX IF NOT EXISTS idx_share_links_active
    ON public.share_links(trip_id, token)
    WHERE status = 'active';

-- Pending agent jobs (for status monitoring)
CREATE INDEX IF NOT EXISTS idx_agent_jobs_pending
    ON public.agent_jobs(trip_id, created_at)
    WHERE status = 'pending';

-- Running agent jobs (for active monitoring)
CREATE INDEX IF NOT EXISTS idx_agent_jobs_running
    ON public.agent_jobs(trip_id, started_at)
    WHERE status = 'running';

-- ============================================================================
-- PART 4: Optimized Aggregation Function for Agent Status
-- ============================================================================

-- Create a function to get aggregated agent job stats (avoids N+1 queries)
CREATE OR REPLACE FUNCTION get_agent_job_stats(p_trip_id UUID)
RETURNS TABLE (
    total_jobs INTEGER,
    completed_jobs INTEGER,
    failed_jobs INTEGER,
    pending_jobs INTEGER,
    running_jobs INTEGER,
    avg_duration_seconds NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INTEGER as total_jobs,
        COUNT(*) FILTER (WHERE status = 'completed')::INTEGER as completed_jobs,
        COUNT(*) FILTER (WHERE status = 'failed')::INTEGER as failed_jobs,
        COUNT(*) FILTER (WHERE status = 'pending')::INTEGER as pending_jobs,
        COUNT(*) FILTER (WHERE status = 'running')::INTEGER as running_jobs,
        AVG(
            EXTRACT(EPOCH FROM (completed_at - started_at))
        ) FILTER (WHERE status = 'completed' AND completed_at IS NOT NULL AND started_at IS NOT NULL)
        as avg_duration_seconds
    FROM public.agent_jobs
    WHERE trip_id = p_trip_id;
END;
$$ LANGUAGE plpgsql STABLE
SET search_path = '';

-- ============================================================================
-- PART 5: Materialized View for Analytics (Optional - for heavy analytics)
-- ============================================================================

-- Create materialized view for trip analytics (refresh periodically)
-- This avoids expensive aggregations on every analytics request
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_user_trip_stats AS
SELECT
    user_id,
    COUNT(*) as total_trips,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_trips,
    COUNT(*) FILTER (WHERE status = 'draft') as draft_trips,
    COUNT(DISTINCT (destinations->0->>'country')) as unique_countries,
    AVG(budget) as avg_budget,
    MAX(created_at) as last_trip_date
FROM public.trips
GROUP BY user_id;

-- Index on the materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_user_trip_stats_user
    ON mv_user_trip_stats(user_id);

-- Function to refresh the materialized view
CREATE OR REPLACE FUNCTION refresh_user_trip_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_trip_stats;
END;
$$ LANGUAGE plpgsql
SET search_path = '';

-- ============================================================================
-- PART 6: Query Optimization Hints
-- ============================================================================

-- Analyze tables to update statistics for query planner
ANALYZE public.trips;
ANALYZE public.agent_jobs;
ANALYZE public.report_sections;
ANALYZE public.share_links;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON INDEX idx_agent_jobs_trip_status IS 'Optimizes generation status polling queries (called every 3s during generation)';
COMMENT ON INDEX idx_report_sections_trip_section IS 'Optimizes report section lookups by trip and type';
COMMENT ON INDEX idx_trips_user_created IS 'Optimizes trip listing with user filter and date ordering';
COMMENT ON FUNCTION get_agent_job_stats IS 'Returns aggregated job statistics for a trip, avoiding N+1 queries';
COMMENT ON MATERIALIZED VIEW mv_user_trip_stats IS 'Pre-computed user trip statistics for analytics dashboard';
