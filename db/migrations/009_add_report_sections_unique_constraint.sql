-- Migration: Add unique constraint on report_sections for upsert support
-- This allows incremental saving of report sections during generation
-- Date: 2025-12-29

-- First, remove any duplicates (keep the most recent one)
DELETE FROM public.report_sections a
USING public.report_sections b
WHERE a.trip_id = b.trip_id
  AND a.section_type = b.section_type
  AND a.generated_at < b.generated_at;

-- Add unique constraint on (trip_id, section_type)
-- This enables ON CONFLICT upsert behavior
ALTER TABLE public.report_sections
ADD CONSTRAINT report_sections_trip_section_unique
UNIQUE (trip_id, section_type);

-- Note: The existing index idx_report_sections_trip_section will be replaced by this constraint's implicit index
