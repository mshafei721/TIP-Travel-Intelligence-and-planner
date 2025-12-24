# Milestone 5: Visa & Entry Intelligence

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

This milestone implements the critical visa and entry requirements section. This is the most important section in TIP, as visa misinformation can have serious legal and financial consequences for travelers. Accuracy and clear source attribution are paramount.

## Overview

Key functionality in this section:

- Comprehensive visa requirements display (visa type, stay duration, application process)
- Entry conditions (passport validity, vaccinations)
- Transit requirements for layovers
- Processing times from official sources
- Color-coded confidence indicators (green=official, yellow=third-party, gray=uncertain)
- Links to official embassy and government websites
- Warning banners for partial or missing information

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/visa-entry-intelligence/components/`

Build the following components based on the provided references:

- **VisaRequirementsPage.tsx** — Main page container
- **VisaRequirementsSection.tsx** — Visa type, stay duration, application process, required documents
- **EntryConditionsSection.tsx** — Passport validity, vaccinations, other entry conditions
- **TransitRequirementsSection.tsx** — Visa requirements for layovers
- **ProcessingTimesSection.tsx** — Estimated visa processing duration
- **ConfidenceBadge.tsx** — Color-coded trust indicator (green/yellow/gray)
- **SourceLinks.tsx** — Clickable links to official sources
- **PartialDataWarning.tsx** — Banner for missing or uncertain information
- **LoadingState.tsx** — Skeleton screen while fetching visa data

### 2. Data Layer

**Files:** `sections/visa-entry-intelligence/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface VisaRequirement {
  visaType: string; // e.g., "Tourist Visa", "eVisa", "Visa-Free"
  maxStayDuration: string; // e.g., "90 days"
  applicationProcess: string;
  requiredDocuments: string[];
  processingTime?: string;
  confidenceLevel: 'official' | 'third-party' | 'uncertain';
  sources: SourceReference[];
}

interface EntryConditions {
  passportValidity: string; // e.g., "Must be valid for 6 months beyond stay"
  vaccinations: string[];
  otherRequirements: string[];
}

interface TransitRequirements {
  required: boolean;
  details: string;
  sources: SourceReference[];
}

interface SourceReference {
  name: string;
  url: string;
  type: 'government' | 'embassy' | 'third-party';
  lastVerified: string;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onSourceClick(url: string): void` — Open official source link in new tab
- `onContactEmbassy(): void` — Show embassy contact information modal

### 4. Confidence Indicators

Display color-coded badges:

- **Green (official):** Data from government or embassy sources (e.g., "Official Source")
- **Yellow (third-party):** Data from trusted third-party sources (e.g., "Third-Party Source")
- **Gray (uncertain):** Incomplete or unverified data (e.g., "Uncertain")

Apply badge to entire section or individual requirements.

### 5. Warning Banners

When data is partial or missing:

- Display prominent warning banner at top of section
- Message: "We couldn't find complete visa information for this destination. Please verify requirements with the embassy."
- Include "Contact Embassy" button in banner
- Show partial data below with gray confidence badge

### 6. Loading States

- Skeleton screens with shimmer animation while fetching data
- Separate skeletons for each section (visa, entry, transit, processing)
- Load sections independently (don't wait for all data)

## Files to Reference

- `sections/visa-entry-intelligence/spec.md` — Complete specification
- `sections/visa-entry-intelligence/README.md` — Implementation guide
- `sections/visa-entry-intelligence/types.ts` — TypeScript interfaces
- `sections/visa-entry-intelligence/sample-data.json` — Example visa data
- `sections/visa-entry-intelligence/components/` — Reference components
- `sections/visa-entry-intelligence/*.png` — Screenshots
- `sections/visa-entry-intelligence/tests.md` — Test instructions

## Expected User Flows

### Flow 1: User views complete visa requirements
1. User navigates to visa section for their trip
2. Loading state displays with skeleton screens
3. Page loads with four sections: Visa Requirements, Entry Conditions, Transit Requirements, Processing Times
4. Visa Requirements section shows:
   - "Tourist Visa" visa type
   - "90 days" maximum stay
   - Application process description
   - List of required documents (passport, photos, bank statements, flight booking)
   - Green "Official Source" badge
5. Entry Conditions section shows:
   - "Passport must be valid for 6 months beyond stay"
   - No vaccinations required
6. Transit Requirements section shows:
   - "Transit visa not required for stays under 24 hours"
7. Processing Times section shows:
   - "10-15 business days for standard processing"
8. Each section includes clickable links to embassy and government websites

**Expected outcome:** User sees comprehensive, trustworthy visa information with clear source attribution.

### Flow 2: User views partial visa information
1. User navigates to visa section
2. Page loads with warning banner at top
3. Banner displays: "We couldn't find complete visa information for this destination. Please verify requirements with the embassy."
4. Banner includes "Contact Embassy" button
5. Visa Requirements section shows:
   - "eVisa" visa type with gray "Uncertain" badge
   - "Stay duration unknown"
   - Partial application process description
   - Limited required documents list
6. Entry Conditions section shows complete data
7. Transit Requirements section shows "No data available" with gray badge

**Expected outcome:** User is clearly warned about incomplete information and directed to contact embassy.

### Flow 3: User accesses official sources
1. User views visa requirements section
2. Sees green "Official Source" badge
3. Scrolls to bottom of section
4. Sees "Sources:" heading with links
5. Clicks link labeled "U.S. Department of State - Japan Travel Advisory"
6. Link opens in new tab to official government website

**Expected outcome:** User can verify visa information directly from official sources.

### Flow 4: User checks transit requirements
1. User with connecting flight views visa section
2. Scrolls to Transit Requirements section
3. Sees: "Transit visa required for layovers exceeding 8 hours"
4. Sees application process details and required documents
5. Sees link to embassy transit visa page
6. Clicks link and opens official source

**Expected outcome:** User knows whether they need a transit visa for their layover.

## Done When

- [ ] Visa Requirements section displays visa type, stay duration, application process, and required documents
- [ ] Entry Conditions section shows passport validity, vaccinations, and other requirements
- [ ] Transit Requirements section displays transit visa rules
- [ ] Processing Times section shows estimated processing duration
- [ ] Color-coded confidence badges display correctly (green/yellow/gray)
- [ ] Official source links are clickable and open in new tabs
- [ ] Partial data warning banner appears when information is incomplete
- [ ] "Contact Embassy" button opens embassy contact information
- [ ] Loading states show skeleton screens while fetching data
- [ ] Each section loads independently without blocking others
- [ ] Required documents display as bulleted list
- [ ] Source references include source name, URL, type, and last verified date
- [ ] Mobile layout stacks sections vertically with proper spacing
- [ ] Light and dark mode styles work across all sections
- [ ] Tests cover complete data, partial data, missing data, confidence levels, and source links
- [ ] Empty state tests verify behavior when transit requirements don't apply
- [ ] Visual appearance matches screenshots in section directory
