# I10: Analytics & Settings

> **Prerequisites**: Read `00-session-context.md` first

## Objective

Implement user analytics dashboard and comprehensive application settings.

## Current Status

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Usage Analytics | 0% | 0% | Not Started |
| Trip Analytics | 0% | 0% | Not Started |
| App Settings | 0% | 0% | Not Started |
| Notification Settings | 0% | 0% | Not Started |
| Data Export | 0% | 0% | Not Started |
| Account Management | 80% | 60% | Mostly Done |

---

## BACKEND TASKS

### API Endpoints

```python
# backend/app/api/analytics.py

# Usage analytics
GET  /api/analytics/usage                # Usage summary
GET  /api/analytics/usage/trips          # Trip creation trends
GET  /api/analytics/usage/agents         # Agent usage stats
GET  /api/analytics/usage/time           # Time-based usage

# Trip analytics
GET  /api/analytics/trips/destinations   # Popular destinations
GET  /api/analytics/trips/budgets        # Budget analysis
GET  /api/analytics/trips/duration       # Trip duration trends
GET  /api/analytics/trips/seasons        # Seasonal preferences

# backend/app/api/settings.py

# App settings
GET  /api/settings                       # Get all settings
PUT  /api/settings                       # Update settings
GET  /api/settings/notifications         # Notification prefs
PUT  /api/settings/notifications         # Update notifications
GET  /api/settings/privacy               # Privacy settings
PUT  /api/settings/privacy               # Update privacy
GET  /api/settings/appearance            # Theme settings
PUT  /api/settings/appearance            # Update theme

# Data management
POST /api/settings/data/export           # Request data export
GET  /api/settings/data/export/{id}      # Download export
DELETE /api/settings/data                # Delete all data (GDPR)
```

### Data Models

```python
# backend/app/models/analytics.py

class UsageStats(BaseModel):
    period: str  # week, month, year
    total_trips: int
    trips_created: int
    trips_completed: int
    reports_generated: int
    agents_invoked: dict[str, int]  # agent_type: count
    avg_generation_time: float

class TripAnalytics(BaseModel):
    top_destinations: list[DestinationCount]
    budget_ranges: list[BudgetRange]
    avg_trip_duration: float
    seasonal_distribution: dict[str, int]  # season: count
    purpose_distribution: dict[str, int]   # purpose: count

# backend/app/models/settings.py

class UserSettings(BaseModel):
    user_id: str

    # Appearance
    theme: str = "system"  # light, dark, system
    language: str = "en"
    timezone: str = "UTC"
    date_format: str = "MM/DD/YYYY"
    currency: str = "USD"
    units: str = "metric"

    # Notifications
    email_notifications: bool = True
    email_trip_updates: bool = True
    email_recommendations: bool = False
    email_marketing: bool = False
    push_notifications: bool = False

    # Privacy
    profile_visibility: str = "private"  # private, friends, public
    show_travel_history: bool = False
    allow_template_sharing: bool = True
    analytics_opt_in: bool = True

    # AI preferences
    ai_temperature: float = 0.7  # Creativity level
    preferred_detail_level: str = "balanced"  # brief, balanced, detailed
```

---

## FRONTEND TASKS

### Components to Build

```
frontend/components/analytics/
├── AnalyticsDashboard.tsx    # Main analytics page
├── UsageChart.tsx            # Usage over time
├── TripChart.tsx             # Trip statistics
├── DestinationChart.tsx      # Popular destinations
├── BudgetChart.tsx           # Budget analysis
├── AgentUsageChart.tsx       # Agent invocation stats
├── StatCard.tsx              # Metric card
├── DateRangePicker.tsx       # Analytics date range
└── ExportButton.tsx          # Export analytics

frontend/components/settings/
├── SettingsLayout.tsx        # Settings page layout
├── SettingsSidebar.tsx       # Settings navigation
├── AppearanceSettings.tsx    # Theme, language
├── NotificationSettings.tsx  # Email, push prefs
├── PrivacySettings.tsx       # Privacy controls
├── AISettings.tsx            # AI preferences
├── DataManagement.tsx        # Export, delete
├── SettingsSection.tsx       # Section wrapper
├── SettingsToggle.tsx        # Toggle switch row
└── SettingsSelect.tsx        # Dropdown row
```

### Pages to Build

```
frontend/app/(app)/
├── analytics/
│   ├── page.tsx              # Analytics dashboard
│   └── loading.tsx
└── settings/
    ├── page.tsx              # Settings overview
    ├── appearance/
    │   └── page.tsx          # Appearance settings
    ├── notifications/
    │   └── page.tsx          # Notification settings
    ├── privacy/
    │   └── page.tsx          # Privacy settings
    ├── ai/
    │   └── page.tsx          # AI preferences
    └── data/
        └── page.tsx          # Data management
```

---

## ANALYTICS DASHBOARD UI

```tsx
// frontend/app/(app)/analytics/page.tsx

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange>('month');

  return (
    <div class="space-y-6">
      {/* Header with date picker */}
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold">Analytics</h1>
        <DateRangePicker value={dateRange} onChange={setDateRange} />
      </div>

      {/* Key metrics */}
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Trips Created"
          value={stats.tripsCreated}
          change={stats.tripsChange}
          icon={PlaneIcon}
        />
        <StatCard
          label="Reports Generated"
          value={stats.reportsGenerated}
          change={stats.reportsChange}
          icon={FileTextIcon}
        />
        <StatCard
          label="Countries Planned"
          value={stats.countriesPlanned}
          icon={GlobeIcon}
        />
        <StatCard
          label="Avg. Generation Time"
          value={`${stats.avgGenerationTime}s`}
          icon={ClockIcon}
        />
      </div>

      {/* Charts row */}
      <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800">
          <h3 class="font-semibold mb-4">Trip Activity</h3>
          <UsageChart data={usageData} />
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800">
          <h3 class="font-semibold mb-4">Popular Destinations</h3>
          <DestinationChart data={destinationData} />
        </div>
      </div>

      {/* More charts */}
      <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800">
          <h3 class="font-semibold mb-4">Budget Distribution</h3>
          <BudgetChart data={budgetData} />
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-800">
          <h3 class="font-semibold mb-4">AI Agent Usage</h3>
          <AgentUsageChart data={agentData} />
        </div>
      </div>
    </div>
  );
}
```

---

## SETTINGS UI

```tsx
// frontend/app/(app)/settings/page.tsx

export default function SettingsPage() {
  return (
    <SettingsLayout>
      <SettingsSidebar />

      <div class="flex-1 space-y-6">
        {/* Appearance preview */}
        <SettingsSection title="Quick Settings">
          <SettingsToggle
            label="Dark Mode"
            description="Use dark theme"
            checked={settings.theme === 'dark'}
            onChange={handleThemeToggle}
          />
          <SettingsSelect
            label="Language"
            value={settings.language}
            options={languages}
            onChange={handleLanguageChange}
          />
        </SettingsSection>

        {/* Links to detailed settings */}
        <div class="grid md:grid-cols-2 gap-4">
          <SettingsCard
            title="Appearance"
            description="Theme, language, date format"
            href="/settings/appearance"
            icon={PaletteIcon}
          />
          <SettingsCard
            title="Notifications"
            description="Email and push preferences"
            href="/settings/notifications"
            icon={BellIcon}
          />
          <SettingsCard
            title="Privacy"
            description="Profile visibility and data"
            href="/settings/privacy"
            icon={ShieldIcon}
          />
          <SettingsCard
            title="AI Preferences"
            description="Customize AI behavior"
            href="/settings/ai"
            icon={SparklesIcon}
          />
        </div>

        {/* Danger zone */}
        <SettingsSection title="Data Management" variant="danger">
          <Button variant="outline" onClick={handleExportData}>
            <Download class="w-4 h-4 mr-2" />
            Export My Data
          </Button>
          <Button variant="destructive" onClick={handleDeleteData}>
            <Trash2 class="w-4 h-4 mr-2" />
            Delete All Data
          </Button>
        </SettingsSection>
      </div>
    </SettingsLayout>
  );
}
```

### Settings Toggle Component

```tsx
// frontend/components/settings/SettingsToggle.tsx

export function SettingsToggle({ label, description, checked, onChange }: Props) {
  return (
    <div class="flex items-center justify-between py-3 border-b border-slate-100 dark:border-slate-800 last:border-0">
      <div>
        <p class="font-medium text-slate-900 dark:text-slate-50">{label}</p>
        {description && (
          <p class="text-sm text-slate-500">{description}</p>
        )}
      </div>
      <Switch checked={checked} onCheckedChange={onChange} />
    </div>
  );
}
```

---

## CHARTS IMPLEMENTATION

```tsx
// Using recharts library

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function UsageChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis dataKey="date" stroke="#94A3B8" />
        <YAxis stroke="#94A3B8" />
        <Tooltip
          contentStyle={{
            backgroundColor: 'var(--slate-900)',
            border: 'none',
            borderRadius: '8px',
          }}
        />
        <Line
          type="monotone"
          dataKey="trips"
          stroke="#3B82F6"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

---

## TDD TEST CASES

### Backend Tests

```python
def test_usage_analytics():
    """Should return accurate usage stats"""

def test_analytics_date_range():
    """Should filter by date range"""

def test_update_settings():
    """Should persist settings changes"""

def test_data_export():
    """Should generate export file"""

def test_data_deletion():
    """Should delete all user data (GDPR)"""
```

### Frontend Tests

```typescript
describe('AnalyticsDashboard', () => {
  it('displays key metrics')
  it('updates on date range change')
  it('handles loading state')
})

describe('SettingsToggle', () => {
  it('reflects current value')
  it('calls onChange on toggle')
})

describe('DataManagement', () => {
  it('exports data on click')
  it('confirms before deletion')
})
```

---

## IMPLEMENTATION ORDER

### Phase 1: Analytics Backend (Day 1)
1. [ ] Usage analytics endpoints
2. [ ] Trip analytics endpoints
3. [ ] Aggregation queries
4. [ ] Date range filtering

### Phase 2: Analytics Frontend (Day 2)
1. [ ] StatCard component
2. [ ] Chart components (recharts)
3. [ ] AnalyticsDashboard page
4. [ ] DateRangePicker

### Phase 3: Settings Backend (Day 3)
1. [ ] Settings CRUD endpoints
2. [ ] Data export job
3. [ ] Data deletion (GDPR)
4. [ ] Settings validation

### Phase 4: Settings Frontend (Day 4)
1. [ ] SettingsLayout
2. [ ] Individual settings pages
3. [ ] Toggle/Select components
4. [ ] Data management UI

### Phase 5: Polish (Day 5)
1. [ ] Chart animations
2. [ ] Export progress
3. [ ] Mobile responsive
4. [ ] Update feature_list.json

---

## DEPENDENCIES

```json
// Add to frontend/package.json
"recharts": "^2.12.0"
```

---

## DELIVERABLES

- [ ] Backend: 15+ API endpoints
- [ ] Analytics dashboard with charts
- [ ] All settings pages
- [ ] Data export functionality
- [ ] GDPR data deletion
- [ ] Tests: >80% coverage
- [ ] Dark mode: All components
- [ ] feature_list.json updated
- [ ] Committed and pushed
