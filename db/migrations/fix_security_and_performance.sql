-- Migration: Fix Security and Performance Issues
-- Date: 2025-12-24
-- Description: Address all Supabase advisor warnings and errors

-- ============================================================================
-- PART 1: CRITICAL SECURITY - Enable RLS on public tables
-- ============================================================================

-- Enable RLS on tables that are missing it
ALTER TABLE public.traveler_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trip_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.source_references ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PART 2: RLS POLICIES - Add policies for all tables
-- ============================================================================

-- User Profiles Policies
CREATE POLICY "Users can view own profile"
  ON public.user_profiles
  FOR SELECT
  USING ((SELECT auth.uid()) = id);

CREATE POLICY "Users can update own profile"
  ON public.user_profiles
  FOR UPDATE
  USING ((SELECT auth.uid()) = id)
  WITH CHECK ((SELECT auth.uid()) = id);

CREATE POLICY "Users can insert own profile"
  ON public.user_profiles
  FOR INSERT
  WITH CHECK ((SELECT auth.uid()) = id);

-- Traveler Profiles Policies
CREATE POLICY "Users can view own traveler profile"
  ON public.traveler_profiles
  FOR SELECT
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can create own traveler profile"
  ON public.traveler_profiles
  FOR INSERT
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update own traveler profile"
  ON public.traveler_profiles
  FOR UPDATE
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete own traveler profile"
  ON public.traveler_profiles
  FOR DELETE
  USING ((SELECT auth.uid()) = user_id);

-- Trip Templates Policies
CREATE POLICY "Users can view own templates"
  ON public.trip_templates
  FOR SELECT
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can create own templates"
  ON public.trip_templates
  FOR INSERT
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update own templates"
  ON public.trip_templates
  FOR UPDATE
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete own templates"
  ON public.trip_templates
  FOR DELETE
  USING ((SELECT auth.uid()) = user_id);

-- Agent Jobs Policies (access via trip ownership)
CREATE POLICY "Users can view agent jobs for own trips"
  ON public.agent_jobs
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.trips
      WHERE trips.id = agent_jobs.trip_id
      AND trips.user_id = (SELECT auth.uid())
    )
  );

-- Report Sections Policies (access via trip ownership)
CREATE POLICY "Users can view report sections for own trips"
  ON public.report_sections
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.trips
      WHERE trips.id = report_sections.trip_id
      AND trips.user_id = (SELECT auth.uid())
    )
  );

-- Source References Policies (access via trip ownership)
CREATE POLICY "Users can view source references for own trips"
  ON public.source_references
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.trips
      WHERE trips.id = source_references.trip_id
      AND trips.user_id = (SELECT auth.uid())
    )
  );

-- Notifications Policies
CREATE POLICY "Users can view own notifications"
  ON public.notifications
  FOR SELECT
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update own notifications"
  ON public.notifications
  FOR UPDATE
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete own notifications"
  ON public.notifications
  FOR DELETE
  USING ((SELECT auth.uid()) = user_id);

-- Deletion Schedule Policies (access via trip ownership)
CREATE POLICY "Users can view deletion schedule for own trips"
  ON public.deletion_schedule
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.trips
      WHERE trips.id = deletion_schedule.trip_id
      AND trips.user_id = (SELECT auth.uid())
    )
  );

-- ============================================================================
-- PART 3: OPTIMIZE EXISTING RLS POLICIES
-- Fix auth function re-evaluation (wrap in SELECT for performance)
-- ============================================================================

-- Drop and recreate trips policies with optimized auth calls
DROP POLICY IF EXISTS "Users can view own trips" ON public.trips;
DROP POLICY IF EXISTS "Users can create own trips" ON public.trips;
DROP POLICY IF EXISTS "Users can update own trips" ON public.trips;
DROP POLICY IF EXISTS "Users can delete own trips" ON public.trips;

CREATE POLICY "Users can view own trips"
  ON public.trips
  FOR SELECT
  USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can create own trips"
  ON public.trips
  FOR INSERT
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can update own trips"
  ON public.trips
  FOR UPDATE
  USING ((SELECT auth.uid()) = user_id)
  WITH CHECK ((SELECT auth.uid()) = user_id);

CREATE POLICY "Users can delete own trips"
  ON public.trips
  FOR DELETE
  USING ((SELECT auth.uid()) = user_id);

-- ============================================================================
-- PART 4: SECURITY - Fix function search_path vulnerability
-- ============================================================================

-- Set immutable search_path on functions to prevent security issues
ALTER FUNCTION public.update_updated_at_column() SET search_path = '';
ALTER FUNCTION public.schedule_trip_deletion() SET search_path = '';
ALTER FUNCTION public.update_trip_status() SET search_path = '';

-- ============================================================================
-- PART 5: PERFORMANCE - Add missing indexes on foreign keys
-- ============================================================================

-- Index for notifications.trip_id foreign key
CREATE INDEX IF NOT EXISTS idx_notifications_trip_id
  ON public.notifications(trip_id)
  WHERE trip_id IS NOT NULL;

-- Index for notifications.user_id foreign key
CREATE INDEX IF NOT EXISTS idx_notifications_user_id
  ON public.notifications(user_id);

-- Index for source_references.trip_id foreign key
CREATE INDEX IF NOT EXISTS idx_source_references_trip_id
  ON public.source_references(trip_id);

-- Index for traveler_profiles.user_id foreign key
CREATE INDEX IF NOT EXISTS idx_traveler_profiles_user_id
  ON public.traveler_profiles(user_id);

-- Index for trip_templates.user_id foreign key
CREATE INDEX IF NOT EXISTS idx_trip_templates_user_id
  ON public.trip_templates(user_id);

-- ============================================================================
-- VERIFICATION QUERIES (Comment out - for manual testing)
-- ============================================================================

-- Verify RLS is enabled on all public tables:
-- SELECT schemaname, tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public'
-- ORDER BY tablename;

-- Verify policies exist:
-- SELECT schemaname, tablename, policyname
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;

-- Verify indexes:
-- SELECT schemaname, tablename, indexname
-- FROM pg_indexes
-- WHERE schemaname = 'public'
-- ORDER BY tablename, indexname;
