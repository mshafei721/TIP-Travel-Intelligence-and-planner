# I8: Trip Updates & Recalculation

> **Prerequisites**: Read `00-session-context.md` first

## Objective

Enable users to modify trip parameters and trigger selective AI agent recalculation for affected sections.

## Current Status

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Edit Trip Details | 0% | 0% | Not Started |
| Selective Recalc | 0% | 0% | Not Started |
| Change Detection | 0% | 0% | Not Started |
| Version History | 0% | 0% | Not Started |
| Diff View | 0% | - | Not Started |

---

## BACKEND TASKS

### API Endpoints

```python
# backend/app/api/trips.py (additions)

PUT  /api/trips/{id}                    # Update trip (triggers recalc)
POST /api/trips/{id}/recalculate        # Manual recalculation
GET  /api/trips/{id}/changes            # Get pending changes
POST /api/trips/{id}/changes/apply      # Apply changes and recalculate
POST /api/trips/{id}/changes/discard    # Discard pending changes

# Version history
GET  /api/trips/{id}/versions           # List versions
GET  /api/trips/{id}/versions/{version} # Get specific version
POST /api/trips/{id}/versions/{version}/restore  # Restore version
```

### Change Detection Logic

```python
# backend/app/services/change_detection.py

class ChangeDetector:
    """Detect which agents need recalculation based on changes"""

    AGENT_DEPENDENCIES = {
        "visa": ["nationality", "destination", "trip_purpose"],
        "weather": ["destination", "departure_date", "return_date"],
        "currency": ["destination", "budget", "currency"],
        "flights": ["origin", "destination", "departure_date", "return_date"],
        "itinerary": ["destination", "departure_date", "return_date", "preferences"],
        "attractions": ["destination", "preferences", "budget"],
        "food": ["destination", "dietary_restrictions"],
        "culture": ["destination"],
        "country": ["destination"],
    }

    def detect_changes(self, old_trip: Trip, new_trip: Trip) -> dict:
        """Return dict of changed fields"""
        changes = {}
        for field in self.TRACKED_FIELDS:
            old_value = getattr(old_trip, field)
            new_value = getattr(new_trip, field)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
        return changes

    def get_affected_agents(self, changes: dict) -> list[str]:
        """Determine which agents need recalculation"""
        affected = set()
        for field in changes.keys():
            for agent, deps in self.AGENT_DEPENDENCIES.items():
                if field in deps:
                    affected.add(agent)
        return list(affected)
```

### Selective Recalculation

```python
# backend/app/services/recalculation.py

class RecalculationService:
    async def recalculate(self, trip_id: str, agents: list[str]) -> str:
        """Queue selective recalculation for specified agents"""
        from app.tasks.agent_jobs import execute_selective_recalc

        task = execute_selective_recalc.delay(trip_id, agents)

        # Update trip status
        await self.update_status(trip_id, "recalculating", agents)

        return task.id

# backend/app/tasks/agent_jobs.py

@shared_task
def execute_selective_recalc(trip_id: str, agents: list[str]):
    """Recalculate only specified agents"""
    orchestrator = OrchestratorAgent()

    for agent_type in agents:
        # Run individual agent
        result = orchestrator.run_single_agent(agent_type, trip_id)

        # Update section in database
        update_report_section(trip_id, agent_type, result)

    # Update trip status
    update_trip_status(trip_id, "completed")
```

---

## FRONTEND TASKS

### Components to Build

```
frontend/components/trip-edit/
├── TripEditForm.tsx          # Edit trip form
├── ChangePreview.tsx         # Show pending changes
├── AffectedSections.tsx      # Which sections will update
├── RecalculationStatus.tsx   # Recalc progress
├── VersionHistory.tsx        # Version list
├── VersionCard.tsx           # Single version
├── DiffView.tsx              # Compare versions
├── RestoreDialog.tsx         # Confirm restore
└── ChangeConfirmDialog.tsx   # Confirm recalculation
```

### Pages to Build

```
frontend/app/(app)/trips/[id]/
├── edit/
│   └── page.tsx              # Edit trip page
└── history/
    └── page.tsx              # Version history
```

---

## EDIT FLOW UX

```tsx
// frontend/components/trip-edit/TripEditForm.tsx

export function TripEditForm({ trip }: Props) {
  const [formData, setFormData] = useState(trip);
  const [changes, setChanges] = useState<Changes | null>(null);
  const [affectedAgents, setAffectedAgents] = useState<string[]>([]);

  // Detect changes on blur
  const handleFieldBlur = async (field: string) => {
    const detected = await detectChanges(trip.id, formData);
    setChanges(detected.changes);
    setAffectedAgents(detected.affectedAgents);
  };

  const handleSubmit = async () => {
    // Show confirmation with affected sections
    const confirmed = await showConfirmDialog({
      changes,
      affectedAgents,
      estimatedTime: affectedAgents.length * 15, // ~15s per agent
    });

    if (confirmed) {
      await updateTrip(trip.id, formData);
      // Recalculation starts automatically
      router.push(`/trips/${trip.id}?recalculating=true`);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}

      {/* Change preview panel */}
      {changes && (
        <ChangePreview changes={changes}>
          <AffectedSections agents={affectedAgents} />
          <p class="text-sm text-slate-500">
            Updating will recalculate {affectedAgents.length} sections
            (~{affectedAgents.length * 15}s)
          </p>
        </ChangePreview>
      )}

      <Button type="submit" disabled={!changes}>
        Update Trip
      </Button>
    </form>
  );
}
```

### Change Confirmation Dialog

```tsx
// frontend/components/trip-edit/ChangeConfirmDialog.tsx

export function ChangeConfirmDialog({ changes, agents, onConfirm, onCancel }: Props) {
  return (
    <Dialog>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Confirm Changes</DialogTitle>
        </DialogHeader>

        <div class="space-y-4">
          {/* Changes summary */}
          <div>
            <h4 class="font-medium mb-2">What's changing:</h4>
            <ul class="space-y-1">
              {Object.entries(changes).map(([field, { old, new: newVal }]) => (
                <li key={field} class="flex items-center gap-2">
                  <span class="text-slate-500">{formatFieldName(field)}:</span>
                  <span class="line-through text-red-500">{old}</span>
                  <ArrowRight class="w-4 h-4" />
                  <span class="text-green-500">{newVal}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Affected sections */}
          <div>
            <h4 class="font-medium mb-2">Sections to recalculate:</h4>
            <div class="flex flex-wrap gap-2">
              {agents.map(agent => (
                <Badge key={agent}>{formatAgentName(agent)}</Badge>
              ))}
            </div>
          </div>

          {/* Time estimate */}
          <p class="text-sm text-slate-500">
            Estimated time: ~{agents.length * 15} seconds
          </p>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>Cancel</Button>
          <Button onClick={onConfirm}>Update & Recalculate</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

---

## VERSION HISTORY

```tsx
// frontend/components/trip-edit/VersionHistory.tsx

export function VersionHistory({ tripId }: Props) {
  const [versions, setVersions] = useState<Version[]>([]);
  const [comparing, setComparing] = useState<[string, string] | null>(null);

  return (
    <div class="space-y-4">
      <h3 class="text-lg font-semibold">Version History</h3>

      <div class="space-y-2">
        {versions.map((version, index) => (
          <VersionCard
            key={version.id}
            version={version}
            isCurrent={index === 0}
            onCompare={() => setComparing([version.id, versions[0].id])}
            onRestore={() => handleRestore(version.id)}
          />
        ))}
      </div>

      {comparing && (
        <DiffView
          oldVersion={comparing[0]}
          newVersion={comparing[1]}
          onClose={() => setComparing(null)}
        />
      )}
    </div>
  );
}
```

---

## TDD TEST CASES

### Backend Tests

```python
def test_detect_destination_change():
    """Changing destination should affect most agents"""
    changes = detector.detect_changes(old_trip, new_trip)
    affected = detector.get_affected_agents(changes)
    assert "visa" in affected
    assert "weather" in affected
    assert "attractions" in affected

def test_detect_date_change():
    """Changing dates should affect weather and itinerary"""
    changes = {"departure_date": {...}}
    affected = detector.get_affected_agents(changes)
    assert "weather" in affected
    assert "itinerary" in affected
    assert "visa" not in affected

def test_selective_recalculation():
    """Should only run specified agents"""

def test_version_creation():
    """Should create version on update"""

def test_version_restore():
    """Should restore trip to previous version"""
```

### Frontend Tests

```typescript
describe('TripEditForm', () => {
  it('detects changes on field blur')
  it('shows affected sections')
  it('shows confirmation dialog')
  it('triggers recalculation on confirm')
})

describe('ChangeConfirmDialog', () => {
  it('displays all changes')
  it('lists affected agents')
  it('shows time estimate')
})

describe('VersionHistory', () => {
  it('lists all versions')
  it('allows comparison')
  it('allows restore')
})
```

---

## IMPLEMENTATION ORDER

### Phase 1: Change Detection (Day 1)
1. [ ] Build ChangeDetector service
2. [ ] Define agent dependencies
3. [ ] Create changes preview endpoint
4. [ ] Write detection tests

### Phase 2: Selective Recalc (Day 2)
1. [ ] Update Celery task for selective
2. [ ] Add recalculation endpoint
3. [ ] Status tracking
4. [ ] Error handling

### Phase 3: Edit UI (Day 3)
1. [ ] TripEditForm component
2. [ ] ChangePreview component
3. [ ] ChangeConfirmDialog
4. [ ] RecalculationStatus

### Phase 4: Version History (Day 4)
1. [ ] Version storage logic
2. [ ] Version API endpoints
3. [ ] VersionHistory component
4. [ ] DiffView component

### Phase 5: Polish (Day 5)
1. [ ] Real-time status updates
2. [ ] Error recovery
3. [ ] Mobile responsive
4. [ ] Update feature_list.json

---

## DELIVERABLES

- [ ] Change detection system
- [ ] Selective agent recalculation
- [ ] Trip edit form with preview
- [ ] Version history with restore
- [ ] Diff view for comparisons
- [ ] Tests: >80% coverage
- [ ] feature_list.json updated
- [ ] Committed and pushed
