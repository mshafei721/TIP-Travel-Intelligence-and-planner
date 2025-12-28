-- Migration: Add image support to trips table
-- Description: Adds cover_image_url column to trips table for trip cover images
-- Date: 2025-12-29

-- Add cover_image_url column to trips table
ALTER TABLE trips
ADD COLUMN IF NOT EXISTS cover_image_url TEXT;

-- Add index for faster queries when filtering by image presence
CREATE INDEX IF NOT EXISTS idx_trips_cover_image
ON trips (cover_image_url)
WHERE cover_image_url IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN trips.cover_image_url IS 'URL to the trip cover image stored in Supabase Storage';

-- Create storage bucket for trip images (if not exists)
-- Note: This needs to be run via Supabase dashboard or CLI as SQL doesn't support bucket creation
-- Bucket name: trip-images
-- Public: true (for serving images)

-- RLS policy for storage (to be added via Supabase dashboard):
-- Allow authenticated users to upload to trip-images bucket
-- Allow public read access to trip-images bucket
