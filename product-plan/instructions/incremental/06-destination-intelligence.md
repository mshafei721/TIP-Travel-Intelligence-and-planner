# Milestone 6: Destination Intelligence

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

This milestone implements the comprehensive destination information section that provides travelers with essential knowledge about their destination. Information is organized in an interactive card-based grid where each card expands to reveal detailed content.

## Overview

Key functionality in this section:

- Interactive card-based grid layout (2-3 columns desktop, 1 column mobile)
- Seven information cards: Country Overview, Weather, Currency & Costs, Cultural Norms, Unusual Laws, Safety & Security, Latest News
- Cards expand in place to show detailed content
- Animated weather visuals with daily forecasts scoped to visit dates
- Packing recommendations based on weather
- External links to official sources within expanded cards

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/destination-intelligence/components/`

Build the following components based on the provided references:

- **DestinationIntelligencePage.tsx** — Main page with card grid layout
- **IntelligenceCard.tsx** — Reusable card component with expand/collapse behavior
- **CountryOverviewCard.tsx** — Capital, language, population, timezone, political system
- **WeatherCard.tsx** — Animated weather icons, daily forecasts, best time to visit, packing list
- **CurrencyCard.tsx** — Exchange rates, ATM availability, tipping customs, cost of living
- **CultureCard.tsx** — Dress codes, greetings, customs, dos and don'ts, etiquette
- **UnusualLawsCard.tsx** — Country-specific legal restrictions travelers should know
- **SafetyCard.tsx** — Safety alerts, crime rates, emergency numbers, health risks
- **NewsCard.tsx** — Recent relevant news about the destination
- **LoadingState.tsx** — Card skeletons while loading

### 2. Data Layer

**Files:** `sections/destination-intelligence/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface DestinationIntelligence {
  countryOverview: CountryOverview;
  weather: WeatherForecast;
  currency: CurrencyInfo;
  culture: CulturalNorms;
  laws: UnusualLaws;
  safety: SafetyInfo;
  news: NewsItem[];
}

interface WeatherForecast {
  dailyForecasts: DailyForecast[];
  bestTimeToVisit: string;
  packingRecommendations: string[];
}

interface DailyForecast {
  date: string;
  tempHigh: number;
  tempLow: number;
  condition: 'sunny' | 'rainy' | 'cloudy' | 'snowy' | 'windy';
  precipitationChance: number;
}

interface CurrencyInfo {
  exchangeRate: number;
  atmAvailability: string;
  tippingCustoms: string;
  costOfLivingEstimate: string;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onCardExpand(cardId: string): void` — Track which card is expanded
- `onCardCollapse(cardId: string): void` — Track when card is collapsed
- `onExternalLinkClick(url: string): void` — Open external source in new tab

### 4. Card Interaction Behavior

- Cards display in collapsed state initially (title + icon only)
- Click anywhere on card to expand
- Expanded card shows full content below card header
- Click again to collapse
- Smooth expand/collapse animations (300ms)
- Only one card expanded at a time (optional, or allow multiple)

### 5. Weather Card Features

- Animated weather icons matching forecast condition
- Daily temperature range (high/low) for each day of visit
- Precipitation percentage for each day
- "Best time to visit" recommendation
- Packing list based on weather (e.g., "Bring umbrella, light jacket, comfortable walking shoes")

### 6. Loading States

- Card skeletons with shimmer animation
- Cards load independently
- Show skeleton until data is available

## Files to Reference

- `sections/destination-intelligence/spec.md` — Complete specification
- `sections/destination-intelligence/README.md` — Implementation guide
- `sections/destination-intelligence/types.ts` — TypeScript interfaces
- `sections/destination-intelligence/sample-data.json` — Example destination data
- `sections/destination-intelligence/components/` — Reference components
- `sections/destination-intelligence/*.png` — Screenshots
- `sections/destination-intelligence/tests.md` — Test instructions

## Expected User Flows

### Flow 1: User explores country overview
1. User navigates to destination intelligence section
2. Sees card grid with 7 cards in collapsed state
3. Each card shows title and icon (e.g., "Country Overview" with flag icon)
4. User clicks "Country Overview" card
5. Card expands smoothly, revealing content:
   - Capital: Tokyo
   - Language: Japanese
   - Population: 125 million
   - Timezone: JST (UTC+9)
   - Political System: Constitutional Monarchy
6. Links to official government and tourism websites at bottom
7. User clicks on card again to collapse

**Expected outcome:** User quickly accesses basic country information.

### Flow 2: User views weather forecast
1. User clicks "Weather" card
2. Card expands showing animated weather icons
3. Daily forecast displays for entire trip duration (7 days):
   - Day 1: Sunny, 72°F high, 58°F low, 10% precipitation
   - Day 2: Rainy, 68°F high, 55°F low, 80% precipitation
   - Day 3: Cloudy, 70°F high, 56°F low, 30% precipitation
   - (continues for all days)
4. "Best time to visit" section shows: "March-May (Spring) and September-November (Fall)"
5. Packing recommendations: "Bring umbrella, light jacket, layers, comfortable walking shoes"
6. User sees clear weather patterns for their specific travel dates

**Expected outcome:** User knows exactly what weather to expect and what to pack.

### Flow 3: User learns cultural norms
1. User clicks "Cultural Norms" card
2. Card expands showing:
   - Dress code: "Modest dress expected at temples and shrines. Remove shoes when entering homes."
   - Greetings: "Bow as greeting. Handshakes less common but acceptable for foreigners."
   - Customs: "Gift-giving is important. Present and receive gifts with both hands."
   - Dos and Don'ts: "Do: Learn basic Japanese phrases. Don't: Tip (considered rude)."
3. Links to cultural etiquette guides at bottom
4. User now understands local expectations

**Expected outcome:** User is prepared to behave respectfully in the destination.

### Flow 4: User checks unusual laws
1. User clicks "Unusual Laws" card
2. Card expands showing country-specific legal restrictions:
   - "Dancing in clubs without a license is technically illegal"
   - "Possession of certain over-the-counter medications (e.g., cold medicine with pseudoephedrine) is prohibited"
   - "Using VPNs is restricted in some cases"
3. Links to official legal resources
4. User is aware of potential legal issues

**Expected outcome:** User avoids unintentional legal violations.

### Flow 5: User reviews safety information
1. User clicks "Safety & Security" card
2. Card expands showing:
   - Safety alert: "Low crime rate. Very safe for travelers."
   - Crime rates: "Petty theft is rare. Violent crime is extremely rare."
   - Emergency numbers: "Police: 110, Fire/Ambulance: 119"
   - Health risks: "No major health risks. Tap water is safe to drink."
3. Links to government travel advisories
4. User feels confident about safety

**Expected outcome:** User understands safety situation and has emergency contacts.

### Flow 6: User reads latest news
1. User clicks "Latest News" card
2. Card expands showing 3-5 recent news items relevant to travelers
3. Each item includes headline, brief summary, date, and link to full article
4. Example: "Japan Reopens Borders to International Tourists - May 2024"
5. User clicks on news item link to read full article

**Expected outcome:** User is aware of recent developments that may affect their trip.

## Done When

- [ ] Card grid layout displays 7 cards (2-3 columns desktop, 1 column mobile)
- [ ] All cards render in collapsed state initially with title and icon
- [ ] Click on card expands it smoothly to show full content
- [ ] Click again collapses card back to initial state
- [ ] Country Overview card shows capital, language, population, timezone, political system
- [ ] Weather card displays animated weather icons matching forecast conditions
- [ ] Weather card shows daily temperature ranges and precipitation for entire trip
- [ ] Weather card includes "Best time to visit" and packing recommendations
- [ ] Currency card shows exchange rates, ATM info, tipping customs, cost of living
- [ ] Culture card displays dress codes, greetings, customs, dos and don'ts
- [ ] Unusual Laws card lists country-specific legal restrictions
- [ ] Safety card shows safety alerts, crime rates, emergency numbers, health risks
- [ ] News card displays 3-5 recent relevant news items with links
- [ ] External links within cards open in new tabs
- [ ] Loading states show card skeletons while data loads
- [ ] Cards load independently without blocking each other
- [ ] Mobile layout stacks cards vertically with proper touch interactions
- [ ] Light and dark mode styles work across all cards
- [ ] Tests cover card expand/collapse, content display, external links, and loading states
- [ ] Visual appearance matches screenshots in section directory
