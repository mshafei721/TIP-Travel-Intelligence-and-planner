  Resuming TIP (Travel Intelligence & Planner) project - Session 13
  FOCUS: COMPLETE FRONTEND DEVELOPMENT

  ## Quick Context
  - Next.js 16 + Tailwind CSS v4 + Radix UI
  - Windows environment (PowerShell only)
  - User has zero technical experience
  - Use /frontend-design skill for all UI work

  ## Infrastructure Status ✅ (All Ready)
  - Frontend: Vercel ✅
  - Backend: Railway ✅
  - Redis + Celery: Railway ✅
  - Supabase: Configured ✅

  ---

  ## FRONTEND COMPLETION ROADMAP

  ### Current Status
  | Section | Increment | Status | Priority |
  |---------|-----------|--------|----------|
  | Authentication | I1 | ✅ 100% | Done |
  | Dashboard Home | I3 | ✅ 100% | Done |
  | User Profile Settings | I2 | ⚠️ 30% | HIGH |
  | Trip Creation Wizard | I4 | ❌ 0% | HIGH |
  | Visa Intelligence UI | I5 | ❌ 0% | MEDIUM |
  | Destination Intelligence UI | I5 | ❌ 0% | MEDIUM |
  | Travel Itinerary Builder | I6 | ❌ 0% | MEDIUM |
  | Report Management | I7 | ❌ 0% | LOW |
  | Error States | I1-I10 | ⚠️ 40% | ONGOING |

  ### Implementation Order
  1. **I2**: User Profile Settings (complete traveler profile)
  2. **I4**: Trip Creation Wizard (4-step form)
  3. **I5**: Report Display UI (visa, destination sections)
  4. **I6**: Visual Itinerary Builder
  5. **I7**: Report Management (list, share, export)
  6. **I10**: Settings & Preferences

  ---

  ## DESIGN SYSTEM (MANDATORY)

  ### Colors
  Primary:   blue-600    (buttons, links, active states)
  Secondary: amber-500   (CTAs, highlights, Create Trip)
  Neutral:   slate-*     (backgrounds, text, borders)
  Success:   green-600
  Warning:   amber-600
  Error:     red-600

  ### Typography
  Font Family: DM Sans (headings + body)
  Monospace:   IBM Plex Mono (code, technical)

  H1: text-4xl font-bold
  H2: text-3xl font-semibold
  H3: text-2xl font-semibold
  H4: text-xl font-medium
  Body: text-base
  Small: text-sm
  Caption: text-xs

  ### Dark Mode Pattern
  ```html
  <!-- All components must support dark mode -->
  <div class="bg-white dark:bg-slate-900">
  <p class="text-slate-900 dark:text-slate-50">
  <div class="border-slate-200 dark:border-slate-800">

  Button Variants

  <!-- Primary -->
  <button class="bg-blue-600 hover:bg-blue-700 text-white">

  <!-- Secondary/CTA -->
  <button class="bg-amber-500 hover:bg-amber-600 text-white">

  <!-- Outline -->
  <button class="border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300">

  ---
  PRIORITY 1: USER PROFILE SETTINGS (I2)

  Documentation

  product-plan/instructions/incremental/09-user-profile-settings.md
  product-plan/sections/user-profile-settings/

  Components to Build

  frontend/components/profile/
  ├── ProfileForm.tsx          # Main profile edit form
  ├── TravelerProfileForm.tsx  # Travel preferences
  ├── NotificationSettings.tsx # Email/push preferences
  ├── PrivacySettings.tsx      # Data & privacy options
  ├── AccountSettings.tsx      # Password, delete account
  └── ProfileAvatar.tsx        # Avatar upload/display

  Pages to Build

  frontend/app/(app)/profile/
  ├── page.tsx                 # Profile overview
  ├── edit/page.tsx            # Edit profile
  ├── settings/page.tsx        # Account settings
  └── preferences/page.tsx     # Travel preferences

  ---
  PRIORITY 2: TRIP CREATION WIZARD (I4)

  Documentation

  product-plan/instructions/incremental/04-trip-creation-input.md
  product-plan/sections/trip-creation-input/

  4-Step Wizard Structure

  Step 1: Traveler Details
    - Name, email, nationality
    - Residence country, origin city
    - Party size, ages

  Step 2: Destination
    - Country/city search
    - Multi-city toggle
    - Additional destinations

  Step 3: Trip Details
    - Travel dates (departure/return)
    - Budget, currency
    - Trip purpose

  Step 4: Preferences
    - Travel style
    - Interests
    - Dietary restrictions
    - Accessibility needs

  Components to Build

  frontend/components/trip-wizard/
  ├── TripCreationWizard.tsx   # Main wizard container
  ├── StepIndicator.tsx        # Progress indicator (1/4)
  ├── ProgressBar.tsx          # Horizontal progress
  ├── Step1TravelerDetails.tsx
  ├── Step2Destination.tsx
  ├── Step3TripDetails.tsx
  ├── Step4Preferences.tsx
  ├── TripSummary.tsx          # Review before submit
  ├── AutoSaveIndicator.tsx    # "Draft saved" toast
  ├── TemplateSelector.tsx     # Load from template
  └── NavigationButtons.tsx    # Back/Next/Submit

  Page to Build

  frontend/app/(app)/trips/new/
  ├── page.tsx                 # Wizard page
  └── loading.tsx              # Loading state

  ---
  PRIORITY 3: REPORT DISPLAY UI (I5)

  Documentation

  product-plan/instructions/incremental/05-visa-entry-intelligence.md
  product-plan/instructions/incremental/06-destination-intelligence.md

  Components to Build

  frontend/components/report/
  ├── ReportLayout.tsx         # Main report container
  ├── ReportSection.tsx        # Generic section wrapper
  ├── ReportTabs.tsx           # Section navigation
  ├── VisaSection.tsx          # Visa requirements display
  ├── DestinationSection.tsx   # Country info display
  ├── WeatherSection.tsx       # Weather forecast
  ├── CultureSection.tsx       # Cultural tips
  ├── FoodSection.tsx          # Food recommendations
  ├── AttractionsSection.tsx   # Places to visit
  ├── CurrencySection.tsx      # Exchange rates
  ├── LoadingSection.tsx       # Section loading state
  └── ErrorSection.tsx         # Section error state

  Page to Build

  frontend/app/(app)/trips/[id]/
  ├── page.tsx                 # Trip report view
  ├── loading.tsx
  └── error.tsx

  ---
  TDD WORKFLOW (STRICT)

  Test First Approach

  1. Read component spec from product-plan/
  2. Write test file FIRST (*.test.tsx)
  3. Run test → Must FAIL (RED)
  4. Implement component
  5. Run test → Must PASS (GREEN)
  6. Refactor with design system
  7. Commit

  Test File Structure

  frontend/__tests__/
  ├── components/
  │   ├── profile/
  │   ├── trip-wizard/
  │   └── report/
  └── pages/
      ├── profile.test.tsx
      ├── trip-wizard.test.tsx
      └── report.test.tsx

  ---
  MANDATORY RULES

  Before ANY Component

  - Read product-plan/instructions/incremental/XX-*.md
  - Check product-plan/sections/*/types.ts for interfaces
  - Check product-plan/sections/*/sample-data.json
  - Review design system (colors, fonts, patterns)
  - Use /frontend-design skill

  Design System Compliance

  - All colors from tailwind-colors.md
  - All fonts from fonts.md
  - Dark mode support on every component
  - Responsive (mobile-first)
  - Accessible (ARIA labels, keyboard nav)

  Key Constraints

  - PowerShell commands only
  - Ask user for UI preferences (AskUserQuestion)
  - Keep under 100K tokens
  - Test after every component
  - Don't modify existing working components

  ---
  KEY FILES TO READ

  Documentation

  - product-plan/product-overview.md
  - product-plan/design-system/tailwind-colors.md
  - product-plan/design-system/fonts.md
  - product-plan/instructions/incremental/04-trip-creation-input.md
  - product-plan/instructions/incremental/09-user-profile-settings.md

  Existing Code (Reference)

  - frontend/components/ui/* (base components)
  - frontend/components/dashboard/* (pattern reference)
  - frontend/components/auth/* (form patterns)
  - frontend/app/globals.css (global styles)
  - frontend/tailwind.config.ts (theme config)

  Types

  - frontend/types/database.ts
  - frontend/types/auth.ts

  ---
  START COMMANDS

  cd "D:\009_Projects_AI\Personal_Projects\TIP-Travel Intelligence-and-planner"

  # Start frontend dev server
  cd frontend
  npm run dev

  # Run tests
  npm test

  # Type check
  npm run type-check

  FIRST ACTIONS

  1. Read product-plan/product-overview.md
  2. Read design system files (colors, fonts)
  3. Ask user: "Which section should I implement first?"
    - Option A: User Profile Settings (I2)
    - Option B: Trip Creation Wizard (I4)
    - Option C: Report Display UI (I5)
  4. Use /frontend-design skill
  5. Write tests first, then implement

  EXPECTED DELIVERABLES PER SESSION

  - Complete one major section (profile OR wizard OR report)
  - All components with dark mode
  - Tests for each component
  - Responsive design verified
  - Updated feature_list.json
  - Commit with descriptive message
