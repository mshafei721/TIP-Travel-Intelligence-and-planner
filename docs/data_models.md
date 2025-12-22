# Data Models & Database Schema

## Overview
This document defines the Postgres database schema for TIP using Supabase.

---

## Schema Diagram

```
┌─────────────┐
│    Users    │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────┴──────────────────┐
│        Trips            │
└──┬────────────┬─────────┘
   │ 1       1  │
   │            │
   │ N       N  │
┌──┴──────┐  ┌─┴────────────────┐
│AgentJobs│  │ ReportSections    │
└─────────┘  └──┬───────────────┘
                │ 1
                │
                │ N
           ┌────┴──────────────┐
           │ SourceReferences  │
           └───────────────────┘
```

---

## Table Definitions

### 1. Users (managed by Supabase Auth)

```sql
-- Users table is managed by Supabase Auth
-- auth.users contains: id, email, created_at, etc.

-- We can extend with a public.user_profiles table if needed:
CREATE TABLE public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT,
  avatar_url TEXT,
  preferences JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
  ON public.user_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON public.user_profiles FOR UPDATE
  USING (auth.uid() = id);
```

### 2. Trips

```sql
CREATE TABLE public.trips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Destination
  destination_country TEXT NOT NULL,
  cities JSONB NOT NULL, -- Array of city names: ["Paris", "Lyon"]

  -- Dates
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  CHECK (end_date >= start_date),

  -- Budget
  budget_amount NUMERIC(10, 2) NOT NULL,
  budget_currency TEXT NOT NULL DEFAULT 'USD',
  CHECK (budget_amount > 0),

  -- Traveler Info
  nationality TEXT NOT NULL,
  residence_country TEXT NOT NULL,
  residence_status TEXT, -- e.g., "citizen", "permanent resident", "temporary visa"
  traveler_count INTEGER NOT NULL DEFAULT 1,
  traveler_ages JSONB, -- Array of objects: [{"age": 30, "type": "adult"}, {"age": 8, "type": "child"}]

  -- Preferences (optional)
  preferences JSONB DEFAULT '{}'::jsonb, -- {"travel_style": "relaxed", "pace": "moderate", "food": "adventurous"}

  -- Status
  status TEXT NOT NULL DEFAULT 'pending',
  CHECK (status IN ('pending', 'processing', 'completed', 'failed')),

  -- Data Lifecycle
  auto_delete_at TIMESTAMP WITH TIME ZONE,
  deleted_at TIMESTAMP WITH TIME ZONE,

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_trips_user_id ON public.trips(user_id);
CREATE INDEX idx_trips_status ON public.trips(status);
CREATE INDEX idx_trips_auto_delete_at ON public.trips(auto_delete_at) WHERE deleted_at IS NULL;

-- RLS Policies
ALTER TABLE public.trips ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own trips"
  ON public.trips FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own trips"
  ON public.trips FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own trips"
  ON public.trips FOR DELETE
  USING (auth.uid() = user_id);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_trips_updated_at BEFORE UPDATE ON public.trips
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3. AgentJobs

```sql
CREATE TABLE public.agent_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,

  -- Agent Info
  agent_type TEXT NOT NULL,
  CHECK (agent_type IN (
    'orchestrator', 'visa', 'country', 'weather', 'currency',
    'culture', 'food', 'attractions', 'itinerary', 'flight'
  )),

  -- Execution Status
  status TEXT NOT NULL DEFAULT 'queued',
  CHECK (status IN ('queued', 'running', 'completed', 'failed', 'retrying')),

  -- Timing
  started_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  duration_seconds NUMERIC(10, 2),

  -- Error Handling
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,

  -- Results
  result_data JSONB, -- Agent-specific output data
  confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_agent_jobs_trip_id ON public.agent_jobs(trip_id);
CREATE INDEX idx_agent_jobs_status ON public.agent_jobs(status);
CREATE INDEX idx_agent_jobs_agent_type ON public.agent_jobs(agent_type);

-- RLS Policies
ALTER TABLE public.agent_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own agent jobs"
  ON public.agent_jobs FOR SELECT
  USING (auth.uid() = (SELECT user_id FROM public.trips WHERE id = trip_id));

-- Trigger for updated_at
CREATE TRIGGER update_agent_jobs_updated_at BEFORE UPDATE ON public.agent_jobs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 4. ReportSections

```sql
CREATE TABLE public.report_sections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,

  -- Section Info
  section_type TEXT NOT NULL,
  CHECK (section_type IN (
    'visa', 'country', 'weather', 'currency', 'culture',
    'food', 'attractions', 'itinerary', 'flight', 'summary'
  )),

  -- Content
  content JSONB NOT NULL, -- Section-specific structured data
  sources JSONB DEFAULT '[]'::jsonb, -- Array of source URLs
  confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),

  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_report_sections_trip_id ON public.report_sections(trip_id);
CREATE INDEX idx_report_sections_section_type ON public.report_sections(section_type);
CREATE UNIQUE INDEX idx_report_sections_trip_section ON public.report_sections(trip_id, section_type);

-- RLS Policies
ALTER TABLE public.report_sections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own report sections"
  ON public.report_sections FOR SELECT
  USING (auth.uid() = (SELECT user_id FROM public.trips WHERE id = trip_id));

-- Trigger for updated_at
CREATE TRIGGER update_report_sections_updated_at BEFORE UPDATE ON public.report_sections
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5. SourceReferences

```sql
CREATE TABLE public.source_references (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,

  -- Source Info
  url TEXT NOT NULL,
  source_type TEXT NOT NULL,
  CHECK (source_type IN ('official', 'api', 'scraped', 'government', 'third_party')),

  -- Metadata
  title TEXT,
  accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  reliability_score INTEGER CHECK (reliability_score >= 0 AND reliability_score <= 100),

  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_source_references_trip_id ON public.source_references(trip_id);
CREATE INDEX idx_source_references_source_type ON public.source_references(source_type);

-- RLS Policies
ALTER TABLE public.source_references ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own source references"
  ON public.source_references FOR SELECT
  USING (auth.uid() = (SELECT user_id FROM public.trips WHERE id = trip_id));
```

### 6. DeletionSchedule

```sql
CREATE TABLE public.deletion_schedule (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trip_id UUID NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,

  -- Schedule
  scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
  executed_at TIMESTAMP WITH TIME ZONE,

  -- Status
  status TEXT NOT NULL DEFAULT 'pending',
  CHECK (status IN ('pending', 'executing', 'completed', 'failed')),

  -- Metadata
  deletion_reason TEXT DEFAULT 'auto_expiry',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_deletion_schedule_scheduled_at ON public.deletion_schedule(scheduled_at) WHERE status = 'pending';
CREATE INDEX idx_deletion_schedule_trip_id ON public.deletion_schedule(trip_id);

-- RLS Policies
ALTER TABLE public.deletion_schedule ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own deletion schedules"
  ON public.deletion_schedule FOR SELECT
  USING (auth.uid() = (SELECT user_id FROM public.trips WHERE id = trip_id));
```

---

## JSONB Field Schemas

### trips.cities
```json
["Paris", "Lyon", "Nice"]
```

### trips.traveler_ages
```json
[
  {"age": 30, "type": "adult"},
  {"age": 8, "type": "child"},
  {"age": 5, "type": "child"}
]
```

### trips.preferences
```json
{
  "travel_style": "relaxed",
  "pace": "moderate",
  "food": "adventurous"
}
```

### agent_jobs.result_data (example for Visa Agent)
```json
{
  "visa_required": true,
  "visa_type": "eVisa",
  "allowed_stay": "90 days",
  "processing_time": "3-5 business days",
  "cost_usd": 50,
  "application_url": "https://evisa.gov.example",
  "requirements": ["Valid passport", "Proof of accommodation", "Return ticket"],
  "warnings": ["Passport must be valid for 6 months beyond travel dates"]
}
```

### report_sections.content (example for Weather Section)
```json
{
  "forecast": [
    {"date": "2025-06-01", "high": 25, "low": 15, "condition": "Sunny", "rain_chance": 10},
    {"date": "2025-06-02", "high": 24, "low": 14, "condition": "Partly Cloudy", "rain_chance": 20}
  ],
  "historical_average": {"high": 23, "low": 13},
  "warnings": ["UV index high - sunscreen recommended"],
  "best_activities": ["Outdoor sightseeing", "Beach visits"]
}
```

### report_sections.sources
```json
[
  {"url": "https://embassy.gov.example/visa", "type": "official", "accessed": "2025-12-22T10:00:00Z"},
  {"url": "https://api.weather.com/forecast", "type": "api", "accessed": "2025-12-22T10:05:00Z"}
]
```

---

## Database Functions & Triggers

### 1. Auto-schedule deletion on trip creation

```sql
CREATE OR REPLACE FUNCTION schedule_trip_deletion()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.deletion_schedule (trip_id, scheduled_at, status)
  VALUES (NEW.id, NEW.end_date + INTERVAL '7 days', 'pending');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trigger_schedule_deletion
  AFTER INSERT ON public.trips
  FOR EACH ROW
  EXECUTE FUNCTION schedule_trip_deletion();
```

### 2. Update trip status based on agent jobs

```sql
CREATE OR REPLACE FUNCTION update_trip_status()
RETURNS TRIGGER AS $$
DECLARE
  total_jobs INTEGER;
  completed_jobs INTEGER;
  failed_jobs INTEGER;
BEGIN
  SELECT COUNT(*) INTO total_jobs
  FROM public.agent_jobs
  WHERE trip_id = NEW.trip_id;

  SELECT COUNT(*) INTO completed_jobs
  FROM public.agent_jobs
  WHERE trip_id = NEW.trip_id AND status = 'completed';

  SELECT COUNT(*) INTO failed_jobs
  FROM public.agent_jobs
  WHERE trip_id = NEW.trip_id AND status = 'failed';

  IF failed_jobs > 3 THEN
    UPDATE public.trips SET status = 'failed' WHERE id = NEW.trip_id;
  ELSIF completed_jobs = total_jobs THEN
    UPDATE public.trips SET status = 'completed' WHERE id = NEW.trip_id;
  ELSIF completed_jobs > 0 THEN
    UPDATE public.trips SET status = 'processing' WHERE id = NEW.trip_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER trigger_update_trip_status
  AFTER UPDATE ON public.agent_jobs
  FOR EACH ROW
  EXECUTE FUNCTION update_trip_status();
```

---

## Migration Strategy

1. **Phase 1**: Create base tables (Users, Trips, AgentJobs)
2. **Phase 2**: Create ReportSections, SourceReferences
3. **Phase 14**: Create DeletionSchedule, implement cleanup
4. **Production**: Add indexes, optimize queries, add materialized views if needed

---

## Notes

- All timestamps use `TIMESTAMP WITH TIME ZONE` for global users
- JSONB used for flexible, evolving data structures
- RLS ensures data isolation between users
- Triggers automate status updates and scheduling
- Soft delete pattern used for audit trails

---

**Document Status**: Complete
**Next Review**: After Phase 1 implementation
