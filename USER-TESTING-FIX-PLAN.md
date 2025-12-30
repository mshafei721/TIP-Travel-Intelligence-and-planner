# User Testing Issues - Fix Plan

## Executive Summary
This document contains the investigation results and fix plan for 13 user testing issues discovered during testing. Each issue is analyzed with root cause, affected files, and proposed fix.

---

## Issue 1: Dashboard Text Not Centered

### Problem
The sentence "Start planning your next adventure with AI-powered travel intelligence..." is not centered on the dashboard empty state.

### Root Cause
The paragraph element has `max-w-md` constraint but lacks `mx-auto` for horizontal centering.

### Affected Files
- `frontend/components/dashboard/EmptyState.tsx` (lines 42-46)

### Fix
```tsx
// Before (line 42):
<p className="mb-6 max-w-md text-slate-600 dark:text-slate-400">

// After:
<p className="mb-6 mx-auto max-w-md text-slate-600 dark:text-slate-400">
```

### Complexity: Low | Priority: Medium

---

## Issue 2: "Create Your First Trip" Button Not Routing

### Problem
The "Create Your First Trip" button on the dashboard empty state doesn't navigate to the trip creation form.

### Root Cause
The `EmptyState` component calls `onCreateTrip?.()` but is instantiated in `page.tsx` without passing this callback prop. Unlike `QuickActionsCard` which uses `useRouter` as fallback, `EmptyState` silently fails.

### Affected Files
- `frontend/components/dashboard/EmptyState.tsx` (lines 1-14)

### Fix
Add router fallback navigation:
```tsx
// Add import at top:
import { useRouter } from 'next/navigation';

// Inside component:
const router = useRouter();

const handleClick = () => {
  analytics.createTripStart('empty_state');
  if (onCreateTrip) {
    onCreateTrip();
  } else {
    router.push('/trips/create');  // Fallback navigation
  }
};
```

### Complexity: Low | Priority: High

---

## Issue 3: App Shell Shows "Demo User" Instead of Authenticated User

### Problem
The user menu in the top right corner shows "Demo User" instead of the actual authenticated user's name.

### Root Cause
In `frontend/app/(app)/layout.tsx` (lines 18-22), the user is hardcoded as a mock object:
```tsx
const mockUser = {
  name: 'Demo User',
};
```

### Affected Files
- `frontend/app/(app)/layout.tsx` (lines 18-33)

### Fix
Integrate Supabase authentication to get real user data:
```tsx
'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { AppShell } from '@/components/shell';
// ... other imports

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<{ name: string; avatarUrl?: string } | null>(null);

  useEffect(() => {
    const supabase = createClient();

    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        setUser({
          name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'User',
          avatarUrl: user.user_metadata?.avatar_url,
        });
      }
    };

    getUser();
  }, []);

  const handleLogout = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    window.location.href = '/login';
  };

  return (
    <AppShell navigationItems={navigationItems} user={user || undefined} onLogout={handleLogout}>
      {children}
    </AppShell>
  );
}
```

### Complexity: Medium | Priority: High

---

## Issue 4: My Trips Page - Create Trip Opens Outside App Shell

### Problem
Clicking "Create Your First Trip" button in My Trips page navigates outside the app shell layout.

### Root Cause
Navigation to `/trips/create` works correctly - the issue is that the trip creation wizard is styled as a standalone page with its own full-screen layout (`min-h-screen bg-gradient-to-br...`).

### Affected Files
- `frontend/components/trip-wizard/TripCreationWizard.tsx` (line 259)

### Fix
Option A: Modify TripCreationWizard to remove standalone layout styling
Option B: Create a modal/slideout version for in-app creation
Option C: Accept this as designed behavior (standalone experience for complex form)

Recommended: Option A - Remove `min-h-screen` and background styles, let parent layout control:
```tsx
// Change line 259 from:
<div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-amber-50/20 dark:from-slate-950 dark:via-slate-900 dark:to-slate-900">

// To:
<div className="py-8">
```

### Complexity: Low | Priority: Medium

---

## Issue 5: Traveler Age Inputs Should Be Dropdowns

### Problem
When party size > 1, additional traveler ages use text inputs instead of dropdowns with age categories (including infant <2).

### Root Cause
Current implementation uses `<input type="number">` for ages (lines 308-316 in `Step1TravelerDetails.tsx`).

### Affected Files
- `frontend/components/trip-wizard/Step1TravelerDetails.tsx` (lines 299-320)
- `frontend/components/trip-wizard/TripCreationWizard.tsx` (type definition)

### Fix
Replace number inputs with select dropdowns:
```tsx
const AGE_CATEGORIES = [
  { value: 0, label: 'Infant (< 2 years)' },
  { value: 2, label: 'Child (2-12 years)' },
  { value: 13, label: 'Teen (13-17 years)' },
  { value: 18, label: 'Adult (18-64 years)' },
  { value: 65, label: 'Senior (65+ years)' },
];

// Replace the input with:
<select
  value={age}
  onChange={(e) => updatePartyAge(index, parseInt(e.target.value))}
  className="w-full px-3 py-2 rounded-lg border..."
>
  <option value="">Select age range...</option>
  {AGE_CATEGORIES.map((cat) => (
    <option key={cat.value} value={cat.value}>{cat.label}</option>
  ))}
</select>
```

### Complexity: Low | Priority: Medium

---

## Issue 6: Destination Country/City Dropdowns with Search

### Problem
Not all countries are available, and cities should be a dropdown based on selected country with search capabilities.

### Root Cause
- Countries list is hardcoded with only 50 countries (lines 12-63 in `Step1TravelerDetails.tsx`)
- City is a text input, not a searchable dropdown
- No country-city relationship

### Affected Files
- `frontend/components/trip-wizard/Step1TravelerDetails.tsx` (COUNTRIES array)
- `frontend/components/trip-wizard/Step2Destination.tsx`

### Fix
1. Use a comprehensive countries library (e.g., `country-state-city` npm package)
2. Implement a searchable select component (e.g., react-select or Radix Combobox)
3. Create API endpoint or static data for cities by country

```tsx
// Install: npm install country-state-city react-select

import { Country, City } from 'country-state-city';
import Select from 'react-select';

const countries = Country.getAllCountries().map(c => ({
  value: c.isoCode,
  label: c.name
}));

const getCitiesForCountry = (countryCode: string) => {
  return City.getCitiesOfCountry(countryCode)?.map(c => ({
    value: c.name,
    label: c.name
  })) || [];
};
```

### Complexity: High | Priority: High

---

## Issue 7: Multiple Trip Purpose Selection

### Problem
User should be able to select more than one trip purpose.

### Root Cause
Current implementation uses single-select with `tripPurpose: string` type.

### Affected Files
- `frontend/components/trip-wizard/TripCreationWizard.tsx` (TripDetails interface, line 48)
- `frontend/components/trip-wizard/Step3TripDetails.tsx` (selection logic, lines 214-230)
- `frontend/lib/validation/trip-wizard-schemas.ts`

### Fix
1. Change type from `tripPurpose: string` to `tripPurposes: string[]`
2. Update Step3TripDetails to handle multiple selections:
```tsx
// Change type definition:
tripPurposes: ('Tourism' | 'Business' | 'Education' | 'Family Visit' | 'Medical' | 'Other')[];

// Toggle function:
const togglePurpose = (purpose: string) => {
  const current = data.tripPurposes || [];
  const isSelected = current.includes(purpose);
  const newPurposes = isSelected
    ? current.filter(p => p !== purpose)
    : [...current, purpose];
  updateField('tripPurposes', newPurposes);
};

// Button className:
className={`... ${data.tripPurposes?.includes(purpose.value) ? 'border-blue-600 bg-blue-50' : '...'}`}
```

### Complexity: Medium | Priority: Medium

---

## Issue 8: "Failed to Create Trip" Error

### Problem
Clicking "Confirm & Generate Report" shows "Failed to create trip" error.

### Root Cause
The trip wizard POSTs to `/api/trips` (line 229 in TripCreationWizard.tsx), but:
1. No API route exists at `frontend/app/api/trips/route.ts`
2. Backend expects different field names/format
3. Missing authentication headers in fetch call

### Affected Files
- `frontend/components/trip-wizard/TripCreationWizard.tsx` (handleSubmit, lines 211-253)
- Need to create: `frontend/app/api/trips/route.ts`

### Fix
Option A: Create Next.js API route to proxy to backend:
```tsx
// frontend/app/api/trips/route.ts
import { NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await request.json();

  // Transform frontend format to backend format
  const tripData = {
    destination_city: body.destinations[0]?.city,
    destination_country: body.destinations[0]?.country,
    departure_date: body.tripDetails.departureDate,
    return_date: body.tripDetails.returnDate,
    budget: body.tripDetails.budget,
    // ... map other fields
  };

  // Forward to backend or insert directly to Supabase
  const { data, error } = await supabase.from('trips').insert(tripData).select().single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json(data);
}
```

### Complexity: High | Priority: Critical

---

## Issue 9: Profile Page Failed to Load

### Problem
Profile page fails to load.

### Root Cause
The profile page (line 34 in `app/(app)/profile/page.tsx`) calls `getProfile()` which makes API request to backend. If:
1. Backend is not running
2. API endpoint doesn't exist
3. Authentication token is missing/invalid

The page throws an error (line 82).

### Affected Files
- `frontend/app/(app)/profile/page.tsx` (lines 32-83)
- `frontend/lib/api/profile.ts`

### Fix
1. Add proper error boundary with fallback UI
2. Ensure backend profile endpoint is running
3. Add loading state for better UX
4. Consider client-side data fetching with SWR/React Query for better error handling

```tsx
// Wrap in try-catch with user-friendly error:
try {
  const [profileResponse, templates] = await Promise.all([...]);
  // ...
} catch (error) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-6">
      <h2>Failed to load profile</h2>
      <p>Please check your connection and try again.</p>
      <button onClick={() => window.location.reload()}>Retry</button>
    </div>
  );
}
```

### Complexity: Medium | Priority: High

---

## Issue 10: Settings Toggles Not Working (Toast Shows Success)

### Problem
Settings toggles don't visually toggle but toast messages show "saved setting".

### Root Cause
The `SettingsToggle` component (lines 21-23) correctly calls `onChange(!checked)`, but the issue is in the parent page's `saveSettings` function. When `updateAllSettings` API call fails or returns different data, the UI state doesn't update properly.

Checking `SettingsSelect` and `SettingsToggle` - they rely on `settings` state which is updated after API response (line 64). If API fails or returns unexpected format, the state isn't updated but toast is shown.

### Affected Files
- `frontend/app/(app)/settings/page.tsx` (lines 55-74)
- `frontend/lib/api/settings.ts`

### Fix
1. Ensure optimistic UI update before API call
2. Rollback on failure
```tsx
const saveSettings = async (updates) => {
  // Optimistic update
  const previousSettings = settings;
  setSettings(prev => ({ ...prev, ...mergeDeep(prev, updates) }));

  setSaveStatus('saving');
  try {
    const response = await updateAllSettings(updates);
    setSettings(response.data);  // Confirm with server response
    setSaveStatus('saved');
    toast.success('Settings saved successfully');
  } catch (err) {
    // Rollback on failure
    setSettings(previousSettings);
    setSaveStatus('error');
    toast.error('Failed to save settings');
  }
};
```

### Complexity: Medium | Priority: Medium

---

## Issue 11: Dark Mode / Light Mode Not Changing

### Problem
Toggling dark/light mode in settings does nothing.

### Root Cause
Multiple issues:
1. No `ThemeProvider` wrapping the app
2. Settings page calls `saveSettings({ appearance: { theme } })` but doesn't apply theme to DOM
3. Tailwind dark mode requires class on `<html>` element but nothing updates it

### Affected Files
- `frontend/app/layout.tsx` (needs ThemeProvider)
- `frontend/app/(app)/settings/page.tsx` (lines 156-164)
- Need to create: Theme context/provider

### Fix
1. Install next-themes: `npm install next-themes`
2. Create ThemeProvider wrapper:
```tsx
// frontend/components/providers/ThemeProvider.tsx
'use client';
import { ThemeProvider as NextThemesProvider } from 'next-themes';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </NextThemesProvider>
  );
}
```
3. Wrap app in layout.tsx
4. In settings, call `setTheme()` from next-themes:
```tsx
import { useTheme } from 'next-themes';

const { setTheme } = useTheme();

// In SettingsSelect onChange:
onChange={(theme) => {
  setTheme(theme);  // Apply immediately
  saveSettings({ appearance: { theme } });  // Persist to backend
}}
```

### Complexity: Medium | Priority: Medium

---

## Issue 12: Trip Drafts Not Saving to My Trips Page

### Problem
When navigating back to create trip, the last step shows but drafts aren't visible in My Trips.

### Root Cause
Drafts are saved to `localStorage` (line 129 in TripCreationWizard.tsx) but never synced to database or shown in My Trips. My Trips page only shows trips from Supabase database.

### Affected Files
- `frontend/components/trip-wizard/TripCreationWizard.tsx` (lines 123-132)
- `frontend/app/(app)/trips/page.tsx`

### Fix
Option A: Add "Drafts" section to My Trips page:
```tsx
// In trips/page.tsx
const [drafts, setDrafts] = useState<Draft[]>([]);

useEffect(() => {
  const savedDraft = localStorage.getItem('trip-wizard-draft');
  if (savedDraft) {
    setDrafts([JSON.parse(savedDraft)]);
  }
}, []);

// Render drafts section with "Continue editing" button
```

Option B: Save drafts to database with `status: 'draft'`:
```tsx
// In TripCreationWizard saveDraft:
const saveDraft = async () => {
  const supabase = createClient();
  await supabase.from('trips').upsert({
    id: draftId,
    status: 'draft',
    data: formData,
    // ...
  });
};
```

### Complexity: Medium | Priority: Low

---

## Issue 13: History Page Map Not Loading

### Problem
History page shows boxes instead of a map.

### Root Cause
The `WorldMapViz` component uses a simplified SVG with hardcoded country paths (rectangles). It's not a real map library integration - just placeholder geometry representing countries as colored boxes.

### Affected Files
- `frontend/components/history/WorldMapViz.tsx` (lines 8-54, 122-170)

### Fix
Option A: Accept current simplified visualization (it works as designed)
Option B: Integrate proper map library:
```tsx
// Install: npm install react-simple-maps @types/topojson-specification

import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

export function WorldMapViz({ countries }) {
  return (
    <ComposableMap>
      <Geographies geography={geoUrl}>
        {({ geographies }) =>
          geographies.map((geo) => {
            const isVisited = countries.some(c => c.country_code === geo.properties.iso_a2);
            return (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill={isVisited ? '#3b82f6' : '#e2e8f0'}
              />
            );
          })
        }
      </Geographies>
    </ComposableMap>
  );
}
```

### Complexity: Medium | Priority: Low

---

## Priority Matrix

| Priority | Issue # | Description |
|----------|---------|-------------|
| Critical | 8 | Trip creation fails - blocks core functionality |
| High | 2 | Button doesn't route - poor UX |
| High | 3 | Demo user shown - unprofessional |
| High | 6 | Countries/cities missing - incomplete data |
| High | 9 | Profile fails to load - broken page |
| Medium | 1 | Text not centered - visual polish |
| Medium | 4 | Navigation outside shell - UX consistency |
| Medium | 5 | Age dropdowns - UX improvement |
| Medium | 7 | Multi-select purpose - feature enhancement |
| Medium | 10 | Toggles not working - broken feature |
| Medium | 11 | Theme not changing - broken feature |
| Low | 12 | Drafts not shown - nice-to-have |
| Low | 13 | Map boxes - acceptable for MVP |

---

## Recommended Fix Order

1. **Issue 8**: Trip creation error (Critical - unblocks core flow)
2. **Issue 2**: Dashboard button routing (High - quick fix)
3. **Issue 3**: Demo user replacement (High - visible issue)
4. **Issue 9**: Profile page loading (High - broken page)
5. **Issue 1**: Text centering (Quick win)
6. **Issue 10 + 11**: Settings & theme (Combined - related issues)
7. **Issue 5**: Age dropdowns (Medium)
8. **Issue 7**: Multi-select purpose (Medium)
9. **Issue 6**: Countries/cities (Requires research)
10. **Issue 4**: Trip wizard layout (Design decision)
11. **Issue 12**: Draft saving (Enhancement)
12. **Issue 13**: Map improvement (Enhancement)

---

## Estimated Effort

- **Quick Fixes (< 30 min each)**: Issues 1, 2, 5
- **Medium (1-2 hours each)**: Issues 3, 4, 7, 9, 10, 11, 12
- **Complex (2-4 hours each)**: Issues 6, 8, 13
