# TIP — Travel Intelligence & Planner — Implementation Instructions

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

The provided components are **reference implementations** from the Design OS planning tool. You will build the actual production application using these references as a guide. Your implementation should:

- Use your chosen tech stack (React/Next.js, Vue/Nuxt, etc.)
- Implement authentication and authorization
- Connect to your backend API
- Add data persistence (database)
- Include proper error handling
- Follow security best practices
- Be production-ready

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Each section includes a `tests.md` file with detailed framework-agnostic test instructions. These test specs cover:

- User flows with specific expected outcomes
- Empty states and edge cases
- Validation and error handling
- Component interactions
- Accessibility requirements

---

# Implementation Milestones

## Milestone 1: Foundation

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

---


---


---


---


---


---


---


---


---


This milestone implements the complete authentication system with separate pages for login, signup, password reset, and email verification. The authentication layer is the gateway to the entire application and must be secure, user-friendly, and reliable.

## Overview

Key functionality in this section:

- User signup with email/password and Google OAuth (primary method)
- Login with session management and rate limiting
- Password reset flow with email verification
- Account deletion with data cleanup
- Change password functionality
- Real-time password strength validation
- Session expiry warnings and extension
- Mobile-responsive standalone auth pages (no app shell)

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/authentication-account-management/components/`

Build the following components based on the provided references:

- **LoginForm.tsx** — Email/password login with Google OAuth button at top
- **SignupForm.tsx** — User registration with real-time validation and auto-login
- **PasswordResetRequestForm.tsx** — Email input to request password reset
- **PasswordResetForm.tsx** — New password entry with strength validation
- **EmailVerificationPage.tsx** — Success page after email verification
- **SessionExpiryWarning.tsx** — Banner warning about session expiry
- **AccountDeletionDialog.tsx** — Confirmation dialog for account deletion
- **ChangePasswordForm.tsx** — Current password + new password fields

### 2. Data Layer

**Files:** `sections/authentication-account-management/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface User {
  id: string;
  email: string;
  name: string;
  authProvider: 'email' | 'google';
  emailVerified: boolean;
  createdAt: string;
}

interface AuthSession {
  userId: string;
  token: string;
  expiresAt: string;
}

interface PasswordStrength {
  score: 'weak' | 'medium' | 'strong';
  feedback: string[];
}
```

### 3. Callbacks and Integration

Implement these callback props for each component:

- `onLogin(email: string, password: string): Promise<void>`
- `onGoogleLogin(): Promise<void>`
- `onSignup(email: string, password: string, name: string): Promise<void>`
- `onPasswordResetRequest(email: string): Promise<void>`
- `onPasswordReset(token: string, newPassword: string): Promise<void>`
- `onAccountDelete(): Promise<void>`
- `onChangePassword(currentPassword: string, newPassword: string): Promise<void>`
- `onExtendSession(): Promise<void>`

### 4. Empty States and Error Handling

- **Rate limit lockout:** Display "Too many failed attempts. Try again in 15 minutes or reset your password."
- **Invalid credentials:** Display "Incorrect email or password. Please try again."
- **Email not verified:** Display "Please verify your email address. Check your inbox for a verification link."
- **Session expired:** Redirect to login with message "Your session has expired. Please log in again."
- **Network errors:** Display "Unable to connect. Please check your internet connection and try again."

### 5. Validation Rules

Implement real-time password strength validation:

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 number
- At least 1 special character

Display validation feedback as user types:
- Red border and error message for invalid fields
- Green checkmark for valid fields
- Password strength indicator (weak/medium/strong) with color coding

### 6. Page Routes

Create standalone pages (without app shell) at these routes:

- `/login` — LoginForm
- `/signup` — SignupForm
- `/forgot-password` — PasswordResetRequestForm
- `/reset-password?token=...` — PasswordResetForm
- `/verify-email?token=...` — EmailVerificationPage

## Files to Reference

- `sections/authentication-account-management/spec.md` — Complete specification
- `sections/authentication-account-management/README.md` — Implementation guide
- `sections/authentication-account-management/types.ts` — TypeScript interfaces
- `sections/authentication-account-management/sample-data.json` — Example user data
- `sections/authentication-account-management/components/` — Reference components
- `sections/authentication-account-management/*.png` — Screenshots
- `sections/authentication-account-management/tests.md` — Test instructions

## Expected User Flows

### Flow 1: New user signs up with Google OAuth
1. User lands on `/signup` page
2. Sees "Continue with Google" button prominently displayed
3. Clicks Google OAuth button
4. Google authorization popup/redirect appears
5. User authorizes the app
6. Returns to app, auto-logged in
7. Redirected to dashboard

**Expected outcome:** User is authenticated and has an active session without entering email/password.

### Flow 2: New user signs up with email/password
1. User lands on `/signup` page
2. Scrolls past Google OAuth button to email/password form
3. Enters email address (validated for format)
4. Enters password (real-time strength indicator updates)
5. Password shows "weak" → user adds uppercase → shows "medium" → user adds number → shows "strong"
6. Enters password confirmation (matches original)
7. Clicks "Sign Up" button
8. Account created, verification email sent
9. User auto-logged in and redirected to dashboard

**Expected outcome:** User account is created, and user is immediately logged in without needing to verify email first (verification is optional background task).

### Flow 3: Returning user logs in
1. User lands on `/login` page
2. Sees Google OAuth button and email/password form
3. Enters email and password
4. Clicks "Login" button
5. Credentials validated
6. Redirected to dashboard or last visited page

**Expected outcome:** User is authenticated and sees their previous content.

### Flow 4: User forgets password
1. User clicks "Forgot password?" link on login page
2. Navigates to `/forgot-password`
3. Enters email address
4. Clicks "Send Reset Link" button
5. Success message appears: "Check your email for a password reset link"
6. User receives email with reset link
7. Clicks link, navigates to `/reset-password?token=...`
8. Enters new password (validated for strength)
9. Clicks "Reset Password" button
10. Password updated, success message shown
11. Redirected to `/login` after 3 seconds

**Expected outcome:** User successfully resets password and can log in with new credentials.

### Flow 5: User hits rate limit
1. User attempts login 5 times with incorrect password
2. After 5th attempt, lockout message appears
3. "Too many failed attempts. Try again in 15 minutes or reset your password."
4. Login button is disabled
5. User can click "Forgot password?" to bypass lockout

**Expected outcome:** Account is temporarily protected from brute force attacks.

### Flow 6: User session expires (with warning)
1. User is logged in and actively using the app
2. 5 minutes before session expires, warning banner appears at top
3. "Your session will expire soon. Extend session?"
4. User clicks "Extend Session" button
5. Session extended, warning disappears
6. User continues using the app

**Expected outcome:** User maintains active session without losing work or being logged out unexpectedly.

### Flow 7: User deletes account
1. User navigates to profile settings (implemented in later milestone)
2. Scrolls to Account section
3. Clicks "Delete Account" button
4. Confirmation dialog appears with warning
5. "This will permanently delete your account and all trip data. This action cannot be undone."
6. User clicks "Confirm Delete" button
7. Account and all associated data deleted
8. User logged out and redirected to `/signup`

**Expected outcome:** Account is permanently deleted with no remaining user data.

## Done When

- [ ] Signup page renders with Google OAuth button prominently at top
- [ ] Email/password signup form includes real-time validation
- [ ] Password strength indicator updates as user types (weak/medium/strong)
- [ ] Login page includes Google OAuth and email/password options
- [ ] "Forgot password?" link navigates to password reset request page
- [ ] Password reset flow sends email and allows password update
- [ ] Email verification page displays success message
- [ ] Rate limiting displays lockout message after 5 failed login attempts
- [ ] Session expiry warning appears 5 minutes before expiry with "Extend Session" button
- [ ] Account deletion dialog warns user of permanent data loss
- [ ] Change password form validates current password and new password strength
- [ ] All auth pages are mobile-responsive and work without app shell
- [ ] Light and dark mode styles are applied
- [ ] Show/hide password toggle works on all password fields
- [ ] Auto-focus on first form field improves UX
- [ ] Tests cover all user flows including edge cases (rate limiting, session expiry, validation errors)
- [ ] Visual appearance matches screenshots in section directory

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

This milestone implements the centralized settings page where users manage their profile, default traveler details, travel preferences, saved templates, notification settings, privacy controls, and account deletion. This is a comprehensive settings hub with auto-save functionality.

## Overview

Key functionality in this section:

- Profile information management (name, email, photo)
- Default traveler details (nationality, residency, DOB)
- Travel preferences (style, dietary restrictions, accessibility needs)
- Saved trip templates (view, create, edit, delete)
- Notification preferences (email toggles)
- Privacy controls and data deletion policy acknowledgment
- Account deletion with warning
- Auto-save with "Saved" indicators

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/user-profile-settings/components/`

Build the following components based on the provided references:

- **ProfileSettingsPage.tsx** — Main page container with all sections
- **ProfileSection.tsx** — Name, email, photo upload
- **TravelerDetailsSection.tsx** — Nationality, residency, residency status, DOB
- **TravelPreferencesSection.tsx** — Travel style, dietary restrictions, accessibility needs
- **SavedTemplatesSection.tsx** — Template cards with edit/delete actions
- **TemplateCard.tsx** — Individual template display
- **TemplateModal.tsx** — Create/edit template form
- **NotificationsSection.tsx** — Email notification toggles
- **PrivacySection.tsx** — Data deletion policy info and privacy controls
- **AccountSection.tsx** — Delete account button with warning
- **AutoSaveIndicator.tsx** — "Saved" message that appears after changes
- **ProfilePhotoUpload.tsx** — Photo upload with preview

### 2. Data Layer

**Files:** `sections/user-profile-settings/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface UserProfile {
  id: string;
  name: string;
  email: string;
  photoUrl?: string;
  authProvider: 'email' | 'google';
}

interface TravelerDetails {
  nationality: string;
  residenceCountry: string;
  residencyStatus: string;
  dateOfBirth: string;
}

interface TravelPreferences {
  travelStyle: 'relaxed' | 'balanced' | 'packed' | 'budget-focused';
  dietaryRestrictions: string[];
  accessibilityNeeds?: string;
}

interface TripTemplate {
  id: string;
  name: string;
  destinations: string[];
  datePattern: string; // e.g., "Weekend getaway", "1 week"
  preferences: TravelPreferences;
}

interface NotificationSettings {
  deletionReminders: boolean;
  reportCompletion: boolean;
  productUpdates: boolean;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onProfileUpdate(data: Partial<UserProfile>): Promise<void>` — Update profile info with auto-save
- `onTravelerDetailsUpdate(data: TravelerDetails): Promise<void>` — Update traveler details with auto-save
- `onPreferencesUpdate(data: TravelPreferences): Promise<void>` — Update preferences with auto-save
- `onPhotoUpload(file: File): Promise<string>` — Upload photo, return URL
- `onTemplateCreate(template: TripTemplate): Promise<void>` — Create new template
- `onTemplateEdit(id: string, template: TripTemplate): Promise<void>` — Update template
- `onTemplateDelete(id: string): Promise<void>` — Delete template after confirmation
- `onNotificationToggle(setting: string, value: boolean): Promise<void>` — Update notification preference
- `onAccountDelete(): Promise<void>` — Delete account after confirmation
- `onChangePassword(): void` — Navigate to change password flow (from auth section)

### 4. Auto-Save Behavior

- Save changes automatically as user types/selects (debounced by 1-2 seconds)
- Show "Saved" indicator briefly (2-3 seconds fade) next to modified field/section
- Display loading spinner during save
- Show error message if save fails with retry option

### 5. Template Management

**Saved Templates Section:**
- Display templates as cards in grid layout
- Each card shows: template name, destination(s), date pattern, preference summary
- "Edit" and "Delete" buttons on each card
- "Create Template" button to add new template (requires active trip context or manual entry)

**Template Modal (Create/Edit):**
- Template name input
- Destination selection (can add multiple)
- Date pattern input (e.g., "Weekend", "1 week", "2 weeks")
- Travel style selector
- Dietary restrictions checkboxes
- Save/Cancel buttons

**Empty state:** "No saved templates yet. Create a trip template to speed up future trip creation."

### 6. Notification Settings

Three email notification toggles:

- **Deletion Reminders:** Email notifications before trip auto-deletion (default: ON)
- **Report Completion:** Email when travel intelligence report is ready (default: ON)
- **Product Updates:** Occasional emails about new features (default: OFF)

Each toggle includes description text explaining what it controls.

### 7. Privacy & Data Deletion

**Privacy Section displays:**
- Data deletion policy: "Your trip data is automatically deleted 7 days after your trip end date to protect your privacy."
- Link to full privacy policy (opens in new tab)
- Privacy controls (optional toggles for data usage)

### 8. Account Deletion

**Account Section:**
- "Delete Account" button with red destructive styling
- Warning text: "This action is permanent and cannot be undone. All your trips and data will be permanently deleted."
- Click opens confirmation dialog
- Dialog message: "Are you sure you want to delete your account? This will permanently delete all your trip data."
- "Cancel" and "Confirm Delete" buttons
- On confirm, account deleted and user logged out, redirected to signup page

### 9. Change Password Link

If user is authenticated via email/password (not OAuth):
- Display "Change Password" link in Profile section
- Clicking navigates to change password flow (implemented in auth section)

If user is authenticated via Google OAuth:
- Hide "Change Password" link (password managed by Google)

## Files to Reference

- `sections/user-profile-settings/spec.md` — Complete specification
- `sections/user-profile-settings/README.md` — Implementation guide
- `sections/user-profile-settings/types.ts` — TypeScript interfaces
- `sections/user-profile-settings/sample-data.json` — Example profile data
- `sections/user-profile-settings/components/` — Reference components
- `sections/user-profile-settings/*.png` — Screenshots
- `sections/user-profile-settings/tests.md` — Test instructions

## Expected User Flows

### Flow 1: User updates profile information
1. User navigates to Profile settings page
2. Page loads with all sections displayed in single scrollable view
3. User clicks on name field and changes from "John Doe" to "John Smith"
4. Auto-save triggers after 2 seconds
5. "Saved" indicator appears next to name field
6. User scrolls to email field (read-only if OAuth, shows Google icon)
7. User clicks "Change Password" link (if email/password auth)
8. Navigates to password change flow

**Expected outcome:** Profile updates save automatically without explicit "Save" button.

### Flow 2: User sets default traveler details
1. User scrolls to Traveler Details section
2. Selects nationality from dropdown: "United States"
3. Auto-save triggers, "Saved" indicator appears
4. Selects residence country: "United States"
5. Selects residency status: "Citizen"
6. Enters date of birth: "January 15, 1990"
7. Each field auto-saves as it's updated
8. "Saved" indicators appear and fade after 2-3 seconds
9. These defaults will pre-fill future trip creation forms

**Expected outcome:** Default traveler details are saved and will speed up future trip creation.

### Flow 3: User manages travel preferences
1. User scrolls to Travel Preferences section
2. Selects travel style radio button: "Balanced"
3. Auto-save triggers
4. Checks dietary restrictions: "Vegetarian", "Gluten-free"
5. Each selection auto-saves
6. Enters accessibility needs: "Wheelchair accessible accommodations preferred"
7. Auto-save triggers after typing stops
8. "Saved" indicator appears

**Expected outcome:** Preferences are saved and will customize future itinerary generation.

### Flow 4: User creates trip template
1. User scrolls to Saved Templates section
2. Clicks "Create Template" button
3. Template modal opens
4. User enters:
   - Template name: "Weekend Getaway"
   - Destinations: "San Francisco"
   - Date pattern: "3 days / 2 nights"
   - Travel style: "Relaxed"
   - Dietary restrictions: "Vegetarian"
5. Clicks "Save Template" button
6. Modal closes, new template card appears in grid
7. Success message: "Template saved successfully"

**Expected outcome:** User can reuse this template for quick trip creation.

### Flow 5: User edits and deletes template
1. User views Saved Templates section with 3 templates
2. Clicks "Edit" on "Business Trip" template
3. Template modal opens with fields pre-filled
4. User changes date pattern from "1 week" to "5 days"
5. Clicks "Save" button
6. Modal closes, template card updates
7. User clicks "Delete" on "Old Template" card
8. Confirmation dialog: "Delete this template? This action cannot be undone."
9. User confirms
10. Template card is removed from grid
11. Success message: "Template deleted"

**Expected outcome:** User maintains organized template library.

### Flow 6: User configures notifications
1. User scrolls to Notifications section
2. Sees three toggle switches:
   - Deletion Reminders: ON
   - Report Completion: ON
   - Product Updates: OFF
3. User toggles "Product Updates" to ON
4. Auto-save triggers
5. "Saved" indicator appears
6. User will now receive product update emails

**Expected outcome:** User controls which emails they receive.

### Flow 7: User reviews privacy policy
1. User scrolls to Privacy section
2. Reads data deletion policy: "Your trip data is automatically deleted 7 days after your trip end date to protect your privacy."
3. Clicks "View Full Privacy Policy" link
4. Privacy policy opens in new tab
5. User reviews policy and returns to settings page

**Expected outcome:** User understands data retention practices.

### Flow 8: User deletes account
1. User scrolls to Account section
2. Sees red "Delete Account" button with warning text
3. Clicks button
4. Confirmation dialog appears: "Are you sure you want to delete your account? This will permanently delete all your trip data. This action cannot be undone."
5. User clicks "Confirm Delete"
6. Account deletion process starts
7. User is logged out
8. Redirected to signup page
9. All user data and trips are permanently deleted

**Expected outcome:** Account is fully deleted with clear warnings at each step.

### Flow 9: User uploads profile photo
1. User clicks on profile photo upload area
2. File picker opens
3. User selects photo file (JPG, PNG)
4. Photo preview displays immediately
5. Upload starts automatically
6. Loading spinner shows during upload
7. Upload completes, "Saved" indicator appears
8. New photo displays in profile section and user menu

**Expected outcome:** Profile photo updates and displays throughout app.

## Done When

- [ ] Profile section displays name, email, and photo upload
- [ ] Email field is read-only for OAuth users with provider icon
- [ ] "Change Password" link appears only for email/password users
- [ ] Photo upload works with preview and loading state
- [ ] Traveler Details section includes nationality, residence, residency status, DOB dropdowns/pickers
- [ ] Travel Preferences section has travel style radio buttons and dietary restrictions checkboxes
- [ ] Accessibility needs textarea allows free-form input
- [ ] Auto-save triggers after user stops typing/selecting (debounced)
- [ ] "Saved" indicator appears briefly (2-3 seconds) after successful save
- [ ] Saved Templates section displays templates as cards in grid
- [ ] Template cards show name, destinations, date pattern, preferences summary
- [ ] "Create Template" button opens template modal
- [ ] Template modal includes all fields and Save/Cancel buttons
- [ ] "Edit" button on template card opens modal with pre-filled data
- [ ] "Delete" button on template card shows confirmation before deletion
- [ ] Empty state displays when no templates exist
- [ ] Notifications section has three toggle switches with descriptions
- [ ] Privacy section displays data deletion policy and link to full policy
- [ ] Account section has red "Delete Account" button with warning text
- [ ] Account deletion shows confirmation dialog before execution
- [ ] All sections use single scrollable page layout within app shell
- [ ] Loading states show during photo upload and save operations
- [ ] Error messages display if save fails with retry option
- [ ] Mobile layout uses single column with touch-friendly controls
- [ ] Light and dark mode styles work across all sections
- [ ] Tests cover profile updates, traveler details, preferences, templates, notifications, and account deletion
- [ ] Visual appearance matches screenshots in section directory

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
