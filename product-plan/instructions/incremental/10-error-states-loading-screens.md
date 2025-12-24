# Milestone 10: Error States & Loading Screens

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

This milestone implements comprehensive error handling and loading states that ensure users always understand what's happening in the application. This includes global error pages, inline error states, validation errors, and progress indicators for all async operations.

## Overview

Key functionality in this section:

- Standalone 404 and 500 error pages (without app shell)
- Inline API failure banners within app shell
- Validation error messages on forms
- Report generation progress screen with status updates
- Skeleton screens for page and component loading
- Button loading states with spinners
- Error details toggle for technical information
- Network offline detection

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/error-states-loading-screens/components/`

Build the following components based on the provided references:

- **NotFoundPage.tsx** — Standalone 404 page without shell
- **ServerErrorPage.tsx** — Standalone 500 page without shell
- **InlineErrorBanner.tsx** — Error banner for API failures within app shell
- **ValidationError.tsx** — Inline field validation message
- **ReportGenerationProgress.tsx** — Full-page modal with progress bar and status messages
- **SkeletonScreen.tsx** — Content placeholder with pulse animation
- **ButtonLoadingState.tsx** — Button with spinner and disabled state
- **ErrorDetailsToggle.tsx** — Collapsible section showing technical error info
- **NetworkOfflineWarning.tsx** — Banner when internet connection is lost

### 2. Data Layer

**Files:** `sections/error-states-loading-screens/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface ErrorState {
  type: '404' | '500' | 'api-failure' | 'validation' | 'network';
  message: string;
  details?: ErrorDetails;
}

interface ErrorDetails {
  errorCode?: string;
  timestamp: string;
  requestId?: string;
  stackTrace?: string;
}

interface ProgressState {
  percentage: number;
  currentStage: string;
  stages: ProgressStage[];
  estimatedTimeRemaining?: number;
}

interface ProgressStage {
  name: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  message: string;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onRetry(): void` — Retry failed operation
- `onGoToDashboard(): void` — Navigate to dashboard from error page
- `onGoBack(): void` — Navigate to previous page
- `onDismissError(): void` — Dismiss inline error banner
- `onShowErrorDetails(): void` — Toggle error details visibility
- `onCopyErrorDetails(): void` — Copy technical error info to clipboard
- `onContactSupport(): void` — Open support contact modal

### 4. 404 Not Found Page

**Standalone page (no app shell):**
- Illustration or 404 icon
- Heading: "Page Not Found"
- Message: "The page you're looking for doesn't exist or has been removed."
- Primary button: "Go to Dashboard" (blue)
- Secondary button: "Go Back" (gray)
- Route: `/404` or catch-all route

### 5. 500 Server Error Page

**Standalone page (no app shell):**
- Illustration or 500 icon
- Heading: "Something Went Wrong"
- Message: "We're experiencing technical difficulties. Please try again."
- Primary button: "Retry" (blue)
- Secondary button: "Go to Dashboard" (gray)
- Optional: Error ID for support reference
- Route: `/500`

### 6. Inline API Failure Banner

**Used within app shell when API calls fail:**
- Banner at top of page content area
- Error icon + concise message (e.g., "Failed to load trip data")
- "Retry" button within banner
- Dismissible X button
- Optional "Show Details" toggle
- Color: Red background for critical errors, yellow for warnings

**Common scenarios:**
- Failed to load trips
- Failed to save draft
- Failed to generate report
- Failed to export PDF
- Network timeout

### 7. Validation Errors

**Inline form field errors:**
- Red border on invalid field
- Red error text below/beside field
- Icon indicating error
- Real-time validation (clears as user corrects)

**Summary error banner:**
- Appears at top of form if multiple errors
- Lists all validation issues
- Each error links to corresponding field (scrolls and focuses)

**Common validations:**
- Required field empty
- Invalid email format
- Password too weak
- Date range invalid (return before departure)
- Budget must be positive number

### 8. Report Generation Progress

**Full-page modal overlay:**
- Blocks navigation during generation
- Animated progress bar (0-100%)
- Current stage display (e.g., "Analyzing visa requirements...")
- Stage list showing completed/in-progress/pending:
  - ✓ Analyzing trip details (completed)
  - ⏳ Generating visa intelligence (in-progress)
  - ⏸ Creating itinerary (pending)
  - ⏸ Finalizing report (pending)
- Estimated time remaining (optional)
- Cannot be dismissed (only completes or errors)

**Progress stages for report generation:**
1. Analyzing trip details
2. Generating visa intelligence
3. Gathering destination information
4. Checking weather forecasts
5. Creating itinerary
6. Finding flight options
7. Finalizing report

### 9. Skeleton Screens

**Content placeholders with shimmer animation:**
- Match actual layout structure
- Use for page loads, card loads, list loads
- Subtle pulse/shimmer effect
- Replaces spinner for better UX

**Common skeleton screens:**
- Dashboard cards
- Trip list items
- Report sections
- Navigation items during initial load

### 10. Button Loading States

**Button with loading spinner:**
- Spinner replaces button text or appears next to it
- Button disabled during loading
- Loading text (optional): "Saving...", "Loading...", "Generating..."
- Color remains consistent with button type

**Used for:**
- Form submissions
- Save draft
- Export PDF
- Delete operations
- Template creation

### 11. Error Details Toggle

**Collapsible technical information:**
- Default: Hidden, show user-friendly message only
- "Show Details" button/link
- Expands to show:
  - Error code
  - Timestamp
  - Request ID
  - Stack trace (if available)
- Monospace font for technical content
- "Copy Error Details" button
- "Contact Support" link with pre-filled error info

### 12. Network Offline Warning

**Banner when internet connection lost:**
- Appears at top of page
- Message: "You're offline. Some features may not work."
- Icon indicating no connection
- Automatically dismisses when connection restored
- Non-blocking (user can still view cached content)

## Files to Reference

- `sections/error-states-loading-screens/spec.md` — Complete specification
- `sections/error-states-loading-screens/README.md` — Implementation guide
- `sections/error-states-loading-screens/types.ts` — TypeScript interfaces
- `sections/error-states-loading-screens/sample-data.json` — Example error states
- `sections/error-states-loading-screens/components/` — Reference components
- `sections/error-states-loading-screens/*.png` — Screenshots
- `sections/error-states-loading-screens/tests.md` — Test instructions

## Expected User Flows

### Flow 1: User encounters 404 error
1. User navigates to `/trips/nonexistent-id`
2. 404 page loads without app shell
3. Sees illustration and "Page Not Found" heading
4. Reads message: "The page you're looking for doesn't exist or has been removed."
5. Clicks "Go to Dashboard" button
6. Navigates to dashboard

**Expected outcome:** User understands the issue and can navigate back to working pages.

### Flow 2: User encounters server error
1. User tries to load trip detail page
2. Server returns 500 error
3. 500 page loads without app shell
4. Sees "Something Went Wrong" heading
5. Clicks "Retry" button
6. Page reloads and attempts to fetch data again
7. Either succeeds or shows persistent error with "Go to Dashboard" option

**Expected outcome:** User can retry or navigate away from broken page.

### Flow 3: API failure during page interaction
1. User viewing dashboard
2. Clicks "Export PDF" on trip
3. API call fails due to network issue
4. Inline error banner appears at top of dashboard
5. Banner displays: "Failed to export PDF. Please try again."
6. User clicks "Retry" button in banner
7. Export succeeds, banner disappears
8. Success message: "PDF exported successfully"

**Expected outcome:** User can recover from transient errors without leaving page.

### Flow 4: Form validation errors
1. User fills out trip creation form (Step 1)
2. Enters invalid email: "notanemail"
3. Email field shows red border and error message: "Please enter a valid email address"
4. User clicks "Next" without fixing
5. Summary error banner appears at top: "Please fix the following errors:"
6. User corrects email to "user@example.com"
7. Validation error clears in real-time
8. User clicks "Next" successfully

**Expected outcome:** User receives clear feedback and can correct errors before proceeding.

### Flow 5: Report generation progress
1. User completes trip creation and clicks "Confirm & Generate Report"
2. Full-page progress modal appears
3. Progress bar at 0%
4. Stage 1 shows: "✓ Analyzing trip details" (completed)
5. Stage 2 shows: "⏳ Generating visa intelligence" (in-progress)
6. Progress bar advances to 30%
7. Stage 2 completes, Stage 3 starts: "⏳ Gathering destination information"
8. Progress continues through all stages
9. Progress bar reaches 100%
10. Modal closes, user navigates to completed report

**Expected outcome:** User understands report generation is progressing and sees clear status updates.

### Flow 6: Skeleton screens during page load
1. User clicks "My Trips" in navigation
2. Page navigation starts
3. Skeleton screen displays with placeholder cards
4. Shimmer animation runs on skeletons
5. After 500ms, real data loads
6. Skeleton replaced with actual trip cards

**Expected outcome:** User experiences smooth loading without jarring blank pages.

### Flow 7: Button loading state
1. User edits trip and clicks "Save Draft" button
2. Button text changes to "Saving..."
3. Spinner appears in button
4. Button disabled to prevent double-click
5. Save completes after 1 second
6. Button returns to "Save Draft" text
7. Success indicator appears: "Draft saved"

**Expected outcome:** User knows action is processing and cannot accidentally submit twice.

### Flow 8: User views error details
1. User encounters API failure
2. Inline error banner appears with generic message
3. User clicks "Show Details" link
4. Error details expand showing:
   - Error Code: API_TIMEOUT
   - Timestamp: 2024-04-15 14:32:18
   - Request ID: req_abc123xyz
5. User clicks "Copy Error Details" button
6. Details copied to clipboard
7. User can paste into support email

**Expected outcome:** Technical users or support staff can access diagnostic information.

### Flow 9: Network offline warning
1. User actively using app with internet connection
2. Internet connection drops
3. Banner appears at top: "You're offline. Some features may not work."
4. User can still view cached content
5. User attempts to create new trip (requires network)
6. Action fails with error: "Unable to save. Please check your connection."
7. Internet connection restored
8. Offline banner automatically disappears

**Expected outcome:** User is aware of connectivity issues and understands limitations.

## Done When

- [ ] 404 page renders without app shell with illustration and navigation buttons
- [ ] 500 page renders without app shell with retry functionality
- [ ] Inline error banner displays for API failures within app shell
- [ ] Error banner includes error icon, message, Retry button, and Dismiss button
- [ ] Validation errors show red borders and error messages on form fields
- [ ] Real-time validation clears errors as user corrects input
- [ ] Summary error banner lists all validation issues at top of form
- [ ] Report generation progress modal blocks navigation and shows progress bar
- [ ] Progress stages update status (pending → in-progress → completed)
- [ ] Progress percentage advances from 0% to 100%
- [ ] Skeleton screens display with shimmer animation during page loads
- [ ] Button loading states show spinner and disable button
- [ ] Error details toggle reveals technical information (error code, timestamp, request ID)
- [ ] "Copy Error Details" button copies tech info to clipboard
- [ ] Network offline warning banner appears when connection is lost
- [ ] Offline banner auto-dismisses when connection restored
- [ ] All error states support light and dark mode
- [ ] Mobile layouts work for all error and loading components
- [ ] Tests cover 404, 500, API failures, validation errors, loading states, and offline scenarios
- [ ] Visual appearance matches screenshots in section directory
