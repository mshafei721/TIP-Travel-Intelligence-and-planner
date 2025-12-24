# I5: AI Agents Backend Implementation

> **Prerequisites**: Read `00-session-context.md` first
> **Reference**: `docs/visa-agent-roadmap.md` (detailed specs)

## Objective

Implement all 10 AI agents using CrewAI framework with Celery task integration.

## Current Status

| Agent | Implementation | Tests | Status |
|-------|---------------|-------|--------|
| Base Framework | 0% | 0% | Not Started |
| Orchestrator | 0% | 0% | Not Started |
| Visa Agent | 0% | 0% | Not Started |
| Country Agent | 0% | 0% | Not Started |
| Weather Agent | 0% | 0% | Not Started |
| Currency Agent | 0% | 0% | Not Started |
| Culture Agent | 0% | 0% | Not Started |
| Food Agent | 0% | 0% | Not Started |
| Attractions Agent | 0% | 0% | Not Started |
| Itinerary Agent | 0% | 0% | Not Started |
| Flight Agent | 0% | 0% | Not Started |

---

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│  - Receives trip request from Celery                        │
│  - Coordinates all specialist agents                        │
│  - Aggregates results into final report                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
     ┌─────────┬─────────┼─────────┬─────────┐
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
  │ VISA │ │COUNTRY│ │WEATHER│ │CURRENCY│ │CULTURE│
  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
  │ FOOD │ │ATTRACT│ │ITINER-│ │FLIGHT │ │(future)│
  └──────┘ └──────┘ │  ARY  │ └──────┘ └──────┘
                    └──────┘
```

---

## BASE FRAMEWORK

### File Structure

```
backend/app/agents/
├── __init__.py
├── base.py                   # BaseAgent abstract class
├── config.py                 # Agent configuration
├── interfaces.py             # Input/Output interfaces
├── exceptions.py             # Agent exceptions
├── registry.py               # Agent registry
│
├── orchestrator/
│   ├── __init__.py
│   ├── agent.py              # OrchestratorAgent
│   └── tasks.py              # Coordination tasks
│
├── visa/
│   ├── __init__.py
│   ├── agent.py              # VisaAgent
│   ├── models.py             # Input/Output models
│   ├── prompts.py            # LLM prompts
│   └── tools.py              # API tools
│
├── country/
│   └── ... (same structure)
├── weather/
│   └── ...
├── currency/
│   └── ...
├── culture/
│   └── ...
├── food/
│   └── ...
├── attractions/
│   └── ...
├── itinerary/
│   └── ...
└── flight/
    └── ...
```

### BaseAgent Class

```python
# backend/app/agents/base.py

from abc import ABC, abstractmethod
from pydantic import BaseModel
from crewai import Agent, Task

class BaseAgentInput(BaseModel):
    """Base input for all agents"""
    trip_id: str
    user_nationality: str
    destination_country: str
    destination_city: str
    departure_date: date
    return_date: date

class BaseAgentOutput(BaseModel):
    """Base output for all agents"""
    trip_id: str
    agent_type: str
    generated_at: datetime
    confidence_score: float
    sources: list[str]
    warnings: list[str] = []

class BaseAgent(ABC):
    """Abstract base class for all TIP agents"""

    def __init__(self, llm_model: str = "claude-3-5-sonnet-20241022"):
        self.llm = ChatAnthropic(model=llm_model, temperature=0.1)
        self.agent = self._create_agent()

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return agent type identifier"""
        pass

    @property
    @abstractmethod
    def role(self) -> str:
        """Return agent role description"""
        pass

    @property
    @abstractmethod
    def goal(self) -> str:
        """Return agent goal"""
        pass

    @abstractmethod
    def _create_agent(self) -> Agent:
        """Create CrewAI agent"""
        pass

    @abstractmethod
    def _create_task(self, input: BaseAgentInput) -> Task:
        """Create CrewAI task"""
        pass

    @abstractmethod
    def run(self, input: BaseAgentInput) -> BaseAgentOutput:
        """Execute agent and return result"""
        pass

    def save_result(self, result: BaseAgentOutput) -> None:
        """Save result to database"""
        from app.core.supabase import supabase
        supabase.table("report_sections").insert({
            "trip_id": result.trip_id,
            "section_type": self.agent_type,
            "content": result.model_dump(),
            "generated_at": result.generated_at.isoformat()
        }).execute()
```

---

## AGENT IMPLEMENTATIONS

### 1. Visa Agent (Priority - Proof of Concept)

```python
# backend/app/agents/visa/agent.py

class VisaAgentInput(BaseAgentInput):
    trip_purpose: str = "tourism"
    duration_days: int

class VisaAgentOutput(BaseAgentOutput):
    visa_required: bool
    visa_type: str | None
    max_stay_days: int | None
    processing_time: str | None
    cost_usd: float | None
    required_documents: list[str]
    application_url: str | None
    tips: list[str]

class VisaAgent(BaseAgent):
    agent_type = "visa"
    role = "Visa Requirements Specialist"
    goal = "Provide accurate visa requirements for travelers"

    def _create_agent(self) -> Agent:
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory="""Expert in international travel requirements
            with knowledge of visa policies for all countries.""",
            llm=self.llm,
            tools=[self.visa_lookup_tool],
            verbose=True
        )
```

### 2. Country Agent

```python
class CountryAgentOutput(BaseAgentOutput):
    country_name: str
    capital: str
    population: int
    languages: list[str]
    time_zones: list[str]
    emergency_numbers: dict[str, str]
    power_outlets: str
    driving_side: str
    safety_rating: float
    travel_advisories: list[str]
```

### 3. Weather Agent

```python
class WeatherAgentOutput(BaseAgentOutput):
    forecast: list[DailyForecast]
    average_temp: float
    precipitation_chance: float
    packing_suggestions: list[str]
    best_time_to_visit: str
```

### 4. Currency Agent

```python
class CurrencyAgentOutput(BaseAgentOutput):
    local_currency: str
    exchange_rate: float
    base_currency: str
    atm_availability: str
    card_acceptance: str
    tipping_culture: str
    budget_breakdown: dict[str, float]
```

### 5. Culture Agent

```python
class CultureAgentOutput(BaseAgentOutput):
    greeting_customs: list[str]
    dress_code: str
    religious_considerations: list[str]
    taboos: list[str]
    local_etiquette: list[str]
    common_phrases: list[dict]
```

### 6. Food Agent

```python
class FoodAgentOutput(BaseAgentOutput):
    must_try_dishes: list[Dish]
    restaurant_recommendations: list[Restaurant]
    dietary_considerations: list[str]
    food_safety_tips: list[str]
    price_ranges: dict[str, str]
```

### 7. Attractions Agent

```python
class AttractionsAgentOutput(BaseAgentOutput):
    top_attractions: list[Attraction]
    hidden_gems: list[Attraction]
    day_trips: list[DayTrip]
    estimated_costs: dict[str, float]
    booking_tips: list[str]
```

### 8. Itinerary Agent

```python
class ItineraryAgentOutput(BaseAgentOutput):
    daily_plans: list[DayPlan]
    total_estimated_cost: float
    transportation_plan: str
    accommodation_suggestions: list[Accommodation]
    optimization_notes: list[str]
```

### 9. Flight Agent

```python
class FlightAgentOutput(BaseAgentOutput):
    recommended_flights: list[Flight]
    price_range: dict[str, float]
    booking_tips: list[str]
    airport_info: AirportInfo
    layover_suggestions: list[str] | None
```

---

## ORCHESTRATOR AGENT

```python
# backend/app/agents/orchestrator/agent.py

class OrchestratorAgent:
    """Coordinates all specialist agents"""

    def __init__(self):
        self.agents = {
            "visa": VisaAgent(),
            "country": CountryAgent(),
            "weather": WeatherAgent(),
            "currency": CurrencyAgent(),
            "culture": CultureAgent(),
            "food": FoodAgent(),
            "attractions": AttractionsAgent(),
            "itinerary": ItineraryAgent(),
            "flight": FlightAgent(),
        }

    async def generate_report(self, trip_id: str) -> dict:
        """Generate complete travel report"""
        # 1. Fetch trip data
        trip = await self.get_trip(trip_id)

        # 2. Create agent input
        base_input = self.create_input(trip)

        # 3. Run agents in parallel (where possible)
        results = {}

        # Phase 1: Independent agents (parallel)
        phase1_agents = ["visa", "country", "weather", "currency", "culture"]
        phase1_results = await asyncio.gather(*[
            self.run_agent(name, base_input)
            for name in phase1_agents
        ])

        # Phase 2: Dependent agents (need phase 1 results)
        phase2_agents = ["food", "attractions"]
        phase2_results = await asyncio.gather(*[
            self.run_agent(name, base_input)
            for name in phase2_agents
        ])

        # Phase 3: Itinerary (needs all above)
        itinerary_result = await self.run_agent("itinerary", base_input)

        # Phase 4: Flight (can run in parallel with phase 2-3)
        flight_result = await self.run_agent("flight", base_input)

        # 4. Aggregate and save
        return self.aggregate_results(results)
```

---

## CELERY INTEGRATION

```python
# backend/app/tasks/agent_jobs.py

@shared_task(bind=True, max_retries=3)
def execute_orchestrator(self, trip_id: str):
    """Main task to generate complete travel report"""
    try:
        # Update status
        update_trip_status(trip_id, "processing")

        # Run orchestrator
        orchestrator = OrchestratorAgent()
        result = asyncio.run(orchestrator.generate_report(trip_id))

        # Update status
        update_trip_status(trip_id, "completed")

        return {"success": True, "trip_id": trip_id}

    except Exception as e:
        update_trip_status(trip_id, "failed", str(e))
        raise self.retry(exc=e)
```

---

## EXTERNAL API INTEGRATION

### API Clients

```
backend/app/services/
├── visa/
│   ├── sherpa_client.py      # Sherpa API
│   └── fallback_data.py      # Static fallback
├── weather/
│   └── visual_crossing.py    # Visual Crossing API
├── currency/
│   └── exchange_rate.py      # ExchangeRate API
├── flights/
│   └── skyscanner.py         # Skyscanner API
└── geocoding/
    └── mapbox.py             # Mapbox Geocoding
```

### API Key Requirements

```env
# User must configure in .env
ANTHROPIC_API_KEY=sk-ant-...      # Required
SHERPA_API_KEY=...                # Optional (fallback available)
VISUAL_CROSSING_API_KEY=...       # Optional
EXCHANGERATE_API_KEY=...          # Optional
SKYSCANNER_API_KEY=...            # Optional
MAPBOX_API_KEY=...                # Optional
```

---

## TDD TEST CASES

```python
# backend/tests/agents/

# Base framework tests
def test_base_agent_interface():
    """All agents must implement BaseAgent"""

def test_agent_registry():
    """Registry should contain all agents"""

# Visa agent tests
def test_visa_us_to_france():
    """US → France should be visa-free"""

def test_visa_india_to_usa():
    """India → USA should require visa"""

# Orchestrator tests
def test_orchestrator_runs_all_agents():
    """Should execute all agents"""

def test_orchestrator_handles_agent_failure():
    """Should continue if one agent fails"""

def test_orchestrator_saves_results():
    """Should save all results to database"""

# Integration tests
def test_celery_task_execution():
    """Should run through Celery"""

def test_end_to_end_report_generation():
    """Complete flow from trip to report"""
```

---

## IMPLEMENTATION ORDER

### Phase 1: Base Framework (Day 1)
1. [ ] Create BaseAgent abstract class
2. [ ] Create agent interfaces
3. [ ] Create agent registry
4. [ ] Write base framework tests

### Phase 2: Visa Agent (Day 2) - Proof of Concept
1. [ ] Implement VisaAgent
2. [ ] Create visa tools (API + fallback)
3. [ ] Write comprehensive tests
4. [ ] Test with Celery

### Phase 3: Orchestrator (Day 3)
1. [ ] Implement OrchestratorAgent
2. [ ] Add parallel execution
3. [ ] Add error handling
4. [ ] Write orchestrator tests

### Phase 4: Remaining Agents (Day 4-6)
1. [ ] CountryAgent
2. [ ] WeatherAgent
3. [ ] CurrencyAgent
4. [ ] CultureAgent
5. [ ] FoodAgent
6. [ ] AttractionsAgent
7. [ ] ItineraryAgent
8. [ ] FlightAgent

### Phase 5: Integration (Day 7)
1. [ ] Test all agents together
2. [ ] Performance optimization
3. [ ] Error handling improvements
4. [ ] Update feature_list.json

---

## DEPENDENCIES

```txt
# Add to backend/requirements.txt
crewai>=0.51.0
langchain-anthropic>=0.1.23
httpx>=0.27.0  # For async API calls
```

---

## DELIVERABLES

- [ ] BaseAgent framework complete
- [ ] All 10 agents implemented
- [ ] OrchestratorAgent working
- [ ] Celery integration tested
- [ ] External API clients (with fallbacks)
- [ ] Tests: >80% coverage
- [ ] Railway deployment updated
- [ ] feature_list.json updated
- [ ] Committed and pushed
