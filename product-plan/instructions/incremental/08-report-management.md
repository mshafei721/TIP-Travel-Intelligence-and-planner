# Milestone 8: Report Management

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

This milestone implements the report management system that provides a centralized hub for viewing, organizing, exporting, and managing travel intelligence reports. This includes both a list view for all trips and a detailed interactive report view.

## Overview

Key functionality in this section:

- Trip list view showing all saved trips with destination, dates, status, and expiry
- Interactive report view with summary overview, section navigation, and embedded map
- PDF export functionality with print-optimized layout
- Trip deletion with confirmation dialog
- Auto-deletion schedule display with countdown warnings
- Bulk operations (select multiple trips for delete or export)
- Report editing and versioning capabilities

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/report-management/components/`

Build the following components based on the provided references:

- **TripListPage.tsx** — Main list view showing all trips
- **TripListItem.tsx** — Individual trip card/row with quick actions
- **TripDetailPage.tsx** — Full interactive report view
- **ReportSummary.tsx** — Overview section with key trip info at top of report
- **SectionNavigation.tsx** — Tabs or jump links to report sections (Overview, Visa, Destination, Itinerary)
- **EmbeddedMap.tsx** — Interactive map showing itinerary locations and regions
- **ExportPDFButton.tsx** — Button triggering PDF generation
- **DeleteTripButton.tsx** — Button with confirmation dialog
- **AutoDeletionWarning.tsx** — Countdown banner showing days until deletion
- **BulkActionsBar.tsx** — Toolbar for bulk operations when trips are selected
- **EmptyState.tsx** — Message for users with no trips

### 2. Data Layer

**Files:** `sections/report-management/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface TripListItem {
  id: string;
  destination: string;
  startDate: string;
  endDate: string;
  status: 'upcoming' | 'in-progress' | 'completed';
  createdAt: string;
  deletionDate: string;
}

interface TravelReport {
  id: string;
  trip: Trip;
  summary: ReportSummary;
  sections: ReportSection[];
}

interface ReportSummary {
  destination: string;
  dates: string;
  visaStatus: string;
  weatherSummary: string;
  totalCost: number;
}

interface ReportSection {
  id: string;
  type: 'visa' | 'destination' | 'itinerary' | 'flights';
  title: string;
  content: any;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onTripClick(tripId: string): void` — Navigate to trip detail page
- `onExportPDF(tripId: string): Promise<void>` — Generate and download PDF
- `onDeleteTrip(tripId: string): Promise<void>` — Delete trip after confirmation
- `onBulkDelete(tripIds: string[]): Promise<void>` — Delete multiple trips
- `onBulkExport(tripIds: string[]): Promise<void>` — Export multiple trips as PDFs
- `onSectionNavigate(sectionId: string): void` — Scroll/jump to report section
- `onEditReport(tripId: string): void` — Open report editing mode
- `onMapInteract(location: Location): void` — Handle map marker clicks

### 4. Trip List View

Display all trips in a table or card layout with:

- Destination name (e.g., "Tokyo, Japan")
- Travel dates (e.g., "Apr 1-10, 2024")
- Status badge (upcoming/in-progress/completed) with color coding
- Creation date (e.g., "Created Mar 1, 2024")
- Auto-delete expiry date (e.g., "Expires Apr 17, 2024")
- Quick action buttons: "View Report", "Export PDF", "Delete"

Sort options: Most recent, Upcoming first, Alphabetical by destination

### 5. Interactive Report View

**Layout:**
- Report Summary section at top (destination, dates, visa status, weather summary, total cost)
- Section Navigation (tabs or anchor links): Overview, Visa & Entry, Destination Intelligence, Travel Itinerary, Flights
- Embedded interactive map below navigation
- Full report content sections below map

**Navigation behavior:**
- Click section tab/link to scroll to that section
- Sections are collapsible/expandable (optional)
- Active section highlighted in navigation

**Map features:**
- Shows itinerary locations as markers
- Color-coded by type (attractions, restaurants, activities)
- Click marker to see details
- Pan, zoom, and reset view controls

### 6. PDF Export

- "Export PDF" button in trip list and detail view
- Click triggers PDF generation with loading state
- Print-optimized layout:
  - Proper page breaks between sections
  - Readable fonts and sizing
  - Map rendered as static image
  - All text and data included
- Download PDF file with name: `TIP-Report-[Destination]-[Date].pdf`

### 7. Deletion Flow

- "Delete" button shows confirmation dialog
- Dialog message: "Are you sure you want to delete this trip? This action cannot be undone."
- Confirm button triggers deletion
- Success message: "Trip deleted successfully"
- Redirect to trip list if deleting from detail view

### 8. Auto-Deletion Warning

- Display countdown banner if trip is scheduled for deletion soon
- Banner text: "This trip will be automatically deleted in 5 days"
- Calculation: 7 days after trip end date
- Banner appears when < 7 days remain
- Color-coded: Yellow warning for < 7 days, Red alert for < 3 days

### 9. Bulk Operations

- Checkboxes on trip list items
- Select multiple trips
- Bulk actions bar appears with "Delete Selected" and "Export Selected" buttons
- Confirmation dialog for bulk delete
- Progress indicator during bulk operations

### 10. Empty State

When no trips exist:
- Empty state message: "You haven't created any trips yet."
- "Create Your First Trip" button
- Navigate to trip creation wizard

## Files to Reference

- `sections/report-management/spec.md` — Complete specification
- `sections/report-management/README.md` — Implementation guide
- `sections/report-management/types.ts` — TypeScript interfaces
- `sections/report-management/sample-data.json` — Example report data
- `sections/report-management/components/` — Reference components
- `sections/report-management/*.png` — Screenshots
- `sections/report-management/tests.md` — Test instructions

## Expected User Flows

### Flow 1: User views all trips
1. User navigates to "My Trips" from main navigation
2. Trip list page loads with loading state
3. List displays 5 trips in table/card format
4. Each trip shows: destination, dates, status badge, creation date, expiry date
5. Quick action buttons visible on each trip: View Report, Export PDF, Delete
6. User can sort by "Most Recent" or filter by status

**Expected outcome:** User sees comprehensive overview of all their trips.

### Flow 2: User views trip detail report
1. User clicks "View Report" on "Tokyo, Japan" trip
2. Navigates to report detail page
3. Report Summary section displays at top:
   - Destination: Tokyo, Japan
   - Dates: April 1-10, 2024
   - Visa Status: Visa-Free (90 days)
   - Weather: Spring weather, 60-72°F, occasional rain
   - Total Estimated Cost: $2,850
4. Section Navigation shows tabs: Overview, Visa & Entry, Destination Intelligence, Travel Itinerary, Flights
5. Embedded interactive map shows all itinerary locations as markers
6. User scrolls to view full content for each section
7. Clicks on "Visa & Entry" tab to jump to that section

**Expected outcome:** User accesses comprehensive travel intelligence report with easy navigation.

### Flow 3: User exports report to PDF
1. User views trip detail page
2. Clicks "Export PDF" button at top
3. Loading indicator appears: "Generating PDF..."
4. PDF file downloads: `TIP-Report-Tokyo-Japan-2024-04-01.pdf`
5. User opens PDF and sees print-optimized layout with all sections
6. Map rendered as static image in PDF
7. Success message appears: "PDF exported successfully"

**Expected outcome:** User has offline copy of report for printing or sharing.

### Flow 4: User deletes a trip
1. User views trip list
2. Clicks "Delete" button on completed trip from 6 months ago
3. Confirmation dialog appears: "Are you sure you want to delete this trip? This action cannot be undone."
4. User clicks "Confirm Delete"
5. Trip is removed from list
6. Success message: "Trip deleted successfully"

**Expected outcome:** User removes unwanted trip with clear confirmation step.

### Flow 5: User sees auto-deletion warning
1. User views trip list
2. Notices trip to "Barcelona, Spain" ending on March 31
3. Today is April 5 (5 days after trip end)
4. Warning badge displays: "Expires in 2 days"
5. User clicks on trip to view details
6. Yellow warning banner at top: "This trip will be automatically deleted in 2 days as part of our data retention policy."
7. User can export PDF before deletion if desired

**Expected outcome:** User is warned about impending auto-deletion and can take action.

### Flow 6: User performs bulk operations
1. User views trip list with 10 trips
2. Selects checkboxes on 3 completed trips
3. Bulk actions bar appears at top: "3 trips selected"
4. User clicks "Export Selected" button
5. Progress indicator shows: "Exporting 1 of 3..."
6. All 3 PDFs download sequentially
7. Success message: "3 trips exported successfully"
8. User deselects trips, then selects 2 draft trips
9. Clicks "Delete Selected"
10. Confirmation: "Delete 2 trips? This action cannot be undone."
11. User confirms, trips are deleted

**Expected outcome:** User efficiently manages multiple trips simultaneously.

### Flow 7: User navigates report sections
1. User views trip detail page
2. Clicks on "Travel Itinerary" tab in section navigation
3. Page scrolls smoothly to itinerary section
4. Active tab highlights with amber accent
5. User clicks on map marker for "Senso-ji Temple"
6. Marker popup displays: Name, Type, Cost, Duration
7. User clicks "Destination Intelligence" tab
8. Page scrolls to destination section

**Expected outcome:** User efficiently navigates large report document.

## Done When

- [ ] Trip list page displays all trips with destination, dates, status, and expiry
- [ ] Status badges use color coding (green=completed, blue=upcoming, amber=in-progress)
- [ ] Quick action buttons (View Report, Export PDF, Delete) work on each trip
- [ ] Empty state displays when no trips exist with "Create Your First Trip" button
- [ ] Clicking trip card/row navigates to trip detail page
- [ ] Report detail page shows summary overview at top with key trip info
- [ ] Section navigation (tabs or links) allows jumping to specific report sections
- [ ] Active section highlights in navigation
- [ ] Embedded interactive map displays itinerary locations as markers
- [ ] Map markers are color-coded by type and clickable for details
- [ ] Export PDF button generates and downloads print-optimized PDF
- [ ] PDF includes all report content with proper formatting and static map image
- [ ] Delete button shows confirmation dialog before deletion
- [ ] Auto-deletion warning displays countdown for trips expiring soon
- [ ] Bulk selection checkboxes allow selecting multiple trips
- [ ] Bulk actions bar appears with Delete Selected and Export Selected buttons
- [ ] Bulk delete confirms before execution
- [ ] Bulk export shows progress indicator during multi-file generation
- [ ] Loading states display while fetching trip list and report data
- [ ] Mobile layout uses single column with touch-friendly controls
- [ ] Light and dark mode styles work across all components
- [ ] Tests cover list view, detail view, PDF export, deletion, bulk operations, and navigation
- [ ] Visual appearance matches screenshots in section directory
