# TIP - Travel Intelligence & Planner
## Comprehensive Development Plan

**Version**: 1.0.0
**Last Updated**: 2025-12-22
**Status**: Phase 0 - Research & Planning

---

## Executive Summary

TIP is a **decision-grade travel intelligence system** that provides travelers with accurate, legally compliant, and actionable travel reports. Built on a multi-agent architecture with 10 specialized AI agents, TIP delivers comprehensive intelligence covering visa requirements, weather, budget, culture, attractions, and more.

**Key Differentiator**: NOT a booking platform - focus is on intelligent, trustworthy information aggregation with explicit source attribution and confidence scoring.

---

## Project Phases Overview

| Phase | Name | Features | Status |
|-------|------|----------|---------|
| 0 | Research & Planning | 15 | 73% Complete |
| 1 | Foundation | 13 | Not Started |
| 2 | Orchestrator Agent | 8 | Not Started |
| 3 | Visa & Entry Agent | 8 | Not Started |
| 4 | Country Intelligence Agent | 7 | Not Started |
| 5 | Weather Agent | 6 | Not Started |
| 6 | Currency & Budget Agent | 6 | Not Started |
| 7 | Culture & Law Agent | 6 | Not Started |
| 8 | Food Agent | 6 | Not Started |
| 9 | Attractions Agent | 7 | Not Started |
| 10 | Itinerary Agent | 8 | Not Started |
| 11 | Flight Agent | 7 | Not Started |
| 12 | Trip Creation & Input | 6 | Not Started |
| 13 | Report Generation | 10 | Not Started |
| 14 | Data Lifecycle | 6 | Not Started |
| 15 | Polish & Production | 8 | Not Started |

**Total**: 135 features across 15 phases

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14+ (App Router, TypeScript)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Maps**: Mapbox
- **Auth**: Supabase Auth Client
- **State Management**: React Context + Server Components
- **Form Validation**: Zod
- **HTTP Client**: Fetch API / axios

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **API Style**: REST
- **Async**: Python asyncio
- **Validation**: Pydantic V2
- **Agent Framework**: CrewAI
- **Task Queue**: Celery
- **Worker**: Celery with Redis backend

### Database & Auth
- **Database**: Supabase Postgres
- **Auth**: Supabase Auth (email/password + Google OAuth)
- **ORM**: Supabase Client / SQL Alchemy (if needed)
- **Security**: Row-Level Security (RLS)

### Caching & Jobs
- **Cache**: Redis (Upstash for production)
- **Job Queue**: Celery
- **Result Backend**: Redis

### AI & Agents
- **Orchestration**: CrewAI
- **Primary LLM**: OpenAI GPT-4 Turbo
- **Fallback LLM**: Anthropic Claude 3.5 Sonnet
- **Scraping** (Hybrid 4-Layer):
  - Layer 1: Custom Playwright scrapers (self-hosted, cost control)
  - Layer 2: Apify actors (TripAdvisor, News, battle-tested)
  - Layer 3: Firecrawl (critical visa data backup only)
  - [Source: scraping-apis-for-devs research]

### External APIs
- **Weather**: Visual Crossing
- **Currency**: Fixer.io or ExchangeRate-API
- **Flights**: Skyscanner (MVP) → Amadeus (production)
- **Visa**: Sherpa API or IATA Travel Centre
- **Maps**: Mapbox

### PDF Generation
- **Approach**: Server-side HTML → PDF
- **Library**: Playwright or Puppeteer
- **Storage**: Temporary (auto-deleted after download)

### Deployment
- **Frontend**: Vercel
- **Backend (MVP)**: Render or Railway
- **Backend (Prod)**: AWS (EC2, ECS, ElastiCache)
- **Redis**: Upstash (serverless) or AWS ElastiCache
- **CI/CD**: GitHub Actions

---

## Multi-Agent Architecture

### Agent Graph

```
┌─────────────────────────────────────────────┐
│         ORCHESTRATOR AGENT                  │
│  (Coordinates all agents, validates output) │
└──────────────┬──────────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
   PARALLEL          SEQUENTIAL
      │                 │
      ├─ Visa Agent     └─ Itinerary Agent
      ├─ Country Agent      (depends on all)
      ├─ Weather Agent
      ├─ Currency Agent
      ├─ Culture Agent
      ├─ Food Agent
      ├─ Attractions Agent
      │   (depends on Weather)
      └─ Flight Agent
```

### Agent Details

| Agent | Priority | Dependencies | Output |
|-------|----------|--------------|---------|
| **Orchestrator** | Critical | None | Agent coordination, conflict resolution |
| **Visa & Entry** | Critical | None | Visa requirements, entry conditions, sources |
| **Country** | High | None | Flag, politics, demographics, safety, news |
| **Weather** | High | None | Forecast, historical data, warnings |
| **Currency** | High | None | Exchange rates, daily costs, budget analysis |
| **Culture** | High | None | Etiquette, religious norms, laws, warnings |
| **Food** | Medium | None | National dishes, restaurants, safety |
| **Attractions** | High | Weather, Country | Top attractions, costs, duration, crowds |
| **Itinerary** | Critical | All agents | Day-by-day schedule, weather-aware, budget-aligned |
| **Flight** | High | Dates | Real-time prices, booking links, comparisons |

### Agent Base Class

```python
class BaseAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.sources = []
        self.confidence = 0

    def execute(self, context) -> AgentResult:
        # Execute agent logic
        pass

    def validate(self, result) -> bool:
        # Validate output
        pass

    def retry(self, max_retries=3):
        # Retry logic
        pass
```

### Orchestrator Responsibilities

1. Determine execution graph (topological sort)
2. Launch independent agents in parallel
3. Wait for dependencies before launching dependent agents
4. Validate each agent's output (confidence threshold ≥ 70)
5. Retry failed agents (max 3 attempts)
6. Aggregate results into cohesive report
7. Resolve conflicts (e.g., budget vs itinerary cost)
8. Generate final confidence score
9. Flag sections needing manual review

---

## Data Model (High-Level)

### Core Entities

**Users**
- id, email, auth_provider, created_at, updated_at

**Trips**
- id, user_id, destination_country, cities[], start_date, end_date
- budget_amount, budget_currency, nationality, residence_country
- traveler_count, traveler_ages[], preferences{}, status
- auto_delete_at, deleted_at

**AgentJobs**
- id, trip_id, agent_type, status, started_at, completed_at
- retry_count, error_message, result_data{}, confidence_score

**ReportSections**
- id, trip_id, section_type, content{}, sources[], confidence_score

**SourceReferences**
- id, trip_id, url, source_type, accessed_at, reliability_score

**DeletionSchedule**
- id, trip_id, scheduled_at, executed_at, status

### Row-Level Security (RLS)

- Users can only access their own trips and reports
- System service account can access all for deletion jobs
- No cross-user data visibility

---

## User Flows

### 1. Authentication Flow
Landing → Sign Up/Login → Email Verification → Dashboard

### 2. Trip Creation Flow
Dashboard → Create Trip → Multi-step Form → Validation → Submit → Report Generation

### 3. Report Generation Flow
Job Queued → Agents Running (progress bar) → Partial Results Displayed → Full Report → Export PDF

### 4. Error Handling
Agent Failure → Retry (3x) → Fallback Data → Show Warning → Manual Review Option

### 5. Data Lifecycle
Trip Created → Auto-deletion Scheduled (end_date + 7 days) → Email Notification → Data Purged

---

## API Contracts (REST)

### Authentication
- `POST /auth/register` - Register user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `POST /auth/reset-password` - Reset password

### Trips
- `POST /trips` - Create trip and queue agents
- `GET /trips` - List user's trips
- `GET /trips/:id` - Get trip details
- `DELETE /trips/:id` - Delete trip early
- `GET /trips/:id/status` - Get agent execution status

### Reports
- `GET /trips/:id/report` - Get full report
- `GET /trips/:id/report/:section` - Get specific section
- `GET /trips/:id/report/pdf` - Generate and download PDF

### Agent Jobs
- `GET /trips/:id/jobs` - Get all agent job statuses
- `POST /trips/:id/jobs/:agent/retry` - Manually retry agent

---

## Risk Mitigation Strategies

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Visa Misinformation** | Critical | Official sources only, 2+ source confirmation, prominent disclaimers, manual review queue |
| **API Failures** | High | Circuit breakers, fallback sources, cached results, graceful degradation |
| **Cost Overruns** | Medium | Rate limiting, aggressive caching, auto-deletion, user quotas |
| **Data Privacy** | Critical | Encryption at rest, strict auto-deletion, minimal data collection, GDPR compliance |
| **Performance** | Medium | Async agents, progressive rendering, background jobs, lazy loading |

---

## Quality Assurance Strategy

### Per-Agent Testing

1. **Unit Tests**: Test agent logic with mocked APIs
2. **Integration Tests**: Test with real API (rate-limited)
3. **E2E Tests**: Full pipeline with sample trip data
4. **Confidence Scoring**: Each agent outputs 0-100 confidence
5. **Source Validation**: All facts must have source URLs

### Acceptance Criteria

- All unit tests pass (100% coverage for critical paths)
- Integration tests pass with real APIs
- E2E tests complete full trip → report flow
- Visa Agent achieves ≥ 90% accuracy (manual validation)
- Report generation time < 2 minutes for 90% of trips
- No PII leaks (security audit)

---

## Development Workflow

### Agent-by-Agent Development

1. **Design Phase**: Define agent inputs, outputs, data sources
2. **Implementation**: Write agent class, integrate APIs
3. **Unit Testing**: Mock all external dependencies
4. **Integration Testing**: Test with real APIs (limited)
5. **Code Review**: Review by second developer or AI
6. **Merge**: Merge to main, deploy to staging
7. **Verification**: E2E test on staging
8. **Next Agent**: Proceed to next agent

### Git Workflow

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/<agent-name>`: Per-agent feature branches
- PR required for all merges to `develop`
- Automated tests run on all PRs

---

## Success Metrics

### Phase-Specific Metrics

**Phase 0-2 (Foundation)**
- Setup time < 1 hour (via init.ps1)
- All services configured and tested
- Orchestrator handles 10+ concurrent agent jobs

**Phase 3-11 (Agents)**
- Each agent achieves ≥ 70% confidence score
- API integration success rate > 95%
- Agent execution time < 30 seconds (average)

**Phase 12-13 (Report)**
- Trip creation success rate > 98%
- Report generation success rate > 90%
- Time to first result < 15 seconds
- PDF export success rate > 95%

**Phase 14-15 (Production)**
- Auto-deletion success rate 100%
- Uptime > 99.5%
- Error rate < 1%
- User satisfaction > 4.5/5

---

## Cost Management

### MVP Phase (Free Tiers + Minimal Paid)
- **Target**: ~$75/mo (revised down from $110/mo due to hybrid scraping strategy)
- **Breakdown**:
  - Scraping (Custom + Apify + Firecrawl): $15/mo
  - APIs (Weather, Currency, Maps): Free tiers
  - Fixer.io: $10/mo
  - OpenAI: ~$50/mo
  - Infrastructure: Free tiers (Supabase, Redis, Vercel, Render)
- **Strategy**: Max out free tiers, cache aggressively, rate limit users, use custom scrapers as primary

### Production Phase
- **Target**: ~$541/mo (for first 1K users)
- **Key Change**: Hybrid scraping adds reliability with 4-layer fallback for comparable cost
- **Revenue Model**: Freemium (3 reports/mo free → $9.99/mo unlimited)
- **Break-even**: ~100 paid users
- **See**: docs/services_config.md for detailed breakdown

---

## Timeline Estimates (Not Commitments)

| Phase | Estimated Duration | Notes |
|-------|-------------------|-------|
| Phase 0 | 1 session | Research & planning (current) |
| Phase 1 | 1-2 sessions | Foundation setup |
| Phase 2 | 1 session | Orchestrator |
| Phase 3-11 | 1 session each | 9 agents × 1 session = 9 sessions |
| Phase 12-13 | 2 sessions | UI and report generation |
| Phase 14-15 | 2 sessions | Lifecycle & production prep |
| **Total** | ~17 sessions | Assuming efficient execution |

**Note**: User decides scheduling. This is planning only.

---

## Next Immediate Steps

1. ✅ Complete Phase 0 documentation
2. ⏳ Initialize git repository
3. ⏳ Commit initial structure
4. → Begin Phase 1: Supabase setup
5. → Configure .env with API keys
6. → Run init.ps1 to verify setup

---

## References

### Research Sources

**Weather APIs**:
- [Best Weather API for 2025](https://www.visualcrossing.com/resources/blog/best-weather-api-for-2025/)
- [The Best Weather APIs for 2025](https://www.tomorrow.io/blog/top-weather-apis/)

**Currency APIs**:
- [Free Currency Converter API: 7 Best Conversion APIs of 2025](https://blog.apilayer.com/7-best-free-currency-converter-apis-in-2025/)

**Flight APIs**:
- [Top 5 Flights APIs for Travel Apps](https://www.codebridge.tech/articles/top-5-flights-apis-for-travel-apps)
- [Connect to Amadeus travel APIs](https://developers.amadeus.com/)

**Visa Data**:
- [Sherpa - Visa and Travel Rules API](http://docs.joinsherpa.io/)
- [IATA - Travel Centre](https://www.iata.org/en/services/compliance/timatic/travel-documentation/)

**Maps**:
- [Mapbox vs. Google Maps API: 2026 comparison](https://radar.com/blog/mapbox-vs-google-maps-api)
- [Mapbox API vs Google Maps API for app development in 2025](https://volpis.com/blog/mapbox-vs-google-maps-api-for-app-development/)

### GitHub Repositories Analyzed

- [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) - CrewAI patterns, multi-agent examples
- [cporter202/scraping-apis-for-devs](https://github.com/cporter202/scraping-apis-for-devs) - Scraping API collection, Apify patterns

---

**Document Status**: Complete
**Next Review**: After Phase 1 completion
