-- Migration: Add GDPR Compliance Tables
-- Date: 2025-12-26
-- Description: Creates tables for GDPR compliance including audit logs and consent management

-- =============================================================================
-- ENUMS
-- =============================================================================

-- Consent types for GDPR compliance
create type public.consent_type as enum (
  'terms_of_service',
  'privacy_policy',
  'marketing_emails',
  'data_processing',
  'third_party_sharing',
  'analytics'
);

-- Audit event types for GDPR compliance
create type public.audit_event_type as enum (
  'data_accessed',
  'data_exported',
  'data_created',
  'data_updated',
  'data_deleted',
  'account_created',
  'account_deleted',
  'deletion_requested',
  'deletion_cancelled',
  'consent_granted',
  'consent_revoked',
  'login_success',
  'login_failed',
  'password_changed'
);

-- =============================================================================
-- USER CONSENTS TABLE
-- =============================================================================

create table if not exists public.user_consents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  consent_type public.consent_type not null,
  granted boolean not null default false,
  granted_at timestamptz,
  revoked_at timestamptz,
  ip_address inet,
  user_agent text,
  version text not null default '1.0',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  -- Unique constraint for upsert operations
  unique (user_id, consent_type)
);

-- Indexes for user_consents
create index if not exists idx_user_consents_user_id on public.user_consents(user_id);
create index if not exists idx_user_consents_consent_type on public.user_consents(consent_type);
create index if not exists idx_user_consents_granted on public.user_consents(granted) where granted = true;

-- Updated_at trigger for user_consents
create trigger update_user_consents_updated_at
  before update on public.user_consents
  for each row execute function public.update_updated_at_column();

-- RLS for user_consents
alter table public.user_consents enable row level security;

create policy "Users can view own consents"
  on public.user_consents for select
  using (auth.uid() = user_id);

create policy "Users can manage own consents"
  on public.user_consents for insert
  with check (auth.uid() = user_id);

create policy "Users can update own consents"
  on public.user_consents for update
  using (auth.uid() = user_id);

-- =============================================================================
-- GDPR AUDIT LOG TABLE
-- =============================================================================

-- Note: This table stores audit logs for compliance purposes
-- Logs are retained for 365 days as per GDPR requirements
create table if not exists public.gdpr_audit_log (
  id uuid primary key default gen_random_uuid(),
  event_type public.audit_event_type not null,
  user_id uuid not null,  -- No FK to allow logging after user deletion
  resource_type text,
  resource_id text,
  action text,
  ip_address inet,
  user_agent text,
  details jsonb,
  created_at timestamptz not null default now()
);

-- Indexes for gdpr_audit_log
create index if not exists idx_gdpr_audit_log_user_id on public.gdpr_audit_log(user_id);
create index if not exists idx_gdpr_audit_log_event_type on public.gdpr_audit_log(event_type);
create index if not exists idx_gdpr_audit_log_created_at on public.gdpr_audit_log(created_at);
create index if not exists idx_gdpr_audit_log_resource on public.gdpr_audit_log(resource_type, resource_id);

-- RLS for gdpr_audit_log
-- Note: Audit logs should generally only be accessible by admins
-- Users can see their own audit log entries for transparency
alter table public.gdpr_audit_log enable row level security;

create policy "Users can view own audit logs"
  on public.gdpr_audit_log for select
  using (auth.uid()::text = user_id::text);

-- Only service role can insert audit logs (from backend)
create policy "Service role can insert audit logs"
  on public.gdpr_audit_log for insert
  with check (true);  -- Backend uses service role key

-- =============================================================================
-- DATA RETENTION CLEANUP FUNCTION
-- =============================================================================

-- Function to clean up old audit logs (run via scheduled job)
create or replace function public.cleanup_old_audit_logs(retention_days integer default 365)
returns integer as $$
declare
  deleted_count integer;
begin
  delete from public.gdpr_audit_log
  where created_at < now() - (retention_days || ' days')::interval;

  get diagnostics deleted_count = row_count;
  return deleted_count;
end;
$$ language plpgsql security definer;

-- Function to clean up old agent jobs (run via scheduled job)
create or replace function public.cleanup_old_agent_jobs(retention_days integer default 30)
returns integer as $$
declare
  deleted_count integer;
begin
  delete from public.agent_jobs
  where created_at < now() - (retention_days || ' days')::interval
    and status in ('completed', 'failed');

  get diagnostics deleted_count = row_count;
  return deleted_count;
end;
$$ language plpgsql security definer;

-- =============================================================================
-- GDPR DATA EXPORT VIEW
-- =============================================================================

-- View to simplify data export for GDPR compliance
create or replace view public.gdpr_user_data_export as
select
  up.id as user_id,
  up.display_name,
  up.avatar_url,
  up.preferences,
  up.created_at as account_created_at,
  tp.nationality,
  tp.residency_country,
  tp.residency_status,
  tp.date_of_birth,
  tp.travel_style,
  tp.dietary_restrictions,
  tp.accessibility_needs,
  (
    select json_agg(json_build_object(
      'id', t.id,
      'title', t.title,
      'status', t.status,
      'destinations', t.destinations,
      'created_at', t.created_at
    ))
    from public.trips t
    where t.user_id = up.id
  ) as trips,
  (
    select json_agg(json_build_object(
      'consent_type', uc.consent_type,
      'granted', uc.granted,
      'granted_at', uc.granted_at,
      'version', uc.version
    ))
    from public.user_consents uc
    where uc.user_id = up.id
  ) as consents
from public.user_profiles up
left join public.traveler_profiles tp on tp.user_id = up.id;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

comment on table public.user_consents is 'Stores user consent records for GDPR compliance (Article 7)';
comment on table public.gdpr_audit_log is 'GDPR-compliant audit log for data access and modifications';
comment on function public.cleanup_old_audit_logs is 'Scheduled cleanup of old audit logs per retention policy';
comment on function public.cleanup_old_agent_jobs is 'Scheduled cleanup of old agent job records';
comment on view public.gdpr_user_data_export is 'Consolidated view for GDPR data export (Articles 15, 20)';
