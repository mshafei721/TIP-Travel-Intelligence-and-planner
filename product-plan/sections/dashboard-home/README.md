# Dashboard & Home - Implementation Guide

## Section Status: 🟡 IN PROGRESS

**Current Phase:** Batch 2 - Frontend Components (Partial)

---

## ✅ Completed (Batch 1 - Backend)

### Backend API Endpoints
- ✅ **Feature Flags** - `FEATURE_DASHBOARD_HOME`, `FEATURE_RECOMMENDATIONS`, `FEATURE_ANALYTICS`
- ✅ **Authentication** - JWT verification utility (`backend/app/core/auth.py`)
- ✅ **Supabase Client** - Backend database client (`backend/app/core/supabase.py`)
- ✅ **GET /api/trips** - List trips endpoint with pagination
- ✅ **GET /api/trips/{id}** - Get single trip details
- ✅ **GET /api/profile** - Get user profile data
- ✅ **GET /api/profile/statistics** - Aggregated travel statistics
- ✅ **GET /api/recommendations** - Algorithm-based destination recommendations
- ✅ **Recommendations Service** - 10 popular destinations with filtering logic

**Commit:** `0959498` - Backend infrastructure complete

---

## ✅ Completed (Batch 2 - Frontend Partial)

### Frontend Utilities
- ✅ **Feature Flags** - `frontend/lib/config/features.ts`
- ✅ **API Client** - `frontend/lib/api/client.ts` (wrapper around fetch)
- ✅ **Analytics** - `frontend/lib/analytics/index.ts` (event tracking)

### Base Components
- ✅ **TripCard** - `frontend/components/dashboard/TripCard.tsx`
  - Displays trip destination, dates, status
  - Optional countdown timer
  - Click handler with analytics
  - Dark mode support

- ✅ **EmptyState** - `frontend/components/dashboard/EmptyState.tsx`
  - Welcome message for new users
  - Feature highlights
  - CTA button with analytics tracking
  - Responsive grid layout

### Test Specifications
- ✅ **tests.md** - 120+ test cases across 13 suites
- ✅ **types.ts** - TypeScript interfaces for all dashboard data
- ✅ **sample-data.json** - Mock data for development/testing

---

## 🚧 Remaining Work (Batch 2 Continuation)

### Components to Create

1. **Skeleton Components** (`frontend/components/dashboard/skeletons/`)
   - `CardSkeleton.tsx` - Generic card skeleton with shimmer animation
   - `TripCardSkeleton.tsx` - Trip card specific skeleton
   - `StatsSkeleton.tsx` - Statistics summary skeleton

2. **QuickActionsCard** (`frontend/components/dashboard/QuickActionsCard.tsx`)
   - Create New Trip button (primary blue styling)
   - View All Trips button
   - Use Template button (opens modal)
   - Analytics tracking for all CTAs

3. **StatisticsSummaryCard** (`frontend/components/dashboard/StatisticsSummaryCard.tsx`)
   - Display 4 metrics: totalTrips, countriesVisited, destinationsExplored, activeTrips
   - Icons for each metric
   - Loading skeleton state
   - Error state

4. **RecentTripsCard** (`frontend/components/dashboard/RecentTripsCard.tsx`)
   - Display up to 5 recent trips using TripCard component
   - "View All" link to /trips
   - Loading skeleton
   - Error boundary
   - Empty state message

5. **UpcomingTripsCard** (`frontend/components/dashboard/UpcomingTripsCard.tsx`)
   - Display future trips using TripCard with countdown
   - Filter by `departureDate >= today AND status IN ('draft', 'pending', 'processing')`
   - "No upcoming trips planned" empty state
   - Loading skeleton

6. **RecommendationsCard** (`frontend/components/dashboard/RecommendationsCard.tsx`)
   - Display up to 3 recommendations
   - Destination image, name, reason, tags
   - Click to pre-fill trip creation
   - Hide entirely if no recommendations (feature flag OFF or empty array)
   - Loading skeleton

7. **DashboardLayout** (`frontend/components/dashboard/DashboardLayout.tsx`)
   - Responsive grid: 2 columns desktop, 1 column mobile
   - Card arrangement:
     ```
     [ Quick Actions ]    [ Statistics Summary ]
     [ Recent Trips  ]    [ Upcoming Trips     ]
     [ Recommendations (full width)           ]
     ```

8. **Template Modal** (`frontend/components/dashboard/TemplateModal.tsx`)
   - Opens when "Use Template" is clicked
   - Lists available templates
   - Select template → navigate to /trips/create with template ID

---

## Dashboard Page Implementation

**File:** `frontend/app/(app)/dashboard/page.tsx`

### Requirements

1. **Feature Flag Check**
   - If `features.dashboardHome === false`, return `notFound()` (404)

2. **Authentication**
   - Protected by middleware (already implemented in Section 02)
   - Get session using `createServerClient()` from `@/lib/supabase/server`

3. **Data Fetching (Server Components)**
   - Fetch from FastAPI backend using `ApiClient`
   - Get access token from session
   - Parallel data fetching:
     - `GET /api/trips?limit=5&sort=createdAt:desc` (recent trips)
     - `GET /api/trips?filter=departureDate>=today` (upcoming trips)
     - `GET /api/profile/statistics` (stats)
     - `GET /api/recommendations?limit=3` (recommendations)

4. **Loading States**
   - Use `loading.tsx` with skeleton components
   - Suspense boundaries around each card
   - Independent loading (don't block entire page)

5. **Error Handling**
   - Per-card error boundaries
   - Retry buttons on failed data fetches
   - Graceful degradation (show partial dashboard if some APIs fail)

6. **Analytics**
   - Track page view on mount
   - Track all CTA clicks
   - Track trip card interactions

7. **Client Interactions**
   - Navigation handlers for CTAs
   - Modal state management for templates
   - Route navigation using Next.js router

---

## Files Structure

```
frontend/
├── app/(app)/dashboard/
│   ├── page.tsx (Server Component - main dashboard)
│   ├── loading.tsx (Loading state with skeletons)
│   └── error.tsx (Error boundary)
├── components/dashboard/
│   ├── TripCard.tsx ✅
│   ├── EmptyState.tsx ✅
│   ├── QuickActionsCard.tsx ⏳
│   ├── StatisticsSummaryCard.tsx ⏳
│   ├── RecentTripsCard.tsx ⏳
│   ├── UpcomingTripsCard.tsx ⏳
│   ├── RecommendationsCard.tsx ⏳
│   ├── DashboardLayout.tsx ⏳
│   ├── TemplateModal.tsx ⏳
│   └── skeletons/
│       ├── CardSkeleton.tsx ⏳
│       ├── TripCardSkeleton.tsx ⏳
│       └── StatsSkeleton.tsx ⏳
├── lib/
│   ├── config/
│   │   └── features.ts ✅
│   ├── api/
│   │   └── client.ts ✅
│   └── analytics/
│       └── index.ts ✅
└── types/
    └── dashboard.ts (Import from contracts/types.ts)

backend/
├── app/
│   ├── core/
│   │   ├── config.py ✅ (feature flags)
│   │   ├── auth.py ✅ (JWT verification)
│   │   └── supabase.py ✅ (client)
│   ├── api/
│   │   ├── trips.py ✅
│   │   ├── profile.py ✅
│   │   └── recommendations.py ✅
│   └── services/
│       └── recommendations.py ✅

product-plan/sections/dashboard-home/
├── README.md (this file) ✅
├── tests.md ✅ (120+ test cases)
├── types.ts ✅ (TypeScript interfaces)
└── sample-data.json ✅ (mock data)
```

---

## Acceptance Criteria (from tests.md)

### Must-Pass Criteria

- [x] `flag.disabled` - Returns 404 when feature flag OFF
- [x] `flag.enabled` - Renders dashboard when feature flag ON
- [x] `access.protected` - Redirects to /login if not authenticated
- [x] `access.authenticated` - Renders dashboard when authenticated
- [x] `empty.noTrips` - Shows EmptyState for users with no trips
- [x] `empty.ctaClick` - Navigate to /trips/create on CTA click
- [ ] `recent.display` - Display up to 5 recent trips
- [ ] `recent.tripData` - Trip cards show destination, dates, status
- [ ] `recent.navigation` - Trip card click navigates to trip details
- [ ] `upcoming.filter` - Show only future trips with active statuses
- [ ] `upcoming.countdown` - Display static countdown (X days until departure)
- [ ] `upcoming.empty` - Show "No upcoming trips planned" when empty
- [ ] `actions.createClick` - Create Trip button navigates to /trips/create
- [ ] `actions.templateModal` - Use Template opens modal
- [ ] `stats.metrics` - Display all 4 statistics metrics
- [ ] `stats.zeroState` - Display zeros for new users
- [ ] `recommendations.display` - Display up to 3 recommendations
- [ ] `recommendations.hidden` - Hide card when no recommendations
- [ ] `loading.skeleton` - Show skeleton screens during loading
- [ ] `loading.independent` - Cards load independently
- [ ] `error.boundaries` - Per-card error handling
- [ ] `layout.desktop` - 2-column grid on desktop
- [ ] `layout.mobile` - Single column on mobile
- [ ] `analytics.pageView` - Track dashboard page views
- [ ] `analytics.ctaClick` - Track CTA clicks

**Progress:** 6/24 must-pass criteria implemented (25%)

---

## Next Steps

1. Complete remaining dashboard card components
2. Implement dashboard page with server-side data fetching
3. Add loading and error states
4. Test all components against test specifications
5. Update `claude-progress.txt` and `features_list.json`
6. Commit Batch 2 completion
7. Update INTEGRATED_PLAN.md with section status

---

## API Endpoint Usage

### List Recent Trips
```typescript
const response = await apiClient.get<TripListResponse>('/trips?limit=5&sort=createdAt:desc')
// response.items: TripListItem[]
```

### List Upcoming Trips
```typescript
const today = new Date().toISOString().split('T')[0]
const response = await apiClient.get<TripListResponse>(`/trips?filter=departureDate>=${today}`)
// response.items: TripListItem[] (filtered by status in component)
```

### Get Statistics
```typescript
const response = await apiClient.get<StatisticsResponse>('/profile/statistics')
// response.statistics: { totalTrips, countriesVisited, destinationsExplored, activeTrips }
```

### Get Recommendations
```typescript
const response = await apiClient.get<RecommendationsResponse>('/recommendations?limit=3')
// response.recommendations: Recommendation[]
```

---

## Testing Strategy

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test data fetching and API interactions
3. **E2E Tests** - Test complete user flows (empty state → create trip)
4. **Visual Tests** - Test responsive layout and dark mode

**Test Framework:** Jest + React Testing Library
**Coverage Target:** ≥90%

---

## Feature Flag Control

### Enable Dashboard
```env
NEXT_PUBLIC_FEATURE_DASHBOARD_HOME=true
FEATURE_DASHBOARD_HOME=true
```

### Disable Recommendations
```env
NEXT_PUBLIC_FEATURE_RECOMMENDATIONS=false
FEATURE_RECOMMENDATIONS=false
```

### Disable Analytics
```env
NEXT_PUBLIC_FEATURE_ANALYTICS=false
FEATURE_ANALYTICS=false
```

---

## Deployment Checklist

- [ ] All components implemented
- [ ] Tests passing (≥90% coverage)
- [ ] Feature flags tested (ON and OFF states)
- [ ] Protected routes verified
- [ ] Loading states smooth
- [ ] Error boundaries working
- [ ] Analytics events firing
- [ ] Dark mode supported
- [ ] Mobile responsive
- [ ] Backend APIs deployed
- [ ] Environment variables configured

---

**Last Updated:** 2025-12-24
**Section Owner:** Core Team
**Status:** 🟡 In Progress (Batch 2 Partial)
