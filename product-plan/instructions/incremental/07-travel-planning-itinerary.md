# Milestone 7: Travel Planning & Itinerary

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

This milestone implements the AI-powered itinerary generation system that creates personalized day-by-day travel plans. This is one of the most sophisticated features in TIP, combining AI generation, natural language editing, and interactive customization.

## Overview

Key functionality in this section:

- Template selection screen with 4 itinerary styles (Relaxed, Balanced, Packed, Budget-focused)
- AI-generated day-by-day itinerary with attractions, restaurants, and activities
- Natural language editing interface for customizing itinerary
- Manual customization (add, remove, reorder items)
- Interactive map view showing all itinerary locations
- Regenerate itinerary button for completely new plan
- Separate flight options section aligned to trip dates

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/travel-planning-itinerary/components/`

Build the following components based on the provided references:

- **ItineraryPage.tsx** — Main page container
- **TemplateSelector.tsx** — Initial style selection screen with 4 cards
- **NaturalLanguageEditor.tsx** — Text input for AI-powered edits (e.g., "Add more restaurants on day 2")
- **ItineraryTimeline.tsx** — Vertical timeline showing all days
- **DaySection.tsx** — Single day container with date header and items
- **ItineraryItem.tsx** — Individual attraction/restaurant/activity with details
- **ItemControls.tsx** — Remove button and drag handle for reordering
- **AddItemButton.tsx** — Button to add custom item to day
- **MapView.tsx** — Interactive map showing all itinerary locations
- **FlightOptionsSection.tsx** — Separate section for recommended flights
- **RegenerateButton.tsx** — Button to create new AI-generated itinerary
- **LoadingState.tsx** — Skeleton/spinner for template selection and generation

### 2. Data Layer

**Files:** `sections/travel-planning-itinerary/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface Itinerary {
  id: string;
  tripId: string;
  style: 'relaxed' | 'balanced' | 'packed' | 'budget-focused';
  days: ItineraryDay[];
}

interface ItineraryDay {
  dayNumber: number;
  date: string;
  items: ItineraryItem[];
}

interface ItineraryItem {
  id: string;
  type: 'attraction' | 'restaurant' | 'activity';
  name: string;
  description: string;
  location: Location;
  costEstimate: number;
  duration: string; // e.g., "2 hours"
  order: number;
}

interface Location {
  address: string;
  latitude: number;
  longitude: number;
}

interface FlightOption {
  airline: string;
  route: string;
  price: number;
  bookingLink: string;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onStyleSelect(style: string): Promise<void>` — Generate itinerary based on selected style
- `onNaturalLanguageEdit(prompt: string): Promise<void>` — AI regenerates itinerary based on prompt
- `onAddItem(dayNumber: number, item: ItineraryItem): void` — Add custom item to day
- `onRemoveItem(itemId: string): void` — Remove item from itinerary
- `onReorderItems(dayNumber: number, items: ItineraryItem[]): void` — Update item order
- `onRegenerateItinerary(): Promise<void>` — Create completely new itinerary
- `onViewMap(): void` — Toggle map overlay
- `onFlightClick(bookingLink: string): void` — Open flight booking link in new tab

### 4. Template Styles

Provide 4 itinerary style cards:

- **Relaxed Pace:** 2-3 activities per day, longer durations, more free time
- **Balanced:** 3-4 activities per day, mix of structured and free time
- **Packed/Adventure:** 5-7 activities per day, fast-paced, maximizes sightseeing
- **Budget-focused:** Prioritizes free/low-cost activities, local food spots

Each card shows:
- Style name
- Brief description
- Icon/illustration
- Example day structure

### 5. Natural Language Editing

- Prominent text input at top: "Ask me to adjust your itinerary..."
- User can type requests like:
  - "Add more restaurants on day 2"
  - "Replace museum with outdoor activities"
  - "Make day 3 more relaxed"
  - "Add shopping destinations"
- Submit triggers AI regeneration with modifications
- Show loading state during regeneration
- Update timeline with new itinerary

### 6. Manual Customization

- Drag handle on each item for reordering
- Remove button (X icon) on each item
- "Add item" button within each day section
- Add item form includes: name, type (attraction/restaurant/activity), location, cost, duration

### 7. Map Integration

- Interactive map (Leaflet, Mapbox, or similar)
- Plot all itinerary items as markers
- Color-code markers by type (blue=attraction, amber=restaurant, green=activity)
- Click marker to see item details
- Day-by-day filtering (show only Day 1, Day 2, etc.)
- "View on Map" button toggles map overlay

## Files to Reference

- `sections/travel-planning-itinerary/spec.md` — Complete specification
- `sections/travel-planning-itinerary/README.md` — Implementation guide
- `sections/travel-planning-itinerary/types.ts` — TypeScript interfaces
- `sections/travel-planning-itinerary/sample-data.json` — Example itinerary data
- `sections/travel-planning-itinerary/components/` — Reference components
- `sections/travel-planning-itinerary/*.png` — Screenshots
- `sections/travel-planning-itinerary/tests.md` — Test instructions

## Expected User Flows

### Flow 1: User generates balanced itinerary
1. User navigates to itinerary section
2. Template selection screen displays with 4 style cards
3. User clicks "Balanced" card
4. Loading state appears with message "Generating your itinerary..."
5. Timeline view displays with 7 days (based on trip duration)
6. Day 1 shows:
   - Morning: Senso-ji Temple (2 hours, $0)
   - Lunch: Sushi Zanmai (1.5 hours, $25)
   - Afternoon: Tokyo Skytree (2 hours, $30)
   - Dinner: Izakaya Gonpachi (2 hours, $40)
7. Each subsequent day shows 3-4 activities with descriptions, locations, costs

**Expected outcome:** User receives personalized itinerary matching their travel style.

### Flow 2: User edits itinerary with natural language
1. User views generated itinerary
2. Notices Day 2 has only one restaurant
3. Clicks on natural language editor at top
4. Types: "Add more restaurants on day 2"
5. Clicks submit button
6. Loading state appears: "Updating your itinerary..."
7. Timeline refreshes with Day 2 now showing 2 additional restaurants
8. User reviews updated itinerary and is satisfied

**Expected outcome:** AI understands request and modifies itinerary accordingly.

### Flow 3: User manually removes and reorders items
1. User reviews Day 3 itinerary
2. Sees "Tokyo Disneyland" attraction but prefers cultural sites
3. Clicks remove button (X) on Disneyland item
4. Item is removed from timeline
5. User drags "Imperial Palace" item from Day 4 to Day 3 using drag handle
6. Item moves and day numbers update
7. User adds custom item by clicking "Add item" button in Day 3
8. Enters: Name: "Meiji Shrine", Type: Attraction, Cost: $0, Duration: 1.5 hours
9. New item appears in Day 3 timeline

**Expected outcome:** User has full control over itinerary customization.

### Flow 4: User views itinerary on map
1. User clicks "View on Map" button at top
2. Map overlay appears showing all itinerary locations
3. Markers are color-coded: blue (attractions), amber (restaurants), green (activities)
4. User clicks on Day 1 filter
5. Map shows only Day 1 locations
6. User clicks on marker for "Senso-ji Temple"
7. Popup displays: Name, Type, Cost, Duration, Description
8. User clicks "Close Map" button to return to timeline view

**Expected outcome:** User visualizes itinerary geographically and understands spatial relationships.

### Flow 5: User regenerates entire itinerary
1. User reviews generated itinerary but wants completely different suggestions
2. Clicks "Regenerate Itinerary" button at top
3. Confirmation dialog appears: "This will create a new itinerary. Current itinerary will be lost unless saved."
4. User confirms
5. Loading state appears: "Generating new itinerary..."
6. Timeline refreshes with completely different activities for each day
7. User explores new options

**Expected outcome:** User can easily explore multiple itinerary options.

### Flow 6: User views flight options
1. User scrolls to Flight Options section (above or below timeline)
2. Sees 3-4 recommended flights:
   - Flight 1: United Airlines, Direct, $850, Link to Google Flights
   - Flight 2: ANA, Direct, $920, Link to Expedia
   - Flight 3: Delta, 1 stop, $680, Link to Kayak
3. User clicks on booking link for Flight 1
4. Opens flight search in new tab with dates pre-filled
5. User can book flight externally

**Expected outcome:** User discovers flight options aligned to their trip dates.

## Done When

- [ ] Template selection screen displays 4 style cards (Relaxed, Balanced, Packed, Budget-focused)
- [ ] Clicking style card triggers itinerary generation with loading state
- [ ] Vertical timeline displays all trip days chronologically
- [ ] Each day section shows date header and list of items
- [ ] Itinerary items display name, type icon, description, location, cost, duration
- [ ] Natural language editor allows text input for AI-powered edits
- [ ] Submitting natural language prompt regenerates itinerary with modifications
- [ ] Remove button deletes item from timeline
- [ ] Drag handles allow reordering items within and between days
- [ ] "Add item" button opens form to add custom attraction/restaurant/activity
- [ ] "Regenerate Itinerary" button creates completely new plan after confirmation
- [ ] "View on Map" button toggles interactive map overlay
- [ ] Map displays all itinerary items as color-coded markers
- [ ] Map includes day-by-day filtering
- [ ] Clicking map marker shows item details in popup
- [ ] Flight Options section displays 3-4 recommended flights with prices and booking links
- [ ] Clicking flight booking link opens external site in new tab
- [ ] Loading states show during template selection and regeneration
- [ ] Mobile layout uses single column timeline with touch-friendly controls
- [ ] Light and dark mode styles work across all components
- [ ] Tests cover template selection, natural language editing, manual customization, map interactions, and flight clicks
- [ ] Visual appearance matches screenshots in section directory
