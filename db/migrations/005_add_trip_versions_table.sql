-- Migration: 005_add_trip_versions_table.sql
-- Description: Add trip version history table and version column to trips
-- Purpose: Enable trip updates with version history and selective recalculation

-- ============================================================================
-- ADD VERSION COLUMN TO TRIPS TABLE
-- ============================================================================

-- Add version column to trips table if it doesn't exist
ALTER TABLE trips ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

-- Add index for version queries
CREATE INDEX IF NOT EXISTS idx_trips_version ON trips(version);


-- ============================================================================
-- TRIP VERSIONS TABLE
-- ============================================================================

-- Create trip_versions table to store version history
CREATE TABLE IF NOT EXISTS trip_versions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    trip_data JSONB NOT NULL,
    change_summary TEXT,
    fields_changed TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Ensure unique version number per trip
    UNIQUE(trip_id, version_number)
);

-- Add indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_trip_versions_trip_id ON trip_versions(trip_id);
CREATE INDEX IF NOT EXISTS idx_trip_versions_version_number ON trip_versions(version_number);
CREATE INDEX IF NOT EXISTS idx_trip_versions_created_at ON trip_versions(created_at);

-- Add comment
COMMENT ON TABLE trip_versions IS 'Stores version history for trips to enable rollback and comparison';
COMMENT ON COLUMN trip_versions.trip_data IS 'JSONB snapshot of trip data at this version';
COMMENT ON COLUMN trip_versions.change_summary IS 'Human-readable description of changes in this version';
COMMENT ON COLUMN trip_versions.fields_changed IS 'Array of field names that changed from previous version';


-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

-- Enable RLS on trip_versions
ALTER TABLE trip_versions ENABLE ROW LEVEL SECURITY;

-- Users can view their own trip versions
CREATE POLICY "Users can view own trip versions" ON trip_versions
    FOR SELECT
    USING (
        trip_id IN (
            SELECT id FROM trips WHERE user_id = auth.uid()
        )
    );

-- Users can insert versions for their own trips
CREATE POLICY "Users can create trip versions" ON trip_versions
    FOR INSERT
    WITH CHECK (
        trip_id IN (
            SELECT id FROM trips WHERE user_id = auth.uid()
        )
    );

-- Users can delete versions for their own trips
CREATE POLICY "Users can delete own trip versions" ON trip_versions
    FOR DELETE
    USING (
        trip_id IN (
            SELECT id FROM trips WHERE user_id = auth.uid()
        )
    );


-- ============================================================================
-- RECALCULATION JOBS TABLE
-- ============================================================================

-- Create table to track recalculation jobs
CREATE TABLE IF NOT EXISTS recalculation_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    celery_task_id TEXT NOT NULL,
    agents_to_recalculate TEXT[] NOT NULL,
    status TEXT DEFAULT 'queued' CHECK (status IN ('queued', 'in_progress', 'completed', 'failed')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_recalc_jobs_trip_id ON recalculation_jobs(trip_id);
CREATE INDEX IF NOT EXISTS idx_recalc_jobs_status ON recalculation_jobs(status);
CREATE INDEX IF NOT EXISTS idx_recalc_jobs_celery_task_id ON recalculation_jobs(celery_task_id);

-- Add comment
COMMENT ON TABLE recalculation_jobs IS 'Tracks selective recalculation jobs for trips';

-- Enable RLS
ALTER TABLE recalculation_jobs ENABLE ROW LEVEL SECURITY;

-- Users can view their own recalculation jobs
CREATE POLICY "Users can view own recalculation jobs" ON recalculation_jobs
    FOR SELECT
    USING (
        trip_id IN (
            SELECT id FROM trips WHERE user_id = auth.uid()
        )
    );

-- Users can create recalculation jobs for their own trips
CREATE POLICY "Users can create recalculation jobs" ON recalculation_jobs
    FOR INSERT
    WITH CHECK (
        trip_id IN (
            SELECT id FROM trips WHERE user_id = auth.uid()
        )
    );

-- Users can update their own recalculation jobs
CREATE POLICY "Users can update own recalculation jobs" ON recalculation_jobs
    FOR UPDATE
    USING (
        trip_id IN (
            SELECT id FROM trips WHERE user_id = auth.uid()
        )
    );


-- ============================================================================
-- TRIGGER FOR UPDATED_AT
-- ============================================================================

-- Create trigger function if not exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger for recalculation_jobs
DROP TRIGGER IF EXISTS update_recalculation_jobs_updated_at ON recalculation_jobs;
CREATE TRIGGER update_recalculation_jobs_updated_at
    BEFORE UPDATE ON recalculation_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- SERVICE ROLE POLICIES (for backend access)
-- ============================================================================

-- Allow service role full access to trip_versions
CREATE POLICY "Service role can manage trip versions" ON trip_versions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Allow service role full access to recalculation_jobs
CREATE POLICY "Service role can manage recalculation jobs" ON recalculation_jobs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);


-- ============================================================================
-- CLEANUP FUNCTION
-- ============================================================================

-- Function to clean up old versions (keep last N versions per trip)
CREATE OR REPLACE FUNCTION cleanup_old_trip_versions(max_versions INTEGER DEFAULT 10)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH old_versions AS (
        SELECT id
        FROM trip_versions tv
        WHERE tv.version_number < (
            SELECT version_number
            FROM trip_versions tv2
            WHERE tv2.trip_id = tv.trip_id
            ORDER BY version_number DESC
            OFFSET max_versions
            LIMIT 1
        )
    )
    DELETE FROM trip_versions WHERE id IN (SELECT id FROM old_versions);

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION cleanup_old_trip_versions IS 'Removes old versions keeping only the last N versions per trip';
