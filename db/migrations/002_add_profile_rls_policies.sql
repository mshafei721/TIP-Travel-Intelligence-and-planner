-- Migration: Add RLS policies for user_profiles and traveler_profiles
-- Created: 2025-12-25
-- Purpose: Secure user and traveler profile tables with Row-Level Security

-- ============================================
-- USER_PROFILES RLS POLICIES
-- ============================================

-- Enable RLS (already enabled, but keeping for safety)
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile"
  ON public.user_profiles
  FOR SELECT
  USING (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON public.user_profiles
  FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Policy: Users can insert their own profile (for signup)
CREATE POLICY "Users can insert own profile"
  ON public.user_profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Policy: Users can delete their own profile
CREATE POLICY "Users can delete own profile"
  ON public.user_profiles
  FOR DELETE
  USING (auth.uid() = id);


-- ============================================
-- TRAVELER_PROFILES RLS POLICIES
-- ============================================

-- Enable RLS
ALTER TABLE public.traveler_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own traveler profile
CREATE POLICY "Users can view own traveler profile"
  ON public.traveler_profiles
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Users can update their own traveler profile
CREATE POLICY "Users can update own traveler profile"
  ON public.traveler_profiles
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can insert their own traveler profile
CREATE POLICY "Users can insert own traveler profile"
  ON public.traveler_profiles
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own traveler profile
CREATE POLICY "Users can delete own traveler profile"
  ON public.traveler_profiles
  FOR DELETE
  USING (auth.uid() = user_id);


-- ============================================
-- UPDATED_AT TRIGGERS (if not already added)
-- ============================================

-- Add updated_at trigger for user_profiles
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Add updated_at trigger for traveler_profiles
DROP TRIGGER IF EXISTS update_traveler_profiles_updated_at ON public.traveler_profiles;
CREATE TRIGGER update_traveler_profiles_updated_at
  BEFORE UPDATE ON public.traveler_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();
