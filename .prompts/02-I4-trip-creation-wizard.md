# I4: Trip Creation Wizard

> **Prerequisites**: Read `00-session-context.md` first

## Objective

Build the multi-step trip creation wizard that captures all information needed to generate AI travel reports.

## Current Status

| Component | Frontend | Backend | Status |
|-----------|----------|---------|--------|
| Wizard Container | 0% | - | Not Started |
| Step 1: Traveler | 0% | - | Not Started |
| Step 2: Destination | 0% | - | Not Started |
| Step 3: Trip Details | 0% | - | Not Started |
| Step 4: Preferences | 0% | - | Not Started |
| Trip Summary | 0% | - | Not Started |
| Create Trip API | - | 0% | Not Started |
| Draft Auto-save | - | 0% | Not Started |

---

## BACKEND TASKS

### API Endpoints to Implement

```python
# backend/app/api/trips.py

# Existing (verify working)
GET  /api/trips                    # List user trips
GET  /api/trips/{id}               # Get trip details

# New endpoints needed
POST /api/trips                    # Create new trip
PUT  /api/trips/{id}               # Update trip
DELETE /api/trips/{id}             # Delete trip
POST /api/trips/{id}/generate      # Start AI report generation
GET  /api/trips/{id}/status        # Get generation status

# Draft management
POST /api/trips/drafts             # Save draft
GET  /api/trips/drafts             # Get user drafts
PUT  /api/trips/drafts/{id}        # Update draft
DELETE /api/trips/drafts/{id}      # Delete draft
```

### Pydantic Models

```python
# backend/app/models/trips.py

class TravelerDetails(BaseModel):
    name: str
    email: EmailStr
    nationality: str              # ISO 3166-1 alpha-2
    residence_country: str
    origin_city: str
    party_size: int = 1
    party_ages: list[int] = []

class Destination(BaseModel):
    country: str
    city: str
    duration_days: int | None = None

class TripDetails(BaseModel):
    departure_date: date
    return_date: date
    budget: float
    currency: str = "USD"
    trip_purpose: str = "tourism"  # tourism, business, adventure

class TripPreferences(BaseModel):
    travel_style: str = "balanced"
    interests: list[str] = []
    dietary_restrictions: list[str] = []
    accessibility_needs: list[str] = []
    accommodation_type: str = "hotel"
    transportation_preference: str = "any"

class TripCreateRequest(BaseModel):
    traveler_details: TravelerDetails
    destinations: list[Destination]  # Multi-city support
    trip_details: TripDetails
    preferences: TripPreferences
    template_id: str | None = None

class TripResponse(BaseModel):
    id: str
    status: str  # draft, pending, processing, completed, failed
    created_at: datetime
    updated_at: datetime
    traveler_details: TravelerDetails
    destinations: list[Destination]
    trip_details: TripDetails
    preferences: TripPreferences
```

### Celery Task Integration

```python
# backend/app/api/trips.py

@router.post("/{trip_id}/generate")
async def generate_trip_report(trip_id: str, token_payload: dict = Depends(verify_jwt_token)):
    """Queue trip for AI report generation"""
    # 1. Update trip status to 'processing'
    # 2. Queue Celery task
    from app.tasks.agent_jobs import execute_orchestrator
    task = execute_orchestrator.delay(trip_id)

    return {"status": "queued", "task_id": task.id}
```

---

## FRONTEND TASKS

### Documentation Reference

```
product-plan/instructions/incremental/04-trip-creation-input.md
product-plan/sections/trip-creation-input/
product-plan/sections/trip-creation-input/types.ts
product-plan/sections/trip-creation-input/sample-data.json
```

### Components to Build

```
frontend/components/trip-wizard/
├── TripCreationWizard.tsx    # Main wizard container
├── WizardContext.tsx         # React context for state
├── StepIndicator.tsx         # Step dots (1/4, 2/4, etc.)
├── ProgressBar.tsx           # Horizontal progress bar
├── NavigationButtons.tsx     # Back/Next/Submit
├── AutoSaveIndicator.tsx     # "Draft saved" toast
│
├── steps/
│   ├── Step1TravelerDetails.tsx
│   ├── Step2Destination.tsx
│   ├── Step3TripDetails.tsx
│   └── Step4Preferences.tsx
│
├── fields/
│   ├── CountrySelect.tsx     # Searchable country dropdown
│   ├── CitySearch.tsx        # City autocomplete
│   ├── DateRangePicker.tsx   # Departure/return dates
│   ├── BudgetInput.tsx       # Budget with currency
│   ├── PartyComposer.tsx     # Party size + ages
│   ├── InterestTags.tsx      # Multi-select tags
│   └── TravelStyleCards.tsx  # Visual style selector
│
├── TripSummary.tsx           # Review before submit
├── TemplateSelector.tsx      # Load from template modal
└── DestinationCard.tsx       # Multi-city destination card
```

### Pages to Build

```
frontend/app/(app)/trips/
├── page.tsx                  # Trips list (existing)
├── new/
│   ├── page.tsx              # Wizard page
│   ├── loading.tsx
│   └── error.tsx
└── [id]/
    ├── page.tsx              # Trip detail (report view)
    ├── edit/
    │   └── page.tsx          # Edit trip
    └── loading.tsx
```

### Wizard State Management

```typescript
// frontend/components/trip-wizard/WizardContext.tsx

interface WizardState {
  currentStep: number;
  totalSteps: number;
  formData: TripFormData;
  isDirty: boolean;
  draftId: string | null;
  errors: Record<string, string>;
}

interface WizardActions {
  nextStep: () => void;
  prevStep: () => void;
  goToStep: (step: number) => void;
  updateFormData: (data: Partial<TripFormData>) => void;
  saveDraft: () => Promise<void>;
  submitTrip: () => Promise<void>;
  loadTemplate: (templateId: string) => void;
}
```

### API Integration

```typescript
// frontend/lib/api/trips.ts

export async function createTrip(data: TripCreateRequest): Promise<TripResponse>
export async function updateTrip(id: string, data: Partial<TripCreateRequest>): Promise<TripResponse>
export async function deleteTrip(id: string): Promise<void>
export async function generateReport(tripId: string): Promise<{ taskId: string }>
export async function getGenerationStatus(tripId: string): Promise<GenerationStatus>

// Draft management
export async function saveDraft(data: Partial<TripFormData>): Promise<{ draftId: string }>
export async function getDrafts(): Promise<Draft[]>
export async function deleteDraft(id: string): Promise<void>
```

---

## TDD TEST CASES

### Backend Tests

```python
# backend/tests/api/test_trips_create.py

def test_create_trip_valid():
    """Should create trip with valid data"""

def test_create_trip_missing_destination():
    """Should reject trip without destination"""

def test_create_trip_invalid_dates():
    """Should reject trip with return before departure"""

def test_create_multi_city_trip():
    """Should support multiple destinations"""

def test_generate_report_queues_task():
    """Should queue Celery task for report generation"""

def test_get_generation_status():
    """Should return current generation status"""

# Draft tests
def test_save_draft():
    """Should save partial trip as draft"""

def test_resume_from_draft():
    """Should load draft into form"""
```

### Frontend Tests

```typescript
// frontend/__tests__/components/trip-wizard/

describe('TripCreationWizard', () => {
  it('renders step 1 by default')
  it('navigates to next step on valid data')
  it('prevents navigation with invalid data')
  it('shows progress indicator')
  it('auto-saves draft on blur')
})

describe('Step1TravelerDetails', () => {
  it('validates nationality selection')
  it('validates party size > 0')
  it('shows party ages when size > 1')
})

describe('Step2Destination', () => {
  it('allows country search')
  it('shows city autocomplete after country')
  it('supports multi-city toggle')
  it('adds additional destinations')
})

describe('Step3TripDetails', () => {
  it('validates date range')
  it('prevents past departure dates')
  it('calculates trip duration')
  it('validates budget > 0')
})

describe('Step4Preferences', () => {
  it('allows multi-select interests')
  it('shows travel style options')
  it('saves all preferences')
})

describe('TripSummary', () => {
  it('displays all entered data')
  it('allows edit of each section')
  it('submits trip on confirm')
})
```

---

## IMPLEMENTATION ORDER

### Phase 1: Backend APIs (Day 1)
1. [ ] Write tests for trip CRUD endpoints
2. [ ] Implement POST /api/trips
3. [ ] Implement PUT /api/trips/{id}
4. [ ] Implement DELETE /api/trips/{id}
5. [ ] Implement draft endpoints
6. [ ] Implement POST /api/trips/{id}/generate

### Phase 2: Frontend Foundation (Day 2)
1. [ ] Create WizardContext
2. [ ] Build TripCreationWizard container
3. [ ] Build StepIndicator
4. [ ] Build ProgressBar
5. [ ] Build NavigationButtons

### Phase 3: Wizard Steps (Day 3-4)
1. [ ] Build Step1TravelerDetails
2. [ ] Build Step2Destination with multi-city
3. [ ] Build Step3TripDetails
4. [ ] Build Step4Preferences
5. [ ] Build TripSummary

### Phase 4: Field Components (Day 4)
1. [ ] Build CountrySelect (searchable)
2. [ ] Build CitySearch (autocomplete)
3. [ ] Build DateRangePicker
4. [ ] Build BudgetInput
5. [ ] Build PartyComposer
6. [ ] Build InterestTags

### Phase 5: Integration (Day 5)
1. [ ] Connect to backend APIs
2. [ ] Implement auto-save
3. [ ] Add template loading
4. [ ] Test complete flow
5. [ ] Update feature_list.json

---

## WIZARD UX PATTERNS

### Step Transition
```typescript
// Validate current step before proceeding
const handleNext = async () => {
  const isValid = await validateStep(currentStep);
  if (isValid) {
    await saveDraft();
    setCurrentStep(prev => prev + 1);
  }
};
```

### Auto-Save (Debounced)
```typescript
// Save draft 2 seconds after last change
useEffect(() => {
  const timeout = setTimeout(() => {
    if (isDirty) saveDraft();
  }, 2000);
  return () => clearTimeout(timeout);
}, [formData, isDirty]);
```

### Multi-City Toggle
```html
<div class="flex items-center gap-2">
  <Switch checked={isMultiCity} onCheckedChange={setIsMultiCity} />
  <span>I'm visiting multiple cities</span>
</div>
```

---

## DESIGN SYSTEM NOTES

### Wizard Container
```html
<div class="min-h-screen bg-slate-50 dark:bg-slate-950 py-8">
  <div class="max-w-3xl mx-auto px-4">
    <!-- Progress indicator -->
    <!-- Step content -->
    <!-- Navigation buttons -->
  </div>
</div>
```

### Step Card
```html
<div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
  <h2 class="text-2xl font-semibold text-slate-900 dark:text-slate-50 mb-6">
    Step Title
  </h2>
  <!-- Form fields -->
</div>
```

### Progress Indicator
```html
<div class="flex items-center justify-center gap-2 mb-8">
  <div class="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center">1</div>
  <div class="w-12 h-1 bg-blue-600"></div>
  <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400">2</div>
  <!-- ... -->
</div>
```

---

## DELIVERABLES

- [ ] Backend: 8+ API endpoints working
- [ ] Frontend: 20+ components built
- [ ] Frontend: Wizard with 4 steps
- [ ] Auto-save: Draft functionality
- [ ] Multi-city: Support for multiple destinations
- [ ] Tests: >80% coverage
- [ ] Dark mode: All components
- [ ] Responsive: Mobile-first
- [ ] feature_list.json updated
- [ ] Committed and pushed
