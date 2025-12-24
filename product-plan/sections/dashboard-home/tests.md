# Dashboard & Home - Test Specifications

## Test Strategy

All tests follow **RED → GREEN → REFACTOR** workflow:
1. Write failing test first
2. Implement minimum code to pass
3. Refactor while keeping tests green

**Coverage Target:** ≥90% for all dashboard components

---

## Test Suite 1: Feature Flag Behavior

### Test 1.1: Feature Flag OFF - Returns 404
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "flag.disabled")

```typescript
describe('Dashboard Feature Flag', () => {
  it('should return 404 when features.dashboardHome is OFF', async () => {
    // Given feature flag is disabled
    process.env.FEATURE_DASHBOARD_HOME = 'false'

    // When user navigates to /dashboard
    const response = await fetch('/dashboard')

    // Then should return 404
    expect(response.status).toBe(404)
  })
})
```

### Test 1.2: Feature Flag ON - Renders Dashboard
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "flag.enabled")

```typescript
it('should render dashboard when features.dashboardHome is ON', async () => {
  // Given feature flag is enabled
  process.env.FEATURE_DASHBOARD_HOME = 'true'

  // When user navigates to /dashboard
  const { getByTestId } = render(<DashboardPage />)

  // Then should render dashboard layout
  expect(getByTestId('dashboard-layout')).toBeInTheDocument()
})
```

---

## Test Suite 2: Protected Route Access

### Test 2.1: Unauthenticated User - Redirects to Login
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "access.protected")

```typescript
describe('Dashboard Authentication', () => {
  it('should redirect to /login when user is not authenticated', async () => {
    // Given no active session
    mockSupabaseAuth.getSession.mockResolvedValue({ data: { session: null } })

    // When user tries to access /dashboard
    const response = await fetch('/dashboard')

    // Then should redirect to /login
    expect(response.status).toBe(307)
    expect(response.headers.get('location')).toBe('/login')
  })
})
```

### Test 2.2: Authenticated User - Renders Dashboard
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "access.authenticated")

```typescript
it('should render dashboard when user is authenticated', async () => {
  // Given active session exists
  mockSupabaseAuth.getSession.mockResolvedValue({
    data: { session: { user: { id: 'user-123' } } }
  })

  // When user accesses /dashboard
  render(<DashboardPage />)

  // Then should render without redirect
  expect(screen.getByTestId('dashboard-layout')).toBeInTheDocument()
})
```

---

## Test Suite 3: Empty State - New Users

### Test 3.1: Zero Trips - Shows EmptyState
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "empty.noTrips")

```typescript
describe('EmptyState Component', () => {
  it('should display empty state when user has no trips', async () => {
    // Given user has zero trips
    mockApiResponse('/trips', { items: [], nextCursor: null })

    // When dashboard loads
    const { getByText, getByRole } = render(<DashboardPage />)

    // Then should show welcome message
    expect(getByText(/Welcome to TIP/i)).toBeInTheDocument()
    expect(getByText(/Start planning your next adventure/i)).toBeInTheDocument()

    // And show prominent CTA button
    const ctaButton = getByRole('button', { name: /Create Your First Trip/i })
    expect(ctaButton).toHaveClass('bg-blue-600') // Primary blue styling
  })
})
```

### Test 3.2: Empty State CTA - Navigates to Trip Creation
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "empty.ctaClick")

```typescript
it('should navigate to /trips/create when CTA is clicked', async () => {
  // Given empty state is displayed
  mockApiResponse('/trips', { items: [] })
  const { getByRole } = render(<DashboardPage />)

  // When user clicks "Create Your First Trip"
  const ctaButton = getByRole('button', { name: /Create Your First Trip/i })
  fireEvent.click(ctaButton)

  // Then should navigate to trip creation
  expect(mockRouter.push).toHaveBeenCalledWith('/trips/create')
})
```

---

## Test Suite 4: Recent Trips Card

### Test 4.1: Displays Up to 5 Recent Trips
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "recent.display")

```typescript
describe('RecentTripsCard', () => {
  it('should display up to 5 most recent trips', async () => {
    // Given user has 10 trips
    const trips = generateMockTrips(10)
    mockApiResponse('/trips?limit=5&sort=createdAt:desc', { items: trips.slice(0, 5) })

    // When card renders
    const { getAllByTestId } = render(<RecentTripsCard />)

    // Then should show exactly 5 trip cards
    const tripCards = getAllByTestId('trip-card')
    expect(tripCards).toHaveLength(5)
  })
})
```

### Test 4.2: Trip Card Shows Correct Data
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "recent.tripData")

```typescript
it('should display trip destination, dates, and status', () => {
  // Given a completed trip
  const trip = {
    id: 'trip-1',
    destination: 'Tokyo, Japan',
    startDate: '2024-03-15',
    endDate: '2024-03-22',
    status: 'completed'
  }

  // When trip card renders
  const { getByText } = render(<TripCard trip={trip} />)

  // Then should show all details
  expect(getByText('Tokyo, Japan')).toBeInTheDocument()
  expect(getByText(/Mar 15.*22, 2024/i)).toBeInTheDocument()
  expect(getByText('Completed')).toBeInTheDocument()
})
```

### Test 4.3: Trip Card Click - Navigates to Trip Details
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "recent.navigation")

```typescript
it('should navigate to trip details on card click', () => {
  // Given a trip card
  const trip = { id: 'trip-123', destination: 'Paris, France' }
  const { getByTestId } = render(<TripCard trip={trip} onClick={mockOnClick} />)

  // When user clicks the card
  const card = getByTestId('trip-card')
  fireEvent.click(card)

  // Then should call onClick with trip ID
  expect(mockOnClick).toHaveBeenCalledWith('trip-123')
})
```

### Test 4.4: View All Link - Navigates to Trips Page
**Type:** Integration
**Priority:** Should-pass (acceptance.id: "recent.viewAll")

```typescript
it('should navigate to /trips when "View All" is clicked', () => {
  // Given recent trips card is displayed
  const { getByRole } = render(<RecentTripsCard />)

  // When user clicks "View All Trips"
  const viewAllLink = getByRole('link', { name: /View All/i })
  fireEvent.click(viewAllLink)

  // Then should navigate to trips list
  expect(viewAllLink).toHaveAttribute('href', '/trips')
})
```

---

## Test Suite 5: Upcoming Trips Card

### Test 5.1: Filters Future Trips Only
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "upcoming.filter")

```typescript
describe('UpcomingTripsCard', () => {
  it('should display only future trips with active statuses', async () => {
    // Given trips with mixed dates and statuses
    const today = new Date().toISOString().split('T')[0]
    mockApiResponse('/trips?filter=departureDate>=' + today, {
      items: [
        { id: '1', departureDate: '2025-06-01', status: 'draft' },
        { id: '2', departureDate: '2025-07-15', status: 'pending' }
      ]
    })

    // When card renders
    const { getAllByTestId } = render(<UpcomingTripsCard />)

    // Then should show only future trips
    expect(getAllByTestId('trip-card')).toHaveLength(2)
  })
})
```

### Test 5.2: Countdown Display - Static Format
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "upcoming.countdown")

```typescript
it('should display static countdown text (X days until departure)', () => {
  // Given a trip departing in 45 days
  const futureDate = new Date()
  futureDate.setDate(futureDate.getDate() + 45)
  const trip = {
    id: '1',
    departureDate: futureDate.toISOString().split('T')[0]
  }

  // When trip card renders
  const { getByText } = render(<TripCard trip={trip} showCountdown />)

  // Then should show days until departure
  expect(getByText('45 days until departure')).toBeInTheDocument()
})
```

### Test 5.3: No Upcoming Trips - Shows Empty Message
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "upcoming.empty")

```typescript
it('should show empty message when no upcoming trips exist', async () => {
  // Given user has no upcoming trips
  mockApiResponse('/trips?filter=departureDate>=*', { items: [] })

  // When card renders
  const { getByText } = render(<UpcomingTripsCard />)

  // Then should show empty state message
  expect(getByText('No upcoming trips planned')).toBeInTheDocument()
})
```

---

## Test Suite 6: Quick Actions Card

### Test 6.1: Create Trip Button - Primary Styling
**Type:** Visual
**Priority:** Should-pass (acceptance.id: "actions.createStyling")

```typescript
describe('QuickActionsCard', () => {
  it('should style Create New Trip button as primary (blue)', () => {
    // Given quick actions card
    const { getByRole } = render(<QuickActionsCard />)

    // When rendered
    const createButton = getByRole('button', { name: /Create New Trip/i })

    // Then should have blue primary styling
    expect(createButton).toHaveClass('bg-blue-600')
  })
})
```

### Test 6.2: Create Trip Click - Navigates
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "actions.createClick")

```typescript
it('should navigate to /trips/create when Create New Trip is clicked', () => {
  // Given quick actions card
  const { getByRole } = render(<QuickActionsCard />)

  // When user clicks Create New Trip
  const button = getByRole('button', { name: /Create New Trip/i })
  fireEvent.click(button)

  // Then should navigate to trip creation wizard
  expect(mockRouter.push).toHaveBeenCalledWith('/trips/create')
})
```

### Test 6.3: Use Template Click - Opens Modal
**Type:** Integration
**Priority:** Should-pass (acceptance.id: "actions.templateModal")

```typescript
it('should open template selection modal when Use Template is clicked', async () => {
  // Given quick actions card
  const { getByRole, findByRole } = render(<QuickActionsCard />)

  // When user clicks Use Template
  const button = getByRole('button', { name: /Use Template/i })
  fireEvent.click(button)

  // Then should open modal
  const modal = await findByRole('dialog')
  expect(modal).toBeInTheDocument()
  expect(getByRole('heading', { name: /Select Template/i })).toBeInTheDocument()
})
```

### Test 6.4: View All Trips - Navigates
**Type:** Integration
**Priority:** Should-pass (acceptance.id: "actions.viewAll")

```typescript
it('should navigate to /trips when View All Trips is clicked', () => {
  // Given quick actions card
  const { getByRole } = render(<QuickActionsCard />)

  // When user clicks View All Trips
  const button = getByRole('button', { name: /View All Trips/i })
  fireEvent.click(button)

  // Then should navigate to trips page
  expect(mockRouter.push).toHaveBeenCalledWith('/trips')
})
```

---

## Test Suite 7: Statistics Summary Card

### Test 7.1: Displays Four Metrics
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "stats.metrics")

```typescript
describe('StatisticsSummaryCard', () => {
  it('should display all four statistics metrics', async () => {
    // Given statistics data
    const stats = {
      totalTrips: 15,
      countriesVisited: 8,
      destinationsExplored: 12,
      activeTrips: 2
    }
    mockApiResponse('/profile/statistics', stats)

    // When card renders
    const { getByText } = render(<StatisticsSummaryCard />)

    // Then should show all metrics
    expect(getByText('15')).toBeInTheDocument() // Total trips
    expect(getByText('8')).toBeInTheDocument()  // Countries
    expect(getByText('12')).toBeInTheDocument() // Destinations
    expect(getByText('2')).toBeInTheDocument()  // Active trips
  })
})
```

### Test 7.2: Zero State - Shows Zeros
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "stats.zeroState")

```typescript
it('should display zeros for new users', async () => {
  // Given new user with no trips
  const stats = {
    totalTrips: 0,
    countriesVisited: 0,
    destinationsExplored: 0,
    activeTrips: 0
  }
  mockApiResponse('/profile/statistics', stats)

  // When card renders
  const { getAllByText } = render(<StatisticsSummaryCard />)

  // Then should show all zeros
  const zeros = getAllByText('0')
  expect(zeros.length).toBeGreaterThanOrEqual(4)
})
```

### Test 7.3: Icons Display Correctly
**Type:** Visual
**Priority:** Should-pass (acceptance.id: "stats.icons")

```typescript
it('should display appropriate icon for each metric', () => {
  // Given statistics card
  const { getByTestId } = render(<StatisticsSummaryCard />)

  // Then should have icons
  expect(getByTestId('icon-total-trips')).toBeInTheDocument()
  expect(getByTestId('icon-countries')).toBeInTheDocument()
  expect(getByTestId('icon-destinations')).toBeInTheDocument()
  expect(getByTestId('icon-active')).toBeInTheDocument()
})
```

---

## Test Suite 8: Recommendations Card

### Test 8.1: Displays Algorithm-Based Recommendations
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "recommendations.display")

```typescript
describe('RecommendationsCard', () => {
  it('should display up to 3 recommended destinations', () => {
    // Given recommendation data
    const recommendations = [
      { destination: 'Barcelona, Spain', reason: 'Popular destination', imageUrl: '/barcelona.jpg' },
      { destination: 'Seoul, South Korea', reason: 'Similar to Tokyo', imageUrl: '/seoul.jpg' },
      { destination: 'Iceland', reason: 'Adventure travel', imageUrl: '/iceland.jpg' }
    ]

    // When card renders
    const { getByText } = render(<RecommendationsCard recommendations={recommendations} />)

    // Then should show all recommendations
    expect(getByText('Barcelona, Spain')).toBeInTheDocument()
    expect(getByText('Seoul, South Korea')).toBeInTheDocument()
    expect(getByText('Iceland')).toBeInTheDocument()
  })
})
```

### Test 8.2: Click Recommendation - Pre-fills Trip Creation
**Type:** Integration
**Priority:** Should-pass (acceptance.id: "recommendations.click")

```typescript
it('should navigate to trip creation with pre-filled destination', () => {
  // Given recommendations are displayed
  const { getByText } = render(<RecommendationsCard />)

  // When user clicks a recommendation
  const recommendation = getByText('Barcelona, Spain')
  fireEvent.click(recommendation)

  // Then should navigate with destination parameter
  expect(mockRouter.push).toHaveBeenCalledWith('/trips/create?destination=Barcelona%2C+Spain')
})
```

### Test 8.3: No Recommendations - Card Hidden
**Type:** Unit
**Priority:** Must-pass (acceptance.id: "recommendations.hidden")

```typescript
it('should not render card when no recommendations available', () => {
  // Given empty recommendations
  const { container } = render(<RecommendationsCard recommendations={[]} />)

  // Then card should not be in DOM
  expect(container.firstChild).toBeNull()
})
```

---

## Test Suite 9: Loading States

### Test 9.1: Skeleton Screens During Loading
**Type:** Visual
**Priority:** Must-pass (acceptance.id: "loading.skeleton")

```typescript
describe('Dashboard Loading States', () => {
  it('should display skeleton screens while data loads', () => {
    // Given data is loading
    mockApiResponse('/trips', { delay: 1000 })

    // When dashboard renders
    const { getAllByTestId } = render(<DashboardPage />)

    // Then should show skeletons for each card
    expect(getAllByTestId('skeleton-card')).toHaveLength(5) // 5 cards total
  })
})
```

### Test 9.2: Independent Card Loading
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "loading.independent")

```typescript
it('should load cards independently without blocking', async () => {
  // Given different API response times
  mockApiResponse('/trips', { items: [], delay: 100 })
  mockApiResponse('/profile/statistics', { delay: 500 })

  // When dashboard loads
  const { getByTestId, queryByTestId } = render(<DashboardPage />)

  // Then recent trips should load first
  await waitFor(() => {
    expect(getByTestId('recent-trips-card')).toBeInTheDocument()
    expect(queryByTestId('statistics-skeleton')).toBeInTheDocument() // Still loading
  })
})
```

### Test 9.3: Shimmer Animation
**Type:** Visual
**Priority:** Should-pass (acceptance.id: "loading.shimmer")

```typescript
it('should display shimmer animation on skeletons', () => {
  // Given loading state
  const { getByTestId } = render(<SkeletonCard />)

  // Then should have shimmer animation class
  const skeleton = getByTestId('skeleton')
  expect(skeleton).toHaveClass('animate-pulse')
})
```

---

## Test Suite 10: Error Handling

### Test 10.1: Per-Card Error Boundaries
**Type:** Integration
**Priority:** Must-pass (acceptance.id: "error.boundaries")

```typescript
describe('Dashboard Error Handling', () => {
  it('should show error UI for failed card without breaking others', async () => {
    // Given one API fails
    mockApiResponse('/trips', { error: 'Network error' })
    mockApiResponse('/profile/statistics', { totalTrips: 5 })

    // When dashboard loads
    const { getByText, getByTestId } = render(<DashboardPage />)

    // Then should show error for failed card
    expect(getByText(/Failed to load recent trips/i)).toBeInTheDocument()

    // And other cards should still render
    expect(getByTestId('statistics-card')).toBeInTheDocument()
  })
})
```

### Test 10.2: Retry Failed Requests
**Type:** Integration
**Priority:** Should-pass (acceptance.id: "error.retry")

```typescript
it('should allow user to retry failed data fetch', async () => {
  // Given initial fetch fails
  mockApiResponse('/trips', { error: 'Timeout' })
  const { getByRole } = render(<RecentTripsCard />)

  // When user clicks retry
  const retryButton = getByRole('button', { name: /Retry/i })
  mockApiResponse('/trips', { items: [{ id: '1' }] }) // Second attempt succeeds
  fireEvent.click(retryButton)

  // Then should re-fetch data
  await waitFor(() => {
    expect(screen.queryByText(/Failed to load/i)).not.toBeInTheDocument()
  })
})
```

---

## Test Suite 11: Responsive Layout

### Test 11.1: Desktop Grid - 2 Columns
**Type:** Visual
**Priority:** Should-pass (acceptance.id: "layout.desktop")

```typescript
describe('Dashboard Responsive Layout', () => {
  it('should display 2-column grid on desktop', () => {
    // Given desktop viewport
    global.innerWidth = 1024

    // When dashboard renders
    const { getByTestId } = render(<DashboardLayout />)

    // Then should have 2-column grid class
    const layout = getByTestId('dashboard-layout')
    expect(layout).toHaveClass('lg:grid-cols-2')
  })
})
```

### Test 11.2: Mobile Stack - Single Column
**Type:** Visual
**Priority:** Should-pass (acceptance.id: "layout.mobile")

```typescript
it('should stack cards in single column on mobile', () => {
  // Given mobile viewport
  global.innerWidth = 375

  // When dashboard renders
  const { getByTestId } = render(<DashboardLayout />)

  // Then should have single column
  const layout = getByTestId('dashboard-layout')
  expect(layout).toHaveClass('grid-cols-1')
})
```

---

## Test Suite 12: Analytics Tracking

### Test 12.1: Track Dashboard View
**Type:** Integration
**Priority:** Should-pass (acceptance.id: "analytics.pageView")

```typescript
describe('Dashboard Analytics', () => {
  it('should track dashboard page view on mount', () => {
    // Given analytics is configured
    const trackEvent = jest.fn()

    // When dashboard mounts
    render(<DashboardPage trackEvent={trackEvent} />)

    // Then should fire page view event
    expect(trackEvent).toHaveBeenCalledWith('page_view', {
      page: 'dashboard',
      section: 'dashboard-home'
    })
  })
})
```

### Test 12.2: Track CTA Clicks
**Type:** Integration
**Priority:** Should-pass (acceptance.id: "analytics.ctaClick")

```typescript
it('should track Create Trip CTA clicks', () => {
  // Given analytics is configured
  const trackEvent = jest.fn()
  const { getByRole } = render(<QuickActionsCard trackEvent={trackEvent} />)

  // When user clicks Create New Trip
  const button = getByRole('button', { name: /Create New Trip/i })
  fireEvent.click(button)

  // Then should fire click event
  expect(trackEvent).toHaveBeenCalledWith('cta_click', {
    cta: 'create_trip',
    location: 'quick_actions_card'
  })
})
```

### Test 12.3: Track Trip Card Interactions
**Type:** Integration
**Priority:** Should-pass (acceptance.id: "analytics.tripClick")

```typescript
it('should track trip card clicks', () => {
  // Given analytics is configured
  const trackEvent = jest.fn()
  const { getByTestId } = render(<TripCard trip={{ id: '123' }} trackEvent={trackEvent} />)

  // When user clicks trip card
  const card = getByTestId('trip-card')
  fireEvent.click(card)

  // Then should fire interaction event
  expect(trackEvent).toHaveBeenCalledWith('trip_card_click', {
    tripId: '123',
    location: 'recent_trips'
  })
})
```

---

## Test Suite 13: Dark Mode Support

### Test 13.1: All Cards Support Dark Mode
**Type:** Visual
**Priority:** Should-pass (acceptance.id: "darkMode.support")

```typescript
describe('Dashboard Dark Mode', () => {
  it('should apply dark mode classes to all cards', () => {
    // Given dark mode is enabled
    document.documentElement.classList.add('dark')

    // When dashboard renders
    const { getByTestId } = render(<DashboardPage />)

    // Then all cards should have dark mode styles
    const layout = getByTestId('dashboard-layout')
    expect(layout).toHaveClass('dark:bg-slate-900')
  })
})
```

---

## Test Coverage Requirements

**Minimum Coverage:** 90%

- **Unit Tests:** 70+ tests for individual components
- **Integration Tests:** 25+ tests for data fetching, navigation, feature flags
- **E2E Tests:** 10+ tests for critical user flows
- **Visual Tests:** 15+ tests for layout, responsiveness, theming

**Total Test Cases:** 120+

---

## Acceptance Criteria Mapping

| Acceptance ID | Test Suite | Status |
|---------------|------------|--------|
| `flag.disabled` | Suite 1 | ❌ RED |
| `flag.enabled` | Suite 1 | ❌ RED |
| `access.protected` | Suite 2 | ❌ RED |
| `access.authenticated` | Suite 2 | ❌ RED |
| `empty.noTrips` | Suite 3 | ❌ RED |
| `empty.ctaClick` | Suite 3 | ❌ RED |
| `recent.display` | Suite 4 | ❌ RED |
| `recent.tripData` | Suite 4 | ❌ RED |
| `recent.navigation` | Suite 4 | ❌ RED |
| `upcoming.filter` | Suite 5 | ❌ RED |
| `upcoming.countdown` | Suite 5 | ❌ RED |
| `upcoming.empty` | Suite 5 | ❌ RED |
| `actions.createClick` | Suite 6 | ❌ RED |
| `actions.templateModal` | Suite 6 | ❌ RED |
| `stats.metrics` | Suite 7 | ❌ RED |
| `stats.zeroState` | Suite 7 | ❌ RED |
| `recommendations.display` | Suite 8 | ❌ RED |
| `recommendations.hidden` | Suite 8 | ❌ RED |
| `loading.skeleton` | Suite 9 | ❌ RED |
| `loading.independent` | Suite 9 | ❌ RED |
| `error.boundaries` | Suite 10 | ❌ RED |
| `layout.desktop` | Suite 11 | ❌ RED |
| `layout.mobile` | Suite 11 | ❌ RED |
| `analytics.pageView` | Suite 12 | ❌ RED |
| `analytics.ctaClick` | Suite 12 | ❌ RED |

---

## Next Steps

1. ✅ Tests authored (RED phase)
2. ⏭️ Implement components to pass tests (GREEN phase)
3. ⏭️ Refactor while keeping tests green
4. ⏭️ Verify 90% coverage achieved
