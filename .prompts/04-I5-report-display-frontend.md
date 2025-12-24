# I5: Report Display Frontend

> **Prerequisites**: Read `00-session-context.md` first
> **Depends On**: `03-I5-ai-agents-backend.md` (agents must be working)

## Objective

Build the frontend UI to display AI-generated travel intelligence reports with real-time status updates.

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Report Layout | 0% | Not Started |
| Visa Section | 0% | Not Started |
| Country Section | 0% | Not Started |
| Weather Section | 0% | Not Started |
| Currency Section | 0% | Not Started |
| Culture Section | 0% | Not Started |
| Food Section | 0% | Not Started |
| Attractions Section | 0% | Not Started |
| Itinerary Section | 0% | Not Started |
| Flight Section | 0% | Not Started |
| Generation Status | 0% | Not Started |

---

## DOCUMENTATION REFERENCE

```
product-plan/instructions/incremental/05-visa-entry-intelligence.md
product-plan/instructions/incremental/06-destination-intelligence.md
product-plan/sections/visa-entry-intelligence/
product-plan/sections/destination-intelligence/
```

---

## COMPONENTS TO BUILD

### Report Container

```
frontend/components/report/
├── ReportPage.tsx            # Main report page
├── ReportHeader.tsx          # Trip title, dates, status
├── ReportTabs.tsx            # Section navigation
├── ReportSidebar.tsx         # Quick navigation
├── GenerationStatus.tsx      # Real-time generation progress
├── SectionWrapper.tsx        # Generic section container
└── ReportActions.tsx         # Share, export, print buttons
```

### Report Sections

```
frontend/components/report/sections/
├── VisaSection.tsx           # Visa requirements
├── CountrySection.tsx        # Country overview
├── WeatherSection.tsx        # Weather forecast
├── CurrencySection.tsx       # Currency & budget
├── CultureSection.tsx        # Cultural tips
├── FoodSection.tsx           # Food recommendations
├── AttractionsSection.tsx    # Places to visit
├── ItinerarySection.tsx      # Day-by-day plan
├── FlightSection.tsx         # Flight options
└── SectionSkeleton.tsx       # Loading state for sections
```

### Section Sub-components

```
frontend/components/report/elements/
├── InfoCard.tsx              # Key info display
├── TipsList.tsx              # Tips with icons
├── WarningBanner.tsx         # Important warnings
├── PriceDisplay.tsx          # Currency formatting
├── WeatherCard.tsx           # Daily weather
├── DishCard.tsx              # Food item card
├── AttractionCard.tsx        # Place card
├── DayPlanAccordion.tsx      # Itinerary day
├── FlightCard.tsx            # Flight option
├── SourcesList.tsx           # Data sources
└── ConfidenceBadge.tsx       # AI confidence indicator
```

---

## PAGE STRUCTURE

```
frontend/app/(app)/trips/[id]/
├── page.tsx                  # Report view page
├── loading.tsx               # Loading state
├── error.tsx                 # Error boundary
└── layout.tsx                # Report layout wrapper
```

### Report Page Layout

```tsx
// frontend/app/(app)/trips/[id]/page.tsx

export default async function TripReportPage({ params }: Props) {
  const trip = await getTrip(params.id);

  // If still generating, show status
  if (trip.status === 'processing') {
    return <GenerationStatus tripId={params.id} />;
  }

  // If failed, show error with retry
  if (trip.status === 'failed') {
    return <GenerationError tripId={params.id} error={trip.error} />;
  }

  // Show full report
  return (
    <ReportPage>
      <ReportHeader trip={trip} />
      <ReportTabs defaultTab="overview">
        <Tab id="overview" label="Overview">
          <CountrySection data={trip.report.country} />
          <WeatherSection data={trip.report.weather} />
        </Tab>
        <Tab id="visa" label="Visa & Entry">
          <VisaSection data={trip.report.visa} />
        </Tab>
        <Tab id="culture" label="Culture">
          <CultureSection data={trip.report.culture} />
          <FoodSection data={trip.report.food} />
        </Tab>
        <Tab id="places" label="Places">
          <AttractionsSection data={trip.report.attractions} />
        </Tab>
        <Tab id="itinerary" label="Itinerary">
          <ItinerarySection data={trip.report.itinerary} />
        </Tab>
        <Tab id="flights" label="Flights">
          <FlightSection data={trip.report.flights} />
        </Tab>
        <Tab id="budget" label="Budget">
          <CurrencySection data={trip.report.currency} />
        </Tab>
      </ReportTabs>
      <ReportActions tripId={params.id} />
    </ReportPage>
  );
}
```

---

## REAL-TIME GENERATION STATUS

```tsx
// frontend/components/report/GenerationStatus.tsx

export function GenerationStatus({ tripId }: Props) {
  const [status, setStatus] = useState<GenerationProgress>();

  // Poll for status updates
  useEffect(() => {
    const interval = setInterval(async () => {
      const progress = await getGenerationStatus(tripId);
      setStatus(progress);

      if (progress.status === 'completed' || progress.status === 'failed') {
        clearInterval(interval);
        router.refresh(); // Reload page to show report
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [tripId]);

  return (
    <div class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <Spinner size="lg" />
        <h2>Generating Your Travel Report</h2>
        <p>Our AI agents are researching your destination...</p>

        {/* Agent progress */}
        <div class="space-y-2 mt-8">
          {status?.agents.map(agent => (
            <AgentProgressBar
              key={agent.type}
              name={agent.name}
              status={agent.status}
            />
          ))}
        </div>

        <p class="text-sm text-slate-500 mt-4">
          This usually takes 30-60 seconds
        </p>
      </div>
    </div>
  );
}
```

---

## API INTEGRATION

```typescript
// frontend/lib/api/reports.ts

export interface TripReport {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  generatedAt: string;
  sections: {
    visa: VisaSectionData;
    country: CountrySectionData;
    weather: WeatherSectionData;
    currency: CurrencySectionData;
    culture: CultureSectionData;
    food: FoodSectionData;
    attractions: AttractionsSectionData;
    itinerary: ItinerarySectionData;
    flights: FlightSectionData;
  };
}

export async function getTrip(id: string): Promise<Trip>
export async function getTripReport(id: string): Promise<TripReport>
export async function getGenerationStatus(id: string): Promise<GenerationProgress>
export async function retryGeneration(id: string): Promise<void>
```

---

## SECTION COMPONENT PATTERNS

### Visa Section

```tsx
// frontend/components/report/sections/VisaSection.tsx

export function VisaSection({ data }: { data: VisaSectionData }) {
  return (
    <SectionWrapper title="Visa & Entry Requirements" icon={PassportIcon}>
      {/* Visa Status Badge */}
      <div class="flex items-center gap-3 mb-6">
        {data.visaRequired ? (
          <Badge variant="warning">Visa Required</Badge>
        ) : (
          <Badge variant="success">Visa-Free Entry</Badge>
        )}
        <ConfidenceBadge score={data.confidenceScore} />
      </div>

      {/* Key Info Grid */}
      <div class="grid grid-cols-2 gap-4 mb-6">
        <InfoCard label="Visa Type" value={data.visaType || "N/A"} />
        <InfoCard label="Max Stay" value={`${data.maxStayDays} days`} />
        <InfoCard label="Processing" value={data.processingTime} />
        <InfoCard label="Cost" value={formatCurrency(data.costUsd)} />
      </div>

      {/* Required Documents */}
      <div class="mb-6">
        <h4>Required Documents</h4>
        <ul class="list-disc pl-5 space-y-1">
          {data.requiredDocuments.map(doc => (
            <li key={doc}>{doc}</li>
          ))}
        </ul>
      </div>

      {/* Warnings */}
      {data.warnings.length > 0 && (
        <WarningBanner warnings={data.warnings} />
      )}

      {/* Tips */}
      <TipsList tips={data.tips} />

      {/* Application Link */}
      {data.applicationUrl && (
        <a href={data.applicationUrl} target="_blank" class="btn-primary">
          Start Application
        </a>
      )}

      {/* Sources */}
      <SourcesList sources={data.sources} />
    </SectionWrapper>
  );
}
```

### Weather Section

```tsx
// frontend/components/report/sections/WeatherSection.tsx

export function WeatherSection({ data }: Props) {
  return (
    <SectionWrapper title="Weather Forecast" icon={SunIcon}>
      {/* Summary */}
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-6">
        <p class="text-lg">
          Average temperature: <strong>{data.averageTemp}°C</strong>
        </p>
        <p>Best time to visit: {data.bestTimeToVisit}</p>
      </div>

      {/* Daily Forecast */}
      <div class="grid grid-cols-7 gap-2 mb-6">
        {data.forecast.map(day => (
          <WeatherCard key={day.date} {...day} />
        ))}
      </div>

      {/* Packing Suggestions */}
      <div class="mb-6">
        <h4>Packing Suggestions</h4>
        <div class="flex flex-wrap gap-2">
          {data.packingSuggestions.map(item => (
            <Badge key={item} variant="outline">{item}</Badge>
          ))}
        </div>
      </div>
    </SectionWrapper>
  );
}
```

---

## DESIGN SYSTEM PATTERNS

### Section Container

```html
<section class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 mb-6">
  <div class="flex items-center gap-3 mb-4">
    <Icon class="w-6 h-6 text-blue-600" />
    <h3 class="text-xl font-semibold text-slate-900 dark:text-slate-50">
      Section Title
    </h3>
  </div>
  <!-- Content -->
</section>
```

### Info Card

```html
<div class="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
  <p class="text-sm text-slate-500 dark:text-slate-400">Label</p>
  <p class="text-lg font-medium text-slate-900 dark:text-slate-50">Value</p>
</div>
```

### Warning Banner

```html
<div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
  <div class="flex items-start gap-3">
    <AlertTriangle class="w-5 h-5 text-amber-600 flex-shrink-0" />
    <div>
      <p class="font-medium text-amber-800 dark:text-amber-200">Warning</p>
      <p class="text-sm text-amber-700 dark:text-amber-300">Message</p>
    </div>
  </div>
</div>
```

---

## TDD TEST CASES

```typescript
// frontend/__tests__/components/report/

describe('ReportPage', () => {
  it('shows generation status when processing')
  it('shows error state when failed')
  it('displays all sections when completed')
  it('handles missing section data gracefully')
})

describe('GenerationStatus', () => {
  it('polls for status updates')
  it('shows agent progress')
  it('redirects when complete')
})

describe('VisaSection', () => {
  it('shows visa-free badge when not required')
  it('shows visa-required badge when required')
  it('displays all required documents')
  it('shows warnings prominently')
  it('links to application when available')
})

describe('WeatherSection', () => {
  it('displays 7-day forecast')
  it('shows average temperature')
  it('lists packing suggestions')
})

// ... tests for each section
```

---

## IMPLEMENTATION ORDER

### Phase 1: Core Components (Day 1)
1. [ ] Build SectionWrapper
2. [ ] Build ReportHeader
3. [ ] Build ReportTabs
4. [ ] Build GenerationStatus

### Phase 2: Report Sections (Day 2-3)
1. [ ] VisaSection
2. [ ] CountrySection
3. [ ] WeatherSection
4. [ ] CurrencySection
5. [ ] CultureSection
6. [ ] FoodSection
7. [ ] AttractionsSection
8. [ ] ItinerarySection
9. [ ] FlightSection

### Phase 3: Element Components (Day 3)
1. [ ] InfoCard
2. [ ] TipsList
3. [ ] WarningBanner
4. [ ] WeatherCard
5. [ ] AttractionCard
6. [ ] DayPlanAccordion
7. [ ] FlightCard

### Phase 4: Integration (Day 4)
1. [ ] Connect to backend APIs
2. [ ] Implement polling for status
3. [ ] Test with real data
4. [ ] Error handling

### Phase 5: Polish (Day 5)
1. [ ] Loading skeletons
2. [ ] Dark mode verification
3. [ ] Responsive design
4. [ ] Print styles
5. [ ] Update feature_list.json

---

## DELIVERABLES

- [ ] ReportPage with all sections
- [ ] GenerationStatus with polling
- [ ] 9 section components
- [ ] 10+ element components
- [ ] Tests: >80% coverage
- [ ] Dark mode: All components
- [ ] Responsive: Mobile-first
- [ ] Print-friendly styles
- [ ] feature_list.json updated
- [ ] Committed and pushed
