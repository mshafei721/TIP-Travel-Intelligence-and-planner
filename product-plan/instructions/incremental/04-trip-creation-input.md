# Milestone 4: Trip Creation & Input

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

This milestone implements the multi-step wizard that captures all information needed to generate a comprehensive travel intelligence report. This is the most complex form in the application, with progressive disclosure, auto-save, and multi-city support.

## Overview

Key functionality in this section:

- Multi-step wizard with 4 main steps (Traveler Details, Destination, Trip Details, Preferences)
- Custom progressive logic that shows/hides steps based on user inputs
- Auto-save draft functionality at each step
- Multi-city trip support with dynamic destination fields
- Trip summary confirmation page before report generation
- Template pre-fill capability
- Real-time validation with error messages

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/trip-creation-input/components/`

Build the following components based on the provided references:

- **TripCreationWizard.tsx** — Main wizard container with step management
- **StepIndicator.tsx** — Visual progress indicator (1/4, 2/4, etc.)
- **ProgressBar.tsx** — Horizontal progress bar showing percentage
- **Step1TravelerDetails.tsx** — Name, email, nationality, residence, party size, contact preferences
- **Step2Destination.tsx** — Destination search, multi-city toggle, additional destinations
- **Step3TripDetails.tsx** — Travel dates, budget, trip purpose
- **Step4Preferences.tsx** — Travel style, interests, dietary restrictions, accessibility needs
- **TripSummary.tsx** — Review page showing all entered data with edit buttons
- **AutoSaveIndicator.tsx** — "Draft saved" message component
- **TemplateSelector.tsx** — Modal for selecting saved templates
- **NavigationButtons.tsx** — Back, Next, Submit buttons

### 2. Data Layer

**Files:** `sections/trip-creation-input/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface TripFormData {
  travelerDetails: TravelerDetails;
  destinations: Destination[];
  tripDetails: TripDetails;
  preferences: TripPreferences;
}

interface TravelerDetails {
  name: string;
  email: string;
  age?: number;
  nationality: string;
  residenceCountry: string;
  originCity: string;
  residencyStatus: string;
  partySize: number;
  partyAges?: number[];
  contactPreferences: string[];
}

interface Destination {
  country: string;
  city: string;
}

interface TripDetails {
  departureDate: string;
  returnDate: string;
  budget: number;
  currency: string;
  tripPurpose: string;
}

interface TripPreferences {
  travelStyle: 'relaxed' | 'balanced' | 'packed' | 'budget-focused';
  interests: string[];
  dietaryRestrictions: string[];
  accessibilityNeeds?: string;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onStepComplete(step: number, data: Partial<TripFormData>): void` — Save draft at each step
- `onSubmit(data: TripFormData): Promise<void>` — Final submission from summary page
- `onLoadTemplate(templateId: string): void` — Pre-fill form with template data
- `onEditFromSummary(step: number): void` — Return to specific step from summary

### 4. Validation Rules

Implement real-time validation for:

- **Email format:** Valid email address required
- **Dates:** Return date must be after departure date
- **Budget:** Must be positive number
- **Required fields:** Name, email, nationality, residence, destination, dates, budget, trip purpose, travel style
- **Party size:** Must be integer ≥ 1
- **Party ages:** Required if party size > 1

Display validation errors inline with red borders and error messages.

### 5. Progressive Logic

Show/hide steps dynamically:

- If party size = 1, skip party ages field
- If single destination selected, simplify Step 2
- If multi-city enabled, show additional destination input fields with add/remove buttons

### 6. Auto-Save Behavior

- Save draft after each step completion
- Show "Draft saved" indicator (3-second fade)
- Store draft in local storage or backend
- Resume from last step on return

## Files to Reference

- `sections/trip-creation-input/spec.md` — Complete specification
- `sections/trip-creation-input/README.md` — Implementation guide
- `sections/trip-creation-input/types.ts` — TypeScript interfaces
- `sections/trip-creation-input/sample-data.json` — Example form data
- `sections/trip-creation-input/components/` — Reference components
- `sections/trip-creation-input/*.png` — Screenshots
- `sections/trip-creation-input/tests.md` — Test instructions

## Expected User Flows

### Flow 1: User creates a single-destination trip
1. User navigates to `/trips/create`
2. Step 1 displays with traveler details form
3. User enters name, email, selects nationality (United States), residence (United States), origin city (New York), residency status (Citizen), party size (1)
4. User clicks "Next"
5. "Draft saved" indicator appears
6. Step 2 displays with destination search
7. User searches for "Tokyo, Japan" and selects it
8. User clicks "Next" (multi-city toggle remains off)
9. Step 3 displays with trip details
10. User selects dates (departure: Apr 1, 2024, return: Apr 10, 2024), enters budget (3000 USD), selects trip purpose (Tourism)
11. User clicks "Next"
12. Step 4 displays with preferences
13. User selects travel style (Balanced), interests (Food, Culture, Museums), no dietary restrictions
14. User clicks "Submit"
15. Trip summary page displays all entered information organized by section
16. User reviews and clicks "Confirm & Generate Report"
17. Redirected to report generation loading screen

**Expected outcome:** User successfully creates trip and proceeds to report generation.

### Flow 2: User creates a multi-city trip
1. User completes Step 1 (Traveler Details)
2. Navigates to Step 2 (Destination)
3. Enters first destination: "Paris, France"
4. Toggles "Multi-city trip" option
5. Second destination field appears
6. Enters "Rome, Italy"
7. Clicks "Add destination" button
8. Third destination field appears
9. Enters "Barcelona, Spain"
10. Clicks "Next"
11. Continues through Steps 3 and 4
12. Summary page shows all three destinations

**Expected outcome:** Multi-city trip is captured with all destinations stored.

### Flow 3: User edits from summary page
1. User completes all steps and reaches trip summary
2. Reviews traveler details section
3. Notices incorrect nationality selected
4. Clicks "Edit" button next to Traveler Details section
5. Returns to Step 1 with all previous data pre-filled
6. Changes nationality to correct value
7. Clicks "Next" through steps (data preserved)
8. Returns to summary page
9. Sees updated nationality

**Expected outcome:** User can edit specific sections without losing other data.

### Flow 4: User saves draft and returns later
1. User starts trip creation, completes Step 1 and Step 2
2. Closes browser or navigates away
3. Returns to `/trips/create` later
4. Wizard loads with Step 3 (last incomplete step)
5. Previous data from Steps 1 and 2 is pre-filled
6. User completes Steps 3 and 4
7. Submits trip successfully

**Expected outcome:** Draft auto-save allows users to resume without re-entering data.

### Flow 5: User starts from template
1. User clicks "Use Saved Template" on dashboard or trip creation page
2. Template selector modal opens
3. User sees list of saved templates: "Weekend Getaway", "Business Trip", "Family Vacation"
4. User selects "Weekend Getaway" template
5. Wizard loads with all fields pre-filled from template
6. User modifies destination and dates
7. Continues through wizard and submits

**Expected outcome:** Templates speed up trip creation for recurring patterns.

## Done When

- [ ] Wizard renders with step indicator showing current step (1/4, 2/4, etc.)
- [ ] Progress bar displays completion percentage across steps
- [ ] Step 1 includes all traveler detail fields with dropdowns for nationality, residence, residency status
- [ ] Step 2 includes destination search with autocomplete
- [ ] Multi-city toggle shows/hides additional destination fields
- [ ] Add/remove destination buttons work correctly
- [ ] Step 3 includes date pickers, budget input with currency selector, trip purpose dropdown
- [ ] Step 4 includes travel style radio buttons, interests checkboxes, dietary restrictions checkboxes
- [ ] "Draft saved" indicator appears after each step completion
- [ ] Back button navigates to previous step with data preserved
- [ ] Next button validates current step before advancing
- [ ] Trip summary page displays all entered data organized by section
- [ ] Edit buttons on summary page return to specific steps
- [ ] Confirm & Generate Report button submits final data
- [ ] Real-time validation displays error messages for invalid fields
- [ ] Required field indicators show which fields must be completed
- [ ] Progressive logic hides party ages field if party size = 1
- [ ] Template selector modal displays saved templates
- [ ] Form resumes from last step on return (draft recovery)
- [ ] Mobile layout uses single column with large touch targets
- [ ] Light and dark mode styles work across all steps
- [ ] Tests cover all steps, validation, multi-city, templates, draft saving, and editing
- [ ] Visual appearance matches screenshots in section directory
