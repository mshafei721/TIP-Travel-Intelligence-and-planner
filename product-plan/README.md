# TIP — Travel Intelligence & Planner — Export Package

This package contains complete specifications, design system, data model, reference components, and implementation instructions for building TIP from scratch.

## What's Inside

- **product-overview.md** — Product description, problems solved, sections list, data model summary
- **design-system/** — Color palette, typography, and design tokens
- **data-model/** — Entity descriptions, TypeScript interfaces, sample data
- **shell/** — Application shell (navigation, layout) with components and spec
- **sections/** — All feature sections with specs, components, types, and test instructions
- **instructions/** — Milestone-by-milestone implementation guides
- **prompts/** — Ready-to-use prompts for coding agents

## How to Use This Package

You have two options for implementing TIP:

### Option A: Incremental (Milestone-by-Milestone)

Build TIP progressively, one milestone at a time. This approach allows you to:
- Validate each feature before moving on
- Make architectural decisions incrementally
- Test and refine as you go

**Steps:**
1. Read `product-overview.md` for context
2. Start with `instructions/incremental/01-foundation.md`
3. Complete each milestone in order (01 through 10)
4. Use section assets (components, types, tests) as references
5. Check off "Done When" criteria before advancing

**Use the section prompt template** (`prompts/section-prompt.md`) when working with coding agents.

### Option B: One-Shot (All at Once)

Build the entire application in one comprehensive session. This approach is best if you:
- Have a clear tech stack and architecture plan
- Want to optimize for consistency across features
- Are using an AI coding agent with large context

**Steps:**
1. Read `product-overview.md` for context
2. Review `instructions/one-shot-instructions.md` (all milestones combined)
3. Ask clarifying questions about tech stack, deployment, and external services
4. Implement all milestones following the instructions
5. Use reference components and test specs throughout

**Use the one-shot prompt** (`prompts/one-shot-prompt.md`) when working with coding agents.

## Test-Driven Development

Both approaches emphasize TDD. Each section includes a `tests.md` file with detailed, framework-agnostic test specifications. These specs cover:

- **User flows** with specific steps and expected outcomes
- **Empty states** (no data, filtered results, related records)
- **Validation** and error handling
- **Component interactions** and callbacks
- **Accessibility** requirements

Write tests first using these specs, then implement features to make tests pass.

## Implementation Milestones

1. **Foundation** — Design tokens, data model types, routing, application shell
2. **Authentication & Account Management** — Signup, login, OAuth, password reset, session management
3. **Dashboard & Home** — Landing page with trips overview and quick actions
4. **Trip Creation & Input** — Multi-step wizard for trip details
5. **Visa & Entry Intelligence** — Critical visa requirements with confidence indicators
6. **Destination Intelligence** — Country info, weather, culture, safety in card format
7. **Travel Planning & Itinerary** — AI-powered day-by-day itinerary generation
8. **Report Management** — Trip list, report viewing, PDF export, deletion management
9. **User Profile & Settings** — Profile, preferences, templates, notifications
10. **Error States & Loading Screens** — 404/500 pages, error handling, progress indicators

## Reference Components

All sections include React components in `sections/[section-id]/components/`. These are **reference implementations** from the Design OS planning tool. Use them as:

- Visual and functional guides
- Code structure examples
- Component API references

Build production-ready versions in your chosen tech stack. The references show:
- Component structure and props
- State management patterns
- Event handling
- Styling approach

## Design System

**Colors:**
- Primary: `blue` (Tailwind blue-50 through blue-950)
- Secondary: `amber` (Tailwind amber-50 through amber-950)
- Neutral: `slate` (Tailwind slate-50 through slate-950)

**Typography:**
- Heading: `DM Sans`
- Body: `DM Sans`
- Mono: `IBM Plex Mono`

**Google Fonts Import:**
```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=IBM+Plex+Mono:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;1,100;1,200;1,300;1,400;1,500;1,600;1,700&display=swap');
```

See `design-system/` for complete token specifications.

## Data Model

Core entities:
- **User** — Traveler accounts
- **Trip** — Planned journeys with destinations and dates
- **Destination** — Countries/cities within trips
- **AgentJobs** — Background AI processing tasks
- **ReportSections** — Generated intelligence (visa, itinerary, etc.)
- **TravelReport** — Complete aggregated reports
- **TravelerProfile** — Saved preferences and defaults
- **FlightOption** — Flight search results
- **Notification** — System notifications
- **DeletionSchedule** — GDPR-compliant data lifecycle

See `data-model/README.md` and `data-model/types.ts` for complete definitions.

## Key Features to Implement

### Authentication
- Email/password signup and login
- Google OAuth (primary method)
- Password reset flow
- Session management with expiry warnings
- Account deletion

### AI Integration
TIP requires AI agents to generate travel intelligence:
- Visa requirements (>95% accuracy, official sources only)
- Destination information (weather, culture, safety, costs)
- Smart itinerary generation
- Natural language itinerary editing
- Flight price discovery

Plan your AI architecture before implementation.

### GDPR Compliance
- Auto-delete trips 7 days after end date
- Email notifications before deletion
- Deletion schedule tracking
- Full account deletion option

### Mobile Responsive
- All screens work on mobile, tablet, desktop
- Touch-friendly interactions
- Responsive layouts using Tailwind breakpoints

### Light & Dark Mode
- Full theme support across all screens
- Use Tailwind `dark:` variants

## File Structure

```
product-plan/
├── README.md                       # This file
├── product-overview.md             # Product summary
│
├── prompts/
│   ├── one-shot-prompt.md          # Prompt for full implementation
│   └── section-prompt.md           # Template for incremental approach
│
├── instructions/
│   ├── one-shot-instructions.md    # All milestones combined
│   └── incremental/
│       ├── 01-foundation.md
│       ├── 02-authentication-account-management.md
│       ├── 03-dashboard-home.md
│       ├── 04-trip-creation-input.md
│       ├── 05-visa-entry-intelligence.md
│       ├── 06-destination-intelligence.md
│       ├── 07-travel-planning-itinerary.md
│       ├── 08-report-management.md
│       ├── 09-user-profile-settings.md
│       └── 10-error-states-loading-screens.md
│
├── design-system/
│   ├── tokens.css                  # CSS custom properties
│   ├── tailwind-colors.md          # Tailwind utility class mappings
│   └── fonts.md                    # Google Fonts import and usage
│
├── data-model/
│   ├── README.md                   # Entity descriptions and relationships
│   ├── types.ts                    # TypeScript interface definitions
│   └── sample-data.json            # Example data for testing
│
├── shell/
│   ├── README.md                   # Shell overview and usage
│   ├── components/
│   │   ├── AppShell.tsx
│   │   ├── MainNav.tsx
│   │   ├── UserMenu.tsx
│   │   └── index.ts
│   └── *.png                       # Screenshots
│
└── sections/
    └── [section-id]/
        ├── README.md               # Section overview
        ├── tests.md                # Test specifications
        ├── types.ts                # TypeScript interfaces
        ├── sample-data.json        # Example data
        ├── components/             # Reference React components
        │   ├── [Component].tsx
        │   └── index.ts
        └── *.png                   # Screenshots
```

## Tips for Success

1. **Start with clarifying questions** — Nail down tech stack, architecture, and external services before coding
2. **Write tests first** — Use the provided test specs to guide implementation
3. **Build incrementally** — Even if using one-shot approach, validate each milestone's "Done When" checklist
4. **Use reference components wisely** — They show intent and structure, but build production versions
5. **Prioritize security** — Authentication, session management, data protection are critical
6. **Plan AI integration early** — Report generation is core to TIP's value proposition
7. **Mobile-first** — Design and test on mobile screens first
8. **Accessibility matters** — Follow ARIA guidelines, keyboard navigation, screen reader support

## Getting Help

If you encounter ambiguities or edge cases not covered in the specs:

1. Check the section's `README.md` for design decisions and rationale
2. Review user flows in the section's `spec.md` for intended behavior
3. Look at reference components for implementation patterns
4. Refer to screenshots for visual clarification
5. Make reasonable assumptions aligned with the product vision

## Next Steps

1. Choose your implementation approach (incremental or one-shot)
2. Read `product-overview.md` to understand the product
3. Follow the appropriate prompt and instructions
4. Build TIP!

Happy coding!
