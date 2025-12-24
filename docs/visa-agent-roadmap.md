# Visa Agent Implementation Roadmap

> **Status**: Planning Phase
> **Priority**: HIGH (First agent to implement as proof-of-concept)
> **Increment**: I5 - AI Report Generation
> **Last Updated**: 2025-12-24

## 1. Overview

The Visa Agent is the first AI agent to be implemented as a proof-of-concept for the TIP multi-agent architecture. It will gather visa requirements based on user nationality and destination, providing actionable intelligence for trip planning.

### 1.1 Why Visa Agent First?

1. **Clear Input/Output**: Simple inputs (nationality, destination) with structured output
2. **External API Integration**: Demonstrates API integration patterns for other agents
3. **User Value**: High-value information that users need early in trip planning
4. **Validation**: Tests the CrewAI + Celery + FastAPI integration pattern
5. **Foundation**: Establishes patterns for remaining 9 agents

## 2. Architecture

### 2.1 Agent Position in System

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│  (Coordinates all agents, manages job lifecycle)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │   VISA   │    │ COUNTRY  │    │ WEATHER  │
    │  AGENT   │    │  AGENT   │    │  AGENT   │
    └──────────┘    └──────────┘    └──────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │         EXTERNAL DATA SOURCES        │
    │  • Sherpa API (visa requirements)    │
    │  • IATA Travel Centre (backup)       │
    │  • Embassy websites (fallback)       │
    └──────────────────────────────────────┘
```

### 2.2 Data Flow

```
User Request
    │
    ▼
FastAPI Endpoint (POST /api/trips/{id}/generate)
    │
    ▼
Celery Task Queue (Redis)
    │
    ▼
Orchestrator Agent
    │
    ▼
Visa Agent (CrewAI)
    │
    ├─► Sherpa API (primary)
    │   └── OR IATA Travel Centre (secondary)
    │       └── OR Embassy scraping (fallback)
    │
    ▼
Database (report_sections table)
    │
    ▼
Frontend (real-time updates via polling/SSE)
```

## 3. Implementation Phases

### Phase 1: Infrastructure Setup (Prerequisites)

| Task | Description | Status |
|------|-------------|--------|
| I1-INFRA-01 | Set up Redis instance (Upstash or local) | ❌ Pending |
| I1-INFRA-02 | Configure Celery workers | ❌ Pending |
| I1-INFRA-03 | Create Docker Compose for dev | ❌ Pending |
| I1-BE-04 | Install CrewAI dependencies | ❌ Pending |

**Files to create/modify:**
- `backend/requirements.txt` - Add crewai, celery, redis
- `docker-compose.yml` - Redis, Celery worker services
- `backend/app/core/celery.py` - Celery app configuration
- `backend/app/core/redis.py` - Redis connection

### Phase 2: Base Agent Framework

| Task | Description | Status |
|------|-------------|--------|
| AGENT-01 | Create BaseAgent abstract class | ❌ Pending |
| AGENT-02 | Create agent configuration schema | ❌ Pending |
| AGENT-03 | Implement agent result interface | ❌ Pending |
| AGENT-04 | Create agent job tracking | ❌ Pending |

**Files to create:**
```
backend/app/agents/
├── __init__.py
├── base.py              # BaseAgent abstract class
├── config.py            # Agent configuration
├── interfaces.py        # Result interfaces
└── exceptions.py        # Agent exceptions
```

### Phase 3: External API Integration

| Task | Description | Status |
|------|-------------|--------|
| API-01 | Implement Sherpa API client | ❌ Pending |
| API-02 | Implement IATA Travel Centre client | ❌ Pending |
| API-03 | Create fallback scraper (Playwright) | ❌ Pending |
| API-04 | Implement API response caching | ❌ Pending |

**Files to create:**
```
backend/app/services/
├── visa/
│   ├── __init__.py
│   ├── sherpa_client.py    # Sherpa API integration
│   ├── iata_client.py      # IATA backup
│   ├── embassy_scraper.py  # Playwright fallback
│   └── cache.py            # Redis caching layer
```

### Phase 4: Visa Agent Core

| Task | Description | Status |
|------|-------------|--------|
| VISA-01 | Create VisaAgent class | ❌ Pending |
| VISA-02 | Implement visa data model | ❌ Pending |
| VISA-03 | Create visa prompt templates | ❌ Pending |
| VISA-04 | Implement result formatting | ❌ Pending |

**Files to create:**
```
backend/app/agents/visa/
├── __init__.py
├── agent.py              # VisaAgent class
├── models.py             # Pydantic models
├── prompts.py            # LLM prompt templates
├── tasks.py              # CrewAI task definitions
└── tools.py              # CrewAI tools (API calls)
```

### Phase 5: Integration & Testing

| Task | Description | Status |
|------|-------------|--------|
| TEST-01 | Unit tests for VisaAgent | ❌ Pending |
| TEST-02 | Integration tests with APIs | ❌ Pending |
| TEST-03 | End-to-end test with Celery | ❌ Pending |
| TEST-04 | Performance/load testing | ❌ Pending |

## 4. Technical Specifications

### 4.1 Input Schema

```python
class VisaAgentInput(BaseModel):
    """Input for Visa Agent"""
    trip_id: str
    user_nationality: str  # ISO 3166-1 alpha-2 (e.g., "US", "GB")
    destination_country: str  # ISO 3166-1 alpha-2
    destination_city: str
    trip_purpose: str = "tourism"  # tourism, business, transit
    duration_days: int
    departure_date: date
    traveler_count: int = 1
```

### 4.2 Output Schema

```python
class VisaRequirement(BaseModel):
    """Visa requirement information"""
    visa_required: bool
    visa_type: str | None  # "tourist", "business", "e-visa", "visa-free"
    max_stay_days: int | None
    validity_period: str | None  # "90 days", "6 months"

class ApplicationProcess(BaseModel):
    """How to apply for visa"""
    application_method: str  # "online", "embassy", "on-arrival"
    processing_time: str  # "3-5 business days"
    cost_usd: float | None
    cost_local: str | None
    required_documents: list[str]
    application_url: str | None

class EntryRequirement(BaseModel):
    """Entry requirements beyond visa"""
    passport_validity: str  # "6 months beyond stay"
    blank_pages_required: int
    vaccinations: list[str]
    health_declaration: bool
    travel_insurance: bool
    proof_of_funds: bool
    return_ticket: bool

class VisaAgentOutput(BaseModel):
    """Complete output from Visa Agent"""
    trip_id: str
    generated_at: datetime
    confidence_score: float  # 0.0 - 1.0

    # Core visa information
    visa_requirement: VisaRequirement
    application_process: ApplicationProcess
    entry_requirements: EntryRequirement

    # Additional intelligence
    tips: list[str]  # Helpful tips for travelers
    warnings: list[str]  # Important warnings

    # Data provenance
    sources: list[SourceReference]
    last_verified: datetime
```

### 4.3 CrewAI Configuration

```python
# backend/app/agents/visa/agent.py

from crewai import Agent, Task, Crew
from langchain_anthropic import ChatAnthropic

class VisaAgent:
    def __init__(self, llm_model: str = "claude-3-5-sonnet-20241022"):
        self.llm = ChatAnthropic(
            model=llm_model,
            temperature=0.1  # Low temperature for factual accuracy
        )

        self.agent = Agent(
            role="Visa Requirements Specialist",
            goal="Provide accurate, up-to-date visa requirements for travelers",
            backstory="""You are an expert in international travel requirements
            with extensive knowledge of visa policies worldwide. You verify
            information from multiple official sources and always prioritize
            accuracy over speed.""",
            llm=self.llm,
            tools=[
                self.sherpa_tool,
                self.iata_tool,
                self.embassy_scraper_tool
            ],
            verbose=True
        )

    def create_task(self, input: VisaAgentInput) -> Task:
        return Task(
            description=f"""
            Research visa requirements for a {input.user_nationality} citizen
            traveling to {input.destination_country} ({input.destination_city})
            for {input.trip_purpose} purposes for {input.duration_days} days
            starting {input.departure_date}.

            Steps:
            1. Query Sherpa API for official visa requirements
            2. Verify with IATA Travel Centre if available
            3. Check for recent policy changes
            4. Compile required documents list
            5. Calculate estimated costs and processing time
            6. Note any special requirements or warnings

            Return structured JSON matching VisaAgentOutput schema.
            """,
            agent=self.agent,
            expected_output="JSON object with complete visa requirements"
        )
```

### 4.4 Celery Task Integration

```python
# backend/app/tasks/visa_task.py

from celery import shared_task
from app.agents.visa.agent import VisaAgent
from app.core.supabase import supabase

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=120,
    time_limit=180
)
def generate_visa_report(self, trip_id: str, input_data: dict):
    """Celery task to generate visa report"""
    try:
        # Update job status
        supabase.table("agent_jobs").update({
            "status": "running",
            "started_at": datetime.utcnow().isoformat()
        }).eq("trip_id", trip_id).eq("agent_type", "visa").execute()

        # Run agent
        agent = VisaAgent()
        input = VisaAgentInput(**input_data)
        result = agent.run(input)

        # Store result
        supabase.table("report_sections").insert({
            "trip_id": trip_id,
            "section_type": "visa",
            "content": result.model_dump(),
            "generated_at": datetime.utcnow().isoformat()
        }).execute()

        # Update job status
        supabase.table("agent_jobs").update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }).eq("trip_id", trip_id).eq("agent_type", "visa").execute()

        return {"success": True, "trip_id": trip_id}

    except Exception as e:
        # Handle failure
        supabase.table("agent_jobs").update({
            "status": "failed",
            "error_message": str(e)
        }).eq("trip_id", trip_id).eq("agent_type", "visa").execute()

        raise self.retry(exc=e)
```

## 5. External API Details

### 5.1 Sherpa API (Primary)

**Documentation**: https://docs.joinsherpa.com/api
**Cost**: Contact for pricing (free tier available for testing)

```python
# Example request
GET https://api.joinsherpa.com/v1/visa-requirements
Headers:
  Authorization: Bearer {API_KEY}
Query:
  nationality: US
  destination: FR
  departure: 2025-01-15
  return: 2025-01-25
  purpose: tourism
```

### 5.2 IATA Travel Centre (Secondary)

**Documentation**: https://www.iata.org/en/publications/timatic-solutions/
**Cost**: Subscription-based (expensive for production)

### 5.3 Embassy Scraping (Fallback)

Using Playwright for dynamic content:

```python
# backend/app/services/visa/embassy_scraper.py

async def scrape_embassy_visa_info(country_code: str, embassy_url: str):
    """Scrape visa info from embassy website as fallback"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(embassy_url)

        # Extract visa information (site-specific selectors)
        visa_info = await page.evaluate("""
            () => {
                // Extract relevant content
                return {
                    requirements: document.querySelector('.visa-requirements')?.innerText,
                    documents: document.querySelector('.required-docs')?.innerText,
                    // ... more selectors
                }
            }
        """)

        await browser.close()
        return visa_info
```

## 6. Testing Strategy

### 6.1 Unit Tests

```python
# backend/tests/agents/test_visa_agent.py

class TestVisaAgent:
    def test_us_to_france_tourism(self):
        """US citizen traveling to France for tourism (visa-free)"""
        agent = VisaAgent()
        input = VisaAgentInput(
            trip_id="test-123",
            user_nationality="US",
            destination_country="FR",
            destination_city="Paris",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
            traveler_count=1
        )
        result = agent.run(input)

        assert result.visa_requirement.visa_required == False
        assert result.visa_requirement.visa_type == "visa-free"
        assert result.visa_requirement.max_stay_days == 90
        assert result.confidence_score >= 0.9

    def test_india_to_usa_tourism(self):
        """Indian citizen traveling to USA (visa required)"""
        agent = VisaAgent()
        input = VisaAgentInput(
            trip_id="test-456",
            user_nationality="IN",
            destination_country="US",
            destination_city="New York",
            trip_purpose="tourism",
            duration_days=14,
            departure_date=date(2025, 6, 1),
            traveler_count=1
        )
        result = agent.run(input)

        assert result.visa_requirement.visa_required == True
        assert result.visa_requirement.visa_type == "tourist"
        assert "B1/B2" in result.application_process.application_method
```

### 6.2 Integration Tests

```python
# backend/tests/integration/test_visa_flow.py

@pytest.mark.integration
async def test_visa_agent_celery_flow():
    """Test complete visa generation flow through Celery"""
    # Create test trip
    trip_id = create_test_trip()

    # Queue visa task
    task = generate_visa_report.delay(trip_id, {
        "user_nationality": "US",
        "destination_country": "JP",
        "destination_city": "Tokyo",
        "trip_purpose": "tourism",
        "duration_days": 14,
        "departure_date": "2025-06-01",
        "traveler_count": 1
    })

    # Wait for completion (timeout 60s)
    result = task.get(timeout=60)

    assert result["success"] == True

    # Verify database
    report = await get_report_section(trip_id, "visa")
    assert report is not None
    assert report["content"]["visa_requirement"]["visa_required"] == False
```

## 7. Success Criteria

### 7.1 Functional Requirements

| Requirement | Acceptance Criteria |
|-------------|---------------------|
| Visa detection | Correctly identifies if visa required for 50+ country pairs |
| Document list | Provides accurate required documents list |
| Processing time | Returns realistic processing time estimates |
| Cost estimation | Provides cost in USD and local currency |
| E-visa support | Correctly identifies e-visa options |

### 7.2 Performance Requirements

| Metric | Target |
|--------|--------|
| Response time | < 30 seconds per request |
| API success rate | > 95% |
| Cache hit rate | > 70% for repeated queries |
| Accuracy | > 90% verified against official sources |

### 7.3 Quality Gates

- [ ] All unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] No critical security vulnerabilities
- [ ] Performance within targets
- [ ] Documentation complete

## 8. Dependencies

### 8.1 External Services

| Service | Purpose | Status | Action Needed |
|---------|---------|--------|---------------|
| Sherpa API | Primary visa data | Not configured | User: Obtain API key |
| IATA TIM | Backup visa data | Not configured | User: Evaluate subscription |
| Anthropic API | LLM for CrewAI | Configured | Key in .env |
| Redis | Task queue | Not configured | Set up Upstash or local |

### 8.2 Python Dependencies

```txt
# Add to backend/requirements.txt
crewai==0.51.0
langchain-anthropic==0.1.23
celery[redis]==5.3.4
redis==5.0.1
playwright==1.40.0
```

## 9. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API rate limits | High | Medium | Implement caching, request queuing |
| Inaccurate data | Medium | High | Multi-source verification, user feedback |
| API downtime | Low | High | 3-layer fallback (Sherpa → IATA → scraping) |
| Cost overrun | Medium | Medium | Monitor usage, implement alerts |
| LLM hallucination | Medium | High | Low temperature, structured output, validation |

## 10. Next Steps

### Immediate Actions (This Week)

1. **Infrastructure**: Set up Redis and Celery (I1-INFRA-01/02)
2. **Dependencies**: Install CrewAI and related packages
3. **API Key**: User to obtain Sherpa API key
4. **Base Classes**: Create BaseAgent abstract class

### Implementation Order

1. Phase 1: Infrastructure (2-3 days)
2. Phase 2: Base Framework (1-2 days)
3. Phase 3: API Integration (2-3 days)
4. Phase 4: Visa Agent Core (3-4 days)
5. Phase 5: Testing & Refinement (2-3 days)

**Total Estimated Time**: 10-15 days

---

## Appendix A: Country Code Reference

Common country pairs for testing:

| From | To | Expected Result |
|------|-----|-----------------|
| US | FR | Visa-free (Schengen 90 days) |
| US | JP | Visa-free (90 days) |
| US | CN | Visa required |
| GB | US | ESTA required |
| IN | US | B1/B2 visa required |
| IN | TH | Visa on arrival |
| AU | UK | ETA required |

## Appendix B: Related Documentation

- [INTEGRATED_PLAN.md](./INTEGRATED_PLAN.md) - Overall project plan
- [services_config.md](./services_config.md) - External API configuration
- [data_models.md](./data_models.md) - Database schema
- [comprehensive_plan.md](./comprehensive_plan.md) - Architecture overview
