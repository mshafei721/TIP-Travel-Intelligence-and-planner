# TIP - Travel Intelligence & Planner: Master Plan

**Document Version:** 1.0
**Created:** December 30, 2025
**Timeline:** 8+ weeks (Quality-focused)
**Status:** Planning Phase

---

## Executive Summary

The TIP application is approximately **85-90% complete** but has critical integration issues preventing production readiness. The core problems are:

1. **Data Contract Mismatch**: Frontend sends camelCase, backend expects snake_case - **trip creation is broken**
2. **Three Data Paths**: Browser→Supabase, Vercel→Supabase, Vercel→Railway→Supabase causing schema drift
3. **Mock Data in Production**: Visa and destination pages show fake data
4. **Agent Pipeline Incomplete**: Orchestrator exists but agents have placeholders

### Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MVP Scope | Full 10 Agents | Complete travel intelligence experience |
| API Casing | camelCase | Frontend-friendly, backend adds Pydantic aliases |
| Data Path | All via Railway API | Single validation point, consistent contracts |
| Agent Framework | Keep CrewAI | Already integrated, fix rather than rewrite |
| API Cost Strategy | Free + Premium Fallback | Balance cost with data quality |
| Scraping | Playwright + Firecrawl | Self-hosted primary, paid fallback |
| Timeline | 8+ weeks | Quality-focused, production-grade |

---

## Current State Assessment

### Database Tables (Supabase - 16 tables)
| Table | Rows | Status |
|-------|------|--------|
| `trips` | 3 | Core table, working |
| `report_sections` | 14 | 13 section types defined |
| `agent_jobs` | 5 | Job tracking working |
| `user_profiles` | 1 | Basic profile exists |
| `traveler_profiles` | 0 | Empty, needs population |
| `trip_templates` | 0 | Feature not tested |
| `trip_versions` | 0 | Versioning not used |
| `share_links` | 0 | Sharing not implemented |
| `deletion_schedule` | 3 | Auto-deletion partially wired |

### Available API Keys
| Service | Key Present | Status |
|---------|-------------|--------|
| Supabase | Yes | Working |
| OpenAI | Yes | Primary LLM |
| Anthropic | Yes | Backup (quota exhausted) |
| Google/Gemini | Yes | Available |
| RapidAPI | Yes | For flights |
| WeatherAPI | Yes | Working |
| OpenTripMap | Yes | For attractions |
| Mapbox | Yes | For maps |
| Firecrawl | Yes | For scraping |
| **Currency API** | **NO** | Need to add |
| **PostHog** | **NO** | Need to add |

### Critical Bugs from User Testing
| ID | Issue | Severity | Root Cause |
|----|-------|----------|------------|
| UT-1 | Dashboard text not centered | Low | CSS issue |
| UT-2 | "Create Trip" button broken | High | Wrong route |
| UT-3 | Demo user shown | Medium | Not using auth data |
| UT-7 | Trip creation fails | **Critical** | Payload mismatch |
| UT-8 | Profile page fails | High | API response shape |
| UT-9 | Settings toggles broken | Medium | Not persisted |
| UT-10 | Dark mode broken | Medium | State not synced |
| UT-12 | Map not rendering | Medium | Mapbox config |

---

## Architecture: Canonical Data Flow

**Before (3 paths causing drift):**
```
Browser ──→ Supabase (direct)        ← RLS, different validation
Browser ──→ Vercel API ──→ Supabase  ← Different shapes
Browser ──→ Vercel ──→ Railway ──→ Supabase ← Full validation
```

**After (single path):**
```
Browser ──→ Vercel (proxy) ──→ Railway API ──→ Supabase
                                    │
                                    ├── JWT Validation
                                    ├── Pydantic Models (camelCase aliases)
                                    ├── Business Logic
                                    └── Celery Tasks ──→ Agents
```

### API Contract Standard: camelCase with Pydantic Aliases

```python
# Backend Pydantic Model
class TripResponse(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    destination_city: str = Field(alias="destinationCity")
    departure_date: date = Field(alias="departureDate")

    model_config = {
        "populate_by_name": True,  # Accept both formats
        "by_alias": True,          # Output camelCase
    }
```

```typescript
// Frontend TypeScript
interface TripResponse {
    id: string;
    userId: string;       // camelCase
    destinationCity: string;
    departureDate: string;
}
```

---

## Phase 0: Contract Alignment (Week 1)

**Goal:** Establish single source of truth for all API contracts.

### Task 0.1: Backend Pydantic Alias Migration
- [ ] Add `Field(alias="...")` to ALL response models
- [ ] Files: `backend/app/models/trips.py`, `report.py`, `analytics.py`
- [ ] Test: All endpoints return camelCase JSON

### Task 0.2: Frontend Type Sync
- [ ] Update `frontend/types/*.ts` to match camelCase contracts
- [ ] Remove any snake_case references
- [ ] Generate types from OpenAPI spec if possible

### Task 0.3: Remove Direct Supabase Writes from Frontend
- [ ] Audit `frontend/lib/supabase/` for direct mutations
- [ ] Route all writes through Railway API
- [ ] Keep Supabase reads for real-time subscriptions only

### Task 0.4: API Client Standardization
- [ ] Ensure `frontend/lib/api/client.ts` is used everywhere
- [ ] Add request/response interceptors for consistent handling
- [ ] Implement proper error boundaries

**Deliverable:** API contract document with all endpoints, request/response shapes.

---

## Phase 1: Core Functionality Fix (Weeks 2-3)

**Goal:** Make trip creation and profile work end-to-end.

### Task 1.1: Fix Trip Creation Payload
**Priority:** CRITICAL
**Files:**
- `backend/app/api/trips.py` (add aliases)
- `backend/app/models/trips.py` (TripCreateRequest, TripResponse)
- `frontend/components/trip-wizard/TripCreationWizard.tsx`

**Current Issue:**
```javascript
// Frontend sends:
{ residencyCountry: "US", budgetCurrency: "USD", tripPurposes: ["leisure"] }

// Backend expects:
{ residence_country: "US", currency: "USD", trip_purpose: "leisure" }
```

**Fix:** Add Pydantic aliases to accept camelCase:
```python
class TripCreateRequest(BaseModel):
    residence_country: str = Field(alias="residencyCountry")
    currency: str = Field(alias="budgetCurrency")
    trip_purposes: list[str] = Field(alias="tripPurposes")
```

### Task 1.2: Fix Profile API Response Shape
**Priority:** HIGH
**Issue:** Frontend expects `{ templates: [] }`, backend returns `[]`

**Files:**
- `backend/app/api/templates.py`
- `frontend/app/(app)/profile/page.tsx`

### Task 1.3: Wire Settings Toggles to Backend
**Priority:** MEDIUM
**Files:**
- `backend/app/api/profile.py` (add preferences endpoint)
- `frontend/app/(app)/settings/page.tsx`

### Task 1.4: Fix Dark Mode State
**Priority:** MEDIUM
**Files:**
- `frontend/lib/hooks/useTheme.ts`
- `frontend/providers/theme-provider.tsx`

### Task 1.5: Fix User Name in App Shell
**Priority:** LOW
**Files:**
- `frontend/app/(app)/layout.tsx`
- Remove "Demo User" hardcode, use `supabase.auth.getUser()`

**Deliverable:** Trip creation works, profile loads, settings persist.

---

## Phase 2: Agent Pipeline & Real Data (Weeks 4-6)

**Goal:** Replace mock data with real agent-generated intelligence.

### Agent Architecture Overview

```
                    ┌─────────────────┐
                    │  Orchestrator   │
                    │    Agent        │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
   │ Phase 1 │          │ Phase 2 │          │ Phase 3 │
   │ Parallel│          │ Parallel│          │ Sequential │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
   ┌────┴────┐          ┌────┴────┐          ┌────┴────┐
   │  Visa   │          │ Weather │          │Itinerary│
   │ Country │          │Currency │          │         │
   │  Safety │          │ Culture │          │         │
   │         │          │  Food   │          │         │
   │         │          │Attractions│        │         │
   └─────────┘          └─────────┘          └─────────┘
```

### Task 2.1: Implement Free API Integrations

#### Weather Agent (DONE - WeatherAPI)
- Current: WeatherAPI.com (1M calls/month free)
- Fallback: Open-Meteo (unlimited, no key)

#### Currency Agent (NEEDS WORK)
```python
# Add ExchangeRate-API integration
# https://www.exchangerate-api.com/
# Free tier: 1,500 calls/month

class CurrencyTool:
    PRIMARY = "exchangerate-api"  # Free
    FALLBACK = "rapid-api"        # Paid, already have key
```

#### Attractions Agent (NEEDS WORK)
```python
# Current: OpenTripMap (limited)
# Add: Overpass API (OpenStreetMap, unlimited)

class AttractionsTool:
    PRIMARY = "overpass-api"      # Free, unlimited
    FALLBACK = "opentripmap"      # Free, limited
```

#### Flight Agent (NEEDS WORK)
```python
# Use RapidAPI (already have key)
# Options: Skyscanner, Amadeus, or Google Flights via RapidAPI
```

### Task 2.2: Build Scraping Fallback Layer

```python
# backend/app/scrapers/base.py

class ScrapingStrategy:
    """
    4-Layer fallback:
    1. Official API (fastest, most reliable)
    2. Playwright self-hosted (free, good for JS-heavy sites)
    3. Firecrawl (paid, reliable fallback)
    4. BeautifulSoup (simple HTML scraping)
    """

    async def scrape(self, url: str, method: str = "auto") -> dict:
        if method == "api":
            return await self._try_api(url)

        # Try each method in order
        for scraper in [self._playwright, self._firecrawl, self._beautifulsoup]:
            try:
                return await scraper(url)
            except ScrapingError:
                continue

        raise AllScrapersFailedError(url)
```

### Task 2.3: Wire Orchestrator to Real Execution
**Files:**
- `backend/app/agents/orchestrator/agent.py`
- `backend/app/tasks/agent_jobs.py`

**Current Issue:** `agent_jobs.py:162` returns placeholder
**Fix:** Call actual agent `.run()` methods

### Task 2.4: Fix Report Section Storage
**Issue:** Section types don't match enum in DB
**DB Enum:** `visa, destination, itinerary, flight, summary, country, weather, currency, culture, food, attractions, safety, packing`

### Task 2.5: Fix Report Progress UI
**Files:**
- `frontend/components/reports/TripGenerationProgress.tsx`
- `frontend/app/(app)/trips/[id]/page.tsx`

**Issue:** Status fields don't match (`agents_completed` vs `completed_agents`)

**Deliverable:** Real agent data in reports, no mock data in production.

---

## Phase 3: UI/UX Polish (Weeks 7-8)

**Goal:** Beautiful, engaging interface matching design system.

### Design System Reference
| Token | Value |
|-------|-------|
| Primary | Blue (#3B82F6) |
| Secondary | Amber (#F59E0B) |
| Neutral | Slate |
| Font Body | DM Sans |
| Font Code | IBM Plex Mono |

### Task 3.1: Dashboard Polish
- [ ] Center empty state text
- [ ] Fix "Create Your First Trip" button routing
- [ ] Add loading skeletons

### Task 3.2: Trip Wizard Enhancements
- [ ] Age selection: Convert to dropdown with "Infant (<2)" option
- [ ] Country/City: Searchable dropdowns with all countries
- [ ] Multi-city: Visual flow indicator
- [ ] Trip purpose: Multi-select checkboxes

### Task 3.3: Visa Report Page Redesign
**Current Issue:** Shows full progress tracker even when complete

**Target Design:**
```
┌────────────────────────────────────────────┐
│  Visa Requirements for [Country]           │
│  Confidence: 95% ████████████░░            │
├────────────────────────────────────────────┤
│                                            │
│  Visa Status: [Required/Not Required]      │
│                                            │
│  ┌────────────────┐ ┌────────────────┐    │
│  │ Duration       │ │ Cost           │    │
│  │ 90 days        │ │ $160 USD       │    │
│  └────────────────┘ └────────────────┘    │
│                                            │
│  Requirements                              │
│  • Valid passport (6 months)              │
│  • Return flight ticket                    │
│  • Hotel reservation                       │
│                                            │
│  Sources                                   │
│  🏛 US Embassy Official [gov.uk]           │
│  🏛 State Department [travel.state.gov]    │
│                                            │
└────────────────────────────────────────────┘
```

### Task 3.4: Map Integration Fix
**Files:**
- `frontend/app/(app)/history/page.tsx`
- `frontend/components/maps/MapView.tsx`

**Issue:** Map not rendering, showing empty boxes
**Fix:** Verify Mapbox token, check GL JS initialization

### Task 3.5: Report Section Cards
- [ ] Expandable/collapsible sections
- [ ] Confidence badges (green/yellow/gray)
- [ ] Source attribution with icons
- [ ] Print-friendly layout

**Deliverable:** Polished UI matching design system, all pages functional.

---

## Phase 4: Production Readiness (Week 9+)

**Goal:** CI/CD, monitoring, security, performance.

### Task 4.1: CI/CD Fix
**Issue:** `continue-on-error` causes bad deploys
**Files:** `.github/workflows/*.yml`

```yaml
# BEFORE (bad)
- name: Lint
  run: npm run lint
  continue-on-error: true  # ❌ Remove this

# AFTER (good)
- name: Lint
  run: npm run lint
  # No continue-on-error = fails pipeline on lint errors
```

### Task 4.2: PostHog Integration
```bash
# Frontend integration
npx -y @posthog/wizard@latest

# Add to frontend/.env.local
NEXT_PUBLIC_POSTHOG_KEY=phc_xxx
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

**Track:**
- Page views
- Trip creation funnel
- Report generation time
- Error rates

### Task 4.3: Environment Variable Audit
| Variable | Local | Railway | Vercel | Status |
|----------|-------|---------|--------|--------|
| `CORS_ORIGINS` | localhost | ? | - | Verify production URL |
| `SECRET_KEY` | test-key | ? | - | Must not be default |
| `REDIS_URL` | localhost | ? | - | Verify not localhost |
| `SUPABASE_SERVICE_ROLE_KEY` | - | Yes | - | Backend only |

### Task 4.4: Security Checklist
- [ ] Rotate any committed API keys (check git history)
- [ ] Verify JWT audience validation
- [ ] Add server-side rate limiting on auth endpoints
- [ ] Implement upsert pattern in Celery tasks (idempotency)
- [ ] Enable Supabase leaked password protection

### Task 4.5: Performance Baseline
```bash
# k6 load tests
k6 run --vus 10 --duration 30s tests/load/api-health.js
k6 run --vus 5 --duration 60s tests/load/trip-creation.js
```

**Targets:**
- `/api/health`: p95 < 100ms
- `/api/trips` (GET): p95 < 500ms
- `/api/trips` (POST): p95 < 2000ms

**Deliverable:** Production-ready application with monitoring and security.

---
Phase 5: Analytics, Observability, and User Feedback Loop (Week 10+)

Goal: End-to-end telemetry (errors, performance, product analytics) plus a closed-loop user feedback intake (bugs + feature requests) with triage workflow.

Task 5.1: Sentry Integration (Frontend + Backend)

Issue: Production errors are not centralized, no stack traces, no release correlation
Files:

Frontend: frontend/sentry.client.config.ts, frontend/sentry.server.config.ts, frontend/next.config.js

Backend: backend/app/main.py (or your Flask entry), backend/app/config.py

# Frontend (Next.js) Sentry setup
cd frontend
npx @sentry/wizard@latest -i nextjs

# Backend (Python/Flask) Sentry SDK
cd backend
pip install sentry-sdk[flask]


Backend example (Flask):

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
  dsn=os.environ.get("SENTRY_DSN"),
  integrations=[FlaskIntegration()],
  traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
  profiles_sample_rate=float(os.environ.get("SENTRY_PROFILES_SAMPLE_RATE", "0.0")),
  environment=os.environ.get("APP_ENV", "production"),
  release=os.environ.get("APP_RELEASE", "unknown"),
)


Capture:

Unhandled exceptions

API error responses (4xx, 5xx) with context

Frontend crashes + route context

Performance traces for key flows

Task 5.2: Sentry Releases, Source Maps, and Alerting

Issue: Errors are hard to reproduce and not tied to deploy versions
Files: frontend/next.config.js, .github/workflows/*.yml

# Required env vars (CI)
SENTRY_AUTH_TOKEN=xxx
SENTRY_ORG=your-org
SENTRY_PROJECT=your-project
APP_RELEASE=$(git rev-parse --short HEAD)


Alert policy (minimum viable):

Page: spike in Error Rate over baseline

Page: new issue with events > N in 30 minutes

Warn: p95 web vitals degrade (if enabled)

Rule: Alerts map to an owner and a response SLA (even if lightweight).

Task 5.3: PostHog Integration (Product Analytics)

Issue: No visibility on adoption, funnels, drop-offs, retention
Files: frontend/app/layout.tsx (or root), frontend/lib/analytics/*

# Frontend integration (wizard)
cd frontend
npx -y @posthog/wizard@latest

# Add to frontend/.env.local
NEXT_PUBLIC_POSTHOG_KEY=phc_xxx
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com


Track (standardized events):

$pageview (auto)

trip_created (properties: destination, days, travelers_count)

report_generated (properties: duration_ms, success=true|false)

payment_started, payment_completed (if applicable)

feedback_submitted (properties: type=bug|feature, has_attachment)

Task 5.4: Event Taxonomy + Dashboards (Make Analytics Actionable)

Issue: Events become noise if naming and properties are inconsistent
Files: frontend/lib/analytics/events.ts, docs/analytics/event-taxonomy.md

export const EVENTS = {
  TripCreated: "trip_created",
  ReportGenerated: "report_generated",
  FeedbackSubmitted: "feedback_submitted",
} as const;

// Example properties contract
// report_generated: { duration_ms: number; success: boolean; error_code?: string }


Dashboards to build in PostHog:

Acquisition: new users, activation rate

Funnel: landing → trip setup → report generation

Reliability: report success rate, error occurrences by step

Retention: D1, D7 retention for active planners

Rule: No new feature ships without at least 1 measurable event.

Task 5.5: User Feature Request + Bug Report (In-App Intake)

Issue: Users have no structured channel to report problems or request enhancements
Files:

Frontend UI: frontend/components/feedback/FeedbackModal.tsx

API client: frontend/lib/api/feedback.ts

UI requirements (minimum viable):

Entry points: footer link “Send Feedback” + error-state CTA “Report this issue”

Type selector: Bug or Feature Request

Fields:

Title (required)

Description (required)

Email optional (or auto if logged-in)

Screenshot/attachment optional

Auto-attach context:

app version (release)

device/browser

current route

PostHog distinct_id (if available)

Sentry event_id (if report triggered from an error screen)

Task 5.6: Feedback API + Storage + Notifications

Issue: Feedback must land somewhere persistent, searchable, and triageable
Files: backend/app/api/feedback.py, backend/app/models/feedback.py, DB migrations (or Supabase SQL)

Endpoint:

POST /api/feedback

Rate-limited (per IP and per user)

Spam control (basic): throttling + optional captcha later

Payload example:

{
  "type": "bug",
  "title": "Trip creation fails on step 2",
  "description": "After selecting dates, the Next button spins forever.",
  "route": "/trip/create",
  "app_release": "a1b2c3d",
  "posthog_id": "ph_123",
  "sentry_event_id": "abcd1234",
  "attachments": []
}


Routing options (pick one and standardize):

Create GitHub Issues via GitHub App or webhook

Create Linear/Jira tickets via API

Send to Slack channel #feedback-triage with structured fields

Task 5.7: Triage Workflow (Operationalize the Intake)

Issue: Feedback dies in a queue without ownership and rules
Files: .github/ISSUE_TEMPLATE/*, docs/ops/triage.md

Rules (practical):

Bug: reproduce? yes/no within 24 to 48 hours

Severity labels: sev1 (blocked), sev2 (major), sev3 (minor)

Feature requests: tag with theme/* and impact/*

Close-loop: optional automated email “Received” and “Shipped” later

GitHub issue forms (example structure):

Bug: steps to reproduce, expected vs actual, logs, screenshot

Feature: user goal, proposed solution, alternatives, priority

Task 5.8: Analytics Governance (Privacy, PII, and Cost Control)

Issue: Analytics can accidentally collect PII and create compliance risk
Files: docs/analytics/privacy.md, frontend/lib/analytics/sanitize.ts, backend/app/logging.py

Minimum controls:

Do not send raw user input fields (free text) to PostHog by default

Redact tokens, emails, phone numbers from Sentry breadcrumbs

Sampling:

Sentry traces: 0.05 to 0.2 depending on traffic

Session replay: off by default unless explicitly needed

Explicit user consent toggle if required by your policy

Environment Variables Audit
Variable	Frontend	Backend	Prod	Status
NEXT_PUBLIC_POSTHOG_KEY	Yes	-	Set	Required
NEXT_PUBLIC_POSTHOG_HOST	Yes	-	Set	Required
SENTRY_DSN	-	Yes	Set	Required
NEXT_PUBLIC_SENTRY_DSN	Yes	-	Set	Required
APP_RELEASE	Yes	Yes	Set in CI	Required
SENTRY_TRACES_SAMPLE_RATE	-	Yes	Tune	Recommended

Deliverable: A measurable product with production-grade error tracking, performance visibility, adoption funnels, and a user feedback mechanism that reliably produces actionable tickets.


## Cost Optimization Summary

### Before (Current Plan)
| Service | Monthly Cost |
|---------|--------------|
| Supabase | $25 |
| Redis (Upstash) | $10 |
| Weather (Visual Crossing) | $35 |
| Currency (Fixer) | $10 |
| Scraping (Apify + Firecrawl) | $88 |
| Maps (Mapbox) | $50 |
| LLM (OpenAI) | $200 |
| Vercel | $20 |
| Railway | $20 |
| Sentry | $26 |
| **Total** | **$484/mo** |

### After (Optimized)
| Service | Monthly Cost | Change |
|---------|--------------|--------|
| Supabase | $25 | - |
| Redis (Upstash) | $10 | - |
| Weather (WeatherAPI free) | $0 | -$35 |
| Currency (ExchangeRate-API free) | $0 | -$10 |
| Scraping (Playwright self-hosted) | $0 | -$88 |
| Maps (Mapbox free tier) | $0 | -$50 |
| LLM (OpenAI) | $150 | -$50 |
| Vercel | $20 | - |
| Railway | $20 | - |
| PostHog (free tier) | $0 | -$26 |
| **Total** | **$225/mo** | **-54%** |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API key exhaustion | Medium | High | Implement rate limiting, caching |
| Scraping blocks | High | Medium | Multi-layer fallback, rotate IPs |
| LLM hallucinations | Medium | High | Confidence scoring, source verification |
| Schema drift | Low | High | Single data path, generated types |
| Agent timeouts | Medium | Medium | Celery retries, graceful degradation |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Trip creation success rate | ~0% | >95% |
| Report generation time | N/A | <60 seconds |
| Page load time (LCP) | Unknown | <2.5s |
| Error rate | High | <1% |
| User satisfaction | Untested | 4+ stars |

---

## Next Steps

1. **Immediate:** Fix trip creation payload (Task 1.1)
2. **This week:** Complete Phase 0 contract alignment
3. **Week 2:** Profile and settings working
4. **Week 3-4:** Agent pipeline real data
5. **Week 5-6:** Free API integrations
6. **Week 7-8:** UI polish
7. **Week 9+:** Production hardening

---

## Appendix A: File Impact Map

### High-Impact Files (Touch Multiple Systems)
| File | Systems Affected |
|------|------------------|
| `backend/app/models/trips.py` | API, DB, Frontend types |
| `backend/app/api/trips.py` | All trip operations |
| `frontend/lib/api/client.ts` | All API calls |
| `frontend/types/database.ts` | Type safety everywhere |
| `backend/app/tasks/agent_jobs.py` | All agent execution |

### Files to Add
| File | Purpose |
|------|---------|
| `backend/app/scrapers/base.py` | Scraping fallback layer |
| `backend/app/services/currency.py` | Free currency API |
| `frontend/lib/hooks/usePostHog.ts` | Analytics tracking |

---

## Appendix B: API Endpoints Inventory

### Working Endpoints
- `GET /api/health` - Health check
- `GET /api/profile` - User profile
- `GET /api/trips` - List trips
- `POST /api/trips/{id}/generate` - Start report generation

### Broken/Partial Endpoints
- `POST /api/trips` - Payload mismatch (F-01)
- `GET /api/trips/{id}/report/visa` - Returns mock data
- `GET /api/trips/{id}/report/destination` - Returns mock data
- `GET /api/templates` - Wrong response shape

### Not Implemented
- `GET /api/history/*` - History features
- `GET /api/analytics/*` - Analytics dashboard
- `POST /api/share/*` - Sharing functionality

---

*This document is the single source of truth for the TIP remediation project. Update as decisions are made and tasks are completed.*
