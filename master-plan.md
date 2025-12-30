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
