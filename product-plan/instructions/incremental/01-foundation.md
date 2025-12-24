# Milestone 1: Foundation

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

This milestone establishes the technical foundation and visual structure for TIP. You will implement the design system, data model infrastructure, routing, and the complete application shell that wraps all feature sections.

## Overview

In this milestone, you will:

- Set up design tokens (colors, typography) in your chosen CSS framework
- Define TypeScript interfaces for all core entities (User, Trip, Destination, etc.)
- Configure routing structure for all product sections
- Implement the complete application shell with top navigation, user menu, and layout

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in the shell directory for detailed test instructions.

## What to Implement

### 1. Design System Setup

**Files:** `design-system/tokens.css`, `design-system/tailwind-colors.md`, `design-system/fonts.md`

Implement the design tokens from `design-system/`:

- **Colors:**
  - Primary: `blue` (blue-50 through blue-950)
  - Secondary: `amber` (amber-50 through amber-950)
  - Neutral: `slate` (slate-50 through slate-950)
- **Typography:**
  - Heading: `DM Sans`
  - Body: `DM Sans`
  - Mono: `IBM Plex Mono`
- **Google Fonts Import:**
  ```
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=IBM+Plex+Mono:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500;1,600;1,700&display=swap');
  ```

Apply these tokens consistently throughout the application. Use Tailwind's built-in color utility classes:
- Primary actions: `bg-blue-600 hover:bg-blue-700 text-white`
- Secondary actions: `bg-amber-500 hover:bg-amber-600 text-white`
- Neutral backgrounds: `bg-slate-100 dark:bg-slate-800`
- Text: `text-slate-900 dark:text-slate-100`

### 2. Data Model Types

**Files:** `data-model/types.ts`, `data-model/sample-data.json`

Define TypeScript interfaces for all entities described in `data-model/README.md`:

- User
- Trip
- Destination
- AgentJobs
- ReportSections
- VisaRequirement
- Itinerary
- ItineraryItem
- TravelReport
- TravelerProfile
- SourceReference
- FlightOption
- Notification
- DeletionSchedule

Include proper types, optional fields, and relationships. Reference the provided `data-model/types.ts` as a starting point.

### 3. Routing Structure

Configure your router to support all product sections:

- `/` or `/dashboard` — Dashboard & Home
- `/login`, `/signup`, `/forgot-password`, `/reset-password`, `/verify-email` — Authentication pages
- `/trips/create` — Trip Creation & Input
- `/trips/:tripId` — Report Management (trip detail)
- `/trips/:tripId/visa` — Visa & Entry Intelligence
- `/trips/:tripId/destination` — Destination Intelligence
- `/trips/:tripId/itinerary` — Travel Planning & Itinerary
- `/trips` — Report Management (list view)
- `/profile` — User Profile & Settings
- `/404` — Not Found page
- `/500` — Server Error page

Use your framework's routing library (React Router, Next.js App Router, etc.).

### 4. Application Shell

**Files:** `shell/components/AppShell.tsx`, `shell/components/MainNav.tsx`, `shell/components/UserMenu.tsx`

Implement the complete application shell as specified in `shell/spec.md` and shown in `shell/README.md`. The provided components in `shell/components/` serve as a reference implementation.

**Components to build:**

- **AppShell.tsx:**
  - Top navigation bar with blue background (`bg-blue-600`)
  - Left: TIP logo (links to dashboard)
  - Center-left: Main navigation items (My Trips, Create Trip, Profile)
  - Right: User menu (avatar + name + dropdown)
  - Content area below navigation
  - Mobile: Hamburger menu, slide-out navigation panel

- **MainNav.tsx:**
  - Horizontal list of navigation links
  - Active state styling (amber accent: `text-amber-400`)
  - Hover states (`hover:text-amber-300`)
  - Responsive: Hidden on mobile, shown in slide-out panel

- **UserMenu.tsx:**
  - User avatar (circular, shows initials if no photo)
  - User name (hidden on mobile)
  - Dropdown menu (Settings, Logout)
  - Positioned in top-right corner

**Layout requirements:**

- Top nav bar height: 64px (16 on mobile)
- Content area: Full width, padding for readability
- Max content width: 1280px (centered)
- Mobile breakpoint: 768px
- Support light and dark mode (`dark:` variants)

**Props and callbacks:**

- `AppShell` should accept `children` (page content)
- `MainNav` should accept `currentPath` for active state
- `UserMenu` should accept `user` object and `onLogout` callback

**User flows covered:**

1. User views navigation → sees TIP logo, My Trips, Create Trip, Profile, and user menu
2. User clicks logo → navigates to dashboard
3. User clicks "Create Trip" → navigates to trip creation wizard
4. User clicks avatar → dropdown opens with Settings and Logout
5. User clicks Logout → callback fires, session ends
6. Mobile user clicks hamburger → navigation panel slides in
7. Mobile user clicks backdrop → panel closes

Refer to `shell/README.md` and screenshots in `shell/` for visual guidance.

## Files to Reference

- `product-overview.md` — Product summary and section list
- `design-system/tokens.css` — CSS custom properties for colors and fonts
- `design-system/tailwind-colors.md` — Tailwind utility class mappings
- `design-system/fonts.md` — Google Fonts import and font-family declarations
- `data-model/README.md` — Entity descriptions and relationships
- `data-model/types.ts` — TypeScript interface definitions
- `data-model/sample-data.json` — Example data for testing
- `shell/spec.md` — Shell specification
- `shell/README.md` — Shell implementation guide
- `shell/components/AppShell.tsx` — Reference implementation
- `shell/components/MainNav.tsx` — Reference implementation
- `shell/components/UserMenu.tsx` — Reference implementation
- `shell/*.png` — Screenshots of the shell in action

## Expected User Flows

### Flow 1: First-time user views the application
1. User opens the app and logs in
2. App shell loads with TIP logo, navigation items, and user menu
3. User sees their name/avatar in the top-right corner
4. Main navigation shows "My Trips", "Create Trip", "Profile"
5. Content area displays the dashboard (implemented in next milestone)

**Expected outcome:** Clean, professional navigation structure is visible and functional.

### Flow 2: User navigates between sections
1. User clicks "My Trips" in navigation
2. Navigation highlights "My Trips" with amber accent
3. Content area updates to show trip list
4. User clicks "Profile" in navigation
5. Navigation highlights "Profile" with amber accent
6. Content area updates to show profile settings

**Expected outcome:** Navigation updates correctly and content swaps smoothly.

### Flow 3: User accesses user menu
1. User clicks on avatar/name in top-right
2. Dropdown menu appears with "Settings" and "Logout"
3. User clicks "Settings"
4. Navigates to profile page
5. User clicks avatar again and selects "Logout"
6. Logout callback fires and user is redirected to login

**Expected outcome:** User menu provides access to settings and logout functionality.

### Flow 4: Mobile user navigates the app
1. Mobile user opens the app
2. Sees TIP logo and hamburger menu icon
3. Taps hamburger icon
4. Navigation panel slides in from left with menu items
5. User taps "Create Trip"
6. Navigation panel closes and trip creation page loads

**Expected outcome:** Mobile navigation is accessible and intuitive.

## Done When

- [ ] Design tokens (colors, typography) are implemented and applied consistently
- [ ] Google Fonts (DM Sans, IBM Plex Mono) are imported and used
- [ ] All data model TypeScript interfaces are defined
- [ ] Routing structure covers all product sections
- [ ] Application shell renders with top navigation bar
- [ ] TIP logo links to dashboard
- [ ] Main navigation items (My Trips, Create Trip, Profile) are visible and clickable
- [ ] User menu displays avatar, name, and dropdown (Settings, Logout)
- [ ] Active navigation state highlights with amber accent
- [ ] Mobile hamburger menu opens/closes navigation panel
- [ ] Light and dark mode styling works for shell components
- [ ] Shell components accept appropriate props (user, currentPath, onLogout, children)
- [ ] Tests cover navigation rendering, active states, user menu interactions, and mobile behavior
- [ ] Visual appearance matches screenshots in `shell/` directory
