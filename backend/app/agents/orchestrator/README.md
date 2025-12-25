# Orchestrator Agent

Coordinates all specialist agents to generate comprehensive travel intelligence reports.

## Overview

The Orchestrator Agent is the central coordinator in the TIP multi-agent system. It manages the lifecycle of specialist agents (Visa, Weather, Currency, etc.) and aggregates their results into a unified travel report.

## Architecture

```
OrchestratorAgent
    │
    ├─► Phase 1: Independent Agents (Parallel)
    │   ├─► Visa Agent
    │   ├─► Country Agent
    │   ├─► Weather Agent
    │   ├─► Currency Agent
    │   └─► Culture Agent
    │
    ├─► Phase 2: Dependent Agents (Sequential)
    │   ├─► Food Agent (needs culture)
    │   └─► Attractions Agent (needs country)
    │
    ├─► Phase 3: Synthesis Agents
    │   └─► Itinerary Agent (needs all above)
    │
    └─► Phase 4: Final Agents
        └─► Flight Agent (can run in parallel)
```

## Features

- **Phased Execution**: Runs agents in dependency-aware phases
- **Parallel Processing**: Executes independent agents concurrently using asyncio
- **Error Recovery**: Continues report generation even if individual agents fail
- **Result Aggregation**: Combines outputs from all agents into unified report
- **Database Integration**: Saves results to `report_sections` and tracks status in `agent_jobs`
- **Extensible**: Easy to add new agents without modifying core logic

## Usage

### Basic Usage

```python
from app.agents.orchestrator.agent import OrchestratorAgent

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Prepare trip data
trip_data = {
    "trip_id": "trip-123",
    "user_nationality": "US",
    "destination_country": "FR",
    "destination_city": "Paris",
    "departure_date": date(2025, 6, 1),
    "return_date": date(2025, 6, 15),
    "trip_purpose": "tourism"
}

# Generate report
result = await orchestrator.generate_report(trip_data)

print(f"Generated {len(result['sections'])} sections")
print(f"Errors: {len(result['errors'])}")
```

### With Celery

```python
from app.tasks.agent_jobs import execute_orchestrator

# Queue orchestrator task
task = execute_orchestrator.delay("trip-123", trip_data)

# Wait for result
result = task.get(timeout=300)  # 5-minute timeout
```

## API

### OrchestratorAgent

#### Methods

**`async generate_report(trip_data: Dict) -> Dict`**

Generate complete travel report.

**Parameters:**
- `trip_data` (dict): Trip information
  - `trip_id` (str): Unique trip identifier
  - `user_nationality` (str): ISO 3166-1 alpha-2 code (e.g., "US")
  - `destination_country` (str): ISO 3166-1 alpha-2 code
  - `destination_city` (str): City name
  - `departure_date` (date): Departure date
  - `return_date` (date): Return date
  - `trip_purpose` (str): "tourism", "business", or "transit"

**Returns:**
```python
{
    "trip_id": "trip-123",
    "generated_at": "2025-12-24T10:00:00Z",
    "sections": {
        "visa": {...},      # Visa requirements
        "country": {...},   # Country information
        "weather": {...},   # Weather forecast
        # ... other sections
    },
    "errors": [
        {
            "agent": "weather",
            "error": "API timeout",
            "timestamp": "2025-12-24T10:01:00Z"
        }
    ],
    "metadata": {
        "agent_count": 8,
        "error_count": 1,
        "orchestrator_version": "1.0.0"
    }
}
```

**`list_available_agents() -> List[str]`**

Get list of available agents.

**`is_agent_available(agent_name: str) -> bool`**

Check if specific agent is available.

## Configuration

### Agent Registry

Agents are registered in `__init__()`:

```python
self.available_agents = {
    'visa': VisaAgent,
    'country': CountryAgent,
    # ... add more agents
}
```

### Execution Phases

Phases defined in `generate_report()`:

```python
# Phase 1: Independent agents
phase1_agents = ['visa', 'country', 'weather', 'currency', 'culture']

# Phase 2: Dependent agents
phase2_agents = ['food', 'attractions']

# Phase 3: Synthesis agents
phase3_agents = ['itinerary']

# Phase 4: Final agents
phase4_agents = ['flight']
```

## Error Handling

The orchestrator handles errors gracefully:

1. **Agent Failures**: Caught and logged, other agents continue
2. **Validation Errors**: Raises `ValueError` with details
3. **Database Errors**: Logged, report generation continues
4. **Timeout Errors**: Agent-specific timeouts enforced

Example error object:

```python
{
    "agent": "weather",
    "error": "API rate limit exceeded",
    "timestamp": "2025-12-24T10:00:00Z"
}
```

## Database Schema

### report_sections Table

```sql
CREATE TABLE report_sections (
    trip_id VARCHAR NOT NULL,
    section_type VARCHAR NOT NULL,
    content JSONB NOT NULL,
    generated_at TIMESTAMP NOT NULL,
    PRIMARY KEY (trip_id, section_type)
);
```

### agent_jobs Table

```sql
CREATE TABLE agent_jobs (
    trip_id VARCHAR NOT NULL,
    agent_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    PRIMARY KEY (trip_id, agent_type)
);
```

## Testing

### Run Tests

```bash
cd backend
python -m pytest tests/agents/test_orchestrator.py -v
```

### Test Coverage

- ✅ Orchestrator initialization
- ✅ Report generation
- ✅ Phase-based execution
- ✅ Error handling
- ✅ Database operations
- ✅ Agent availability checks

## Dependencies

```txt
# Required
asyncio (built-in)
pydantic>=2.0.0

# For agents
crewai>=0.51.0
langchain-anthropic>=0.1.23

# For database
supabase>=1.0.0
```

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Core Orchestrator | ✅ Complete | Async execution, error handling |
| Phase Management | ✅ Complete | 4-phase execution pipeline |
| Visa Agent Integration | ✅ Complete | First specialist agent |
| Database Integration | ✅ Complete | report_sections + agent_jobs |
| Error Recovery | ✅ Complete | Graceful degradation |
| Country Agent | ❌ Pending | Phase 4 implementation |
| Weather Agent | ❌ Pending | Phase 4 implementation |
| Currency Agent | ❌ Pending | Phase 4 implementation |
| Culture Agent | ❌ Pending | Phase 4 implementation |
| Food Agent | ❌ Pending | Phase 4 implementation |
| Attractions Agent | ❌ Pending | Phase 4 implementation |
| Itinerary Agent | ❌ Pending | Phase 4 implementation |
| Flight Agent | ❌ Pending | Phase 4 implementation |

## Next Steps

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Implement Remaining Agents**: CountryAgent, WeatherAgent, etc.
3. **Run Full Test Suite**: Verify all agents integrate correctly
4. **Production Testing**: End-to-end testing with real trip data
5. **Performance Optimization**: Profile and optimize parallel execution

## Troubleshooting

### "No module named 'langchain_anthropic'"

Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### "VISA_AGENT_AVAILABLE is False"

The VisaAgent failed to import. Check:
1. CrewAI installed: `pip install crewai>=0.51.0`
2. Anthropic installed: `pip install langchain-anthropic>=0.1.23`
3. API key configured: `ANTHROPIC_API_KEY` in `.env`

### Tests Failing

Ensure database is accessible:
```python
from app.core.supabase import supabase
print(supabase.table("report_sections").select("*").execute())
```

## Architecture Decisions

### Why Async?

- **Parallel Execution**: Run independent agents simultaneously
- **Improved Throughput**: Handle multiple trips concurrently
- **Better Resource Utilization**: Non-blocking I/O for API calls

### Why Phased Execution?

- **Dependency Management**: Agents that depend on others run after
- **Error Isolation**: Failures in one phase don't block others
- **Optimized Performance**: Maximum parallelization within constraints

### Why Graceful Degradation?

- **User Experience**: Partial report better than no report
- **Reliability**: System remains functional with agent failures
- **Debugging**: Clear error tracking for failed agents

## Contributing

When adding a new agent:

1. **Create Agent Class**: Implement `BaseAgent`
2. **Register Agent**: Add to `available_agents` dict
3. **Assign Phase**: Add to appropriate phase list
4. **Create Input Factory**: Add case to `_create_agent_input()`
5. **Write Tests**: Add tests to `test_orchestrator.py`
6. **Update Documentation**: Update this README

## License

Part of TIP - Travel Intelligence & Planner
