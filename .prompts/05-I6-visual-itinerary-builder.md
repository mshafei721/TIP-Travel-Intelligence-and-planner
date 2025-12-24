# I6: Visual Itinerary Builder

> **Prerequisites**: Read `00-session-context.md` first

## Objective

Build an interactive visual itinerary builder with drag-and-drop, map integration, and real-time updates.

## Current Status

| Component | Frontend | Backend | Status |
|-----------|----------|---------|--------|
| Itinerary Editor | 0% | 0% | Not Started |
| Day Timeline | 0% | - | Not Started |
| Activity Cards | 0% | - | Not Started |
| Map Integration | 0% | 0% | Not Started |
| Drag & Drop | 0% | - | Not Started |
| Time Slots | 0% | - | Not Started |

---

## DOCUMENTATION REFERENCE

```
product-plan/instructions/incremental/07-travel-planning-itinerary.md
product-plan/sections/travel-planning-itinerary/
```

---

## BACKEND TASKS

### API Endpoints

```python
# backend/app/api/itinerary.py

GET  /api/trips/{id}/itinerary          # Get itinerary
PUT  /api/trips/{id}/itinerary          # Update full itinerary
POST /api/trips/{id}/itinerary/days     # Add day
DELETE /api/trips/{id}/itinerary/days/{day_id}  # Remove day
POST /api/trips/{id}/itinerary/days/{day_id}/activities  # Add activity
PUT  /api/trips/{id}/itinerary/activities/{activity_id}  # Update activity
DELETE /api/trips/{id}/itinerary/activities/{activity_id}  # Remove activity
POST /api/trips/{id}/itinerary/reorder  # Reorder activities
GET  /api/places/search                 # Search places for adding
```

### Data Models

```python
# backend/app/models/itinerary.py

class Activity(BaseModel):
    id: str
    name: str
    type: str  # attraction, restaurant, transport, accommodation
    location: Location
    start_time: time
    end_time: time
    duration_minutes: int
    cost_estimate: float | None
    notes: str | None
    booking_url: str | None
    booking_status: str | None  # none, pending, confirmed

class DayPlan(BaseModel):
    id: str
    date: date
    day_number: int
    title: str
    activities: list[Activity]
    total_cost: float
    notes: str | None

class Itinerary(BaseModel):
    trip_id: str
    days: list[DayPlan]
    total_cost: float
    last_modified: datetime
```

---

## FRONTEND TASKS

### Components to Build

```
frontend/components/itinerary/
├── ItineraryBuilder.tsx       # Main builder page
├── ItineraryContext.tsx       # State management
├── DayColumn.tsx              # Single day column
├── DayHeader.tsx              # Day date and title
├── ActivityCard.tsx           # Draggable activity
├── ActivityForm.tsx           # Add/edit activity modal
├── TimeSlot.tsx               # Time slot indicator
├── Timeline.tsx               # Vertical timeline
├── DragDropContext.tsx        # DnD provider
├── MapSidebar.tsx             # Map with markers
├── PlaceSearch.tsx            # Search places to add
├── CostSummary.tsx            # Total cost display
├── ItineraryActions.tsx       # Export, share buttons
└── EmptyDay.tsx               # Empty state for day
```

### Page Structure

```
frontend/app/(app)/trips/[id]/itinerary/
├── page.tsx                   # Itinerary builder page
├── loading.tsx
└── error.tsx
```

---

## DRAG AND DROP IMPLEMENTATION

```tsx
// Using @dnd-kit/core

import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';

export function ItineraryBuilder({ itinerary }: Props) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (active.id !== over?.id) {
      // Reorder activities
      const reordered = arrayMove(activities, oldIndex, newIndex);
      await updateItinerary(reordered);
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <div class="flex gap-4 overflow-x-auto p-4">
        {itinerary.days.map(day => (
          <DayColumn key={day.id} day={day} />
        ))}
      </div>
    </DndContext>
  );
}
```

---

## MAP INTEGRATION

```tsx
// Using Mapbox GL

import mapboxgl from 'mapbox-gl';

export function MapSidebar({ activities }: Props) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<mapboxgl.Map>();

  useEffect(() => {
    if (!mapContainer.current) return;

    const mapInstance = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [activities[0]?.location.lng, activities[0]?.location.lat],
      zoom: 12,
    });

    // Add markers for each activity
    activities.forEach((activity, index) => {
      new mapboxgl.Marker({ color: '#3B82F6' })
        .setLngLat([activity.location.lng, activity.location.lat])
        .setPopup(new mapboxgl.Popup().setHTML(`
          <strong>${index + 1}. ${activity.name}</strong>
          <p>${activity.start_time} - ${activity.end_time}</p>
        `))
        .addTo(mapInstance);
    });

    // Draw route line between activities
    if (activities.length > 1) {
      mapInstance.addSource('route', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: activities.map(a => [a.location.lng, a.location.lat]),
          },
        },
      });
      // Add line layer
    }

    setMap(mapInstance);
  }, [activities]);

  return (
    <div class="w-96 h-full">
      <div ref={mapContainer} class="h-full rounded-lg" />
    </div>
  );
}
```

---

## COMPONENT PATTERNS

### Day Column

```tsx
export function DayColumn({ day }: { day: DayPlan }) {
  return (
    <div class="flex-shrink-0 w-80 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
      <DayHeader day={day} />

      <SortableContext items={day.activities} strategy={verticalListSortingStrategy}>
        <div class="p-4 space-y-3 min-h-[400px]">
          {day.activities.length === 0 ? (
            <EmptyDay onAddActivity={() => openActivityForm(day.id)} />
          ) : (
            day.activities.map((activity, index) => (
              <ActivityCard
                key={activity.id}
                activity={activity}
                index={index}
              />
            ))
          )}
        </div>
      </SortableContext>

      <div class="p-4 border-t border-slate-200 dark:border-slate-800">
        <button onClick={() => openActivityForm(day.id)} class="btn-outline w-full">
          + Add Activity
        </button>
      </div>
    </div>
  );
}
```

### Activity Card

```tsx
export function ActivityCard({ activity, index }: Props) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: activity.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      class="bg-slate-50 dark:bg-slate-800 rounded-lg p-3 cursor-grab active:cursor-grabbing"
    >
      <div class="flex items-start gap-3">
        <div class="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs">
          {index + 1}
        </div>
        <div class="flex-1">
          <p class="font-medium text-slate-900 dark:text-slate-50">
            {activity.name}
          </p>
          <p class="text-sm text-slate-500">
            {activity.start_time} - {activity.end_time}
          </p>
          {activity.cost_estimate && (
            <p class="text-sm text-slate-500">
              {formatCurrency(activity.cost_estimate)}
            </p>
          )}
        </div>
        <ActivityTypeIcon type={activity.type} />
      </div>
    </div>
  );
}
```

---

## TDD TEST CASES

```typescript
// frontend/__tests__/components/itinerary/

describe('ItineraryBuilder', () => {
  it('renders all days')
  it('allows drag and drop between days')
  it('updates order on drop')
  it('saves changes to API')
})

describe('DayColumn', () => {
  it('shows activities in order')
  it('shows empty state when no activities')
  it('allows adding new activity')
})

describe('ActivityCard', () => {
  it('displays activity details')
  it('is draggable')
  it('opens edit modal on click')
})

describe('MapSidebar', () => {
  it('shows markers for all activities')
  it('draws route line')
  it('centers on activities')
})
```

---

## IMPLEMENTATION ORDER

### Phase 1: Backend APIs (Day 1)
1. [ ] Create itinerary endpoints
2. [ ] Implement reorder logic
3. [ ] Add place search endpoint
4. [ ] Write API tests

### Phase 2: Core Components (Day 2)
1. [ ] Build ItineraryBuilder container
2. [ ] Build DayColumn
3. [ ] Build ActivityCard
4. [ ] Implement drag-and-drop

### Phase 3: Activity Management (Day 3)
1. [ ] Build ActivityForm modal
2. [ ] Build PlaceSearch
3. [ ] Implement add/edit/delete
4. [ ] Connect to backend

### Phase 4: Map Integration (Day 4)
1. [ ] Set up Mapbox
2. [ ] Build MapSidebar
3. [ ] Add activity markers
4. [ ] Draw route lines

### Phase 5: Polish (Day 5)
1. [ ] CostSummary component
2. [ ] Export functionality
3. [ ] Mobile responsive
4. [ ] Update feature_list.json

---

## DEPENDENCIES

```json
// Add to frontend/package.json
"@dnd-kit/core": "^6.1.0",
"@dnd-kit/sortable": "^8.0.0",
"mapbox-gl": "^3.3.0"
```

---

## DELIVERABLES

- [ ] Backend: 8 API endpoints
- [ ] Frontend: Drag-and-drop itinerary
- [ ] Map: Mapbox integration with markers
- [ ] Activity CRUD: Add, edit, delete, reorder
- [ ] Tests: >80% coverage
- [ ] Dark mode: All components
- [ ] Responsive: Tablet and mobile views
- [ ] feature_list.json updated
- [ ] Committed and pushed
