# I9: Templates & Travel History

> **Prerequisites**: Read `00-session-context.md` first

## Objective

Enable users to save trip configurations as templates and maintain a browsable travel history.

## Current Status

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Save as Template | 0% | 0% | Not Started |
| Template Library | 0% | 0% | Not Started |
| Apply Template | 0% | 0% | Not Started |
| Public Templates | 0% | 0% | Not Started |
| Travel History | 0% | 0% | Not Started |
| Trip Archive | 0% | 0% | Not Started |

---

## BACKEND TASKS

### API Endpoints

```python
# backend/app/api/templates.py

# User templates
GET  /api/templates                     # List user's templates
POST /api/templates                     # Create template
GET  /api/templates/{id}                # Get template details
PUT  /api/templates/{id}                # Update template
DELETE /api/templates/{id}              # Delete template

# Public templates
GET  /api/templates/public              # Browse public templates
GET  /api/templates/public/featured     # Featured templates
POST /api/templates/{id}/clone          # Clone template to user

# Apply to trip
POST /api/trips/from-template/{template_id}  # Create trip from template

# backend/app/api/history.py

# Travel history
GET  /api/history                       # Get travel history
GET  /api/history/stats                 # Travel statistics
GET  /api/history/countries             # Countries visited
GET  /api/history/timeline              # Timeline view
POST /api/trips/{id}/archive            # Archive trip
POST /api/trips/{id}/unarchive          # Restore from archive
```

### Data Models

```python
# backend/app/models/templates.py

class TripTemplate(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None
    cover_image: str | None
    is_public: bool = False
    tags: list[str] = []

    # Template content (trip configuration without dates)
    destinations: list[TemplateDestination]
    preferences: TripPreferences
    typical_duration: int  # days
    estimated_budget: float
    currency: str

    # Metadata
    use_count: int = 0
    created_at: datetime
    updated_at: datetime

class TemplateDestination(BaseModel):
    country: str
    city: str
    suggested_days: int
    highlights: list[str] = []

# backend/app/models/history.py

class TravelHistoryEntry(BaseModel):
    trip_id: str
    destination: str
    country: str
    dates: DateRange
    status: str  # completed, cancelled
    rating: int | None  # User rating 1-5
    notes: str | None
    photos: list[str] = []

class TravelStats(BaseModel):
    total_trips: int
    countries_visited: int
    cities_visited: int
    total_days_traveled: int
    favorite_destination: str | None
    most_visited_country: str | None
    travel_streak: int  # consecutive months with travel
```

---

## FRONTEND TASKS

### Components to Build

```
frontend/components/templates/
├── TemplateCard.tsx          # Template preview card
├── TemplateGrid.tsx          # Template gallery
├── TemplateDetail.tsx        # Full template view
├── CreateTemplateDialog.tsx  # Save trip as template
├── TemplateForm.tsx          # Edit template
├── TemplateFilters.tsx       # Filter by tags, destination
├── FeaturedTemplates.tsx     # Featured carousel
├── UseTemplateDialog.tsx     # Apply template to new trip
└── TemplateStats.tsx         # Usage statistics

frontend/components/history/
├── TravelTimeline.tsx        # Timeline visualization
├── TravelMap.tsx             # World map with visited countries
├── TravelStats.tsx           # Statistics cards
├── TripHistoryList.tsx       # List of past trips
├── TripHistoryCard.tsx       # Single trip card
├── CountryBadges.tsx         # Visited countries display
├── ArchiveDialog.tsx         # Archive confirmation
└── TripRating.tsx            # Rate past trip
```

### Pages to Build

```
frontend/app/(app)/
├── templates/
│   ├── page.tsx              # Template library
│   ├── [id]/
│   │   └── page.tsx          # Template detail
│   └── create/
│       └── page.tsx          # Create template
└── history/
    ├── page.tsx              # Travel history
    ├── map/
    │   └── page.tsx          # World map view
    └── stats/
        └── page.tsx          # Statistics page
```

---

## TEMPLATE LIBRARY UI

```tsx
// frontend/app/(app)/templates/page.tsx

export default function TemplatesPage() {
  return (
    <div class="space-y-8">
      {/* Featured templates */}
      <section>
        <h2 class="text-2xl font-semibold mb-4">Featured Templates</h2>
        <FeaturedTemplates />
      </section>

      {/* User's templates */}
      <section>
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-semibold">My Templates</h2>
          <Button onClick={() => router.push('/templates/create')}>
            + Create Template
          </Button>
        </div>
        <TemplateGrid templates={userTemplates} />
      </section>

      {/* Public templates */}
      <section>
        <h2 class="text-2xl font-semibold mb-4">Explore Templates</h2>
        <TemplateFilters
          tags={availableTags}
          destinations={popularDestinations}
          onFilter={handleFilter}
        />
        <TemplateGrid templates={publicTemplates} />
      </section>
    </div>
  );
}
```

### Template Card

```tsx
// frontend/components/templates/TemplateCard.tsx

export function TemplateCard({ template }: Props) {
  return (
    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden hover:shadow-lg transition-shadow">
      {/* Cover image */}
      <div class="aspect-video relative">
        <Image
          src={template.coverImage || '/images/default-template.jpg'}
          alt={template.name}
          fill
          class="object-cover"
        />
        {template.isPublic && (
          <Badge class="absolute top-2 right-2" variant="secondary">
            Public
          </Badge>
        )}
      </div>

      {/* Content */}
      <div class="p-4">
        <h3 class="font-semibold text-lg mb-1">{template.name}</h3>
        <p class="text-sm text-slate-500 mb-3 line-clamp-2">
          {template.description}
        </p>

        {/* Destinations */}
        <div class="flex flex-wrap gap-1 mb-3">
          {template.destinations.map(dest => (
            <Badge key={dest.city} variant="outline" size="sm">
              {dest.city}
            </Badge>
          ))}
        </div>

        {/* Meta */}
        <div class="flex justify-between text-sm text-slate-500">
          <span>{template.typicalDuration} days</span>
          <span>~{formatCurrency(template.estimatedBudget)}</span>
        </div>

        {/* Actions */}
        <div class="mt-4 flex gap-2">
          <Button variant="outline" size="sm" class="flex-1">
            View
          </Button>
          <Button size="sm" class="flex-1">
            Use Template
          </Button>
        </div>
      </div>
    </div>
  );
}
```

---

## TRAVEL HISTORY UI

```tsx
// frontend/app/(app)/history/page.tsx

export default function TravelHistoryPage() {
  return (
    <div class="space-y-8">
      {/* Stats overview */}
      <TravelStats stats={stats} />

      {/* World map */}
      <section class="bg-white dark:bg-slate-900 rounded-xl p-6">
        <h2 class="text-xl font-semibold mb-4">Countries Visited</h2>
        <TravelMap countries={visitedCountries} />
        <CountryBadges countries={visitedCountries} />
      </section>

      {/* Timeline */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Travel Timeline</h2>
        <TravelTimeline entries={history} />
      </section>

      {/* Past trips */}
      <section>
        <h2 class="text-xl font-semibold mb-4">Past Trips</h2>
        <TripHistoryList trips={completedTrips} />
      </section>
    </div>
  );
}
```

### Travel Stats

```tsx
// frontend/components/history/TravelStats.tsx

export function TravelStats({ stats }: Props) {
  return (
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatCard
        label="Countries Visited"
        value={stats.countriesVisited}
        icon={GlobeIcon}
        color="blue"
      />
      <StatCard
        label="Cities Explored"
        value={stats.citiesVisited}
        icon={BuildingIcon}
        color="amber"
      />
      <StatCard
        label="Total Trips"
        value={stats.totalTrips}
        icon={PlaneIcon}
        color="green"
      />
      <StatCard
        label="Days Traveled"
        value={stats.totalDaysTraveled}
        icon={CalendarIcon}
        color="purple"
      />
    </div>
  );
}
```

### Travel Map (World Map)

```tsx
// frontend/components/history/TravelMap.tsx

import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

export function TravelMap({ countries }: Props) {
  const visitedCountryCodes = new Set(countries.map(c => c.code));

  return (
    <div class="w-full aspect-[2/1]">
      <ComposableMap>
        <Geographies geography="/world-110m.json">
          {({ geographies }) =>
            geographies.map(geo => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill={
                  visitedCountryCodes.has(geo.properties.ISO_A2)
                    ? '#3B82F6'  // Visited - blue
                    : '#E2E8F0'  // Not visited - slate
                }
                stroke="#fff"
                strokeWidth={0.5}
              />
            ))
          }
        </Geographies>
      </ComposableMap>
    </div>
  );
}
```

---

## TDD TEST CASES

### Backend Tests

```python
def test_create_template():
    """Should create template from trip"""

def test_clone_public_template():
    """Should clone template to user's library"""

def test_create_trip_from_template():
    """Should create trip with template values"""

def test_travel_stats_calculation():
    """Should calculate accurate statistics"""

def test_archive_trip():
    """Should move trip to archive"""
```

### Frontend Tests

```typescript
describe('TemplateCard', () => {
  it('displays template info')
  it('shows public badge when public')
  it('navigates to detail on click')
})

describe('TravelMap', () => {
  it('highlights visited countries')
  it('shows tooltip on hover')
})

describe('TravelStats', () => {
  it('displays all statistics')
  it('formats numbers correctly')
})
```

---

## IMPLEMENTATION ORDER

### Phase 1: Template Backend (Day 1)
1. [ ] Template CRUD endpoints
2. [ ] Clone functionality
3. [ ] Create trip from template
4. [ ] Public template listing

### Phase 2: Template Frontend (Day 2)
1. [ ] TemplateCard component
2. [ ] TemplateGrid layout
3. [ ] CreateTemplateDialog
4. [ ] Template library page

### Phase 3: History Backend (Day 3)
1. [ ] Travel stats calculation
2. [ ] History endpoints
3. [ ] Archive functionality
4. [ ] Timeline data

### Phase 4: History Frontend (Day 4)
1. [ ] TravelStats component
2. [ ] TravelMap with react-simple-maps
3. [ ] TravelTimeline
4. [ ] History page

### Phase 5: Polish (Day 5)
1. [ ] Featured templates
2. [ ] Filter/search
3. [ ] Mobile responsive
4. [ ] Update feature_list.json

---

## DEPENDENCIES

```json
// Add to frontend/package.json
"react-simple-maps": "^3.0.0"
```

---

## DELIVERABLES

- [ ] Backend: 12+ API endpoints
- [ ] Template library with CRUD
- [ ] Public template browsing
- [ ] Travel history with timeline
- [ ] World map visualization
- [ ] Travel statistics
- [ ] Tests: >80% coverage
- [ ] feature_list.json updated
- [ ] Committed and pushed
