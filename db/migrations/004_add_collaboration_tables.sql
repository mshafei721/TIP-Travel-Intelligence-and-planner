-- TIP Collaboration Tables Migration
-- Adds share_links, trip_collaborators, and trip_comments tables
-- Migration: 004_add_collaboration_tables.sql

-- Enums for collaboration
CREATE TYPE public.collaborator_role AS ENUM ('viewer', 'editor', 'owner');
CREATE TYPE public.share_link_status AS ENUM ('active', 'revoked', 'expired');

-- Share Links table
-- Allows users to generate public share links for their trips
CREATE TABLE IF NOT EXISTS public.share_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,
  created_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  share_token VARCHAR(64) UNIQUE NOT NULL,
  status public.share_link_status NOT NULL DEFAULT 'active',
  is_public BOOLEAN NOT NULL DEFAULT false,
  allow_comments BOOLEAN NOT NULL DEFAULT true,
  allow_copy BOOLEAN NOT NULL DEFAULT false,
  expires_at TIMESTAMPTZ,
  view_count INTEGER NOT NULL DEFAULT 0,
  last_viewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trip Collaborators table
-- Manages invited collaborators with role-based permissions
CREATE TABLE IF NOT EXISTS public.trip_collaborators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  role public.collaborator_role NOT NULL DEFAULT 'viewer',
  invited_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  invitation_token VARCHAR(64) UNIQUE,
  accepted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Unique constraint: one invitation per email per trip
  CONSTRAINT unique_trip_collaborator UNIQUE (trip_id, email)
);

-- Trip Comments table
-- Allows collaborators and viewers to comment on trips
CREATE TABLE IF NOT EXISTS public.trip_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  parent_id UUID REFERENCES public.trip_comments(id) ON DELETE CASCADE,
  section_type public.report_section_type,
  content TEXT NOT NULL,
  is_edited BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_share_links_trip_id ON public.share_links(trip_id);
CREATE INDEX IF NOT EXISTS idx_share_links_token ON public.share_links(share_token);
CREATE INDEX IF NOT EXISTS idx_share_links_status ON public.share_links(status);

CREATE INDEX IF NOT EXISTS idx_trip_collaborators_trip_id ON public.trip_collaborators(trip_id);
CREATE INDEX IF NOT EXISTS idx_trip_collaborators_user_id ON public.trip_collaborators(user_id);
CREATE INDEX IF NOT EXISTS idx_trip_collaborators_email ON public.trip_collaborators(email);
CREATE INDEX IF NOT EXISTS idx_trip_collaborators_token ON public.trip_collaborators(invitation_token);

CREATE INDEX IF NOT EXISTS idx_trip_comments_trip_id ON public.trip_comments(trip_id);
CREATE INDEX IF NOT EXISTS idx_trip_comments_user_id ON public.trip_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_trip_comments_parent_id ON public.trip_comments(parent_id);

-- Updated_at triggers
CREATE TRIGGER update_share_links_updated_at
  BEFORE UPDATE ON public.share_links
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_trip_collaborators_updated_at
  BEFORE UPDATE ON public.trip_collaborators
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_trip_comments_updated_at
  BEFORE UPDATE ON public.trip_comments
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Enable RLS
ALTER TABLE public.share_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trip_collaborators ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trip_comments ENABLE ROW LEVEL SECURITY;

-- RLS Policies for share_links
-- Trip owner can manage share links
CREATE POLICY "Trip owners can manage share links"
  ON public.share_links FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.trips t
      WHERE t.id = share_links.trip_id
      AND t.user_id = auth.uid()
    )
  );

-- Anyone can read active public share links by token (for shared view)
CREATE POLICY "Anyone can view public share links"
  ON public.share_links FOR SELECT
  USING (
    is_public = true
    AND status = 'active'
    AND (expires_at IS NULL OR expires_at > now())
  );

-- RLS Policies for trip_collaborators
-- Trip owner can manage collaborators
CREATE POLICY "Trip owners can manage collaborators"
  ON public.trip_collaborators FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.trips t
      WHERE t.id = trip_collaborators.trip_id
      AND t.user_id = auth.uid()
    )
  );

-- Collaborators can view their own invitations
CREATE POLICY "Users can view their collaborations"
  ON public.trip_collaborators FOR SELECT
  USING (user_id = auth.uid() OR email = (SELECT email FROM auth.users WHERE id = auth.uid()));

-- RLS Policies for trip_comments
-- Trip owner can manage all comments
CREATE POLICY "Trip owners can manage comments"
  ON public.trip_comments FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.trips t
      WHERE t.id = trip_comments.trip_id
      AND t.user_id = auth.uid()
    )
  );

-- Collaborators with accepted invitation can read/create comments
CREATE POLICY "Collaborators can read comments"
  ON public.trip_comments FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.trip_collaborators tc
      WHERE tc.trip_id = trip_comments.trip_id
      AND tc.user_id = auth.uid()
      AND tc.accepted_at IS NOT NULL
    )
  );

CREATE POLICY "Collaborators can create comments"
  ON public.trip_comments FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.trip_collaborators tc
      WHERE tc.trip_id = trip_comments.trip_id
      AND tc.user_id = auth.uid()
      AND tc.accepted_at IS NOT NULL
    )
    OR
    EXISTS (
      SELECT 1 FROM public.trips t
      WHERE t.id = trip_comments.trip_id
      AND t.user_id = auth.uid()
    )
  );

-- Users can update/delete their own comments
CREATE POLICY "Users can update own comments"
  ON public.trip_comments FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "Users can delete own comments"
  ON public.trip_comments FOR DELETE
  USING (user_id = auth.uid());

-- Public share link viewers can read comments (if allow_comments is true)
CREATE POLICY "Public viewers can read comments"
  ON public.trip_comments FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.share_links sl
      WHERE sl.trip_id = trip_comments.trip_id
      AND sl.is_public = true
      AND sl.allow_comments = true
      AND sl.status = 'active'
      AND (sl.expires_at IS NULL OR sl.expires_at > now())
    )
  );
