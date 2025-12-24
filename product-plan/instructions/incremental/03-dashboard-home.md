# Milestone 3: Dashboard & Home

## What's Provided

This export package includes:

- **Product Overview** (`product-overview.md`) — Product description, problems solved, and planned sections
- **Design System** (`design-system/`) — Design tokens (colors, typography)
- **Data Model** (`data-model/`) — Entity descriptions, relationships, TypeScript types, sample data
- **Shell Components** (`shell/components/`) — Pre-built React components for the application shell (navigation, layout)
- **Section Components** (`sections/[section-id]/components/`) — Pre-built React components for each feature section
- **Section Types** (`sections/[section-id]/types.ts`) — TypeScript interfaces for each section
- **Section Sample Data** (`sections/[section-id]/sample-data.json`) — Example data for development/testing
- **Screenshots** (`shell/*.png`, `sections/[section-id]/*.png`) — Visual references for each screen

## What You Need to Build

This milestone implements the central landing page that users see after logging in. It provides an overview of their travel activity, quick access to key actions, and personalized recommendations to encourage engagement.

## Overview

Key functionality in this section:

- Recent trips card showing 3-5 most recent trips
- Upcoming trips card with departure countdown
- Quick actions for creating new trips and using templates
- Statistics summary showing travel metrics
- AI-generated destination recommendations
- Empty state for first-time users with prominent CTA

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/dashboard-home/components/`

Build the following components based on the provided references:

- **DashboardLayout.tsx** — Main grid container for all dashboard cards
- **RecentTripsCard.tsx** — Displays 3-5 most recent trips with thumbnails
- **UpcomingTripsCard.tsx** — Shows future trips with countdown
- **QuickActionsCard.tsx** — Large buttons for Create Trip, View All Trips, Use Template
- **StatisticsSummaryCard.tsx** — Four metrics: total trips, countries, destinations, active trips
- **RecommendationsCard.tsx** — AI-suggested destinations with reasons
- **EmptyState.tsx** — Welcome message for users with no trips
- **TripCard.tsx** — Reusable trip card showing destination, dates, status

### 2. Data Layer

**Files:** `sections/dashboard-home/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface DashboardData {
  recentTrips: Trip[];
  upcomingTrips: Trip[];
  statistics: Statistics;
  recommendations: Recommendation[];
}

interface Statistics {
  totalTrips: number;
  countriesVisited: number;
  destinationsExplored: number;
  activeTrips: number;
}

interface Recommendation {
  destination: string;
  reason: string;
  imageUrl: string;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onCreateTrip(): void` — Navigate to trip creation wizard
- `onViewAllTrips(): void` — Navigate to report management
- `onUseTemplate(): void` — Show template selection modal
- `onTripClick(tripId: string): void` — Navigate to trip details
- `onRecommendationClick(destination: string): void` — Start trip creation with pre-filled destination

### 4. Empty States

- **No trips yet:** Display EmptyState component with:
  - Welcome message: "Welcome to TIP! Start planning your next adventure."
  - Brief explanation of features
  - Prominent "Create Your First Trip" button (blue primary)
- **No upcoming trips:** In UpcomingTripsCard, show "No upcoming trips planned"
- **No recommendations:** Hide RecommendationsCard if no data available

### 5. Loading States

- Skeleton screens for each card while loading
- Shimmer animation on skeleton placeholders
- Cards load independently (don't wait for all data)

## Files to Reference

- `sections/dashboard-home/spec.md` — Complete specification
- `sections/dashboard-home/README.md` — Implementation guide
- `sections/dashboard-home/types.ts` — TypeScript interfaces
- `sections/dashboard-home/sample-data.json` — Example dashboard data
- `sections/dashboard-home/components/` — Reference components
- `sections/dashboard-home/*.png` — Screenshots
- `sections/dashboard-home/tests.md` — Test instructions

## Expected User Flows

### Flow 1: First-time user sees empty state
1. User logs in for the first time
2. Dashboard loads with empty state
3. Sees welcome message: "Welcome to TIP! Start planning your next adventure."
4. Sees brief explanation of TIP features
5. Sees prominent "Create Your First Trip" button
6. Clicks button and navigates to trip creation wizard

**Expected outcome:** User is guided to create their first trip immediately.

### Flow 2: Returning user views dashboard
1. User logs in
2. Dashboard loads with skeleton screens
3. Recent Trips card displays 3 trips with destinations, dates, status badges
4. Upcoming Trips card shows 2 future trips with countdown timers
5. Statistics Summary shows: 15 total trips, 8 countries, 12 destinations, 2 active trips
6. Recommendations card suggests 3 destinations with reasons
7. Quick Actions card provides buttons for Create Trip, View All Trips, Use Template

**Expected outcome:** User sees comprehensive overview of their travel activity and can quickly access key features.

### Flow 3: User explores a recent trip
1. User views Recent Trips card
2. Sees trip card with "Tokyo, Japan" destination, "Mar 15-22, 2024", "Completed" status
3. Clicks on trip card
4. Navigates to trip report detail page

**Expected outcome:** User can quickly access previous trip reports.

### Flow 4: User creates new trip from quick actions
1. User views Quick Actions card
2. Clicks "Create New Trip" button (blue primary, prominent)
3. Navigates to trip creation wizard

**Expected outcome:** User starts trip creation flow from dashboard.

### Flow 5: User explores AI recommendations
1. User views Recommendations card
2. Sees 3 recommended destinations: "Barcelona, Spain", "Seoul, South Korea", "Iceland"
3. Each shows reason: "Based on your trip to Tokyo, you might enjoy..."
4. Clicks on "Barcelona, Spain" recommendation
5. Navigates to trip creation wizard with destination pre-filled

**Expected outcome:** User discovers new destinations based on their travel history.

### Flow 6: User with no upcoming trips
1. User views dashboard
2. Recent Trips card shows completed trips
3. Upcoming Trips card displays "No upcoming trips planned"
4. User clicks "Create New Trip" from Quick Actions

**Expected outcome:** Empty state for upcoming trips is clear but not obtrusive.

## Done When

- [ ] Dashboard layout renders as responsive grid (2-3 columns desktop, 1 column mobile)
- [ ] Recent Trips card displays 3-5 most recent trips with destinations, dates, and status
- [ ] Trip cards are clickable and navigate to trip details
- [ ] Upcoming Trips card shows countdown to departure for future trips
- [ ] Quick Actions card prominently displays Create New Trip button with blue/amber styling
- [ ] Statistics Summary card shows four metrics with icons and counts
- [ ] Recommendations card displays AI-suggested destinations with images and reasons
- [ ] Empty state shows for users with no trips, with prominent CTA
- [ ] "No upcoming trips planned" message appears when applicable
- [ ] Skeleton screens display while dashboard data loads
- [ ] All cards support light and dark mode
- [ ] Mobile layout stacks cards vertically with proper spacing
- [ ] "View All" link in Recent Trips card navigates to Report Management
- [ ] Template button opens template selection modal (or navigates to templates)
- [ ] Tests cover empty states, populated states, click interactions, and loading states
- [ ] Visual appearance matches screenshots in section directory
