-- Migration: 006_fix_advisor_warnings.sql
-- Description: Fix security and performance warnings from Supabase advisor
-- Fixes: function_search_path_mutable, auth_rls_initplan, unindexed_foreign_keys, multiple_permissive_policies

-- ============================================================================
-- FIX 1: Function Search Path Mutable (SECURITY)
-- ============================================================================

-- Fix cleanup_old_audit_logs - set immutable search_path
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(retention_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.gdpr_audit_log
    WHERE created_at < NOW() - INTERVAL '1 day' * retention_days;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = '';

-- Fix cleanup_old_agent_jobs - set immutable search_path
CREATE OR REPLACE FUNCTION cleanup_old_agent_jobs(retention_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.agent_jobs
    WHERE status IN ('completed', 'failed')
    AND created_at < NOW() - INTERVAL '1 day' * retention_days;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = '';

-- Fix cleanup_old_trip_versions - set immutable search_path
CREATE OR REPLACE FUNCTION cleanup_old_trip_versions(max_versions INTEGER DEFAULT 10)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH old_versions AS (
        SELECT id
        FROM public.trip_versions tv
        WHERE tv.version_number < (
            SELECT version_number
            FROM public.trip_versions tv2
            WHERE tv2.trip_id = tv.trip_id
            ORDER BY version_number DESC
            OFFSET max_versions
            LIMIT 1
        )
    )
    DELETE FROM public.trip_versions WHERE id IN (SELECT id FROM old_versions);

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = '';


-- ============================================================================
-- FIX 2: Unindexed Foreign Keys (PERFORMANCE)
-- ============================================================================

-- Add index for share_links.created_by foreign key
CREATE INDEX IF NOT EXISTS idx_share_links_created_by ON public.share_links(created_by);

-- Add index for trip_collaborators.invited_by foreign key
CREATE INDEX IF NOT EXISTS idx_trip_collaborators_invited_by ON public.trip_collaborators(invited_by);


-- ============================================================================
-- FIX 3: Multiple Permissive Policies - traveler_profiles (PERFORMANCE)
-- Remove duplicate INSERT policies
-- ============================================================================

-- Drop duplicate policies on traveler_profiles (keep only one INSERT policy)
DROP POLICY IF EXISTS "Users can create own traveler profile" ON public.traveler_profiles;
-- "Users can insert own traveler profile" will remain


-- ============================================================================
-- FIX 4: Multiple Permissive Policies - trip_templates (PERFORMANCE)
-- Remove duplicate policies from original migration
-- ============================================================================

-- Drop duplicate policies on trip_templates (keep the "manage" policy which covers all)
DROP POLICY IF EXISTS "Users can create own templates" ON public.trip_templates;
DROP POLICY IF EXISTS "Users can update own templates" ON public.trip_templates;
DROP POLICY IF EXISTS "Users can delete own templates" ON public.trip_templates;
DROP POLICY IF EXISTS "Users can view own templates" ON public.trip_templates;
-- "Users can manage own templates" covers INSERT, UPDATE, DELETE for owners
-- "Users can view public templates" remains for SELECT of public templates


-- ============================================================================
-- FIX 5: Auth RLS Initplan - Optimize auth.uid() calls (PERFORMANCE)
-- Wrap auth.uid() in (select auth.uid()) for better performance
-- ============================================================================

-- Fix user_profiles policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING ((select auth.uid()) = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING ((select auth.uid()) = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;
CREATE POLICY "Users can insert own profile" ON public.user_profiles
    FOR INSERT WITH CHECK ((select auth.uid()) = id);

DROP POLICY IF EXISTS "Users can delete own profile" ON public.user_profiles;
CREATE POLICY "Users can delete own profile" ON public.user_profiles
    FOR DELETE USING ((select auth.uid()) = id);

-- Fix traveler_profiles policies
DROP POLICY IF EXISTS "Users can view own traveler profile" ON public.traveler_profiles;
CREATE POLICY "Users can view own traveler profile" ON public.traveler_profiles
    FOR SELECT USING ((select auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own traveler profile" ON public.traveler_profiles;
CREATE POLICY "Users can update own traveler profile" ON public.traveler_profiles
    FOR UPDATE USING ((select auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can insert own traveler profile" ON public.traveler_profiles;
CREATE POLICY "Users can insert own traveler profile" ON public.traveler_profiles
    FOR INSERT WITH CHECK ((select auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can delete own traveler profile" ON public.traveler_profiles;
CREATE POLICY "Users can delete own traveler profile" ON public.traveler_profiles
    FOR DELETE USING ((select auth.uid()) = user_id);

-- Fix user_consents policies
DROP POLICY IF EXISTS "Users can view own consents" ON public.user_consents;
CREATE POLICY "Users can view own consents" ON public.user_consents
    FOR SELECT USING ((select auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can manage own consents" ON public.user_consents;
CREATE POLICY "Users can manage own consents" ON public.user_consents
    FOR INSERT WITH CHECK ((select auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can update own consents" ON public.user_consents;
CREATE POLICY "Users can update own consents" ON public.user_consents
    FOR UPDATE USING ((select auth.uid()) = user_id);

-- Fix gdpr_audit_log policies
DROP POLICY IF EXISTS "Users can view own audit logs" ON public.gdpr_audit_log;
CREATE POLICY "Users can view own audit logs" ON public.gdpr_audit_log
    FOR SELECT USING ((select auth.uid()) = user_id);

-- Fix trip_templates policies
DROP POLICY IF EXISTS "Users can view public templates" ON public.trip_templates;
CREATE POLICY "Users can view public templates" ON public.trip_templates
    FOR SELECT USING (is_public = true OR (select auth.uid()) = user_id);

DROP POLICY IF EXISTS "Users can manage own templates" ON public.trip_templates;
CREATE POLICY "Users can manage own templates" ON public.trip_templates
    FOR ALL USING ((select auth.uid()) = user_id);

-- Fix share_links policies
DROP POLICY IF EXISTS "Trip owners can manage share links" ON public.share_links;
CREATE POLICY "Trip owners can manage share links" ON public.share_links
    FOR ALL USING (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );

-- Fix trip_collaborators policies
DROP POLICY IF EXISTS "Trip owners can manage collaborators" ON public.trip_collaborators;
CREATE POLICY "Trip owners can manage collaborators" ON public.trip_collaborators
    FOR ALL USING (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );

DROP POLICY IF EXISTS "Users can view their collaborations" ON public.trip_collaborators;
CREATE POLICY "Users can view their collaborations" ON public.trip_collaborators
    FOR SELECT USING (
        user_id = (select auth.uid()) OR email = (select auth.email())
    );

-- Fix trip_comments policies
DROP POLICY IF EXISTS "Trip owners can manage comments" ON public.trip_comments;
CREATE POLICY "Trip owners can manage comments" ON public.trip_comments
    FOR ALL USING (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );

DROP POLICY IF EXISTS "Collaborators can read comments" ON public.trip_comments;
CREATE POLICY "Collaborators can read comments" ON public.trip_comments
    FOR SELECT USING (
        trip_id IN (
            SELECT trip_id FROM public.trip_collaborators
            WHERE user_id = (select auth.uid()) OR email = (select auth.email())
        )
    );

DROP POLICY IF EXISTS "Collaborators can create comments" ON public.trip_comments;
CREATE POLICY "Collaborators can create comments" ON public.trip_comments
    FOR INSERT WITH CHECK (
        user_id = (select auth.uid()) AND
        trip_id IN (
            SELECT trip_id FROM public.trip_collaborators
            WHERE (user_id = (select auth.uid()) OR email = (select auth.email()))
            AND role IN ('editor', 'viewer')
        )
    );

DROP POLICY IF EXISTS "Users can update own comments" ON public.trip_comments;
CREATE POLICY "Users can update own comments" ON public.trip_comments
    FOR UPDATE USING (user_id = (select auth.uid()));

DROP POLICY IF EXISTS "Users can delete own comments" ON public.trip_comments;
CREATE POLICY "Users can delete own comments" ON public.trip_comments
    FOR DELETE USING (user_id = (select auth.uid()));

-- Fix trip_versions policies
DROP POLICY IF EXISTS "Users can view own trip versions" ON public.trip_versions;
CREATE POLICY "Users can view own trip versions" ON public.trip_versions
    FOR SELECT USING (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );

DROP POLICY IF EXISTS "Users can create trip versions" ON public.trip_versions;
CREATE POLICY "Users can create trip versions" ON public.trip_versions
    FOR INSERT WITH CHECK (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );

DROP POLICY IF EXISTS "Users can delete own trip versions" ON public.trip_versions;
CREATE POLICY "Users can delete own trip versions" ON public.trip_versions
    FOR DELETE USING (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );

-- Fix recalculation_jobs policies
DROP POLICY IF EXISTS "Users can view own recalculation jobs" ON public.recalculation_jobs;
CREATE POLICY "Users can view own recalculation jobs" ON public.recalculation_jobs
    FOR SELECT USING (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );

DROP POLICY IF EXISTS "Users can create recalculation jobs" ON public.recalculation_jobs;
CREATE POLICY "Users can create recalculation jobs" ON public.recalculation_jobs
    FOR INSERT WITH CHECK (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );

DROP POLICY IF EXISTS "Users can update own recalculation jobs" ON public.recalculation_jobs;
CREATE POLICY "Users can update own recalculation jobs" ON public.recalculation_jobs
    FOR UPDATE USING (
        trip_id IN (SELECT id FROM public.trips WHERE user_id = (select auth.uid()))
    );


-- ============================================================================
-- FIX 6: Consolidate Multiple Permissive Policies (PERFORMANCE)
-- Combine overlapping policies into single efficient policies
-- ============================================================================

-- share_links: Combine "Anyone can view public share links" into the owner policy
DROP POLICY IF EXISTS "Anyone can view public share links" ON public.share_links;
-- The "Trip owners can manage share links" policy now covers owner access
-- Create separate policy for public share link viewing
CREATE POLICY "Public share links are viewable" ON public.share_links
    FOR SELECT USING (status = 'active' AND is_public = true);

-- trip_comments: Remove overlapping SELECT policies, consolidate
DROP POLICY IF EXISTS "Public viewers can read comments" ON public.trip_comments;
-- Create optimized policy for public comment viewing
CREATE POLICY "Public viewers can read comments" ON public.trip_comments
    FOR SELECT USING (
        trip_id IN (
            SELECT trip_id FROM public.share_links
            WHERE status = 'active' AND is_public = true AND allow_comments = true
        )
    );


-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON FUNCTION cleanup_old_audit_logs IS 'Removes audit logs older than retention_days (default 90). Fixed search_path for security.';
COMMENT ON FUNCTION cleanup_old_agent_jobs IS 'Removes completed/failed agent jobs older than retention_days (default 30). Fixed search_path for security.';
COMMENT ON FUNCTION cleanup_old_trip_versions IS 'Removes old versions keeping only the last N versions per trip. Fixed search_path for security.';
