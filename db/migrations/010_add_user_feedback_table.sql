-- Migration: Add user_feedback table for bug reports and feature requests
-- Phase 5 Task 5.6: Feedback API + Storage

-- Create feedback type enum
DO $$ BEGIN
    CREATE TYPE feedback_type AS ENUM ('bug', 'feature');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create feedback status enum
DO $$ BEGIN
    CREATE TYPE feedback_status AS ENUM ('new', 'in_progress', 'resolved', 'closed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create user_feedback table
CREATE TABLE IF NOT EXISTS user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core fields
    type feedback_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status feedback_status NOT NULL DEFAULT 'new',

    -- Contact (optional)
    email VARCHAR(255),

    -- Context information
    route VARCHAR(500),
    app_release VARCHAR(50),
    browser VARCHAR(500),
    posthog_id VARCHAR(100),
    sentry_event_id VARCHAR(100),

    -- User association (optional - allows anonymous feedback)
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,

    -- IP for spam prevention
    ip_address INET,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,

    -- Admin notes (internal use)
    admin_notes TEXT
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_user_feedback_type ON user_feedback(type);
CREATE INDEX IF NOT EXISTS idx_user_feedback_status ON user_feedback(status);
CREATE INDEX IF NOT EXISTS idx_user_feedback_created_at ON user_feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_sentry_event ON user_feedback(sentry_event_id) WHERE sentry_event_id IS NOT NULL;

-- Enable RLS
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Allow anonymous users to create feedback (with rate limiting in API)
CREATE POLICY "Anyone can submit feedback" ON user_feedback
    FOR INSERT
    WITH CHECK (true);

-- Users can view their own feedback
CREATE POLICY "Users can view own feedback" ON user_feedback
    FOR SELECT
    USING (
        auth.uid() = user_id
        OR auth.uid() IN (
            SELECT id FROM auth.users WHERE raw_user_meta_data->>'role' = 'admin'
        )
    );

-- Only admins can update feedback
CREATE POLICY "Admins can update feedback" ON user_feedback
    FOR UPDATE
    USING (
        auth.uid() IN (
            SELECT id FROM auth.users WHERE raw_user_meta_data->>'role' = 'admin'
        )
    );

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_user_feedback_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
        NEW.resolved_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS user_feedback_updated_at ON user_feedback;
CREATE TRIGGER user_feedback_updated_at
    BEFORE UPDATE ON user_feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_user_feedback_updated_at();

-- Add comment for documentation
COMMENT ON TABLE user_feedback IS 'Stores user bug reports and feature requests (Phase 5 Task 5.6)';
COMMENT ON COLUMN user_feedback.posthog_id IS 'PostHog distinct_id for linking with analytics';
COMMENT ON COLUMN user_feedback.sentry_event_id IS 'Sentry event ID if feedback is related to an error';
