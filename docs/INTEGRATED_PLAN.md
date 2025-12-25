# TIP Integrated Plan

## 1. Executive Summary
- Unified the product-plan export (UI scope and milestones) with historical docs (stack, infra, agents, data) into a single, sequenced FE+BE plan with 10 releasable increments and feature flags.
- Final architecture: Next.js 14 App Router frontend, FastAPI + Celery + Redis backend, Supabase Postgres + Auth with PKCE and RLS, Mapbox for maps, Render for backend hosting.
- Data model reconciles product-plan nested types with Supabase JSONB schema and adds missing tables for templates, notifications, and traveler defaults.
- Contracts and schema are defined as initial artifacts for implementation: `contracts/openapi.yaml`, `contracts/types.ts`, and `db/schema.sql`.
- Quality gates cover a11y (WCAG 2.1 AA), security baselines, contract tests, CI pipelines, observability, and rollback discipline.

## 2. Artifact Inventory
| Path | Type | Purpose | Last Modified |
| --- | --- | --- | --- |
| `my-project-design/product-plan.zip` | zip | Export package (specs, components, instructions) | 2025-12-23 21:57 |
| `my-project-design/product-plan-unzipped/product-plan/README.md` | markdown | Export overview and milestones | 2025-12-23 20:32 |
| `my-project-design/product-plan-unzipped/product-plan/product-overview.md` | markdown | Product summary and section list | 2025-12-23 15:37 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/one-shot-instructions.md` | markdown | Combined implementation guide | 2025-12-23 20:29 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/01-foundation.md` | markdown | Milestone 1 instructions | 2025-12-23 20:18 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/02-authentication-account-management.md` | markdown | Milestone 2 instructions | 2025-12-23 20:19 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/03-dashboard-home.md` | markdown | Milestone 3 instructions | 2025-12-23 20:19 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/04-trip-creation-input.md` | markdown | Milestone 4 instructions | 2025-12-23 20:20 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/05-visa-entry-intelligence.md` | markdown | Milestone 5 instructions | 2025-12-23 20:21 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/06-destination-intelligence.md` | markdown | Milestone 6 instructions | 2025-12-23 20:22 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/07-travel-planning-itinerary.md` | markdown | Milestone 7 instructions | 2025-12-23 20:23 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/08-report-management.md` | markdown | Milestone 8 instructions | 2025-12-23 20:24 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/09-user-profile-settings.md` | markdown | Milestone 9 instructions | 2025-12-23 20:25 |
| `my-project-design/product-plan-unzipped/product-plan/instructions/incremental/10-error-states-loading-screens.md` | markdown | Milestone 10 instructions | 2025-12-23 20:26 |
| `my-project-design/product-plan-unzipped/product-plan/data-model/README.md` | markdown | Entity definitions | 2025-12-23 15:40 |
| `my-project-design/product-plan-unzipped/product-plan/data-model/types.ts` | typescript | Data model types | 2025-12-23 15:40 |
| `my-project-design/product-plan-unzipped/product-plan/design-system/tokens.css` | css | Design tokens | 2025-12-23 15:38 |
| `docs/comprehensive_plan.md` | markdown | Stack, phases, agent architecture | 2025-12-22 14:44 |
| `docs/data_models.md` | markdown | Supabase schema and RLS | 2025-12-22 12:07 |
| `docs/services_config.md` | markdown | External services and env vars | 2025-12-22 15:01 |
| `docs/phase1_implementation_guide.md` | markdown | Next.js, FastAPI, Celery patterns | 2025-12-22 14:31 |
| `docs/delivery_dependencies.md` | markdown | Phase dependency DAG | 2025-12-22 14:56 |
| `docs/delivery_dependencies.json` | json | Machine-readable dependencies | 2025-12-22 14:57 |
| `docs/decisions/DR-001-backend-hosting.md` | markdown | Backend hosting decision (Render) | 2025-12-22 14:58 |
| `docs/decisions/DR-002-map-provider.md` | markdown | Map provider decision (Mapbox) | 2025-12-22 14:59 |

## 3. Current FE Baseline
- Frontend app present in `my-project-design` is a Design OS viewer, not the TIP product UI, but provides a baseline React + Tailwind stack.
- Stack: Vite, React 19, TypeScript, React Router, Tailwind CSS v4, Radix UI, lucide icons. (`my-project-design/package.json`)
- Routing: `react-router-dom` `createBrowserRouter` in `my-project-design/src/lib/router.tsx`.
- State and data: local React state, no global store; data loaded at build time from static markdown and zip via `import.meta.glob` in `my-project-design/src/lib/product-loader.ts`.
- API clients and env contracts: none detected; no `fetch` calls in `my-project-design/src`.
- Testing: no unit or e2e framework configured; ESLint present.

File map:
```
my-project-design/
  package.json
  vite.config.ts
  src/
    main.tsx
    index.css
    lib/
      router.tsx
      product-loader.ts
      section-loader.ts
    components/
    sections/
    shell/
    types/
    assets/
```

Dependency list (key): react, react-dom, react-router-dom, tailwindcss, @radix-ui/*, class-variance-authority, lucide-react. (`my-project-design/package.json`)

## 4. Historical Source of Truth
- Stack, agents, REST endpoints, and phase sequencing: `docs/comprehensive_plan.md`.
- Supabase schema, triggers, and RLS patterns: `docs/data_models.md`.
- External services, API keys, and providers (Supabase, Redis, Mapbox, Sherpa, Visual Crossing): `docs/services_config.md`.
- Next.js App Router patterns, FastAPI project structure, Celery setup, Docker, CI: `docs/phase1_implementation_guide.md`.
- Dependency DAG and critical path: `docs/delivery_dependencies.md` and `docs/delivery_dependencies.json`.
- Hosting decision (Render) and map provider decision (Mapbox): `docs/decisions/DR-001-backend-hosting.md`, `docs/decisions/DR-002-map-provider.md`.
- Acceptance criteria coverage and docs remediation status: `docs/remediation_validation_report.md`.
- Product requirements and user stories: `PRD.md`.

Note: `docs/user_flows` exists but contains no files.

## 5. Diff Matrix

### Plan Normalization (product-plan increments)
| IncrementID | Goal | Scope | Inputs | Outputs | Risks | Dependencies |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | Foundation | Design tokens, types, routing, shell | `product-plan/design-system`, `product-plan/data-model`, `product-plan/shell` | UI shell, routing map, core types | Token mismatch, routing drift | None |
| M2 | Auth and account | Login, signup, reset, session | `sections/authentication-account-management` | Auth pages, session flows | OAuth config, rate limits | M1 |
| M3 | Dashboard | Home overview and stats | `sections/dashboard-home` | Dashboard UI | Missing trip data | M1, M2 |
| M4 | Trip creation | Wizard, drafts, validation | `sections/trip-creation-input` | Multi-step form | Complex validation | M1, M2 |
| M5 | Visa intelligence | Visa and entry UI | `sections/visa-entry-intelligence` | Visa section UI | Data accuracy | M4 |
| M6 | Destination intel | Country, weather, culture UI | `sections/destination-intelligence` | Intel cards UI | API latency | M4 |
| M7 | Itinerary | Itinerary, flights, map UI | `sections/travel-planning-itinerary` | Itinerary UI | Agent complexity | M5, M6 |
| M8 | Report management | Trip list, report view, PDF | `sections/report-management` | Report UI + export | PDF reliability | M5-M7 |
| M9 | Profile and settings | Preferences, templates, notifications | `sections/user-profile-settings` | Settings UI | Data model gaps | M2 |
| M10 | Error states | 404/500, loading, progress | `sections/error-states-loading-screens` | Error and loading UI | Consistency | M1-M9 |

### Diff Matrix
| Capability | Plan Proposal | Historical Doc | Conflict/Gap | Proposed Resolution | Rationale |
| --- | --- | --- | --- | --- | --- |
| Frontend framework | Generic React implementation | Next.js 14 App Router with shadcn/ui (`docs/comprehensive_plan.md`) | Plan does not pick a framework | Use Next.js 14 App Router; port product-plan components as client components | Docs define stack and server component patterns |
| Auth | Email/password + Google OAuth | Supabase Auth with PKCE (`docs/phase1_implementation_guide.md`) | Auth provider unspecified in plan | Adopt Supabase Auth; backend validates JWT | Supabase provides RLS integration and PKCE |
| Data model | Nested Trip + Destination types | Supabase schema uses JSONB and flat fields (`docs/data_models.md`) | Mismatch in shape | Store nested structures in JSONB and add templates/notifications tables | Keeps product-plan types while honoring Supabase patterns |
| Agent jobs status | Includes `skipped` | Includes `retrying` (`docs/data_models.md`) | Enum mismatch | Use superset enum in DB and contracts | Prevents data loss and keeps compatibility |
| Map provider | Not specified | Mapbox selected (`docs/decisions/DR-002-map-provider.md`) | Missing decision | Use Mapbox for itinerary and report maps | Canonical decision record |
| Backend hosting | Not specified | Render selected (`docs/decisions/DR-001-backend-hosting.md`) | Missing decision | Use Render for FastAPI + Celery workers | Canonical decision record |
| PDF export | Required by plan | Playwright or Puppeteer suggested (`docs/comprehensive_plan.md`) | Tool choice not defined | Use Playwright for PDF generation | Aligns with scraping tooling and docs |
| Orchestrator and agents | Implied by features | Explicit multi-agent architecture (`docs/comprehensive_plan.md`) | Plan lacks backend agent sequencing | Add orchestrator and agent pipeline in I5-I7 | Required to generate report data |
| Error handling | UI error states | No unified API error contract | Inconsistent FE and BE errors | Standardize ErrorResponse across API | Improves UX and observability |
| Data lifecycle | Auto-delete in UI | Deletion schedule triggers (`docs/data_models.md`) | Missing DB linkage | Implement deletion_schedule table + trigger | GDPR requirement with backend enforcement |

## 6. Target Architecture

### Frontend
- Framework: Next.js 16 App Router with React Server Components and client components where interactivity is required. (`docs/phase1_implementation_guide.md`)
- Routing map:
  - Auth (no shell): `/login`, `/signup`, `/forgot-password`, `/reset-password`, `/verify-email`
  - App shell: `/dashboard`, `/trips`, `/trips/create`, `/trips/[id]`, `/trips/[id]/visa`, `/trips/[id]/destination`, `/trips/[id]/itinerary`, `/profile`
  - Error pages: `/404`, `/500`
- State strategy: server components for data reads; client components with React Hook Form + Zod for forms; TanStack Query for client mutations and polling status updates.
- Design system: Tailwind CSS with product-plan tokens (blue, amber, slate) and shadcn base components mapped to those tokens.
- Error/loading UX: route-level error boundaries, skeletons, global error banner, offline detector.

### Backend
- Framework: FastAPI with domain modules: auth, trips, reports, jobs, profiles, templates, notifications. (`docs/phase1_implementation_guide.md`)
- Async pipeline: Celery workers + Redis for background agent execution; orchestrator coordinates agents; results persisted in `report_sections`.
- Data: Supabase Postgres with RLS; JSONB for nested travel data; triggers for deletion schedule and status updates.
- External services: Mapbox, Visual Crossing, Fixer, Sherpa/IATA, Skyscanner/Amadeus, Apify/Firecrawl (fallback). (`docs/services_config.md`)
- Observability: structured logs, trace IDs, Sentry error reporting, metrics for agent durations and report success rate.

### Interfaces and Contracts
- REST endpoints with JSON payloads; all endpoints require Bearer JWT from Supabase Auth.
- Error contract: `{ requestId, error: { code, message, details } }` for consistency across FE/BE.
- Pagination: cursor-based with `limit` and `nextCursor`.
- Idempotency: use `Idempotency-Key` header for POST/DELETE to prevent duplicate trips and deletes.

ASCII diagram:
```
Browser
  |  Next.js App (App Router, RSC, Tailwind)
  |-- Supabase Auth (PKCE)
  |-- REST -> FastAPI API
                 |-- Supabase Postgres (RLS)
                 |-- Redis (broker/results)
                 |-- Celery workers (agents)
                 |-- External APIs (Visa, Weather, Currency, Flights, Mapbox)
```

Initial OpenAPI (excerpt; full spec in `contracts/openapi.yaml`):
```yaml
openapi: 3.1.0
info:
  title: TIP API
  version: 0.1.0
paths:
  /trips:
    get:
      summary: List trips
    post:
      summary: Create trip (draft or submit)
  /trips/{tripId}:
    get:
      summary: Get trip
    patch:
      summary: Update trip (draft)
    delete:
      summary: Delete trip
  /trips/{tripId}/status:
    get:
      summary: Get trip generation status
  /trips/{tripId}/report:
    get:
      summary: Get full report
  /trips/{tripId}/report/pdf:
    post:
      summary: Generate PDF and return download URL
  /profile:
    get:
      summary: Get user profile
    patch:
      summary: Update user profile
components:
  schemas:
    TripStatus:
      type: string
      enum: [draft, pending, processing, completed, failed]
    Trip:
      type: object
      required: [id, userId, title, status]
    ReportSection:
      type: object
      required: [id, tripId, sectionType, content]
```

DB DDL snippet (full skeleton in `db/schema.sql`):
```sql
create table if not exists public.trips (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  status public.trip_status not null default 'pending',
  traveler_details jsonb not null,
  destinations jsonb not null,
  trip_details jsonb not null,
  preferences jsonb not null,
  auto_delete_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.report_sections (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips(id) on delete cascade,
  section_type public.report_section_type not null,
  content jsonb not null,
  confidence_score integer,
  sources jsonb not null default '[]'::jsonb,
  generated_at timestamptz not null default now()
);
```

## 7. Increment Catalog

### I1 - Foundation and Infra
Goal: Establish the baseline FE/BE architecture, design system tokens, routing, and core data types.

User stories:
- As a user, I can load the app shell and navigate between placeholder routes.
- As a developer, I can run FE/BE locally with CI checks passing.

Acceptance criteria:
- Given a logged-in user, when they open `/dashboard`, then the app shell renders with navigation and a placeholder dashboard.
- Given a CI run, when lint and typecheck execute, then both FE and BE pass.
- Given `/health`, when called, then a 200 response returns `{ status: "ok" }`.

API/DB changes:
- Add `GET /health` in `contracts/openapi.yaml` (backward-compat: additive).
- Create baseline schema objects in `db/schema.sql` (tables and enums).

Tasks:
- Initialize Next.js 14 app with Tailwind and shadcn tokens mapped to product-plan colors.
- Create app shell components and route structure.
- Scaffold FastAPI app, config, and health endpoint.
- Add CI workflows for lint, typecheck, and tests.

Test plan:
- FE: lint, typecheck, basic route render test.
- BE: unit test for `/health`.

Observability:
- Log requestId for all API requests.

Rollout/rollback:
- Feature flag: `ff_foundation` controls shell visibility.
- Rollout: enable for internal users only.
- Rollback: disable flag; no DB changes beyond additive tables.

```DEV_PROMPT
Goal:
- Set up baseline FE/BE project structure, routing, and shell with design tokens.
Code Touchpoints:
- frontend/app/layout.tsx
- frontend/app/(auth)/login/page.tsx
- frontend/components/shell/AppShell.tsx
- backend/app/main.py
- backend/app/core/config.py
- contracts/openapi.yaml
- db/schema.sql
Contracts:
- Add/confirm GET /health in contracts/openapi.yaml (additive).
Tasks:
1) Bootstrap Next.js App Router with Tailwind and shadcn, wire product tokens.
2) Implement AppShell, MainNav, UserMenu with stub data.
3) Scaffold FastAPI with health endpoint and config settings.
4) Add base CI workflow for lint/typecheck/tests.
Tests:
- FE: route smoke test and lint.
- BE: test /health returns status ok.
Acceptance Criteria:
- Given /dashboard, when loaded, then AppShell renders and navigation is visible.
- Given /health, when requested, then 200 OK with JSON status.
Observability:
- Add requestId to API responses and logs.
Rollout Plan:
- Guard shell behind ff_foundation; default off in prod.
Review Checklist:
- lint, typecheck, tests, a11y nav focus states.
```

### I2 - Authentication and Account Management
Goal: Implement Supabase Auth flows with Google OAuth and email/password.

User stories:
- As a user, I can sign up, log in, and reset my password.

Acceptance criteria:
- Given a new user, when they sign up via Google, then they are redirected to `/dashboard`.
- Given a user, when they request password reset, then they receive a reset email.

API/DB changes:
- Enable Supabase Auth with PKCE and Google OAuth. (`docs/phase1_implementation_guide.md`)
- Add `user_profiles` table and RLS policies (backward-compat: additive).

Tasks:
- Configure Supabase Auth client in Next.js.
- Build login, signup, reset password pages using product-plan components.
- Implement server-side auth guard in app shell routes.
- Sync `user_profiles` on first login.

Test plan:
- Auth flow integration tests with Supabase test project.
- UI validation tests for login and reset flows.

Observability:
- Log auth success/failure events with provider type.

Rollout/rollback:
- Feature flag: `ff_auth`.
- Rollout: enable for internal testers.
- Rollback: disable flag and block protected routes.

```DEV_PROMPT
Goal:
- Implement Supabase Auth (email/password and Google OAuth) with app routing.
Code Touchpoints:
- frontend/app/(auth)/login/page.tsx
- frontend/app/(auth)/signup/page.tsx
- frontend/lib/supabaseClient.ts
- backend/app/api/auth/router.py
- db/schema.sql
Contracts:
- No new API endpoints; Supabase handles auth (backward-compat: no changes).
Tasks:
1) Configure Supabase Auth with PKCE and Google OAuth.
2) Build auth pages and connect to Supabase client.
3) Add protected route middleware/guards.
4) Create user_profiles row on first login.
Tests:
- Auth flow tests for signup/login/reset.
Acceptance Criteria:
- Given a new user, when they sign up, then they land on /dashboard.
- Given a user, when reset password is requested, then reset email is sent.
Observability:
- Log auth events and failures with requestId.
Rollout Plan:
- Enable ff_auth for internal users only.
Review Checklist:
- lint, tests, a11y for forms, OAuth redirect validation.
```

### I3 - Dashboard and Home
Goal: Deliver the post-login dashboard with stats, recent trips, and quick actions.

User stories:
- As a user, I can see recent trips and start a new trip from the dashboard.

Acceptance criteria:
- Given a user with trips, when `/dashboard` loads, then recent trips and stats render.
- Given a user with no trips, when `/dashboard` loads, then the empty state appears with a CTA.

API/DB changes:
- Add `GET /trips` and `GET /profile` reads (backward-compat: additive). (`contracts/openapi.yaml`)

Tasks:
- Build dashboard cards and empty states from product-plan specs.
- Implement server component data fetch for trips and stats.

Test plan:
- UI tests for empty and populated states.
- API tests for trip list pagination.

Observability:
- Dashboard load time and API latency metrics.

Rollout/rollback:
- Feature flag: `ff_dashboard`.
- Rollout: enable after I2 stable.
- Rollback: disable flag and route to placeholder.

```DEV_PROMPT
Goal:
- Implement dashboard UI and trip list fetch.
Code Touchpoints:
- frontend/app/dashboard/page.tsx
- frontend/components/dashboard/*
- backend/app/api/trips/router.py
- contracts/openapi.yaml
Contracts:
- Add GET /trips response types (additive).
Tasks:
1) Build dashboard components and empty state.
2) Implement trips list API and stats aggregation.
3) Wire dashboard data loading.
Tests:
- FE: empty vs populated states.
- BE: pagination and auth filtering.
Acceptance Criteria:
- Given no trips, when dashboard loads, then empty state CTA is shown.
- Given trips, when dashboard loads, then cards show recent trips.
Observability:
- Emit dashboard_load_ms metric.
Rollout Plan:
- Gate with ff_dashboard.
Review Checklist:
- lint, tests, a11y for cards and focus order.
```

### I4 - Trip Creation and Input
Goal: Build the multi-step trip creation wizard with drafts and validation.

User stories:
- As a user, I can create a trip with multi-city destinations and save drafts.

Acceptance criteria:
- Given a multi-city trip, when I add destinations, then they are saved and summarized.
- Given a draft, when I return, then the wizard resumes at the last step.

API/DB changes:
- Add `POST /trips`, `PATCH /trips/{tripId}` (backward-compat: additive).
- Persist `traveler_details`, `destinations`, `trip_details`, `preferences` in `trips` table.

Tasks:
- Implement wizard UI, validation, auto-save.
- Add backend endpoints for create/update draft.
- Add idempotency support for create.

Test plan:
- Wizard flow tests (single and multi-city).
- API tests for create/update drafts.

Observability:
- Track draft_save_success rate.

Rollout/rollback:
- Feature flag: `ff_trip_creation`.
- Rollout: enable for internal users; canary by percentage.
- Rollback: disable flag; preserve drafts.

```DEV_PROMPT
Goal:
- Implement trip creation wizard and draft persistence.
Code Touchpoints:
- frontend/app/trips/create/page.tsx
- frontend/components/trip-creation/*
- backend/app/api/trips/router.py
- db/schema.sql
- contracts/openapi.yaml
Contracts:
- Add POST /trips and PATCH /trips/{tripId} (additive).
Tasks:
1) Build wizard steps and validation.
2) Implement draft auto-save and resume logic.
3) Add API endpoints for create/update.
Tests:
- FE: wizard steps, validation, resume draft.
- BE: create/update with RLS.
Acceptance Criteria:
- Given a draft, when user returns, then wizard resumes and data is intact.
- Given invalid dates, when submitting, then validation blocks progress.
Observability:
- Emit trip_create and draft_save metrics.
Rollout Plan:
- Gate with ff_trip_creation.
Review Checklist:
- lint, tests, a11y form labels, client/server validation parity.
```

### I5 - Visa and Entry Intelligence
Goal: Deliver visa and entry report section with agent pipeline foundation.

User stories:
- As a user, I can view visa requirements with official sources and confidence levels.

Acceptance criteria:
- Given visa data exists, when I open the visa section, then it shows requirements and source links.
- Given missing data, when I open the visa section, then a warning banner appears.

API/DB changes:
- Add `GET /trips/{tripId}/report/visa` (backward-compat: additive).
- Add orchestrator + visa agent jobs writing to `report_sections`.

Tasks:
- Build visa UI section and loading states.
- Implement orchestrator skeleton and visa agent integration.
- Store results with confidence and sources.

Test plan:
- Agent unit tests with mocked data sources.
- UI tests for complete vs partial visa data.

Observability:
- Metrics: visa_agent_duration_ms, visa_confidence_score.

Rollout/rollback:
- Feature flag: `ff_visa_intel`.
- Rollout: enable per user after internal validation.
- Rollback: disable flag and hide visa section.

```DEV_PROMPT
Goal:
- Implement visa intelligence section and visa agent pipeline.
Code Touchpoints:
- frontend/app/trips/[id]/visa/page.tsx
- frontend/components/visa/*
- backend/app/agents/visa.py
- backend/app/api/reports/router.py
- db/schema.sql
- contracts/openapi.yaml
Contracts:
- Add GET /trips/{tripId}/report/visa (additive).
Tasks:
1) Build visa UI section with confidence badges and sources.
2) Implement orchestrator skeleton and visa agent job.
3) Persist report_sections for visa.
Tests:
- Agent unit tests for parsing and confidence.
- FE tests for warning banner and sources.
Acceptance Criteria:
- Given visa data, when loaded, then section renders with sources.
- Given partial data, when loaded, then warning banner appears.
Observability:
- Record visa_agent_duration_ms and errors.
Rollout Plan:
- Gate with ff_visa_intel.
Review Checklist:
- lint, tests, a11y for badges and links.
```

### I6 - Destination Intelligence
Goal: Deliver destination intelligence cards powered by multiple agents and APIs.

User stories:
- As a user, I can explore destination facts, weather, currency, culture, safety, and news.

Acceptance criteria:
- Given destination data, when I expand a card, then the detailed content appears.
- Given weather data fails, when I open the weather card, then I see a partial data warning.

API/DB changes:
- Add `GET /trips/{tripId}/report/destination` (backward-compat: additive).
- Add agents for country, weather, currency, culture, safety, news.

Tasks:
- Build destination cards UI.
- Integrate external APIs (Visual Crossing, Fixer, news sources).
- Store results as report sections and sources.

Test plan:
- Integration tests with mocked API responses.
- UI tests for card expand/collapse.

Observability:
- Metrics per agent and API error rates.

Rollout/rollback:
- Feature flag: `ff_destination_intel`.
- Rollout: staged per section; disable any card independently.
- Rollback: hide destination section.

```DEV_PROMPT
Goal:
- Implement destination intelligence cards and agent outputs.
Code Touchpoints:
- frontend/app/trips/[id]/destination/page.tsx
- frontend/components/destination/*
- backend/app/agents/*
- backend/app/api/reports/router.py
- contracts/openapi.yaml
Contracts:
- Add GET /trips/{tripId}/report/destination (additive).
Tasks:
1) Build card grid UI with expand/collapse.
2) Implement destination agents and API integrations.
3) Persist report sections and sources.
Tests:
- FE tests for card interactions.
- BE tests for agent data transforms.
Acceptance Criteria:
- Given destination data, when expanded, then details render.
- Given API failure, when expanded, then warning banner appears.
Observability:
- Track per-agent success rates and durations.
Rollout Plan:
- Gate with ff_destination_intel.
Review Checklist:
- lint, tests, a11y focus states for cards.
```

### I7 - Travel Planning and Itinerary
Goal: Deliver itinerary generation, editing, flights, and map view.

User stories:
- As a user, I can generate an itinerary and edit it with natural language.

Acceptance criteria:
- Given a trip, when I select a style, then a day-by-day itinerary is generated.
- Given a prompt, when I submit changes, then the itinerary updates.

API/DB changes:
- Add `GET /trips/{tripId}/report/itinerary` and `GET /trips/{tripId}/report/flight` (backward-compat: additive).
- Add itinerary and flight agents, Mapbox integration.

Tasks:
- Build itinerary UI with timeline, map, and editing tools.
- Implement itinerary agent and natural language edit endpoint.
- Integrate flight provider API and store options.

Test plan:
- Agent tests for itinerary generation.
- UI tests for edits and map interactions.

Observability:
- Metrics for itinerary_agent_duration and edit_success_rate.

Rollout/rollback:
- Feature flag: `ff_itinerary`.
- Rollout: staged by itinerary style.
- Rollback: disable feature and fallback to summary-only report.

```DEV_PROMPT
Goal:
- Implement itinerary UI, agents, and map integration.
Code Touchpoints:
- frontend/app/trips/[id]/itinerary/page.tsx
- frontend/components/itinerary/*
- frontend/lib/mapbox.ts
- backend/app/agents/itinerary.py
- backend/app/api/reports/router.py
- contracts/openapi.yaml
Contracts:
- Add GET /trips/{tripId}/report/itinerary and /report/flight (additive).
Tasks:
1) Build itinerary timeline and natural language editor.
2) Implement itinerary agent and edit endpoint.
3) Add Mapbox map view and flight options.
Tests:
- FE tests for map toggle and edits.
- BE tests for itinerary generation and edits.
Acceptance Criteria:
- Given a style selection, when generating, then itinerary is returned.
- Given edit prompt, when submitted, then itinerary updates.
Observability:
- Track itinerary generation time and failures.
Rollout Plan:
- Gate with ff_itinerary.
Review Checklist:
- lint, tests, a11y for drag and drop, map keyboard support.
```

### I8 - Report Management
Goal: Provide trip list, report view, PDF export, and deletion scheduling.

User stories:
- As a user, I can view a full report and export it as PDF.

Acceptance criteria:
- Given a completed trip, when I open `/trips/[id]`, then the report renders with navigation.
- Given PDF export, when I click Export, then I receive a downloadable file.

API/DB changes:
- Add `GET /trips/{tripId}/report` and `POST /trips/{tripId}/report/pdf` (backward-compat: additive).
- Enable deletion schedule trigger and warning calculations.

Tasks:
- Build trip list, report detail view, and section navigation.
- Implement PDF generation with Playwright.
- Add deletion schedule UI warnings.

Test plan:
- PDF generation tests in backend.
- UI tests for trip list and report navigation.

Observability:
- Metrics: pdf_generation_ms, report_view_load_ms.

Rollout/rollback:
- Feature flag: `ff_report_management`.
- Rollout: enable per environment, then per user.
- Rollback: disable PDF export and hide report tabs.

```DEV_PROMPT
Goal:
- Implement report management UI and PDF export.
Code Touchpoints:
- frontend/app/trips/page.tsx
- frontend/app/trips/[id]/page.tsx
- frontend/components/reports/*
- backend/app/api/reports/router.py
- backend/app/services/pdf_service.py
- contracts/openapi.yaml
Contracts:
- Add GET /trips/{tripId}/report and POST /trips/{tripId}/report/pdf (additive).
Tasks:
1) Build trip list and report detail layout.
2) Add PDF generation endpoint and service.
3) Add deletion schedule warning UI.
Tests:
- BE tests for PDF generation.
- FE tests for report navigation and export.
Acceptance Criteria:
- Given a trip, when viewing report, then sections render with navigation.
- Given export, when requested, then PDF is generated and downloadable.
Observability:
- Track pdf_generation_ms and failures.
Rollout Plan:
- Gate with ff_report_management.
Review Checklist:
- lint, tests, a11y for report navigation.
```

### I9 - User Profile and Settings
Goal: Deliver profile management, templates, and notification preferences.

User stories:
- As a user, I can update my profile and save trip templates.

Acceptance criteria:
- Given profile changes, when saved, then they persist and reflect in the UI.
- Given a new template, when created, then it appears in template list.

API/DB changes:
- Add `/profile`, `/templates`, `/notifications` endpoints (backward-compat: additive).
- Add `traveler_profiles`, `trip_templates`, `notifications` tables.

Tasks:
- Build settings UI with auto-save.
- Implement templates CRUD and notification toggles.
- Wire to backend endpoints.

Test plan:
- UI tests for auto-save and template CRUD.
- API tests for profile updates.

Observability:
- Metrics: profile_save_success_rate, template_create_rate.

Rollout/rollback:
- Feature flag: `ff_profile_settings`.
- Rollout: enable after report management stable.
- Rollback: disable flag and keep read-only profile view.

```DEV_PROMPT
Goal:
- Implement profile and settings with templates and notifications.
Code Touchpoints:
- frontend/app/profile/page.tsx
- frontend/components/profile/*
- backend/app/api/profile/router.py
- backend/app/api/templates/router.py
- backend/app/api/notifications/router.py
- db/schema.sql
Contracts:
- Add GET/PATCH /profile, CRUD /templates, GET/PATCH /notifications (additive).
Tasks:
1) Build settings UI with auto-save indicators.
2) Implement templates CRUD endpoints.
3) Implement notification preference updates.
Tests:
- FE tests for auto-save and template modals.
- BE tests for profile update and template CRUD.
Acceptance Criteria:
- Given profile edits, when saved, then updates persist.
- Given a template create, when saved, then list updates.
Observability:
- Track profile_save_success_rate.
Rollout Plan:
- Gate with ff_profile_settings.
Review Checklist:
- lint, tests, a11y for form fields and modals.
```

### I10 - Error States, Loading, and Hardening
Goal: Implement app-wide error handling, loading UX, and finalize quality gates.

User stories:
- As a user, I see clear error states and progress during report generation.

Acceptance criteria:
- Given a 404 route, when opened, then a standalone 404 page appears.
- Given report generation, when running, then progress stages update.

API/DB changes:
- Standardize ErrorResponse across API responses (backward-compat: additive, no breaking fields).

Tasks:
- Build error pages, inline error banners, skeletons, offline detector.
- Add progress status polling for report generation.
- Integrate Sentry and structured logging.

Test plan:
- UI tests for 404/500 and error banners.
- API tests for error response shape.

Observability:
- Sentry configured for FE and BE; error rate dashboards.

Rollout/rollback:
- Feature flag: `ff_error_states`.
- Rollout: enable after I8; can disable if regressions.
- Rollback: disable flag and fall back to basic error boundaries.

```DEV_PROMPT
Goal:
- Add error states, loading screens, and observability integration.
Code Touchpoints:
- frontend/app/not-found.tsx
- frontend/app/error.tsx
- frontend/components/errors/*
- backend/app/core/exceptions.py
- contracts/openapi.yaml
Contracts:
- Ensure ErrorResponse shape across all endpoints (additive).
Tasks:
1) Implement 404/500 pages and inline error banners.
2) Add report generation progress UI and polling.
3) Integrate Sentry in FE and BE.
Tests:
- FE tests for error pages and banners.
- BE tests for error response structure.
Acceptance Criteria:
- Given invalid route, when loaded, then 404 page renders.
- Given API failure, when retry clicked, then request reattempts.
Observability:
- Send errors to Sentry with requestId.
Rollout Plan:
- Gate with ff_error_states.
Review Checklist:
- lint, tests, a11y for error messaging and focus.
```

## 8. Quality Gates and Runbook

Quality gates:
- Performance: API p95 < 300ms for read endpoints; report generation < 2 minutes for p90.
- A11y: WCAG 2.1 AA (labels, contrast, keyboard navigation, focus order).
- Security: Supabase RLS enforced, JWT validation, secret scanning, no PII in logs.
- Privacy: auto-delete 7 days after trip end; export audit log.
- Reliability: retry policies for agents, circuit breakers for APIs.

CI pipeline:
- Frontend: lint, typecheck, unit tests, build.
- Backend: lint (flake8/ruff), unit tests, contract tests, DB migration checks.
- Contract: OpenAPI lint + generated client validation.

Runbook checklist:
- Preflight: verify env vars, Supabase keys, Redis connectivity, Mapbox key.
- Deploy: run migrations, enable feature flags sequentially.
- Rollback: disable flag, revert migrations using expand/contract plan.
- Post-deploy: monitor error rate, latency, queue backlog, PDF generation success.

## 9. Risks and Spikes
| Risk | Impact | Mitigation | Spike (exit criteria) |
| --- | --- | --- | --- |
| Visa data accuracy | Critical compliance risk | Use official sources, source attribution, confidence scoring | Spike: validate visa coverage for top 10 countries with 95% accuracy |
| External API limits | Service failures | Caching, retries, fallback scrapers | Spike: load test Visual Crossing and Fixer API quotas |
| PDF generation fidelity | Broken exports | Use Playwright, add snapshot tests | Spike: generate sample PDFs for 5 trip sizes |
| Mapbox integration cost | Budget overrun | Cache tiles, limit loads | Spike: estimate loads for 1k users and verify free tier |
| Agent latency | Poor UX | Async pipeline with progress updates | Spike: run full pipeline with sample data under 2 min |
| Data model drift | Data inconsistencies | Contracts and schema alignment | Spike: round-trip test TripCreate -> TripRead with nested JSONB |
| Auth edge cases | Lockouts and login failures | Rate limiting and secure flows | Spike: test OAuth flow and reset in staging |
| GDPR deletion | Compliance risk | Automated deletion schedule | Spike: verify deletion job and audit logs in staging |

## 10. Roadmap and RACI

Roadmap (Gantt-style bullets):
- Weeks 1-2: I1 Foundation and Infra
- Week 3: I2 Authentication and Account Management
- Week 4: I3 Dashboard and Home
- Weeks 5-6: I4 Trip Creation and Input
- Weeks 7-8: I5 Visa and Entry Intelligence
- Weeks 9-10: I6 Destination Intelligence
- Weeks 11-12: I7 Travel Planning and Itinerary
- Week 13: I8 Report Management
- Week 14: I9 User Profile and Settings
- Week 15: I10 Error States and Hardening

RACI:
| Activity | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| Architecture and contracts | Tech Lead | Product Owner | FE, BE, Security | QA |
| Frontend implementation | Frontend Lead | Tech Lead | Product, Design | QA |
| Backend implementation | Backend Lead | Tech Lead | Data/ML, DevOps | QA |
| Agent integrations | Data/ML Lead | Tech Lead | Backend Lead | Product |
| Infra and CI/CD | DevOps | Tech Lead | Backend Lead | Product |
| QA and testing | QA Lead | Tech Lead | FE, BE | Product |
| Security and privacy | Security | Product Owner | Tech Lead | QA |
